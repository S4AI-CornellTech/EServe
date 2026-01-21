"""
Server Carbon Calculator - Calculate carbon footprint of GPU and CPU server components.

This module provides calculators for embodied carbon footprint of:
- GPU components (memory, PCB, PDN, cooling, SoC, connections)
- CPU components (SSD, memory, mainboard, die, PSU, chassis, fans, peripherals)
"""

import enum
from dataclasses import dataclass
from typing import Dict, Optional, Union
import json
import os


class MemoryType(enum.Enum):
    """Memory type enumeration for carbon footprint calculations"""
    HBM3E = "HBM3e"
    HBM3 = "HBM3"
    HBM2E = "HBM2e"
    HBM2 = "HBM2"
    HBM1_BETA = "HBM1β"
    HBM1_ALPHA = "HBM1α"
    DDR4 = "DDR4"
    LPDDR5 = "LPDDR5"
    GDDR6 = "GDDR6"


@dataclass
class GPUSpecs:
    """GPU specifications needed for carbon calculations"""
    tdp: float  # Thermal Design Power in watts
    memory_size: float  # Memory size in GB
    memory_type: MemoryType
    soc_area: float  # SoC area in mm²
    soc_cf: float  # Calculated CF for SoC
    pcb_area: float  # PCB area in cm²
    total_surface_area: float  # PCB area * layers
    process_node: int  # Manufacturing process node in nm
    lifetime_years: float = 4.0  # Default lifetime of 4 years
    suggested_psu: float = 650  # Suggested PSU in watts


class CPUSpecs:
    """CPU specifications needed for carbon calculations"""
    def __init__(self, cpu_cores: int, cpu_memory: float, cpu_tdp: float,
                 nvme_size: float, storage_size: float, accelerators: int, NICs: int):
        self.cpu_cores = cpu_cores  # Number of CPU cores
        self.cpu_memory = cpu_memory  # CPU memory in GB
        self.cpu_tdp = cpu_tdp
        self.nvme_size = nvme_size  # CPU NVMe in GB
        self.storage_size = storage_size  # CPU storage in GB
        self.accelerators = accelerators  # Number of GPU cards
        self.NICs = NICs  # Number of NICs


class ServerSpecs:
    """Server specifications needed for carbon calculations. User take care of the TDP or area constraints"""
    def __init__(self, cpu_specs: Dict[str, CPUSpecs], gpu_specs: Dict[str, GPUSpecs]):
        self.cpu_specs = cpu_specs
        self.gpu_specs = gpu_specs


class GPUCarbonCalculator:
    """Calculator for GPU embodied carbon footprint"""
    
    # Constants from the paper
    PCB_CF_PER_CM2 = 0.048 / 12.0  # kgCO2e/cm² (12 layers)
    
    # Memory carbon footprint coefficients (kgCO2e/GB)
    MEMORY_CF_COEFFICIENTS = {
        MemoryType.HBM3E: 0.85,
        MemoryType.HBM3: 0.85,
        MemoryType.HBM2E: 0.85,
        MemoryType.HBM1_BETA: 0.28,
        MemoryType.HBM2: 0.28,
        MemoryType.HBM1_ALPHA: 0.28,
        MemoryType.DDR4: 0.29,
        MemoryType.LPDDR5: 0.29,
        MemoryType.GDDR6: 0.36
    }
    
    # Reference values from LCA report
    LCA_REFERENCE = {
        'tdp': 300,  # Reference TDP in watts
        'tdp_board': 500, 
        'pdn_cf': 16.3494,  # Reference PDN carbon footprint in kgCO2e
        'cooling_cf': 23.63  # Reference cooling system carbon footprint in kgCO2e
    }
    
    LCA_REFERENCE_GPU = {
        'tdp': 700,  # Reference TDP in watts
        'tdp_board': 1100, 
        'pdn_cf': 28.75,  # Reference PDN carbon footprint in kgCO2e
        'cooling_cf': 6.5  # Reference cooling system carbon footprint in kgCO2e
    }
    
    def __init__(self, specs: GPUSpecs):
        """
        Initialize GPU Carbon Calculator
        
        Args:
            specs: GPUSpecs object containing GPU specifications
        """
        self.specs = specs

    def calculate_memory_cf(self) -> float:
        """Calculate memory carbon footprint"""
        coefficient = self.MEMORY_CF_COEFFICIENTS[self.specs.memory_type]
        return coefficient * self.specs.memory_size

    def calculate_pcb_cf(self) -> float:
        """Calculate PCB carbon footprint"""
        return self.PCB_CF_PER_CM2 * self.specs.pcb_area

    def calculate_pdn_cf(self) -> float:
        """Calculate Power Delivery Network carbon footprint"""
        return (self.specs.suggested_psu / self.LCA_REFERENCE_GPU['tdp_board']) * self.LCA_REFERENCE_GPU['pdn_cf']

    def calculate_cooling_cf(self) -> float:
        """Calculate cooling system carbon footprint"""
        # if H100 SXM, use liquid cooling
        if self.specs.memory_type == MemoryType.HBM3E or self.specs.memory_type == MemoryType.HBM3:
            return (self.specs.tdp / self.LCA_REFERENCE_GPU['tdp']) * self.LCA_REFERENCE_GPU['cooling_cf']
        else:
            return (self.specs.tdp / self.LCA_REFERENCE['tdp']) * self.LCA_REFERENCE['cooling_cf']

    def calculate_soc_cf(self) -> float:
        """
        Calculate SoC carbon footprint using area and process node
        Note: This is a simplified calculation; in practice you might want to use
        more sophisticated models like ACT or iMeC
        """
        # Actually use the ACT / iMeC carbon
        return self.specs.soc_cf
        
    def calculate_connection_cf(self) -> float:
        """Calculate connection (NVLink or NVSwitch carbon footprint)"""
        # Updated: to the same as H100 HGX
        return 7.4 / 8

    def calculate_total_cf(self, execution_time_hours: float) -> Dict[str, float]:
        """
        Calculate total embodied carbon footprint for a given execution time
        
        Args:
            execution_time_hours: Execution time in hours
        
        Returns:
            Dictionary containing breakdown of carbon footprint components
        """
        # Calculate time ratio (execution time / lifetime)
        time_ratio = execution_time_hours / (self.specs.lifetime_years * 365 * 24)
        
        # Calculate individual components
        components = {
            'memory': self.calculate_memory_cf(),
            'PCB': self.calculate_pcb_cf(),
            'PDN': self.calculate_pdn_cf(),
            'cooling': self.calculate_cooling_cf(),
            'SoC': self.calculate_soc_cf(),
            'connection': self.calculate_connection_cf(),
        }
        
        # Apply time ratio to all components
        components = {k: v * time_ratio for k, v in components.items()}
        
        # Add total
        components['total'] = sum(components.values()) * 1.05  # Add 5% margin
        
        return components


