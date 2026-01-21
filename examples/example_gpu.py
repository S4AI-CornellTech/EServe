#!/usr/bin/env python3
"""
Example script demonstrating GPU carbon footprint calculation.
"""

import sys
import os
import json
import argparse

# Add parent directory to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_carbon import (
    GPUCarbonCalculator,
    json_to_gpuspecs,
    MemoryType
)


def main():
    parser = argparse.ArgumentParser(description='Calculate carbon footprint of a GPU')
    parser.add_argument('--gpu', type=str, default='H100HGX', 
                       help='GPU model to calculate carbon footprint for')
    parser.add_argument('--config', type=str, 
                       default=os.path.join(os.path.dirname(__file__), '..', 'config', 'gpuconfigs.json'),
                       help='Path to GPU configs JSON file')
    parser.add_argument('--hours', type=float, default=1.0,
                       help='Execution time in hours')
    args = parser.parse_args()
    
    # Read the JSON file
    with open(args.config, 'r') as f:
        gpu_specs_data = json.load(f)
    
    if args.gpu not in gpu_specs_data:
        print(f"Error: GPU '{args.gpu}' not found in config file.")
        print(f"Available GPUs: {', '.join(gpu_specs_data.keys())}")
        sys.exit(1)
    
    # Convert the JSON data to GPUSpecs
    gpu_specs = json_to_gpuspecs(gpu_specs_data[args.gpu])
    
    # Initialize the GPUCarbonCalculator
    calculator = GPUCarbonCalculator(gpu_specs)
    
    # Calculate carbon footprint
    cf = calculator.calculate_total_cf(execution_time_hours=args.hours)
    
    print(f"\nCarbon Footprint Breakdown for {args.gpu} ({args.hours} hours)")
    print("=" * 60)
    print(f"{'Component':<20} {'Carbon Footprint (kgCO2e)':>30}")
    print("-" * 60)
    for component, value in cf.items():
        if component != 'total':
            print(f"{component:<20} {value:>30.6f}")
    print("-" * 60)
    print(f"{'TOTAL':<20} {cf['total']:>30.6f}")
    print("=" * 60)


if __name__ == "__main__":
    main()





