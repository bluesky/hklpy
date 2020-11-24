Compare *hkl* trajectory with SPEC
===================================================

This example has problems.  Cannot solve the forward reflections
with *hkl* in any of the diffractometer modes.
Is it the wavelength?

Maybe need a simpler example?


Start IPython session from console:

    (bluesky_2020_9) prjemian@poof ~/.../source/examples $ ipython
    Python 3.8.2 (default, Mar 26 2020, 15:53:00) 
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.16.1 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: 

Initialize the MatPlotLib graphics:

    In [1]: %matplotlib
    Using matplotlib backend: Qt5Agg

Import support libraries:

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    import gi
    gi.require_version('Hkl', '5.0')
    from hkl.calc import CalcE6C
