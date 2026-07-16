import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(ROOT))

from src.io.config.config_loader import ConfigLoader
from src.io.configurable_parser import ConfigurableParser


class MDMPaserTest(unittest.TestCase):
    def setUp(self):
        ConfigLoader._configs.clear()
        config_path = Path(ROOT) / 'io' / 'config' / 'mdm_format.yaml'
        ConfigLoader.load(str(config_path))

    def tearDown(self):
        ConfigLoader._configs.clear()

    def test_parse_real_mdm_file(self):
        project_root = ROOT.parent
        mdm_path = project_root / 'data' / 'measurements' / 'diode' / 'mdm' / 'dnw2' / 'iv' / '85' / 'diod1-5V~ndiode_Dn5_A32B640~10~iv_rev.mdm'
        self.assertTrue(mdm_path.exists(), f"MDM test file not found: {mdm_path}")
        parser = ConfigurableParser()
        device = parser.parse_file(str(mdm_path))
        print(device)
        self.assertEqual(device.device_id, 'ndiode_Dn5_A32B640')
        self.assertEqual(device.device_type, 'DIODE')
        self.assertGreater(device.measurements.num_measurements, 0)
        ivs = device.measurements.get_iv()
        self.assertTrue(len(ivs) >= 1)
        self.assertEqual(ivs[0].sweep_variable, 'V')
        self.assertIn('I', ivs[0].currents)


if __name__ == '__main__':
    unittest.main()
