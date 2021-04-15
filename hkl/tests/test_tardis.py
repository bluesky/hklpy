from ophyd import Component as Cpt
from ophyd import PseudoSingle, SoftPositioner
import gi
import numpy.testing
import pytest

gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.calc import UnreachableError
from hkl.geometries import E6C
from hkl.util import Lattice


def setup_module(module):
    pass


class Tardis(E6C):
    h = Cpt(PseudoSingle, "")
    k = Cpt(PseudoSingle, "")
    l = Cpt(PseudoSingle, "")

    # theta
    theta = Cpt(SoftPositioner)
    omega = Cpt(SoftPositioner)
    chi = Cpt(SoftPositioner)
    phi = Cpt(SoftPositioner)
    # delta, gamma
    delta = Cpt(SoftPositioner)
    gamma = Cpt(SoftPositioner)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for p in self.real_positioners:
            p._set_position(0)  # give each a starting position


@pytest.fixture(scope="function")
def tardis():
    tardis = Tardis("", name="tardis")
    tardis.calc.engine.mode = "lifting_detector_mu"
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


@pytest.fixture(scope="function")
def sample(tardis):
    # lengths must have same units as wavelength
    # angles are in degrees
    lattice = Lattice(a=0.5857, b=0.5857, c=0.7849, alpha=90.0, beta=90.0, gamma=90.0)

    # add the sample to the calculation engine
    tardis.calc.new_sample("KCF", lattice=lattice)

    # We can alternatively set the wavelength
    # (or photon energy) on the Tardis.calc instance.
    p1 = tardis.calc.Position(
        # fmt: off
        theta=48.42718305024724,
        omega=0.0,
        chi=0.0,
        phi=0.0,
        delta=115.65436271083637,
        gamma=3.0000034909999993,
        # fmt: on
    )
    r1 = tardis.calc.sample.add_reflection(0, 0, 1, position=p1)

    p2 = tardis.calc.Position(
        # fmt: off
        theta=138.42718305024724,
        omega=0.0,
        chi=0.0,
        phi=0.0,
        delta=115.65436271083637,
        gamma=3.0000034909999993,
        # fmt: on
    )
    r2 = tardis.calc.sample.add_reflection(1, 1, 0, position=p2)
    tardis.calc.sample.compute_UB(r1, r2)

    # note: orientation matrix (below) was pre-computed with this wavelength
    # wavelength units must match lattice unit cell length units
    tardis.calc.wavelength = 1.3317314715359827
    print("calc.wavelength is", tardis.calc.wavelength)
    print("sample is", tardis.calc.sample)
    print("position is", tardis.position)

    print("sample name is", tardis.sample_name.get())
    print("u matrix is", tardis.U.get(), tardis.U.describe())
    print("ub matrix is", tardis.UB.get(), tardis.UB.describe())
    print(
        # fmt: off
        "reflections:",
        tardis.reflections.get(),
        tardis.reflections.describe(),
        # fmt: on
    )
    print("ux is", tardis.ux.get(), tardis.ux.describe())
    print("uy is", tardis.uy.get(), tardis.uy.describe())
    print("uz is", tardis.uz.get(), tardis.uz.describe())
    print("lattice is", tardis.lattice.get(), tardis.lattice.describe())
    print(tardis.read())
    return sample


def constrain(tardis):
    calc = tardis.calc
    # apply some constraints
    calc["theta"].limits = (-181, 181)
    calc["theta"].value = 0
    calc["theta"].fit = True

    # we don't have it. Fix to 0
    calc["phi"].limits = (0, 0)
    calc["phi"].value = 0
    calc["phi"].fit = False

    # we don't have it. Fix to 0
    calc["chi"].limits = (0, 0)
    calc["chi"].value = 0
    calc["chi"].fit = False

    # we don't have it!! Fix to 0
    calc["omega"].limits = (0, 0)
    calc["omega"].value = 0
    calc["omega"].fit = False

    # Attention naming convention inverted at the detector stages!
    # delta
    calc["delta"].limits = (-5, 180)
    calc["delta"].value = 0
    calc["delta"].fit = True

    # gamma
    calc["gamma"].limits = (-5, 180)
    calc["gamma"].value = 0
    calc["gamma"].fit = True


def test_params(tardis):
    """
    Make sure the parameters are set correctly
    """
    calc = tardis.calc
    # gamma
    calc["gamma"].limits = (-5, 180)
    calc["gamma"].value = 10
    calc["gamma"].fit = False

    assert calc["gamma"].limits == (-5, 180)
    assert calc["gamma"].value == 10
    assert calc["gamma"].fit is False

    # try another random set of parameters
    # in case it was initialized to the parameters we "set"
    calc["gamma"].limits = (-10, 180)
    calc["gamma"].value = 20
    calc["gamma"].fit = True

    assert calc["gamma"].limits == (-10, 180)
    assert calc["gamma"].value == 20
    assert calc["gamma"].fit is True


def test_reachable(tardis, sample):
    constrain(tardis)
    ppos = (0, 0, 1.1)
    rpos = (
        101.56806493825435,
        0.0,
        0.0,
        0.0,
        42.02226419522791,
        176.69158155966787,
    )

    tardis.move(ppos)
    print("tardis position is", tardis.position)
    print("tardis position is", tardis.calc.physical_positions)
    numpy.testing.assert_almost_equal(tardis.position, ppos)
    numpy.testing.assert_almost_equal(tardis.calc.physical_positions, rpos)


def test_inversion(tardis, sample):
    constrain(tardis)
    ppos = (0, 0, 1.1)
    rpos = (
        101.56806493825435,
        0.0,
        0.0,
        0.0,
        42.02226419522791,
        # invert gamma for this test:
        -176.69158155966787,
    )

    tardis.calc.inverted_axes = ["gamma"]
    tardis.calc.physical_positions = rpos

    assert not tardis.calc["omega"].inverted
    gamma = tardis.calc["gamma"]
    assert gamma.inverted
    numpy.testing.assert_almost_equal(gamma.limits, (-180.0, 5.0))  # inverted from (-5, 180)
    gamma.limits = (-180.0, 5.0)
    numpy.testing.assert_almost_equal(gamma.limits, (-180.0, 5.0))  # inverted from (-5, 180)

    numpy.testing.assert_almost_equal(tardis.calc.physical_positions, rpos)
    numpy.testing.assert_almost_equal(tardis.calc.inverse(rpos), ppos)


def test_unreachable(tardis, sample):
    print("position is", tardis.position)
    with pytest.raises(UnreachableError) as exinfo:
        tardis.move((0, 0, 1.8))

    ex = exinfo.value
    print("grabbing last valid position", ex.pseudo, ex.physical)
    print("tardis position is", tardis.position)
    print("tardis position is", tardis.calc.physical_positions)

    # it should not have moved:
    numpy.testing.assert_almost_equal(tardis.position, (0, 0, 0))
    numpy.testing.assert_almost_equal(tardis.calc.physical_positions, [0] * 6)
