from typing import Dict, List


class CosimResults:
    out_signals: Dict[str, Dict[int, List[float]]] # Stores all out_signals in a continuous timeline (consistent with timestamps)
    timestamps: List[float]
    abstract_modes: Dict[str, Dict[int, List[float]]] # Stores the sequences of modes (not consistent with timeline)
