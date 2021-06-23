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

.. _diffract.energy:

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

.. _diffract.energy.units:

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


.. _diffract.energy.control_system:

Control System Energy
+++++++++++++++++++++

One way to connect the control system energy is to replace the ``energy``
attribute in the custom subclass of :class:`hkl.diffract.Diffractometer()`,
connecting it as either ``ophyd.EpicsSignal``, ``ophyd.EpicsSignalRO``, or
``ophyd.EpicsSignalWithRBV``.  In the next example, the monochromator energy,
engineering units, and offset are provided by EPICS.  Also, another EPICS PV
controls whether the energy of the diffractometer object should be updated by
changes in the EPICS energy.  Note that the
:meth:`~hkl.diffract.Diffractometer._energy_changed()` method is already
subscribed to updates in the ``energy`` signal.  It is not necessary to do this
in the custom subclass.  Don't forget to add the definitions for the real and
pseudo positioners.

.. code-block:: python
   :caption: Connecting control system energy to a 4-circle diffractometer.

    import gi
    gi.require_version('Hkl', '5.0')
    from hkl import E4CV
    import logging
    from ophyd import Component
    from ophyd import EpicsMotor
    from ophyd import EpicsSignal
    from ophyd import PseudoSingle

    logger = logging.getLogger(__name__)

    class LocalDiffractometer(E4CV):
        h = Component(PseudoSingle, '', kind="hinted")
        k = Component(PseudoSingle, '', kind="hinted")
        l = Component(PseudoSingle, '', kind="hinted")

        omega = Component(EpicsMotor, "EPICS:m1", kind="hinted")
        chi = Component(EpicsMotor, "EPICS:m2", kind="hinted")
        phi = Component(EpicsMotor, "EPICS:m3", kind="hinted")
        tth = Component(EpicsMotor, "EPICS:m4", kind="hinted")

        energy = Component(EpicsSignal, "EPICS:energy")
        energy_units = Component(EpicsSignal, "EPICS:energy.EGU")
        energy_offset = Component(EpicsSignal, "EPICS:energy:offset")
        energy_update_calc_flag = Component(EpicsSignal, "EPICS:energy:lock")

    fourc = LocalDiffractometer("", name="fourc")
    fourc.wait_for_connection()
    fourc._energy_changed()  # force the callback to update

----

Source code documentation
+++++++++++++++++++++++++

.. automodule:: hkl.diffract
    :members:
