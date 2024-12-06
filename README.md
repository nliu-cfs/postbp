# PostBP: A Python Library for Post-Processing Outputs from Wildfire Growth Models

[![image](https://img.shields.io/pypi/v/postbp.svg)](https://pypi.python.org/pypi/postbp)
[![image](https://img.shields.io/conda/vn/conda-forge/postbp.svg)](https://anaconda.org/conda-forge/postbp)


**A Python Library**


-   Free software: MIT License
-   Documentation: https://nliu-cfs.github.io/postbp
    

## Introduction

PostBP is an open-source Python library designed to simplify the analysis and visualization of outputs from wildfire growth models (FGMs), such as the Canadian Burn-P3 model. The library extracts critical fire behavior metrics, including fire spread likelihoods, source-sink ratios, and burn probabilities, providing actionable insights for wildfire risk assessments and mitigation planning.

With PostBP, users can transform raw simulation outputs into intuitive metrics and maps, streamlining decision-making for wildfire management.

---

## Key Features

- **Hexagonal Patch Network**: Discretize landscapes into hexagonal patches for intuitive fire behavior analysis.
- **Fire Spread Analysis**:
  - Compute fire spread likelihoods between pairs of hexagonal patches.
  - Visualize fire spread patterns with rose diagrams.
- **Burn and Ignition Probabilities**:
  - Calculate patch-level burn probabilities and ignition likelihoods.
  - Supports user-defined thresholds for burned area classification.
- **Source-Sink Analysis**:
  - Quantify the tendency of patches to act as fire sources or sinks.
- **Customizable Inputs**:
  - Supports outputs from Burn-P3 and other FGMs with compatible formats.
- **Flexible Outputs**:
  - Save results as GeoDataFrames, GeoJSON, Apache GeoParquet, or ESRI Shapefiles.

---

## Installation

PostBP can be installed using pip, it is recommended to install PostBP in a dedicated Python environment to avoid dependency conflicts.:

```bash
pip install postbp

```

## Documentation and Support

Comprehensive documentation is available at:
https://nliu-cfs.github.io/postbp

For any issues or inquiries, please open an issue on the GitHub repository.

## Citation

If you use PostBP in your research, please cite:

Liu, N., Yemshanov, D., Parisien, M.-A., et al. (2024). PostBP: A Python library to analyze outputs from wildfire growth models. MethodsX, 13, 102816. DOI:10.1016/j.mex.2024.102816
