import pathlib
from contextlib import nullcontext as does_not_raise
from dataclasses import MISSING

import pytest
from apischema import ValidationError
from apischema import deserialize

from .. import DiffractometerConfiguration
from ..configuration import EXPORT_FORMATS
from ..configuration import DCConfiguration
from ..configuration import DCConstraint
from ..configuration import DCLattice
from ..configuration import DCReflection
from ..configuration import DCSample
from ..util import Constraint
from ..util import new_lattice
from .tools import TWO_PI

TEST_CONFIG_FILE = "data/e4c-config.json"


def test_e4cv(e4cv):
    assert e4cv is not None


def test_axes_names(e4cv, e4cv_renamed):
    c_e4cv = DiffractometerConfiguration(e4cv)
    c_e4cv_renamed = DiffractometerConfiguration(e4cv_renamed)
    assert c_e4cv.canonical_axes_names == c_e4cv_renamed.canonical_axes_names
    assert c_e4cv.real_axes_names != c_e4cv_renamed.real_axes_names
    assert c_e4cv.reciprocal_axes_names == c_e4cv_renamed.reciprocal_axes_names


def test_restore(e4cv_renamed, k4cv):
    config = DiffractometerConfiguration(e4cv_renamed)
    before = config.export("dict")
    config.restore(before)
    after = config.export("dict")
    assert before != after, "datetime difference"

    before.pop("datetime")
    after.pop("datetime")
    assert before == after, "should be same configuration"

    with pytest.raises(ValueError):
        # cannot restore k4cv config to e4cv diffractometer
        config.restore(DiffractometerConfiguration(k4cv).export())
    after = config.export("dict")
    after.pop("datetime")
    assert before == after, "configuration should be unchanged"


@pytest.mark.parametrize("fmt", [None] + EXPORT_FORMATS)
def test_format(fmt, e4cv):
    """Verify that various export formats can be imported."""
    config = DiffractometerConfiguration(e4cv)
    with does_not_raise():
        cfg = config.export(fmt)
    assert isinstance(cfg, (dict, str)), f"{cfg=}"

    with does_not_raise():
        # first, test restore by known type
        if fmt in [None, "json"]:
            config.from_json(cfg)  # default format
        elif fmt == "dict":
            config.from_dict(cfg)
        elif fmt == "yaml":
            config.from_yaml(cfg)
        else:
            raise ValueError(f"Unrecognized configuration format: {fmt}")
        config.restore(cfg)  # test restore with automatic type recognition


@pytest.mark.parametrize("file", [None, TEST_CONFIG_FILE])  # default or restored config
@pytest.mark.parametrize("action", "rm set".split())  # remove or set keys incorrectly
@pytest.mark.parametrize(
    "key, value, failure",  # fmt: off
    [
        [k, object, (KeyError, TypeError, ValidationError, ValueError)]
        for k in DCConfiguration.__dataclass_fields__
    ],  # fmt: off
)
def test_validation_fails(file, action, key, value, failure, e4cv):
    agent = DiffractometerConfiguration(e4cv)
    assert isinstance(agent, DiffractometerConfiguration), f"{agent}"

    if file is not None:
        path = pathlib.Path(__file__).parent / file
        assert path.exists(), f"{path}"
        agent.restore(path)

    data = agent.export("dict")
    assert isinstance(data, dict), f"{type(data)=}"

    if action == "rm":
        data.pop(key)
        # Determine if key is optional (default/factory is defined).  Empirical.
        attr = DCConfiguration.__dataclass_fields__[key]
        if attr.default_factory != MISSING or attr.default != MISSING:
            failure = None  # OK if not provided
    elif action == "set":
        data[key] = value

    if failure is None:
        agent.restore(data)
    else:
        with pytest.raises(failure):
            agent.restore(data)


