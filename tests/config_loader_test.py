import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(ROOT))

import yaml
from src.io.config.config_loader import ConfigLoader
from src.io.config.format_config import FormatConfig, DataSectionConfig, ColumnConfig


class ConfigLoaderTest(unittest.TestCase):
    def setUp(self):
        ConfigLoader._configs.clear()

    def tearDown(self):
        ConfigLoader._configs.clear()

    def test_load_yaml_config_and_get_config(self):
        config_dict = {
            'format': {
                'name': 'Test Format',
                'extension': '.dat',
                'encoding': 'utf-8',
                'metadata': {
                    'device_id': {
                        'pattern': r'Device:\s*(\S+)',
                        'type': 'string'
                    }
                },
                'data': [
                    {
                        'columns': [
                            {'name': 'V', 'type': 'float'},
                            {'name': 'I', 'type': 'float', 'measurement': 'IV'}
                        ]
                    }
                ]
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / 'test_format.yaml'
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f)

            config = ConfigLoader.load(str(yaml_path))

            self.assertEqual(config.name, 'Test Format')
            self.assertEqual(config.extension, '.dat')
            self.assertEqual(len(config.data), 1)
            self.assertEqual(config.data[0].columns[1].measurement, 'IV')
            self.assertIs(config, ConfigLoader.get_config('.dat'))
            self.assertEqual(ConfigLoader.list_formats(), {'.dat': 'Test Format'})

    def test_load_directory_counts_yaml_configs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_dir = Path(tmpdir)
            for i in range(2):
                config_dict = {
                    'format': {
                        'name': f'Fmt{i}',
                        'extension': f'.ext{i}',
                        'metadata': {},
                        'data': []
                    }
                }
                config_path = yaml_dir / f'cfg{i}.yaml'
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_dict, f)

            count = ConfigLoader.load_directory(str(yaml_dir))
            self.assertEqual(count, 2)
            self.assertEqual(ConfigLoader.list_formats(), {'.ext0': 'Fmt0', '.ext1': 'Fmt1'})

    def test_get_config_normalizes_extension(self):
        config = FormatConfig('T', '.dat', {}, [])
        ConfigLoader._configs['.dat'] = config

        self.assertIs(ConfigLoader.get_config('dat'), config)
        self.assertIs(ConfigLoader.get_config('.dat'), config)


if __name__ == '__main__':
    unittest.main()
