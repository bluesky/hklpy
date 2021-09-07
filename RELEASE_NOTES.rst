===============
Release History
===============

.. subsections could include these headings (in this order)

    Breaking Changes
    New Features and/or Enhancements
    Fixes
    Maintenance
    Deprecations
    Contributors

v1.0.0 (by 2021-09-30)
======================

First production release.

..
  Consult the 1.0.0 milestone [#]_ on GitHub for an expected
  release date.

  .. [#] https://github.com/bluesky/hklpy/milestone/5

Breaking Changes
----------------

* Python 3.6 no longer supported.
* ``Constraint`` moved from ``hkl.diffract`` to ``hkl.util``
* Wavelength now saved with each reflection
* Wavelength and lattice parameters in Angstroms now
* ``TwoC`` geometry removed since no calculation engines are defined for it in _libhkl_
* ``SOLEIL_SIXS`` geometry removed since it is not described in _libhkl_
* ``MED2+3`` renamed to ``SOLEIL SIXS MED2+3``
* Conda package is built for ``linux-64`` only  due to _libhkl_ requirement

New Features and/or Enhancements
--------------------------------

* Conda package available on conda-forge: ``conda install -c conda-forge hklpy``
* Import any diffractometer from top level ``hkl`` (not from ``hkl.diffract``):  ``from hkl import E4CV``
* Support save and restore of **UB** matrix
* Can swap the order of the two crystal orientation reflections.
* Constant: ``hkl.SI_LATTICE_PARAMETER``
* How-To guides
  * add extra axes to a diffractometer
  * rename physical axes of a diffractometer
  * use additional diffractometer parameters
  * use the Q calculation engine of E4CV
* Specify calculation engine when creating a diffractometer.
* Simplified user interface when working with one diffractometer.
* Versions of component software packages now available.

Maintenance
-----------

* Clarify 6-circle geometries with drawings & labels
* Table of all defined diffractometers and their supported engines
* Show the value used by kappa geometry angle $\alpha$ (50 degrees)
* Show how wavelength and other reflection information are held in _libhkl_

Contributors
------------

* Andi Barbour, NSLS-II
* Jennifer Bui, (NSLS-II) Brown Univ.
* Thomas Caswell, NSLS-II
* Yongseong Choi, APS
* Gilberto Fabbris, APS
* Jong Woo Kim, APS
* Katherine Perez, (NSLS-II) LSU
* Fanny Rodolakis, APS
* Jorg Strempfer, APS
* Andrew Walter, NSLS-II
* Stuart Wilkins, NSLS-II

v0.3.16 (2021-04-28)
================================

Full list of changes is on the `wiki v0.3.16
<https://github.com/bluesky/hklpy/wiki/release-notes-v0.3.16>`_.

Breaking Changes
----------------

* Diffractometer geometries have moved from ``hkl.diffract`` to (the new) ``hkl.geometries``, such as ``hkl.geometries.E4CV``.

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
