# Repository Structure

```
server-carbon-calculator/
├── src/
│   └── server_carbon/
│       ├── __init__.py          # Package initialization and exports
│       └── server_carb.py       # Main module with GPUCarbonCalculator and CPUCarbonCalculator
├── config/
│   └── gpuconfigs.json          # Pre-configured GPU specifications
├── examples/
│   ├── example_gpu.py           # Example script for GPU carbon calculation
│   └── example_cpu.py            # Example script for CPU carbon calculation
├── tests/
│   ├── __init__.py
│   ├── test_gpu_calculator.py   # Unit tests for GPU calculator
│   └── test_cpu_calculator.py   # Unit tests for CPU calculator
├── README.md                     # Main documentation
├── requirements.txt              # Python dependencies (none required)
├── setup.py                      # Package setup script
├── MANIFEST.in                   # Manifest for package distribution
└── .gitignore                    # Git ignore file
```

## Key Components

### Source Code (`src/server_carbon/`)

- **`server_carb.py`**: Contains all the core classes:
  - `MemoryType`: Enumeration of memory types
  - `GPUSpecs`: Dataclass for GPU specifications
  - `CPUSpecs`: Class for CPU specifications
  - `ServerSpecs`: Class for server specifications
  - `GPUCarbonCalculator`: Main GPU carbon footprint calculator
  - `CPUCarbonCalculator`: Main CPU carbon footprint calculator
  - Helper functions: `json_to_gpuspecs()`, `json_to_cpuspecs()`, `json_to_serverspecs()`

### Configuration (`config/`)

- **`gpuconfigs.json`**: JSON file containing pre-configured specifications for various GPU models (A100, H100, T4, etc.)

### Examples (`examples/`)

- **`example_gpu.py`**: Command-line script demonstrating GPU carbon calculation
- **`example_cpu.py`**: Script demonstrating CPU carbon calculation

### Tests (`tests/`)

- Unit tests for both GPU and CPU calculators

## Usage

### Installation

```bash
pip install -e .
```

### Direct Usage (without installation)

```python
import sys
sys.path.insert(0, '/path/to/server-carbon-calculator/src')
from server_carbon import GPUCarbonCalculator, CPUCarbonCalculator
```

### Running Examples

```bash
# GPU example
python examples/example_gpu.py --gpu H100HGX --hours 1.0

# CPU example
python examples/example_cpu.py
```

### Running Tests

```bash
python tests/test_gpu_calculator.py
python tests/test_cpu_calculator.py
```





