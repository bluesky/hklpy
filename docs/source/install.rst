.. include:: /substitutions.txt

.. _install:

Install
=======

The |hklpy| package should be installed by ``conda`` so that the |libhkl|
compiled library is installed properly. That library is only compiled for
workstations with *Linux x86_64* architecture.

.. _install.conda:

conda
-----

If you are using Anaconda Python and have ``conda`` installed, install the most
recent |hklpy| release with this command::

    conda install conda-forge::hklpy

source
------

The |hklpy| source code can be downloaded from the
GitHub repository::

    $ git clone http://github.com/bluesky/hklpy.git

.. note:: |libhkl| library **must** be installed.

    Here are two possible ways, both involve ``conda`` installations to
    satisfy project requirements.

    1. Install |hklpy| first with :ref:`install.conda`

    2. Create and activate a custom conda environment
       using |hklpy|'s ``environment.yml`` file::

            conda env create -n hklpy-source -f environment.yml
            conda activate hklpy-source

    After one of these steps, then install |hklpy| from source as shown next.

To install from the source directory using ``pip`` in editable mode::

    $ cd hklpy
    $ python -m pip install -e .

Required Libraries
------------------

The repository's ``environment.yml`` file lists the additional packages
required by |hklpy|.  Most packages are available as conda packages
from https://anaconda.org.  The others are available on
https://PyPI.python.org.

.. _install.test:

Test the installation
------------------------------

Test that |hklpy| and the |libhkl| library have been installed by creating a
simulated 4-circle diffractometer and showing its default settings:

.. code:: bash

    python -c "import hkl; fourc=hkl.SimulatedE4CV('', name='fourc'); fourc.wh()"
