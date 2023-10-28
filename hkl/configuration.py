"""
Save and restore Diffractometer Configuration.

PUBLIC API

.. autosummary::

    ~DiffractometerConfiguration

PRIVATE API

.. autosummary::

    ~_check_key
    ~_check_type
    ~_check_value
"""

__all__ = [
    "DiffractometerConfiguration",
]

import datetime
import json
from dataclasses import dataclass

import numpy
import yaml

DEFAULT_WAVELENGTH = 1.54  # angstrom
EXPORT_FORMATS = "dict json yaml".split()
REQUIRED_CONFIGURATION_KEYS_TYPES = {
    "name": str,
    "geometry": str,
    "datetime": str,
    "class": str,
    "engine": str,
    "mode": str,
    "hklpy_version": str,
    "library": str,
    "energy_keV": (int, float),
    "wavelength_angstrom": (int, float),
    "constraints": dict,
    "samples": dict,
    "canonical_axes": list,
    "real_axes": list,
    "reciprocal_axes": list,
}


def _check_key(key, biblio, words):
    """Raise KeyError if actual is not in expected."""
    if key not in biblio:
        raise KeyError(f"{words}:  expected {key!r} not in {biblio}")


def _check_type(actual, expected, words):
    """Raise TypeError if actual is not an instance of expected."""
    if not isinstance(actual, expected):
        raise TypeError(f"{words}:  received: {actual}  expected: {expected}")


def _check_value(actual, expected, words):
    """Raise ValueError if actual is not equal to expected."""
    if actual != expected:
        raise ValueError(f"{words}:  received: {actual}  expected: {expected}")


