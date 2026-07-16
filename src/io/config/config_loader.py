"""
@package config_loader
Загрузчик конфигураций форматов из YAML файлов.
@author Dmitry Nikolaenkov
@version 0
@date 15.07.2026
"""
from pathlib import Path
from typing import Dict, Optional
import yaml

from .format_config import FormatConfig


class ConfigLoader:
    """
    @brief   Загрузчик конфигураций форматов.
    @details Загружает YAML-файлы с описанием форматов и 
             создаёт объекты FormatConfig.
    """
    
    _configs: Dict[str, FormatConfig] = {}
    
    @classmethod
    def load(cls, yaml_path: str) -> FormatConfig:
        """
        @brief  Загрузить конфигурацию из YAML файла.
        @param  yaml_path Путь к YAML файлу
        @return Объект FormatConfig
        @throws FileNotFoundError Если файл не найден
        @throws ValueError Если YAML некорректен
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл конфигурации не найден: {yaml_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        config = FormatConfig.from_dict(raw_config)
        cls._configs[config.extension] = config
        
        return config
    
    @classmethod
    def load_directory(cls, dir_path: str) -> int:
        """
        @brief  Загрузить все YAML из директории.
        @param  dir_path Путь к директории
        @return Количество загруженных конфигураций
        """
        path = Path(dir_path)
        if not path.is_dir():
            raise ValueError(f"Не директория: {dir_path}")
        
        count = 0
        for yaml_file in path.glob('*.yaml'):
            try:
                cls.load(str(yaml_file))
                count += 1
            except Exception as e:
                print(f"Ошибка загрузки {yaml_file}: {e}")
        
        return count
    
    @classmethod
    def get_config(cls, extension: str) -> Optional[FormatConfig]:
        """
        @brief  Получить конфигурацию по расширению.
        @param  extension Расширение файла (например, '.dat')
        @return FormatConfig или None
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        return cls._configs.get(extension.lower())
    
    @classmethod
    def list_formats(cls) -> Dict[str, str]:
        """
        @brief  Список загруженных форматов.
        @return Словарь {расширение: название}
        """
        return {ext: cfg.name for ext, cfg in cls._configs.items()}