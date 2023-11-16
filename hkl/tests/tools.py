"""
Common code, setups, constants, ... for these tests.

Avoids direct imports of __init__.py.
"""

import logging

import numpy

from ..util import new_lattice

logger = logging.getLogger("ophyd_session_test")

TARDIS_TEST_MODE = "lifting_detector_mu"
TWO_PI = 2 * numpy.pi


def new_sample(diffractometer, name, lattice):
    return diffractometer.calc.new_sample(name, lattice=lattice)


def sample_kryptonite(diffractometer):
    triclinic = new_lattice(4, 5, 6, 75, 85, 95)
    return new_sample(diffractometer, "kryptonite", lattice=triclinic)


def sample_silicon(diffractometer):
    from .. import SI_LATTICE_PARAMETER

    cubic = new_lattice(SI_LATTICE_PARAMETER)
    return new_sample(diffractometer, "silicon", lattice=cubic)


def sample_vibranium(diffractometer):
    a0 = TWO_PI
    cubic = new_lattice(a0)
    return new_sample(diffractometer, "vibranium", lattice=cubic)
