import numpy as np
import numba
from numba import cuda

@cuda.jit
def process_radiometric_matrix_kernel(raw_adc_array, output_celsius_array, planck_r1, planck_b, planck_f, planck_o, emissivity):
    """
    CUDA Kernel to convert raw 14-bit FLIR linear ADC values directly into True Celsius 
    across all pixels concurrently in GPU VRAM memory space.
    """
    row, col = cuda.grid(2)
    
    if row < raw_adc_array.shape[0] and col < raw_adc_array.shape[1]:
        # Extract raw sensor counts
        raw_val = raw_adc_array[row, col]
        
        # Standard FLIR Radiometric Equation Math Map
        # Formula calculates radiance and balances against internal microbolometer offset
        radiance = (raw_val / emissivity) - planck_o
        
        if radiance > 0:
            # Calculate object temperature in Kelvin
            temp_kelvin = planck_b / numba.cmath.log((planck_r1 / radiance) + planck_f)
            # Convert directly to Celsius array element
            output_celsius_array[row, col] = temp_kelvin - 273.15
        else:
            output_celsius_array[row, col] = 0.0

def run_gpu_thermal_pipeline(raw_frame_matrix):
    """
    Asynchronous CPU-to-GPU memory orchestration layer.
    """
    # FLIR ONE Pro Factory Calibration Constants (Varies slightly per unit batch)
    R1 = 16512.0
    B = 1428.0
    F = 1.0
    O = -120.0
    EMISSIVITY = 0.98 # Calibrated baseline for human skin tissue tissue
    
    # Dimensions for the FLIR ONE Pro Core matrix
    height, width = raw_frame_matrix.shape
    
    # Allocate locked pinned memory blocks on the GPU
    d_raw = cuda.to_device(raw_frame_matrix)
    d_output = cuda.device_array((height, width), dtype=np.float32)
    
    # Configure 2D CUDA thread execution blocks 
    threads_per_block = (16, 16)
    blocks_per_grid_x = int(np.ceil(height / threads_per_block[0]))
    blocks_per_grid_y = int(np.ceil(width / threads_per_block[1]))
    blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y)
    
    # Fire asynchronous CUDA stream across physical hardware cores
    process_radiometric_matrix_kernel[blocks_per_grid, threads_per_block](
        d_raw, d_output, R1, B, F, O, EMISSIVITY
    )
    
    # Pull calculated array metrics back to host CPU memory cache
    return d_output.copy_to_host()
