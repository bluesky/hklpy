========
Overview
========

The ``hklpy`` package provides controls for using diffractometers within the
`Bluesky Framework <https://blueskyproject.io>`_.
:class:`~hkl.diffract.Diffractometer()` is the base class from which all the
different diffractometer geometries are built.  Built on the
`ophyd.PseudoPositioner
<https://blueskyproject.io/ophyd/positioners.html#pseudopositioner>`_ interface,
it defines all the components of a diffractometer.  The different geometries
specify the names and order for the real motor axes.

Definitions
===========

Several terms used throughout are:

.. index:: !real

real axis (positioner)
----------------------

A positioner (whether simulated or attached to hardware) that operates in
*real* space.  Typically an instance of `ophyd.EpicsMotor
<https://blueskyproject.io/ophyd/builtin-devices.html#epicsmotor>`_
or
`ophyd.SoftPositioner
<https://blueskyproject.io/ophyd/positioners.html#softpositioner>`_.

.. index:: !pseudo

pseudo axis (positioner)
------------------------

A positioner (whether simulated or attached to hardware) that operates in
*reciprocal* space.  Typically an instance of `ophyd.PseudoSingle
<https://blueskyproject.io/ophyd/positioners.html#ophyd.pseudopos.PseudoSingle>`_.

.. index:: !forward

forward (transformation)
------------------------

Compute the values of the real positioners given values of the pseudo
positioners.  Since more than one solution is possible, additional
constraints (limits on the real positioner and diffractometer mode) may be
added.

.. index:: !inverse

inverse (transformation)
------------------------

Compute the values of the pseudo positioners given values of the real
positioners.

.. index:: !libhkl

*libhkl* support library
------------------------