def common_DC_dataclass_tests(dc_class, data, key, value, failure, val_arg):
    """Code used to test the DCxyz classes."""
    agent = deserialize(dc_class, data)
    assert isinstance(agent, dc_class)
    assert key in data

    # Is key an optional attribute?
    context = pytest.raises(ValidationError)
    attr = dc_class.__dataclass_fields__[key]
    if attr.default_factory != MISSING or attr.default != MISSING:
        context = does_not_raise()

    data.pop(key)
    with context:
        deserialize(dc_class, data)

    data[key] = value
    with failure:
        agent = deserialize(dc_class, data)
        assert isinstance(agent, dc_class)
        agent.validate(val_arg)


@pytest.mark.parametrize("key", "low_limit high_limit value".split())
@pytest.mark.parametrize(
    "value, failure",
    [
        [-360.01, pytest.raises(ValueError)],
        [-360, does_not_raise()],
        [0, does_not_raise()],
        [360, does_not_raise()],
        [360.01, pytest.raises(ValueError)],
        ["0", pytest.raises(ValidationError)],
    ],
)
def test_DCConstraint_fails(key, value, failure):
    # all attributes are required
    # fmt: off
    data = {
        "low_limit": 0.0,
        "high_limit": 0.0,
        "value": 0.0,
        "fit": True,
    }
    common_DC_dataclass_tests(
        DCConstraint, data, key, value, failure, f"testing DCConstraint.{key=}"
    )
    # fmt: on


@pytest.mark.parametrize("key", "a b c alpha beta gamma".split())
@pytest.mark.parametrize(
    "value, failure",
    [
        [-1, pytest.raises(ValueError)],
        [0, pytest.raises(ValueError)],
        [1e-7, pytest.raises(ValueError)],
        [1, does_not_raise()],
        [179.99, does_not_raise()],
        [180, does_not_raise()],
        [10_000, does_not_raise()],
        [100_000_000, pytest.raises(ValueError)],
    ],
)
def test_DCLattice_fails(key, value, failure, e4cv):
    data = {
        "a": 4,
        "b": 5,
        "c": 6,
        "alpha": 8,
        "beta": 9,
        "gamma": 10,
    }
    if key in "alpha beta gamma".split() and value > 180 - 1e-6:
        failure = pytest.raises(ValueError)

    agent = DiffractometerConfiguration(e4cv)
    common_DC_dataclass_tests(DCLattice, data, key, value, failure, agent)


