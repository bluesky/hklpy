.. include:: /substitutions.txt

.. _user_guide:

==========
User Guide
==========

.. caution:: reorganizational work-in-progress

|hklpy| provides `ophyd <https://blueskyproject.io/ophyd>`_ diffractometer
devices.  Each diffractometer is an ophyd `PseudoPositioner <https://blueskyproject.io/ophyd/user/reference/positioners.html#pseudopositioner>`_
which may be used with `bluesky <https://blueskyproject.io/bluesky>`_ plans.

*Hkl* (`documentation <https://people.debian.org/~picca/hkl/hkl.html>`_), from
Synchrotron Soleil, is used as a backend library to convert between real-space
motor coordinates and reciprocal-space crystallographic coordinates.  Here, we
refer to this library as |libhkl| to clarify and distinguish from other use of
of the term *hkl*.  Multiple source code repositories exist. |hklpy| uses the
`active development repository <https://repo.or.cz/hkl.git>`_.

All diffractometers can be provisioned with simulated axes; motors from an EPICS
control system are not required to use |hklpy|. A few diffractometer simulators
are provided :ref:`ready to use <ready_to_use>`.


.. toctree::
   :glob:
   :hidden:

   overview
   ready_to_use
   examples/*
   constraints

.. grid:: 1

    .. grid-item:: 

        .. grid:: 2

            .. grid-item-card:: :ref:`overview`
            .. grid-item-card:: :ref:`install`

    .. grid-item:: Examples

        .. grid:: 2

            .. grid-item-card:: :ref:`examples.diffractometer`
            .. grid-item-card:: :ref:`examples.howto`
            .. grid-item-card:: :ref:`examples.variations`
            .. grid-item-card:: :ref:`examples.tests`

    .. grid-item:: User interface

        .. grid:: 2

            .. grid-item-card:: :ref:`user`
            .. grid-item-card:: :ref:`configuration`
            .. grid-item-card:: :ref:`ready_to_use`
            .. grid-item-card:: :ref:`geometries`
            .. grid-item-card:: :ref:`constraints`
            .. grid-item-card:: :ref:`spec_commands_map`
