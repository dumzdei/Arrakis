"""
@package parser
Абстрактный класс для парсеров измерений.
Определяет единый интерфейс парсеров для всех форматов ввода.

@author Dmitry Nikolaenkov
@version 0
@date 13.07.2026
"""

from abc import ABC, abstractmethod
from pathlib import Path
import os
from typing import Union, List, Optional
from ..device import Device

class Parser(ABC):
    """
    @brief   Абстрактный класс парсера файлов измерений.
    @details Работает как с отдельными файлами так и с папками.
    """
    
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """
        @brief Список поддерживаемых расширений файлов.
        """
        pass
    
    def _parse(self, file_path):
        """
        @brief Обработка файла.
        """
        pass

    def _merge_devices(self, target: Device):
        

    def input_processing(self, *paths: Union[str, List[str]]):
        all_paths = []
        for arg in paths:
            if isinstance(arg, list):
                all_paths.extend(arg)
            else:
                all_paths.append(arg)
        
        files_to_process = []
        for path in all_paths:
            if os.path.isfile(path):
                files_to_process.append(path)
            elif os.path.isdir(path):
                for file in os.listdir(path):
                    full_path = os.path.join(path, file)
                    if os.path.isfile(full_path):
                        files_to_process.append(full_path)
            else:
                print(f"Предупреждение: путь не существует: {path}")
        
        for file_path in files_to_process:
            self._parse(file_path)
    
    
        