.. shamelessly copied from ophyd's tutorial

How to install `hklpy`
======================

This tutorial covers

* Installation using :ref:`install.conda`

.. TODO:
    * Installation using :ref:`install.pip`
    * Installation from :ref:`install.source`

.. note:: *hklpy* only runs on Linux

    *hklpy* relies on the *hkl* library which is only available for Linux.

It is not required to have an EPICS IOC server running; all diffractometers may
be run with simulated axes.

.. _install.conda:

Conda
-----

We strongly recommend creating a fresh environment (here, named ``try-hklpy``),
installing *hklpy* (from the ``conda-forge`` conda channel [#]_) and other
required packages from the very start.

.. code:: bash

   conda create -n try-hklpy -c conda-forge hklpy
   conda activate try-hklpy

.. [#] conda-forge: https://anaconda.org/conda-forge

.. TODO:
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

    If you intend to use ophyd with EPICS, you should also install an EPICS client
    library for ophyd to use---either pyepics (recommended) or caproto (experimental).

    .. code:: bash

    python3 -m pip install pyepics  # or caproto if you are feeling adventurous

    Finally, to follow along with the EPICS tutorials, you should also install
    ``caproto`` to run EPICS servers with simulated hardware and ``bluesky`` to
    orchestrate scans with the RunEngine.

    .. code:: bash

    python3 -m pip install bluesky caproto[standard]

.. TODO:
    .. _install.source:

    Source
    ------

    To install an editable installation for local development:

    .. code:: bash

    git clone https://github.com/bluesky/ophyd
    cd ophyd
    pip install -e .
