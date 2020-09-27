from fmpy.fmi2 import fmi2OK

from .runner import CosimRunner
from .scenario import CosimScenario


class GaussSeidelRunner(CosimRunner):
    """
    This class implements the gauss seidel co-simulation algorithm.
    """

    def propagate_outputs_fmu(self, scenario, f):
        fmu_connections = filter(lambda c: c.source_fmu == f, scenario.connections)
        self.propagate_outputs(fmu_connections)

    def run_cosim_step(self, time, scenario: CosimScenario):
        for f in scenario.fmus:
            res = f.doStep(time, scenario.step_size)
            assert res == fmi2OK, "Step failed."
            self.propagate_outputs_fmu(scenario, f)