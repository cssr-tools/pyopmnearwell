[![Build Status](https://github.com/cssr-tools/pyopmnearwell/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/pyopmnearwell/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%20|%203.11|%203.12-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/662625461.svg)](https://zenodo.org/doi/10.5281/zenodo.10266790)

# pyopmnearwell: A framework to simulate near well dynamics using OPM Flow

<img src="docs/text/figs/introduction.gif" width="830" height="400">

This repository contains scripts to set up a workflow to run near well numerical studies
using the [_OPM-Flow_](https://opm-project.org/?page_id=19) simulator.

## Installation
You will first need to install
* OPM Flow (https://opm-project.org, Release 2024.04 or current master branches)

To install the _pyopmnearwell_ executable in an existing Python environment: 

```bash
pip install git+https://github.com/cssr-tools/pyopmnearwell.git
```

If you are interested in modifying the source code, then you can clone the repository and 
install the Python requirements in a virtual environment with the following commands:

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
# Install the pyopmnearwell package
pip install -e .
# For contributions/testing/linting, install the dev-requirements
pip install -r dev-requirements.txt
``` 

See the [_installation_](https://cssr-tools.github.io/pyopmnearwell/installation.html) for further details on building OPM Flow from the master branches
in Linux, Windows, and macOS.

## Running pyopmnearwell
You can run _pyopmnearwell_ as a single command line:
```
pyopmnearwell -i some_input.txt -o some_output_folder
```
Run `pyopmnearwell --help` to see all possible command line 
argument options. Inside the `some_input.txt` file you provide the path to the
flow executable and simulation parameters. See the .txt files in the [_examples_](https://github.com/cssr-tools/pyopmnearwell/tree/main/examples),
[_tests/geometries/_](https://github.com/cssr-tools/pyopmnearwell/tree/main/tests/geometries), and [_tests/models/_](https://github.com/cssr-tools/pyopmnearwell/tree/main/tests/models) folders. 

## Getting started
See the [_examples_](https://cssr-tools.github.io/pyopmnearwell/examples.html) in the [_documentation_](https://cssr-tools.github.io/pyopmnearwell/introduction.html).

## About pyopmnearwell
The pyopmnearwell package is being funded by the [_HPC Simulation Software for the Gigatonne Storage Challenge project_](https://www.norceresearch.no/en/projects/hpc-simulation-software-for-the-gigatonne-storage-challenge) [project number 622059] and [_Center for Sustainable Subsurface Resources (CSSR)_](https://cssr.no) 
[project no. 331841].
This is work in progress.
Contributions are more than welcome using the fork and pull request approach.
