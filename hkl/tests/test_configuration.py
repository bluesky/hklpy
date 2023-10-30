import pathlib
from contextlib import nullcontext as does_not_raise
from dataclasses import MISSING

import pytest
from apischema.validation.errors import ValidationError

from .. import DiffractometerConfiguration
from ..configuration import EXPORT_FORMATS
from ..configuration import DCConfiguration


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


# TODO: test sample dictionary
# TODO: test reflections dictionary
# TODO: test that diffractometer is updated by config.restore()
# TODO: Test the `clear` flag for config.restore()
