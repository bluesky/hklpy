
diffract
--------

In most cases, a local subclass of the desired
diffractometer geometry is created to customize
the EPICS PVs used for the motor axes.  Other
capabilities are also customized in a local subclass.

These are the diffractometer geometries defined:

===========================  ==========================
name                         description
===========================  ==========================
:class:`hkl.diffract.E4CH`   Eulerian 4-circle, vertical scattering plane
:class:`hkl.diffract.E4CV`   Eulerian 4-circle, horizontal scattering plane
:class:`hkl.diffract.E6C`    Eulerian 6-circle
:class:`hkl.diffract.K4CV`   Kappa 4-circle, vertical scattering plane
:class:`hkl.diffract.K6C`    Kappa 6-circle
:class:`hkl.diffract.TwoC`   2-circle
:class:`hkl.diffract.Zaxis`  Z-axis
===========================  ==========================

These special-use geometries provided by the
**hkl-c++** library are also provided:

* :class:`hkl.diffract.Med2p3`
* :class:`hkl.diffract.Petra3_p09_eh2`
* :class:`hkl.diffract.SoleilMars`
* :class:`hkl.diffract.SoleilSiriusKappa`
* :class:`hkl.diffract.SoleilSiriusTurret`
* :class:`hkl.diffract.SoleilSixs`
* :class:`hkl.diffract.SoleilSixsMed1p2`
* :class:`hkl.diffract.SoleilSixsMed2p2`

In all cases, see the **hkl-c++** documentation
for further information on these geometries.

https://people.debian.org/~picca/hkl/hkl.html#org7ea41dd

## Examples

Demonstrate the setup of diffractometers using the *hkl* package.

* ``sim6c`` : simulated 6-circle
* ``k4cv`` : kappa 4-circle with EPICS PVs for motors
* ``k4cve`` : ``k4cv`` with energy from local control system

### 6-circle with simulated motors

It is useful, sometimes, to create a simulated
diffractometer where the motor axes are provided
by software simulations, rather than using the
actual motors provided by the diffractometer.

The ``ophyd.SoftPositioner`` [#]_ is such a software simulation.

.. [#] ``ophyd.SoftPositioner``: https://blueskyproject.io/ophyd/positioners.html#ophyd.positioner.SoftPositioner

Create the custom 6-circle subclass::

    import gi
    gi.require_version('Hkl', '5.0')
    # MUST come before `import hkl`
    import hkl.diffract
    from ophyd import Component, PseudoSingle, SoftPositioner

    class SimulatedE6C(hkl.diffract.E6C):
        """E6C: Simulated (soft) 6-circle diffractometer"""

        h = Component(PseudoSingle, '')
        k = Component(PseudoSingle, '')
        l = Component(PseudoSingle, '')

        mu = Component(SoftPositioner)
        omega = Component(SoftPositioner)
        chi = Component(SoftPositioner)
        phi = Component(SoftPositioner)
        gamma = Component(SoftPositioner)
        delta = Component(SoftPositioner)

        def __init__(self, *args, **kwargs):
            """
            start the SoftPositioner objects with initial values
            """
            super().__init__(*args, **kwargs)
            for axis in self.real_positioners:
                axis.move(0)

Create an instance of this diffractometer with::

    sim6c = SimulatedE6C('', name='sim6c')

### kappa 4-circle with EPICS motor PVs

To control a kappa diffractometer (in 4-circle geometry
with vertical scattering plane)
where the motor axes are provided
by EPICS PVs, use `ophyd.EpicsMotor`. [#]_

In this example, we know from our local control system that
the kappa motors have these PVs:

==========  =========
kappa axis  EPICS PVs
==========  =========
komega      sky:m1
kappa       sky:m2
kphi        sky:m3
tth         sky:m4
==========  =========

.. [#] ``ophyd.EpicsMotor``: https://blueskyproject.io/ophyd/builtin-devices.html?highlight=epicsmotor#ophyd.epics_motor.EpicsMotor

Create the custom kappa 4-circle subclass::

    import gi
    gi.require_version('Hkl', '5.0')
    # MUST come before `import hkl`
    import hkl.diffract
    from ophyd import Component, PseudoSingle, EpicsMotor

    class SimulatedE6C(hkl.diffract.K6CV):
        """E6C: kappa diffractometer in 4-circle geometry"""

        h = Component(PseudoSingle, '')
        k = Component(PseudoSingle, '')
        l = Component(PseudoSingle, '')

        komega = Component(EpicsMotor, "sky:m1")
        kappa = Component(EpicsMotor, "sky:m2")
        kphi = Component(EpicsMotor, "sky:m3")
        tth = Component(EpicsMotor, "sky:m4")

Create an instance of this diffractometer with::

    k4cv = SimulatedE6C('', name='k4cv')

### ``k4cv`` with energy from local control system

-tba-

----

## Source code documentation

.. automodule:: hkl.diffract
    :members:
