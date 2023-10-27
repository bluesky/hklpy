import epics
import logging
from ..util import new_lattice
import numpy


logger = logging.getLogger("ophyd_session_test")

TARDIS_TEST_MODE = "lifting_detector_mu"


def new_sample(diffractometer, name, lattice):
    diffractometer.calc.new_sample(name, lattice=lattice)


def sample_kryptonite(diffractometer):
    triclinic = new_lattice(4, 5, 6, 75, 85, 95)
    new_sample(diffractometer, "kryptonite", lattice=triclinic)


def sample_silicon(diffractometer):
    from .. import SI_LATTICE_PARAMETER

    cubic = new_lattice(SI_LATTICE_PARAMETER)
    new_sample(diffractometer, "silicon", lattice=cubic)


def sample_vibranium(diffractometer):
    a0 = 2 * numpy.pi
    cubic = new_lattice(a0)
    new_sample(diffractometer, "vibranium", lattice=cubic)
