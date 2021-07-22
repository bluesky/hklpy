from bluesky import plans as bp
from bluesky.simulators import check_limits
from ophyd.positioner import LimitError
import gi
import numpy as np
import numpy.testing
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


def test_initial(fourc):
    assert fourc.h.position == 0
    assert fourc.k.position == 0
    assert fourc.l.position == 0


def test_limits(fourc):
    assert fourc.h.limits == (0, 0)
    assert fourc.h.check_value(1) is None
    assert fourc.h.check_value(1.2) is None
    with pytest.raises(ValueError) as exinfo:
        fourc.h.check_value(10)
    assert "Unable to solve." in str(exinfo.value)


def test_check_value(fourc):
    assert fourc.check_value((1, 0, 0)) is None
    assert fourc.check_value(dict(h=1, k=0, l=0)) is None
    assert fourc.check_value(dict(h=1, k=0)) is None

    with pytest.raises(TypeError) as exinfo:
        assert fourc.check_value(1, 0, 0) is None
    assert "check_value() takes 2 positional arguments" in str(exinfo.value)

    with pytest.raises(ValueError) as exinfo:
        assert fourc.check_value(1) is None
    assert "Not all required values for a PseudoPosition" in str(exinfo.value)

    assert fourc.check_value(dict(h=1, tth=0)) is None

    with pytest.raises(LimitError) as exinfo:
        fourc.check_value(dict(h=1, tth=np.inf))
    assert "position=inf not within limits" in str(exinfo.value)

    with pytest.raises(KeyError) as exinfo:
        fourc.check_value(dict(waldo=0))
    assert "waldo not in fourc" in str(exinfo.value)


def test_move(fourc):
    ppos = (1.2, 1.2, 0.001)
    rpos = (
        58.051956519652485,
        44.99999005281953,
        89.95225352812487,
        116.10391303930497,
    )
    fourc.move(ppos)
    numpy.testing.assert_almost_equal(fourc.position, ppos)
    numpy.testing.assert_almost_equal(tuple(fourc.real_position), rpos)


def test_hl_scan(fourc):
    fourc.move((1.2, 1.2, 0.001))
    assert check_limits(bp.scan([fourc], fourc.h, 0.9, 1.1, fourc.l, 0, 0, 11)) is None


def test_h00_scan(fourc):
    fourc.move(1, 0, 0)
    assert check_limits(bp.scan([fourc], fourc.h, 0.9, 1.1, fourc.l, 0, 0, 11)) is None


def test_hkl_scan(fourc):
    fourc.move(1, 1, 1)
    assert (
        check_limits(
            # fmt: off
            bp.scan(
                [fourc],
                fourc.h, 0.9, 1.1,
                fourc.k, 0.9, 1.1,
                fourc.l, 0.9, 1.1,
                33,
            )
            # fmt: on
        )
        is None
    )


def test_hkl_range_error(fourc):
    with pytest.raises(ValueError) as exinfo:
        assert (
            check_limits(
                # fmt: off
                bp.scan(
                    [fourc],
                    fourc.h, 0.9, 1.1,
                    fourc.k, 0.9, 1.1,
                    fourc.l, 0.09, 123.1,
                    33,
                )
                # fmt: on
            )
            is None
        )
    assert "Unable to solve." in str(exinfo.value)


def test_real_axis(fourc):
    assert check_limits(bp.scan([fourc], fourc.tth, 10, 20, 3)) is None


def test_axis_contention(fourc):
    # contention if move pseudo and real positioners together
    with pytest.raises(ValueError) as exinfo:
        check_limits(bp.scan([fourc], fourc.tth, 10, 20, fourc.k, 0, 0, 3))
    assert "mix of real and pseudo" in str(exinfo.value)


def test_real_axis_range_multi(fourc):
    assert check_limits(bp.scan([fourc], fourc.tth, 10, 20, fourc.chi, 5, 7, 3)) is None


def test_real_axis_range_error(fourc):
    with pytest.raises(LimitError) as exinfo:
        check_limits(bp.scan([fourc], fourc.tth, 10, 20000, 3))
    assert "not within limits" in str(exinfo.value)
