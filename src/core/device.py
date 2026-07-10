## @package device_parameters
#  Модуль для хранения параметров электронных компонентов.
#
#  Предоставляет классы для управления параметрами SPICE-моделей
#
#  @author Dmitry Nikolaenkov
#  @version 0
#  @date 10.07.2026

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List


## @brief Абстрактный класс параметров устройства.
#  @details Базовый класс для всех типов параметров электронных компонентов.
#  Обеспечивает унифицированный доступ к значениям параметров через словари
#  и поддержку доверительных интервалов.
#
#  @tparam name Имя устройства (например, "Q1", "D1")
#  @tparam values Словарь значений параметров
#  @tparam confidence Словарь доверия к параметрам (0.0-1.0)
@dataclass
class DeviceParameters(ABC):
    name: str
    values: Dict[str, float] = field(default_factory=dict)
    confidence: Dict[str, float] = field(default_factory=dict)  # доверие к параметру
    
    ## @brief Список всех допустимых параметров для данного типа.
    @property
    @abstractmethod
    def parameter_names(self) -> List[str]:
        pass
    
    ## @brief Доступ к параметру через квадратные скобки.
    #  @param key Имя параметра
    #  @return Значение параметра
    #  @throws KeyError Если параметр не найден в values
    def __getitem__(self, key: str) -> float:
        if key not in self.values:
            raise KeyError(f"Параметр {key} не извлечён")
        return self.values[key]
    
    ## @brief Установка значения параметра.
    #  @param key Имя параметра
    #  @param value Значение параметра
    #  @throws ValueError Если параметр неизвестен для данного типа
    def __setitem__(self, key: str, value: float):
        if key not in self.parameter_names:
            raise ValueError(f"Неизвестный параметр {key} для {self.__class__.__name__}")
        self.values[key] = value
    
    def to_dict(self) -> Dict[str, float]:
        return self.values.copy()

## @brief Класс параметров диода.
@dataclass
class DiodeParameters(DeviceParameters):
    
    @property
    def parameter_names(self) -> List[str]:
        return [
            "IS", "N", "RS", "TT", "CJO", "VJ", "M", 
            "BV", "IBV", "EG", "XTI", "KF", "AF"
        ]

## @brief Класс параметров BSIM3/BSIM4.
@dataclass
class MOSFETParameters(DeviceParameters):
    
    @property
    def parameter_names(self) -> List[str]:
        return [
            # Пороговые
            "VTH0", "K1", "K2", "U0", "TOX",
            # Короткоканальные
            "DVT0", "DVT1", "DVT2", "DSUB",
            # Подпорог
            "NFACTOR", "VOFF", "CIT",
            # Токи
            "VSAT", "ETA0", "ETAB",
            # Ёмкости
            "CGSO", "CGDO", "CGBO", "CJSW", "CJ",
            # И другие (нужно расширять)
        ]
