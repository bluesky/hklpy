"""
v2: Save and restore Diffractometer Configuration.

PUBLIC API

.. autosummary::

    ~DiffractometerConfiguration

PRIVATE API

.. autosummary::

    ~_check_key
    ~_check_type
    ~_check_value
    ~DCConstraint
    ~DCLattice
    ~DCReflection
    ~DCSample
    ~DCConfiguration
"""

__all__ = [
    "DiffractometerConfiguration",
]

import datetime
import json
from dataclasses import dataclass

import numpy
import yaml
from apischema import ValidationError
from apischema import deserialize
from apischema import serialize

from hkl.util import libhkl

# from apischema.json_schema import deserialization_schema


# TODO: can these be learned from the diffractometer? (not constraints but axes?)
AX_MIN = -360.0  # lowest allowed value for real-space axis
AX_MAX = 360.0  # highest allowed value for real-space axis

DEFAULT_WAVELENGTH = 1.54  # angstrom
EXPORT_FORMATS = "dict json yaml".split()


# standard value checks, raise exception(s) when appropriate
def _check_key(key, biblio, intro):
    """Raise KeyError if key is not in biblio."""
    if key not in biblio:
        raise KeyError(f"{intro}:  expected {key!r} not in {biblio}")


def _check_range(value, low, high, intro):
    """Raise ValueError if value is not between low & high."""
    if low > high:
        raise ValueError(f"{intro}:  {low} should not be greater than {high}")
    if not (low <= value <= high):
        raise ValueError(f"{intro}:  {value} is not between {low} & {high}")


def _check_type(actual, expected, intro):
    """Raise TypeError if actual is not an instance of expected."""
    if not isinstance(actual, intro):
        raise TypeError(f"{intro}:  received: {actual}  expected: {expected}")


def _check_value(actual, expected, intro):
    """Raise ValueError if actual is not equal to expected."""
    if actual != expected:
        raise ValueError(f"{intro}:  received: {actual}  expected: {expected}")


# DC classes: Diffractometer Configuration
# apischema: https://wyfo.github.io/apischema/0.18/


@dataclass
class DCConstraint:
    """Configuration of one diffractometer axis constraint."""

    low_limit: float
    high_limit: float
    value: float
    fit: bool

    @property
    def values(self):
        """Return the list of values in order."""
        return list(self.__dict__.values())

    def validate(self, cname):
        """
        Check this constraint has values the diffractometer can accept.

        Assumes diffractometer real axis limits of AX_MIN to AX_MAX degrees.
        """
        _check_range(self.low_limit, AX_MIN, AX_MAX, f"{cname} low_limit")
        _check_range(self.high_limit, AX_MIN, AX_MAX, f"{cname} high_limit")
        _check_range(self.value, AX_MIN, AX_MAX, f"{cname} value")
        # no additional validation needed for 'fit'


@dataclass
class DCLattice:
    """Configuration of one crystal lattice."""

    a: float
    b: float
    c: float
    alpha: float
    beta: float
    gamma: float

    def validate(self, config):
        """Check this lattice has values the diffractometer can accept."""
        for side in "a b c".split():
            _check_range(getattr(self, side), 1e-6, 1e6, f"side {side}")
        for angle in "alpha beta gamma".split():
            _check_range(getattr(self, angle), AX_MIN, AX_MAX, f"angle {angle}")

    @property
    def values(self):
        """Return the list of values in order."""
        return list(self.__dict__.values())


@dataclass
class DCReflection:
    """Configuration of one orientation reflection."""

    reflection: dict[str, float]
    position: dict[str, float]
    wavelength: float
    orientation_reflection: bool
    flag: int

    def validate(self, config):
        """Check this reflection has values the diffractometer can accept."""
        from hkl import A_KEV

        _check_range(self.wavelength, 1e-6, 1e6, "wavelength")
        energy = A_KEV / self.wavelength  # assumes X-rays
        q_max = energy  # physics: X-ray reciprocal-space won't stretch any further
        q_min = -q_max
        for axis, reflection in self.reflection.items():
            _check_key(axis, config.reciprocal_axes_names, f"reciprocal-space axis {axis}")
            _check_range(reflection["axis"], q_min, q_max, f"reciprocal-space axis {axis}")
        for axis, position in self.position.items():
            _check_key(axis, config.canonical_axes_names, f"real-space axis {axis}")
            _check_range(position["axis"], AX_MIN, AX_MAX, f"real-space axis {axis}")
        # TODO: How to validate 'flag'?


