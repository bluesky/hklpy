[![Circle CI](https://circleci.com/gh/NSLS-II/hklpy.svg?style=svg)](https://circleci.com/gh/NSLS-II/hklpy)

[![Code Health](https://landscape.io/github/NSLS-II/hklpy/master/landscape.svg?style=flat)](https://landscape.io/github/NSLS-II/hklpy/master)

hklpy
=====

Based on the *hkl*  library, with slightly cleaner abstractions
when compared to the auto-generated `gobject-introspection` classes.

NOTE: main repository: https://repo.or.cz/hkl.git (GitHub repo
https://github.com/picca/hkl is a shadow copy that may not be
synchronized with the latest version from repo.or.cz)

Integrates with ophyd pseudopositioners.

[Documentation](https://blueskyproject.io/) about the bluesky framework.
No documentation for *hklpy* exists at this time.

Always import the ``gobject-introspection`` package first
and require ``Hkl`` version 5.0, as in:

```python
import gi
gi.require_version('Hkl', '5.0')

from hkl.diffract import E4CV
```


## Conda Recipes

Install the most recent build: `conda install hklpy -c nsls2forge`

Find the tagged recipe [here](https://github.com/NSLS-II/lightsource2-recipes/tree/master/recipes-tag/hklpy) and the dev recipe [here](https://github.com/NSLS-II/lightsource2-recipes/tree/master/recipes-dev/hklpy)
