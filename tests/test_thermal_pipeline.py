import unittest
import numpy as np
from pipelines.cuda_thermal_math import run_gpu_thermal_pipeline

class TestCudaThermalPipeline(unittest.TestCase):
    
    def setUp(self):
        """Instantiates uniform synthetic sensor structures mimicking real clinical data."""
        self.height = 120
        self.width = 160
        # Generate baseline sensor counts within standard physiological thresholds (~30C)
        self.synthetic_adc_counts = np.full((self.height, self.width), 8200, dtype=np.uint16)

    def test_gpu_processing_dimensions(self):
        """Verifies that the CUDA memory grid maintains precise aspect ratio stability."""
        processed_matrix = run_gpu_thermal_pipeline(self.synthetic_adc_counts)
        self.assertEqual(processed_matrix.shape, (120, 160))
        self.assertEqual(processed_matrix.dtype, np.float32)

    def test_thermal_calculation_bounds(self):
        """Ensures the calculated numerical outputs fall within a valid medical envelope."""
        processed_matrix = run_gpu_thermal_pipeline(self.synthetic_adc_counts)
        
        # Extract individual sample data point
        sample_pixel_temp = processed_matrix[60, 80]
        
        # Ensure calculations do not return NaN errors or infinite values due to division anomalies
        self.assertFalse(np.isnan(sample_pixel_temp))
        self.assertFalse(np.isinf(sample_pixel_temp))
        
        # Verify the numerical calibration output remains within typical clinical envelopes
        # 8200 ADC units roughly scales to the 28C - 34C range under standard factory calibration variables
        self.assertGreater(sample_pixel_temp, 25.0)
        self.assertLess(sample_pixel_temp, 40.0)

if __name__ == '__main__':
    unittest.main()
