from fmpy.fmi2 import fmi2True, fmi2OK

from cosimlibrary.virtual_fmus import VirtualFMU


class MSD1(VirtualFMU):
    def __init__(self, instanceName):
        ref = 0
        self.x = ref;
        ref += 1
        self.v = ref;
        ref += 1
        self.m = ref;
        ref += 1
        self.c = ref;
        ref += 1
        self.cf = ref;
        ref += 1
        self.fe = ref;
        ref += 1

        super().__init__(instanceName, ref)

    def reset(self):
        super().reset()

        self.state[self.x] = 1.0
        self.state[self.v] = 0.0
        self.state[self.m] = 1.0
        self.state[self.c] = 1.0
        self.state[self.cf] = 1.0
        self.state[self.fe] = 0.0

    def doStep(self, currentCommunicationPoint, communicationStepSize, noSetFMUStatePriorToCurrentPoint=fmi2True):
        n = 10
        h = communicationStepSize / n
        for i in range(n):
            der_x = self.state[self.v]
            der_v = (1.0 / self.state[self.m]) * (- self.state[self.c] * self.state[self.x]
                                                  - self.state[self.cf] * self.state[self.v]
                                                  + self.state[self.fe])

            self.state[self.x] = self.state[self.x] + der_x * h
            self.state[self.v] = self.state[self.v] + der_v * h

        return fmi2OK


class MSD2(VirtualFMU):
    def __init__(self, instanceName):
        ref = 0
        self.x = ref;
        ref += 1
        self.v = ref;
        ref += 1
        self.m = ref;
        ref += 1
        self.c = ref;
        ref += 1
        self.cf = ref;
        ref += 1
        self.ce = ref;
        ref += 1
        self.cef = ref;
        ref += 1
        self.fe = ref;
        ref += 1
        self.xe = ref;
        ref += 1
        self.ve = ref;
        ref += 1

        super().__init__(instanceName, ref)

    def reset(self):
        super().reset()

        self.state[self.x] = 0.0
        self.state[self.v] = 0.0
        self.state[self.m] = 1.0
        self.state[self.c] = 1.0
        self.state[self.cf] = 0.0
        self.state[self.ce] = 1.0
        self.state[self.cef] = 1.0
        self.state[self.fe] = 0.0
        self.state[self.xe] = 0.0
        self.state[self.ve] = 0.0

    def doStep(self, currentCommunicationPoint, communicationStepSize, noSetFMUStatePriorToCurrentPoint=fmi2True):
        n = 10
        h = communicationStepSize / n
        for i in range(n):
            self.state[self.fe] = self.state[self.ce] * (self.state[self.x] - self.state[self.xe]) \
                                  + self.state[self.cef] * (self.state[self.v] - self.state[self.ve])

            der_x = self.state[self.v]
            der_v = (1.0 / self.state[self.m]) * (- self.state[self.c] * self.state[self.x]
                                                  - self.state[self.cf] * self.state[self.v]
                                                  - self.state[self.fe])

            self.state[self.x] = self.state[self.x] + der_x * h
            self.state[self.v] = self.state[self.v] + der_v * h

        return fmi2OK