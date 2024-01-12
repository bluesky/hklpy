"""
Utility functions and structures.

.. autosummary::

    ~Constraint
    ~diffractometer_types
    ~get_package_info
    ~get_position_tuple
    ~Lattice
    ~list_orientation_runs
    ~new_detector
    ~new_lattice
    ~restore_constraints
    ~restore_energy
    ~restore_orientation
    ~restore_reflections
    ~restore_sample
    ~restore_UB
    ~run_orientation_info
    ~software_versions

Also provides `SI_LATTICE_PARAMETER` as defined by the
*2018 CODATA recommended lattice parameter of silicon*. [#]_

.. [#] https://physics.nist.gov/cgi-bin/cuu/Value?asil
"""

import logging
import subprocess
import sys
from collections import defaultdict
from collections import namedtuple

import databroker
import gi
import numpy as np
import pandas as pd
import tqdm

gi.require_version("Hkl", "5.0")
from gi.repository import GLib  # noqa: F401
from gi.repository import Hkl as libhkl

__all__ = """
    Constraint
    diffractometer_types
    get_package_info
    get_position_tuple
    Lattice
    list_orientation_runs
    new_detector
    new_lattice
    restore_constraints
    restore_energy
    restore_orientation
    restore_reflections
    restore_sample
    restore_UB
    run_orientation_info
    SI_LATTICE_PARAMETER
    software_versions
""".split()
logger = logging.getLogger(__name__)


# when getting software package versions
DEFAULT_PACKAGE_LIST = "hkl pygobject".split()

# 2018 CODATA recommended lattice parameter of silicon, Angstrom.
# see: https://physics.nist.gov/cgi-bin/cuu/Value?asil
SI_LATTICE_PARAMETER = 5.431020511
# also provide the reported uncertainty, in case anyone is interested
SI_LATTICE_PARAMETER_UNCERTAINTY = 0.000000089


def new_detector(dtype=0):
    """Create a new HKL-library detector"""
    return libhkl.Detector.factory_new(libhkl.DetectorType(dtype))


if libhkl:
    diffractometer_types = tuple(sorted(libhkl.factories().keys()))
    UserUnits = libhkl.UnitEnum.USER
    DefaultUnits = libhkl.UnitEnum.DEFAULT

    # fmt: off
    units = {
        "user": UserUnits,
        "default": DefaultUnits
    }
    # fmt: on
else:
    diffractometer_types = ()
    units = {}


def to_numpy(mat):
    """Convert an hkl ``Matrix`` to a numpy ndarray

    Parameters
    ----------
    mat : Hkl.Matrix

    Returns
    -------
    ndarray
    """
    if isinstance(mat, np.ndarray):
        return mat

    ret = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            ret[i, j] = mat.get(i, j)

    return ret


def to_hkl(arr):
    """Convert a numpy ndarray to an hkl ``Matrix``

    Parameters
    ----------
    arr : ndarray

    Returns
    -------
    Hkl.Matrix
    """
    if isinstance(arr, libhkl.Matrix):
        return arr

    arr = np.array(arr)

    hklm = hkl_euler_matrix(0, 0, 0)
    hklm.init(*arr.flatten())
    return hklm


def hkl_euler_matrix(euler_x, euler_y, euler_z):
    """Convert into matrix form."""
    return libhkl.Matrix.new_euler(euler_x, euler_y, euler_z)


def _gi_info(gi_val):
    def get(attr):
        try:
            getter = getattr(gi_val, attr)
            # inspect.signature doesn't work on gi functions...
            return getter()
        except Exception as ex:
            try:
                return getter(units["user"])
            except Exception:
                return f"({ex.__class__.__name__}: {ex})"

    return {attr: get(attr) for attr in dir(gi_val) if attr.endswith("_get")}


