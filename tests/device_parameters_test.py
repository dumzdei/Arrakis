import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(ROOT))

from src.core.device_parameters import DiodeParameters, MOSFETParameters


class DeviceParametersTest(unittest.TestCase):
    def test_diode_parameter_setting_and_getting(self):
        params = DiodeParameters(name='D1')
        params['IS'] = 1e-12
        self.assertEqual(params['IS'], 1e-12)
        self.assertEqual(params.to_dict(), {'IS': 1e-12})
        params.update({'N': 1.5})
        self.assertEqual(params['N'], 1.5)

    def test_mosfet_parameter_names_and_rejection(self):
        params = MOSFETParameters(name='M1')
        self.assertIn('VTH0', params.parameter_names)
        with self.assertRaises(ValueError):
            params['UNKNOWN'] = 0.1
        with self.assertRaises(KeyError):
            _ = params['VTH0']

    def test_update_raises_for_invalid_parameter(self):
        params = DiodeParameters(name='D2')
        with self.assertRaises(ValueError):
            params.update({'BAD': 1.0})


if __name__ == '__main__':
    unittest.main()
