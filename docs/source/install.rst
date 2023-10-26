.. shamelessly copied from ophyd's tutorial

How to install `hklpy`
======================

This tutorial covers:

* Installation for users using :ref:`install.conda.user`
* Installation for developers using :ref:`install.conda.developer`
* Installation for users using :ref:`install.pip.user`
* Test the installation using :ref:`install.test`

.. note:: *hklpy* only runs on Linux, since it relies on the *hkl*
    library which is only available for Linux.

It is not required to have an EPICS IOC server running; all diffractometers may
be run with simulated axes.

.. _install.conda.user:

Conda for *hklpy* Users
-----------------------

We strongly recommend creating a fresh environment (here, named ``try-hklpy``),
installing *hklpy* (from the ``conda-forge`` conda channel [#conda]_) and other
required packages from the very start.

.. code:: bash

   conda create -n try-hklpy -c conda-forge hklpy
   conda activate try-hklpy

.. [#conda] conda-forge: https://anaconda.org/conda-forge

.. _install.conda.developer:

Conda for Development
---------------------

We strongly recommend creating a fresh environment (here, named ``hklpy-dev``),
first installing *hklpy* (from the ``conda-forge`` conda channel [#conda]_) and
other packages.  This will add all required packages to the new environment.
Start from the source directory:

.. code:: bash

   cd hklpy
   conda create -n dev-hklpy -f env-dev.yml
   conda activate hklpy-dev

Next, pip install the source directory:

.. code:: bash

   pip install -e . --no-deps

.. _install.pip.user:

Pip for *hklpy* Users
---------------------

We strongly recommend creating a fresh environment (here, named ``try-hklpy``).
Both Python and the *hkl* library must already be installed.  Here, we create
a conda environment with just these packages required:

.. .. code:: bash

..     python3 -m venv try-hklpy
..     source try-hklpy/bin/activate

.. code:: bash

    conda create -y -n try-hklpy python=3.9 hkl -c conda-forge
    conda activate try-hklpy

Install *hklpy* from PyPI.

.. code:: bash

    python3 -m pip install hklpy

.. _install.test:

Test that *hklpy* is installed
------------------------------

Test the *hklpy* has been installed by creating a simulated 4-circle
diffractometer and showing its defaults:

.. code:: bash

    python -c "import hkl; fourc=hkl.SimulatedE4CV('', name='fourc'); fourc.wh()"
