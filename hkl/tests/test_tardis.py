from ophyd import Component as Cpt
from ophyd import PseudoSingle, SoftPositioner
import gi
import numpy.testing
import pytest

gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.calc import UnreachableError
from hkl.diffract import Constraint
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


@pytest.fixture(scope="function")
def constrain(tardis):
    tardis.apply_constraints(
        dict(
            theta=Constraint(-181, 181, 0, True),
            # we don't have these!! Fix to 0
            phi=Constraint(0, 0, 0, False),
            chi=Constraint(0, 0, 0, False),
            omega=Constraint(0, 0, 0, False),
            # Attention naming convention inverted at the detector stages!
            delta=Constraint(-5, 180, 0, True),
            gamma=Constraint(-5, 180, 0, True),
        )
    )


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


def test_reachable(tardis, sample, constrain):
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


def test_inversion(tardis, sample, constrain):
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


def interpret_LiveTable(data_table):
    lines = data_table.strip().splitlines()
    keys = [k.strip() for k in lines[1].split("|")[3:-1]]
    data = {k: [] for k in keys}
    for line in lines[3:-1]:
        for i, value in enumerate(line.split("|")[3:-1]):
            data[keys[i]].append(float(value))
    return data


def test_issue62(tardis, sample, constrain):
    tardis.energy_units.put("eV")
    tardis.energy.put(573)
    tardis.calc["gamma"].limits = (-2.81, 183.1)
    assert round(tardis.calc.energy, 5) == 0.573

    # this test is not necessary
    # ref = tardis.inverse(theta=41.996, omega=0, chi=0, phi=0, delta=6.410, gamma=0)
    # # FIXME: assert round(ref.h, 2) == 0.1
    # # FIXME: assert round(ref.k, 2) == 0.51
    # # FIXME: assert round(ref.l, 2) == 0.1

    # simulate the scan, computing hkl from angles
    # RE(scan([hw.det, tardis],tardis.theta, 0, 0.3, tardis.delta,0,0.5, num=5))
    # values as reported from LiveTable
    with open("livedata_issue62.txt", "r") as fp:
        livedata = fp.read()
    run_data = interpret_LiveTable(livedata)
    # TODO: can this tolerance be made much smaller (was 0.05)?  < 0.01?  How?
    tolerance = 0.055  # empirical

    # test inverse() on each row in the table
    for i in range(len(run_data["tardis_theta"])):
        ref = tardis.inverse(
            theta=run_data["tardis_theta"][i],
            omega=0,
            chi=0,
            phi=0,
            delta=run_data["tardis_delta"][i],
            gamma=run_data["tardis_gamma"][i],
        )
        assert abs(ref.h - run_data["tardis_h"][i]) <= tolerance
        assert abs(ref.k - run_data["tardis_k"][i]) <= tolerance
        assert abs(ref.l - run_data["tardis_l"][i]) <= tolerance
