.. hklpy documentation master file

=====
hklpy
=====

Controls for using diffractometers within the `Bluesky Framework
<https://blueskyproject.io>`_.

Based on the *hkl* library (`documentation
<https://people.debian.org/~picca/hkl/hkl.html>`_, `source
<https://repo.or.cz/hkl.git>`_).  (Caution: The GitHub source `repository
<https://github.com/picca/hkl>`_ may not be synchronized with the latest version
from repo.or.cz.)

.. ,
   with slightly cleaner abstractions
   when compared to the auto-generated gobject-introspection classes.

Integrates with `ophyd <https://blueskyproject.io/ophyd>`_ pseudopositioners
for use with `bluesky <https://blueskyproject.io/bluesky>`_ plans.

.. toctree::
   :maxdepth: 2
   :glob:
   :caption: Core Functionality

   overview
   constraints
   install

.. toctree::
   :maxdepth: 2
   :glob:
   :caption: Ready-to-Use Devices

   ready_to_use
   examples/*

.. toctree::
   :maxdepth: 2
   :glob:
   :caption: Developer Notes

   api
   release_notes

Indices
-------

* :ref:`General Index <genindex>`
* :ref:`Index of Modules <modindex>`

.. note:: *hklpy* documentation built |today| for version |version|.
