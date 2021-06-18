| Name | Downloads | Version | Platforms | Testing |
| --- | --- | --- | --- | --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-hklpy-green.svg)](https://anaconda.org/nsls2forge/hklpy) | [![Conda Downloads](https://img.shields.io/conda/dn/nsls2forge/hklpy.svg)](https://anaconda.org/nsls2forge/hklpy) | [![Conda Version](https://img.shields.io/conda/vn/nsls2forge/hklpy.svg)](https://anaconda.org/nsls2forge/hklpy) | [![Conda Platforms](https://img.shields.io/conda/pn/nsls2forge/hklpy.svg)](https://anaconda.org/nsls2forge/hklpy) | [![Build Status](https://img.shields.io/github/workflow/status/bluesky/hklpy/Unit%20Tests)](https://github.com/bluesky/hklpy/actions?query=workflow%3A%22Unit+Tests%22+branch%3Amain) |

hklpy
=====

Controls for using diffractometers within the [Bluesky
Framework](https://blueskyproject.io).

Based on the *hkl*  C++ library (described here as [*libhkl*](https://people.debian.org/~picca/hkl/hkl.html#)), with
slightly cleaner abstractions when compared to the auto-generated
`gobject-introspection` classes. Integrates with ophyd
pseudopositioners.

**TIP**: Always import the ``gobject-introspection`` package first
and require ``Hkl`` version 5.0, as in:

```python
import gi
gi.require_version('Hkl', '5.0')

from hkl import E4CV
# note: before v1.0 release use:
# from hkl.geometries import E4CV
```

**NOTE**: main repository: https://repo.or.cz/hkl.git (GitHub repo
https://github.com/picca/hkl is a shadow copy that may not be
synchronized with the latest version from repo.or.cz)

**NOTE**: hklpy documentation: https://blueskyproject.io/hklpy

**NOTE**: Bluesky framework documentation: https://blueskyproject.io

## Conda Recipes

Install the most recent build: `conda install hklpy -c nsls2forge`

The recipes for `hkl` and `hklpy` are available in the following feedstocks:
- https://github.com/nsls-ii-forge/hkl-feedstock
- https://github.com/nsls-ii-forge/hklpy-feedstock
