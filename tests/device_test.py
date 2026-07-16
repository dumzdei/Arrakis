import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(ROOT))

from src.core.device import Device
from src.core.geometry import DiodeGeometry, MOSFETGeometry
from src.core.device_parameters import DiodeParameters
from src.core.measurement import MeasurementSet, MeasurementCondition, IVMeasurement
import numpy as np


class DeviceTest(unittest.TestCase):
    def test_get_set_update_parameter(self):
        parameters = DiodeParameters(name='D1')
        device = Device(
            device_id='D1',
            device_type='DIODE',
            geometry=DiodeGeometry(area=1e-8, perimeter=1e-4, device_num=1),
            parameters=parameters,
            measurements=MeasurementSet(device_id='D1')
        )
        device.set_parameter('IS', 2e-12)
        self.assertEqual(device.get_parameter('IS'), 2e-12)
        device.update_parameters({'N': 2.0})
        self.assertEqual(device.get_parameter('N'), 2.0)

    def test_get_geometry_info_for_diode_and_mosfet(self):
        diode = Device(
            device_id='D1',
            device_type='DIODE',
            geometry=DiodeGeometry(area=2e-8, perimeter=1e-4, device_num=2),
            parameters=DiodeParameters(name='D1'),
            measurements=MeasurementSet(device_id='D1')
        )
        info = diode.get_geometry_info()
        self.assertEqual(info['effective_area'], 4e-8)
        self.assertEqual(info['device_num'], 2)

        mosfet = Device(
            device_id='M1',
            device_type='MOSFET',
            geometry=MOSFETGeometry(width=2e-6, length=1e-6, fingers=2, m=1),
            parameters=DiodeParameters(name='M1'),
            measurements=MeasurementSet(device_id='M1')
        )
        info = mosfet.get_geometry_info()
        self.assertEqual(info['width'], 2e-6)
        self.assertEqual(info['w_over_l'], 2.0)

    def test_summary_contains_device_info(self):
        meas = MeasurementSet(device_id='D2')
        iv = IVMeasurement(
            device_id='D2',
            condition=MeasurementCondition(),
            setup='cfg',
            sweep_variable='V',
            sweep_values=np.array([0.0]),
            currents={'I': np.array([0.0])}
        )
        meas.add(iv)
        device = Device(
            device_id='D2',
            device_type='DIODE',
            geometry=DiodeGeometry(area=1e-8, perimeter=1e-4, device_num=1),
            parameters=DiodeParameters(name='D2'),
            measurements=meas
        )
        summary = device.summary()
        self.assertIn('Device: D2', summary)
        self.assertIn('Measurements: 1', summary)


if __name__ == '__main__':
    unittest.main()
