"""
diffract
--------

Support for diffractometer instances.

SUPPORT

.. autosummary::

    ~SimMixin

DIFFRACTOMETER GEOMETRIES

.. autosummary::

    ~E4CH
    ~E4CV
    ~E6C
    ~K4CV
    ~K6C
    ~Zaxis
    ~SimulatedE4CV
    ~SimulatedE6C
    ~SimulatedK4CV
    ~SimulatedK6C

SPECIAL-USE DIFFRACTOMETER GEOMETRIES

.. autosummary::

    ~ApsPolar
    ~Petra3_p09_eh2
    ~Petra3_p23_4c
    ~Petra3_p23_6c
    ~SoleilMars
    ~SoleilNanoscopiumRobot
    ~SoleilSiriusKappa
    ~SoleilSiriusTurret
    ~SoleilSixsMed1p2
    ~SoleilSixsMed2p2
    ~SoleilSixsMed2p3
    ~SoleilSixsMed2p3v2

"""

import logging

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import PseudoSingle
from ophyd import SoftPositioner

from . import calc
from .diffract import Diffractometer

__all__ = """
    ApsPolar
    E4CH
    E4CV
    E6C
    K4CV
    K6C
    Petra3_p09_eh2
    Petra3_p23_4c
    Petra3_p23_6c
    SimMixin
    SimulatedE4CV
    SimulatedE6C
    SimulatedK4CV
    SimulatedK6C
    SoleilMars
    SoleilNanoscopiumRobot
    SoleilSiriusKappa
    SoleilSiriusTurret
    SoleilSixsMed1p2
    SoleilSixsMed2p2
    SoleilSixsMed2p3
    SoleilSixsMed2p3v2
    Zaxis
""".split()
logger = logging.getLogger(__name__)


class ApsPolar(Diffractometer):
    """APS POLAR 6-circle diffractometer."""

    calc_class = calc.CalcApsPolar


class E4CH(Diffractometer):
    """Eulerian 4-circle, horizontal scattering plane"""

    calc_class = calc.CalcE4CH


class E4CV(Diffractometer):
    """Eulerian 4-circle, vertical scattering plane"""

    calc_class = calc.CalcE4CV


class E6C(Diffractometer):
    """Eulerian 6-circle, vertical scattering plane"""

    calc_class = calc.CalcE6C


class K4CV(Diffractometer):
    """Kappa 4-circle, vertical scattering plane"""

    calc_class = calc.CalcK4CV


class K6C(Diffractometer):
    """Kappa 6-circle, vertical scattering plane"""

    calc_class = calc.CalcK6C


class Petra3_p09_eh2(Diffractometer):
    """6-circle Used at Petra3 P09"""

    calc_class = calc.CalcPetra3_p09_eh2


class Petra3_p23_4c(Diffractometer):
    """4-circle Used at Petra3 P23"""

    calc_class = calc.CalcPetra3_p23_4c


class Petra3_p23_6c(Diffractometer):
    """7-circle Used at Petra3 P23"""

    calc_class = calc.CalcPetra3_p23_6c


class SoleilMars(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilMars


class SoleilNanoscopiumRobot(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilNanoscopiumRobot


class SoleilSiriusKappa(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilSiriusKappa


class SoleilSiriusTurret(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilSiriusTurret


class SoleilSixsMed1p2(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilSixsMed1p2


class SoleilSixsMed2p2(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilSixsMed2p2


class SoleilSixsMed2p3(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilSixsMed2p3


class SoleilSixsMed2p3v2(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilSixsMed2p3v2


class Zaxis(Diffractometer):
    """Z-axis geometry"""

    calc_class = calc.CalcZaxis


class SimMixin(Device):
    """
    Defines `h`, `k`, & `l` pseudo-positioners.

    Use this mixin class with any of the diffractometer geometries to create
    your own simulator.  Follow one of the simulators below, such as
    :class:`~hkl.geometries.SimulatedE4CV`.  You should replace ``E4CV`` with
    your geomtry's name.  And, you will need to create SoftPositioner components
    for each of the real-space axes, in the order required by that geometry.
    """

    h = Cpt(PseudoSingle, "", kind="hinted")
    k = Cpt(PseudoSingle, "", kind="hinted")
    l = Cpt(PseudoSingle, "", kind="hinted")


class SimulatedE4CV(SimMixin, E4CV):
    """SimulatedE4CV: Eulerian 4-circle diffractometer, vertical"""

    omega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    tth = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")


class SimulatedE6C(SimMixin, E6C):
    """SimulatedE6C: Eulerian 6-circle diffractometer"""

    mu = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    omega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    chi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    phi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    gamma = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    delta = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")


class SimulatedK4CV(SimMixin, K4CV):
    """SimulatedK4CV: Kappa 4-circle diffractometer, vertical"""

    komega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    kappa = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    kphi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    tth = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")


class SimulatedK6C(SimMixin, K6C):
    """SimulatedK6C: Kappa 6-circle diffractometer"""

    mu = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    komega = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    kappa = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    kphi = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    gamma = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
    delta = Cpt(SoftPositioner, limits=(-180, 180), init_pos=0, kind="normal")
