import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(ROOT))

from src.core.measurement import (
    MeasurementCondition,
    IVMeasurement,
    CVMeasurement,
    MeasurementSet,
)


class MeasurementTest(unittest.TestCase):
    def test_measurement_condition_temperature_kelvin_and_bias(self):
        condition = MeasurementCondition(temperature=30.0, bias_conditions={'Vg': 1.2})
        self.assertAlmostEqual(condition.temperature_kelvin, 303.15)
        self.assertEqual(condition.get_bias('Vg'), 1.2)
        self.assertEqual(condition.get_bias('Vd', default=0.5), 0.5)

    def test_iv_measurement_get_current_and_response_variables(self):
        iv = IVMeasurement(
            device_id='D1',
            condition=MeasurementCondition(),
            setup='test',
            sweep_variable='V',
            sweep_values=np.array([0.0, 1.0]),
            currents={'I': np.array([0.1, 0.2])}
        )
        self.assertEqual(iv.measurement_type, 'IV')
        np.testing.assert_allclose(iv.get_sweep_variable(), np.array([0.0, 1.0]))
        self.assertIn('I', iv.get_response_variables())
        with self.assertRaises(KeyError):
            iv.get_current('J')

    def test_cv_measurement_response_variables(self):
        cv = CVMeasurement(
            device_id='D2',
            condition=MeasurementCondition(),
            setup='test',
            sweep_variable='V',
            sweep_values=np.array([0.0, 1.0]),
            capacitance=np.array([1e-12, 2e-12]),
            conductance=np.array([1e-6, 2e-6])
        )
        self.assertEqual(cv.measurement_type, 'CV')
        rv = cv.get_response_variables()
        self.assertIn('C', rv)
        self.assertIn('G', rv)
        np.testing.assert_allclose(rv['C'], np.array([1e-12, 2e-12]))
        np.testing.assert_allclose(rv['G'], np.array([1e-6, 2e-6]))

    def test_measurement_set_add_and_filters(self):
        ms = MeasurementSet(device_id='D1')
        iv = IVMeasurement(
            device_id='D1',
            condition=MeasurementCondition(),
            setup='a',
            sweep_variable='V',
            sweep_values=np.array([0.0]),
            currents={'I': np.array([0.0])}
        )
        cv = CVMeasurement(
            device_id='D1',
            condition=MeasurementCondition(),
            setup='b',
            sweep_variable='V',
            sweep_values=np.array([0.0]),
            capacitance=np.array([1e-12])
        )
        ms.add(iv)
        ms.add(cv)
        self.assertEqual(ms.num_measurements, 2)
        self.assertEqual(len(ms.get_iv()), 1)
        self.assertEqual(len(ms.get_cv()), 1)
        self.assertEqual(len(ms.get_iv(setup='a')), 1)
        self.assertEqual(len(ms.get_cv(setup='a')), 0)
        with self.assertRaises(ValueError):
            ms.add(IVMeasurement(
                device_id='D2',
                condition=MeasurementCondition(),
                setup='x',
                sweep_variable='V',
                sweep_values=np.array([0.0]),
                currents={'I': np.array([0.0])}
            ))


if __name__ == '__main__':
    unittest.main()
