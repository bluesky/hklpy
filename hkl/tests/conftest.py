"""
Common structures for testing.
"""

import pytest
from ophyd import Component
from ophyd import SoftPositioner

from .. import E4CV
from .. import E6C
from .. import SimMixin
from .. import SimulatedE4CV
from .. import SimulatedE6C
from .. import SimulatedK4CV
from .. import SimulatedK6C


@pytest.fixture
def e4cv():
    """Standard E4CV."""
    diffractometer = SimulatedE4CV("", name="e4cv")
    diffractometer.wait_for_connection()
    diffractometer._update_calc_energy()
    return diffractometer


@pytest.fixture
def e4cv_renamed():
    """E4CV with renamed axes."""

    class CustomFourCircle(SimMixin, E4CV):
        """E4CV with renamed axes."""

        theta = Component(SoftPositioner, kind="hinted", init_pos=0)
        chi = Component(SoftPositioner, kind="hinted", init_pos=0)
        phi = Component(SoftPositioner, kind="hinted", init_pos=0)
        ttheta = Component(SoftPositioner, kind="hinted", init_pos=0)

    diffractometer = CustomFourCircle("", name="e4cv_renamed")
    # rename the physical axes
    diffractometer.calc.physical_axis_names = {
        # E4CV: local
        "omega": "theta",
        "chi": "chi",
        "phi": "phi",
        "tth": "ttheta",
    }
    return diffractometer


@pytest.fixture
def e6c():
    """Standard E6C."""
    diffractometer = SimulatedE6C("", name="e6cv")
    diffractometer.wait_for_connection()
    diffractometer._update_calc_energy()
    return diffractometer


@pytest.fixture
def k4cv():
    """Standard K4CV."""
    diffractometer = SimulatedK4CV("", name="k4cv")
    diffractometer.wait_for_connection()
    diffractometer._update_calc_energy()
    return diffractometer


@pytest.fixture
def k6c():
    """Standard K6C."""
    diffractometer = SimulatedK6C("", name="k6c")
    diffractometer.wait_for_connection()
    diffractometer._update_calc_energy()
    return diffractometer


@pytest.fixture
def tardis():
    class Tardis(SimMixin, E6C):
        """E6C variant at NSLS-II."""

        # theta
        theta = Component(SoftPositioner, init_pos=0)
        omega = Component(SoftPositioner, init_pos=0)
        chi = Component(SoftPositioner, init_pos=0)
        phi = Component(SoftPositioner, init_pos=0)
        # delta, gamma
        delta = Component(SoftPositioner, init_pos=0)
        gamma = Component(SoftPositioner, init_pos=0)

    diffractometer = Tardis("", name="tardis")
    diffractometer.calc.engine.mode = "lifting_detector_mu"
    # re-map Tardis' axis names onto what an E6C expects
    diffractometer.calc.physical_axis_names = {
        "mu": "theta",
        "omega": "omega",
        "chi": "chi",
        "phi": "phi",
        "gamma": "delta",
        "delta": "gamma",
    }
    diffractometer.wait_for_connection()
    return diffractometer
