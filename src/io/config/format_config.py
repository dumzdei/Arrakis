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
from typing import List, Optional, Dict, Any, Union
import re

@dataclass
class ColumnConfig:
    """
    @brief  Конфигурация одной колонки данных.
    @tparam name              Имя колонки
    @tparam type              Тип данных (float, int, string)
    @tparam measurement       Тип измерения (IV, CV) или None
    @tparam response_variable Для CV: имя емкости, для IV: имя тока
    """
    name: str
    type: str = "float"
    measurement: Optional[str] = None
    response_variable: Optional[str] = None


@dataclass
class MetadataFieldConfig:
    """
    @brief  Конфигурация одного поля метаданных.
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
    @brief  Конфигурация секции данных.
    @tparam start_marker   Маркер начала данных (или номер строки)
    @tparam end_marker     Маркер конца данных (опционально)
    @tparam separator      Разделитель колонок
    @tparam header_row     Строка с заголовками (или None)
    @tparam skip_comments  Пропускать строки-комментарии
    @tparam skip_prefixes  Список префиксов строк, которые нужно пропустить
    @tparam columns        Список конфигурации колонок
    """
    columns: List[ColumnConfig] = field(default_factory=list)
    start_marker: Optional[str] = None
    start_line: Optional[int] = None
    end_marker: Optional[str] = None
    separator: str = ","
    header_row: Optional[int] = None
    skip_comments: bool = False
    skip_prefixes: List[str] = field(default_factory=list)


@dataclass
class FormatConfig:
    """
    @brief  Полная конфигурация формата файла.
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
        @brief  Создать конфигурацию из словаря (загруженного из YAML).
        @param  config Словарь конфигурации
        @return Объект FormatConfig
        """
        fmt = config.get('format', config)
        
        metadata = {}
        for key, field_cfg in fmt.get('metadata', {}).items():
            metadata[key] = MetadataFieldConfig(
                pattern=field_cfg['pattern'],
                type=field_cfg.get('type', 'string'),
                default=field_cfg.get('default'),
                required=field_cfg.get('required', False)
            )
        
        data_sections = []
        for section in fmt.get('data', []):
            columns = [
                ColumnConfig(
                    name=col['name'],
                    type=col.get('type', 'float'),
                    measurement=col.get('measurement'),
                    response_variable=col.get('response_variable')
                )
                for col in section.get('columns', [])
            ]
            
            data_sections.append(DataSectionConfig(
                columns=columns,
                start_marker=section.get('start_marker'),
                start_line=section.get('start_line'),
                end_marker=section.get('end_marker'),
                separator=section.get('separator', ','),
                header_row=section.get('header_row'),
                skip_comments=section.get('skip_comments', False),
                skip_prefixes=section.get('skip_prefixes', [])
            ))
        
        return cls(
            name=fmt.get('name', 'Unknown'),
            extension=fmt.get('extension', '.txt'),
            metadata=metadata,
            data=data_sections,
            encoding=fmt.get('encoding', 'utf-8')
        )