"""
Server Carbon Calculator - A standalone library for calculating carbon footprint
of GPU and CPU server components.
"""

from .server_carb import (
    MemoryType,
    GPUSpecs,
    CPUSpecs,
    ServerSpecs,
    GPUCarbonCalculator,
    CPUCarbonCalculator,
    json_to_gpuspecs,
    json_to_cpuspecs,
    json_to_serverspecs,
)

__version__ = "1.0.0"
__all__ = [
    "MemoryType",
    "GPUSpecs",
    "CPUSpecs",
    "ServerSpecs",
    "GPUCarbonCalculator",
    "CPUCarbonCalculator",
    "json_to_gpuspecs",
    "json_to_cpuspecs",
    "json_to_serverspecs",
]





