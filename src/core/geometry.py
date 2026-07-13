"""
@package geometry
Модуль геометрии электронных компонентов.
Содержит иерархию классов для описания геометрии различных
типов устройств: диодов, MOSFET (возможно расширение).

@author Dmitry Nikolaenkov
@version 0
@date 10.07.2026
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class Geometry(ABC):
    """
    @brief   Абстрактный базовый класс геометрии устройства.
    @details Определяет интерфейс для всех типов геометрии.
    """

    @property
    @abstractmethod
    def geometry_type(self) -> str:
        pass

    @abstractmethod
    def effective_area(self) -> float:
        pass

    @abstractmethod
    def scale_factor(self) -> float:
        pass


@dataclass(frozen=True)
class DiodeGeometry(Geometry):
    """
    @brief  Геометрия диода.
    @tparam area        Площадь, м²
    @tparam perimeter   Периметр, м
    @tparam num_devices Количество параллельных диодов
    """
    area: float
    perimeter: float
    num_devices: int = 1

    @property
    def geometry_type(self) -> str:
        return "DIODE"

    def effective_area(self) -> float:
        return self.area * self.num_devices

    def scale_factor(self) -> float:
        return float(self.num_devices)


@dataclass(frozen=True)
class MOSFETGeometry(Geometry):
    """
    @brief  Геометрия МОП транзистора.
    @tparam width   Ширина W, м
    @tparam length  Длина L, м
    @tparam fingers Количество пальцев
    @tparam m       Множитель 
    """
    width: float
    length: float
    fingers: int = 1
    m: int = 1

    @property
    def geometry_type(self) -> str:
        return "MOSFET"

    @property
    def w_over_l(self) -> float:
        """
        @brief  Отношение ширины к длине канала.
        @return Значение W/L
        @throws ValueError Если длина <= 0
        """
        if self.length <= 0:
            raise ValueError(f"Length must be positive, got {self.length}")
        return self.width / self.length

    def effective_area(self) -> float:
        return self.width * self.length * self.fingers * self.m

    def scale_factor(self) -> float:
        return float(self.fingers * self.m)
