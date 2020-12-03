
import pytest
import numpy.testing

from ophyd import Component as Cpt
from ophyd import (PseudoSingle, SoftPositioner)

import gi
gi.require_version('Hkl', '5.0')
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.calc import A_KEV
from hkl.diffract import E4CV


class Fourc(E4CV):
    h = Cpt(PseudoSingle, '')
    k = Cpt(PseudoSingle, '')
    l = Cpt(PseudoSingle, '')

    omega = Cpt(SoftPositioner)
    chi = Cpt(SoftPositioner)
    phi = Cpt(SoftPositioner)
    tth = Cpt(SoftPositioner)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for p in self.real_positioners:
            p._set_position(0)  # give each a starting position


@pytest.fixture(scope='function')
def fourc():
    fourc = Fourc('', name='fourc')
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
    numpy.testing.assert_almost_equal(
        fourc.calc.energy, nrg)

    fourc._energy_changed(fourc.energy.get())
    numpy.testing.assert_almost_equal(
        fourc.calc.energy, nrg)

    fourc._energy_changed(5.989)
    numpy.testing.assert_almost_equal(
        fourc.calc.energy, nrg)

    fourc._update_calc_energy()
    numpy.testing.assert_almost_equal(
        fourc.calc.energy, 5.989)

    fourc._update_calc_energy(A_KEV/1)
    numpy.testing.assert_almost_equal(
        fourc.calc.energy, A_KEV)


def test_energy(fourc):
    numpy.testing.assert_almost_equal(
        fourc.energy.get(), fourc.calc.energy)

    for nrg in (8.0, 8.04, 9.0, 0.931):
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal(fourc.calc.energy, nrg)
        numpy.testing.assert_almost_equal(
            fourc.calc.wavelength, A_KEV/nrg)


def test_energy_offset(fourc):
    assert fourc.energy_offset.get() == 0

    nrg = 8.0
    fourc.energy.put(nrg)
    numpy.testing.assert_almost_equal(
        fourc.energy.get(), nrg)
    numpy.testing.assert_almost_equal(
        fourc.energy.get(), fourc.calc.energy)

    for offset in (0.05, -0.1):
        fourc.energy_offset.put(offset)
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(
            fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal(
            fourc.energy.get() + offset, fourc.calc.energy)


def test_energy_offset_units(fourc):
    assert fourc.energy_offset.get() == 0
    assert fourc.energy_units.get() == "keV"
    fourc.energy_units.put("eV")
    assert fourc.energy_units.get() == "eV"

    nrg = 931
    fourc.energy.put(nrg)
    numpy.testing.assert_almost_equal(fourc.energy.get(), nrg)
    numpy.testing.assert_almost_equal(
        fourc.energy.get()/1000, fourc.calc.energy)

    for offset in (5, -6):
        fourc.energy_offset.put(offset)
        fourc.energy.put(nrg)
        numpy.testing.assert_almost_equal(
            fourc.energy.get(), nrg)
        numpy.testing.assert_almost_equal(
            (fourc.energy.get() + offset)/1000, fourc.calc.energy)


def test_energy_units(fourc):
    assert fourc.energy_units.get() == "keV"
    fourc.energy_units.put("eV")
    assert fourc.energy_units.get() == "eV"

    eV = 931
    fourc.energy.put(eV)
    numpy.testing.assert_almost_equal(
        fourc.energy.get(), eV)
    numpy.testing.assert_almost_equal(
        fourc.calc.energy, eV/1000)
