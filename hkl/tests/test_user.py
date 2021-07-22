import pytest
import numpy.testing

import gi

gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl import SimulatedE4CV
from hkl import SI_LATTICE_PARAMETER
import hkl.user


class Fourc(SimulatedE4CV):
    ...


@pytest.fixture(scope="function")
def fourc():
    fourc = Fourc("", name="fourc")
    fourc.wait_for_connection()
    fourc._update_calc_energy()
    return fourc


def test_select_diffractometer(capsys, fourc):
    # This test function must be first or the next assertion will fail.
    assert hkl.user._geom_ is None
    hkl.user.select_diffractometer(fourc)
    assert hkl.user._geom_ is not None
    assert hkl.user._geom_ == fourc
    capsys.readouterr()  # flush the output buffers

    hkl.user.show_selected_diffractometer()
    out, err = capsys.readouterr()
    assert str(err) == ""
    assert str(out).strip() == "fourc"


def test_cahkl(fourc):
    hkl.user.select_diffractometer(fourc)
    fourc.calc["tth"].limits = (0, 180)

    # use the default "main" sample and UB matrix
    response = hkl.user.cahkl(1, 0, 0)
    expected = (30, 0, 90, 60)
    assert round(response[0]) == expected[0]
    assert round(response[1]) == expected[1]
    assert round(response[2]) == expected[2]
    assert round(response[3]) == expected[3]


def test_cahkl_table(capsys, fourc):
    hkl.user.select_diffractometer(fourc)
    fourc.calc["tth"].limits = (0, 180)

    # use the default "main" sample and UB matrix
    rlist = [(1, 0, 0), (0, 1, 0)]
    hkl.user.cahkl_table(rlist, digits=0)
    out, err = capsys.readouterr()
    expected = """
    ========= ======== ===== === === ===
    (hkl)     solution omega chi phi tth
    ========= ======== ===== === === ===
    (1, 0, 0) 0        30    0   90  60
    (0, 1, 0) 0        30    90  0   60
    ========= ======== ===== === === ===
    """.strip().splitlines()
    assert err == ""
    for el, rl in list(zip(expected[3:5], str(out).strip().splitlines()[3:5])):
        # just compare the position values
        for e, r in list(zip(el.split()[-4:], rl.split()[-4:])):
            assert float(r) == float(e)


def test_calc_UB(fourc):
    hkl.user.select_diffractometer(fourc)
    a0 = SI_LATTICE_PARAMETER
    hkl.user.new_sample("silicon standard", a0, a0, a0, 90, 90, 90)
    r1 = hkl.user.setor(4, 0, 0, tth=69.0966, omega=-145.451, chi=0, phi=0, wavelength=1.54)
    fourc.omega.move(-145.451)
    fourc.chi.move(90)
    fourc.phi.move(0)
    fourc.tth.move(69.0966)
    r2 = hkl.user.setor(0, 4, 0)

    ub = hkl.user.calc_UB(r1, r2)
    if ub is None:
        hkl.user.calc_UB(r1, r2)
        ub = fourc.calc.sample.UB
    assert isinstance(ub, numpy.ndarray)
    assert isinstance(fourc.UB.get(), numpy.ndarray)


