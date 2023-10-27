
.. _configuration:

configuration
-------------

Record the configuration of the diffractometer so that it can be restored later.

Users want to see a list of reflections, samples, etc. from their recent
session, even after the session stops. Multiple sessions could (optionally) access
the same list or use a different one.

This code provides a core representation of a diffractometer's configuration and
methods to export and restore that configuration. User code could choose to
write the configuration to a file, an EPICS PV, or some other persistent
location.

Configuration dictionary
++++++++++++++++++++++++

*Configuration* includes:

* geometry
* current wavelength of the source
* soft limits (constraints) on the physical axes
* list [#axes.order]_ of reciprocal-space axes names
* list [#axes.order]_ of canonical (geometry-defined) real-space axes names
* list [#axes.order]_ of real-space axes names as the user has defined
* list of samples
* other general metadata about the diffractometer.  

.. [#axes.order] The axes names are listed in the order prescribed by the back-end library.

Each sample includes:

* name
* crystal lattice constants
* list of orientation reflections
* :math:`U` matrix
* :math:`UB` matrix

Each reflection includes:

* coordinates of the reciprocal-space axes
* coordinates of the real-space axes
* wavelength to be used for the reflection
* a flag indicating if the reflection is used to calculate the orientation
* a ``fit`` parameter used by the *libhkl* backend library

To enable some generality when restoring reflections, the real-space coordinates
are recorded using the canonical (not user-defined) axis names defined by the
diffractometer geometry.

The complete configuration list could be saved into a file, stored in the
current working directory or elsewhere. A session could load this file by
default, start a new one, or load from somewhere else.  Or, the files could be
saved by time-stamp to compare as the configuration changes.

Alternatively, the list could be saved as text into an EPICS PV (the PV would
need to handle text of several kilobytes in size).  Or into a memory cache, such
as `redis <https://redis.io>`_.

Export
++++++

The diffractometer configuration can be exported to any of the formats shown in
the table below. Assuming ``config`` is the object returned by calling
:class:`~hkl.DiffractometerConfiguration()`:

===========================  ============================================================
command                      returns
===========================  ============================================================
``config.export()``          Defaults to JSON format.  See below.
``config.export("json")``    `JSON string <https://json.org>`_
``config.export("dict")``    `Python dict <https://docs.python.org/3/library/stdtypes.html#dict>`_
``config.export("yaml")``    `YAML string <https://yaml.org>`_
===========================  ============================================================

Restore
+++++++

A single command is used to set a diffractometer's configuration from a Python object.
Assuming:

* ``config`` is the object returned by calling :class:`~hkl.DiffractometerConfiguration()`
* ``settings`` contains the configuration object (dict, json, or yaml) to be restored

The same command is used to restore the configuration settings from either dict,
JSON string, or YAML string.  The
:meth:`~hkl.DiffractometerConfiguration.restore` method will determine the
data type from its structure::

    config.restore(settings)

The example below demonstrates this process using a YAML file.

Example
+++++++

Build a diffractometer (using E4CV geometry)::

    import numpy
    from hkl import SimulatedE4CV
    from hkl.configuration import DiffractometerConfiguration
    from hkl.util import new_lattice

    e4c = SimulatedE4CV("", name="e4c")
    config = DiffractometerConfiguration(e4c)

Add a sample::

    a0 = 2 * numpy.pi
    cubic = new_lattice(a0)
    e4c.calc.new_sample("vibranium", lattice=cubic)

Define some reflections.  Pick two of them to define its orientation::

    _r400 = e4c.calc.sample.add_reflection(4, 0, 0, (-145.451, 0, 0, 69.0966)),
    _r040 = e4c.calc.sample.add_reflection(0, 4, 0, (-145.451, 0, 90, 69.0966))
    _r004 = e4c.calc.sample.add_reflection(0, 0, 4, (-145.451, 90, 0, 69.0966))
    e4c.calc.sample.compute_UB(_r040, _r004)

Save the orientation and other configuration::

    settings = config.export()
    with open("e4c-config.json", "w") as f:
        f.write(settings)

A :download:`JSON </_static/e4c-config.json>` example of this file can be
downloaded. (Compare with :download:`YAML </_static/e4c-config.yml>`.) This example
configuration can be restored to any diffractometer with matching ``"geometry":
"E4CV"``::

    with open("e4c-config.json") as f:
        settings = f.read()
        config.restore(settings, clear=True)

The extra keyword argument, ``clear=True`` (which is the default), means to
first remove any previous configuration of the diffractometer and reset it to
default values before restoring the configuration.

API
+++

.. automodule:: hkl.configuration
    :members: DiffractometerConfiguration
    :exclude-members: Diffractometer
 