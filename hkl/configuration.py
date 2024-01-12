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

.. note:: New in v1.1.
"""

__all__ = [
    "DiffractometerConfiguration",
]

import datetime
import json
import pathlib
import typing
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import List

import numpy
import pyRestTable
import yaml
from apischema import deserialize
from apischema import serialize

from .util import libhkl

# TODO: can these be learned from the diffractometer? (not constraints but axes?)
AX_MIN = -360.0  # lowest allowed value for real-space axis
AX_MAX = 360.0  # highest allowed value for real-space axis

DEFAULT_WAVELENGTH = 1.54  # angstrom
EXPORT_FORMATS = "dict json yaml".split()

SIGNIFICANT_DIGITS = 7


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
    if not low <= value <= high:
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
    """
    (internal) Configuration of one diffractometer axis constraint.
    """

    low_limit: float
    """
    Lowest acceptable value for this axis when computing real-space solutions
    from given reciprocal-space positions.
    """

    high_limit: float
    """
    Highest acceptable value for this axis when computing real-space solutions
    from given reciprocal-space positions.
    """

    value: float
    """
    Constant value used (on condition) for ``forward(hkl)`` calculation.

    Implemented by diffractometer :attr:`~hkl.engine.Engine.mode`.

    The diffractometer engine's :attr:`~hkl.engine.Engine.mode` (such as E4CV's
    ``constant_phi`` mode) controls whether or not the axis is to be held
    constant.
    """

    fit: bool = True
    """
    (deprecated) Not used as a constraint.  Value is ignored. See
    :class:`~hkl.util.Constraint`.
    """

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
    """unit cell length :math:`a` (angstrom)"""

    b: float
    """unit cell length :math:`b` (angstrom)"""

    c: float
    """unit cell length :math:`c` (angstrom)"""

    alpha: float
    """unit cell angle alpha (degrees)"""

    beta: float
    """unit cell angle beta (degrees)"""

    gamma: float
    """unit cell angle gamma (degrees)"""

    def validate(self, *_args):
        """Check this lattice has values the diffractometer can accept."""
        _check_range(self.a, 1e-6, 1e6, "a")
        _check_range(self.b, 1e-6, 1e6, "b")
        _check_range(self.c, 1e-6, 1e6, "c")
        _check_range(self.alpha, 1e-6, 180.0 - 1e-6, "alpha")
        _check_range(self.beta, 1e-6, 180.0 - 1e-6, "beta")
        _check_range(self.gamma, 1e-6, 180.0 - 1e-6, "gamma")
        # exclude zero
        _check_not_value(self.alpha, 0.0, "alpha")
        _check_not_value(self.beta, 0.0, "beta")
        _check_not_value(self.gamma, 0.0, "gamma")

    @property
    def values(self):
        """Return the list of values in order."""
        return list(self.__dict__.values())


@dataclass
class DCReflection:
    """(internal) Configuration of one orientation reflection."""

    reflection: Dict[str, float]
    """
    Reciprocal-space axis positions.  Keys must match in the list of
    ``reciprocal_axes``.
    """

    position: Dict[str, float]
    """
    Real-space axis positions.  Keys must match in the list of
    ``canonical_axes``.
    """

    wavelength: float
    """Wavelength (angstroms) at which *this* reflection was measured."""

    orientation_reflection: bool
    """Use this reflection for calculating :math:`UB` matrix?"""

    flag: int = 1
    """(only used by *libhkl*)"""

    def validate(self, dc_obj):
        """Check this reflection has values the diffractometer can accept."""
        _check_range(self.wavelength, 1e-6, 1e6, "wavelength")
        # physics: reciprocal-space won't stretch any further
        q_max = 4 * numpy.pi / self.wavelength
        q_min = -q_max
        for axis, value in self.reflection.items():
            _check_key(axis, dc_obj.reciprocal_axes_names, f"reciprocal-space axis {axis}")
            _check_range(value, q_min, q_max, f"reciprocal-space axis {axis}")
        for axis, value in self.position.items():
            _check_key(axis, dc_obj.canonical_axes_names, f"real-space axis {axis}")
            _check_range(value, AX_MIN, AX_MAX, f"real-space axis {axis}")
        # do not validate 'flag' (not used in hklpy)


@dataclass
class DCSample:
    """(internal) Configuration of one crystalline sample with a lattice."""

    name: str
    """Name of this crystalline sample."""

    lattice: DCLattice
    """Crystal lattice parameters (angstroms and degrees)"""

    reflections: List[DCReflection]
    """List of orientation reflections."""

    UB: List[List[float]]
    """
    Orientation matrix (3 x 3).  U is the crystal orientation matrix relative
    to the diffractometer and B is the transition matrix of a non-orthonormal
    (the reciprocal of the crystal) in an orthonormal system.
    """

    # TODO: Once py38 is dropped, re-enable the default value setting
    U: List[List[float]]  # = field(default_factory=list[list[float]])
    """
    Orientation matrix (3 x 3) of the crystal relative to the diffractometer.
    (optional)
    """

    def validate(self, dc_obj):
        """Check this sample has values the diffractometer can accept."""
        self.lattice.validate()
        _check_not_value(self.name.strip(), "", "name cannot be empty")
        for reflection in self.reflections:
            reflection.validate(dc_obj)
        for k in "U UB".split():
            arr = numpy.array(getattr(self, k))
            _check_value(arr.shape, (3, 3), f"{k} matrix shape")
            for i in range(len(arr)):  # Want i, j for reporting
                for j in range(len(arr[i])):
                    _check_type(arr[i][j], (float, numpy.floating), f"{k}[{i}][{j}]")

    def write(self, diffractometer):
        """Write sample details to diffractometer."""
        sample = diffractometer.calc._samples.get(self.name)
        lattice_parameters = list(self.lattice.values)
        if sample is None:
            sample = diffractometer.calc.new_sample(self.name, lattice=lattice_parameters)
        else:
            sample.lattice = lattice_parameters

        reflection_list = []
        for reflection in self.reflections:
            rdict = asdict(reflection)
            # fmt: off
            args = [  # hkl values
                *list(rdict["reflection"].values()),
                tuple(rdict["position"].values())]
            # fmt: on

            # temporarily, change the wavelength
            w0 = diffractometer.calc.wavelength
            w1 = rdict["wavelength"]
            try:
                diffractometer.calc.wavelength = w1
                r = sample.add_reflection(*args)
                if rdict["orientation_reflection"]:
                    reflection_list.append(r)
            except RuntimeError as exc:
                raise RuntimeError(f"could not add reflection({args}, wavelength={w1})") from exc
            finally:
                diffractometer.calc.wavelength = w0
            # Remaining code will not be executed if exception was raised.

            if len(reflection_list) > 1:
                r1, r2 = reflection_list[0], reflection_list[1]
                sample.compute_UB(r1, r2)


@dataclass
class DCConfiguration:
    """
    (internal) Full structure of the diffractometer configuration.

    Optional (keyword) attributes are not used to restore a diffractometer's
    configuration.

    Required (non-optional) attributes are used by ``restore()`` to either match
    the diffractometer or restore the configuration.
    """

    geometry: str
    """
    Name of the diffractometer geometry as provided by the back-end
    computation library.  MUST match diffractometer to restore.
    """

    engine: str
    """
    Name of the computational support for the reciprocal-space (pseudo) axes.
    MUST match in the list provided by the diffractometer geometry to restore.
    The *engine* defines the list of the reciprocal-space (pseudo) axes.
    """

    library: str
    """
    Name of the back-end computation library.  MUST match diffractometer to
    restore.
    """

    mode: str
    """
    Diffractometer calculation mode.  Chosen from list provided by the
    back-end computation library.  MUST match in the list provided by the
    diffractometer to restore.
    """

    canonical_axes: List[str]
    """
    List of the diffractometer real-space axis names.  Both the exact spelling
    and order are defined by the back-end computation library.  MUST match
    diffractometer to restore.
    """

    real_axes: List[str]
    """
    User-defined real-space axis names. MUST match diffractometer to restore.
    The length and order of this list must be the same as the
    ``canonical_axes``. It is used to resolve any (real-space) ``positioner``
    names in this file.
    """

    reciprocal_axes: List[str]
    """
    List of names of the diffractometer reciprocal-space (pseudo) axes. Both
    the exact spelling and order are defined by the back-end computation
    library ``engine``.
    MUST match diffractometer to restore.
    """

    constraints: Dict[str, DCConstraint]
    """
    Limits to be imposed on the real-space axes for operations and
    computations.  Keys must match in the list of ``canonical_axes``.
    """

    samples: Dict[str, DCSample]
    """
    Crystalline samples (lattice and orientation reflections).
    The sample name is used as the key in the dictionary.
    """

    # -------------------- optional attributes
    name: str = ""
    """
    Name of this diffractometer. (optional)
    """

    datetime: str = ""
    """
    Date and time this configuration was recorded. (optional)
    """

    wavelength_angstrom: float = field(default_factory=float)
    """
    Wavelength (angstrom) of the incident radiation. (optional)
    """

    energy_keV: float = field(default_factory=float)
    """
    Energy (keV) of the incident beam.  Useful for synchrotron X-ray
    instruments. (optional)
    """

    hklpy_version: str = ""
    """
    Version of the *hklpy* Python package used to create this diffractometer
    configuration content. (optional)
    """

    library_version: str = ""
    """
    Version information of the back-end computation library. (optional)
    """

    python_class: str = ""
    """
    Name of the Python class that defines this diffractometer. (optional)
    """

    other: Dict[str, typing.Any] = field(default_factory=dict)
    """
    *Any* other content goes into this dictionary (comments, unanticipated
    keys, ...) (optional)
    """

    def validate(self, dc_obj):
        """
        Check this configuration has values the diffractometer can accept.

        PARAMETERS

        dc_obj *DiffractometerConfiguration*:
            The DiffractometerConfiguration object.
        """
        diffractometer = dc_obj.diffractometer
        _check_value(self.geometry, diffractometer.calc._geometry.name_get(), "geometry")
        _check_key(self.engine, diffractometer.calc._engine_names, "engine")
        _check_value(self.engine, diffractometer.calc.engine.name, "engine")
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
            sample.validate(dc_obj)

    def write(self, diffractometer, restore_constraints=True):
        """Update diffractometer with configuration."""
        from .util import Constraint

        # fmt: off
        if not isinstance(restore_constraints, bool):
            raise TypeError(
                "'restore_constraints' must be True or False,"
                f" received {restore_constraints}"
            )
        # fmt: on

        # don't reset the wavelength
        # don't reset the (real-space) positions
        # don't reset the (reciprocal-space) positions
        diffractometer.engine.mode = self.mode

        # fmt: off
        if restore_constraints:
            diffractometer.apply_constraints(
                {
                    k: Constraint(*constraint.values)
                    for k, constraint in self.constraints.items()
                }
            )
        # fmt: on

        for sample in self.samples.values():
            sample.write(diffractometer)


class DiffractometerConfiguration:
    """
    Save and restore Diffractometer Configuration.

    .. autosummary::

        ~export
        ~preview
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
        Export configuration in a recognized format (dict, JSON, YAML, file).

        PARAMETERS

        fmt *str* or *pathlib.Path* object:
            One of these: ``None``, ``"dict"``, ``"json"``, ``"yaml"``. If
            ``None`` (or empty string or no argument at all), then JSON will be
            the default.
        """
        path = None
        if isinstance(fmt, pathlib.Path):
            path = fmt
            fmt = "json"  # use default format

        fmt = (fmt or "json").lower()
        if fmt == "yml":
            fmt = "yaml"  # a common substitution, just being friendly
        if fmt not in EXPORT_FORMATS:
            raise ValueError(f"fmt must be one of {EXPORT_FORMATS}, received {fmt!r}")
        data = getattr(self, f"to_{fmt}")()
        if path is not None:
            with open(path, "w") as f:
                f.write(data)
        return data

    def preview(self, data, show_constraints=False, show_reflections=False):
        """
        List the samples in the configuration.

        PARAMETERS

        data *dict* or *str* *pathlib.Path* object:
            Structure (dict, json, or yaml) with diffractometer configuration
            or pathlib object referring to a file with one of these formats.
        show_constraints *bool*:
            If ``True`` (default: ``False``), will also show any constraints
            in a separate table.
        show_reflections *bool*:
            If ``True`` (default: ``False``), will also show reflections, if
            any, in a separate table for each sample.
        """
        if isinstance(data, pathlib.Path):
            if not data.exists():
                raise FileNotFoundError(f"{data}")
            with open(data) as f:
                data = f.read()

        if isinstance(data, str):
            if data.strip().startswith("{"):
                data = json.loads(data)
            else:
                data = yaml.load(data, Loader=yaml.Loader)

        return self._preview(data, show_constraints, show_reflections)

    def _preview(self, data, show_constraints=False, show_reflections=False):
        if not isinstance(data, dict):
            raise TypeError(f"Cannot interpret configuration data: {type(data)}")

        def float_format(v):
            return f"{round(v, SIGNIFICANT_DIGITS):g}"

        text = (
            f"name: {data.get('name', '-n/a-')}"
            f"\ndate: {data.get('datetime', '-n/a-')}"
            f"\ngeometry: {data['geometry']}"
        )

        title = "Table of Samples"
        table = pyRestTable.Table()
        table.labels = "# sample a b c alpha beta gamma #refl".split()
        for i, sname in enumerate(data["samples"], start=1):
            sample = data["samples"][sname]
            row = [i, sname]
            for v in sample["lattice"].values():
                row.append(float_format(v))
            row.append(len(sample["reflections"]))
            table.addRow(row)
        text += f"\n\n{title}\n{table}"

        if show_reflections:
            for sname, sample in data["samples"].items():
                if len(sample["reflections"]) == 0:
                    continue  # nothing to report
                title = f"Table of Reflections for Sample: {sname}"
                table = pyRestTable.Table()
                refl = sample["reflections"][0]
                table.addLabel("#")
                table.labels += list(refl["reflection"])
                table.labels += list(refl["position"])
                table.addLabel("wavelength")
                table.addLabel("orient?")
                for i, refl in enumerate(sample["reflections"], start=1):
                    row = [i]
                    row += [float_format(v) for v in refl["reflection"].values()]
                    row += [float_format(v) for v in refl["position"].values()]
                    row.append(f"{round(refl['wavelength'], SIGNIFICANT_DIGITS):g}")
                    row.append(str(refl["orientation_reflection"]))
                    table.addRow(row)
                text += f"\n\n{title}\n{table}"

        if show_constraints and len(data["constraints"]) > 0:
            title = "Table of Axis Constraints"
            table = pyRestTable.Table()
            table.labels = "axis low_limit high_limit value fit?".split()
            for aname, constraint in data["constraints"].items():
                row = [aname]
                for k in "low_limit high_limit value".split():
                    row.append(float_format(constraint[k]))
                row.append(f"{constraint['fit']}")
                table.addRow(row)
            text += f"\n\n{title}\n{table}"

        return text

    def restore(self, data, clear=True, restore_constraints=True):
        """
        Restore configuration from a recognized format (dict, JSON, YAML, file).

        Instead of guessing, recognize the kind of config data by its structure.

        PARAMETERS

        data *dict* or *str* *pathlib.Path* object:
            Structure (dict, json, or yaml) with diffractometer configuration
            or pathlib object referring to a file with one of these formats.
        clear *bool*:
            If ``True`` (default), remove any previous configuration of the
            diffractometer and reset it to default values before restoring the
            configuration.

            If ``False``, sample reflections will be append with all reflections
            included in the configuration data for that sample.  Existing
            reflections will not be changed.  The user may need to edit the
            list of reflections after ``restore(clear=False)``.
        restore_constraints *bool*:
            If ``True`` (default), restore any constraints provided.

        Note: Can't name this method "import", it's a reserved Python word.
        """
        importer = None

        if not isinstance(clear, bool):
            raise TypeError(f"clear must be either True or False, received {clear}")

        if isinstance(data, pathlib.Path):
            if not data.exists():
                raise FileNotFoundError(f"{data}")
            with open(data) as f:
                data = f.read()

        if isinstance(data, dict):
            importer = self.from_dict
        elif isinstance(data, str):
            if data.strip().startswith("{"):
                importer = self.from_json
            else:
                importer = self.from_yaml
        if importer is None:
            raise TypeError("Unrecognized configuration structure.")

        importer(data, clear=clear, restore_constraints=restore_constraints)

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

        # either an empty dict or maps renamed axes to canonical
        xref = dict(diffractometer.calc._axis_name_to_original)

        def canonical_name(axis):
            return xref.get(axis, axis)

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
                canonical_name(axis): {
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

    def from_dict(self, data, clear=True, restore_constraints=True):
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
        model.write(self.diffractometer, restore_constraints=restore_constraints)

    def to_dict(self):
        """Report diffractometer configuration as Python dictionary."""
        return serialize(DCConfiguration, self.model)

    def from_json(self, data, clear=True, restore_constraints=True):
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
        self.from_dict(json.loads(data), clear=clear, restore_constraints=restore_constraints)

    def to_json(self, indent=2):
        """Report diffractometer configuration as JSON text."""
        return json.dumps(self.to_dict(), indent=indent)

    def from_yaml(self, data, clear=True, restore_constraints=True):
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
        # fmt: off
        self.from_dict(
            yaml.load(data, Loader=yaml.Loader),
            clear=clear,
            restore_constraints=restore_constraints
        )
        # fmt: on

    def to_yaml(self, indent=2):
        """
        Report diffractometer configuration as YAML text.

        Order of appearance may be important for some entries, such as the list
        of reflections.  Use ``sort_keys=False`` here. Don't make ``sort_keys``
        a keyword argument that could be changed.
        """
        return yaml.dump(self.to_dict(), indent=indent, sort_keys=False)
