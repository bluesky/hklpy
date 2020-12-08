4-circle diffractometer example
===============================

The `IUCr provides a schematic of the 4-circle
diffractometer <http://ww1.iucr.org/iucr-top/comm/cteach/pamphlets/2/node14.html>`__
(in horizontal geometry typical of a laboratory instrument):

At X-ray synchrotrons, the vertical geometry is more common due to the
polarization of the X-rays.

Load the *hklpy* package (named *``hkl``*)
------------------------------------------

Since the *hklpy* package is a thin interface to the *hkl* library
(compiled C++ code), we need to **first** load the
*gobject-introspection* package (named *``gi``*) and name our required
code and version.

This is needed *every* time before the *hkl* package is first imported.

.. code:: ipython3

    import gi
    gi.require_version('Hkl', '5.0')

Setup the *E4CV* diffractometer in *hklpy*
------------------------------------------

In *hkl* *E4CV* geometry
(https://people.debian.org/~picca/hkl/hkl.html#org7ef08ba):

-  xrays incident on the :math:`\vec{x}` direction (1, 0, 0)

===== ======== =============================
axis  moves    rotation about axis
===== ======== =============================
omega sample   :math:`-\vec{y}` ``[0 -1 0]``
chi   sample   :math:`\vec{x}` ``[1 0 0]``
phi   sample   :math:`-\vec{y}` ``[0 -1 0]``
tth   detector :math:`-\vec{y}` ``[0 -1 0]``
===== ======== =============================

Define *this* diffractometer
----------------------------

Create a python class that specifies the names of the real-space
positioners. We call it ``FourCircle`` here but that choice is
arbitrary. Pick any valid Python name not already in use.

The argument to the ``FourCircle`` class tells which *hklpy* base class
will be used. This sets the geometry. See the `hklpy diffractometers
documentation <https://blueskyproject.io/hklpy/master/diffract.html#hkl.diffract.Diffractometer.calc_class>`__
for a list of other choices.

In *hklpy*, the reciprocal-space axes are known as ``pseudo``
positioners while the real-space axes are known as ``real`` positioners.
For the real positioners, it is possible to use different names than the
canonical names used internally by the *hkl* library. That is not
covered here.

note: The keyword argument ``kind="hinted"`` is an indication that this
signal may be plotted.

This demo uses simulated motors. To use EPICS motors, import that
structure from *ophyd*:

.. code:: python

   from ophyd import EpicsMotor

Then, in the class, replace the real positioners with (substituting with
the correct EPICS PV for each motor):

.. code:: python

   omega = Cpt(EpicsMotor, "pv_prefix:m41", kind="hinted")
   chi = Cpt(EpicsMotor, "pv_prefix:m22", kind="hinted")
   phi = Cpt(EpicsMotor, "pv_prefix:m35", kind="hinted")
   tth = Cpt(EpicsMotor, "pv_prefix:m7", kind="hinted")

and, **most important**, remove the ``def __init__()`` method. It is
only needed to define an initial position for the simulators. Otherwise,
this will move these EPICS motors to zero.

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
        omega = Cpt(SoftPositioner, kind="hinted")
        chi = Cpt(SoftPositioner, kind="hinted")
        phi = Cpt(SoftPositioner, kind="hinted")
        tth = Cpt(SoftPositioner, kind="hinted")
    
        def __init__(self, *args, **kwargs):
            """Define an initial position for simulators."""
            super().__init__(*args, **kwargs)
    
            for p in self.real_positioners:
                p._set_position(0)  # give each a starting position

.. code:: ipython3

    fourc = FourCircle("", name="fourc")

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
            tth=69.0966,
            omega=-145.451,
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
            tth=69.0966,
            omega=-145.451,
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
-  keep ``tth`` in the positive range
-  keep ``omega`` in the negative range
-  keep ``phi`` fixed at zero

.. code:: ipython3

    fourc.calc["tth"].limits = (-0.001, 180)
    fourc.calc["omega"].limits = (-180, 0.001)
    
    fourc.phi.move(0)
    fourc.engine.mode = "constant_phi"

Check the inverse calculation: (400)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    sol = fourc.inverse((-145.451, 0, 0, 69.0966))
    print("(4 0 0) ?", f"{sol.h:.2f}", f"{sol.k:.2f}", f"{sol.l:.2f}")


.. parsed-literal::

    (4 0 0) ? 4.00 0.00 0.00


Check the inverse calculation: (040)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        f"tth={sol.tth:.4f}", 
        f"omega={sol.omega:.4f}", 
        f"chi={sol.chi:.4f}", 
        f"phi={sol.phi:.4f}"
        )


.. parsed-literal::

    (400) : tth=69.0985 omega=-145.4500 chi=0.0000 phi=0.0000


Check the forward calculation: (040)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    sol = fourc.forward((0, 4, 0))
    print(
        "(040) :", 
        f"tth={sol.tth:.4f}", 
        f"omega={sol.omega:.4f}", 
        f"chi={sol.chi:.4f}", 
        f"phi={sol.phi:.4f}"
        )


.. parsed-literal::

    (040) : tth=69.0985 omega=-145.4500 chi=90.0000 phi=0.0000


Check the forward calculation: (440)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    sol = fourc.forward((4, 4, 0))
    print(
        "(440) :", 
        f"tth={sol.tth:.4f}", 
        f"omega={sol.omega:.4f}", 
        f"chi={sol.chi:.4f}", 
        f"phi={sol.phi:.4f}"
        )


.. parsed-literal::

    (440) : tth=106.6471 omega=-126.6755 chi=45.0000 phi=0.0000


Scan in reciprocal space using Bluesky
--------------------------------------

To scan with Bluesky, we need more setup.

.. code:: ipython3

    %matplotlib inline
    
    from bluesky import RunEngine
    from bluesky import SupplementalData
    from bluesky.callbacks.best_effort import BestEffortCallback
    import bluesky.plans as bp
    import bluesky.plan_stubs as bps
    import databroker
    import matplotlib.pyplot as plt
    
    plt.ion()
    
    bec = BestEffortCallback()
    db = databroker.temp().v1
    sd = SupplementalData()
    
    RE = RunEngine({})
    RE.md = {}
    RE.preprocessors.append(sd)
    RE.subscribe(db.insert)
    RE.subscribe(bec)




.. parsed-literal::

    1



(*h00*) scan near (400)
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    RE(bp.scan([], fourc.h, 3.9, 4.1, 5))


.. parsed-literal::

    
    
    Transient Scan ID: 1     Time: 2020-12-07 15:47:53
    Persistent Unique Scan ID: '67026d11-6546-4f40-b9c6-b704c81ea910'
    New stream: 'primary'
    +-----------+------------+------------+
    |   seq_num |       time |    fourc_h |
    +-----------+------------+------------+
    |         1 | 15:47:53.4 |      3.900 |
    |         2 | 15:47:53.4 |      3.950 |
    |         3 | 15:47:53.4 |      4.000 |
    |         4 | 15:47:53.4 |      4.050 |
    |         5 | 15:47:53.4 |      4.100 |
    +-----------+------------+------------+
    generator scan ['67026d11'] (scan num: 1)
    
    
    




.. parsed-literal::

    ('67026d11-6546-4f40-b9c6-b704c81ea910',)



chi scan from (400) to (040)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    RE(bp.scan([fourc.chi, fourc.h, fourc.k, fourc.l], fourc.chi, 0, 90, 10))


