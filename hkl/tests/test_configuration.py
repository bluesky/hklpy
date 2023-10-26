import pytest

from .. import DiffractometerConfiguration
from ..configuration import EXPECTED_CONFIGURATION_KEYS_TYPES
from ..configuration import EXPORT_FORMATS


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
    before = config.export()
    config.restore(before)
    assert before == config.export(), "should be same configuration"

    with pytest.raises(ValueError):
        # cannot restore k4cv config to e4cv diffractometer
        config.restore(DiffractometerConfiguration(k4cv).export())
    assert before == config.export(), "configuration should be unchanged"


@pytest.mark.parametrize("fmt", [None] + EXPORT_FORMATS)
def test_format(fmt, e4cv):
    """Test the various export formats can be imported."""
    config = DiffractometerConfiguration(e4cv)
    cfg = config.export(fmt)
    assert isinstance(cfg, (dict, str)), f"{cfg=}"

    class TestNoException(Exception):
        """Raised when test has not had any exceptions."""

    with pytest.raises(TestNoException):
        # first, test restore by known type
        if fmt in [None, "json"]:
            config.from_json(cfg)  # default format
        elif fmt == "dict":
            config.from_dict(cfg)
        elif fmt == "yaml":
            config.from_yaml(cfg)
        else:
            raise TypeError(f"Unexpected configuration type: {type(cfg)}")
        config.restore(cfg)  # test restore with automatic type recognition

        raise TestNoException()


@pytest.mark.parametrize(
    "action, key, value, failure",
    # remove each of the expected keys, individually
    [["rm", k, None, AssertionError] for k in EXPECTED_CONFIGURATION_KEYS_TYPES]
    # set each of the expected keys, individually, to invalid value
    + [["set", k, object, AssertionError] for k in EXPECTED_CONFIGURATION_KEYS_TYPES],
)
def test_validation_fails(action, key, value, failure, tardis):
    assert len(tardis.calc._samples) == 1
    assert tardis.calc.sample.name == "main"

    with pytest.raises(AssertionError):
        cfg = DiffractometerConfiguration("wrong diffractometer object")
        cfg.validate_config_dict({})

    with pytest.raises(AssertionError):
        cfg = DiffractometerConfiguration(tardis)
        cfg.validate_config_dict("wrong configuration object")

    with pytest.raises(failure):
        cfg = DiffractometerConfiguration(tardis)
        assert isinstance(cfg, dict)

        if action == "rm":
            cfg.pop(key)
        elif action == "set":
            cfg[key] = value
        cfg.validate_config_dict(cfg)


# TODO: test sample dictionary
# TODO: test reflections dictionary
