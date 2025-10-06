[![Build Status](https://github.com/cssr-tools/pyopmnearwell/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/pyopmnearwell/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/662625461.svg)](https://zenodo.org/doi/10.5281/zenodo.10266790)

**Note: This branch is fixed to run with Python 3.10.12. No future updates will come to this branch (after 06th October 2025).**

# pyopmnearwell: A framework to simulate near well dynamics using OPM Flow

<img src="docs/text/figs/introduction.gif" width="830" height="400">

This repository contains scripts to set up a workflow to run near well numerical studies
using the [_OPM-Flow_](https://opm-project.org/?page_id=19) simulator.

## Installation
You will first need to install
* Flow (https://opm-project.org, Release 2023.10 or current master branches)

You can install the requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/cssr-tools/pyopmnearwell.git
# Get inside the folder
cd pyopmnearwell
# Create virtual environment
python3 -m venv vpyopmnearwell
# Activate virtual environment
source vpyopmnearwell/bin/activate
# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
# Install the pyopmnearwell package (in editable mode for contributions/modifications; otherwise, pip install .)
pip install -e .
# For contributions/testing/linting, install the dev-requirements
pip install -r dev-requirements.txt
``` 

See the [_CI.yml_](https://github.com/cssr-tools/pyopmnearwell/blob/main/.github/workflows/CI.yml) script 
for installation of OPM Flow (binary packages) and the pyopmnearwell package. If you are a Linux user (including the windows subsystem for Linux), then you could try to build Flow from the master branches with mpi support, by running the script `./build_opm-flow_mpi.bash`, which in turn should build flow in the folder ./build/opm-simulators/bin/flow. 

For macOS users with the latest chips (M1/M2, guessing also M3?), the ecl, resdata, and opm Python packages are not available via pip install. Then before installation, remove them from the `requirements.txt`, then proceed with the Python requirements installation, install the OPM Flow dependencies (using macports or brew), and once inside the vpyopmnearwell Python environment, run the `./build_opm-flow_macOS.bash`, and deactivate and activate the virtual environment (this script builds OPM Flow as well as the opm Python package, and it exports the required PYTHONPATH).

## Running pyopmnearwell
You can run _pyopmnearwell_ as a single command line:
```
pyopmnearwell -i some_input.txt -o some_output_folder
```
Run `pyopmnearwell --help` to see all possible command line 
argument options. Inside the `some_input.txt` file you provide the path to the
flow executable and simulation parameters. See the .txt files in the `examples/`,
`tests/geometries/`, and `tests/models/` folders. For macOS users, then use the flag
`-p opm` for plotting (resdata is the default one).

## Getting started
See the [_documentation_](https://cssr-tools.github.io/pyopmnearwell/introduction.html).

## About pyopmnearwell
The pyopmnearwell package is being funded by the [_HPC Simulation Software for the Gigatonne Storage Challenge project_](https://www.norceresearch.no/en/projects/hpc-simulation-software-for-the-gigatonne-storage-challenge) [project number 622059] and [_Center for Sustainable Subsurface Resources (CSSR)_](https://cssr.no) 
[project no. 331841].
This is work in progress.
Contributions are more than welcome using the fork and pull request approach.