@pytest.mark.parametrize(
    "key, value, failure",
    [
        ["wavelength", -1, pytest.raises(ValueError)],
        ["wavelength", 0, pytest.raises(ValueError)],
        ["wavelength", 0.01, does_not_raise()],
        ["wavelength", 500, does_not_raise()],
        ["wavelength", 1_000_000.0, does_not_raise()],
        ["wavelength", 100_000_000, pytest.raises(ValueError)],
        ["reflection", {"h": 12.4, "k": 0, "l": 0}, does_not_raise()],
        ["reflection", {"h": 0, "k": 12.4, "l": 0}, does_not_raise()],
        ["reflection", {"h": 0, "k": 0, "l": 12.4}, does_not_raise()],
        ["reflection", {"h": -12.4, "k": 0, "l": 0}, does_not_raise()],
        ["reflection", {"h": 0, "k": -12.4, "l": 0}, does_not_raise()],
        ["reflection", {"h": 0, "k": 0, "l": -12.4}, does_not_raise()],
        ["reflection", {"h": 20_000, "k": 0, "l": 0}, pytest.raises(ValueError)],
        ["reflection", {"h": -20_000, "k": 0, "l": 0}, pytest.raises(ValueError)],
        ["reflection", {"h": 0, "k": 20_000, "l": 0}, pytest.raises(ValueError)],
        ["reflection", {"h": 0, "k": -20_000, "l": 0}, pytest.raises(ValueError)],
        ["reflection", {"h": 0, "k": 0, "l": 20_000}, pytest.raises(ValueError)],
        ["reflection", {"h": 0, "k": 0, "l": -20_000}, pytest.raises(ValueError)],
        ["position", {"omega": 360, "chi": 0, "phi": 0, "tth": 0}, does_not_raise()],
        ["position", {"omega": 0, "chi": 360, "phi": 0, "tth": 0}, does_not_raise()],
        ["position", {"omega": 0, "chi": 0, "phi": 360, "tth": 0}, does_not_raise()],
        ["position", {"omega": 0, "chi": 0, "phi": 0, "tth": 360}, does_not_raise()],
        ["position", {"omega": -360, "chi": 0, "phi": 0, "tth": 0}, does_not_raise()],
        ["position", {"omega": 0, "chi": -360, "phi": 0, "tth": 0}, does_not_raise()],
        ["position", {"omega": 0, "chi": 0, "phi": -360, "tth": 0}, does_not_raise()],
        ["position", {"omega": 0, "chi": 0, "phi": 0, "tth": -360}, does_not_raise()],
        ["position", {"omega": 360.01, "chi": 0, "phi": 0, "tth": 0}, pytest.raises(ValueError)],
        ["position", {"omega": 0, "chi": 360.01, "phi": 0, "tth": 0}, pytest.raises(ValueError)],
        ["position", {"omega": 0, "chi": 0, "phi": 360.01, "tth": 0}, pytest.raises(ValueError)],
        ["position", {"omega": 0, "chi": 0, "phi": 0, "tth": 360.01}, pytest.raises(ValueError)],
        ["position", {"omega": -360.01, "chi": 0, "phi": 0, "tth": 0}, pytest.raises(ValueError)],
        ["position", {"omega": 0, "chi": -360.01, "phi": 0, "tth": 0}, pytest.raises(ValueError)],
        ["position", {"omega": 0, "chi": 0, "phi": -360.01, "tth": 0}, pytest.raises(ValueError)],
        ["position", {"omega": 0, "chi": 0, "phi": 0, "tth": -360.01}, pytest.raises(ValueError)],
    ],
)
def test_DCReflection_fails(key, value, failure, e4cv):
    data = {
        "reflection": {"h": 0, "k": 0, "l": 0},
        "position": {"omega": 0, "chi": 0, "phi": 0, "tth": 0},
        "wavelength": 1,
        "orientation_reflection": True,
    }
    agent = DiffractometerConfiguration(e4cv)
    common_DC_dataclass_tests(DCReflection, data, key, value, failure, agent)


@pytest.mark.parametrize(
    "key, value, failure",
    [
        ["name", "", pytest.raises(ValueError)],
        ["name", "   ", pytest.raises(ValueError)],
        ["lattice", object, pytest.raises(TypeError)],
        ["lattice", {}, pytest.raises(ValidationError)],
        ["lattice", {"error", object}, pytest.raises(TypeError)],
        ["reflections", [object], pytest.raises(TypeError)],
        ["U", [object], pytest.raises(TypeError)],
        ["UB", [object], pytest.raises(TypeError)],
        ["U", [[1, 0, object], [0, 0, 0], [0, 0, 0]], pytest.raises(TypeError)],
        ["UB", [[1, 0, object], [0, 0, 0], [0, 0, 0]], pytest.raises(TypeError)],
        ["U", [[1, 0, 0], [0, 0, 0]], pytest.raises(ValueError)],
        ["UB", [[1, 0, 0], [0, 0, 0]], pytest.raises(ValueError)],
    ],
)
def test_DCSample_fails(key, value, failure, e4cv):
    data = {
        "name": "vibranium",
        "lattice": {"a": 4, "b": 4, "c": 4, "alpha": 90, "beta": 90, "gamma": 90},
        "reflections": [],
        "U": [[1.0, 0.0, 0.0], [0.0, 1.0, 1.0], [0.0, 0.0, 1.0]],
        "UB": [[TWO_PI, 0.0, 0.0], [0.0, TWO_PI, 0.0], [0.0, 0.0, TWO_PI]],
    }
    agent = DiffractometerConfiguration(e4cv)
    common_DC_dataclass_tests(DCSample, data, key, value, failure, agent)


