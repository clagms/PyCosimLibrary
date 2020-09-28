from typing import List, Callable
import numpy as np
from fmpy.fmi2 import FMU2Slave

from PyCosimLibrary.results import CosimResults
from PyCosimLibrary.scenario import CosimScenario, VarType, SignalType, Connection


class CosimRunner:
    """
    This class is responsible for running co-simulations.
    It gets a set of FMUs, their interconnections, parameters, and runs them.
    It assumes that the FMUs are loaded and have been instantiated elsewhere.
    The outputs are handled by some other objects as well.
    The concrete co-simulation step is implemented by subclasses.
    """

    def propagate_initial_outputs(self, scenario: CosimScenario):
        """
        To be subclassed by specialized methods.
        Default implementation is normal output propagation.
        :param scenario:
        :return:
        """
        self.propagate_outputs(scenario.connections)

    def propagate_outputs(self, connections: List[Connection]):
        """
        For now, we use the order of the connections as an indicator for the order of output propagation.
        This means the user is responsible for providing this information.
        """
        for c in connections:
            if c.target_fmu is not None:
                if c.value_type == VarType.REAL:
                    c.target_fmu.setReal(c.target_vr, c.source_fmu.getReal(c.source_vr))
                else:
                    c.target_fmu.setBoolean(c.target_vr, c.source_fmu.getBoolean(c.source_vr))

    def init_results(self, scenario: CosimScenario, results = CosimResults()):
        results.timestamps = []

        # Output signals store the outputs of the FMU at the end of the cosim step.
        results.out_signals = {}

        results.abstract_modes = {}

        for ov in scenario.outputs:
            # Store the output signals
            if ov.source_fmu.instanceName not in results.out_signals.keys():
                assert ov.source_fmu.instanceName not in results.abstract_modes.keys(), \
                    "Using duplicate connections for output is not allowed."
                results.out_signals[ov.source_fmu.instanceName] = {}
                results.abstract_modes[ov.source_fmu.instanceName] = {}
            for vr in ov.source_vr:
                assert vr not in results.out_signals[ov.source_fmu.instanceName].keys(), \
                    "Using duplicate connections for output is not allowed."
                results.out_signals[ov.source_fmu.instanceName][vr] = []
            # Init the modes (only for discontinuous out_signals)
            if ov.signal_type == SignalType.DISCONTINUOUS:
                for vr in ov.source_vr:
                    assert vr not in results.abstract_modes[ov.source_fmu.instanceName].keys(), \
                        "Duplicate abstract mode found."
                    results.abstract_modes[ov.source_fmu.instanceName][vr] = []

        return results

    def get_fmu_vars(self, fmu: FMU2Slave, vrs: List[int], type: VarType):
        if type == VarType.REAL:
            values = fmu.getReal(vrs)
        else:
            values = fmu.getBoolean(vrs)
        return values

    def snapshot(self, time: float, scenario: CosimScenario, results: CosimResults):
        results.timestamps.append(time)
        for ov in scenario.outputs:

            # Get values from FMU and place them in the corresponding signal streams
            values = self.get_fmu_vars(ov.source_fmu, ov.source_vr, ov.value_type)

            # Each item with index i in values corresponds to the value of item with index i in ov.source_vr
            for i in range(len(values)):
                value_append = values[i]
                vr: int = ov.source_vr[i]
                signal = results.out_signals[ov.source_fmu.instanceName][vr]
                signal.append(value_append)

            # Aggregate modes
            if ov.signal_type == SignalType.DISCONTINUOUS:
                # If last known mode has changed (modulo quantization_tol), then it's a new mode.
                for i in range(len(values)):
                    current_mode = values[i]
                    vr: int = ov.source_vr[i]
                    abstract_modes = results.abstract_modes[ov.source_fmu.instanceName][vr]
                    if len(abstract_modes) == 0:
                        abstract_modes.append(current_mode)
                    else:
                        last_mode = abstract_modes[-1]
                        if not np.isclose(current_mode, last_mode, rtol=ov.quantization_tol, atol=ov.quantization_tol):
                            abstract_modes.append(current_mode)

    def should_continue(self, scenario, time):
        end_connection = scenario.stop_condition
        if end_connection is None:
            assert scenario.stop_time > 0.0
            return (time + scenario.step_size <= scenario.stop_time) or \
                   np.isclose(time + scenario.step_size, scenario.stop_time, rtol=scenario.step_size * 1e-03,
                              atol=scenario.step_size * 1e-03)

        last_value = end_connection.source_fmu.getReal(end_connection.source_vr)[0]
        return last_value > 0.0 and not \
            np.isclose(last_value, 0.0, rtol=scenario.step_size * 1e-3, atol=scenario.step_size * 1e-3)

    def run_cosim_step(self, time, scenario: CosimScenario):
        """
        To be overriden.
        Implements the cosim step algorithm.
        :param time:
        :param scenario:
        :return:
        """
        raise NotImplementedError("This method needs to be overriden.")

    def valid_scenario(self, scenario: CosimScenario):
        set_fmus = set(scenario.fmus)
        # Rule: no duplicates in the list of FMUs.
        if len(scenario.fmus) != len(set_fmus):
            raise ValueError("Invalid Scenario. Duplicate fmus found: {}".format(scenario.fmus))

        # Rule: every connection must refer to an FMU that exists in the list of FMUs.
        for connection in scenario.connections:
            if connection.source_fmu not in set_fmus:
                raise ValueError(
                    "Invalid Scenario. Connection {} points to an FMU ({}) not contained in the list of given FMUs ({}).".format(
                        connection, connection.source_fmu, scenario.fmus))
            if connection.target_fmu not in set_fmus:
                raise ValueError(
                    "Invalid Scenario. Connection {} points to an FMU ({}) not contained in the list of given FMUs ({}).".format(
                        connection, connection.target_fmu, scenario.fmus))

    def terminate_cosim(self, scenario: CosimScenario):
        """
        To be inherited by custom runners.
        :param scenario:
        :return:
        """
        pass

    def run_cosim(self, scenario: CosimScenario, status: Callable):

        self.valid_scenario(scenario)

        # Init results
        results = self.init_results(scenario)

        for f in scenario.fmus:
            f.setupExperiment(None, 0.0, scenario.stop_time if scenario.stop_time > 0.0 else 0.0)
            f.enterInitializationMode()

        for f, (vrs, vals) in scenario.real_parameters.items():
            f.setReal(vrs, vals)

        # TODO Support fixed point iteration initialization
        self.propagate_initial_outputs(scenario)

        for f in scenario.fmus:
            f.exitInitializationMode()

        time = 0.0
        print_frequency = int(scenario.print_interval / scenario.step_size)
        print_counter = print_frequency

        self.snapshot(time, scenario, results)
        should_continue = self.should_continue(scenario, time)
        # TODO: Take output snapshot
        while should_continue:
            self.run_cosim_step(time, scenario)

            print_counter -= 1
            time += scenario.step_size
            should_continue = self.should_continue(scenario, time)
            if print_counter == 0:
                if status is not None:
                    status(time)
                self.snapshot(time, scenario, results)
                print_counter = print_frequency

        self.terminate_cosim(scenario)

        return results
