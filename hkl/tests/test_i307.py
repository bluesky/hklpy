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

    with interceptor as exinfo:
        sample.add_reflection(*args)
    if message is not None:
        assert message in str(exinfo.value)


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