@pytest.mark.parametrize("clear", [True, False, object, None])
def test_diffractometer_restored(clear, e4cv):
    # -------------------------------- default configuration
    mode_default = e4cv.engine.mode
    positions_before = e4cv.RealPosition
    reciprocal_positions_before = e4cv.PseudoPosition
    constraints_default = e4cv._constraints_for_databroker

    assert round(e4cv.calc.wavelength, 2) == 1.55
    assert e4cv.engine.mode == mode_default
    assert len(e4cv.calc._samples) == 1
    assert e4cv.calc.sample.name == "main"
    assert len(e4cv.calc.sample.reflections_details) == 0

    # -------------------------------- perturb from the defaults
    mode_changed = e4cv.engine.modes[-1]
    constraints_test = {
        "omega": Constraint(-10, 80, 10, 1),
        "chi": Constraint(-10, 91, 45, 0),
        "phi": Constraint(-10, 91, 90, 0),
        "tth": Constraint(-10, 120, 20, 1),
    }
    wavelength_test = 0.25

    e4cv.engine.mode = mode_changed
    assert e4cv.engine.mode == mode_changed

    assert e4cv._constraints_for_databroker == constraints_default
    assert e4cv.calc.wavelength != wavelength_test

    e4cv.apply_constraints(constraints_test)
    constraints_changed = e4cv._constraints_for_databroker
    assert constraints_changed != constraints_default

    e4cv.calc.wavelength = wavelength_test
    assert e4cv.calc.wavelength == wavelength_test

    # modify the sample lattice
    orthorhombic = new_lattice(4, 5, 6)
    e4cv.calc.sample.lattice = orthorhombic
    assert e4cv.calc.sample.lattice == orthorhombic

    # add a reflection
    assert len(e4cv.calc.sample.reflections_details) == 0
    e4cv.calc.sample.add_reflection(0.1, 0, 0, (1, 2, 3, 4))
    assert len(e4cv.calc.sample.reflections_details) == 1

    # -------------------------------- restore config from file
    test_file = pathlib.Path(__file__).parent / TEST_CONFIG_FILE
    assert test_file.exists()

    agent = DiffractometerConfiguration(e4cv)
    full_config_before = agent.export("dict")
    context = does_not_raise()
    if not isinstance(clear, bool):
        context = pytest.raises(TypeError)
    with context:
        agent.restore(test_file, clear=clear)

    # -------------------------------- these should not have been changed
    assert e4cv.calc.wavelength == wavelength_test, "wavelength changed"
    assert e4cv.RealPosition == positions_before, "RealPosition changed"
    assert e4cv.PseudoPosition == reciprocal_positions_before, "PseudoPosition changed"

    # -------------------------------- changes conditional on clear

    full_config_after = agent.export("dict")
    full_config_before.pop("datetime")
    full_config_after.pop("datetime")

    if isinstance(clear, bool):
        assert full_config_after != full_config_before
        assert e4cv._constraints_for_databroker != constraints_default
        assert e4cv._constraints_for_databroker != constraints_changed
        # one additional sample
        assert len(e4cv.calc._samples) == 2
        assert list(e4cv.calc._samples) == "main vibranium".split()

        if clear:
            assert e4cv.engine.mode == mode_default
            assert e4cv.engine.mode != mode_changed
            assert e4cv.calc._samples["main"].lattice != orthorhombic
            assert len(e4cv.calc._samples["main"].reflections_details) == 0
        else:
            # switch samples
            e4cv.calc.sample = "vibranium"
            assert len(e4cv.calc.sample.reflections_details) == 3
            e4cv.calc.sample.lattice.a == TWO_PI
            e4cv.calc.sample.lattice.b == TWO_PI
            e4cv.calc.sample.lattice.c == TWO_PI
    else:
        # when restore() failed
        assert full_config_after == full_config_before
        assert len(e4cv.calc._samples) == 1
        assert list(e4cv.calc._samples) == "main".split()
        assert e4cv.engine.mode != mode_default
        assert e4cv.engine.mode == mode_changed
        assert e4cv.calc._samples["main"].lattice == orthorhombic
        assert len(e4cv.calc._samples["main"].reflections_details) == 1


