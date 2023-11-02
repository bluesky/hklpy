.. hklpy documentation master file

=====
hklpy
=====

Controls for using diffractometers within the `Bluesky Framework
<https://blueskyproject.io>`_.

Based on the *hkl* library
([documentation](https://people.debian.org/~picca/hkl/hkl.html),
[source](https://repo.or.cz/hkl.git)).  The source repository
on [GitHub](https://github.com/picca/hkl) may not be synchronized with the latest version from repo.or.cz.

.. ,
   with slightly cleaner abstractions
   when compared to the auto-generated gobject-introspection classes.

Integrates with ophyd pseudopositioners.

Documentation about *ophyd* and the *bluesky* framework
(https://blueskyproject.io/).

.. toctree::
   :maxdepth: 2
   :glob:
   :caption: Core Functionality

   overview
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