.. parsed-literal::

    
    
    Transient Scan ID: 2     Time: 2020-12-07 15:47:53
    Persistent Unique Scan ID: 'cf8f3d22-7c94-49eb-9ece-743b0fffe977'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+------------+
    |   seq_num |       time |  fourc_chi |    fourc_l |    fourc_k |    fourc_h |
    +-----------+------------+------------+------------+------------+------------+
    |         1 | 15:47:53.7 |      0.000 |      0.000 |      0.000 |      4.100 |
    |         2 | 15:47:54.0 |     10.000 |     -0.000 |      0.712 |      4.038 |
    |         3 | 15:47:54.3 |     20.000 |     -0.000 |      1.402 |      3.853 |
    |         4 | 15:47:54.5 |     30.000 |     -0.000 |      2.050 |      3.551 |
    |         5 | 15:47:54.8 |     40.000 |     -0.000 |      2.635 |      3.141 |
    |         6 | 15:47:55.0 |     50.000 |     -0.000 |      3.141 |      2.635 |
    |         7 | 15:47:55.3 |     60.000 |     -0.000 |      3.551 |      2.050 |
    |         8 | 15:47:55.5 |     70.000 |     -0.000 |      3.853 |      1.402 |
    |         9 | 15:47:55.7 |     80.000 |     -0.000 |      4.038 |      0.712 |
    |        10 | 15:47:56.0 |     90.000 |      0.000 |      4.100 |      0.000 |
    +-----------+------------+------------+------------+------------+------------+
    generator scan ['cf8f3d22'] (scan num: 2)
    
    
    




.. parsed-literal::

    ('cf8f3d22-7c94-49eb-9ece-743b0fffe977',)




.. image:: e4cv_files/e4cv_36_2.svg


(*0k0*) scan near (040)
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    RE(bp.scan([], fourc.k, 3.9, 4.1, 5))


.. parsed-literal::

    
    
    Transient Scan ID: 5     Time: 2020-12-07 15:49:23
    Persistent Unique Scan ID: 'b86c4725-4b62-4cf0-96b6-4912389e83f2'
    New stream: 'primary'
    +-----------+------------+------------+
    |   seq_num |       time |    fourc_k |
    +-----------+------------+------------+
    |         1 | 15:49:23.2 |      3.900 |
    |         2 | 15:49:23.3 |      3.950 |
    |         3 | 15:49:23.3 |      4.000 |
    |         4 | 15:49:23.3 |      4.050 |
    |         5 | 15:49:23.3 |      4.100 |
    +-----------+------------+------------+
    generator scan ['b86c4725'] (scan num: 5)
    
    
    




.. parsed-literal::

    ('b86c4725-4b62-4cf0-96b6-4912389e83f2',)



(*hk0*) scan near (440)
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    RE(bp.scan([], fourc.h, 3.9, 4.1, fourc.k, 3.9, 4.1, 5))


.. parsed-literal::

    
    
    Transient Scan ID: 4     Time: 2020-12-07 15:49:13
    Persistent Unique Scan ID: '52b70612-24ad-40a1-ac87-6bf9bedeb6e1'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+-------------+------------+------------+------------+
    |   seq_num |       time |    fourc_h |    fourc_k |    fourc_l | fourc_omega |  fourc_chi |  fourc_phi |  fourc_tth |
    +-----------+------------+------------+------------+------------+-------------+------------+------------+------------+
    |         1 | 15:49:13.4 |      3.900 |      3.900 |      0.000 |    -128.558 |     45.000 |      0.000 |    102.883 |
    |         2 | 15:49:14.0 |      3.950 |      3.950 |     -0.000 |    -127.627 |     45.000 |      0.000 |    104.745 |
    |         3 | 15:49:14.6 |      4.000 |      4.000 |     -0.000 |    -126.675 |     45.000 |      0.000 |    106.647 |
    |         4 | 15:49:15.3 |      4.050 |      4.050 |     -0.000 |    -125.703 |     45.000 |      0.000 |    108.593 |
    |         5 | 15:49:16.0 |      4.100 |      4.100 |      0.000 |    -124.706 |     45.000 |      0.000 |    110.585 |
    +-----------+------------+------------+------------+------------+-------------+------------+------------+------------+
    generator scan ['52b70612'] (scan num: 4)
    
    
    




.. parsed-literal::

    ('52b70612-24ad-40a1-ac87-6bf9bedeb6e1',)




.. image:: e4cv_files/e4cv_40_2.svg

