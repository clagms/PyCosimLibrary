from enum import Enum,auto
from typing import List, Dict, Callable, Tuple
from fmpy.fmi2 import FMU2Slave
from cosimlibrary.autoinit import AutoInit


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

class OutputConnection(Connection):
    pass

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
                assert vr not in self.fmu_connections[c.source_fmu.instanceName].keys(), "Duplicate vr found."
                self.fmu_connections[c.source_fmu.instanceName][vr] = c
