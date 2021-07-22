
.. _geometries:

geometries
----------

See examples in the :ref:`examples.diffractometer` section.

.. toctree::
   :maxdepth: 2
   :glob:
   :caption: Ready-to-Use Devices

   geometry_tables

Source code documentation
+++++++++++++++++++++++++

.. automodule:: hkl.geometries
    :members:

----

.. _geometries.examples:

Examples
++++++++

Demonstrate the setup of diffractometers using the *hkl* package.

* :ref:`geometries.k4cv`
* :ref:`geometries.k4cve`
* :ref:`geometries.sim6c`

The :ref:`sample` :ref:`sample.examples` section describes how to setup
a crystal sample with an orientation matrix.


.. _geometries.sim6c:

``sim6c``: Eulerian 6-circle with simulated motors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is useful, sometimes, to create a simulated diffractometer where the
motor axes are provided by software simulations, [#]_ rather than using
the actual motors provided by the diffractometer.

.. [#] The ``ophyd.SoftPositioner`` is such a software simulation:
    https://blueskyproject.io/ophyd/positioners.html#ophyd.positioner.SoftPositioner

Load the simulated 6-circle geometry from *hklpy*:

.. code-block:: python
    :linenos:

    import gi
    gi.require_version("Hkl", "5.0")
    # MUST come before `import hkl`
    from hkl import SimulatedE6C

Create an instance of this diffractometer with::

    sim6c = SimulatedE6C("", name="sim6c")

.. _geometries.k4cv:

``k4cv`` : kappa 4-circle with EPICS motor PVs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To control a kappa diffractometer (in 4-circle geometry with vertical
scattering plane) where the motor axes are provided by EPICS PVs, use
``ophyd.EpicsMotor``. [#]_

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

In this case, we must first create a custom kappa 4-circle subclass and
connect our motor PVs to the positioners for the *real axes*:

.. code-block:: python
    :linenos:

    import gi
    gi.require_version("Hkl", "5.0")
    # MUST come before `import hkl`
    import hkl
    from ophyd import Component
    from ophyd import EpicsMotor
    from ophyd import PseudoSingle

    class KappaK4CV(hkl.K4CV):
        """K4CV: kappa diffractometer in 4-circle geometry"""

        h = Component(PseudoSingle, "")
        k = Component(PseudoSingle, "")
        l = Component(PseudoSingle, "")

        komega = Component(EpicsMotor, "sky:m1")
        kappa = Component(EpicsMotor, "sky:m2")
        kphi = Component(EpicsMotor, "sky:m3")
        tth = Component(EpicsMotor, "sky:m4")

Create an instance of this diffractometer with::

    k4cv = KappaK4CV("", name="k4cv")

.. _geometries.k4cve:

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
*added* to the control system energy (in
:meth:`~hkl.diffract.Diffractometer._update_calc_energy()`), before
conversion of the units to *keV* and then setting the diffractometer's
*calc* engine energy:

  calc engine *energy* (keV) = in_keV(control system *energy* + *offset*)

which then sets the wavelength:

  calc engine *wavelength* (angstrom) = :math:`h\nu` / calc engine *energy*

(:math:`h\nu=` 12.39842 angstrom :math:`\cdot` keV) and account for the
units of the control system *energy*.  To combine all this, we define a
new python class starting similar to ``KappaK4CV`` above, and adding the
energy signals.  Create the custom kappa 4-circle subclass with energy:

.. code-block:: python
    :linenos:

    import gi
    gi.require_version("Hkl", "5.0")
    # MUST come before `import hkl`
    import hkl
    from ophyd import Component
    from ophyd import PseudoSingle
    from ophyd import EpicsMotor
    from ophyd import EpicsSignal
    from ophyd import Signal
    import pint

    class KappaK4CV_Energy(hkl.K4CV):
        """
        K4CV: kappa diffractometer in 4-circle geometry with energy
        """

        h = Component(PseudoSingle, "")
        k = Component(PseudoSingle, "")
        l = Component(PseudoSingle, "")

        komega = Component(EpicsMotor, "sky:m1")
        kappa = Component(EpicsMotor, "sky:m2")
        kphi = Component(EpicsMotor, "sky:m3")
        tth = Component(EpicsMotor, "sky:m4")

        energy = Component(EpicsSignal, "optics:energy")
        energy_units = Component(EpicsSignal, "optics:energy.EGU")
        energy_offset = Component(Signal, value=0)
        energy_update_calc_flag = Component(
            EpicsSignal,
            "optics:energy_locked")

Create an instance of this diffractometer with::

    k4cve = KappaK4CV_Energy("", name="k4cve")

.. note::

    If you get a log message such as this on the console::

        W Fri-09:12:16 - k4cve not fully connected, k4cve.calc.energy not updated

    this informs you the update cannot happen until all EPICS
    PVs are connected.  The following code, will create the object, wait
    for all PVs to connect, then update the `calc` engine::

        k4cve = KappaK4CV_Energy("", name="k4cve")
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

    k4cve._energy_changed()

But this only works when the ``optics:energy_locked`` PV is 1 (permitted
to update the calc engine energy). To update the diffractometer's *calc*
engine energy and bypass the ``k4cve.energy_update_calc_flag`` signal,
call this command::

    k4cve._update_calc_energy()

Finally, to set the energy of the diffractometer's *calc* engine, use
one of these two methods:

============================   ============================
``energy_update_calc_flag``    command
============================   ============================
obey signal                    ``k4cve._energy_changed()``
ignore signal                  ``k4cve._update_calc_energy()``
============================   ============================

Each of these two methods will accept an optional ``value`` argument
which, if provided, will be used in place of the ``energy`` signal from
the control system.
