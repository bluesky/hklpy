from .. import SimulatedE4CV
from ..reflect import Reflection
from ..reflect import ReflectionManager
import numpy as np
import pytest


class Fourc(SimulatedE4CV):
    ...


@pytest.fixture(scope="function")
def fourc():
    fourc = Fourc("", name="fourc")
    return fourc


# def test_Reflection_class_raises_AttributeError():
#     with pytest.raises(AttributeError) as exinfo:
#         Reflection("h k l".split(), "omega chi phi tth".split(), 1.54)
#     assert "'h.attr_name' not found" in str(exinfo.value)


@pytest.mark.parametrize(
    "pseudos, reals, wavelength, ok",
    [
        [(0, 1, -1), (10, 20, 30, 40), 1.0, True],
        [(0, -1, -1), (10, 20, 30, 40), 1.0, False],
        [1, (10, 20, 30, 40), 1.0, False],
        [None, (10, 20, 30, 40), 1.0, False],
        [(0, 1, -1), (10, 20), 1.0, False],
        [(0, 1, -1), None, 1.0, False],
        [(0, 1, -1), (10, 20, 30, 40), 2.0, False],
    ],
)
def test_Reflection_equal(pseudos, reals, wavelength, ok):
    r0 = Reflection((0, 1, -1), (10, 20, 30, 40), 1.0)
    r1 = Reflection(pseudos, reals, wavelength)
    if ok:
        assert r0 == r1
    else:
        assert r0 != r1
    assert r1 is not None


def test_Reflection_class(fourc):
    # TODO: test with default reflections
    r1 = Reflection(fourc._pseudo, fourc._real, fourc.calc.wavelength)
    assert r1.wavelength == fourc.calc.wavelength


# FIXME:
# def test_Reflection_repr(fourc):
#     r1 = Reflection(fourc._pseudo, fourc._real, fourc.calc.wavelength)
#     # fmt: off
#     expected = (
#         "Reflection((0.0, 0.0, 0.0), "
#         "(0, 0, 0, 0), wavelength=1.54)"
#     )
#     # fmt: on
#     assert repr(r1) == expected


def test_ReflectionManager_class(fourc):
    manager = ReflectionManager()
    assert manager.all_reflections == []
    assert manager.UB_reflections == []

    assert len(manager) == 0
    assert len(manager.all_reflections) == 0
    assert len(manager.UB_reflections) == 0

    manager.add(fourc._pseudo, fourc._real, fourc.calc.wavelength)
    assert len(manager) == 1
    assert len(manager.all_reflections) == 1
    assert len(manager.UB_reflections) == 1

    manager.clear()
    assert len(manager) == 0
    assert len(manager.all_reflections) == 0
    assert len(manager.UB_reflections) == 0

    r1 = manager.add(fourc._pseudo, fourc._real, fourc.calc.wavelength)
    assert len(manager) == 1
    manager.remove(r1)
    assert len(manager) == 0
    assert len(manager.UB_reflections) == 0

    manager.remove(r1)  # no problem to repeat this
    assert len(manager) == 0


def test_compute_UB(fourc):
    sample = fourc.calc.sample
    default_UB = sample.UB

    fourc.calc.wavelength = 1.54
    #  compute the UB matrix from two reflections
    r1 = sample.add_reflection(-1, 0, 0, (30, 0, -90, 60))
    r2 = sample.add_reflection(0, 1, 1, (45, 45, 0, 90))
    sample.compute_UB(r1, r2)
    np.testing.assert_array_almost_equal(default_UB, sample.UB)

    # manager = sample.refl_mgr
    # assert len(manager.all_reflections) == 2
    # assert manager.all_reflections != [r1, r2]
    # assert manager.UB_reflections == manager.all_reflections

    # refl = Reflection(
    #     (-1, 0, 0),
    #     (30, 0, -90, 60),
    #     fourc.calc.wavelength
    # )
    # r0 = manager.all_reflections[0]
    # assert isinstance(r0, Reflection)
    # assert isinstance(refl, Reflection)
    # assert r0 == refl
