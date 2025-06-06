============
Installation
============

The following steps work installing the dependencies in Linux via apt-get or in macOS using brew or macports.
While using packages managers such as Anaconda, Miniforge, or Mamba might work, these are not tested.

.. note::
    The tensorflow Python package is not yet available via pip install in Python 3.13. Then, tensorflow has been removed from
    the dependencies to allow installation of **pyopmnearwell** in Python 3.13. If you are using Python 3.12, then after installing 
    **pyopmnearwell**, install tensorflow `pip install tensorflow`. Most of the functionality in **pyopmnearwell** can be used without 
    having installed tensorflow.

Python package
--------------

To install the **pyopmnearwell** executable from the development version: 

.. code-block:: bash

    pip install git+https://github.com/cssr-tools/pyopmnearwell.git

If you are interested in a specific version (e.g., v2024.10) or in modifying the source code, then you can clone the repository and 
install the Python requirements in a virtual environment with the following commands:

.. code-block:: console

    # Clone the repo
    git clone https://github.com/cssr-tools/pyopmnearwell.git
    # Get inside the folder
    cd pyopmnearwell
    # For a specific version (e.g., v2024.10), or else skip this step (i.e., edge version)
    git checkout v2024.10
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

.. tip::

    Typing **git tag -l** writes all available specific versions.

OPM Flow
--------
You also need to install:

* OPM Flow (https://opm-project.org, Release 2025.04 or current master branches)

.. tip::

    See the `CI.yml <https://github.com/cssr-tools/pyopmnearwell/blob/main/.github/workflows/CI.yml>`_ script 
    for installation of OPM Flow (binary packages) and the pyopmnearwell package in Ubuntu. 

Source build in Linux/Windows
+++++++++++++++++++++++++++++
If you are a Linux user (including the Windows subsystem for Linux), then you could try to build Flow (after installing the `prerequisites <https://opm-project.org/?page_id=239>`_) from the master branches with mpi support by running
in the terminal the following lines (which in turn should build flow in the folder ./build/opm-simulators/bin/flow): 

.. code-block:: console

    CURRENT_DIRECTORY="$PWD"

    for repo in common grid simulators
    do
        git clone https://github.com/OPM/opm-$repo.git
    done

    mkdir build

    for repo in common grid
    do
        mkdir build/opm-$repo
        cd build/opm-$repo
        cmake -DUSE_MPI=1 -DWITH_NDEBUG=1 -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CURRENT_DIRECTORY/build/opm-common" $CURRENT_DIRECTORY/opm-$repo
        make -j5 opm$repo
        cd ../..
    done    

    mkdir build/opm-simulators
    cd build/opm-simulators
    cmake -DUSE_MPI=1 -DWITH_NDEBUG=1 -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CURRENT_DIRECTORY/build/opm-common;$CURRENT_DIRECTORY/build/opm-grid" $CURRENT_DIRECTORY/opm-simulators
    make -j5 flow
    cd ../..


.. tip::

    You can create a .sh file (e.g., build_opm_mpi.sh), copy the previous lines, and run in the terminal **source build_opm_mpi.sh**

Source build in macOS
+++++++++++++++++++++
For macOS, there are no available binary packages, so OPM Flow needs to be built from source, in addition to the dune libraries (see the `prerequisites <https://opm-project.org/?page_id=239>`_, which can be installed using macports or brew). This can be achieved by the following lines:

.. code-block:: console

    CURRENT_DIRECTORY="$PWD"

    for module in common geometry grid istl
    do   git clone https://gitlab.dune-project.org/core/dune-$module.git --branch v2.9.1
    done
    for module in common geometry grid istl
    do   ./dune-common/bin/dunecontrol --only=dune-$module cmake -DCMAKE_DISABLE_FIND_PACKAGE_MPI=1
         ./dune-common/bin/dunecontrol --only=dune-$module make -j5
    done

    for repo in common grid simulators
    do
        git clone https://github.com/OPM/opm-$repo.git
    done

    source vpyopmnearwell/bin/activate

    mkdir build

    for repo in common grid
    do
        mkdir build/opm-$repo
        cd build/opm-$repo
        cmake -DWITH_NDEBUG=1 -DUSE_MPI=0 -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CURRENT_DIRECTORY/dune-common/build-cmake;$CURRENT_DIRECTORY/dune-grid/build-cmake;$CURRENT_DIRECTORY/dune-geometry/build-cmake;$CURRENT_DIRECTORY/dune-istl/build-cmake;$CURRENT_DIRECTORY/build/opm-common" $CURRENT_DIRECTORY/opm-$repo
        make -j5 opm$repo
        cd ../..
    done    

    mkdir build/opm-simulators
    cd build/opm-simulators
    cmake -DUSE_MPI=0 -DWITH_NDEBUG=1 -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CURRENT_DIRECTORY/dune-common/build-cmake;$CURRENT_DIRECTORY/dune-grid/build-cmake;$CURRENT_DIRECTORY/dune-geometry/build-cmake;$CURRENT_DIRECTORY/dune-istl/build-cmake;$CURRENT_DIRECTORY/build/opm-common;$CURRENT_DIRECTORY/build/opm-grid" $CURRENT_DIRECTORY/opm-simulators
    make -j5 flow
    cd ../..
