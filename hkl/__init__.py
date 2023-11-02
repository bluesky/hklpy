"""
:mod:`hkl` - HKL diffractometer support
=======================================

.. module:: hkl
   :synopsis:

"""

# flake8: noqa

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)
    del get_version
except (LookupError, ModuleNotFoundError):
    from importlib.metadata import version

    __version__ = version("pkgdemo")
    del version

# gobject-introspection, to access libhkl
import gi

gi.require_version("Hkl", "5.0")

# import shortcuts

from .calc import A_KEV  # noqa: F401, F402, E402
from .calc import UnreachableError  # noqa: F401, F402, E402
from .configuration import DiffractometerConfiguration  # noqa: F401, F402, E402
from .geometries import E4CH  # noqa: F401, F402, E402
from .geometries import E4CV
from .geometries import E6C
from .geometries import K4CV
from .geometries import K6C
from .geometries import Petra3_p09_eh2
from .geometries import Petra3_p23_4c
from .geometries import Petra3_p23_6c
from .geometries import SimMixin
from .geometries import SimulatedE4CV
from .geometries import SimulatedE6C
from .geometries import SimulatedK4CV
from .geometries import SimulatedK6C
from .geometries import SoleilMars
from .geometries import SoleilNanoscopiumRobot
from .geometries import SoleilSiriusKappa
from .geometries import SoleilSiriusTurret
from .geometries import SoleilSixsMed1p2
from .geometries import SoleilSixsMed2p2
from .geometries import SoleilSixsMed2p3
from .geometries import SoleilSixsMed2p3v2
from .geometries import Zaxis
from .user import cahkl  # noqa: F401, F402, E402
from .user import cahkl_table
from .user import calc_UB
from .user import change_sample
from .user import list_samples
from .user import new_sample
from .user import or_swap
from .user import pa
from .user import select_diffractometer
from .user import set_energy
from .user import setor
from .user import show_sample
from .user import show_selected_diffractometer
from .user import update_sample
from .user import wh
from .util import SI_LATTICE_PARAMETER  # noqa: F401, F402, E402
from .util import Constraint
from .util import Lattice
from .util import diffractometer_types
from .util import get_position_tuple
from .util import list_orientation_runs
from .util import new_detector
from .util import new_lattice
from .util import restore_constraints
from .util import restore_energy
from .util import restore_orientation
from .util import restore_reflections
from .util import restore_sample
from .util import restore_UB
from .util import run_orientation_info
from .util import software_versions