@dataclass
class CPUCarbonCalculator:
    """Calculate the carbon footprint for CPU components."""
    # https://docs.google.com/spreadsheets/d/14_teYVhwtiLcSeyIuuQY6Pc0rhvQ_QFUIjCXLylBvqU/edit?gid=680012399#gid=680012399
    # System parameters
    lifetime_years: float = 4.0  # Default lifetime in years
    execution_time: float = 1.0  # Execution time in hours
    packing_cf: float = 0.0      # Packing carbon footprint (Nr * Kr)
    
    # Component specifications
    pcb_area_cm2: float = 1925.0  # Default PCB area in cm²
    ssd_capacity_gb: float = 0.0  # SSD capacity in GB
    memory_capacity_gb: float = 0.0  # Memory capacity in GB
    memory_type: MemoryType = MemoryType.DDR4
    die_area_mm2: Optional[float] = None
    process_node_nm: Optional[float] = None
    
    def __post_init__(self):
        """Initialize derived constants."""
        self.CF_SSD_PER_GB = 0.10999  # kgCO2e/GB
        self.CF_PCB_PER_CM2 = 0.056   # kgCO2e/cm²
        
        # Memory CF coefficients based on memory type
        self.memory_cf_coefficients = {
            MemoryType.HBM3E: 0.24,
            MemoryType.HBM3: 0.24,
            MemoryType.HBM2E: 0.24,
            MemoryType.HBM1_BETA: 0.24,
            MemoryType.HBM2: 0.28,
            MemoryType.HBM1_ALPHA: 0.28,
            MemoryType.DDR4: 0.29,
            MemoryType.LPDDR5: 0.29,
            MemoryType.GDDR6: 0.36
        }

    def calculate_ssd_cf(self) -> float:
        """Calculate SSD carbon footprint."""
        return self.CF_SSD_PER_GB * self.ssd_capacity_gb

    def calculate_peripheral_pwb_cf(self) -> Dict[str, float]:
        """Calculate peripheral PWB components carbon footprint."""
        ethernet_cf = 102.3 * self.CF_PCB_PER_CM2
        hdd_controller_cf = 107.0 * self.CF_PCB_PER_CM2
        q_logic_cf = 111.4 * 2 * self.CF_PCB_PER_CM2
        rise_card_cf = (114.3 + 127.5 + 117.3) * self.CF_PCB_PER_CM2
        intel_x710_cf = 178.2 * self.CF_PCB_PER_CM2
        
        return {
            "ethernet": ethernet_cf,
            "hdd_controller": hdd_controller_cf,
            "q_logic": q_logic_cf,
            "rise_card": rise_card_cf,
            "intel_x710": intel_x710_cf,
            "total": ethernet_cf + hdd_controller_cf + q_logic_cf + rise_card_cf + intel_x710_cf
        }

    def calculate_memory_cf(self) -> float:
        """Calculate memory carbon footprint based on memory type."""
        if self.memory_capacity_gb <= 0:
            return 0.0
        
        cf_coefficient = self.memory_cf_coefficients[self.memory_type]
        return cf_coefficient * self.memory_capacity_gb
    
    def calculate_chasis_cf(self) -> float:
        """Calculate chassis carbon footprint."""
        return 34.304  # Placeholder for chassis carbon footprint calculation
    
    def calculate_fans_cf(self) -> float:
        """Calculate fans carbon footprint."""
        return 12.864
    
    def calculate_psu_cf(self) -> float:
        """Calculate PSU carbon footprint."""
        return 30.016

    def calculate_mainboard_cf(self) -> Optional[float]:
        """
        Placeholder for mainboard carbon footprint calculation.
        This would typically use ACT and iMeC tools based on area and process node.
        """
        return 118  # Example scaling
    
    def calculate_die_cf(self) -> Optional[float]:
        """
        Placeholder for die carbon footprint calculation.
        This would typically use ACT and iMeC tools based on area and process node.
        """
        if self.die_area_mm2 is None or self.process_node_nm is None:
            return None
        
        # This is a simplified placeholder calculation
        # In practice, you would integrate with ACT and iMeC tools
        return 27  # ACT Table 12

    def calculate_total_cf(self) -> Dict[str, Union[float, Dict[str, float]]]:
        """Calculate total carbon footprint and component breakdown."""
        lifetime_hours = self.lifetime_years * 365 * 24
        
        # Calculate individual components
        ssd_cf = self.calculate_ssd_cf()
        peripheral_cf = self.calculate_peripheral_pwb_cf()
        memory_cf = self.calculate_memory_cf()
        mainboard_cf = self.calculate_mainboard_cf()
        die_cf = self.calculate_die_cf()
        psu_cf = self.calculate_psu_cf()
        chasis_cf = self.calculate_chasis_cf()
        fans_cf = self.calculate_fans_cf()
        
        # Sum all components
        total_embodied_cf = (
            self.packing_cf +
            ssd_cf +
            mainboard_cf +
            peripheral_cf["total"] +
            memory_cf +
            (die_cf if die_cf is not None else 0.0) + psu_cf + chasis_cf + fans_cf
        )
        
        # Scale by execution time and lifetime
        scaled_cf = (self.execution_time / lifetime_hours) * total_embodied_cf
        
        return {
            "total_cf": scaled_cf,
            "components": {
                "ssd ({})".format(self.ssd_capacity_gb): ssd_cf,
                "peripheral_pwb": peripheral_cf,
                "memory ({})".format(self.memory_capacity_gb): memory_cf,
                "die": die_cf,
                "mainboard": mainboard_cf,
                "psu": psu_cf,
                "chasis": chasis_cf,
                "fans": fans_cf,
                "packing": self.packing_cf
            },
            "execution_time_hours": self.execution_time,
            "lifetime_hours": lifetime_hours
        }


