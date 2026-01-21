# H100 Validation Test Instructions

This test compares our calculated H100HGX carbon footprint values with the ground truth from NVIDIA's Product Carbon Footprint (PCF) report.

## Reference Document

**NVIDIA H100 HGX PCF Summary**
- URL: https://images.nvidia.com/aem-dam/Solutions/documents/HGX-H100-PCF-Summary.pdf

## Current Calculated Values

Our calculator produces the following values for H100HGX (full 4-year lifetime):

| Component | Calculated (kgCO2e) | Percentage |
|-----------|---------------------|------------|
| Memory    | 68.0000             | 46.30%     |
| PCB       | 1.1899              | 0.81%      |
| PDN       | 28.7500             | 19.58%     |
| Cooling   | 6.5000              | 4.43%      |
| SoC       | 41.5000             | 28.26%     |
| Connection| 0.9250              | 0.63%      |
| **Total** | **154.2082**        | **100%**   |

*(Note: Total includes a 5% margin)*

## How to Update Ground Truth Values

1. **Open the PDF report**: Download and open the NVIDIA H100 HGX PCF Summary PDF from the link above.

2. **Find the carbon footprint values**: Look for sections like:
   - "Product Carbon Footprint Summary"
   - "Embodied Carbon Breakdown"
   - "Life Cycle Assessment Results"
   - Component-wise breakdown tables

3. **Extract the values**: The report typically provides values in kgCO2e. Look for:
   - Total Product Carbon Footprint
   - Individual component contributions
   - May be categorized differently (e.g., "DRAM" instead of "Memory")

4. **Update the test file**: Edit `test_h100_validation.py` and update the `H100_HGX_GROUND_TRUTH` dictionary:

```python
H100_HGX_GROUND_TRUTH = {
    'total': 150.0,      # Replace with actual total from PDF
    'memory': 68.0,      # Replace with actual memory value
    'PCB': 1.2,          # Replace with actual PCB value
    'PDN': 28.75,        # Replace with actual PDN value
    'cooling': 6.5,      # Replace with actual cooling value
    'SoC': 41.5,         # Replace with actual SoC value
    'connection': 0.925, # Replace with actual connection value
}
```

5. **Run the test**: Execute the validation test:

```bash
python tests/test_h100_validation.py
```

6. **Review the results**: The test will show:
   - Calculated vs. Ground Truth comparison
   - Relative error percentages for each component
   - Overall validation status (PASS/WARNING/FAIL based on error thresholds)

## Validation Criteria

- **PASS**: Relative error < 5%
- **WARNING**: Relative error < 10%
- **FAIL**: Relative error >= 10%

## Notes

- The PDF may use different component names or groupings than our calculator
- Some components may be combined in the report (e.g., "PCB and components")
- The report may provide values for different scopes (e.g., manufacturing only vs. full lifecycle)
- Ensure you're comparing values for the same lifetime period (typically 4 years)

## Troubleshooting

If values don't match:
1. Check if the report uses different component categories
2. Verify the lifetime period matches (4 years)
3. Check if the report includes/excludes certain components
4. Verify units are consistent (kgCO2e)
5. Check if the report includes the 5% margin or not





