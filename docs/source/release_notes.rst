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

v0.3.15 (2020-12-21)
====================

Breaking Changes
----------------

* Diffractometer wavelength **must** use *angstrom* units to match the
  lattice constants.  Previously, wavelength was stated to be in
  `nm`. Instruments upgrading to this release should verify the units
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
