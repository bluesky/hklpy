.. hklpy documentation master file

hklpy
=====

Diffractometer computation library with
ophyd pseudopositioner support.

Based on the *hkl* library (https://repo.or.cz/hkl.git,
also https://github.com/picca/hkl but that repository
may not be synchronized with the latest version from repo.or.cz).
Documentation for *hkl* is here:
https://people.debian.org/~picca/hkl/hkl.html

.. ,
   with slightly cleaner abstractions
   when compared to the auto-generated gobject-introspection classes.

Integrates with ophyd pseudopositioners.

Documentation about *ophyd* and the *bluesky* framework
(https://blueskyproject.io/).

Always import the ``gobject-introspection`` package first
and require ``Hkl`` version 5.0, as in::

   import gi
   gi.require_version('Hkl', '5.0')

   from hkl.diffract import E4CV

Contents:

.. toctree::
   :maxdepth: 1
   :glob:

   calc
   context
   diffract
   engine
   geometries
   sample
   util
   examples/*
   release_notes
