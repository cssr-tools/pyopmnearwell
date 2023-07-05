[![Build Status](https://github.com/daavid00/pyopmnearwell/actions/workflows/CI.yml/badge.svg)](https://github.com/daavid00/pyopmnearwell/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# pyopmnearwell: A framework to simulate near well dynamics using OPM Flow

<img src="docs/text/figs/introduction.gif" width="830" height="400">

This repository contains scripts to set up a workflow to run near well numerical studies
using the [_OPM-Flow_](https://opm-project.org/?page_id=19) simulator.

## Installation
You will first need to install
* Flow (https://opm-project.org)

You can install the requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/daavid00/pyopmnearwell.git
# Get inside the folder
cd pyopmnearwell
# Create virtual environment
python3 -m venv vpyopmnearwell
# Activate virtual environment
source vpyopmnearwell/bin/activate
# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
# Install the pyopmnearwell package (in editable mode for contributions/modifications, i.e., pip install -e .)
pip install .
# For contributions/testing/linting, install the dev-requirements
pip install -r dev-requirements.txt
``` 

For MAC users with the latest chips (M1/M2), both ecl and opm packages are not available via pip install. Then
before installation, comment the first two lines in the requierements.txt file, then proceed with the installation and 
after build opm-common from source inside the virtual environment with the flag -DOPM_ENABLE_PYTHON=ON and, finally,
add to the python path the folder where you have built it, e.g., by running in the terminal
`export PYTHONPATH=$PYTHONPATH:/Users/dmar/Github/opm-common/build/python` .

## Running pyopmnearwell
You can run _pyopmnearwell_ as a single command line:
```
pyopmnearwell -i some_input.txt -o some_output_folder
```
Run `pyopmnearwell --help` to see all possible command line 
argument options. Inside the `some_input.txt` file you provide the path to the
flow executable and simulation parameters. See the .txt files in the tests/configs
folder.

## Getting started
See the [_documentation_](https://daavid00.github.io/pyopmnearwell/introduction.html).

## About pyopmnearwell
The pyopmnearwell package is being funded by the [_HPC Simulation Software for the Gigatonne Storage Challenge project_](https://www.norceresearch.no/en/projects/hpc-simulation-software-for-the-gigatonne-storage-challenge) [project number 622059] and [_Center for Sustainable Subsurface Resources (CSSR)_](https://cssr.no) 
[project no. 331841].
This is work in progress.
Contributions are more than welcome using the fork and pull request approach.
