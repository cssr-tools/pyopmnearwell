============
Introduction
============

.. image:: ./figs/introduction.gif
    :scale: 50%

This documentation describes the content of the **pyopmnearwell** package.
The numerical studies are performed using the 
`Flow <https://opm-project.org/?page_id=19>`_ simulator.

Concept
-------
Simplified and flexible testing framework for near-well simulations via a
:doc:`configuration file <./configuration_file>`:

- Choose the physical model (current ones are co2store and h2store).
- Define the grid refinment in the x/y and z directions.
- Define the number of different rocks along the z direction.
- Define the number of layers (heterogeneity around the well) and its length.
- Set the rock and fluid properties.
- Define the injection schedule.
- Run the simulations
- Inspect the results by looking at the generated figures.

Overview
--------

The current implementation supports the following executable with the argument options:

.. code-block:: bash

    pyopmnearwell -i input.txt -o output -p ecl -c compare

where 

- \-i, \-input: The base name of the :doc:`configuration file <./configuration_file>` ('input.txt' by default).
- \-o, \-output: The base name of the :doc:`output folder <./output_folder>` ('output' by default).
- \-p, \-plotting: Using the 'ecl' or 'opm' python package to generate the figures ('ecl' by default).
- \-c, \-compare: Compare the results from different output folders ('' (write any name to actiate) by default).

Installation
------------

See the `Github page <https://github.com/daavid00/pyopmnearwell>`_.

.. tip::
    Check the `CI.yml <https://github.com/daavid00/pyopmnearwell/blob/main/.github/workflows/CI.yml>`_ file.

.. note::
    For MAC users with the latest chip, both **ecl** and **opm** packages are not available via pip install. Then
    before installation, comment the first line in the requierements.txt file, then proceed with the installation and 
    after build opm-common from source inside the virtual environment with the flag -DOPM_ENABLE_PYTHON=ON and, finally,
    add to the python path the folder where you have built it, e.g., by running in the terminal
    export PYTHONPATH=$PYTHONPATH:/Users/dmar/Github/opm-common/build/python .

.. warning::
    The h2store option is under development and it is based on an input deck available in 
    `opm-tests <https://github.com/OPM/opm-tests/blob/master/diffusion/BO_DIFFUSE_CASE1.DATA>`_. Currently the PVT tables
    in that example are used, limiting the range of reservoir pressure and temperature, it is in the TODO list to extend
    this. 
