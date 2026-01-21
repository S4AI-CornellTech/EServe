#!/usr/bin/env python3
"""
Example script demonstrating CPU carbon footprint calculation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_carbon import CPUCarbonCalculator, MemoryType


def main():
    # Create a CPU carbon calculator
    calculator = CPUCarbonCalculator(
        lifetime_years=4.0,
        execution_time=1.0,  # 1 hour
        packing_cf=10.0,
        pcb_area_cm2=1925.0,
        ssd_capacity_gb=120,  # 120 GB SSD
        memory_capacity_gb=120,  # 120 GB memory
        memory_type=MemoryType.DDR4,
        die_area_mm2=600.0,
        process_node_nm=7
    )
    
    # Calculate carbon footprint
    results = calculator.calculate_total_cf()
    
    print("\nCPU Carbon Footprint Analysis")
    print("=" * 60)
    print(f"Total Carbon Footprint: {results['total_cf']:.6f} kgCO2e")
    print(f"Execution Time: {results['execution_time_hours']} hours")
    print(f"Lifetime: {results['lifetime_hours']} hours")
    print("\nComponent Breakdown:")
    print("-" * 60)
    print(f"{'Component':<30} {'Carbon Footprint (kgCO2e)':>30}")
    print("-" * 60)
    
    for component, value in results['components'].items():
        if isinstance(value, dict):
            print(f"\n{component.upper()}:")
            for subcomp, subvalue in value.items():
                print(f"  {subcomp:<28} {subvalue:>30.6f}")
        else:
            print(f"{component:<30} {value:>30.6f}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()





