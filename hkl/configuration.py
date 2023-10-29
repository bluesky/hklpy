"""
Save and restore Diffractometer Configuration.

PUBLIC API

.. autosummary::

    ~DiffractometerConfiguration

PRIVATE API

note: DC classes: Diffractometer Configuration

.. autosummary::

    ~_check_key
    ~_check_not_value
    ~_check_range
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

from . import A_KEV
from .util import libhkl

# TODO: can these be learned from the diffractometer? (not constraints but axes?)
AX_MIN = -360.0  # lowest allowed value for real-space axis
AX_MAX = 360.0  # highest allowed value for real-space axis

DEFAULT_WAVELENGTH = 1.54  # angstrom
EXPORT_FORMATS = "dict json yaml".split()


# standard value checks, raise exception(s) when appropriate
def _check_key(key, biblio, intro):
    """(internal) Raise KeyError if key is not in biblio."""
    if key not in biblio:
        raise KeyError(f"{intro}:  expected {key!r} not in {biblio}")


def _check_not_value(actual, avoid, intro):
    """(internal) Raise ValueError if actual IS equal to expected."""
    if actual == avoid:
        raise ValueError(f"{intro}:  received: {actual}  cannot be: {avoid}")


def _check_range(value, low, high, intro):
    """(internal) Raise ValueError if value is not between low & high."""
    if low > high:
        raise ValueError(f"{intro}:  {low} should not be greater than {high}")
    if not (low <= value <= high):
        raise ValueError(f"{intro}:  {value} is not between {low} & {high}")


def _check_type(actual, expected, intro):
    """(internal) Raise TypeError if actual is not an instance of expected."""
    if not isinstance(actual, expected):
        raise TypeError(f"{intro}:  received: {actual}  expected: {expected}")


def _check_value(actual, expected, intro):
    """(internal) Raise ValueError if actual is not equal to expected."""
    if actual != expected:
        raise ValueError(f"{intro}:  received: {actual}  expected: {expected}")


@dataclass
class DCConstraint:
    """(internal) Configuration of one diffractometer axis constraint."""

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
    """(internal) Configuration of one crystal lattice."""

    a: float
    b: float
    c: float
    alpha: float
    beta: float
    gamma: float

    def validate(self, dc_obj):
        """Check this lattice has values the diffractometer can accept."""
        for side in "a b c".split():
            _check_range(getattr(self, side), 1e-6, 1e6, f"side {side}")
        for angle in "alpha beta gamma".split():
            v = getattr(self, angle)
            _check_not_value(v, 0., f"angle {angle}")  # exclude zero
            _check_range(v, 1e-6, 180. - 1e-6, f"angle {angle}")

    @property
    def values(self):
        """Return the list of values in order."""
        return list(self.__dict__.values())


@dataclass
class DCReflection:
    """(internal) Configuration of one orientation reflection."""

    reflection: dict[str, float]
    position: dict[str, float]
    wavelength: float
    orientation_reflection: bool
    flag: int = 1  # only used by libhkl

    def validate(self, dc_obj):
        """Check this reflection has values the diffractometer can accept."""
        _check_range(self.wavelength, 1e-6, 1e6, "wavelength")
        # physics: reciprocal-space won't stretch any further
        q_max = 4 * numpy.pi / self.wavelength
        q_min = -q_max
        for axis, value in self.reflection.items():
            _check_key(axis, dc_obj.reciprocal_axes, f"reciprocal-space axis {axis}")
            _check_range(value, q_min, q_max, f"reciprocal-space axis {axis}")
        for axis, value in self.position.items():
            _check_key(axis, dc_obj.canonical_axes, f"real-space axis {axis}")
            _check_range(value, AX_MIN, AX_MAX, f"real-space axis {axis}")
        # do not validate 'flag' (not used in hklpy)


@dataclass
class DCSample:
    """(internal) Configuration of one crystalline sample with a lattice."""

    name: str
    lattice: DCLattice
    reflections: list[DCReflection]
    U: list[list[float]]
    UB: list[list[float]]

    def validate(self, dc_obj):
        """Check this sample has values the diffractometer can accept."""
        self.lattice.validate(dc_obj)
        for reflection in self.reflections:
            reflection.validate(dc_obj)
        for k in "U UB".split():
            arr = numpy.array(getattr(self, k))
            _check_value(arr.shape, (3, 3), f"{k} matrix shape")
            _check_type(arr[0][0], (float, numpy.floating), f"{k} matrix")

    def write(self, diffractometer):
        """Write sample details to diffractometer."""
        lattice_parameters = list(self.lattice.values)

        s = diffractometer.calc._samples.get(self.name)
        if s is None:
            s = diffractometer.calc.new_sample(self.name, lattice=lattice_parameters)
        else:
            s.lattice = lattice_parameters

        reflection_list = []
        for reflection in self.reflections:
            rdict = serialize(DCReflection, reflection)
            args = [*list(rdict["reflection"].values()), tuple(rdict["position"].values())]  # hkl values

            # temporarily, change the wavelength
            w0 = diffractometer.calc.wavelength
            w1 = rdict["wavelength"]
            try:
                diffractometer.calc.wavelength = w1
                r = diffractometer.calc.sample.add_reflection(*args)
            except RuntimeError as exc:
                print(f"RuntimeError when adding reflection({args}, wavelength={w1}): {exc}")
            finally:
                diffractometer.calc.wavelength = w0

            if rdict["orientation_reflection"]:
                reflection_list.append(r)

            if len(reflection_list) > 1:
                r1, r2 = reflection_list[0], reflection_list[1]
                diffractometer.calc.sample.compute_UB(r1, r2)


@dataclass
class DCConfiguration:
    """(internal) Full structure of the diffractometer configuration."""

    name: str
    geometry: str  # MUST match diffractometer to restore
    library: str  # MUST match diffractometer to restore
    mode: str  # MUST match a diffractometer mode to restore
    canonical_axes: list[str]  # MUST match diffractometer to restore
    real_axes: list[str]  # MUST match number of diffractometer axes to restore
    reciprocal_axes: list[str]  # MUST match diffractometer to restore
    wavelength_angstrom: float
    constraints: dict[str, DCConstraint]
    samples: dict[str, DCSample]

    # optional attributes
    datetime: str = ""
    energy_keV: float = A_KEV / DEFAULT_WAVELENGTH  # assumes X-rays
    engine: str = ""
    hklpy_version: str = ""
    library_version: str = ""
    python_class: str = ""

    def validate(self, dc_obj):
        """
        Check this configuration has values the diffractometer can accept.

        PARAMETERS

        dc_obj *DiffractometerConfiguration*:
            The DiffractometerConfiguration object.
        """
        diffractometer = dc_obj.diffractometer
        _check_value(self.geometry, diffractometer.calc._geometry.name_get(), "geometry")
        _check_value(self.library, libhkl.__name__, "library")
        _check_value(self.canonical_axes, dc_obj.canonical_axes_names, "canonical_axes")
        _check_value(self.reciprocal_axes, dc_obj.reciprocal_axes_names, "reciprocal_axes")
        _check_key(self.mode, diffractometer.engine.modes, "mode")

        for k in "canonical real reciprocal".split():
            # number of axes must match
            _check_value(
                len(getattr(self, f"{k}_axes")), len(getattr(dc_obj, f"{k}_axes_names")), f"number of {k}_axes"
            )

        for cname, constraint in self.constraints.items():
            try:
                _check_key(cname, dc_obj.canonical_axes_names, "constraint axis")
            except KeyError:
                _check_key(cname, dc_obj.real_axes_names, "constraint axis")
            constraint.validate(cname)

        for sample in self.samples.values():
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

    .. autosummary::

        ~export
        ~restore
        ~model
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

    def __init__(self, diffractometer):
        from .diffract import Diffractometer

        if not isinstance(diffractometer, Diffractometer):
            raise TypeError("diffractometer should be 'Diffractometer' or subclass.")
        self.diffractometer = diffractometer

    def export(self, fmt="json"):
        """
        Export configuration in a recognized format (dict, JSON, YAML).

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

    def restore(self, data, clear=True):
        """
        Restore configuration from a recognized format (dict, json, yaml).

        Instead of guessing, recognize the kind of config data by its structure.

        PARAMETERS

        data *dict* or *str*:
            structure (dict, json, or yaml) with diffractometer configuration
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.

        Note: Can't name this method "import", it's a reserved Python word.
        """
        importer = None

        if isinstance(data, dict):
            importer = self.from_dict
        elif isinstance(data, str):
            if data.strip().startswith("{"):
                importer = self.from_json
            else:
                importer = self.from_yaml
        if importer is None:
            raise TypeError("Unrecognized configuration structure.")

        importer(data, clear=clear)

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
        """Names of the reciprocal-space axes, defined by the back-end library."""
        return list(self.diffractometer.PseudoPosition._fields)

    @property
    def model(self) -> DCConfiguration:
        """Return validated diffractometer configuration object."""
        diffractometer = self.diffractometer
        data = {
            "name": diffractometer.name,
            "geometry": diffractometer.calc._geometry.name_get(),
            "datetime": str(datetime.datetime.now()),
            "python_class": diffractometer.__class__.__name__,
            "engine": diffractometer.calc.engine.name,
            "mode": diffractometer.calc.engine.mode,
            "canonical_axes": self.canonical_axes_names,
            "real_axes": self.real_axes_names,
            "reciprocal_axes": self.reciprocal_axes_names,
            "energy_keV": diffractometer.calc.energy,  # for X-ray instruments
            "wavelength_angstrom": diffractometer.calc.wavelength,
            "hklpy_version": diffractometer._hklpy_version_,
            "library": libhkl.__name__,
            "library_version": libhkl.VERSION,
            # fmt: off
            "constraints": {
                axis: {
                    parm: getattr(constraint, parm)
                    for parm in "low_limit high_limit value fit".split()
                }
                for axis, constraint in diffractometer._constraints_dict.items()
            },
            # fmt: on
            "samples": {
                sname: {
                    "name": sample.name,
                    "lattice": sample.lattice._asdict(),
                    "reflections": sample.reflections_details,
                    "U": sample.U.tolist(),
                    "UB": sample.UB.tolist(),
                }
                for sname, sample in diffractometer.calc._samples.items()
            },
        }
        obj = deserialize(DCConfiguration, data)  # also validates structure
        obj.validate(self)  # check that values are valid
        return obj

    def reset_diffractometer(self):
        """Reset the diffractometer to the default configuration."""
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

    def from_dict(self, data, clear=True):
        """
        Load diffractometer configuration from Python dictionary.

        PARAMETERS

        data *dict*:
            structure (dict) with diffractometer configuration
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.
        """
        # note: deserialize first runs a structural validation
        model = deserialize(DCConfiguration, data)
        model.validate(self)  # check that values are valid
        if clear:
            self.reset_diffractometer()
        # tell the model to update the diffractometer
        model.write(self.diffractometer)

    def to_dict(self):
        """Report diffractometer configuration as Python dictionary."""
        return serialize(DCConfiguration, self.model)

    def from_json(self, data, clear=True):
        """
        Load diffractometer configuration from JSON text.

        PARAMETERS

        data *str* (JSON):
            structure (JSON string) with diffractometer configuration
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.
        """
        self.from_dict(json.loads(data), clear=clear)

    def to_json(self, indent=4):
        """Report diffractometer configuration as JSON text."""
        return json.dumps(self.to_dict(), indent=indent)

    def from_yaml(self, data, clear=True):
        """
        Load diffractometer configuration from YAML text.

        PARAMETERS

        data *str* (YAML):
            structure (YAML string) with diffractometer configuration
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.
        """
        self.from_dict(yaml.load(data, Loader=yaml.Loader), clear=clear)

    def to_yaml(self, indent=4):
        """
        Report diffractometer configuration as YAML text.

        Order of appearance may be important for some entries, such as the list
        of reflections.  Use ``sort_keys=False`` here. Don't make ``sort_keys``
        a keyword argument that could be changed.
        """
        return yaml.dump(self.to_dict(), indent=indent, sort_keys=False)
