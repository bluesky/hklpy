"""
:mod:`hkl` - HKL diffractometer support
=======================================

.. module:: hkl
   :synopsis:

"""

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from ._version import get_versions  # noqa: F402, E402

__version__ = get_versions()["version"]
del get_versions

# import shortcuts

from .calc import A_KEV, UnreachableError  # noqa: F401, F402, E402

from .geometries import (  # noqa: F401, F402, E402
    E4CH,
    E4CV,
    E6C,
    K4CV,
    K6C,
    Petra3_p09_eh2,
    SimMixin,
    SimulatedE4CV,
    SimulatedE6C,
    SimulatedK4CV,
    SimulatedK6C,
    SoleilMars,
    SoleilSiriusKappa,
    SoleilSiriusTurret,
    SoleilSixsMed1p2,
    SoleilSixsMed2p2,
    SoleilSixsMed2p3,
    Zaxis,
)

from .user import (  # noqa: F401, F402, E402
    cahkl,
    cahkl_table,
    calc_UB,
    change_sample,
    list_samples,
    new_sample,
    or_swap,
    pa,
    select_diffractometer,
    set_energy,
    setor,
    show_sample,
    show_selected_diffractometer,
    update_sample,
    wh,
)

from .util import (  # noqa: F401, F402, E402
    Constraint,
    diffractometer_types,
    get_position_tuple,
    Lattice,
    list_orientation_runs,
    new_detector,
    restore_constraints,
    restore_energy,
    restore_orientation,
    restore_reflections,
    restore_sample,
    restore_UB,
    run_orientation_info,
    SI_LATTICE_PARAMETER,
    software_versions,
)
