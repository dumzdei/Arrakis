from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np

@dataclass
class Measurement:
    """
    @brief Универсальное представление измерения для устройства.
    @todo TODO: улучшить валидацию и добавить валидацию геометрии
    """
    device_type: str
    model_target: str

    geometry: Dict[str, float] = field(default_factory=dict)

    temperature: float = 300.15  # К

    fixed_biases: Dict[str, float] = field(default_factory=dict)
    sweep_vars: Dict[str, np.ndarray] = field(default_factory=dict)
    measured_data: Dict[str, np.ndarray] = field(default_factory=dict)

    def validate(self, required_sweeps: List[str], required_outputs: List[str]):
        for req in required_sweeps:
            if req not in self.sweep_vars:
                raise ValueError(f"Нет развертки '{req}' в измерении {self.device_type}.")
        for req in required_outputs:
            if req not in self.measured_data:
                raise ValueError(f"Нет отклика '{req}' в измерении {self.device_type}.")
        
        # Проверка согласованности длин массивов
        if self.sweep_vars:
            sweep_len = len(next(iter(self.sweep_vars.values())))
            for key, arr in self.measured_data.items():
                if len(arr) != sweep_len:
                    raise ValueError(f"Длина '{key}' ({len(arr)}) != длина развертки ({sweep_len}).")

    def get_geometry_value(self, key: str, default: float = 1.0) -> float:
        """Безопасное получение значения геометрии."""
        return self.geometry.get(key, default)