class Constraint:
    """
    Limitations on acceptable positions from computed forward() solutions.

    Parameters
    ----------
    low_limit : float
        Lowest acceptable value for this axis when computing real-space solutions
        from given reciprocal-space positions.
    high_limit : float
        Highest acceptable value for this axis when computing real-space solutions
        from given reciprocal-space positions.
    value : float
        Constant value used (on condition) for ``forward(hkl)`` calculation.

        Implemented by diffractometer :attr:`~hkl.engine.Engine.mode`.

        The diffractometer engine's :attr:`~hkl.engine.Engine.mode` (such as E4CV's
        ``constant_phi`` mode) controls whether or not the axis is to be held
        constant.
    fit : bool
        (deprecated) Not used as a constraint.

        The value of ``fit`` is ignored.  It remains now for compatibility with
        previous *hklpy* releases. It will be dropped in a future *hklpy* release.

        While this parameter is used by *libhkl* to adjust lattice parameters when
        refining the **UB** matrix from more than 2 reflections, it is not used in
        the calculation of rotation angles from reciprocal-space coordinates.
    """

    def __init__(self, low_limit, high_limit, value, fit=True):
        self.low_limit = float(low_limit)
        self.high_limit = float(high_limit)
        self.value = float(value)
        self.fit = bool(fit)

        self._fields = "low_limit high_limit value fit".split()
        # fmt: off
        _fields = ", ".join(
            name + "=" + repr(getattr(self, name))
            for name in self._fields
        )
        # fmt: on
        self._repr_fmt = f"({_fields})"

    def _asdict(self):
        "Return a new dict which maps field names to their values."
        return dict(zip(self._fields, self))

    class _ConstraintIterator:
        "Iterator"

        def __init__(self, constraint):
            self.constraint = constraint
            self._index = 0

        def __next__(self):
            if self._index < len(self.constraint._fields):
                c = getattr(self.constraint, self.constraint._fields[self._index])
                self._index += 1
                return c
            else:
                raise StopIteration

    def __iter__(self):
        "Iterate through the fields."
        return self._ConstraintIterator(self)

    def __repr__(self):
        "Return a nicely formatted representation string."
        content = "(" + ", ".join([f"{k}={getattr(self, k)}" for k in self._fields]) + ")"
        return self.__class__.__name__ + content


Lattice = namedtuple("LatticeTuple", "a b c alpha beta gamma")


def new_lattice(a, b=None, c=None, alpha=90.0, beta=None, gamma=None):
    """
    Simplify for high-symmetry crystal systems.

    EXAMPLES (highest to lowest symmetry):

    =============== =================================== === === === ======= ======= =====
    system          command                             a   b   c   alpha   beta    gamma
    =============== =================================== === === === ======= ======= =====
    cubic           new_lattice(5.)                     5   5   5   90      90      90
    hexagonal       new_lattice(4., c=3., gamma=120)    4   4   3   90      90      120
    rhombohedral    new_lattice(4., alpha=80.0)         4   4   4   80      80      80
    tetragonal      new_lattice(4, c=3)                 4   4   3   90      90      90
    orthorhombic    new_lattice(4, 5, 3)                4   5   3   90      90      90
    monoclinic      new_lattice(4, 5, 3, beta=75)       4   5   3   90      75      90
    triclinic       new_lattice(4, 5, 3, 75., 85., 95.) 4   5   3   75      85      95
    =============== =================================== === === === ======= ======= =====

    .. see: https://en.wikipedia.org/wiki/Crystal_system
    """
    return Lattice(a, b or a, c or a, alpha, beta or alpha, gamma or alpha)


_position_tuples = {}


def get_position_tuple(axis_names, class_name="Position"):
    """Return a namedtuple with the positions."""
    global _position_tuples

    key = frozenset(axis_names)
    if key not in _position_tuples:
        _position_tuples[key] = namedtuple(class_name, tuple(axis_names))

    return _position_tuples[key]


def list_orientation_runs(catalog, *args, limit=20):
    """
    List the runs with orientation information.

    Returns
    -------
    orientation information: Pandas DataFrame object

    Parameters
    ----------
    *args : [str]
        A list of additional data column names to be displayed,
        corresponding to the names of available orientation
        information in the descriptor document.

        Example::

            list_orientation_runs(
                "class_name", energy", "energy_units", "lattice")

    catalog : object
        Instance of a databroker catalog.
    limit : int
        Limit the list to the first ``limit`` rows. (default=20)
    """
    buffer = []
    _count = 0
    default_columns = "sample_name diffractometer_name geometry_name".split()
    display_columns = default_columns + list(args)
    with tqdm.tqdm(total=len(catalog.v2), file=sys.stdout) as progress_bar:
        for run in catalog.v2.values():
            info = run_orientation_info(run)
            if len(info):
                scan_id = run.metadata["start"]["scan_id"]
                if databroker.__version__ >= "2.0":
                    uid = run.start["uid"][:7]
                else:
                    uid = run.name[:7]
                for device in sorted(info.keys()):
                    orientation = info[device]
                    row = dict(scan_id=scan_id)
                    for f in display_columns:
                        if f in orientation:
                            row[f] = orientation[f]
                    row["uid"] = uid
                    buffer.append(row)
                    _count += 1
                    if _count >= limit:
                        break
            if _count >= limit:
                break
            progress_bar.update()
    return pd.DataFrame(buffer)


