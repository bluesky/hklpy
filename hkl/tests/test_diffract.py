import pytest
import numpy.testing

from ophyd import Component as Cpt
from ophyd import PseudoSingle, SoftPositioner

import gi

gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.calc import A_KEV
from hkl.diffract import E4CV
from hkl.diffract import Constraint


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
    numpy.testing.assert_almost_equal(
        fourc.energy.get(), fourc.calc.energy
    )

    for nrg in (8.0, 8.04, 9.0, 0.931):
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal(fourc.calc.energy, nrg)
        numpy.testing.assert_almost_equal(
            fourc.calc.wavelength, A_KEV / nrg
        )


def test_energy_offset(fourc):
    assert fourc.energy_offset.get() == 0

    nrg = 8.0
    fourc.energy.put(nrg)
    numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
    numpy.testing.assert_almost_equal(
        fourc.energy.get(), fourc.calc.energy
    )

    for offset in (0.05, -0.1):
        fourc.energy_offset.put(offset)
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal(
            fourc.energy.get() + offset, fourc.calc.energy
        )


def test_energy_offset_units(fourc):
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "keV"
    fourc.energy_units.put("eV")
    assert fourc.energy_units.get() == "eV"

    nrg = 931
    fourc.energy.put(nrg)
    numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
    numpy.testing.assert_almost_equal(
        fourc.energy.get() / 1000, fourc.calc.energy
    )

    for offset in (5, -6):
        fourc.energy_offset.put(offset)
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal(
            (fourc.energy.get() + offset) / 1000, fourc.calc.energy
        )


def test_energy_units(fourc):
    assert fourc.energy_units.get() == "keV"
    fourc.energy_units.put("eV")
    assert fourc.energy_units.get() == "eV"

    eV = 931
    fourc.energy.put(eV)
    numpy.testing.assert_almost_equal(fourc.energy.get(), eV)
    numpy.testing.assert_almost_equal(fourc.calc.energy, eV / 1000)


def test_pa(fourc):
    expected = [
        # ["term", "value"],
        ["diffractometer", "fourc"],
        ["geometry", "E4CV"],
        ["class", "Fourc"],
        ["energy (keV)", 8.0],
        ["energy offset (keV)", 0.0],
        ["wavelength (angstrom)", 1.54980],
        ["calc energy (keV)", 8.0],
        ["calc wavelength (angstrom)", 1.54980],
        ["calc engine", "hkl"],
        ["mode", "bissector"],
        # --- row-by-row testing stops here
        ["real positioners", 0.0],  # see below for specific test
        ["sample", 0.0],  # see below for specific test
    ]
    table = fourc.pa(printing=False)
    assert len(expected) == len(table.rows)
    for i, row in enumerate(table.rows):
        if row[0] == "real positioners":
            break
        for c in range(2):
            assert expected[i][c] == row[c]

    # real positioners, table row 10
    expected = """
    ===== ===== ==== ========= ========== ========
    name  value fit  low_limit high_limit inverted
    ===== ===== ==== ========= ========== ========
    omega 0     True -180.0    180.0      False
    chi   0     True -180.0    180.0      False
    phi   0     True -180.0    180.0      False
    tth   0     True -180.0    180.0      False
    ===== ===== ==== ========= ========== ========
    """.strip().splitlines()
    sub_table = table.rows[10][1].splitlines()
    assert len(expected) == len(sub_table)
    for i in range(len(expected)):
        assert expected[i].strip() == sub_table[i].strip()

    # sample, table row 11
    expected = """
    ============================= =================================
    term                          value
    ============================= =================================
    unit cell lengths (angstroms) a=1.54, b=1.54, c=1.54
    unit cell angles (degrees)    alpha=90.0, beta=90.0, gamma=90.0
    [U]                           [[1. 0. 0.]
                                   [0. 1. 0.]
                                   [0. 0. 1.]]
    [UB]                          [[ 4.07999 -0.      -0.     ]
                                   [ 0.       4.07999 -0.     ]
                                   [ 0.       0.       4.07999]]
    ============================= =================================
    """.strip().splitlines()
    sub_table = table.rows[11][1].splitlines()
    assert len(expected) == len(sub_table)
    for i in range(len(expected)):
        assert expected[i].strip() == sub_table[i].strip()


