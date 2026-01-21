# Server Carbon Calculator

A standalone Python library for calculating the embodied carbon footprint of GPU and CPU server components.

## Features

- **GPU Carbon Calculator**: Calculate carbon footprint for GPU components including:
  - Memory (HBM, DDR, GDDR)
  - PCB (Printed Circuit Board)
  - PDN (Power Delivery Network)
  - Cooling systems
  - SoC (System on Chip)
  - Interconnect (NVLink/NVSwitch)

- **CPU Carbon Calculator**: Calculate carbon footprint for CPU server components including:
  - SSD storage
  - Memory (DDR4, LPDDR5, etc.)
  - Mainboard
  - CPU die
  - PSU (Power Supply Unit)
  - Chassis
  - Fans
  - Peripheral components (Ethernet, controllers, etc.)

## Installation

### From Source

```bash
git clone git@github.com:yl3469/AI-server-carbon-calculator.git
cd server-carbon-calculator
pip install -e .
```

### Direct Usage

You can also use the library directly without installation by adding the `src` directory to your Python path:

```python
import sys
sys.path.insert(0, '/path/to/server-carbon-calculator/src')
from server_carbon import GPUCarbonCalculator, CPUCarbonCalculator
```

## Quick Start

### GPU Carbon Calculation

```python
from server_carbon import GPUCarbonCalculator, GPUSpecs, MemoryType

# Define GPU specifications
gpu_specs = GPUSpecs(
    tdp=700,                    # Thermal Design Power in watts
    memory_size=80,             # Memory size in GB
    memory_type=MemoryType.HBM3,
    soc_area=814,               # SoC area in mm²
    soc_cf=41.5,                # SoC carbon footprint
    pcb_area=297.48,            # PCB area in cm²
    total_surface_area=4759.68, # Total surface area
    process_node=5,             # Process node in nm
    lifetime_years=4.0,         # Lifetime in years
    suggested_psu=1100          # Suggested PSU in watts
)

# Create calculator
calculator = GPUCarbonCalculator(gpu_specs)

# Calculate carbon footprint for 1 hour of operation
cf = calculator.calculate_total_cf(execution_time_hours=1.0)

print(f"Total carbon footprint: {cf['total']:.6f} kgCO2e")
```

### CPU Carbon Calculation

```python
from server_carbon import CPUCarbonCalculator, MemoryType

# Create calculator
calculator = CPUCarbonCalculator(
    lifetime_years=4.0,
    execution_time=1.0,         # 1 hour
    packing_cf=10.0,
    pcb_area_cm2=1925.0,
    ssd_capacity_gb=120,
    memory_capacity_gb=120,
    memory_type=MemoryType.DDR4,
    die_area_mm2=600.0,
    process_node_nm=7
)

# Calculate carbon footprint
results = calculator.calculate_total_cf()
print(f"Total carbon footprint: {results['total_cf']:.6f} kgCO2e")
```

### Using JSON Configuration

```python
import json
from server_carbon import GPUCarbonCalculator, json_to_gpuspecs

# Load GPU configuration from JSON
with open('config/gpuconfigs.json', 'r') as f:
    gpu_configs = json.load(f)

# Convert to GPUSpecs
gpu_specs = json_to_gpuspecs(gpu_configs['H100HGX'])

# Calculate
calculator = GPUCarbonCalculator(gpu_specs)
cf = calculator.calculate_total_cf(execution_time_hours=1.0)
```

## Examples

The repository includes example scripts in the `examples/` directory:

### GPU Example

```bash
python examples/example_gpu.py --gpu H100HGX --hours 1.0
```

### CPU Example

```bash
python examples/example_cpu.py
```

## Supported Memory Types

- **HBM**: HBM3E, HBM3, HBM2E, HBM2, HBM1β, HBM1α
- **DDR**: DDR4
- **LPDDR**: LPDDR5
- **GDDR**: GDDR6

## API Reference

### GPUCarbonCalculator

#### Methods

- `calculate_memory_cf()`: Calculate memory carbon footprint
- `calculate_pcb_cf()`: Calculate PCB carbon footprint
- `calculate_pdn_cf()`: Calculate Power Delivery Network carbon footprint
- `calculate_cooling_cf()`: Calculate cooling system carbon footprint
- `calculate_soc_cf()`: Calculate SoC carbon footprint
- `calculate_connection_cf()`: Calculate interconnect carbon footprint
- `calculate_total_cf(execution_time_hours)`: Calculate total carbon footprint

### CPUCarbonCalculator

#### Methods

- `calculate_ssd_cf()`: Calculate SSD carbon footprint
- `calculate_memory_cf()`: Calculate memory carbon footprint
- `calculate_peripheral_pwb_cf()`: Calculate peripheral PCB components
- `calculate_mainboard_cf()`: Calculate mainboard carbon footprint
- `calculate_die_cf()`: Calculate CPU die carbon footprint
- `calculate_psu_cf()`: Calculate PSU carbon footprint
- `calculate_chasis_cf()`: Calculate chassis carbon footprint
- `calculate_fans_cf()`: Calculate fans carbon footprint
- `calculate_total_cf()`: Calculate total carbon footprint

## Configuration Files

The `config/gpuconfigs.json` file contains pre-configured specifications for various GPU models including:

- A100PCIE, A100SXM
- H100PCIE, H100HGX
- GH200SXM
- A40, A5500, A6000
- V100PCIE
- T4, L4

## Carbon Footprint Methodology

The carbon footprint calculations are based on:

- **Embodied carbon**: Manufacturing and material carbon footprint
- **Time-based allocation**: Carbon footprint is allocated based on usage time relative to component lifetime

The calculations follow Life Cycle Assessment (LCA) methodologies and reference values from published research.

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Contributing
We welcome contributions from the community! If you would like to contribute to this project, please follow these steps:

1. **Fork the repository** and create your own branch.
2. **Make your changes** with clear commit messages.
3. **Test your code** thoroughly before submission.
4. **Open a pull request** describing your changes and the motivation behind them.
5. Ensure your code follows the style and documentation guidelines present in the repository.

If you have questions or suggestions, feel free to open an issue.

Thank you for helping improve this project!


## Citation

If you use this library in your research, please cite:

```
@article{li2025ecoserve,
  title={Ecoserve: Designing carbon-aware ai inference systems},
  author={Li, Yueying and Hu, Zhanqiu and Choukse, Esha and Fonseca, Rodrigo and Suh, G Edward and Gupta, Udit},
  journal={arXiv preprint arXiv:2502.05043},
  year={2025}
}

@article{lisa2025fair,
  title={Fair, Practical, and Efficient Carbon Accounting for LLM Serving},
  author={Lisa Li, Yueying and Han, Leo and Suh, G Edward and Delimitrou, Christina and Kazhamiaka, Fiodar and Choukse, Esha and Fonseca, Rodrigo and Yu, Liangcheng and Mace, Jonathan and Gupta, Udit},
  journal={ACM SIGMETRICS Performance Evaluation Review},
  volume={53},
  number={2},
  pages={99--103},
  year={2025},
  publisher={ACM New York, NY, USA}
}
```

## References

- ACT (Architecture Carbon Modeling Tool)
- iMeC (Integrated Manufacturing Carbon)
- NVIDIA, Microsoft and Google LCA reports