The transformation between real and reciprocal (_pseudo_) space are passed
(from :mod:`hkl.diffract` through :mod:`hkl.calc`) to a support library
known here as *libhkl* (https://repo.or.cz/hkl.git), written in C++.

Parts of a `Diffractometer` object
==================================

A ``Diffractometer`` object has several parts:

name
----

The ``name`` of the :class:`~hkl.diffract.Diffractometer()` instance is
completely at the choice of the user and conveys no specific information to
the underlying Python support code.

One important convention is that the name given on the left side of the ``=``
matches the name given by the ``name="..."`` keyword, such as this example::

    e4cv = E4CV("", name="e4cv")

.. index:: geometry

geometry
--------

The geometry describes the physical arrangement of real positioners that
make up the diffractometer.  The choices are limited to those geometries
provided in :mod:`hkl.geometries` (which are the geometries provided by the
*libhkl* support library).  A geometry will provide a list of the real
positioners.  It is possible to use alternate names.

.. TODO: how to add a new geometry? (text does not yet exist)

.. index:: calc

calc
----

The ``calc`` attribute, set when the :class:`~hkl.diffract.Diffractometer`
object is defined, connects with the underlying *libhkl* support library.
While a user might call certain methods from this
:class:`~hkl.calc.CalcRecip()` object, it is usually not necessary.  The
most common term from this layer would be the actual wavelength used for
computations.  Using from the example above, ``DFRCT.calc.wavelength``
(where ``DFRCT`` is the diffractometer object, such as ``e4cv`` above),
expressed in Angstrom units. Normally, the user will set the energy in the
diffractometer object, ``DFRCT.energy``, which will then set the wavelength.

The ``calc`` contains the methods that convert between energy and
wavelength. To use this Python support at an instrument that does not use
X-rays (such as a neutron source), re-write these methods and also redefine
any classes that use :class:`hkl.calc.CalcRecip()`.

.. index:: energy

energy
------

The :ref:`energy <diffract.energy>` of the diffractometer sets the
wavelength, which is used when:

#. computing ``forward()`` and ``inverse()`` transformations
#. defining orientation reflections
#. documenting the state of the diffractometer

It is more common for users to describe energy than wavelength.  The
high-level interface allows the energy to be expressed in any
:ref:`engineering units <diffract.energy.units>` that are convertible to
the expected units (`keV`).  An offset may be applied, which is useful when
connecting the diffractometer energy with a control system variable.
(See the :ref:`diffract.energy.control_system` section.)

.. index:: sample

sample
------

The point of a diffractometer is to position a sample for scientific
measurements. The ``sample`` attribute is an instance of
:class:`hkl.sample.HklSample`. Behind the scenes, the
:class:`hkl.diffract.Diffractometer` object maintains a *dictionary* of
samples (keyed by ``name``), each with its own :class:`hkl.utils.Lattice`
and orientation (reflections) information.

.. index:: lattice

lattice
-------

Crystal :class:`hkl.utils.Lattice` parameters of unit cell lengths and angles.

.. index:: orientation

orientation
-----------

The **UB** matrix describes the ``forward()`` and ``inverse()`` transformations
that allow precise positioning of a crystal's atomic planes in the laboratory
reference system of the diffractometer.  Typically, the **UB** matrix is computed
(by *libhkl*) from two orientation reflections.

.. index:: constraint

constraint
----------

The ``forward()`` transformation can have many solutions.  A
:class:`~hkl.diffract.Constraint` can be applied to a real positioner to
limit the range of solutions accepted for that positioner.

.. TODO: more explanation here?  or link?

.. index:: mode

mode
----

The ``forward()`` transformation can have many solutions.  The
diffractometer is set to a mode (chosen from a list specified by the
diffractometer geometry) that controls how values for each of the real
positioners will be controlled. A mode can control relationships between
real positioners in addition to limiting the motion of a real positioner.
Further, a mode can specify an additional reflection which will be used to
determine the outcome of the ``forward()`` transformation.

=======================  =======================
object                   meaning
=======================  =======================
``DFRCT.engine.mode``    mode selected now
``DFRCT.engine.modes``   list of possible modes
=======================  =======================

Here, ``DFRCT`` is the diffractometer object (such as ``e4cv`` above).

Steps to define a diffractometer object
=======================================

#. Identify the geometry.
#. Check that it is supported in  :mod:`hkl.geometries`.
#. Create a custom subclass for the diffractometer.
#. Connect the real positioners with the control system motors.
#. (optional) Connect energy to the control system.
#. Define the diffractometer object from the custom subclass.

Use a Diffractometer with the bluesky RunEngine
===============================================

The positioners of a :class:`~hkl.diffract.Diffractometer` object may be
used with the `bluesky RunEngine
<https://blueskyproject.io/bluesky/generated/bluesky.run_engine.RunEngine.html?highlight=runengine>`_
with any of the `pre-assembled plans
<https://blueskyproject.io/bluesky/plans.html#pre-assembled-plans>`_ or
in custom plans of your own.  ::

    fourc = hkl.geometries.SimulatedE4CV("", name="fourc")
    # steps not shown here:
    #   define a sample & orientation reflections, and compute UB matrix

    # record the diffractometer metadata to a run
    RE(bp.count([fourc]))

    # relative *(h00)* scan
    RE(bp.rel_scan([scaler, fourc], fourc.h, -0.1, 0.1, 21))

    # absolute *(0kl)* scan
    RE(bp.scan([scaler, fourc], fourc.k, 0.9, 1.1, fourc.l, 2, 3, 21))

    # absolute ``chi`` scan
    RE(bp.scan([scaler, fourc], fourc.chi, 30, 60, 31))

Keep in mind these considerations:

1. Don't mix axis types (pseudos *v.* reals) in a scan.  You can only
   scan with either *pseudo* axes (``h``, ``k``, ``l``, ``q``, ...) or *real*
   axes (``omega``, ``tth``, ``chi``, ...) at one time.  You cannot scan with
   both types (such as ``h`` and ``tth``) in a single scan (because the
   :meth:`~hkl.diffract.Diffractometer.forward()` and
   :meth:`~hkl.diffract.Diffractometer.inverse()` methods cannot
   resolve).  Example::

       # Cannot scan both ``k`` and ``chi`` at the same time.
       # This will raise a `ValueError` exception.
       RE(bp.scan([scaler, fourc], fourc.k, 0.9, 1.1, fourc.chi, 2, 3, 21))


2. When scanning with pseudo axes (``h``, ``k``, ``l``, ``q``, ...), first
   check that all steps in the scan can be computed successfully with
   the :meth:`~hkl.diffract.Diffractometer.forward()` computation::

        fourc.forward(1.9, 0, 0)

3. Include the diffractometer object as an additional detector
   to record the diffractometer metadata [#]_ as part of the scan.
   For example::

       fourc = hkl.geometries.SimulatedE4CV("", name="fourc")
       RE(bp.scan([scaler, fourc], fourc.h, 1.9, 2.1, 21))

4. To save crystal orientation and reflections for later use,
   include the diffractometer object as an additional detector
   (as stated in consideration 3 above)::

       RE(bp.scan([scaler, fourc], fourc.chi, 30, 60, 31))
       #                   ^^^^^


5. To restore crystal lattice and orientation reflections from a previous
   run, first use the `databroker
   <https://blueskyproject.io/databroker/tutorials/search-and-lookup.html#find-runs-in-a-catalog>`_
   to find the run.  (The :func:`hkl.util.list_orientation_runs()` function
   can list any recent runs with orientation information.  It needs
   the databroker catalog object.)  With the run, use
   :func:`hkl.util.run_orientation_info()` to obtain
   the orientation information.
   Then call :func:`hkl.util.restore_orientation()`
   with the run's orientation information.  Here is an example
   with the `fourc` object created above and a previous run with
   ``scan_id = 457``::

        # find a run
        hkl.util.list_orientation_runs(cat)

        # get the run's orientation metadata
        info = hkl.util.run_orientation_info(cat[457])

        # restore the orientation
        hkl.util.restore_orientation(info["fourc"], fourc)

6. You should only restore orientation reflections from a **matching**
   diffractometer geometry (such as ``E4CV``).  A `ValueError`
   exception will be raised if the geometry names (one of the names
   in :mod:`hkl.geometries`) do not match.  To override this check
   (at your own risk), replace :func:`hkl.util._check_geometry`
   with your own code.

7. A sample lattice can be restored into any
   :class:`~hkl.diffract.Diffractometer` object, as long
   as it has not already been defined (by name) in that object::

        info = hkl.util.run_orientation_info(cat[457])
        hkl.util.restore_sample(info["fourc"], fourc)

8. If you want to save other information during a run, or save
   this information in a different format, it is suggested to
   write that information as a separate stream using a custom plan.

.. [#] The diffractometer metadata will be recorded in the scan's
   descriptor document and can be retrieved later for analysis or use in
   other scans.  Recorded data includes diffractometer name and
   geometry, sample name and lattice, orientation reflections, ...  A
   complete list of the metadata keys is available from the
   diffractometer object as either an ophyd
   `Signal <https://blueskyproject.io/ophyd/signals.html#signals>`_
   (such as ``fourc.orientation_attrs.get()``) or a direct attribute (such
   as ``fourc._orientation_attrs``).
