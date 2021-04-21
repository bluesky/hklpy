"""
diffract
--------

Support for diffractometer instances.

DIFFRACTOMETER GEOMETRIES

.. autosummary::

    ~E4CH
    ~E4CV
    ~E6C
    ~K4CV
    ~K6C
    ~TwoC
    ~Zaxis
    ~SimulatedE4CV
    ~SimulatedE6C
    ~SimulatedK4CV
    ~SimulatedK6C

SPECIAL-USE DIFFRACTOMETER GEOMETRIES

.. autosummary::

    ~Med2p3
    ~Petra3_p09_eh2
    ~SoleilMars
    ~SoleilSiriusKappa
    ~SoleilSiriusTurret
    ~SoleilSixs
    ~SoleilSixsMed1p2
    ~SoleilSixsMed2p2

"""

from . import calc
from .diffract import Diffractometer
from ophyd import Component as Cpt
from ophyd import Device
from ophyd import PseudoSingle
from ophyd import SoftPositioner
import logging

__all__ = """
    E4CH
    E4CV
    E6C
    K4CV
    K6C
    Med2p3
    Petra3_p09_eh2
    SimMixin
    SimulatedE4CV
    SimulatedE6C
    SimulatedK4CV
    SimulatedK6C
    SoleilMars
    SoleilSiriusKappa
    SoleilSiriusTurret
    SoleilSixs
    SoleilSixsMed1p2
    SoleilSixsMed2p2
    TwoC
    Zaxis
""".split()
logger = logging.getLogger(__name__)


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
    """Used at Petra3"""

    calc_class = calc.CalcPetra3_p09_eh2


class SoleilMars(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilMars


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


class SoleilSixs(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcSoleilSixs


class Med2p3(Diffractometer):
    """Used at Soleil"""

    calc_class = calc.CalcMed2p3


class TwoC(Diffractometer):
    """Two circle geometry"""

    calc_class = calc.CalcTwoC


class Zaxis(Diffractometer):
    """Z-axis geometry"""

    calc_class = calc.CalcZaxis


class SimMixin(Device):
    """Common setup for simulated geometries."""

    h = Cpt(PseudoSingle, "")
    k = Cpt(PseudoSingle, "")
    l = Cpt(PseudoSingle, "")

    def __init__(self, *args, **kwargs):
        """
        start the SoftPositioner objects with initial values
        """
        super().__init__(*args, **kwargs)
        for axis in self.real_positioners:
            axis.move(0)


class SimulatedE4CV(SimMixin, E4CV):
    """SimulatedE4CV: Eulerian 4-circle diffractometer, vertical"""

    omega = Cpt(SoftPositioner, limits=(-180, 180))
    chi = Cpt(SoftPositioner, limits=(-180, 180))
    phi = Cpt(SoftPositioner, limits=(-180, 180))
    tth = Cpt(SoftPositioner, limits=(-180, 180))


class SimulatedE6C(SimMixin, E6C):
    """SimulatedE6C: Eulerian 6-circle diffractometer"""

    mu = Cpt(SoftPositioner, limits=(-180, 180))
    omega = Cpt(SoftPositioner, limits=(-180, 180))
    chi = Cpt(SoftPositioner, limits=(-180, 180))
    phi = Cpt(SoftPositioner, limits=(-180, 180))
    gamma = Cpt(SoftPositioner, limits=(-180, 180))
    delta = Cpt(SoftPositioner, limits=(-180, 180))


class SimulatedK4CV(SimMixin, K4CV):
    """SimulatedK4CV: Kappa 4-circle diffractometer, vertical"""

    komega = Cpt(SoftPositioner, limits=(-180, 180))
    kappa = Cpt(SoftPositioner, limits=(-180, 180))
    kphi = Cpt(SoftPositioner, limits=(-180, 180))
    tth = Cpt(SoftPositioner, limits=(-180, 180))


class SimulatedK6C(SimMixin, K6C):
    """SimulatedK6C: Kappa 6-circle diffractometer"""

    mu = Cpt(SoftPositioner, limits=(-180, 180))
    komega = Cpt(SoftPositioner, limits=(-180, 180))
    kappa = Cpt(SoftPositioner, limits=(-180, 180))
    kphi = Cpt(SoftPositioner, limits=(-180, 180))
    gamma = Cpt(SoftPositioner, limits=(-180, 180))
    delta = Cpt(SoftPositioner, limits=(-180, 180))
