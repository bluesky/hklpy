Ready-to-Use Devices
====================

These simulated diffractometer devices are ready-made classes in Python. To
configure them, the user needs only provide a name.

.. index:: !SimulatedE4CV

SimulatedE4CV
-------------

.. code-block:: python
   :caption: Create a simulated 4-circle Eulerian diffractometer.

    import gi
    gi.require_version("Hkl", "5.0")
    # MUST come before `import hkl`
    from hkl import SimulatedE4CV

    sim4c = SimulatedE4CV("", name="sim4c")

.. autoclass:: hkl.geometries.SimulatedE4CV
    :members:
    :noindex:

.. index:: !SimulatedE6C

SimulatedE6C
------------

.. code-block:: python
   :caption: Create a simulated 6-circle Eulerian diffractometer.

    import gi
    gi.require_version("Hkl", "5.0")
    # MUST come before `import hkl`
    from hkl import SimulatedE6C

    sim6c = SimulatedE6C("", name="sim6c")

.. autoclass:: hkl.geometries.SimulatedE6C
    :members:
    :noindex:

.. index:: !SimulatedK4CV

SimulatedK4CV
-------------

.. code-block:: python
   :caption: Create a simulated 4-circle Kappa diffractometer.

    import gi
    gi.require_version("Hkl", "5.0")
    # MUST come before `import hkl`
    from hkl import SimulatedK4CV

    simk4c = SimulatedK4CV("", name="simk4c")

.. autoclass:: hkl.geometries.SimulatedK4CV
    :members:
    :noindex:

.. index:: !SimulatedK6C

SimulatedK6C
------------

.. code-block:: python
   :caption: Create a simulated 6-circle Kappa diffractometer.

    import gi
    gi.require_version("Hkl", "5.0")
    # MUST come before `import hkl`
    from hkl import SimulatedK6C

    simk6c = SimulatedK6C("", name="simk6c")

.. autoclass:: hkl.geometries.SimulatedK6C
    :members:
    :noindex:
