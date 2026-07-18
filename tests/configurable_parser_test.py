import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(ROOT))

import numpy as np
from src.io.config.format_config import (
    FormatConfig,
    DataSectionConfig,
    ColumnConfig,
    MetadataFieldConfig,
)
from src.io.config.config_loader import ConfigLoader
from src.io.configurable_parser import ConfigurableParser
from src.core.measurement import MeasurementSet, IVMeasurement, CVMeasurement, MeasurementCondition


class ConfigurableParserTest(unittest.TestCase):
    def setUp(self):
        ConfigLoader._configs.clear()

    def tearDown(self):
        ConfigLoader._configs.clear()

    def _make_column(self, name, type='float', response_variable=None):
        return ColumnConfig(name=name, type=type, response_variable=response_variable)

    def _make_data_section(self, start_marker=None, end_marker=None, separator=' ', header_prefix=None, header_row=None):
        return DataSectionConfig(
            start_marker=start_marker,
            end_marker=end_marker,
            separator=separator,
            header_prefix=header_prefix,
            header_row=header_row
        )

    def make_config(self):
        metadata = {
            'device_id': MetadataFieldConfig(pattern=r'Device:\s*(\S+)', type='string', required=True),
            'temperature': MetadataFieldConfig(pattern=r'Temperature:\s*([\d\.]+)', type='float', default=25.0)
        }
        data = [
            self._make_data_section(
                start_marker='BEGIN DATA',
                end_marker='END DATA',
                separator=',',
                header_prefix='#'
            )
        ]
        return FormatConfig('Test', '.dat', metadata=metadata, data=data)

    def test_read_file_raises_if_no_config_loaded(self):
        parser = ConfigurableParser()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'test.dat'
            file_path.write_text('Device: D1\n', encoding='utf-8')

            with self.assertRaises(ValueError):
                parser._read_file(str(file_path))

    def test_extract_metadata_and_parse_measurements(self):
        config = self.make_config()
        parser = ConfigurableParser(config=config)

        raw_text = (
            'Device: D1\n'
            'Temperature: 42.5\n'
            'BEGIN DATA\n'
            '# V I\n'
            '0.0,1.0\n'
            '1.0,2.0\n'
            'END DATA\n'
        )

        metadata = parser._extract_metadata(raw_text, 'file.dat')
        self.assertEqual(metadata['device_id'], 'D1')
        self.assertEqual(metadata['temperature'], 42.5)

        measurements = parser._parse_measurements(raw_text, metadata)
        self.assertIsInstance(measurements, MeasurementSet)
        self.assertEqual(measurements.device_id, 'D1')
        self.assertEqual(measurements.num_measurements, 1)

        iv = measurements.get_iv()[0]
        self.assertIsInstance(iv, IVMeasurement)
        np.testing.assert_allclose(iv.get_sweep_variable(), np.array([0.0, 1.0]))
        np.testing.assert_allclose(iv.get_current('I'), np.array([1.0, 2.0]))
        self.assertEqual(iv.condition.temperature, 42.5)

    def test_parse_columns_skips_invalid_rows_and_comments(self):
        config = self.make_config()
        parser = ConfigurableParser(config=config)

        raw_text = (
            'Device: D1\n'
            'Temperature: 25.0\n'
            'BEGIN DATA\n'
            '# comment line\n'
            '0.0,1.0\n'
            'invalid,2.0\n'
            '1.0,3.0\n'
            'END DATA\n'
        )
        metadata = parser._extract_metadata(raw_text, 'file.dat')
        measurements = parser._parse_measurements(raw_text, metadata)

        iv = measurements.get_iv()[0]
        np.testing.assert_allclose(iv.get_sweep_variable(), np.array([0.0, 1.0]))
        np.testing.assert_allclose(iv.get_current('I'), np.array([1.0, 3.0]))

    def test_parse_cv_measurement(self):
        metadata = {
            'device_id': 'D1',
            'temperature': 25.0
        }
        data = [
            self._make_data_section(
                start_marker='BEGIN DATA',
                end_marker='END DATA',
                separator=',',
                header_prefix='#'
            )
        ]
        config = FormatConfig('CVTest', '.dat', metadata={}, data=data)
        parser = ConfigurableParser(config=config)

        raw_text = (
            'BEGIN DATA\n'
            '0.0,1.0,0.1\n'
            '1.0,2.0,0.2\n'
            'END DATA\n'
        )

        measurements = parser._parse_measurements(raw_text, metadata)
        self.assertEqual(measurements.num_measurements, 1)

        cv = measurements.get_cv()[0]
        self.assertIsInstance(cv, CVMeasurement)
        np.testing.assert_allclose(cv.get_sweep_variable(), np.array([0.0, 1.0]))
        np.testing.assert_allclose(cv.capacitance, np.array([1.0, 2.0]))
        np.testing.assert_allclose(cv.conductance, np.array([0.1, 0.2]))

    def test_infer_columns_and_measurement_type_from_setup(self):
        metadata = {
            'device_id': 'D1',
            'temperature': 25.0,
            'setup': 'cv'
        }
        data = [
            self._make_data_section(
                start_marker='BEGIN DATA',
                end_marker='END DATA',
                separator='',
                header_prefix='#'
            )
        ]
        config = FormatConfig('HeaderInfer', '.dat', metadata={}, data=data)
        parser = ConfigurableParser(config=config)

        raw_text = (
            'BEGIN DATA\n'
            '#V C G\n'
            '0.0 1.0 0.1\n'
            '1.0 2.0 0.2\n'
            'END DATA\n'
        )

        measurements = parser._parse_measurements(raw_text, metadata)
        self.assertEqual(measurements.num_measurements, 1)

        cv = measurements.get_cv()[0]
        self.assertEqual(cv.setup, 'cv')
        self.assertEqual(cv.sweep_variable, 'V')
        np.testing.assert_allclose(cv.capacitance, np.array([1.0, 2.0]))
        np.testing.assert_allclose(cv.conductance, np.array([0.1, 0.2]))


if __name__ == '__main__':
    unittest.main()