def test_list_samples(capsys, fourc):
    hkl.user.select_diffractometer(fourc)
    a0 = SI_LATTICE_PARAMETER
    hkl.user.new_sample("silicon", a0, a0, a0, 90, 90, 90)
    capsys.readouterr()  # flush the output buffers

    hkl.user.list_samples(verbose=False)
    out, err = capsys.readouterr()
    assert err == ""
    expected = """
    silicon (*): [5.431020511, 5.431020511, 5.431020511, 90.0, 90.0, 90.0]
    main: [1.54, 1.54, 1.54, 90.0, 90.0, 90.0]
    """.strip().splitlines()
    for e, r in list(zip(expected, str(out).strip().splitlines())):
        assert r.strip() == e.strip()

    hkl.user.list_samples()
    out, err = capsys.readouterr()
    assert err == ""
    expected = """
    Sample: silicon (*)

    ======= =========================================================
    key     value
    ======= =========================================================
    name    silicon
    lattice [5.431020511, 5.431020511, 5.431020511, 90.0, 90.0, 90.0]
    U       [[1. 0. 0.]
             [0. 1. 0.]
             [0. 0. 1.]]
    UB      [[ 1.15691 -0.      -0.     ]
             [ 0.       1.15691 -0.     ]
             [ 0.       0.       1.15691]]
    ======= =========================================================


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


def test_new_sample(fourc):
    hkl.user.select_diffractometer(fourc)

    # sample is the silicon standard
    a0 = SI_LATTICE_PARAMETER
    hkl.user.new_sample("silicon standard", a0, a0, a0, 90, 90, 90)
    assert fourc.calc.sample.name == "silicon standard"
    lattice = fourc.calc.sample.lattice
    assert round(lattice.a, 9) == a0
    assert round(lattice.b, 9) == a0
    assert round(lattice.c, 9) == a0
    assert round(lattice.alpha, 7) == 90
    assert round(lattice.beta, 7) == 90
    assert round(lattice.gamma, 7) == 90


def test_set_energy(fourc):
    hkl.user.select_diffractometer(fourc)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 8)
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "keV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8)

    hkl.user.set_energy(8.1)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 8.1)
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "keV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.1)

    hkl.user.set_energy(7500, units="eV")
    numpy.testing.assert_approx_equal(fourc.energy.get(), 7500)
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "eV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 7.5)

    hkl.user.set_energy(7100, units="eV", offset=25)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 7100)
    assert fourc.energy_offset.get() == 25
    assert fourc.energy_units.get() == "eV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 7.125)

    # Now, do not set offset.  It will use the previous value.
    hkl.user.set_energy(2500, units="eV")
    numpy.testing.assert_approx_equal(fourc.energy.get(), 2500)
    assert fourc.energy_offset.get() == 25
    assert fourc.energy_units.get() == "eV"
    numpy.testing.assert_approx_equal(fourc.calc.energy, 2.525)


def test_setor(fourc):
    hkl.user.select_diffractometer(fourc)
    a0 = SI_LATTICE_PARAMETER
    hkl.user.new_sample("silicon standard", a0, a0, a0, 90, 90, 90)

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


def test_show_sample(capsys, fourc):
    hkl.user.select_diffractometer(fourc)
    a0 = SI_LATTICE_PARAMETER
    hkl.user.new_sample("silicon", a0, a0, a0, 90, 90, 90)
    capsys.readouterr()  # flush the output buffers

    hkl.user.show_sample(verbose=False)
    out, err = capsys.readouterr()
    assert str(out).strip() == ("silicon (*):" " [5.431020511, 5.431020511, 5.431020511, 90.0, 90.0, 90.0]")
    assert err == ""

    hkl.user.show_sample()
    out, err = capsys.readouterr()
    assert err == ""
    expected = """
    Sample: silicon (*)

    ======= =========================================================
    key     value
    ======= =========================================================
    name    silicon
    lattice [5.431020511, 5.431020511, 5.431020511, 90.0, 90.0, 90.0]
    U       [[1. 0. 0.]
             [0. 1. 0.]
             [0. 0. 1.]]
    UB      [[ 1.15691 -0.      -0.     ]
             [ 0.       1.15691 -0.     ]
             [ 0.       0.       1.15691]]
    ======= =========================================================
    """.strip().splitlines()
    for e, r in list(zip(expected, str(out).strip().splitlines())):
        assert r.strip() == e.strip()


def test_update_sample(capsys, fourc):
    hkl.user.select_diffractometer(fourc)

    hkl.user.update_sample(2, 2, 2, 90, 90, 90)
    out, err = capsys.readouterr()
    assert err == ""
    expected = """
    main (*): [2.0, 2.0, 2.0, 90.0, 90.0, 90.0]
    """.strip().splitlines()
    for e, r in list(zip(expected, str(out).strip().splitlines())):
        assert r.strip() == e.strip()


def test_pa(fourc, capsys):
    hkl.user.select_diffractometer(fourc)

    tbl = hkl.user.pa()
    assert tbl is None
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert err == ""
    out = [v.rstrip() for v in out.strip().splitlines()]
    expected = [
        "===================== ====================================================================",
        "term                  value",
        "===================== ====================================================================",
        "diffractometer        fourc",
        "geometry              E4CV",
        "class                 Fourc",
        "energy (keV)          8.00000",
        "wavelength (angstrom) 1.54980",
        "calc engine           hkl",
        "mode                  bissector",
        "positions             ===== =======",
        "                      name  value",
        "                      ===== =======",
        "                      omega 0.00000",
        "                      chi   0.00000",
        "                      phi   0.00000",
        "                      tth   0.00000",
        "                      ===== =======",
        "constraints           ===== ========= ========== ===== ====",
        "                      axis  low_limit high_limit value fit",
        "                      ===== ========= ========== ===== ====",
        "                      omega -180.0    180.0      0.0   True",
        "                      chi   -180.0    180.0      0.0   True",
        "                      phi   -180.0    180.0      0.0   True",
        "                      tth   -180.0    180.0      0.0   True",
        "                      ===== ========= ========== ===== ====",
        "sample: main          ================ ===================================================",
        "                      term             value",
        "                      ================ ===================================================",
        "                      unit cell edges  a=1.54, b=1.54, c=1.54",
        "                      unit cell angles alpha=90.0, beta=90.0, gamma=90.0",
        "                      [U]              [[1. 0. 0.]",
        "                                        [0. 1. 0.]",
        "                                        [0. 0. 1.]]",
        "                      [UB]             [[ 4.07999046e+00 -2.49827363e-16 -2.49827363e-16]",
        "                                        [ 0.00000000e+00  4.07999046e+00 -2.49827363e-16]",
        "                                        [ 0.00000000e+00  0.00000000e+00  4.07999046e+00]]",
        "                      ================ ===================================================",
        "===================== ====================================================================",
    ]
    assert len(out) == len(expected)
    assert out == expected


def test_wh(fourc, capsys):
    hkl.user.select_diffractometer(fourc)

    tbl = hkl.user.wh()
    assert tbl is None
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert err == ""
    out = [v.rstrip() for v in out.strip().splitlines()]
    expected = [
        "===================== ========= =========",
        "term                  value     axis_type",
        "===================== ========= =========",
        "diffractometer        fourc",
        "sample name           main",
        "energy (keV)          8.00000",
        "wavelength (angstrom) 1.54980",
        "calc engine           hkl",
        "mode                  bissector",
        "h                     0.0       pseudo",
        "k                     0.0       pseudo",
        "l                     0.0       pseudo",
        "omega                 0         real",
        "chi                   0         real",
        "phi                   0         real",
        "tth                   0         real",
        "===================== ========= =========",
    ]
    assert len(out) == len(expected)
    assert out == expected
