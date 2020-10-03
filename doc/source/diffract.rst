.. _diffract:

diffract
--------

A local subclass of the desired diffractometer geometry must be created
to define the reciprocal-space axes and customize the EPICS PVs used for
the motor axes.  Other capabilities are also customized in a local
subclass.

Examples are provided after the source code documentation.

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

These special-use geometries are also provided by the **hkl-c++**
library [#]_:

* :class:`hkl.diffract.Med2p3`
* :class:`hkl.diffract.Petra3_p09_eh2`
* :class:`hkl.diffract.SoleilMars`
* :class:`hkl.diffract.SoleilSiriusKappa`
* :class:`hkl.diffract.SoleilSiriusTurret`
* :class:`hkl.diffract.SoleilSixs`
* :class:`hkl.diffract.SoleilSixsMed1p2`
* :class:`hkl.diffract.SoleilSixsMed2p2`

In all cases, see the **hkl-c++** documentation for further information
on these geometries.

.. [#] **hkl-c++** documentation:
    https://people.debian.org/~picca/hkl/hkl.html#org7ea41dd

----

Source code documentation
+++++++++++++++++++++++++

.. automodule:: hkl.diffract
    :members:

----

_diffract.examples:

Examples
++++++++

Demonstrate the setup of diffractometers using the *hkl* package.

* ``sim6c`` : simulated 6-circle
* ``k4cv`` : kappa 4-circle with EPICS PVs for motors
* ``k4cve`` : ``k4cv`` with energy from local control system

The :ref:`sample` :ref:`sample.examples` section describes how to setup
a crystal sample with an orientation matrix.

.. _diffract.sim6c:

``sim6c``: 6-circle with simulated motors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is useful, sometimes, to create a simulated diffractometer where the
motor axes are provided by software simulations, rather than using the
actual motors provided by the diffractometer.

The ``ophyd.SoftPositioner`` [#]_ is such a software simulation.

.. [#] ``ophyd.SoftPositioner``:
    https://blueskyproject.io/ophyd/positioners.html#ophyd.positioner.SoftPositioner

Create the custom 6-circle subclass:

.. code-block:: python
    :linenos:

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

``k4cv`` : kappa 4-circle with EPICS motor PVs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To control a kappa diffractometer (in 4-circle geometry with vertical
scattering plane) where the motor axes are provided by EPICS PVs, use
`ophyd.EpicsMotor`. [#]_

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

.. [#] ``ophyd.EpicsMotor``:
    https://blueskyproject.io/ophyd/builtin-devices.html?highlight=epicsmotor#ophyd.epics_motor.EpicsMotor

Create the custom kappa 4-circle subclass:

.. code-block:: python
    :linenos:

    import gi
    gi.require_version('Hkl', '5.0')
    # MUST come before `import hkl`
    import hkl.diffract
    from ophyd import Component, PseudoSingle, EpicsMotor

    class KappaK4CV(hkl.diffract.K4CV):
        """K4CV: kappa diffractometer in 4-circle geometry"""

        h = Component(PseudoSingle, '')
        k = Component(PseudoSingle, '')
        l = Component(PseudoSingle, '')

        komega = Component(EpicsMotor, "sky:m1")
        kappa = Component(EpicsMotor, "sky:m2")
        kphi = Component(EpicsMotor, "sky:m3")
        tth = Component(EpicsMotor, "sky:m4")

Create an instance of this diffractometer with::

    k4cv = KappaK4CV('', name='k4cv')

``k4cve`` : ``k4cv`` with energy from local control system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extend the ``k4cv`` example above to use the energy as provided by the
local control system.  In this example, assume these are the PVs to be
used:

==============  ====================
signal          EPICS PV
==============  ====================
energy          optics:energy
energy units    optics:energy.EGU
energy locked?  optics:energy_locked
energy offset   no PV, same units as *energy* (above)
==============  ====================

The *energy locked?* signal is a flag controlled by the user that
controls whether (or not) the *energy* signal will update the wavelength
of the diffractometer's *calc* engine. We expect this to be either 1
(update the calc engine) or 0 (do NOT update the calc engine).

We'll also create a (non-EPICS) signal to provide for an energy offset
(in the same units as the control system energy). This offset will be
*added* to the control system energy, before conversion of the units to
*keV* and then setting the diffractometer's *calc* engine energy (which
then sets the wavelength)::

    calc engine *energy* (keV) = control system *energy* + *offset*

and account for the units of the control system *energy*.  To combine
all this, we define a new python class starting with `KappaK4CV` from
above, adding the energy signals.  Create the custom kappa 4-circle
subclass with energy:

.. code-block:: python
    :linenos:

    import gi
    gi.require_version('Hkl', '5.0')
    # MUST come before `import hkl`
    import hkl.diffract
    from ophyd import Component
    from ophyd import PseudoSingle
    from ophyd import EpicsSignal, EpicsMotor, Signal
    import pint

    class KappaK4CV_Energy(hkl.diffract.K4CV):
        """
        K4CV: kappa diffractometer in 4-circle geometry with energy
        """

        h = Component(PseudoSingle, '')
        k = Component(PseudoSingle, '')
        l = Component(PseudoSingle, '')

        komega = Component(EpicsMotor, "sky:m1")
        kappa = Component(EpicsMotor, "sky:m2")
        kphi = Component(EpicsMotor, "sky:m3")
        tth = Component(EpicsMotor, "sky:m4")

        energy = Component(EpicsSignal, "optics:energy")
        energy_EGU = Component(EpicsSignal, "optics:energy.EGU")
        energy_update_calc = Component(
            EpicsSignal,
            "optics:energy_locked")
        energy_offset = Component(Signal, value=0)

        def _energy_changed(self, value=None, **kwargs):
            '''
            Callback indicating that the energy signal was updated
            '''
            if not self.connected:
                logger.warning(
                    "%s not fully connected, %s.calc.energy not updated",
                    self.name, self.name)
                return
            if self.energy_update_calc.get() in (1, "Yes", "locked", "OK"):
                # energy_offset has same units as energy
                local_energy = value + self.energy_offset.get()

                # either get units from control system
                units = self.energy_EGU.get()
                # or define as a constant here
                # units = "eV"

                keV = pint.Quantity(local_energy, units).to("keV")
                logger.debug(
                    "setting %s.calc.energy = %f (keV)",
                    self.name, keV.magnitude)
                self._calc.energy = keV.magnitude
                self._update_position()

Create an instance of this diffractometer with::

    k4cve = KappaK4CV_Energy('', name='k4cve')

.. note::

    This command will print a log message to the console::

        W Fri-09:12:16 - k4cve not fully connected, k4cve.calc.energy not updated

    which is expected since the update cannot happen until all EPICS
    PVs are connected.  This code, will create the object, wait for
    all PVs to connect, then update the `calc` engine::

        k4cve = KappaK4CV_Energy('', name='k4cve')
        k4cve.wait_for_connection()
        k4cve._energy_changed(k4cve.energy.get())

To set the energy offset from the command line::

    %mov k4cve.energy_offset 50

which means the diffractometer (assuming the control system uses "eV"
units) will use an energy that is 50 eV *higher* than the control system
reports. The diffractometer's *calc* engine will **only** be updated
when the energy signal is next updated.  To force an update to the calc
engine, call ``_energy_changed()`` directly with the energy value as the
argument::

    k4cve._energy_changed(k4cve.energy.get())

But this only works when the ``optics:energy_locked`` PV is 1 (permitted
to update the calc engine energy). To update the diffractometer's *calc*
engine energy and bypass the ``k4cve.energy_update_calc`` signal, we can
call these routines on the command console::

    %mov diffractometer.energy_update_calc 1
    diffractometer._energy_changed(diffractometer.energy.get())
    %mov diffractometer.energy_update_calc 0

or we need to modify the ``_energy_changed()`` method and provide an
additional method that does not check this signal.  We'll move code into
the new method and modify ``_energy_changed()`` to call it:

.. code-block:: python
    :linenos:

        def _energy_changed(self, value=None, **kwargs):
            '''
            Callback indicating that the energy signal was updated
            '''
            if not self.connected:
                logger.warning(
                    "%s not fully connected, %s.calc.energy not updated",
                    self.name, self.name)
                return

            if self.energy_update_calc.get() in (1, "Yes", "locked", "OK"):
                self._update_calc_energy(value)

        def _update_calc_energy(self, value=None, **kwargs):
            '''
            Callback indicating that the energy signal was updated
            '''
            if not self.connected:
                logger.warning(
                    "%s not fully connected, %s.calc.energy not updated",
                    self.name, self.name)
                return

            # use either supplied value or get from signal
            value = value or self.energy.get()

            # energy_offset has same units as energy
            local_energy = value + self.energy_offset.get()

            # either get units from control system
            units = self.energy_EGU.get()
            # or define as a constant here
            # units = "eV"

            keV = pint.Quantity(local_energy, units).to("keV")
            logger.debug(
                "setting %s.calc.energy = %f (keV)",
                self.name, keV.magnitude)
            self._calc.energy = keV.magnitude
            self._update_position()

Finally, to set the diffractometer's *calc* engine energy, use one of
these two methods:

=====================================   ============================
motive                                  command
=====================================   ============================
obey ``energy_update_calc`` signal      ``k4cve._energy_changed()``
ignore ``energy_update_calc`` signal    ``k4cve._update_calc_energy()``
=====================================   ============================

Each of these two methods will accept an optional ``value`` argument
which, if provided, will be used in place of the ``energy`` signal from
the control system.