@dataclass
class DiffractometerConfiguration:
    """
    Save and restore Diffractometer Configuration.

    .. autosummary::

        ~export
        ~restore
        ~_update
        ~validate_config_dict
        ~reset_diffractometer
        ~reset_diffractometer_constraints
        ~reset_diffractometer_samples
        ~from_dict
        ~from_json
        ~from_yaml
        ~to_dict
        ~to_json
        ~to_yaml
        ~canonical_axes_names
        ~real_axes_names
        ~reciprocal_axes_names
    """

    from .diffract import Diffractometer

    diffractometer: Diffractometer

    def export(self, fmt="json"):
        """
        Export configuration in a recognized format (dict, json, yaml).

        PARAMETERS

        fmt *str*:
            One of these: ``None``, ``"dict"``, ``"json"``, ``"yaml"``. If
            ``None`` (or empty string or no argument at all), then JSON will be
            the default.
        """
        fmt = (fmt or "json").lower()
        if fmt == "yml":
            fmt = "yaml"  # a common substitution, just being friendly
        if fmt not in EXPORT_FORMATS:
            raise ValueError(f"fmt must be one of {EXPORT_FORMATS}, received {fmt!r}")
        return getattr(self, f"to_{fmt}")()

    def restore(self, config, clear=True):
        """
        Restore configuration from a recognized format (dict, json, yaml).

        Instead of guessing, recognize the kind of config data by its structure.

        PARAMETERS

        config *dict* or *str*:
            structure (dict, json, or yaml) with diffractometer configuration
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.

        Note: Can't name this method "import", it's a reserved Python word.
        """
        importer = None

        if isinstance(config, dict):
            importer = self.from_dict
        elif isinstance(config, str):
            if config.strip().startswith("{"):
                importer = self.from_json
            else:
                importer = self.from_yaml
        if importer is None:
            raise TypeError("Unrecognized configuration structure.")

        importer(config, clear=clear)

    def reset_diffractometer(self):
        """Clear all diffractometer settings."""
        from .diffract import Diffractometer

        _check_type(self.diffractometer, Diffractometer, "diffractometer should be 'Diffractometer' or subclass.")

        self.diffractometer.wavelength = DEFAULT_WAVELENGTH
        self.diffractometer.engine.mode = self.diffractometer.engine.modes[0]
        self.reset_diffractometer_constraints()
        self.reset_diffractometer_samples()

    def reset_diffractometer_constraints(self):
        """Reset the diffractometer constraints to defaults."""
        from .util import Constraint

        # fmt: off
        self.diffractometer._set_constraints(
            {
                k: Constraint(-180., 180., 0.0, True)
                for k in self.real_axes_names
            }
        )
        # fmt: on

    def reset_diffractometer_samples(self):
        """Reset the diffractometer sample dict to defaults."""
        for k in list(self.diffractometer.calc._samples):
            self.diffractometer.calc._samples.pop(k)

        # fmt: off
        a0 = DEFAULT_WAVELENGTH  # coincidentally
        self.diffractometer.calc.new_sample(
            "main", lattice=(a0, a0, a0, 90., 90., 90.)
        )
        # fmt: on

    def validate_config_dict(self, config):
        """
        Verify that the config dictionary is correctly formed.

        PARAMETERS

        config *dict*:
            structure (dict) with diffractometer configuration
        """
        from .diffract import Diffractometer
        from .util import libhkl

        diffractometer = self.diffractometer

        _check_type(self.diffractometer, Diffractometer, "diffractometer should be 'Diffractometer' or subclass.")
        _check_type(config, dict, "config")

        for k, types in REQUIRED_CONFIGURATION_KEYS_TYPES.items():
            _check_key(k, config, "missing key")
            _check_type(config[k], types, f"Wrong type for parameter, {k}")

        calc = diffractometer.calc
        _check_value(
            config["canonical_axes"],
            self.canonical_axes_names,
            "canonical_axes",
        )
        _check_value(config["engine"], calc.engine.name, "engine")
        _check_value(config["geometry"], calc._geometry.name_get(), "geometry")
        _check_value(config["library"], libhkl.__name__, "library")
        _check_value(config["reciprocal_axes"], self.reciprocal_axes_names, "reciprocal_axes")

        for k, constraint in config["constraints"].items():
            _check_key(k, self.real_axes_names, "missing key")
            _check_type(constraint, dict, f"{constraint}")
            for k2 in "low_limit high_limit value fit".split():
                _check_key(k2, constraint, "missing key")
                if k2 == "fit":
                    _check_type(constraint[k2], bool, f"{constraint[k2]}")
                else:
                    _check_type(constraint[k2], (float, int), f"{constraint[k2]}")

        for sample in config["samples"].values():
            self.validate_config_dict_sample(sample)

    def validate_config_dict_sample(self, sample):
        """
        Validate a sample dictionary in the configuration.

        PARAMETERS

        sample *dict*:
            structure (dict) with sample configuration
        """
        _check_key("lattice", sample, "missing key")
        _check_type(sample["lattice"], dict, "sample lattice")
        for k in "a b c alpha beta gamma".split():
            _check_key(k, sample["lattice"], "missing key")
            _check_type(sample["lattice"][k], (float, int), f"{k}")

        _check_key("reflections", sample, f"sample {sample['name']} reflections list required, even if empty")
        _check_type(sample["reflections"], list, f"sample {sample['name']} reflections")
        for reflection in sample["reflections"]:
            self.validate_config_dict_sample_reflection(reflection)

        for k in "U UB".split():
            arr = sample.get(k, [])
            if len(arr) > 0:
                _check_value(numpy.array(arr).shape, (3, 3), f"{k} must be 3x3")
                _check_type(arr[0][0], (float, numpy.floating), f"{k} must be numeric")

    def validate_config_dict_sample_reflection(self, reflection):
        """
        Validate a reflection dictionary in the configuration.

        PARAMETERS

        reflection *dict*:
            structure (dict) with reflection configuration
        """
        _check_type(reflection.get("fit"), int, "fit")
        _check_type(reflection.get("wavelength"), (float, int), "wavelength")
        _check_type(reflection.get("orientation_reflection"), bool, "orientation_reflection")

        groups = [
            ["reflection", "reciprocal", self.reciprocal_axes_names],
            ["position", "real", self.canonical_axes_names],
        ]
        for key, desc, names in groups:
            arr = reflection.get(key)
            _check_type(arr, dict, f"{desc}-space coordinates")
            for k, v in arr.items():
                _check_key(k, names, f"{k!r} not in {names}")
                _check_type(v, (float, int), f"{desc}-space {k!r} value")
        # fmt: on

    def _update(self, config):
        """Update diffractometer with configuration."""
        from .util import Constraint

        # don't reset the wavelength
        self.diffractometer.engine.mode = config["mode"]

        # fmt: off
        self.diffractometer._set_constraints(
            {
                k: Constraint(
                    constraint["low_limit"],
                    constraint["high_limit"],
                    constraint["value"],
                    constraint["fit"],
                )
                for k, constraint in config["constraints"].items()
            }
        )
        # fmt: on

        for k, sample in config["samples"].items():
            lattice_tuple = (
                sample["lattice"]["a"],
                sample["lattice"]["b"],
                sample["lattice"]["c"],
                sample["lattice"]["alpha"],
                sample["lattice"]["beta"],
                sample["lattice"]["gamma"],
            )

            s = self.diffractometer.calc._samples.get(k)
            if s is None:
                s = self.diffractometer.calc.new_sample(k, lattice=lattice_tuple)
            else:
                s.lattice = lattice_tuple

            # reflections
            reflection_list = []
            for reflection in sample["reflections"]:
                # fmt: off
                args = [
                    reflection["reflection"][nm]
                    for nm in self.reciprocal_axes_names
                ]
                positions = tuple([
                    reflection["position"][nm]
                    for nm in self.canonical_axes_names
                ])
                args = [*args, positions]  # [h, k, l, (m1, m2, m3, ...)]
                # fmt: on

                # temporarily, change the wavelength
                w0 = self.diffractometer.calc.wavelength
                try:
                    self.diffractometer.calc.wavelength = reflection["wavelength"]
                    r = self.diffractometer.calc.sample.add_reflection(*args)
                except RuntimeError as exc:
                    print(f"RuntimeError when adding reflection({args}): {exc}")
                finally:
                    self.diffractometer.calc.wavelength = w0

                if reflection["orientation_reflection"]:
                    reflection_list.append(r)
            if len(reflection_list) > 1:
                r1, r2 = reflection_list[:2]
                self.diffractometer.calc.sample.compute_UB(r1, r2)

    def from_dict(self, config, clear=True):
        """
        Restore diffractometer configuration from Python dictionary.

        PARAMETERS

        config *dict*:
            structure (dict) with diffractometer configuration
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.
        """
        try:
            self.validate_config_dict(config)
        except AssertionError as exc:
            raise ValueError(f"Cannot restore: {exc!r}")

        if clear:
            self.reset_diffractometer()

        self._update(config)

    def to_dict(self):
        """Report diffractometer configuration as Python dictionary."""
        from .diffract import Diffractometer
        from .util import libhkl

        me = self.diffractometer
        _check_type(me, Diffractometer, "diffractometer should be 'Diffractometer' or subclass.")

        d = {
            "name": me.name,
            "geometry": me.calc._geometry.name_get(),
            "datetime": str(datetime.datetime.now()),
            "class": me.__class__.__name__,
            "engine": me.calc.engine.name,
            "mode": me.calc.engine.mode,
            "hklpy_version": me._hklpy_version_,
            "library": libhkl.__name__,
            "library_version": libhkl.VERSION,
            "energy_keV": me.calc.energy,
            "wavelength_angstrom": me.calc.wavelength,
            # fmt: off
            "constraints": {
                k: {
                    nm: getattr(v, nm)
                    for nm in "low_limit high_limit value fit".split()
                }
                for k, v in me._constraints_dict.items()
            },
            "samples": {
                sname: {
                    "name": sample.name,
                    "lattice": sample.lattice._asdict(),
                    "reflections": sample.reflections_details,
                    "U": sample.U.tolist(),
                    "UB": sample.UB.tolist(),
                }
                for sname, sample in me.calc._samples.items()
            },
            # fmt: on
            "canonical_axes": self.canonical_axes_names,
            "real_axes": self.real_axes_names,
            "reciprocal_axes": self.reciprocal_axes_names,
        }
        return d

    def from_json(self, text, clear=True):
        """
        Restore diffractometer configuration from JSON text.

        PARAMETERS

        config *str* (JSON):
            structure (JSON string) with diffractometer configuration
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.
        """
        self.from_dict(json.loads(text), clear=clear)

    def to_json(self, indent=4):
        """Report diffractometer configuration as JSON text."""
        return json.dumps(self.to_dict(), indent=indent)

    def from_yaml(self, text, clear=True):
        """
        Restore diffractometer configuration from YAML text.

        PARAMETERS

        config *str* (YAML):
            structure (YAML string) with diffractometer configuration
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.
        """
        self.from_dict(yaml.load(text, Loader=yaml.Loader), clear=clear)

    def to_yaml(self, indent=4, sort_keys=False):
        """Report diffractometer configuration as YAML text."""
        return yaml.dump(self.to_dict(), indent=indent, sort_keys=sort_keys)

    @property
    def canonical_axes_names(self):
        """Names of the real-space axes, defined by the back-end library."""
        return self.diffractometer.calc._geometry.axis_names_get()

    @property
    def real_axes_names(self):
        """Names of the real-space axes, defined by the user."""
        return list(self.diffractometer.RealPosition._fields)

    @property
    def reciprocal_axes_names(self):
        """
        Names of the reciprocal-space axes, defined by the back-end library.
        """
        return list(self.diffractometer.PseudoPosition._fields)
