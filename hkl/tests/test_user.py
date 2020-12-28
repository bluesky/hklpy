import pytest
import numpy.testing

from ophyd import Component as Cpt
from ophyd import PseudoSingle, SoftPositioner

import gi

gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.diffract import E4CV
import hkl.user


class Fourc(E4CV):
    h = Cpt(PseudoSingle, "")
    k = Cpt(PseudoSingle, "")
    l = Cpt(PseudoSingle, "")

    omega = Cpt(SoftPositioner)
    chi = Cpt(SoftPositioner)
    phi = Cpt(SoftPositioner)
    tth = Cpt(SoftPositioner)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for p in self.real_positioners:
            p._set_position(0)  # give each a starting position


@pytest.fixture(scope="function")
def fourc():
    fourc = Fourc("", name="fourc")
    fourc.wait_for_connection()
    fourc._update_calc_energy()
    return fourc


def test_select_diffractometer(capsys, fourc):
    # This assertion requires this test function be first.
    assert hkl.user._geom_ is None
    hkl.user.selectDiffractometer(fourc)
    assert hkl.user._geom_ is not None
    assert hkl.user._geom_ == fourc
    capsys.readouterr()  # flush the output buffers

    hkl.user.showSelectedDiffractometer()
    out, err = capsys.readouterr()
    assert str(err) == ""
    assert str(out).strip() == "fourc"


def test_cahkl(fourc):
    hkl.user.selectDiffractometer(fourc)

    # use the default "main" sample and UB matrix
    response = hkl.user.cahkl(1, 0, 0)
    expected = (-30, 0, -90, -60)
    assert round(response[0]) == expected[0]
    assert round(response[1]) == expected[1]
    assert round(response[2]) == expected[2]
    assert round(response[3]) == expected[3]


def test_cahkl_table(capsys, fourc):
    hkl.user.selectDiffractometer(fourc)

    # use the default "main" sample and UB matrix
    rlist = [(1, 0, 0), (0, 1, 0)]
    hkl.user.cahkl_table(rlist, digits=0)
    out, err = capsys.readouterr()
    expected = """
    ========= ======== ===== === === ===
    (hkl)     solution omega chi phi tth
    ========= ======== ===== === === ===
    (1, 0, 0) 0        -30   0   -90 -60
    (0, 1, 0) 0        -30   -90 0   -60
    ========= ======== ===== === === ===
    """.strip().splitlines()
    assert err == ""
    for el, rl in list(
        zip(expected[3:5], str(out).strip().splitlines()[3:5])
    ):
        # just compare the position values
        for e, r in list(zip(el.split()[-4:], rl.split()[-4:])):
            assert float(r) == float(e)


def test_calcUB(fourc):
    hkl.user.selectDiffractometer(fourc)
    a0 = 5.4310196
    hkl.user.newSample("silicon standard", a0, a0, a0, 90, 90, 90)
    r1 = hkl.user.setor(4, 0, 0, -145.451, 0, 0, 69.0966, wavelength=1.54)
    fourc.omega.move(-145.451)
    fourc.chi.move(90)
    fourc.phi.move(0)
    fourc.tth.move(69.0966)
    r2 = hkl.user.setor(0, 4, 0)

    ub = hkl.user.calcUB(r1, r2)
    if ub is None:
        # TODO: PR #85 will make this happen
        hkl.user.calcUB(r1, r2)
        ub = fourc.calc.sample.UB
    assert isinstance(ub, numpy.ndarray)
    assert isinstance(fourc.UB.get(), numpy.ndarray)


def test_listSamples(capsys, fourc):
    hkl.user.selectDiffractometer(fourc)
    a0 = 5.431
    hkl.user.newSample("silicon", a0, a0, a0, 90, 90, 90)
    capsys.readouterr()  # flush the output buffers

    hkl.user.listSamples(verbose=False)
    out, err = capsys.readouterr()
    assert err == ""
    expected = """
    silicon (*): [5.431, 5.431, 5.431, 90.0, 90.0, 90.0]
    main: [1.54, 1.54, 1.54, 90.0, 90.0, 90.0]
    """.strip().splitlines()
    for e, r in list(zip(expected, str(out).strip().splitlines())):
        assert r.strip() == e.strip()

    hkl.user.listSamples()
    out, err = capsys.readouterr()
    assert err == ""
    expected = """
    Sample: silicon (*)

    ======= =======================================
    key     value
    ======= =======================================
    name    silicon
    lattice [5.431, 5.431, 5.431, 90.0, 90.0, 90.0]
    U       [[1. 0. 0.]
             [0. 1. 0.]
             [0. 0. 1.]]
    UB      [[ 1.15691 -0.      -0.     ]
             [ 0.       1.15691 -0.     ]
             [ 0.       0.       1.15691]]
    ======= =======================================


    Sample: main

    ======= ====================================
    key     value
    ======= ====================================
    name    main
    lattice [1.54, 1.54, 1.54, 90.0, 90.0, 90.0]
    U       [[1. 0. 0.]
             [0. 1. 0.]
             [0. 0. 1.]]
    UB      [[ 4.07999 -0.      -0.     ]
             [ 0.       4.07999 -0.     ]
             [ 0.       0.       4.07999]]
    ======= ====================================
    """.strip().splitlines()
    for e, r in list(zip(expected, str(out).strip().splitlines())):
        assert r.strip() == e.strip()


