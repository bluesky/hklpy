"""
Common structures for testing.
"""

import numpy
import pytest
from ophyd import Component
from ophyd import SoftPositioner

from .. import E4CV
from .. import E6C
from .. import SimMixin
from .. import SimulatedE4CV
from .. import SimulatedE6C
from .. import SimulatedK4CV


TARDIS_TEST_MODE = "lifting_detector_mu"


@pytest.fixture
def e4cv():
    e4cv = SimulatedE4CV("", name="e4cv")
    e4cv.wait_for_connection()
    e4cv._update_calc_energy()
    return e4cv


@pytest.fixture
def e4cv_renamed():
    class CustomFourCircle(SimMixin, E4CV):
        theta = Component(SoftPositioner, kind="hinted", init_pos=0)
        chi = Component(SoftPositioner, kind="hinted", init_pos=0)
        phi = Component(SoftPositioner, kind="hinted", init_pos=0)
        ttheta = Component(SoftPositioner, kind="hinted", init_pos=0)

    e4cv_renamed = CustomFourCircle("", name="e4cv_renamed")
    # rename the physical axes
    e4cv_renamed.calc.physical_axis_names = {
        # E4CV: local
        "omega": "theta",
        "chi": "chi",
        "phi": "phi",
        "tth": "ttheta",
    }
    return e4cv_renamed


@pytest.fixture
def e6cv():
    e6cv = SimulatedE6C("", name="e6cv")
    e6cv.wait_for_connection()
    e6cv._update_calc_energy()
    return e6cv


@pytest.fixture
def k4cv():
    ke4cv = SimulatedK4CV("", name="k4cv")
    ke4cv.wait_for_connection()
    ke4cv._update_calc_energy()
    return ke4cv


@pytest.fixture
def tardis():
    class Tardis(SimMixin, E6C):
        # theta
        theta = Component(SoftPositioner, init_pos=0)
        omega = Component(SoftPositioner, init_pos=0)
        chi = Component(SoftPositioner, init_pos=0)
        phi = Component(SoftPositioner, init_pos=0)
        # delta, gamma
        delta = Component(SoftPositioner, init_pos=0)
        gamma = Component(SoftPositioner, init_pos=0)

    tardis = Tardis("", name="tardis")
    tardis.calc.engine.mode = TARDIS_TEST_MODE
    # re-map Tardis' axis names onto what an E6C expects
    tardis.calc.physical_axis_names = {
        "mu": "theta",
        "omega": "omega",
        "chi": "chi",
        "phi": "phi",
        "gamma": "delta",
        "delta": "gamma",
    }
    tardis.wait_for_connection()
    return tardis


def new_sample(diffractometer, name, lattice):
    diffractometer.calc.new_sample(name, lattice=lattice)


def sample_kryptonite(diffractometer):
    triclinic = (4, 5, 6, 75, 85, 95)
    new_sample(diffractometer, "kryptonite", lattice=triclinic)


def sample_silicon(diffractometer):
    from .. import SI_LATTICE_PARAMETER

    a0 = SI_LATTICE_PARAMETER
    cubic = (a0, a0, a0, 90, 90, 90)
    new_sample(diffractometer, "silicon", lattice=cubic)


def sample_vibranium(diffractometer):
    a0 = 2 * numpy.pi
    cubic = (a0, a0, a0, 90, 90, 90)
    new_sample(diffractometer, "vibranium", lattice=cubic)
