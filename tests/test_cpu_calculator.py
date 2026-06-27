"""
Unit tests for CPUCarbonCalculator
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_carbon import CPUCarbonCalculator, MemoryType


def test_cpu_calculator_basic():
    """Test basic CPU carbon calculation"""
    calculator = CPUCarbonCalculator(
        lifetime_years=4.0,
        execution_time=1.0,
        packing_cf=10.0,
        pcb_area_cm2=1925.0,
        ssd_capacity_gb=120,
        memory_capacity_gb=120,
        memory_type=MemoryType.DDR4,
        die_area_mm2=600.0,
        process_node_nm=7
    )
    
    results = calculator.calculate_total_cf()
    
    assert 'total_cf' in results
    assert 'components' in results
    assert 'execution_time_hours' in results
    assert 'lifetime_hours' in results
    assert results['total_cf'] > 0


def test_cpu_ssd_cf():
    """Test SSD carbon footprint calculation"""
    calculator = CPUCarbonCalculator(
        lifetime_years=4.0,
        execution_time=1.0,
        packing_cf=0.0,
        pcb_area_cm2=1925.0,
        ssd_capacity_gb=120,
        memory_capacity_gb=0,
        memory_type=MemoryType.DDR4,
    )
    
    ssd_cf = calculator.calculate_ssd_cf()

    # SSD now uses act_core's bare-die NAND (nand_10nm = 10 g/GB = 0.010 kgCO2e/GB),
    # the same source ACT/MicroGreen use, so 120 GB should give ~1.2 kgCO2e.
    expected = 0.010 * 120
    assert abs(ssd_cf - expected) < 0.01


if __name__ == "__main__":
    test_cpu_calculator_basic()
    test_cpu_ssd_cf()
    print("All tests passed!")





