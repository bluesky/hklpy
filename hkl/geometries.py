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

import logging
from . import calc
from .diffract import Diffractometer


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
