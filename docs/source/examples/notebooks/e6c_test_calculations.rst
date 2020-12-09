Non-exhaustive test of E6C calculations
=======================================

Verify *hklpy* (from its interface to the *hkl* library) computations of
orientation, U, UB, and rotation directions.

With the aid of Yong Chu’s mental math.

`TL;DR <https://www.merriam-webster.com/dictionary/TL%3BDR>`__ appears
to function as documented and as expected

--------------

Note: This example is available as a `Jupyter
notebook <https://jupyter.org/>`__ from the *hklpy* source code website:
https://github.com/bluesky/hklpy/tree/main/examples

Import the python libraries needed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    
    import gi
    gi.require_version('Hkl', '5.0')
    from hkl.calc import CalcE6C
    from hkl.util import Lattice

Initialize the calculation engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    calc = CalcE6C(engine='hkl')
    calc.engine.mode = 'constant_chi_vertical'
    calc.wavelength = 1.  # Angstrom

Setup the crystal lattice
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    lattice = Lattice(a=1, b=1, c=1, alpha=90, beta=90, gamma=90)
    sample = calc.new_sample('sample0', lattice=lattice)
    
    print('lattice', sample.lattice)
    print('physical axes', calc.physical_axes)
    print('pseudo axes', calc.pseudo_axes)
    print('omega parameter is', calc['omega'])


.. parsed-literal::

    lattice LatticeTuple(a=1.0, b=1.0, c=1.0, alpha=90.0, beta=90.0, gamma=90.0)
    physical axes OrderedDict([('mu', 0.0), ('omega', 0.0), ('chi', 0.0), ('phi', 0.0), ('gamma', 0.0), ('delta', 0.0)])
    pseudo axes OrderedDict([('h', 0.0), ('k', 0.0), ('l', 0.0)])
    omega parameter is CalcParameter(name='omega', limits=(-180.0, 180.0), value=0.0, fit=True, inverted=False, units='Degree')


Compute the UB matrix from two reflections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # define the wavelength
    calc.wavelength = 1.0
    
    # checking orientation of delta
    r1p = calc.Position(mu=0.0, omega=30.0, chi=0.0, phi=0.0, gamma=0., delta=60.)
    r1 = sample.add_reflection(0, 0, 1, position=r1p)
    r2p = calc.Position(mu=0.0, omega=120.0, chi=0.0, phi=0.0, gamma=0, delta=60.)
    r2 = sample.add_reflection(1, 0, 0, position=r2p)
    sample.compute_UB(r1, r2)




.. parsed-literal::

    1



Show the computed **U** matrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    sample.U




.. parsed-literal::

    array([[ 1.00000000e+00, -3.74939946e-33,  6.12323400e-17],
           [ 0.00000000e+00,  1.00000000e+00,  6.12323400e-17],
           [-6.12323400e-17, -6.12323400e-17,  1.00000000e+00]])



Show the computed **UB** matrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    sample.UB




.. parsed-literal::

    array([[ 6.28318531e+00, -3.84734139e-16,  0.00000000e+00],
           [ 0.00000000e+00,  6.28318531e+00,  0.00000000e+00],
           [-3.84734139e-16, -3.84734139e-16,  6.28318531e+00]])



Calculate various (*hkl*) given motor positions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(010)
^^^^^

.. code:: ipython3

    calc.physical_positions = calc.Position(mu=0.0, omega=30.0, chi=90.0, phi=0.0, gamma=0, delta=60.)
    print('pseudo should be (0,1,0)=', calc.pseudo_axes)



.. parsed-literal::

    pseudo should be (0,1,0)= OrderedDict([('h', 1.7187070131469975e-16), ('k', 0.9999999999999998), ('l', 1.7919353632379053e-16)])


.. code:: ipython3

    # checking orientation of delta
    calc.physical_positions = calc.Position(mu=30.0, omega=0.0, chi=0.0, phi=0.0, gamma=60., delta=0.)
    print('pseudo should be (0,1,0)=', calc.pseudo_axes)


.. parsed-literal::

    pseudo should be (0,1,0)= OrderedDict([('h', 5.729023377156659e-17), ('k', 0.9999999999999999), ('l', 6.123233995736765e-17)])


(0 -1 0)
^^^^^^^^

.. code:: ipython3

    calc.physical_positions = calc.Position(mu=0, omega=30., chi=-90.0, phi=0.0, gamma=0., delta=60.)
    print('pseudo should be (0,-1,0)=', calc.pseudo_axes)



.. parsed-literal::

    pseudo should be (0,-1,0)= OrderedDict([('h', 0.0), ('k', -0.9999999999999998), ('l', 5.672885640905521e-17)])


(-1 0 0)
^^^^^^^^

.. code:: ipython3

    
    calc.physical_positions = calc.Position(mu=0.0, omega=-60.0, chi=0.0, phi=0.0, gamma=0, delta=60.)
    print('pseudo should be (-1,0,0)=', calc.pseudo_axes)



.. parsed-literal::

    pseudo should be (-1,0,0)= OrderedDict([('h', -0.9999999999999999), ('k', 0.0), ('l', 2.291609350862664e-16)])


Diffracting upside-down now
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note that omega and phi only need to sum to +-120
(:math:`\omega+\varphi = \pm |120|`), which reflects what the inverse
calculations from the library give.

(100)
^^^^^

.. code:: ipython3

    calc.physical_positions = calc.Position(mu=0.0, omega=-50.0, chi=0.0, phi=-70.0, gamma=0, delta=-60.)
    print('pseudo should be (1,0,0)=', calc.pseudo_axes)
    
    calc.physical_positions = calc.Position(mu=0.0, omega=-100.0, chi=0.0, phi=-20.0, gamma=0, delta=-60.)
    print('pseudo should be (1,0,0)=', calc.pseudo_axes)
    
    calc.physical_positions = calc.Position(mu=0.0, omega=100.0, chi=0.0, phi=-220.0, gamma=0, delta=-60.)
    print('pseudo should be (1,0,0)=', calc.pseudo_axes)


.. parsed-literal::

    pseudo should be (1,0,0)= OrderedDict([('h', 1.0), ('k', 0.0), ('l', 5.729023377156662e-17)])
    pseudo should be (1,0,0)= OrderedDict([('h', 1.0), ('k', 0.0), ('l', 5.729023377156662e-17)])
    pseudo should be (1,0,0)= OrderedDict([('h', 1.0), ('k', 0.0), ('l', 5.729023377156662e-17)])


(011)
^^^^^

.. code:: ipython3

    calc.physical_positions = calc.Position(mu=0.0, omega=45.0, chi=45.0, phi=0.0, gamma=0, delta=90.)
    print('pseudo should be (0,1,1)=', calc.pseudo_axes)


.. parsed-literal::

    pseudo should be (0,1,1)= OrderedDict([('h', 3.4374140262939965e-16), ('k', 1.0), ('l', 1.0)])


Verify that :math:`\omega+\varphi = \pm |120|` is kept.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # calculate all allowed combinations of motor positions, given hkl
    solutions = calc.forward((1,0,0))

.. code:: ipython3

    for sol in solutions:
        print("expecting ~120:", sol.omega + sol.phi)


.. parsed-literal::

    expecting ~120: 119.9999999269113
    expecting ~120: -119.9999999269113

