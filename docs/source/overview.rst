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