def test_wh(fourc):
    expected = [
        # ["term", "value"],
        ["diffractometer", "fourc"],
        ["sample name", "main"],
        ["energy (keV)", 8.0],
        ["energy offset (keV)", 0.0],
        ["wavelength (angstrom)", 1.54980],
        ["calc engine", "hkl"],
        ["mode", "bissector"],
        ["h", 0.0],
        ["k", 0.0],
        ["l", 0.0],
        ["omega", 0],
        ["chi", 0],
        ["phi", 0],
        ["tth", 0],
    ]
    table = fourc.wh(printing=False)
    assert len(expected) == len(table.rows)
    for i, row in enumerate(table.rows):
        for c in range(2):
            assert expected[i][c] == row[c]

    fourc.energy_units.put("eV")
    expected[2] = ["energy (eV)", 8000.0]
    expected[3] = ["energy offset (eV)", 0.0]
    table = fourc.wh(printing=False)
    assert len(expected) == len(table.rows)
    for i, row in enumerate(table.rows):
        for c in range(2):
            assert expected[i][c] == row[c]


def test_change_energy_units(fourc):
    assert fourc.energy.get() == 8
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "keV"
    assert fourc.calc.energy == 8.0

    # changes fourc.energy, does not change fourc.calc.energy
    fourc.energy_units.put("eV")
    assert fourc.energy.get() == 8000
    assert fourc.calc.energy == 8.0

    # changes fourc.energy, does not change fourc.calc.energy
    fourc.energy_units.put("fJ")  # femtoJoules
    numpy.testing.assert_approx_equal(
        fourc.energy.get(), 1.28174, significant=5
    )
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.0)

    # changes fourc.energy, does not change fourc.calc.energy
    fourc.energy_units.put("keV")
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.0)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 8.0)

    # changes fourc.energy, changes fourc.calc.energy
    fourc.energy.put(8.014)
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.014)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 8.014)

    # changes fourc.energy, does not change fourc.calc.energy
    fourc.energy_offset.put(0.015)
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.014)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 7.999)

    # changes fourc.energy, changes fourc.calc.energy
    fourc.energy.put(8)
    assert fourc.calc.energy == 8.015
    assert fourc.energy.get() == 8

    # changes fourc.energy, does not change fourc.calc.energy
    fourc.energy_units.put("eV")
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.015)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 8014.985)

    # changes fourc.energy, does not change fourc.calc.energy
    fourc.energy_offset.put(20)
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.015)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 7995)

    # changes fourc.energy, changes fourc.calc.energy
    fourc.energy.put(8000)
    numpy.testing.assert_approx_equal(fourc.calc.energy, 8.02)
    numpy.testing.assert_approx_equal(fourc.energy.get(), 8000)


def test_showConstraints(fourc):
    received = str(fourc.showConstraints(printing=False)).splitlines()
    expected = [
        "===== ===== ========= ========== ====",
        "axis  value low_limit high_limit fit ",
        "===== ===== ========= ========== ====",
        "omega 0.0   -180.0    180.0      True",
        "chi   0.0   -180.0    180.0      True",
        "phi   0.0   -180.0    180.0      True",
        "tth   0.0   -180.0    180.0      True",
        "===== ===== ========= ========== ====",
    ]
    for r, e in zip(received, expected):
        assert r == e


def test_applyConstraints(fourc):
    def check(reflection, expected_tuple):
        sol = fourc.forward(1, 0, 0)
        # Round to nearest int since we don't care about
        # minor mistmatches, we just want the right sector.
        for i, expect in enumerate(expected_tuple):
            assert round(sol[i]) == expect

    # test with the default settings
    check((1, 0, 0), (-30, 0, -90, -60))

    fourc.applyConstraints(
        {
            "tth": Constraint(0, 180, 0, True),
            "chi": Constraint(0, 180, 0, True),
        }
    )
    check((1, 0, 0), (30, 0, 90, 60))

    # look for a different reflection
    fourc.applyConstraints(
        {
            # use a plain tuple instead of Constraint()
            "tth": (-180, 0, 0, True),
        }
    )
    check((-1, 0, 0), (-30, 0, -90, -60))

    fourc.undoLastConstraints()
    check((-1, 0, 0), (30, 0, 90, 60))

    fourc.resetConstraints()
    check((1, 0, 0), (-30, 0, -90, -60))
