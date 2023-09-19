========================
pyopmnearwell Python API
========================

The main script for the **pyopmnearwell** executable is located in the core folder.
The scripts in the utils folder process the input configuration file, creates the geological model, 
write the input files by using the scripts in the templates folder, and execute OPM Flow. The scripts in 
the visualization folder contains files for the postprocessing of the results to generate figures (.png) to show
comparisons between the different runs/parts of the geological model such as well injectivity (WI) and
2D spatial maps for the last time step simulated. The ml folder is under development, see the files in the 
'examples/cemracs2023/peaceman_well-model_nn' if you are curious.

.. figure:: figs/contents.png

    Files in the pyopmnearwell package.

.. include:: modules.rst