def test_newSample(fourc):
    hkl.user.selectDiffractometer(fourc)

    # sample is the silicon standard
    a0 = 5.4310196
    hkl.user.newSample("silicon standard", a0, a0, a0, 90, 90, 90)
    assert fourc.calc.sample.name == "silicon standard"
    lattice = fourc.calc.sample.lattice
    assert round(lattice.a, 7) == a0
    assert round(lattice.b, 7) == a0
    assert round(lattice.c, 7) == a0
    assert round(lattice.alpha, 7) == 90
    assert round(lattice.beta, 7) == 90
    assert round(lattice.gamma, 7) == 90


def test_setEnergy(fourc):
    hkl.user.selectDiffractometer(fourc)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 8)
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "keV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8)

    hkl.user.setEnergy(8.1)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 8.1)
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "keV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.1)

    hkl.user.setEnergy(7500, units="eV")
    numpy.testing.assert_approx_equal(fourc.energy.get(), 7500)
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "eV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 7.5)

    hkl.user.setEnergy(7100, units="eV", offset=25)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 7100)
    assert fourc.energy_offset.get() == 25
    assert fourc.energy_units.get() == "eV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 7.125)

    # Now, do not set offset.  It will use the previous value.
    hkl.user.setEnergy(2500, units="eV")
    numpy.testing.assert_approx_equal(fourc.energy.get(), 2500)
    assert fourc.energy_offset.get() == 25
    assert fourc.energy_units.get() == "eV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 2.525)


def test_setor(fourc):
    hkl.user.selectDiffractometer(fourc)
    a0 = 5.4310196
    hkl.user.newSample("silicon standard", a0, a0, a0, 90, 90, 90)

    assert len(fourc.calc.sample.reflections) == 0
    hkl.user.setor(4, 0, 0, -145.451, 0, 0, 69.0966, wavelength=1.54)
    assert len(fourc.calc.sample.reflections) == 1
    assert fourc.calc.sample.reflections == [(4, 0, 0)]

    fourc.omega.move(-145.451)
    fourc.chi.move(90)
    fourc.phi.move(0)
    fourc.tth.move(69.0966)
    hkl.user.setor(0, 4, 0)
    assert len(fourc.calc.sample.reflections) == 2
    assert fourc.calc.sample.reflections == [(4, 0, 0), (0, 4, 0)]


def test_showSample(capsys, fourc):
    hkl.user.selectDiffractometer(fourc)
    a0 = 5.431
    hkl.user.newSample("silicon", a0, a0, a0, 90, 90, 90)
    capsys.readouterr()  # flush the output buffers

    hkl.user.showSample(verbose=False)
    out, err = capsys.readouterr()
    assert str(out).strip() == (
        "silicon (*):" " [5.431, 5.431, 5.431, 90.0, 90.0, 90.0]"
    )
    assert err == ""

    hkl.user.showSample()
    out, err = capsys.readouterr()
    assert err == ""
    expected = """
    Sample: silicon (*)

    ======= =======================================
    key     value
    ======= =======================================
    name    silicon
    lattice [5.431, 5.431, 5.431, 90.0, 90.0, 90.0]
    U       [[1. 0. 0.]
             [0. 1. 0.]
             [0. 0. 1.]]
    UB      [[ 1.15691 -0.      -0.     ]
             [ 0.       1.15691 -0.     ]
             [ 0.       0.       1.15691]]
    ======= =======================================
    """.strip().splitlines()
    for e, r in list(zip(expected, str(out).strip().splitlines())):
        assert r.strip() == e.strip()


def test_updateSample(capsys, fourc):
    hkl.user.selectDiffractometer(fourc)

    hkl.user.updateSample(2, 2, 2, 90, 90, 90)
    out, err = capsys.readouterr()
    assert err == ""
    expected = """
    main (*): [2.0, 2.0, 2.0, 90.0, 90.0, 90.0]
    """.strip().splitlines()
    for e, r in list(zip(expected, str(out).strip().splitlines())):
        assert r.strip() == e.strip()
