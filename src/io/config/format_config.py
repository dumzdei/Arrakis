"""
@package format_config
Описание формата файла через конфигурацию.
Пользователь описывает структуру файла в YAML, 
а система автоматически создаёт парсер.
@author Dmitry Nikolaenkov
@version 0
@date 15.07.2026
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re

@dataclass
class ColumnConfig:
    """
    @brief  Конфигурация одной колонки данных.

    @tparam name Имя колонки
    @tparam type Тип данных (float, int, string)
    """
    name: str
    type: str = "float"


@dataclass
class MetadataFieldConfig:
    """
    @brief Конфигурация одного поля метаданных.

    @tparam pattern  Regex-паттерн для извлечения значения
    @tparam type     Тип данных (float, int, string)
    @tparam default  Значение по умолчанию
    @tparam required Обязательное поле
    """
    pattern: str
    type: str = "string"
    default: Any = None
    required: bool = False
    
    @property
    def compiled_pattern(self) -> re.Pattern:
        return re.compile(self.pattern, re.MULTILINE)


@dataclass
class DataSectionConfig:
    """
    @brief Конфигурация секции данных.

    @tparam start_marker  Маркер начала данных
    @tparam end_marker    Маркер конца данных
    @tparam separator     Разделитель колонок
    @tparam header_prefix Маркер заголовков
    """
    start_marker: str
    end_marker: str
    separator: str = " "
    header_prefix: str


@dataclass
class FormatConfig:
    """
    @brief Полная конфигурация формата файла.

    @tparam name      Название формата
    @tparam extension Расширение файла
    @tparam metadata  Конфигурация метаданных
    @tparam data      Конфигурация секций данных
    """
    name: str
    extension: str
    metadata: Dict[str, MetadataFieldConfig] = field(default_factory=dict)
    data: List[DataSectionConfig] = field(default_factory=list)
    encoding: str = "utf-8"
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'FormatConfig':
        """
        @brief Создать конфигурацию из словаря (загруженного из YAML).

        @param[in] config Словарь конфигурации

        @return Объект FormatConfig
        """
        fmt = config.get('format', config)
        
        metadata = {}
        for key, field_cfg in fmt.get('metadata', {}).items():
            metadata[key] = MetadataFieldConfig(
                pattern  = field_cfg['pattern'],
                type     = field_cfg.get('type', 'string'),
                default  = field_cfg.get('default'),
                required = field_cfg.get('required', False)
            )
        
        data_sections = []
        for section in fmt.get('data', []):
            data_sections.append(DataSectionConfig(
                start_marker  = section.get('start_marker'),
                end_marker    = section.get('end_marker'),
                separator     = section.get('separator', ' '),
                header_row    = section.get('header_row'),
                header_prefix = section.get('header_prefix')
            ))
        
        return cls(
            name      = fmt.get('name', 'Unknown'),
            extension = fmt.get('extension', '.txt'),
            metadata  = metadata,
            data      = data_sections,
            encoding  = fmt.get('encoding', 'utf-8')
        )