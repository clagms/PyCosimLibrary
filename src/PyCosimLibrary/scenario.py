from enum import Enum,auto
from typing import List, Dict, Callable, Tuple
from fmpy.fmi2 import FMU2Slave
from PyCosimLibrary.autoinit import AutoInit


class VarType(Enum):
    REAL = auto()
    BOOL = auto()

class SignalType(Enum):
    CONTINUOUS = auto()
    DISCONTINUOUS = auto()

class Connection(AutoInit):
    value_type: VarType = None
    signal_type: SignalType = None
    quantization_tol: float = 1e-3 # Determines the different modes considered.
    source_fmu: FMU2Slave = None
    target_fmu: FMU2Slave = None
    source_vr: List[int] = None
    target_vr: List[int] = None
    
    def __init__(self, **args):
        super(Connection, self).__init__(**args)

    def __str__(self):
        string_repr = []
        for (src, trg) in zip(self.source_vr, self.target_vr):
            string_repr.append(f"{self.source_fmu.instanceName}.{src}->{self.target_fmu.instanceName}.{trg}")
        return f"[{', '.join(string_repr)}]"

class OutputConnection(Connection):
    def __str__(self):
        string_repr = []
        for src in self.source_vr:
            string_repr.append(f"{self.source_fmu.instanceName}.{src}->Out")
        return f"[{', '.join(string_repr)}]"

class CosimScenario(AutoInit):
    """
    This class represents a co-simulation scenario: fmu instances, how they are connected, and default parameters
    """
    fmus: List[FMU2Slave] = None
    connections: List[Connection] = None
    step_size: float = 1e-3
    stop_time: float = -1.0
    stop_condition: Connection = None
    print_interval: int = 1e-2
    record_inputs: bool = False
    outputs: List[OutputConnection] = None
    real_parameters: Dict[FMU2Slave, Tuple[List[int], List[float]]] = {}
    fmu_connections: Dict[str, Dict[int, Connection]]

    def __init__(self, **args):
        super().__init__(**args)

        # Build fmu connections
        self.fmu_connections = {}
        for c in self.outputs:
            if c.source_fmu.instanceName not in self.fmu_connections.keys():
                self.fmu_connections[c.source_fmu.instanceName] = {}
            for vr in c.source_vr:
                if (vr in self.fmu_connections[c.source_fmu.instanceName].keys()):
                    raise ValueError(f"Connection found with duplicate value reference {vr}: {c}")
                self.fmu_connections[c.source_fmu.instanceName][vr] = c