@dataclass
class DCSample:
    """Configuration of one sample."""

    name: str
    lattice: DCLattice
    reflections: list[DCReflection]
    U: list[list[float]]
    UB: list[list[float]]

    def validate(self, config):
        """Check this sample has values the diffractometer can accept."""
        self.lattice.validate(config)
        for reflection in self.reflections:
            reflection.validate(config)
        _check_value(numpy.array(self.U).shape, (3, 3), "U matrix shape")
        _check_value(numpy.array(self.UB).shape, (3, 3), "UB matrix shape")

    def write(self, diffractometer):
        """Write sample details to diffractometer."""
        lattice_parameters = list(self.lattice.values)

        s = diffractometer.calc._samples.get(self.name)
        if s is None:
            s = diffractometer.calc.new_sample(self.name, lattice=lattice_parameters)
        else:
            s.lattice = lattice_parameters

        for reflection in self.reflections:
            ...  # TODO:


@dataclass
class DCConfiguration:
    """Full structure of the diffractometer configuration."""

    name: str
    geometry: str
    datetime: str  # TODO: optional?
    python_class: str
    engine: str
    mode: str
    hklpy_version: str
    library: str
    library_version: str
    energy_keV: float  # assumes X-rays
    wavelength_angstrom: float
    constraints: dict[str, DCConstraint]
    samples: dict[str, DCSample]
    canonical_axes: list[str]
    real_axes: list[str]
    reciprocal_axes: list[str]

    def validate(self, config):  # TODO: refactor config to dc_bj and document it here & elsewhere
        """Check this configuration has values the diffractometer can accept."""
        diffractometer = config.diffractometer
        _check_value(self.geometry, diffractometer.calc._geometry.name_get(), "geometry")
        _check_value(self.library, libhkl.__name__, "library")
        _check_value(self.canonical_axes, config.canonical_axes_names, "canonical_axes")
        _check_value(self.reciprocal_axes, config.reciprocal_axes_names, "reciprocal_axes")
        _check_key(self.mode, diffractometer.engine.modes, "mode")

        for cname, constraint in self.constraints.items():
            _check_key(cname, config.canonical_axes_names, "constraint axis")
            constraint.validate(cname)

        for sname, sample in self.samples.items():
            sample.validate(self)

    def write(self, diffractometer):
        """Update diffractometer with configuration."""
        from .util import Constraint

        # don't reset the wavelength
        # don't reset the (real-space) positions
        # don't reset the (reciprocal-space) positions
        diffractometer.engine.mode = self.mode

        diffractometer._set_constraints(
            {k: Constraint(*constraint.values) for k, constraint in self.constraints.items()}
        )

        for sample in self.samples.values():
            sample.write(diffractometer)


class DiffractometerConfiguration:
    """
    Save and restore Diffractometer Configuration.
    """

    def __init__(self, diffractometer):
        from .diffract import Diffractometer

        if not isinstance(diffractometer, Diffractometer):
            raise TypeError("diffractometer should be 'Diffractometer' or subclass.")
        self.diffractometer = diffractometer

    def export(self):
        """
        Export configuration in a recognized format (dict, json, yaml).
        """

    def restore(self, config):
        """
        Restore configuration from a recognized format (dict, json, yaml).
        """

    @property
    def model(self):
        """Return diffractometer configuration as a DCConfiguration object."""
        me = self.diffractometer
        data = {
            "name": me.name,
            "geometry": me.calc._geometry.name_get(),
            "datetime": str(datetime.datetime.now()),
            "python_class": me.__class__.__name__,
            "engine": me.calc.engine.name,
            "mode": me.calc.engine.mode,
            "canonical_axes": self.canonical_axes_names,
            "real_axes": self.real_axes_names,
            "reciprocal_axes": self.reciprocal_axes_names,
            "energy_keV": me.calc.energy,  # assumes X-rays!
            "wavelength_angstrom": me.calc.wavelength,
            "hklpy_version": me._hklpy_version_,
            "library": libhkl.__name__,
            "library_version": libhkl.VERSION,
            "constraints": {
                axis: {parm: getattr(constraint, parm) for parm in "low_limit high_limit value fit".split()}
                for axis, constraint in me._constraints_dict.items()
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
        }
        return deserialize(DCConfiguration, data)  # also validates

    def reset_diffractometer(self):
        """Load configuration from Python dictionary."""
        self.diffractometer.wavelength = DEFAULT_WAVELENGTH
        self.diffractometer.engine.mode = self.diffractometer.engine.modes[0]
        self.reset_diffractometer_constraints()
        self.reset_diffractometer_samples()

    def reset_diffractometer_constraints(self):
        """Reset the diffractometer constraints to defaults."""
        from hkl.util import Constraint

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

    def to_dict(self, indent=4):
        """Load configuration from Python dictionary."""
        # return self.model.__dict__
        return serialize(DCConfiguration, self.model)

    def from_dict(self, config, clear=True):
        """Load configuration from Python dictionary."""
        # note: deserialize first runs a structural validation
        model = deserialize(DCConfiguration, config)
        model.validate(self)  # check that values are valid
        if clear:
            self.reset_diffractometer()
        model.write(self.diffractometer)

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
