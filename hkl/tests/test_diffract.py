import gi
import numpy.testing
import pint
import pyRestTable
import pytest

gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.calc import A_KEV
from hkl.geometries import SimulatedE4CV


class Fourc(SimulatedE4CV):
    ...


@pytest.fixture(scope="function")
def fourc():
    fourc = Fourc("", name="fourc")
    fourc.wait_for_connection()
    fourc._update_calc_energy()
    return fourc


def test_calc_energy_permit(fourc):
    assert fourc._calc_energy_update_permitted
    fourc.energy_update_calc_flag.put(False)
    assert not fourc._calc_energy_update_permitted

    nrg = fourc.calc.energy
    fourc.energy.put(5.989)  # BTW: Cr K absorption edge
    numpy.testing.assert_almost_equal(fourc.energy.get(), 5.989)
    numpy.testing.assert_almost_equal(fourc.calc.energy, nrg)

    fourc._energy_changed()
    numpy.testing.assert_almost_equal(fourc.calc.energy, nrg)

    fourc._energy_changed(fourc.energy.get())
    numpy.testing.assert_almost_equal(fourc.calc.energy, nrg)

    fourc._energy_changed(5.989)
    numpy.testing.assert_almost_equal(fourc.calc.energy, nrg)

    fourc._update_calc_energy()
    numpy.testing.assert_almost_equal(fourc.calc.energy, 5.989)

    fourc._update_calc_energy(A_KEV / 1)
    numpy.testing.assert_almost_equal(fourc.calc.energy, A_KEV)


def test_energy(fourc):
    numpy.testing.assert_almost_equal(fourc.energy.get(), fourc.calc.energy)

    for nrg in (8.0, 8.04, 9.0, 0.931):
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal(fourc.calc.energy, nrg)
        numpy.testing.assert_almost_equal(fourc.calc.wavelength, A_KEV / nrg)


def test_energy_offset(fourc):
    assert fourc.energy_offset.get() == 0

    nrg = 8.0
    fourc.energy.put(nrg)
    numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
    numpy.testing.assert_almost_equal(fourc.energy.get(), fourc.calc.energy)

    for offset in (0.05, -0.1):
        fourc.energy_offset.put(offset)
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal(fourc.energy.get() + offset, fourc.calc.energy)


def test_energy_offset_units(fourc):
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "keV"
    fourc.energy_units.put("eV")
    assert fourc.energy_units.get() == "eV"

    nrg = 931
    fourc.energy.put(nrg)
    numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
    numpy.testing.assert_almost_equal(fourc.energy.get() / 1000, fourc.calc.energy)

    for offset in (5, -6):
        fourc.energy_offset.put(offset)
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal((fourc.energy.get() + offset) / 1000, fourc.calc.energy)


def test_energy_units(fourc):
    assert fourc.energy_units.get() == "keV"
    fourc.energy_units.put("eV")
    assert fourc.energy_units.get() == "eV"

    eV = 931
    fourc.energy.put(eV)
    numpy.testing.assert_almost_equal(fourc.energy.get(), eV)
    numpy.testing.assert_almost_equal(fourc.calc.energy, eV / 1000)

    # issue #79
    fourc.energy_units.put("eV")
    fourc.energy_offset.put(0)
    eV = 1746
    fourc.energy.put(eV)
    numpy.testing.assert_almost_equal(fourc.calc.energy, eV / 1000)
    numpy.testing.assert_almost_equal(
        # fmt: off
        pint.Quantity(fourc.calc.energy, "keV").to(fourc.energy_units.get()).magnitude,
        fourc.energy.get(),
        # fmt: on
    )

    fourc.energy_units.put("keV")
    fourc.energy.put(8)
    fourc.energy_offset.put(0.015)
    assert fourc.calc.energy == 8.0
    assert round(fourc.energy.get(), 6) == 7.985
    fourc.energy.put(8)
    assert fourc.calc.energy == 8.015
    assert round(fourc.energy.get(), 6) == 8

    # issue #86
    # changing units or offset changes .energy, not .calc.energy
    fourc.energy_units.put("eV")
    assert fourc.calc.energy == 8.015
    assert round(fourc.energy.get(), 1) == 8015
    fourc.energy.put(8000)
    assert round(fourc.calc.energy, 8) == 8.000015
    assert round(fourc.energy.get(), 1) == 8000
    fourc.energy_offset.put(15)
    assert round(fourc.calc.energy, 8) == 8.000015
    assert round(fourc.energy.get(), 1) == 7985
    fourc.energy.put(8000)
    assert round(fourc.calc.energy, 8) == 8.015
    assert round(fourc.energy.get(), 1) == 8000


def test_names(fourc):
    assert fourc.geometry_name.get() == "E4CV"
    assert fourc.class_name.get() == "Fourc"


def test_pa(fourc, capsys):
    tbl = fourc.pa()
    assert isinstance(tbl, pyRestTable.Table)
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
    tbl = fourc.wh()
    assert isinstance(tbl, pyRestTable.Table)
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
