4-circle diffractometer example : renamed axes
==============================================

Following the E4CV example, this example will repeat those same steps
but using different names for the motor axes.

========= ==========
E4CV name local name
========= ==========
omega     theta
chi       chi
phi       phi
tth       ttheta
========= ==========

How’s it done?
--------------

This change is made by:

1. Defining the ``FourCircle`` class using our local names (instead of
   the canonical E4CV names)
2. Writing a dictionary to the ``fourc`` object that maps the canonical
   E4CV names to our local names:

.. code:: python

   fourc.calc.physical_axis_names = {
       # E4CV: local
       'omega': 'theta',
       'chi': 'chi',
       'phi': 'phi',
       'tth': 'ttheta',
       }

--------------

Note: This example is available as a `Jupyter
notebook <https://jupyter.org/>`__ from the *hklpy* source code website:
https://github.com/bluesky/hklpy/tree/main/examples

Load the *hklpy* package (named *``hkl``*)
------------------------------------------

As done in the E4CV example.

This is needed *every* time before the *hkl* package is first imported.

.. code:: ipython3

    import gi
    gi.require_version('Hkl', '5.0')

Define *this* diffractometer
----------------------------

Following the E4CV example, create a ``FourCircle`` class, but use our
own names for the motors.

========= ==========
E4CV name local name
========= ==========
omega     theta
chi       chi
phi       phi
tth       ttheta
========= ==========

Use the new motor names when constructing the ``FourCircle`` class.
Otherwise, everything else in this step the same as in the E4CV example.

.. code:: ipython3

    from hkl.diffract import E4CV
    from ophyd import PseudoSingle, SoftPositioner
    from ophyd import Component as Cpt
    
    class FourCircle(E4CV):
        """
        Our 4-circle.  Eulerian, vertical scattering orientation.
        """
        # the reciprocal axes are called: pseudo in hklpy
        h = Cpt(PseudoSingle, '', kind="hinted")
        k = Cpt(PseudoSingle, '', kind="hinted")
        l = Cpt(PseudoSingle, '', kind="hinted")
    
        # the motor axes are called: real in hklpy
        theta = Cpt(SoftPositioner, kind="hinted")
        chi = Cpt(SoftPositioner, kind="hinted")
        phi = Cpt(SoftPositioner, kind="hinted")
        ttheta = Cpt(SoftPositioner, kind="hinted")
    
        def __init__(self, *args, **kwargs):
            """Define an initial position for simulators."""
            super().__init__(*args, **kwargs)
    
            for p in self.real_positioners:
                p._set_position(0)  # give each a starting position

Create an instance of the diffractometer.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As in the E4CV example, create an instance of the diffractometer. Note
that the instance still has the canonical E4CV names, as reported by
libhkl.

.. code:: ipython3

    fourc = FourCircle("", name="fourc")
    print("motor names:", fourc.calc.physical_axis_names)


.. parsed-literal::

    motor names: ['omega', 'chi', 'phi', 'tth']


Switch to **our** motor names
-----------------------------

This is the magic step, *map* the canonical libhkl names onto the names
we want to use. This is done using a Python dictionary. They keys are
the canonical names, the value of key is the local name. *All* axes must
be in the dictionary, even if the names remain the same.

.. code:: ipython3

    fourc.calc.physical_axis_names = {
        # E4CV: local
        'omega': 'theta',
        'chi': 'chi',
        'phi': 'phi',
        'tth': 'ttheta',
        }
    
    print("motor names:", fourc.calc.physical_axis_names)


.. parsed-literal::

    mapping: {'omega': 'theta', 'chi': 'chi', 'phi': 'phi', 'tth': 'ttheta'}
    motor names: ['theta', 'chi', 'phi', 'ttheta']


Add a sample with a crystal structure
-------------------------------------

.. code:: ipython3

    from hkl.util import Lattice
    
    # add the sample to the calculation engine
    a0 = 5.431
    fourc.calc.new_sample(
        "silicon",
        lattice=Lattice(a=a0, b=a0, c=a0, alpha=90, beta=90, gamma=90)
        )




.. parsed-literal::

    HklSample(name='silicon', lattice=LatticeTuple(a=5.431, b=5.431, c=5.431, alpha=90.0, beta=90.0, gamma=90.0), ux=Parameter(name='None (internally: ux)', limits=(min=-180.0, max=180.0), value=0.0, fit=True, inverted=False, units='Degree'), uy=Parameter(name='None (internally: uy)', limits=(min=-180.0, max=180.0), value=0.0, fit=True, inverted=False, units='Degree'), uz=Parameter(name='None (internally: uz)', limits=(min=-180.0, max=180.0), value=0.0, fit=True, inverted=False, units='Degree'), U=array([[1., 0., 0.],
           [0., 1., 0.],
           [0., 0., 1.]]), UB=array([[ 1.15691131e+00, -7.08403864e-17, -7.08403864e-17],
           [ 0.00000000e+00,  1.15691131e+00, -7.08403864e-17],
           [ 0.00000000e+00,  0.00000000e+00,  1.15691131e+00]]), reflections=[])



Setup the UB orientation matrix using *hklpy*
---------------------------------------------

Define the crystal’s orientation on the diffractometer using the
2-reflection method described by `Busing & Levy, Acta Cryst 22 (1967)
457 <https://www.psi.ch/sites/default/files/import/sinq/zebra/PracticalsEN/1967-Busing-Levy-3-4-circle-Acta22.pdf>`__.

Choose the same wavelength X-rays for both reflections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    fourc.calc.wavelength = 1.54 # Angstrom (8.0509 keV)

