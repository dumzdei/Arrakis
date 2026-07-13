"""
@package measurement
Модуль для хранения результатов измерений электронных компонентов.
Предоставляет типизированные классы для IV и CV характеристик
с условиями проведения измерений.

@author Dmitry Nikolaenkov
@version 0
@date 11.07.2026
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np

@dataclass(frozen=True)
class MeasurementCondition:
    """
    @brief   Условия проведения измерения.
    @details Хранит температуру, фиксированные смещения и частоту.
    @tparam  temperature Температура измерения, °C
    @tparam  bias_conditions Смещение
    @tparam  frequency Частота измерения, Гц
    """
    temperature: float = 25.0
    bias_conditions: Dict[str, float] = field(default_factory=dict)
    frequency: Optional[float] = None
    
    @property
    def temperature_kelvin(self) -> float:
        return self.temperature + 273.15
    
    def get_bias(self, name: str, default: float = 0.0) -> float:
        """
        @brief  Получить значение фиксированного смещения.
        @param  name Имя смещения
        @param  default Значение по умолчанию
        @return Значение смещения
        """
        return self.bias_conditions.get(name, default)

@dataclass
class Measurement(ABC):
    """  
    @brief   Абстрактный базовый класс измерения.
    @details Определяет общий интерфейс для всех типов измерений.    
    @tparam  device_id Идентификатор устройства 
    @tparam  condition Условия измерения
    @tparam  setup     Тип измерения 
    @tparam  metadata  Дополнительные метаданные 
    """
    device_id: str
    condition: MeasurementCondition
    setup: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    @abstractmethod
    def measurement_type(self) -> str:
        pass
    
    @abstractmethod
    def get_sweep_variable(self) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_response_variables(self) -> Dict[str, np.ndarray]:
        pass

    def get_meta(self, key: str, default: Any = None) -> Any:
        """
        @brief Получить метаданные по ключу.
        @param key Имя поля
        """
        return self.metadata.get(key, default)


@dataclass
class IVMeasurement(Measurement):
    """
    @brief   Вольт-амперная характеристика.
    @details Хранит развёртку по напряжению и токи.
    
    @tparam sweep_variable Имя развёртывающей переменной 
    @tparam sweep_values   Массив значений развёртки 
    @tparam currents       Массив токов, А
    """
    sweep_variable: str = ""
    sweep_values: np.ndarray = field(default_factory=lambda: np.array([]))
    currents: Dict[str, np.ndarray] = field(default_factory=dict)
    
    @property
    def measurement_type(self) -> str:
        return "IV"
    
    def get_sweep_variable(self) -> np.ndarray:
        return self.sweep_values
    
    def get_response_variables(self) -> Dict[str, np.ndarray]:
        return self.currents.copy()
    
    def get_current(self, name: str) -> np.ndarray:
        """
        @brief           Получить ток по имени.
        @param  name     Имя тока 
        @return          Массив значений тока
        @throws KeyError Если ток не найден
        """
        if name not in self.currents:
            available = list(self.currents.keys())
            raise KeyError(
                f"Ток '{name}' не найден. Доступны: {available}"
            )
        return self.currents[name]

@dataclass
class CVMeasurement(Measurement):
    """
    @brief   Вольт-фарадная характеристика.
    @details Хранит развёртку по напряжению, ёмкость и опционально проводимость.
    
    @tparam  sweep_variable Имя развёртывающей переменной 
    @tparam  sweep_values   Массив значений развёртки
    @tparam  capacitance    Массив ёмкостей, Ф
    @tparam  conductance    Массив проводимостей, См 
    """
    sweep_variable: str = ""
    sweep_values: np.ndarray = field(default_factory=lambda: np.array([]))
    capacitance: np.ndarray = field(default_factory=lambda: np.array([]))
    conductance: Optional[np.ndarray] = None
    
    @property
    def measurement_type(self) -> str:
        return "CV"
    
    def get_sweep_variable(self) -> np.ndarray:
        return self.sweep_values
    
    def get_response_variables(self) -> Dict[str, np.ndarray]:
        result = {'C': self.capacitance}
        if self.conductance is not None:
            result['G'] = self.conductance
        return result

@dataclass
class MeasurementSet:
    """
    @brief   Набор всех измерений одного устройства.
    @details Контейнер для хранения нескольких IV и CV измерений,
    
    @tparam device_id    Идентификатор устройства
    @tparam measurements Список измерений
    """
    device_id: str
    measurements: List[Measurement] = field(default_factory=list)
    
    def add(self, measurement: Measurement) -> None:
        """
        @brief Добавить измерение в набор.

        @param  measurement Измерение для добавления
        @throws ValueError  Если device_id не совпадает
        """
        if measurement.device_id != self.device_id:
            raise ValueError(
                f"device_id не совпадает: ожидался '{self.device_id}', "
                f"получен '{measurement.device_id}'"
            )
        self.measurements.append(measurement)
    
    def get_iv(self, setup: Optional[str] = None) -> List[IVMeasurement]:
        """
        @brief  Получить все ВАХ, опционально фильтруя по setup.
        @param  setup Фильтр по типу setup
        @return Список ВАХ
        """
        result = [m for m in self.measurements 
                  if isinstance(m, IVMeasurement)]
        if setup is not None:
            result = [m for m in result if m.setup == setup]
        return result
    
    def get_cv(self, setup: Optional[str] = None) -> List[CVMeasurement]:
        """
        @brief  Получить все ВФХ, опционально фильтруя по setup
        @param  setup Фильтр по типу setup 
        @return Список CV измерений
        """
        result = [m for m in self.measurements 
                  if isinstance(m, CVMeasurement)]
        if setup is not None:
            result = [m for m in result if m.setup == setup]
        return result
    
    @property
    def num_measurements(self) -> int:
        return len(self.measurements)