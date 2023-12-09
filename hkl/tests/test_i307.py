from collections import namedtuple
from contextlib import nullcontext as does_not_raise

import pytest

# from ..util import get_position_tuple

# TODO: test all the different ways positions can be entered
# tuple
# list
# namedtuple
# Position object


@pytest.mark.parametrize(
    "args, interceptor, message",
    [
        # wrong number of reals, tuple
        [[1, 2, 3, (4, 5)], pytest.raises(ValueError), "Expected 4 positions,"],
        # wrong number of reals, list
        [[1, 2, 3, [4, 5]], pytest.raises(ValueError), "Expected 4 positions,"],
        # wrong number of reals, namedtuple
        [
            [1, 2, 3, namedtuple("Position", "omega chi phi".split())(1, 2, 3)],
            pytest.raises(ValueError),
            "Expected 4 positions,",
        ],
        # wrong representation of position
        [[1, 2, 3, 4], pytest.raises(TypeError), "Expected positions"],
        # pseudos provided as tuple
        [[(1, 2, 3), (4, 5, 6, 7)], pytest.raises(TypeError), "missing 1 required"],
        # only pseudos (uses current positions so no problem)
        [[1, 2, 3], does_not_raise(), None],
        [[1, 2, 3, namedtuple("Position", "omega chi phi tth".split())(4, 5, 6, 7)], does_not_raise(), None],
    ],
)
def test_add_reflection(args, interceptor, message, e4cv):
    calc = e4cv.calc
    sample = calc.sample
    assert sample is not None

    # engine = calc.engine
    # engine.mode = "bissector"
    # assert calc.physical_axis_names == engine._engine.axis_names_get(0)
    # assert calc.physical_axis_names == engine.axes_r

    with interceptor as exinfo:
        sample.add_reflection(*args)
    if message is not None:
        assert message in str(exinfo.value)


def test_axes(e4cv):
    calc = e4cv.calc
    engine = calc.engine
    engine.mode = "bissector"  # tests below apply to this engine and mode
    assert calc.physical_axis_names == engine._engine.axis_names_get(0)
    assert calc.physical_axis_names == engine.axes_r
    assert calc.physical_axis_names == engine.axes_w
    assert [] == engine.axes_c