Find the first reflection and identify its Miller indices: (*hkl*)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    r1 = fourc.calc.sample.add_reflection(
        4, 0, 0,
        position=fourc.calc.Position(
            ttheta=69.0966,
            theta=-145.451,
            chi=0,
            phi=0,
        )
    )

Find the second reflection
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    r2 = fourc.calc.sample.add_reflection(
        0, 4, 0,
        position=fourc.calc.Position(
            ttheta=69.0966,
            theta=-145.451,
            chi=90,
            phi=0,
        )
    )

Compute the *UB* orientation matrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``compute_UB()`` method always returns 1. Ignore it.

.. code:: ipython3

    fourc.calc.sample.compute_UB(r1, r2)




.. parsed-literal::

    1



Report what we have setup
-------------------------

.. code:: ipython3

    import pyRestTable
    
    tbl = pyRestTable.Table()
    tbl.labels = "term value".split()
    tbl.addRow(("energy, keV", fourc.calc.energy))
    tbl.addRow(("wavelength, angstrom", fourc.calc.wavelength))
    tbl.addRow(("position", fourc.position))
    tbl.addRow(("sample name", fourc.sample_name.get()))
    tbl.addRow(("[U]", fourc.U.get()))
    tbl.addRow(("[UB]", fourc.UB.get()))
    tbl.addRow(("lattice", fourc.lattice.get()))
    print(tbl)
    
    print(f"sample\t{fourc.calc.sample}")


.. parsed-literal::

    ==================== ===================================================
    term                 value                                              
    ==================== ===================================================
    energy, keV          8.050922077922078                                  
    wavelength, angstrom 1.54                                               
    position             FourCirclePseudoPos(h=-0.0, k=0.0, l=0.0)          
    sample name          silicon                                            
    [U]                  [[-1.22173048e-05 -1.22173048e-05 -1.00000000e+00] 
                          [ 0.00000000e+00 -1.00000000e+00  1.22173048e-05] 
                          [-1.00000000e+00  1.49262536e-10  1.22173048e-05]]
    [UB]                 [[-1.41343380e-05 -1.41343380e-05 -1.15691131e+00] 
                          [ 0.00000000e+00 -1.15691131e+00  1.41343380e-05] 
                          [-1.15691131e+00  1.72683586e-10  1.41343380e-05]]
    lattice              [ 5.431  5.431  5.431 90.    90.    90.   ]        
    ==================== ===================================================
    
    sample	HklSample(name='silicon', lattice=LatticeTuple(a=5.431, b=5.431, c=5.431, alpha=90.0, beta=90.0, gamma=90.0), ux=Parameter(name='None (internally: ux)', limits=(min=-180.0, max=180.0), value=-45.0, fit=True, inverted=False, units='Degree'), uy=Parameter(name='None (internally: uy)', limits=(min=-180.0, max=180.0), value=-89.99901005102187, fit=True, inverted=False, units='Degree'), uz=Parameter(name='None (internally: uz)', limits=(min=-180.0, max=180.0), value=135.00000000427607, fit=True, inverted=False, units='Degree'), U=array([[-1.22173048e-05, -1.22173048e-05, -1.00000000e+00],
           [ 0.00000000e+00, -1.00000000e+00,  1.22173048e-05],
           [-1.00000000e+00,  1.49262536e-10,  1.22173048e-05]]), UB=array([[-1.41343380e-05, -1.41343380e-05, -1.15691131e+00],
           [ 0.00000000e+00, -1.15691131e+00,  1.41343380e-05],
           [-1.15691131e+00,  1.72683586e-10,  1.41343380e-05]]), reflections=[(h=4.0, k=0.0, l=0.0), (h=0.0, k=4.0, l=0.0)], reflection_measured_angles=array([[0.        , 1.57079633],
           [1.57079633, 0.        ]]), reflection_theoretical_angles=array([[0.        , 1.57079633],
           [1.57079633, 0.        ]]))


Check the orientation matrix
----------------------------

Perform checks with *forward* (hkl to angle) and *inverse* (angle to
hkl) computations to verify the diffractometer will move to the same
positions where the reflections were identified.

Constrain the motors to limited ranges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  allow for slight roundoff errors
-  keep ``ttheta`` in the positive range
-  keep ``theta`` in the negative range
-  keep ``phi`` fixed at zero

.. code:: ipython3

    fourc.calc["ttheta"].limits = (-0.001, 180)
    fourc.calc["theta"].limits = (-180, 0.001)
    
    fourc.phi.move(0)
    fourc.engine.mode = "constant_phi"

Check the inverse calculation: (400)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    sol = fourc.inverse((-145.451, 0, 0, 69.0966))
    print("(4 0 0) ?", f"{sol.h:.2f}", f"{sol.k:.2f}", f"{sol.l:.2f}")


.. parsed-literal::

    (4 0 0) ? 4.00 0.00 0.00


Check another inverse calculation: (040)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    sol = fourc.inverse((-145.451, 90, 0, 69.0966))
    print("(0 4 0) ?", f"{sol.h:.2f}", f"{sol.k:.2f}", f"{sol.l:.2f}")


.. parsed-literal::

    (0 4 0) ? 0.00 4.00 0.00


Check the forward calculation: (400)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    sol = fourc.forward((4, 0, 0))
    print(
        "(400) :", 
        f"ttheta={sol.ttheta:.4f}", 
        f"theta={sol.theta:.4f}", 
        f"chi={sol.chi:.4f}", 
        f"phi={sol.phi:.4f}"
        )


.. parsed-literal::

    (400) : ttheta=69.0985 theta=-145.4500 chi=0.0000 phi=0.0000


Continue the E4CV example on your own…