@pytest.mark.parametrize("restore_constraints", [True, False, object, None])
def test_diffractometer_constraints_restored(restore_constraints, e4cv):
    """Are the constraints restored by option value?"""
    test_file = pathlib.Path(__file__).parent / TEST_CONFIG_FILE
    assert test_file.exists()

    agent = DiffractometerConfiguration(e4cv)
    constraints_before = agent.export("dict")["constraints"]

    context = does_not_raise()
    if not isinstance(restore_constraints, bool):
        context = pytest.raises(TypeError)
    with context:
        agent.restore(test_file, restore_constraints=restore_constraints)

    constraints_now = agent.export("dict")["constraints"]
    if isinstance(restore_constraints, bool) and restore_constraints:
        assert constraints_before != constraints_now
    else:
        assert constraints_before == constraints_now


def test_export_to_file(e4cv, tmp_path):
    """Can configuration be exported to file using pathlib object?"""
    assert isinstance(tmp_path, pathlib.Path)
    assert tmp_path.exists()

    path = tmp_path / "config.txt"
    assert not path.exists()

    agent = DiffractometerConfiguration(e4cv)
    agent.export(path)
    assert path.exists()

    agent.restore(path)  # just to be safe here


def test_constraints_stack(e4cv):
    """Ensure that restored constraints can be removed by undo."""
    agent = DiffractometerConfiguration(e4cv)
    constraints_before = agent.export("dict")["constraints"]

    test_file = pathlib.Path(__file__).parent / TEST_CONFIG_FILE
    assert test_file.exists()

    agent.restore(test_file)
    assert agent.export("dict")["constraints"] != constraints_before

    e4cv.undo_last_constraints()
    assert agent.export("dict")["constraints"] == constraints_before


def test_preview(e4cv):
    agent = DiffractometerConfiguration(e4cv)

    report = agent.preview(agent.export()).splitlines()
    assert report[0] == f"name: {e4cv.name}"
    assert report[2] == f"geometry: {e4cv.geometry_name.get()}"
    assert report[4] == "Table of Samples"
    assert "====" in report[5]
    assert "sample" in report[6]
    assert "main" in report[8]
    assert len(report) == 10

    report = agent.preview(agent.export(), show_reflections=True).splitlines()
    assert len(report) == 10  # no reflections, no new info

    report = agent.preview(agent.export(), show_constraints=True).splitlines()
    assert len(report) == 10 + 11  # new lines
    assert report[12] == "Table of Axis Constraints"
    assert "====" in report[13]
    assert "fit?" in report[14]
    assert report[16].startswith("omega")
    assert report[19].startswith("tth")

    main = e4cv.calc.sample  # the default sample
    m_100 = main.add_reflection(1, 0, 0, (-45, 0, 0, 0))
    m_010 = main.add_reflection(0, 1, 0, (45, 0, 0, 0))
    main.add_reflection(0, 0, 1, (45, 0, 90, 0))
    main.compute_UB(m_100, m_010)
    report = agent.preview(agent.export(), show_reflections=True).splitlines()
    assert len(report) == 10 + 10  # new lines
    assert report[12] == f"Table of Reflections for Sample: {main.name}"
    assert report[14].split()[1] == "h"
    assert report[14].split()[-3] == "tth"
    assert report[14].split()[-2] == "wavelength"
    assert report[14].split()[-1] == "orient?"
    assert report[16].split()[1] == "1"
    assert report[16].split()[2] == "0"
    assert report[16].split()[3] == "0"
    assert report[16].split()[-1] == "True"
    assert report[17].split()[1] == "0"
    assert report[17].split()[2] == "1"
    assert report[17].split()[3] == "0"
    assert report[17].split()[-1] == "True"
    assert report[18].split()[1] == "0"
    assert report[18].split()[2] == "0"
    assert report[18].split()[3] == "1"
    assert report[18].split()[-1] == "False"
