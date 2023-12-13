"""
Tests for changes due to issues #307 & #308.
"""

from collections import namedtuple
from contextlib import nullcontext as does_not_raise

import pytest

from ..util import get_position_tuple


@pytest.mark.parametrize(
    "miller, context, message",
    [
        [(1, 2, 3), does_not_raise(), None],
        [(1.0, 2.0, 3.0), does_not_raise(), None],
        [("1", 2, 3), pytest.raises(TypeError), "Must be number, not str"],
        [(1, 2, "3"), pytest.raises(TypeError), "Must be number, not str"],
        [([1], 2, 3), pytest.raises(TypeError), "Must be number, not list"],
        [(object, 2, 3), pytest.raises(TypeError), "Must be number, not type"],
        [(None, 2, 3), pytest.raises(TypeError), "does not allow None as a value"],
        [None, pytest.raises(TypeError), "argument after * must be an iterable, not NoneType"],
        [((1,), 2, 3), pytest.raises(TypeError), "Must be number, not tuple"],
        [
            # Tests that h, k, l was omitted, only a position was supplied.
            # This is one of the problems reported.
            namedtuple("PosAnything", "a b c d".split())(1, 2, 3, 4),
            pytest.raises(TypeError),
            "Expected positions, received 4",
        ],
    ],
)
def test_miller_args(miller, context, message, e4cv):
    """Test the Miller indices arguments: h, k, l."""
    sample = e4cv.calc.sample
    assert sample is not None

    with context as info:
        sample.add_reflection(*miller)
    if message is not None:
        assert message in str(info.value)


# fmt: off
@pytest.mark.parametrize(
    "miller, angles, context, message",
    [
        # None
        [(-1, -2, -3), None, does_not_raise(), None],
        # tuple
        [(-1, -2, -3), (1, 2, 3, 4), does_not_raise(), None],
        # list
        [(-1, -2, -3), [1, 2, 3, 4], does_not_raise(), None],
        # dict
        [
            (-1, -2, -3),
            {"omega": 1, "chi": 2, "phi": 3, "tth": 4},
            pytest.raises(TypeError),
            "Expected list, tuple, or calc.Position() object,",
        ],
        # namedtuple
        [(-1, -2, -3), "namedtuple 1 2 3 4", does_not_raise(), None],
        # calc.Position object
        [(-1, -2, -3), "Position 1 2 3 4", does_not_raise(), None],
        # Unacceptable namedtuple (does not start with "Pos")
        [
            (-10, -2, -3),
            namedtuple("Not_Position", "a b c d".split())(1, 2, 3, 4),
            pytest.raises(TypeError),
            "Expected list, tuple, or calc.Position() object",
        ],
        # Acceptable namedtuple (starts with "Pos") type
        # yet the axis names are wrong.
        [
            (-10, -2, -3),
            namedtuple("Positron", "a b c d".split())(1, 2, 3, 4),
            pytest.raises(KeyError),
            "Wrong axes names.  Expected [",
        ],
        # Acceptable namedtuple (starts with "Pos") type
        # yet values must all be numeric.
        [
            (-10, -2, -3),
            namedtuple("Post", "omega chi phi tth".split())(1, "2", 3, 4),
            pytest.raises(TypeError),
            "All values must be numeric",
        ],
        # Acceptable namedtuple (starts with "Pos") type & content.
        [
            (-10, -2, -3),
            namedtuple("Posh", "omega chi phi tth".split())(1, 2, 3, 4),
            does_not_raise(),
            None,
        ],
    ]
)
# fmt: on
def test_position_args(miller, angles, context, message, e4cv):
    """Test sample.add_reflection with the different ways positions can be entered."""
    assert len(miller) == 3

    calc = e4cv.calc
    assert calc is not None

    sample = calc.sample
    assert sample is not None

    if isinstance(angles, str):
        # These constructs require some additional setup.
        if angles.startswith("Position"):
            angles = calc.Position(*map(float, angles.split()[1:]))
        elif angles.startswith("namedtuple"):
            # fmt: off
            angles = get_position_tuple("omega chi phi tth".split())(
                *list(map(float, angles.split()[1:]))
            )
            # fmt: on

    with context as info:
        sample.add_reflection(*miller, angles)
    if message is not None:
        assert message in str(info.value)


