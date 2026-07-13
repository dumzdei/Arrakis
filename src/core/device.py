"""
@package device
Модуль для хранения устройств.

@author Dmitry Nikolaenkov
@version 0
@date 12.07.2026
"""

from dataclasses import dataclass
from typing import Dict
from geometry import Geometry, DiodeGeometry, MOSFETGeometry
from device_parameters import DeviceParameters
from measurement import MeasurementSet

@dataclass
class Device:
    """
    @brief   Класс устройства.
    @details Связывает все компоненты устройства в единое целое.

    @tparam device_id    Идентификатор устройства
    @tparam device_type  Тип устройства
    @tparam geometry     Геометрия устройства
    @tparam parameters   Параметры устройства
    @tparam measurements Набор измерений
    """
    device_id: str
    device_type: str
    geometry: Geometry
    parameters: DeviceParameters
    measurements: MeasurementSet
    
    def get_parameter(self, name: str) -> float:
        """
        @brief  Получить значение параметра.
        @param  name Имя параметра
        @return Значение параметра
        """
        return self.parameters[name]
    
    def set_parameter(self, name: str, value: float):
        """
        @brief  Установить значение параметра.
        @param  name  Имя параметра
        @param  value Значение параметра
        """
        self.parameters[name] = value
    
    def update_parameters(self, params: Dict[str, float]):
        """
        @brief Массовое обновление параметров.
        @param params Словарь параметров
        """
        self.parameters.update(params)
    
    def get_geometry_info(self) -> Dict[str, float]:
        """
        @brief  Получить информацию о геометрии.
        @return Словарь с параметрами геометрии
        """
        info = {
            "effective_area": self.geometry.effective_area(),
            "scale_factor": self.geometry.scale_factor(),
        }
        
        if isinstance(self.geometry, DiodeGeometry):
            info.update({
                "area": self.geometry.area,
                "perimeter": self.geometry.perimeter,
                "num_devices": self.geometry.num_devices,
            })
        elif isinstance(self.geometry, MOSFETGeometry):
            info.update({
                "width": self.geometry.width,
                "length": self.geometry.length,
                "w_over_l": self.geometry.w_over_l,
                "fingers": self.geometry.fingers,
                "m": self.geometry.m,
            })
        
        return info
    
    def summary(self) -> str:
        """
        @brief  Краткое описание устройства.
        @return Строка с основной информацией
        """
        
        return (
            f"Device: {self.device_id}\n"
            f"Type: {self.device_type}\n"
            f"Measurements: {self.measurements.num_measurements}\n"
            f"Parameters: {len(self.parameters.values)}\n"
        )