def run_orientation_info(run):
    """
    Return a dictionary with orientation information in this run.

    Dictionary is keyed by "detector" name (in case more than one
    diffractometer was added as a "detector" to the run).

    The orientation information is found in the descriptor document
    of the primary stream.

    Parameters
    ----------
    run : from Databroker
        A Bluesky run, from databroker v2, such as ``cat.v2[-1]``.
    """
    devices = {}

    try:
        if databroker.__version__ >= "2.0":
            for descriptor in run.primary.descriptors:
                for device, configuration in descriptor.get("configuration", {}).items():
                    conf = configuration.get("data", {})
                    if f"{device}_orientation_attrs" in conf:
                        # fmt:off
                        devices[device] = {
                            item[len(f"{device}_"):]: value
                            for item, value in conf.items()
                        }
                        # fmt:on

        else:  # older databroker v1.2
            run_conf = run.primary.config
            for device in sorted(run_conf):
                conf = run_conf[device].read()
                if f"{device}_orientation_attrs" in conf:
                    # fmt:off
                    devices[device] = {
                        item[len(f"{device}_"):]: conf[item].to_dict()["data"][0]
                        for item in conf
                    }
                    # fmt:on
    except Exception as exc:
        logger.warning("Could not process run %s, due to %s", run, exc)
    return devices


def _smart_signal_update(value, signal):
    """Write value to signal if not equal.  Not a plan."""
    if signal.get() != value:
        signal.put(value)


def _check_geometry(orientation, diffractometer):
    """
    Check that geometry of recovered orientation matches diffractometer.

    Parameters
    ----------
    orientation : dict
        Dictionary of orientation parameters (from
        :func:`~hkl.util.run_orientation_info()`) recovered from run.
    diffractometer : :class:`~hkl.diffract.Diffractometer()`
        Diffractometer object.

    Raise ValueError if mismatched.
    """
    if orientation["geometry_name"] != diffractometer.geometry_name.get():
        raise ValueError(
            "Geometries do not match:"
            f" Orientation={orientation['geometry_name']},"
            f" {diffractometer.name}={diffractometer.geometry_name.get()},"
            " will not restore."
        )


def restore_constraints(orientation, diffractometer):
    """
    Restore any constraints from orientation information.

    Parameters
    ----------
    orientation : dict
        Dictionary of orientation parameters (from
        :func:`~hkl.util.run_orientation_info()`) recovered from run.
    diffractometer : :class:`~hkl.diffract.Diffractometer()`
        Diffractometer object.
    """
    _check_geometry(orientation, diffractometer)

    # fmt:off
    if len(orientation["_constraints"]):
        con_dict = {
            k: Constraint(*v)
            for k, v in zip(orientation["_reals"], orientation["_constraints"])
        }
        diffractometer.apply_constraints(con_dict)
    # fmt:on


def restore_energy(orientation, diffractometer):
    """
    Restore energy from orientation information.

    NOTE: This makes blocking calls so do not use in bluesky plan.

    Parameters
    ----------
    orientation : dict
        Dictionary of orientation parameters (from
        :func:`~hkl.util.run_orientation_info()`) recovered from run.
    diffractometer : :class:`~hkl.diffract.Diffractometer()`
        Diffractometer object.
    """
    # get _all_ the expected keys
    try:
        kv_dict = {
            orientation[attr]: getattr(diffractometer, attr)
            for attr in "energy energy_units energy_offset".split()
        }
    except KeyError as exc:
        # fmt: off
        raise KeyError(
            f"{diffractometer.name}: Cannot restore "
            f"diffractometer energy due to missing {exc} term."
        )
        # fmt: on
    # update the signals
    for k, v in kv_dict.items():
        _smart_signal_update(k, v)


def restore_reflections(orientation, diffractometer):
    """
    Restore any reflections from orientation information.

    Parameters
    ----------
    orientation : dict
        Dictionary of orientation parameters (from
        :func:`~hkl.util.run_orientation_info()`) recovered from run.
    diffractometer : :class:`~hkl.diffract.Diffractometer()`
        Diffractometer object.
    """
    _check_geometry(orientation, diffractometer)
    calc = diffractometer.calc
    # remember this wavelength
    wavelength0 = calc.wavelength

    # short aliases
    pseudos = orientation["_pseudos"]
    reals = orientation["_reals"]
    if reals != calc.physical_axis_names and reals == calc._geometry.axis_names_get():
        # Substitute user-defined axes names for canonical axes names.
        reals = calc.physical_axis_names
    orientation_reflections = []
    # might be renamed axes
    renaming = calc._axis_name_to_original

    for ref_base in orientation["reflections_details"]:
        # every reflection has its own wavelength
        calc.wavelength = ref_base["wavelength"]

        # Order of the items is important.
        # Can't just use the dictionaries in ``orientation``.
        # Get the canonical order from the orientation data.
        miller_indices = [ref_base["reflection"][key] for key in pseudos]
        try:
            positions = [ref_base["position"][key] for key in reals]
        except KeyError:
            # switch to use renamed keys
            positions = [ref_base["position"][renaming[key]] for key in reals]
        ppp = namedtuple("PositionTuple", tuple(reals))(*positions)

        # assemble the final form of the reflection for add_reflection()
        reflection = tuple([*miller_indices, ppp])
        r = calc.sample.add_reflection(*reflection)
        if ref_base["orientation_reflection"]:
            orientation_reflections.append(r)

    if len(orientation_reflections) > 1:
        # compute **UB** from the last two orientation reflections
        calc.sample.compute_UB(*orientation_reflections[-2:])

    # restore previous wavelength
    if calc.wavelength != wavelength0:
        calc.wavelength = wavelength0


