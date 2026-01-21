"""
Validation test comparing calculated H100HGX carbon footprint with NVIDIA PCF report.
Reference: https://images.nvidia.com/aem-dam/Solutions/documents/HGX-H100-PCF-Summary.pdf

This test compares our calculated values with the ground truth from NVIDIA's Product Carbon Footprint report.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_carbon import GPUCarbonCalculator, json_to_gpuspecs
import json


# Ground truth values from NVIDIA H100 HGX PCF Summary report
# Reference: https://images.nvidia.com/aem-dam/Solutions/documents/HGX-H100-PCF-Summary.pdf
# 
# The report typically provides embodied carbon footprint in kgCO2e for the full product lifetime.
# Update the values below with actual numbers from the PDF report.
#
# NOTE: The PDF may use different component naming. Common categories include:
# - Total Product Carbon Footprint
# - Memory/DRAM
# - PCB/Printed Circuit Board
# - Power Delivery/PDN
# - Cooling/Thermal Solution
# - SoC/Die/Processor
# - Interconnect/NVLink/NVSwitch
#

H100_HGX_GROUND_TRUTH = {
    'total': 150.0,      # Replace with actual total from PDF
    'memory': 68.0,      # Replace with actual memory value
    'PCB': 1.2,          # Replace with actual PCB value
    'PDN': 28.75,        # Replace with actual PDN value
    'cooling': 6.5,      # Replace with actual cooling value
    'SoC': 41.5,         # Replace with actual SoC value
    'connection': 0.925, # Replace with actual connection value
}


def calculate_h100_carbon_footprint(lifetime_hours=None):
    """
    Calculate H100HGX carbon footprint for full lifetime.
    
    Args:
        lifetime_hours: If None, uses 4 years (default from config)
    
    Returns:
        Dictionary with component breakdown
    """
    # Load GPU config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'gpuconfigs.json')
    with open(config_path, 'r') as f:
        gpu_configs = json.load(f)
    
    # Get H100HGX specs
    h100_specs = json_to_gpuspecs(gpu_configs['H100HGX'])
    
    # Create calculator
    calculator = GPUCarbonCalculator(h100_specs)
    
    # Calculate for full lifetime
    if lifetime_hours is None:
        lifetime_hours = h100_specs.lifetime_years * 365 * 24
    
    cf = calculator.calculate_total_cf(execution_time_hours=lifetime_hours)
    
    return cf, h100_specs


def calculate_relative_error(calculated, ground_truth):
    """
    Calculate relative error percentage.
    
    Args:
        calculated: Calculated value
        ground_truth: Ground truth value
    
    Returns:
        Relative error as percentage, or None if ground_truth is None
    """
    if ground_truth is None or ground_truth == 0:
        return None
    return abs((calculated - ground_truth) / ground_truth) * 100


def format_comparison_table(calculated, ground_truth):
    """
    Format a comparison table showing calculated vs ground truth values and errors.
    """
    print("\n" + "=" * 80)
    print("H100 HGX Carbon Footprint Validation")
    print("Reference: NVIDIA HGX-H100-PCF-Summary.pdf")
    print("=" * 80)
    print(f"{'Component':<20} {'Calculated (kgCO2e)':>20} {'Ground Truth (kgCO2e)':>25} {'Relative Error (%)':>20}")
    print("-" * 80)
    
    total_error = None
    for component in ['memory', 'PCB', 'PDN', 'cooling', 'SoC', 'connection', 'total']:
        calc_val = calculated.get(component, 0)
        truth_val = ground_truth.get(component)
        error = calculate_relative_error(calc_val, truth_val)
        
        if component == 'total':
            total_error = error
        
        truth_str = f"{truth_val:.4f}" if truth_val is not None else "N/A"
        error_str = f"{error:.2f}%" if error is not None else "N/A"
        
        print(f"{component:<20} {calc_val:>20.4f} {truth_str:>25} {error_str:>20}")
    
    print("-" * 80)
    
    # Summary
    print("\nSummary:")
    print(f"  Calculated Total: {calculated['total']:.4f} kgCO2e")
    if ground_truth.get('total') is not None:
        print(f"  Ground Truth Total: {ground_truth['total']:.4f} kgCO2e")
        print(f"  Relative Error: {total_error:.2f}%")
        if total_error < 5:
            print("  ✓ Validation PASSED (error < 5%)")
        elif total_error < 10:
            print("  ⚠ Validation WARNING (error < 10%)")
        else:
            print("  ✗ Validation FAILED (error >= 10%)")
    else:
        print("  ⚠ Ground truth values not provided - please update H100_HGX_GROUND_TRUTH")
        print("     with values from the NVIDIA PCF report")
    
    print("=" * 80)


def test_h100_validation():
    """
    Main test function that calculates and compares values.
    """
    # Calculate carbon footprint
    calculated_cf, specs = calculate_h100_carbon_footprint()
    
    # Display calculated values
    print("\nCalculated H100HGX Carbon Footprint (Full Lifetime):")
    print(f"Lifetime: {specs.lifetime_years} years ({specs.lifetime_years * 365 * 24} hours)")
    print("\nComponent Breakdown:")
    for component, value in calculated_cf.items():
        print(f"  {component}: {value:.4f} kgCO2e")
    
    # Compare with ground truth
    format_comparison_table(calculated_cf, H100_HGX_GROUND_TRUTH)
    
    # Return values for further analysis
    return calculated_cf, H100_HGX_GROUND_TRUTH


def test_individual_components():
    """
    Test individual component calculations and show breakdown.
    """
    calculated_cf, specs = calculate_h100_carbon_footprint()
    calculator = GPUCarbonCalculator(specs)
    
    print("\n" + "=" * 80)
    print("Individual Component Calculations (Before Time Scaling)")
    print("=" * 80)
    
    components = {
        'Memory': calculator.calculate_memory_cf(),
        'PCB': calculator.calculate_pcb_cf(),
        'PDN': calculator.calculate_pdn_cf(),
        'Cooling': calculator.calculate_cooling_cf(),
        'SoC': calculator.calculate_soc_cf(),
        'Connection': calculator.calculate_connection_cf(),
    }
    
    total_before_margin = sum(components.values())
    total_after_margin = total_before_margin * 1.05
    
    print(f"{'Component':<20} {'Value (kgCO2e)':>20} {'Percentage':>20}")
    print("-" * 80)
    for component, value in components.items():
        percentage = (value / total_before_margin) * 100
        print(f"{component:<20} {value:>20.4f} {percentage:>19.2f}%")
    print("-" * 80)
    print(f"{'Subtotal (before 5% margin)':<20} {total_before_margin:>20.4f}")
    print(f"{'Total (with 5% margin)':<20} {total_after_margin:>20.4f}")
    print("=" * 80)


if __name__ == "__main__":
    print("H100 HGX Carbon Footprint Validation Test")
    print("=" * 80)
    print("NOTE: To complete validation, please update H100_HGX_GROUND_TRUTH")
    print("      dictionary with actual values from the NVIDIA PCF report.")
    print("=" * 80)
    
    # Run main validation test
    calculated, ground_truth = test_h100_validation()
    
    # Show individual component breakdown
    test_individual_components()
    
    # Instructions for updating ground truth
    print("\n" + "=" * 80)
    print("Instructions to Update Ground Truth Values:")
    print("=" * 80)
    print("1. Open the NVIDIA H100 HGX PCF Summary PDF:")
    print("   https://images.nvidia.com/aem-dam/Solutions/documents/HGX-H100-PCF-Summary.pdf")
    print("2. Find the embodied carbon footprint values (typically in kgCO2e)")
    print("3. Update the H100_HGX_GROUND_TRUTH dictionary in this file")
    print("4. Re-run this test to see relative errors")
    print("=" * 80)