# Helper functions to convert JSON to spec objects
def json_to_gpuspecs(gpu_data: Dict) -> GPUSpecs:
    """
    Convert JSON dictionary to GPUSpecs object
    
    Args:
        gpu_data: Dictionary containing GPU specifications
    
    Returns:
        GPUSpecs object
    """
    return GPUSpecs(
        tdp=gpu_data["tdp"],
        memory_size=gpu_data["memory_size"],
        memory_type=MemoryType(gpu_data["memory_type"]),
        soc_area=gpu_data["soc_area"],
        pcb_area=gpu_data["pcb_area"],
        total_surface_area=gpu_data["total_surface_area"],
        process_node=gpu_data["process_node"],
        lifetime_years=gpu_data.get("lifetime_years", 4.0),  # Default to 4 years if not in JSON
        suggested_psu=gpu_data.get("suggested_psu", 650),  # Default PSU value if not in JSON
        soc_cf=gpu_data.get("soc_cf", 0),
    )


def json_to_cpuspecs(cpu_config: Dict) -> CPUSpecs:
    """
    Convert JSON dictionary to CPUSpecs object
    
    Args:
        cpu_config: Dictionary containing CPU specifications
    
    Returns:
        CPUSpecs object
    """
    return CPUSpecs(
        cpu_cores=cpu_config["cores"],
        cpu_memory=cpu_config["memory_size"],
        cpu_tdp=cpu_config.get("cpu_tdp_w", 100),  # Default to 100W if not specified
        nvme_size=cpu_config.get("nvme_size", 0),
        storage_size=cpu_config.get("storage_size", 0),
        accelerators=cpu_config.get("accelerators", 0),
        NICs=cpu_config.get("NICs", 0),
    )


def json_to_serverspecs(server_data: Dict, config_idx: Optional[int] = None) -> Optional[ServerSpecs]:
    """
    Convert JSON dictionary to ServerSpecs object
    
    Args:
        server_data: Dictionary containing server specifications
        config_idx: Optional index for CPU config (e.g., 1 for "cpu_configs1")
    
    Returns:
        ServerSpecs object or None if incomplete
    """
    # Extract GPU specs
    gpu_specs = {}
    gpu_data = {k: v for k, v in server_data.items() 
                if k not in ["cpu_configs"] and not k.startswith("cpu_configs")}
    if gpu_data:
        # Create a GPU spec from the main server data
        gpu_spec = json_to_gpuspecs(gpu_data)
        gpu_specs["main"] = gpu_spec
    
    # Extract CPU specs
    cpu_specs = {}
    config_key = f"cpu_configs{config_idx}" if config_idx else "cpu_configs"
    if config_key in server_data:
        cpu_config = json_to_cpuspecs(server_data[config_key])
        cpu_specs[config_key] = cpu_config
        return ServerSpecs(cpu_specs=cpu_specs, gpu_specs=gpu_specs)
    
    return None

