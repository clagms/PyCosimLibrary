from fmpy.fmi2 import fmi2OK

from cosimlibrary.runner import CosimRunner
from cosimlibrary.scenario import CosimScenario


class JacobiRunner(CosimRunner):
    """
    This class implements the jacobi co-simulation algorithm.
    """
    def run_cosim_step(self, time, scenario: CosimScenario):
        for f in scenario.fmus:
            res = f.doStep(time, scenario.step_size)
            assert res == fmi2OK, "Step failed."
        self.propagate_outputs(scenario)
