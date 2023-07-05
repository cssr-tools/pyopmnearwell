=============
Output folder
=============

The following screenshot shows the generated files in the selected output folder after 
executing **pyopmnearwell**.

.. figure:: figs/output.png

    Generated files after executing **pyopmnearwell**.

The simulation results are saved in the output folder, and
`ResInsight <https://resinsight.org>`_ can be used for the visualization.
Then after running **pyopmnearwell**, one could modify the generated OPM related files and 
run directly the simulations calling the Flow solvers, e.g., to add tracers 
(see the OPM Flow documentation `here <https://opm-project.org/?page_id=955>`_).
In addition, some plots comparing the simulations in different parts of the reservoir are generated
in the postprocessing folder. Then the **plotting.py** script in the output/jobs folder can be modified/extended
to generate additional plots.