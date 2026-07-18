"""
@package configurable_parser
Универсальный парсер, работающий по YAML-конфигурации.
Пользователь описывает формат файла, а этот класс парсит его.
@author Dmitry Nikolaenkov
@version 0
@date 15.07.2026
"""
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

from .config.format_config import FormatConfig, DataSectionConfig, ColumnConfig
from .config.config_loader import ConfigLoader
from ..core.device import Device
from ..core.geometry import DiodeGeometry, MOSFETGeometry
from ..core.device_parameters import DiodeParameters, MOSFETParameters
from ..core.measurement import MeasurementSet, IVMeasurement, CVMeasurement, MeasurementCondition

class ConfigurableParser:
    """
    @brief   Парсер, работающий по YAML-конфигурации.
    @details Пользователь описывает формат файла в YAML,
             а этот класс автоматически парсит файлы этого формата.
    """
    
    def __init__(self, config: Optional[FormatConfig] = None):
        """
        @brief Конструктор.

        @param[in] config Конфигурация формата (или None для автоопределения)
        """
        self._config = config
        self._raw_content: str = ""
        self._file_path: str = ""
    
    def set_config(self, config: FormatConfig) -> None:
        """Установить конфигурацию вручную."""
        self._config = config
    
    def _read_file(self, file_path: str) -> str:
        """Чтение файла как текст."""
        self._file_path = file_path
        
        # Автоопределение конфигурации по расширению
        if self._config is None:
            ext = Path(file_path).suffix.lower()
            self._config = ConfigLoader.get_config(ext)
            ## @todo TODO: заменить загрузку вручную на что-то нормальное
            if self._config is None:
                raise ValueError(
                    f"Конфигурация для формата '{ext}' не загружена. "
                )
        
        with open(file_path, 'r', encoding=self._config.encoding) as f:
            self._raw_content = f.read()
        
        return self._raw_content
    
    def _extract_metadata(self, raw_data: str, file_path: str) -> Dict[str, Any]:
        """Извлечение метаданных по regex-паттернам."""
        metadata = {}
        
        for key, field_cfg in self._config.metadata.items():
            match = field_cfg.compiled_pattern.search(raw_data)
            
            if match:
                value_str = match.group(1).strip()
                metadata[key] = self._convert_value(value_str, field_cfg.type)
            elif field_cfg.default is not None:
                metadata[key] = field_cfg.default
            elif field_cfg.required:
                raise ValueError(
                    f"Обязательное поле '{key}' не найдено в {file_path}"
                )
        
        if 'device_id' not in metadata:
            metadata['device_id'] = Path(file_path).stem
        
        return metadata
    
    def _convert_value(self, value_str: Any, value_type: str) -> Any:
        """Конвертация строки или числового значения в нужный тип."""
        try:
            if value_type == 'float':
                if isinstance(value_str, (int, float)):
                    return float(value_str)
                return self._parse_si_value(value_str)
            elif value_type == 'int':
                if isinstance(value_str, (int, float)):
                    return int(value_str)
                return int(self._parse_si_value(value_str))
            else:
                return value_str
        except (ValueError, TypeError) as e:
            raise ValueError(f"Не удалось конвертировать '{value_str}' в {value_type}: {e}")

    def _parse_si_value(self, value_str: Any) -> float:
        """Парсинг числового значения с SI-суффиксом или возврат числового значения."""
        if isinstance(value_str, (int, float)):
            return float(value_str)

        text = str(value_str).strip().lower()
        if not text:
            raise ValueError("Пустое значение для числового поля")

        units = {
            'p': 1e-12,
            'n': 1e-9,
            'u': 1e-6,
            'm': 1e-3,
            'k': 1e3,
            'meg': 1e6,
            'g': 1e9,
            't': 1e12,
        }
        # Strip optional quotes and spaces
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1].strip()

        for unit, factor in units.items():
            if unit and text.endswith(unit):
                return float(text[:-len(unit)]) * factor

        return float(text)
    
    def _parse_measurements(self, raw_data: str, metadata: Dict) -> MeasurementSet:
        """Парсинг всех секций данных."""
        device_id = metadata.get('device_id', 'unknown')
        temperature = metadata.get('temperature', 25.0)
        bias_conditions = {
            key: metadata[key]
            for key in ('vb', 'vd', 'vs')
            if key in metadata
        }
        
        measurement_set = MeasurementSet(device_id=device_id)
        condition = MeasurementCondition(
            temperature=temperature,
            bias_conditions=bias_conditions
        )
        
        # Парсим каждую секцию данных
        for section_cfg in self._config.data:
            measurements = self._parse_data_section(raw_data, section_cfg, device_id, condition, metadata)
            for m in measurements:
                measurement_set.add(m)
        
        return measurement_set
    
    def _parse_data_section(
        self, 
        raw_data: str, 
        section_cfg: DataSectionConfig,
        device_id: str,
        condition: MeasurementCondition,
        metadata: Dict[str, Any]
    ) -> List:
        """Парсинг одной секции данных."""
        lines = raw_data.split('\n')
        
        start_indices = self._find_section_starts(lines, section_cfg)
        if not start_indices:
            return []

        measurements = []
        for start_idx in start_indices:
            end_idx = self._find_section_end(lines, start_idx, section_cfg)
            
            data_lines = []
            header_line = None
            for i in range(start_idx, end_idx):
                raw_line = lines[i]
                stripped = raw_line.strip()

                if not stripped:
                    continue

                # Сохраняем строку заголовка
                if (section_cfg.header_prefix is not None
                        and stripped.startswith(section_cfg.header_prefix)):
                    header_line = stripped
                    continue


                data_lines.append(stripped)

            if data_lines and header_line is not None:
                section_columns = self._get_columns_from_header(header_line, section_cfg)
                measurements.extend(
                    self._parse_columns(
                        data_lines,
                        section_cfg,
                        device_id,
                        condition,
                        section_columns,
                        metadata.get('setup', '')
                    )
                )
        
        return measurements
    
    def _find_section_start(self, lines: List[str], section_cfg: DataSectionConfig) -> Optional[int]:
        """Поиск начала секции данных."""
        if section_cfg.start_marker:
            for i, line in enumerate(lines):
                if section_cfg.start_marker in line:
                    return i + 1  # Данные начинаются после маркера
        elif section_cfg.start_line is not None:
            return section_cfg.start_line
        else:
            return 0  # По умолчанию — с начала файла
        
        return None

    def _find_section_starts(self, lines: List[str], section_cfg: DataSectionConfig) -> List[int]:
        """Найти все начала секции данных."""
        if section_cfg.start_marker:
            return [i + 1 for i, line in enumerate(lines) if section_cfg.start_marker in line]
        else:
            return [0]
    
    def _find_section_end(self, lines: List[str], start_idx: int, section_cfg: DataSectionConfig) -> int:
        """Поиск конца секции данных."""
        if section_cfg.end_marker:
            for i in range(start_idx, len(lines)):
                if section_cfg.end_marker in lines[i]:
                    return i
        return len(lines)

    def _get_columns_from_header(
        self,
        header_line: str,
        section_cfg: DataSectionConfig
    ) -> List[ColumnConfig]:
        """Извлечение колонок из строки заголовка."""
        header_text = header_line.strip()
        if section_cfg.header_prefix and header_text.startswith(section_cfg.header_prefix):
            header_text = header_text[len(section_cfg.header_prefix):].strip()

        names = header_text.split(sep=section_cfg.separator)
        if not names:
            raise ValueError("Не удалось извлечь колонки данных: пустая строка заголовка")

        columns: List[ColumnConfig] = []
        for name in names:
            columns.append(ColumnConfig(name=name, type='string'))
        return columns

    def _parse_columns(
        self,
        data_lines: List[str],
        section_cfg: DataSectionConfig,
        columns: Optional[List[ColumnConfig]] = None
    ) -> List:
        """Парсинг колонок."""
        if columns is not None:
            section_columns = columns 
        else:
            []
        if not section_columns:
            return []

        columns_data: Dict[str, List] = {col.name: [] for col in section_columns}
        
        for line in data_lines:
            if section_cfg.separator is None:
                parts = line.split()
            else:
                parts = line.split(section_cfg.separator)
            row_values: Dict[str, Any] = {}
            valid_row = True
            
            for i, col_cfg in enumerate(section_columns):
                if i >= len(parts):
                    raise ValueError(
                        f"Ожидается {i} колонок, "
                        f"получено {len(parts)}. "
                        f"Содержимое строки: '{line.strip()}'"
                    )
                value_str = parts[i].strip()
                try:
                    row_values[col_cfg.name] = self._convert_value(value_str, col_cfg.type)
                except ValueError:
                    valid_row = False
                    break
            
            if not valid_row:
                continue
            
            for name, value in row_values.items():
                columns_data[name].append(value)
        
        sweep_variable = None
        sweep_values = None
        measurements_by_type: Dict[str, np.ndarray] = {}
        for i, col_cfg in enumerate(section_columns):
            if i == 0:
                sweep_variable = col_cfg.name
                sweep_values = np.array(columns_data[col_cfg.name])
            else:
                var_name = col_cfg.name
                measurements_by_type[var_name] = np.array(columns_data[col_cfg.name])

        if sweep_values is None:
            return []

        measurements = []
        ## @todo TODO: закончить создание измерения из колонок
        return measurements

    def parse_file(self, file_path: str) -> Device:
        """Полный разбор файла в объект Device."""
        raw_data = self._read_file(file_path)
        metadata = self._extract_metadata(raw_data, file_path)
        measurements = self._parse_measurements(raw_data, metadata)
        return self._build_device(metadata, measurements)

    def _build_device(self, metadata: Dict, measurements: MeasurementSet) -> Device:
        """Сборка устройства."""
        device_id = metadata.get('device_id', 'unknown')
        device_type = metadata.get('device_type', 'DIODE').upper()
        if device_type == 'DIO':
            device_type = 'DIODE'
        elif device_type == 'MOS':
            device_type = 'MOSFET'
        
        # Создаём геометрию
        if device_type == 'DIODE':
            geometry = DiodeGeometry(
                area=self._parse_si_value(metadata.get('area', 1e-8)),
                perimeter=self._parse_si_value(metadata.get('perimeter', 1e-4)),
                device_num=metadata.get('device_num', 1)
            )
            parameters = DiodeParameters(name=device_id)
        elif device_type == 'MOSFET':
            geometry = MOSFETGeometry(
                width=self._parse_si_value(metadata.get('width', 1e-6)),
                length=self._parse_si_value(metadata.get('length', 1e-6)),
                fingers=int(self._parse_si_value(metadata.get('fingers', 1))),
                m=int(self._parse_si_value(metadata.get('m', 1)))
            )
            parameters = MOSFETParameters(name=device_id)
        else:
            raise ValueError(f"Неизвестный тип устройства: {device_type}")
        
        return Device(
            device_id=device_id,
            device_type=device_type,
            geometry=geometry,
            parameters=parameters,
            measurements=measurements
        )