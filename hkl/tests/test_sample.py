import gi
import numpy as np
import pytest

gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl import SimulatedE4CV


class Fourc(SimulatedE4CV):
    ...


@pytest.fixture(scope="function")
def fourc():
    fourc = Fourc("", name="fourc")
    return fourc


def test_compute_UB(fourc):
    sample = fourc.calc.sample
    default_UB = sample.UB

    fourc.calc.wavelength = 1.54
    #  compute the UB matrix from two reflections
    r1 = sample.add_reflection(-1, 0, 0, (30, 0, -90, 60))
    r2 = sample.add_reflection(0, 1, 1, (45, 45, 0, 90))
    sample.compute_UB(r1, r2)
    np.testing.assert_array_almost_equal(default_UB, sample.UB)

    #  compute the UB matrix from two other reflections
    # fmt: off
    r3 = sample.add_reflection(
        0.1, 0.2, 0.3,
        (10.7826, 32.3115, 18.4349, 21.5652)
    )
    r4 = sample.add_reflection(
        0.5, 0, 0.001,
        (14.4775, 0, 89.8854, 28.9551)
    )
    # fmt: on
    sample.compute_UB(r3, r4)
    # Since the angles are rounded to 4 decimal places,
    # limit the comparison as well.
    np.testing.assert_array_almost_equal(default_UB, sample.UB, decimal=5)


def test_orientation_reflections(fourc):
    sample = fourc.calc.sample
    assert len(sample._orientation_reflections) == 0

    fourc.calc.wavelength = 1.54
    r1 = sample.add_reflection(-1, 0, 0, (30, 0, -90, 60))
    r2 = sample.add_reflection(0, 1, 1, (45, 45, 0, 90))
    sample.compute_UB(r1, r2)
    assert len(sample._orientation_reflections) == 2
    details = sample.reflections_details
    assert details[0]["orientation_reflection"]
    assert details[1]["orientation_reflection"]

    # fmt: off
    r3 = sample.add_reflection(
        .1, .2, .3,
        (10.7826, 32.3115, 18.4349, 21.5652)
    )
    r4 = sample.add_reflection(
        .5, 0, .001,
        (14.4775, 0, 89.8854, 28.9551)
    )
    # fmt: on
    sample.compute_UB(r3, r4)
    assert len(sample._orientation_reflections) == 2
    details = sample.reflections_details
    assert not details[0]["orientation_reflection"]
    assert not details[1]["orientation_reflection"]
    assert details[2]["orientation_reflection"]
    assert details[3]["orientation_reflection"]

    sample.compute_UB(r1, r2)
    assert len(sample._orientation_reflections) == 2
    details = sample.reflections_details
    assert details[0]["orientation_reflection"]
    assert details[1]["orientation_reflection"]
    assert not details[2]["orientation_reflection"]
    assert not details[3]["orientation_reflection"]

    sample.remove_reflection(r3)
    assert len(sample._orientation_reflections) == 2
    sample.remove_reflection((0.5, 0, 0.001))
    assert len(sample._orientation_reflections) == 2


def test_reflections_details(fourc):
    def compare(expected, received):
        for e, r in list(zip(expected, received)):
            # scalar comparisons
            for key in "flag orientation_reflection wavelength".split():
                assert e[key] == r[key]
            # dictionary comparisons
            for key in "position reflection".split():
                for k, v in e[key].items():
                    assert round(abs(v - r[key][k])) == 0

    sample = fourc.calc.sample
    assert len(sample._orientation_reflections) == 0

    fourc.calc.wavelength = 1.54
    r1 = sample.add_reflection(-1, 0, 0, (30, 0, -90, 60))

    details = sample.reflections_details
    # fmt: off
    expected = [
        dict(
            flag=1,
            orientation_reflection=False,
            position=dict(omega=30, chi=0, phi=-90, tth=60),
            reflection=dict(h=-1, k=0, l=0),
            wavelength=1.54
        )
    ]
    # fmt: on
    compare(expected, details)

    r2 = sample.add_reflection(0, 1, 1, (45, 45, 0, 90))
    # fmt: off
    expected += [
        dict(
            flag=1,
            orientation_reflection=False,
            position=dict(omega=45, chi=45, phi=0, tth=90),
            reflection=dict(h=0, k=1, l=1),
            wavelength=1.54
        )
    ]
    sample.add_reflection(
        .1, .2, .3,
        (10.7826, 32.3115, 18.4349, 21.5652)
    )
    expected += [
        dict(
            flag=1,
            orientation_reflection=False,
            position=dict(
                omega=10.7826,
                chi=32.3115,
                phi=18.4349,
                tth=21.5652
            ),
            reflection=dict(h=.1, k=.2, l=.3),
            wavelength=1.54
        )
    ]
    sample.add_reflection(
        .5, 0, .001,
        (14.4775, 0, 89.8854, 28.9551)
    )
    expected += [
        dict(
            flag=1,
            orientation_reflection=False,
            position=dict(
                omega=14.4775,
                chi=0,
                phi=89.8854,
                tth=28.9551
            ),
            reflection=dict(h=.5, k=0, l=1e-3),
            wavelength=1.54
        ),
    ]
    # fmt: on
    details = sample.reflections_details
    compare(expected, details)

    sample.compute_UB(r1, r2)
    expected[0]["orientation_reflection"] = True
    expected[1]["orientation_reflection"] = True

    details = sample.reflections_details
    compare(expected, details)

    sample.UB = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert len(sample._orientation_reflections) == 0
    expected[0]["orientation_reflection"] = False
    expected[1]["orientation_reflection"] = False

    details = sample.reflections_details
    compare(expected, details)


def test_swap_orientation_reflections(fourc):
    sample = fourc.calc.sample

    fourc.calc.wavelength = 1.54
    #  compute the UB matrix from two reflections
    assert len(sample._orientation_reflections) == 0

    with pytest.raises(ValueError) as exinfo:
        sample.swap_orientation_reflections()
    expected = "Must have exactly 2 orientation reflections defined"
    assert expected in str(exinfo.value)

    r1 = sample.add_reflection(-1, 0, 0, (30, 0, -90, 60))
    assert len(sample._orientation_reflections) == 0

    r2 = sample.add_reflection(0, 1, 1, (45, 45, 0, 90))
    assert len(sample._orientation_reflections) == 0

    ub12 = sample.compute_UB(r1, r2)
    assert len(sample._orientation_reflections) == 2
    assert sample._orientation_reflections == [r1, r2]

    ub21 = sample.swap_orientation_reflections()
    assert len(sample._orientation_reflections) == 2
    assert sample._orientation_reflections == [r2, r1]
    assert (ub12 != ub21).any()

    r3 = sample.add_reflection(1, 1, 1, (1, 2, 3, 4))
    assert len(sample._orientation_reflections) == 2

    ubswap = sample.swap_orientation_reflections()
    assert len(sample._orientation_reflections) == 2
    assert sample._orientation_reflections == [r1, r2]
    assert (ub12 == ubswap).all()

    sample._orientation_reflections.append(r3)
    assert len(sample._orientation_reflections) == 3
    assert sample._orientation_reflections == [r1, r2, r3]
    with pytest.raises(ValueError) as exinfo:
        sample.swap_orientation_reflections()
    expected = "Must have exactly 2 orientation reflections defined"
    assert expected in str(exinfo.value)
