![Unit Tests](https://github.com/bluesky/hklpy/workflows/Unit%20Tests/badge.svg)
![Code Style](https://github.com/bluesky/hklpy/workflows/Code%20Style/badge.svg)
[![Code Health](https://landscape.io/github/bluesky/hklpy/main/landscape.svg?style=flat)](https://landscape.io/github/bluesky/hklpy/main)

hklpy
=====

Based on the *hkl*  library, with slightly cleaner abstractions
when compared to the auto-generated `gobject-introspection` classes.
Integrates with ophyd pseudopositioners.

**TIP**: Always import the ``gobject-introspection`` package first
and require ``Hkl`` version 5.0, as in:

```python
import gi
gi.require_version('Hkl', '5.0')

from hkl.diffract import E4CV
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
