from typing import List, Callable

from fmpy.fmi2 import FMU2Slave, fmi2OK, fmi2True


class VirtualFMU(FMU2Slave):
    """
    Utility class to override the FMI2 C methods.
    """
    state: List[float] = None
    state_size: int = 0

    def __init__(self, instanceName: str, state_size: int):
        self.instanceName = instanceName
        self.state_size = state_size
        self.reset()

    def reset(self):
        self.state = [0.0] * self.state_size

    def instantiate(self, visible=False, callbacks=None, loggingOn=False):
        pass

    def terminate(self):
        pass

    def doStep(self, currentCommunicationPoint, communicationStepSize, noSetFMUStatePriorToCurrentPoint=fmi2True):
        return fmi2OK

    def setupExperiment(self, tolerance=None, startTime=0.0, stopTime=None):
        pass

    def enterInitializationMode(self):
        pass

    def exitInitializationMode(self):
        pass

    def getReal(self, vr):
        values = [self.state[v] for v in vr]
        return values

    def getInteger(self, vr):
        values = self.getReal(vr)
        return [int(n) for n in values]

    def getBoolean(self, vr):
        values = self.getReal(vr)
        return [v > 0.5 for v in values]

    def setReal(self, vr, value):
        for i in range(len(value)):
            self.state[vr[i]] = value[i]

    def setInteger(self, vr, value):
        self.setReal(vr, value)

    def setBoolean(self, vr, value):
        self.setReal(vr, [(1.0 if b else 0.0) for b in value])

    def getFMUstate(self):
        return self.state.copy()

    def setFMUstate(self, state):
        self.state = state.copy()
