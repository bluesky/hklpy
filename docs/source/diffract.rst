.. _diffract:

diffract
--------

A local subclass of :class:`hkl.diffract.Diffractometer` for the desired
diffractometer geometry must be created to define the reciprocal-space
axes and customize the EPICS PVs used for the motor axes.  Other
capabilities are also customized in a local subclass.

Examples are provided in the 
:ref:`Geometries Examples <geometries.examples>` section.

These are the diffractometer geometries provided by the **libhkl**
library [#libhkl]_:

==============================  ==========================
name                            description
==============================  ==========================
:class:`~hkl.geometries.E4CH`   Eulerian 4-circle, vertical scattering plane
:class:`~hkl.geometries.E4CV`   Eulerian 4-circle, horizontal scattering plane
:class:`~hkl.geometries.E6C`    Eulerian 6-circle
:class:`~hkl.geometries.K4CV`   Kappa 4-circle, vertical scattering plane
:class:`~hkl.geometries.K6C`    Kappa 6-circle
:class:`~hkl.geometries.TwoC`   2-circle
:class:`~hkl.geometries.Zaxis`  Z-axis
==============================  ==========================

These special-use geometries are also provided by the **libhkl**
library [#libhkl]_:

* :class:`~hkl.geometries.Med2p3`
* :class:`~hkl.geometries.Petra3_p09_eh2`
* :class:`~hkl.geometries.SoleilMars`
* :class:`~hkl.geometries.SoleilSiriusKappa`
* :class:`~hkl.geometries.SoleilSiriusTurret`
* :class:`~hkl.geometries.SoleilSixs`
* :class:`~hkl.geometries.SoleilSixsMed1p2`
* :class:`~hkl.geometries.SoleilSixsMed2p2`

In all cases, see the **libhkl** documentation for further information
on these geometries.

.. [#libhkl] **libhkl** documentation:
    https://people.debian.org/~picca/hkl/hkl.html

Energy
++++++

The monochromatic X-ray energy used by the diffractometer is defined as
an ophyd ``Signal``.  The ``.energy`` signal may be used as-provided, as
a constant or the Component may be replaced by an ``ophyd.EpicsSignal``
in a custom subclass of :class:`~hkl.diffract.Diffractometer`, to
connect with an EPICS PV from the instrument's control system.  There is
no corresponding ``.wavelength`` signal at the diffractometer level.
The ``.energy_offset`` signal is used to allow for a difference between
the reported energy of ``.energy`` and the energy used for
diffractometer operations ``.calc.energy``.  

These are the terms:

==================== =======================
term                 meaning
==================== =======================
``.energy``          nominal energy (such as value reported by control system)
``.energy_offset``   adjustment from nominal to calibrated energy for diffraction
``.energy_units``    engineering units to be used for ``.energy`` and ``.energy_offset``
``.calc.energy``     energy for diffraction (used to compute wavelength)
``.calc.wavelength`` used for diffraction calculations
==================== ======================= 

These are the relationships::

    .calc.energy = in_keV(.energy + .energy_offset)
    .calc.wavelength = A*keV / .calc.energy

For use with other types of radiation (such as neutrons or electrons),
the conversion between energy and wavelength must be changed by editing
the energy and wavelength methods in the :class:`hkl.calc.CalcRecip`
class.

When the Diffractometer ``.energy`` signal is written (via
``.energy.put(value)`` operation), the ``.energy_offset`` is added.
This result is converted to ``keV`` as required by the lower-level
:mod:`hkl.calc` module, and then written to ``.calc.energy`` which in
turn writes the ``.calc.wavelength`` value. Likewise, when
``.energy.get()`` reads the energy, it takes its value from
``.calc.energy``, converts into ``.energy_units``, and then applies
``.energy_offset``.

.. tip:: How to set energy, offset, and units

    To change energy, offset, & units, do it in this order:

    * First, set units and offset
    * Finally, set energy

    Example for a ``e4cv`` diffractometer::

        e4cv.energy_units.put("eV")
        e4cv.energy_offset.put(1.5)
        e4cv.energy.put(8000)
        # now, e4cv.calc.energy = 8.0015 keV


Engineering Units
+++++++++++++++++

The :mod:`~hkl.geometries` module is the main user interface, providing
the various diffractometer geometries provided by **libhkl** as *ophyd*
`PseudoPositioner` Devices [#]_.  Each of these geometries is built from
the base class :class:`~hkl.diffract.Diffractometer`, where a feature
has been added to allow the energy units to be set by the user.
Internally, :class:`~hkl.diffract.Diffractometer` will apply any
necessary units conversion when interacting with the values from the
:mod:`~hkl.calc` module.

In the :mod:`~hkl.calc` module (lower level than
:class:`~hkl.diffract.Diffractometer`), the units for *energy* and
*wavelength* are ``keV`` and ``angstrom``, respectively.  These
engineering units are not changeable by the user since the **libhkl** code
requires a consistent set of units (it does not anticipate the need to
do a units conversion).

The Python *pint* package [#]_ is used to apply any unit conversion.

This table summarizes the units for the energy and wavelength terms
for all diffractometer geometries.

==========================  =================
diffractometer attribute    engineering units
==========================  =================
``.energy``                 set by value of ``.energy_units`` Signal
``.calc.energy``            ``keV``
``.wavelength``             does not exist in :class:`~hkl.diffract.Diffractometer`
``.calc.wavelength``        ``angstrom``
==========================  =================

.. [#] *ophyd* `PseudoPositioner` Device:
   https://blueskyproject.io/ophyd/positioners.html#pseudopositioner
.. [#] *pint* (for engineering units conversion):
   https://pint.readthedocs.io

----

Source code documentation
+++++++++++++++++++++++++

.. automodule:: hkl.diffract
    :members:
