===============
Release History
===============

.. subsections could include these headings (in this order)

    Breaking Changes
    New Features and/or Enhancements
    Fixes
    Maintenance
    Deprecations

v1.0.0 (tba)
============

Consult the 1.0.0 milestone [#]_ on GitHub for an expected
release date.

.. [#] https://github.com/bluesky/hklpy/milestone/5

v0.3.16 (2021-04-28)
================================

Full list of changes is on the `wiki v0.3.16
<https://github.com/bluesky/hklpy/wiki/release-notes-v0.3.16>`_.

New Features and/or Enhancements
--------------------------------

* Diffractometer additions from apstools

  - simple user interface for a diffractometer
  - constraints

* Create simulators for common geometries.

  - ``hkl.geometries.SimMixin`` for simulators.

* ``compute_UB()`` now returns the **UB** matrix or ``None`` (previously returned 1 or 0)

Fixes
-----

* Ensure that diffractometer energy is read-only (and not modified) by changes in units or energy offset.
* Diffractometer responds to energy, energy units, and energy offset PV updates now.

Maintenance
-----------

* separate diffractometer geometry instances from base class
* refer to the hkl C++ library code as **libhkl**
* add Python 3.9 to unit test suite
* now can use Python f-strings
* re-arrange documentation structure
* define ``__all__`` in modules

v0.3.15 (2020-12-20)
====================

Full list of changes is on the `wiki v0.3.15
<https://github.com/bluesky/hklpy/wiki/release-notes-v0.3.15>`_.

Breaking Changes
----------------

* Diffractometer wavelength **must** use *angstrom* units to match the
  lattice constants.  Previously, wavelength was stated to be in
  ``nm``. Instruments upgrading to this release should verify the units
  actually in use.

New Features and/or Enhancements
--------------------------------

* Diffractometer energy units can be specified.  Unit conversions
  are handled by the *pint* [#]_ package.

* Examples of E4CV, K4CV, and E6C diffractometer geometries.
* Comparison of UB matrix calculation with SPEC data.
* Source code documentation in `hkl.diffract`.
* Show how to connect energy from local controls.

.. [#] *pint*: https://pint.readthedocs.io/en/stable/

Fixes
-----

* Limits-checking for *hkl* values now coordinated with upstream
  ``bluesky`` code.

Maintenance
-----------

* Move continuous integration processes to GitHub Actions.
* Documentation now published with other bluesky packages:
  https://blueskyproject.io/hklpy/

Deprecations
------------

* All the previous examples have been archived and will be
  removed for the 1.0.0 release.

v0.3.14 (2020-09-28)
====================
