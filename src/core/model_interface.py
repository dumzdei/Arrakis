from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Optional
import numpy as np
from .measurement import Measurement

@dataclass(frozen=True)
class ParameterDefinition:
    bounds: tuple[float, float]
    initial_guess: float
    unit: str = ""

@dataclass(frozen=True)
class ExtractionStep:
    name: str
    active_params: List[str]
    data_filter: Optional[Callable[[Measurement], Measurement]] = None
    target_outputs: List[str] = field(default_factory=list)
    target_sweeps: List[str] = field(default_factory=list)

class CompactModel(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def parameter_definitions(self) -> Dict[str, Dict[str, Any]]: ...

    @abstractmethod
    def evaluate(self, measurement: Measurement, params: Dict[str, float]) -> np.ndarray: ...

    @abstractmethod
    def get_extraction_flow(self) -> List[ExtractionStep]: ...
