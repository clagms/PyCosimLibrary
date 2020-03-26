from typing import List

from cosimlibrary.runner import CosimRunner
from cosimlibrary.scenario import CosimScenario, VarType
import numpy as np

class JacobiIterativeRunner(CosimRunner):
    def __init__(self, max_iterations: int, tol: float):
        self.max_iterations = max_iterations
        self.tol = tol

    def run_cosim_step(self, time, scenario: CosimScenario):
        has_converged = False
        previous_outputs: List[List[float]] = None
        new_outputs: List[List[float]] = []
        iteration_count = 0
        while not has_converged:
            # Record state
            old_states = [(f, f.getFMUstate()) for f in scenario.fmus]

            # Feed the outputs recorded in the previous iteration
            no_output_records = previous_outputs is None
            output_index = 0
            for c in scenario.connections:
                if c.target_fmu is not None:
                    if c.value_type == VarType.REAL:
                        previous_output_value = None
                        if no_output_records:
                            new_output_value = c.source_fmu.getReal(c.source_vr)
                            previous_output_value = new_output_value
                        else:
                            previous_output_value = previous_outputs[output_index]
                        output_index += 1
                        c.target_fmu.setReal(c.target_vr, previous_output_value)
                    else:
                        # TODO: find a way to support the multiple types elegantly.
                        raise NotImplementedError()

            # Run cosim step
            for f in scenario.fmus:
                f.doStep(time, scenario.step_size)

            # Record new outputs, and check for convergence
            output_index = 0
            has_converged = True
            for c in scenario.connections:
                if c.target_fmu is not None:
                    if c.value_type == VarType.REAL:
                        # Gets the new output value, but forwards the previous output value.
                        # This way, we make sure that every FMU keeps getting updated outputs at every iteration.
                        # The propagation of outputs to inputs is slower this way,
                        #   but the alternative is to select a few strategic connections to do this,
                        #   which is harder to implement.
                        new_output_value = c.source_fmu.getReal(c.source_vr)
                        new_outputs.append(new_output_value)
                        if no_output_records:
                            has_converged = False
                        else:
                            previous_output_value = previous_outputs[output_index]
                            assert len(previous_output_value) == len(new_output_value), "Output sizes must be the same"
                            if has_converged:
                                for (po,no) in zip(previous_output_value, new_output_value):
                                    if (not np.isclose(po, no,rtol=self.tol,
                                                            atol=self.tol)):
                                        has_converged = False
                        output_index += 1
                    else:
                        # TODO: find a way to support the multiple types elegantly.
                        raise NotImplementedError()

            previous_outputs = new_outputs
            new_outputs = []

            # Check if convergence has been achieved, or the max number of iterations has been reached.
            iteration_count += 1
            has_converged = has_converged or iteration_count > self.max_iterations
            if not has_converged:
                # Rollback and Repeat if necessary
                for (f,s) in old_states:
                    f.setFMUstate(s)
