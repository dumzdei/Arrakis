"""
@package device_parameters
Модуль для хранения параметров электронных компонентов.
Предоставляет классы для управления параметрами SPICE-моделей.

@author Dmitry Nikolaenkov
@version 0
@date 12.07.2026
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DeviceParameters(ABC):
    """
    @brief   Абстрактный класс параметров устройства.
    @details Базовый класс для всех типов параметров электронных компонентов.
    @tparam  name       Имя устройства 
    @tparam  values     Словарь значений параметров
    @tparam  confidence Словарь доверия к параметрам (0.0-1.0)
    """
    name: str
    values: Dict[str, float] = field(default_factory=dict)
    confidence: Dict[str, float] = field(default_factory=dict)

    @property
    @abstractmethod
    def parameter_names(self) -> List[str]:
        pass

    def __getitem__(self, key: str) -> float:
        """
        @brief  Доступ к параметру через квадратные скобки.
        @param  key Имя параметра
        @return Значение параметра
        @throws KeyError Если параметр не найден в values
        """
        if key not in self.values:
            raise KeyError(f"Параметр {key} не извлечён")
        return self.values[key]

    def __setitem__(self, key: str, value: float):
        """
        @brief  Установка значения параметра.
        @param  key   Имя параметра
        @param  value Значение параметра
        @throws ValueError Если параметр неизвестен для данного типа
        """
        if key not in self.parameter_names:
            raise ValueError(
                f"Неизвестный параметр {key} для {self.__class__.__name__}"
            )
        self.values[key] = value

    def update(self, params: Dict[str, float]):
        """
        @brief Массовая установка параметров.
        @param params Словарь параметров для установки
        """
        for key, value in params.items():
            self[key] = value

    def to_dict(self) -> Dict[str, float]:
        """
        @brief  Преобразовать параметры в словарь.
        @return Словарь значений параметров
        """
        return self.values.copy()


@dataclass
class DiodeParameters(DeviceParameters):
    @property
    def parameter_names(self) -> List[str]:
        return [
            "IS", "N", "RS", "TT", "CJO", "VJ", "M",
            "BV", "IBV", "EG", "XTI", "KF", "AF"
        ]


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

"""
@package device_parameters
Модуль для хранения параметров электронных компонентов.
Предоставляет классы для управления параметрами SPICE-моделей.
@author Dmitry Nikolaenkov
@version 1
@date 13.07.2026
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class DeviceParameters(ABC):
    """
    @brief   Абстрактный класс параметров устройства.
    @details Базовый класс для всех типов параметров электронных компонентов.
    @tparam  name       Имя устройства
    @tparam  values     Словарь значений параметров
    @tparam  confidence Словарь доверия к параметрам (0.0-1.0)
    """
    name: str
    values: Dict[str, float] = field(default_factory=dict)
    confidence: Dict[str, float] = field(default_factory=dict)
    
    @property
    @abstractmethod
    def parameter_names(self) -> List[str]:
        pass
    
    def __getitem__(self, key: str) -> float:
        """
        @brief  Доступ к параметру через квадратные скобки.
        @param  key Имя параметра
        @return Значение параметра
        @throws KeyError Если параметр не найден в values
        """
        if key not in self.values:
            raise KeyError(f"Параметр {key} не извлечён")
        return self.values[key]
    
    def __setitem__(self, key: str, value: float):
        """
        @brief  Установка значения параметра.
        @param  key   Имя параметра
        @param  value Значение параметра
        @throws ValueError Если параметр неизвестен для данного типа
        """
        if key not in self.parameter_names:
            raise ValueError(
                f"Неизвестный параметр {key} для {self.__class__.__name__}"
            )
        self.values[key] = value
    
    def update(self, params: Dict[str, float]):
        """
        @brief Массовая установка параметров.
        @param params Словарь параметров для установки
        """
        for key, value in params.items():
            self[key] = value
    
    def to_dict(self) -> Dict[str, float]:
        """
        @brief  Преобразовать параметры в словарь.
        @return Словарь значений параметров
        """
        return self.values.copy()

@dataclass
class DiodeParameters(DeviceParameters):
    @property
    def parameter_names(self) -> List[str]:
        return [
            "IS", "N", "RS", "TT", "CJO", "VJ", "M",
            "BV", "IBV", "EG", "XTI", "KF", "AF"
        ]

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
        ]
