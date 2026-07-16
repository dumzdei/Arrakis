import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(ROOT))

from src.core.geometry import DiodeGeometry, MOSFETGeometry


class GeometryTest(unittest.TestCase):
    def test_diode_geometry_area_and_scale(self):
        diode = DiodeGeometry(area=1e-8, perimeter=1e-4, device_num=4)
        self.assertEqual(diode.geometry_type, 'DIODE')
        self.assertEqual(diode.effective_area(), 4e-8)
        self.assertEqual(diode.scale_factor(), 4)

    def test_mosfet_geometry_area_and_scale(self):
        mosfet = MOSFETGeometry(width=10e-6, length=1e-6, fingers=2, m=3)
        self.assertEqual(mosfet.geometry_type, 'MOSFET')
        self.assertAlmostEqual(mosfet.w_over_l, 10.0)
        self.assertAlmostEqual(mosfet.effective_area(), 60e-12)
        self.assertEqual(mosfet.scale_factor(), 6.0)

    def test_mosfet_w_over_l_raises_for_zero_length(self):
        mosfet = MOSFETGeometry(width=5e-6, length=0.0)
        with self.assertRaises(ValueError):
            _ = mosfet.w_over_l


if __name__ == '__main__':
    unittest.main()
