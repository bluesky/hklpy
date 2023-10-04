import numpy as np
import numpy.testing
import pytest
from bluesky import plans as bp
from bluesky.run_engine import RunEngine
from ophyd.positioner import LimitError

from .. import SimulatedE4CV
from ..calc import UnreachableError


class Fourc(SimulatedE4CV):
    ...


def check_hkl(diffractometer, h, k, l):
    try:
        diffractometer.check_value({"h": h, "k": k, "l": l})
    except UnreachableError as exc:
        assert False, f"({h}, {k}, {l}) : {exc}"


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


@pytest.mark.parametrize("start", [[1.2, 1.2, 0.001], [1, 0, 0], [1, 1, 1]])
@pytest.mark.parametrize("h", np.arange(0.9, 1.1, 0.1))
@pytest.mark.parametrize("k", np.arange(0.0, 1.2, 0.6))
@pytest.mark.parametrize("l", np.arange(0, 1, 0.5))
def test_hkl_scan(start, h, k, l, fourc):
    assert len(start) == 3
    fourc.move(start)
    check_hkl(fourc, h, k, l)


def test_hkl_range_error(fourc):
    with pytest.raises(UnreachableError) as exinfo:
        fourc.check_value({"h": 0.9, "k": 0.9, "l": 123})
    assert "Unable to solve." in str(exinfo.value)


@pytest.mark.parametrize("start", [[1, 1, 1]])
@pytest.mark.parametrize("tth", np.arange(10, 20, 4))
def test_real_axis(start, tth, fourc):
    assert len(start) == 3
    fourc.move(start)
    try:
        fourc.check_value({"tth": tth})
    except UnreachableError as exc:
        assert False, f"{exc}"


@pytest.mark.parametrize("start", [[1, 1, 1]])
@pytest.mark.parametrize(
    "target",
    [
        {"tth": 10},
        {"tth": 20},
        {"tth": 20, "chi": 7},
    ],
)
def test_moves(start, target, fourc):
    assert len(start) == 3
    assert isinstance(target, dict)
    fourc.move(start)
    try:
        fourc.inverse(target)
    except UnreachableError as exc:
        assert False, f"{target=} : {exc}"


def test_axis_contention(fourc):
    RE = RunEngine()
    # contention if move pseudo and real positioners together
    with pytest.raises(ValueError) as exinfo:
        RE(bp.scan([fourc], fourc.tth, 10, 20, fourc.k, 0, 0, 3))
    assert "mix of real and pseudo" in str(exinfo.value)


def test_real_axis_range_error(fourc):
    with pytest.raises(LimitError) as exinfo:
        fourc.check_value({"tth": 10_000})
    assert "not within limits" in str(exinfo.value)
