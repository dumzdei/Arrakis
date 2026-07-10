## @package geometry
#  Модуль геометрии электронных компонентов.
#
#  Содержит иерархию классов для описания геометрии различных
#  типов устройств: диодов, MOSFET (возмозжно расширение)
#
#  @author Dmitry Nikolaenkov
#  @version 0
#  @date 10.07.2026

from abc import ABC, abstractmethod
from dataclasses import dataclass

## @brief Абстрактный базовый класс геометрии устройства.
#  @details Определяет интерфейс для всех типов геометрии.

@dataclass(frozen=True)
class Geometry(ABC):
    ## @brief Тип геометрии устройства
    #  @return str Тип геометрии (например, "DIODE", "MOSFET")    
    @property
    @abstractmethod
    def geometry_type(self) -> str:
        """Тип геометрии"""
        pass
    
    @abstractmethod
    def effective_area(self) -> float:
        """Эффективная площадь устройства"""
        pass
    
    @abstractmethod
    def scale_factor(self) -> float:
        """Коэффициент масштабирования (для multi-finger и т.п.)"""
        pass


## @brief Геометрия диода.
@dataclass(frozen=True)
class DiodeGeometry(Geometry):
    area: float         # м²
    perimeter: float    # м
    num_devices: int = 1  # количество параллельных диодов
    
    @property
    def geometry_type(self) -> str:
        return "DIODE"
    
    def effective_area(self) -> float:
        return self.area * self.num_devices
    
    def scale_factor(self) -> float:
        return float(self.num_devices)

## @brief Геометрия MOSFET транзистора.
@dataclass(frozen=True)
class MOSFETGeometry(Geometry):
    width: float        # W, м
    length: float       # L, м
    fingers: int = 1    # количество пальцев
    m: int = 1          # множитель (parallel devices)
    
    @property
    def geometry_type(self) -> str:
        return "MOSFET"
    
    @property
    def w_over_l(self) -> float:
        return self.width / self.length
    
    def effective_area(self) -> float:
        return self.width * self.length * self.fingers * self.m
    
    def scale_factor(self) -> float:
        return float(self.fingers * self.m)