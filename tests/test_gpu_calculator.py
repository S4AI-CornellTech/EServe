"""
Unit tests for GPUCarbonCalculator
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_carbon import GPUCarbonCalculator, GPUSpecs, MemoryType


def test_gpu_calculator_basic():
    """Test basic GPU carbon calculation"""
    gpu_specs = GPUSpecs(
        tdp=700,
        memory_size=80,
        memory_type=MemoryType.HBM3,
        soc_area=814,
        soc_cf=41.5,
        pcb_area=297.48,
        total_surface_area=4759.68,
        process_node=5,
        lifetime_years=4.0,
        suggested_psu=1100
    )
    
    calculator = GPUCarbonCalculator(gpu_specs)
    cf = calculator.calculate_total_cf(execution_time_hours=1.0)
    
    assert 'total' in cf
    assert 'memory' in cf
    assert 'PCB' in cf
    assert 'PDN' in cf
    assert 'cooling' in cf
    assert 'SoC' in cf
    assert 'connection' in cf
    assert cf['total'] > 0


def test_gpu_memory_cf():
    """Test memory carbon footprint calculation"""
    gpu_specs = GPUSpecs(
        tdp=700,
        memory_size=80,
        memory_type=MemoryType.HBM3,
        soc_area=814,
        soc_cf=41.5,
        pcb_area=297.48,
        total_surface_area=4759.68,
        process_node=5,
        lifetime_years=4.0,
        suggested_psu=1100
    )
    
    calculator = GPUCarbonCalculator(gpu_specs)
    memory_cf = calculator.calculate_memory_cf()
    
    # HBM3 coefficient is 0.85, so 80 GB should give 68.0 kgCO2e
    expected = 0.85 * 80
    assert abs(memory_cf - expected) < 0.01


if __name__ == "__main__":
    test_gpu_calculator_basic()
    test_gpu_memory_cf()
    print("All tests passed!")