@pytest.mark.parametrize(
    "args, context, message",
    [
        # wrong number of reals, tuple
        [[1, 2, 3, (4, 5)], pytest.raises(ValueError), "Expected 4 positions,"],
        # wrong number of reals, list
        [[1, 2, 3, [4, 5]], pytest.raises(ValueError), "Expected 4 positions,"],
        # wrong number of reals, namedtuple
        [
            [1, 2, 3, namedtuple("Position", "omega chi phi".split())(1, 2, 3)],
            pytest.raises(KeyError),
            "Wrong axes names.  Expected [",
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
def test_add_reflection(args, context, message, e4cv):
    calc = e4cv.calc
    sample = calc.sample
    assert sample is not None

    with context as info:
        sample.add_reflection(*args)
    if message is not None:
        assert message in str(info.value)


@pytest.mark.parametrize(
    "dname, mode, n_r, n_w, e_a_c, c_a_c",
    [
        # all modes on each common geometry, some with canonical names, some with renames
        # If not renamed, set c_a_c to `None`
        # fmt: off
        ["e4cv", "bissector", 4, 4, "", None],
        ["e4cv", "constant_chi", 4, 3, "chi", None],
        ["e4cv", "constant_omega", 4, 3, "omega", None],
        ["e4cv", "constant_phi", 4, 3, "phi", None],

        ["e4cv_renamed", "bissector", 4, 4, "", ""],
        ["e4cv_renamed", "constant_chi", 4, 3, "chi", "chi"],
        ["e4cv_renamed", "constant_omega", 4, 3, "omega", "theta"],
        ["e4cv_renamed", "constant_phi", 4, 3, "phi", "phi"],
        ["e4cv_renamed", "double_diffraction", 4, 4, "", ""],

        ["e6c", "bissector_horizontal", 6, 5, "delta", None],
        ["e6c", "bissector_vertical", 6, 4, "mu gamma", None],
        ["e6c", "constant_phi_vertical", 6, 3, "mu phi gamma", None],
        ["e6c", "psi_constant_horizontal", 6, 4, "mu delta", None],
        ["e6c", "psi_constant_vertical", 6, 4, "mu gamma", None],

        ["tardis", "bissector_horizontal", 6, 5, "delta", "gamma"],
        ["tardis", "bissector_vertical", 6, 4, "mu gamma", "theta delta"],
        ["tardis", "constant_phi_vertical", 6, 3, "mu phi gamma", "theta phi delta"],
        ["tardis", "psi_constant_horizontal", 6, 4, "mu delta", "theta gamma"],
        ["tardis", "psi_constant_vertical", 6, 4, "mu gamma", "theta delta"],
        ["tardis", "constant_chi_vertical", 6, 3, "mu chi gamma", "theta chi delta"],
        ["tardis", "constant_mu_horizontal", 6, 3, "mu omega delta", "theta omega gamma"],
        ["tardis", "constant_omega_vertical", 6, 3, "mu omega gamma", "theta omega delta"],
        ["tardis", "double_diffraction_horizontal", 6, 4, "omega delta", "omega gamma"],
        ["tardis", "double_diffraction_vertical", 6, 4, "mu gamma", "theta delta"],
        ["tardis", "lifting_detector_mu", 6, 3, "omega chi phi", "omega chi phi"],
        ["tardis", "lifting_detector_omega", 6, 3, "mu chi phi", "theta chi phi"],
        ["tardis", "lifting_detector_phi", 6, 3, "mu omega chi", "theta omega chi"],

        ["k4cv", "bissector", 4, 4, "", None],
        ["k4cv", "constant_chi", 4, 4, "", None],
        ["k4cv", "constant_omega", 4, 4, "", None],
        ["k4cv", "constant_phi", 4, 4, "", None],
        ["k4cv", "psi_constant", 4, 4, "", None],
        ["k4cv", "double_diffraction", 4, 4, "", None],

        ["k6c", "bissector_horizontal", 6, 5, "delta", None],
        ["k6c", "bissector_vertical", 6, 4, "mu gamma", None],
        ["k6c", "constant_incidence", 6, 5, "mu", None],
        ["k6c", "constant_kphi_horizontal", 6, 4, "kphi delta", None],
        ["k6c", "constant_omega_vertical", 6, 4, "mu gamma", None],
        ["k6c", "constant_phi_horizontal", 6, 5, "delta", None],
        ["k6c", "constant_phi_vertical", 6, 4, "mu gamma", None],
        ["k6c", "double_diffraction_horizontal", 6, 5, "delta", None],
        ["k6c", "double_diffraction_vertical", 6, 4, "mu gamma", None],
        ["k6c", "lifting_detector_komega", 6, 3, "mu kappa kphi", None],
        ["k6c", "lifting_detector_kphi", 6, 3, "mu komega kappa", None],
        ["k6c", "lifting_detector_mu", 6, 3, "komega kappa kphi", None],
        ["k6c", "psi_constant_vertical", 6, 4, "mu gamma", None],
        # fmt: on
    ],
)
def test_engine_axes(dname, mode, n_r, n_w, e_a_c, c_a_c, e4cv, e4cv_renamed, e6c, k4cv, k6c, tardis):
    diffractometer_choices = dict(e4cv=e4cv, e4cv_renamed=e4cv_renamed, e6c=e6c, k4cv=k4cv, k6c=k6c, tardis=tardis)
    assert dname in diffractometer_choices

    dfrctmtr = diffractometer_choices[dname]
    calc = dfrctmtr.calc
    engine = calc.engine

    assert mode in engine.modes
    engine.mode = mode  # tests below apply to this engine and mode

    # engine: canonical names
    assert len(engine.axes_r) == n_r
    assert len(engine.axes_w) == n_w
    assert engine.axes_c == e_a_c.split()  # e_a_c : engine axes_c

    # calc: user names (might be renamed from canonical)
    assert len(calc.axes_r) == n_r
    assert len(calc.axes_w) == n_w
    assert calc.axes_c == (c_a_c or e_a_c).split()  # c_a_c : calc axes_c
