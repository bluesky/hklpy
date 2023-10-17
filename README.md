hklpy
=====

| Name | Downloads | Version | Platforms | PyPI |
| --- | --- | --- | --- | --- |
| [![Conda Package](https://img.shields.io/badge/package-hklpy-green.svg)](https://anaconda.org/conda-forge/hklpy) | [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/hklpy.svg)](https://anaconda.org/conda-forge/hklpy) | [![Conda Version](https://img.shields.io/conda/vn/conda-forge/hklpy.svg)](https://anaconda.org/conda-forge/hklpy) | [![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/hklpy.svg)](https://anaconda.org/conda-forge/hklpy) | [![PyPi](https://img.shields.io/pypi/v/hklpy.svg)](https://pypi.python.org/pypi/hklpy) |

Controls for using diffractometers within the [Bluesky
Framework](https://blueskyproject.io).

Based on the *hkl*  C library (described here as [*libhkl*](https://people.debian.org/~picca/hkl/hkl.html#)), with
slightly cleaner abstractions when compared to the auto-generated
`gobject-introspection` classes. Integrates with ophyd
pseudopositioners.

## References

- hklpy documentation: <https://blueskyproject.io/hklpy>
- *libhkl* main repository: <https://repo.or.cz/hkl.git>
  - ([GitHub repo](https://github.com/picca/hkl) is a shadow copy rarely
    synchronized with the main repository.)
- Bluesky framework documentation: <https://blueskyproject.io>

## Conda Recipes

Install the most recent build: `conda install hklpy -c conda-forge`

The recipes for *libhkl* (`hkl`) and `hklpy` are available in the following
conda-forge feedstocks:

- <https://github.com/conda-forge/hkl-feedstock>
- <https://github.com/conda-forge/hklpy-feedstock>
