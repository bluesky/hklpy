"""
Save and restore Diffractometer Configuration.

.. autosummary::

    ~DiffractometerConfiguration
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
EXPECTED_CONFIGURATION_KEYS_TYPES = {
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
            raise ValueError(
                f"fmt must be one of {EXPORT_FORMATS}, received {fmt!r}"
            )
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
        from .util import Constraint

        assert isinstance(self.diffractometer, Diffractometer)

        self.diffractometer.wavelength = DEFAULT_WAVELENGTH
        self.diffractometer.engine.mode = self.diffractometer.engine.modes[0]

        # fmt: off
        self.diffractometer._set_constraints(
            {
                k: Constraint(-180, 180, 0.0, True)
                for k in self.real_axes_names
            }
        )
        # fmt: on

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
        assert isinstance(diffractometer, Diffractometer)
        assert isinstance(config, dict)

        for k, types in EXPECTED_CONFIGURATION_KEYS_TYPES.items():
            assert k in config, f"Missing required parameter, {k}"
            assert isinstance(config[k], types), f"Bad value type for parameter, {k}"

        calc = diffractometer.calc  # shortcut
        assert config["canonical_axes"] == self.canonical_axes_names
        assert config["engine"] == calc.engine.name
        assert config["geometry"] == calc._geometry.name_get()
        assert config["library"].split()[0] == libhkl.__name__
        assert config["reciprocal_axes"] == self.reciprocal_axes_names

        for k, constraint in config["constraints"].items():
            # fmt: off
            assert k in self.real_axes_names, (
                f"{k} not in {self.real_axes_names=}"
            )
            # fmt: on
            assert isinstance(constraint, dict)
            for k2 in "low_limit high_limit value fit".split():
                assert k2 in constraint
                if k2 == "fit":
                    assert isinstance(constraint[k2], bool)
                else:
                    assert isinstance(constraint[k2], (float, int))

        for sample in config["samples"].values():
            self.validate_config_dict_sample(sample)

    def validate_config_dict_sample(self, sample):
        """
        Validate a sample dictionary in the configuration.

        PARAMETERS

        sample *dict*:
            structure (dict) with sample configuration
        """
        assert "lattice" in sample
        assert isinstance(sample["lattice"], dict)
        for k in "a b c alpha beta gamma".split():
            assert k in sample["lattice"]
            assert isinstance(sample["lattice"][k], (float, int))

        # fmt: off
        assert "reflections" in sample, (
            f"sample {sample['name']} must have"
            " reflections list, even if it is empty."
        )
        assert isinstance(sample["reflections"], list), (
            "reflections must be a list"
        )
        for reflection in sample["reflections"]:
            self.validate_config_dict_sample_reflection(reflection)

        for k in "U UB".split():
            arr = sample.get(k, [])
            if len(arr) > 0:
                assert numpy.array(arr).shape == (3, 3), f"{k} must be 3x3"
                assert isinstance(arr[0][0], (float, numpy.floating)), (
                    f"{k} must be numeric"
                )
        # fmt: on

    def validate_config_dict_sample_reflection(self, reflection):
        """
        Validate a reflection dictionary in the configuration.

        PARAMETERS

        reflection *dict*:
            structure (dict) with reflection configuration
        """
        # fmt: off
        assert isinstance(reflection.get("flag"), int), (
            "'flag' must be int"
        )
        assert isinstance(
            reflection.get("wavelength"), (float, int)
        ), (
            "'wavelength' must be numeric"
        )
        assert isinstance(
            reflection.get("orientation_reflection"), bool
        ), (
            # TODO: or integer, in the future
            "'orientation_reflection' must be True or False"
        )

        groups = [
            ["reflection", "reciprocal", self.reciprocal_axes_names],
            ["position", "real", self.canonical_axes_names],
        ]
        for key, desc, names in groups:
            arr = reflection.get(key)
            assert isinstance(arr, dict), (
                f"{desc}-space coordinates must be a dict"
            )
            for k, v in arr.items():
                assert k in names, f"{k!r} not in {names}"
                assert isinstance(v, (float, int)), (
                    f"{desc}-space {k!r} value must be a number, got {v}"
                )
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
                # TODO: try..except..finally?
                w0 = self.diffractometer.calc.wavelength
                self.diffractometer.calc.wavelength = reflection["wavelength"]
                r = self.diffractometer.calc.sample.add_reflection(*args)
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
        assert isinstance(me, Diffractometer)

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

    def to_json(self):
        """Report diffractometer configuration as JSON text."""
        return json.dumps(self.to_dict(), indent=4)

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

    def to_yaml(self):
        """Report diffractometer configuration as YAML text."""
        return yaml.dump(self.to_dict(), indent=4, sort_keys=False)

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
