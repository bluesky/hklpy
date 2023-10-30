import pathlib
from contextlib import nullcontext as does_not_raise
from dataclasses import MISSING

import pytest
from apischema import ValidationError
from apischema import deserialize
from apischema import serialize

from .. import DiffractometerConfiguration
from ..configuration import EXPORT_FORMATS
from ..configuration import DCConfiguration
from ..configuration import DCConstraint
from ..configuration import DCLattice
from ..configuration import DCReflection
from ..configuration import DCSample


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


@pytest.mark.parametrize("file", [None, "data/e4c-config.json"])  # default or restored config
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
        with open(path) as f:
            agent.restore(f.read())

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


@pytest.mark.parametrize("key", "low_limit high_limit value".split())
# fit is a boolean, existing validation testing is sufficient for now
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
    data = {
        "low_limit": 0.0,
        "high_limit": 0.0,
        "value": 0.0,
        "fit": True,
    }
    agent = deserialize(DCConstraint, data)
    assert isinstance(agent, DCConstraint)
    assert key in data

    data.pop(key)
    with pytest.raises(ValidationError):
        deserialize(DCConstraint, data)

    data[key] = value
    with failure:
        agent = deserialize(DCConstraint, data)
        assert isinstance(agent, DCConstraint)
        agent.validate(f"testing {key=}")


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
def test_DCLattice_fails(key, value, failure):
    data = {
        "a": 4,
        "b": 5,
        "c": 6,
        "alpha": 8,
        "beta": 9,
        "gamma": 10,
    }
    agent = deserialize(DCLattice, data)
    assert isinstance(agent, DCLattice)
    assert key in data

    data.pop(key)
    with pytest.raises(ValidationError):
        deserialize(DCConstraint, data)

    data[key] = value
    if key in "alpha beta gamma".split() and value > 180 - 1e-6:
        failure = pytest.raises(ValueError)
    with failure:
        agent = deserialize(DCLattice, data)
        assert isinstance(agent, DCLattice)
        agent.validate(f"testing {key=}")


# TODO: test sample dictionary
def test_DCReflection_fails():
    assert True  # TODO:


# TODO: test reflections dictionary
def test_DCSample_fails():
    assert True  # TODO:


# TODO: test that diffractometer is updated by config.restore()
# TODO: Test the `clear` flag for config.restore()
