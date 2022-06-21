.. shamelessly copied from ophyd's tutorial

How to install `hklpy`
======================

This tutorial covers:

* Installation for users using :ref:`install.conda.user`
* Installation for users using :ref:`install.conda.developer`

.. * Installation using :ref:`install.pip`
.. * Installation from :ref:`install.source`

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

.. FIXME:
    .. _install.pip:

    Pip
    ---

    We strongly recommend creating a fresh environment (here, named ``try-hklpy``).

    .. FIXME:

        (base) prjemian@zap:~/Documents$ source try-hklpy/bin/activate
        (try-hklpy) (base) prjemian@zap:~/Documents$ python
        Python 3.8.12 (default, Oct 12 2021, 13:49:34)
        [GCC 7.5.0] :: Anaconda, Inc. on linux
        Type "help", "copyright", "credits" or "license" for more information.
        >>> import hkl
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        ModuleNotFoundError: No module named 'hkl'
        >>>

    .. code:: bash

    python3 -m venv try-hklpy
    source try-hklpy/bin/activate

    Install hklpy from PyPI.

    .. code:: bash

        python3 -m pip install hklpy pygobject

.. FIXME:
    .. _install.source:

    Source
    ------

    To install an editable installation for local development:

    .. code:: bash

        git clone https://github.com/bluesky/hklpy
        cd hklpy
        pip install -e .


.. conda create -n try-hklpy -c conda-forge hklpy jupyter black flake8 pytest bluesky "databroker=1" sphinx sphinx_rtd_theme
