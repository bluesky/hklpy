
from bluesky import plans as bp
# TODO: from bluesky.simulators import check_limits
from ophyd import (PseudoSingle, SoftPositioner)
from ophyd import Component as Cpt
from ophyd.positioner import LimitError
from warnings import warn
import numpy as np
import numpy.testing
import pytest

import gi
gi.require_version('Hkl', '5.0')
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.diffract import E4CV


# TODO: remove once bluesky 1.6.6+ is released
def check_limits(plan):
    """
    Check that a plan will not move devices outside of their limits.

    Parameters
    ----------
    plan : iterable
        Must yield `Msg` objects
    """
    ignore = []
    for msg in plan:
        if msg.command == 'set' and msg.obj not in ignore:
            if hasattr(msg.obj, "check_value"):
                msg.obj.check_value(msg.args[0])
            else:
                warn(f"{msg.obj.name} has no check_value() method"
                     f" to check if {msg.args[0]} is within its limits.")
                ignore.append(msg.obj)


class Fourc(E4CV):
    h = Cpt(PseudoSingle, '')
    k = Cpt(PseudoSingle, '')
    l = Cpt(PseudoSingle, '')

    omega = Cpt(SoftPositioner, limits=(-180, 180))
    chi = Cpt(SoftPositioner, limits=(-180, 180))
    phi = Cpt(SoftPositioner, limits=(-180, 180))
    tth = Cpt(SoftPositioner, limits=(-180, 180))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for p in self.real_positioners:
            p._set_position(0)  # give each a starting position


@pytest.fixture(scope='function')
def fourc():
    fourc = Fourc('', name="fourc")
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
    rpos = (58.051956519652485, 44.99999005281953,
            89.95225352812487, 116.10391303930497)
    fourc.move(ppos)
    numpy.testing.assert_almost_equal(fourc.position, ppos)
    numpy.testing.assert_almost_equal(tuple(fourc.real_position), rpos)


def test_hl_scan(fourc):
    fourc.move((1.2, 1.2, 0.001))
    assert check_limits(
        bp.scan(
            [fourc],
            fourc.h, 0.9, 1.1,
            fourc.l, 0, 0,
            11)
    ) is None


def test_h00_scan(fourc):
    fourc.move(1, 0, 0)
    assert check_limits(
        bp.scan(
            [fourc],
            fourc.h, 0.9, 1.1,
            fourc.l, 0, 0,
            11)
    ) is None


def test_hkl_scan(fourc):
    fourc.move(1, 1, 1)
    assert check_limits(
        bp.scan(
            [fourc],
            fourc.h, 0.9, 1.1,
            fourc.k, 0.9, 1.1,
            fourc.l, 0.9, 1.1,
            33)
    ) is None


def test_hkl_range_error(fourc):
    with pytest.raises(ValueError) as exinfo:
        assert check_limits(
            bp.scan(
                [fourc],
                fourc.h, 0.9, 1.1,
                fourc.k, 0.9, 1.1,
                fourc.l, 0.09, 123.1,
                33)
        ) is None
    assert "Unable to solve." in str(exinfo.value)


def test_real_axis(fourc):
    assert check_limits(
        bp.scan(
            [fourc],
            fourc.tth, 10, 20,
            3)
    ) is None


def test_axis_contention(fourc):
    # contention if move pseudo and real positioners together
    with pytest.raises(ValueError) as exinfo:
        check_limits(
            bp.scan(
                [fourc],
                fourc.tth, 10, 20,
                fourc.k, 0, 0,
                3)
        )
    assert "mix of real and pseudo" in str(exinfo.value)


def test_real_axis_range_multi(fourc):
    assert check_limits(
        bp.scan(
            [fourc],
            fourc.tth, 10, 20,
            fourc.chi, 5, 7,
            3)
    ) is None


def test_real_axis_range_error(fourc):
    with pytest.raises(LimitError) as exinfo:
        check_limits(
            bp.scan(
                [fourc],
                fourc.tth, 10, 20000,
                3)
        )
    assert "not within limits" in str(exinfo.value)
