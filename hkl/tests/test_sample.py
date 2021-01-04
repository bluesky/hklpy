from ophyd import Component as Cpt
from ophyd import PseudoSingle, SoftPositioner
import gi
import numpy.testing
import pytest

gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.diffract import E4CV


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
    # fourc._update_calc_energy()
    return fourc


def test_compute_UB(fourc):
    e4cv = fourc
    e4cv.energy.put(8.0)
    r1 = e4cv.calc.sample.add_reflection(0, 0, 1, (30, 0, 0, 60))
    r2 = e4cv.calc.sample.add_reflection(0, 1, 1, (45, 45, 0, 90))
    result = e4cv.calc.sample.compute_UB(r1, r2)
    assert result is not None
    assert isinstance(result, numpy.ndarray)

    r3 = e4cv.calc.sample.add_reflection(0, 0, 0.5, (30 / 2, 0, 0, 60 / 2))
    with pytest.raises(Exception) as exinfo:
        e4cv.calc.sample.compute_UB(r1, r3)
    assert "given reflections are colinear" in str(exinfo.value)