def restore_orientation(orientation, diffractometer):
    """
    Restore all orientation information.

    Parameters
    ----------
    orientation : dict
        Dictionary of orientation parameters (from
        :func:`~hkl.util.run_orientation_info()`) recovered from run.
    diffractometer : :class:`~hkl.diffract.Diffractometer()`
        Diffractometer object.
    """
    _check_geometry(orientation, diffractometer)
    restore_energy(orientation, diffractometer)
    restore_sample(orientation, diffractometer)
    restore_constraints(orientation, diffractometer)
    restore_reflections(orientation, diffractometer)


def restore_sample(orientation, diffractometer):
    """
    Restore sample & lattice from orientation information.

    Parameters
    ----------
    orientation : dict
        Dictionary of orientation parameters (from
        :func:`~hkl.util.run_orientation_info()`) recovered from run.
    diffractometer : :class:`~hkl.diffract.Diffractometer()`
        Diffractometer object.
    """
    nm = orientation["sample_name"]
    lattice = orientation["lattice"]
    if nm not in diffractometer.calc._samples:
        diffractometer.calc.new_sample(nm, lattice=lattice)
    else:
        raise ValueError(f"Sample '{nm}' already exists in {diffractometer.name}.")


def restore_UB(orientation, diffractometer):
    """
    Restore **UB** matrix from orientation information.

    Parameters
    ----------
    orientation : dict
        Dictionary of orientation parameters (from
        :func:`~hkl.util.run_orientation_info()`) recovered from run.
    diffractometer : :class:`~hkl.diffract.Diffractometer()`
        Diffractometer object.
    """
    _check_geometry(orientation, diffractometer)
    _smart_signal_update(orientation["UB"], diffractometer.UB)


def _installed_package_information():
    """Index information about packages known by conda and/or pip."""
    packages = defaultdict(dict)

    def run(tool):
        try:
            # Python 3.7+
            s = subprocess.run([tool, "list"], capture_output=True)
        except TypeError:
            # Python < 3.7
            s = subprocess.run([tool, "list"], stdout=subprocess.PIPE)
        return s

    for tool in "conda pip".split():
        s = run(tool)
        for line in s.stdout.splitlines():
            if not line.decode().startswith("#"):
                args = line.decode().strip().split()
                key = args[0]
                packages[key]["version"] = args[1]
                packages[key][tool] = True
                if tool == "conda":
                    packages[key]["build"] = args[2]
                    packages[key]["conda"] = True
                    if len(args) == 4:
                        packages[key]["channel"] = args[3]

                elif tool == "pip":
                    if len(args) == 3:
                        packages[key]["location"] = args[2]

    return packages


# cache of discovered installed package information
_package_info = None


def get_package_info(package_name):
    """Return dict of information about installed package, by name."""
    global _package_info
    if _package_info is None:
        # index the known packages
        # This is not expected to change once the process has started.
        _package_info = _installed_package_information()
    return _package_info.get(package_name)


def software_versions(keys=[]):
    """
    Report the package versions, in a dictionary.

    EXAMPLE::

        In [1]: import gi
        ...:
        ...: gi.require_version("Hkl", "5.0")
        ...:
        ...: import hkl.util

        In [2]: hkl.util.software_versions()
        Out[2]:
        {'hkl': '5.0.0.2173',
        'hklpy': '0.3.16+131.ga5a449a.dirty',
        'pygobject': '3.40.1'}

    Here, it shows (albeit indirectly) *Hkl 5.0.0 tag 2173*.  Proceed to the Hkl
    source repository, list of tags [#]_, and find tag ``2173`` [#]_.

    .. [#] Hkl source tags: https://repo.or.cz/hkl.git/refs
    .. [#] Hkl tag 2173: https://repo.or.cz/hkl.git/tree/refs/tags/v5.0.0.2173)
    """
    if keys is None or len(keys) == 0:
        keys = DEFAULT_PACKAGE_LIST
    v_dict = {}
    for key in keys:
        info = get_package_info(key)
        if info is not None:
            v_dict[key] = info.get("version")
    return v_dict
