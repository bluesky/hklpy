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

v2.0.0 (expected 2024)
======================================

User-requested changes

v1.1.0 (expected 2023-12)
======================================

Add new geometries from upstream *libhkl*.

New Features and/or Enhancements
--------------------------------

* Add ``DiffractometerConfiguration`` to export & restore configuration and orientation.
* Add ``Petra3_p23_4c`` diffractometer geometry.
* Add ``Petra3_p23_6c`` diffractometer geometry.
* Add ``SoleilNanoscopiumRobot`` diffractometer geometry.
* Add ``SoleilSixsMed2p3v2`` diffractometer geometry.
* Export and restore diffractometer configuration as JSON string, YAML string, Python dictionary, or file.
* Add ``user.current_diffractometer()`` function.
* Add ``axes_r``, ``axes_w``, & ``axes_c`` properties to both ``calc`` & ``engine``.
* Build tables of diffractometer geometry, engines, and modes from *libhkl* API.
* Export and reload diffractometer configuration as JSON string, YAML string, or Python dictionary.

Fixes
-----

* ``diffract.forward()`` should pick solution consistent with ``diffract.forward_solution_table()``, if it can. Otherwise, fall back to previous iterative method.
* Make ``util.list_orientation_runs()`` work with databroker v1.2 or v2+.
* Make ``util.run_orientation_info()`` work with databroker v1.2 or v2+.
* Resolved under-reported problems in CI unit tests.
* ``util.restore_reflections()`` use renamed motor axes if so defined.

Maintenance
-----------

* Add pre-commit checks.
* Add ``apischema`` to package requirements.
* Add test for ``or_swap()``.
* Change documentation theme to pydata-sphinx-theme.
* Documentation ZIP file uploaded as artifact with each build.  Great for review!
* Expand testing to to Py3.8 - Py3.11.
* Fix code in ``util.restore_reflections()`` that failed unit tests locally.
* Make it easier to find the SPEC command cross-reference table.
* Update packaging to latest PyPA recommendations.
* Validate user input to sample.add_reflection().

Deprecations
------------

* Deprecate the ``fit`` parameter in diffractometer constraints.

v1.0.4 (released 2023-10-06)
======================================

Maintenance release.

Fixes
-----

* ``util.run_orientation_info()`` failed when no primary stream present.
* Broken link in documentation.

Maintenance
-----------

* Move table with SPEC commands cross-reference to a HOWTO document.
* ``util.list_orientation_runs()`` added progress bar.
* Support Py3.8, 3.9, 3.10, & 3.11
* Support libhkl v5.0.0.3001 (& v5.0.0.3357 when ready)

v1.0.3 (released 2022-06-22)
======================================

Maintenance release.

Maintenance
-----------

* Publish to PyPI from GitHub Actions workflow.
* Enable installation by pip.
* Update the conda environment.
* Show how to install *hklpy*.
* Revise how Jupyter notebook examples are published.

v1.0.2 (2022-06-14)
===================

Maintenance release.

Maintenance
-----------

* No longer need to ``import gi; gi.require_version('Hkl', '5.0')`` first.
  Just ``import hkl`` and the other steps will be done by the package.

v1.0.1 (2021-09-20)
===================

Maintenance release.

Maintenance
-----------

* Increase precision of ``A_KEV`` constant to match 2018 CODATA value.
* Document the ``max_forward_iterations`` attribute.
* Provide project description for PyPI packaging.

Contributors
------------

* Andi Barbour, NSLS-II

v1.0.0 (2021-09-13)
===================

First production release.

.. https://github.com/bluesky/hklpy/milestone/5

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
====================

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
