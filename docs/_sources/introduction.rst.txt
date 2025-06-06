============
Introduction
============

.. image:: ./figs/saturation.gif
    :scale: 50%

This documentation describes the **pyopmnearwell** package hosted in `https://github.com/cssr-tools/pyopmnearwell <https://github.com/cssr-tools/pyopmnearwell>`_.

Concept
-------
Simplified and flexible testing framework for near-well simulations via a
:doc:`configuration file <./configuration_file>` using the `OPM Flow simulator <https://opm-project.org/?page_id=19>`_:

- Set the physical model (current ones are co2store, co2eor, h2store, saltprec, co2eor, and foam).
- Choose a `specific template <https://github.com/cssr-tools/pyopmnearwell/blob/main/src/pyopmnearwell/templates>`_ inside the folder for the chosen physical model.
- Define the grid refinement in the x/y and z directions.
- Define the number of different rocks along the z direction.
- Define the number of layers (heterogeneity around the well) and its length.
- Set the rock and fluid properties.
- Define the injection schedule.
- Run the simulations.

Overview
--------

The current implementation supports the following executable with the argument options:

.. code-block:: bash

    pyopmnearwell -i configuration_file.toml

where 

-i  The base name of the :doc:`configuration file <./configuration_file>` ('input.toml' by default).
-o  The base name of the :doc:`output folder <./output_folder>` ('output' by default).
-m  Run the whole framework ('all'), only generate the deck ('deck'), or only run flow ('flow'), or generate the deck and run flow in the same output folder ('single') ('all' by default). 
-v  Write cell values, i.e., EGRID, INIT, UNRST ('1' by default).
-w  Set to 1 to print warnings ('0' by default).

.. tip::
    The plotting functionality in **pyopmnearwell** has been retired in the release 2025.04. Instead, to generate
    PNGs and GIFs of the simulation results, you could use `plopm <https://github.com/cssr-tools/plopm>`_, where previous functionality in
    the plotting routines in **pyopmnearwell** has been implemented such as distance of a variable (e.g., gas saturation) to the model boundaries, 
    variable values along a given layer in the model, etc.

.. warning::
    The H2CH4 template in the h2store model folder is under development and it is based on an input deck available in 
    `opm-tests <https://github.com/OPM/opm-tests/blob/master/diffusion/BO_DIFFUSE_CASE1.DATA>`_. In addition, the templates 
    in the co2eor/foam model are based on an input deck available in `opm-publications <https://github.com/OPM/opm-publications/blob/master/dynamic_blackoil/SPE5.BASE>`_. 
    Currently the PVT tables in those examples are used, limiting the range of reservoir pressure and temperature, it is in the TODO list to extend
    this.