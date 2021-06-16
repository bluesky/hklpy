"""
Utility functions and structures.

.. autosummary::
    ~diffractometer_types
    ~get_position_tuple
    ~Lattice
    ~list_orientation_runs
    ~new_detector
    ~restore_constraints
    ~restore_energy
    ~restore_orientation
    ~restore_reflections
    ~restore_sample
    ~restore_UB
    ~run_orientation_info
"""

from __future__ import print_function
from .diffract import Constraint
from collections import namedtuple
import logging
import numpy as np
import pandas as pd
import sys

try:
    from gi.repository import Hkl as libhkl
    from gi.repository import GLib
except ImportError as ex:
    libhkl = None
    GLib = None

    print(
        # fmt: off
        "[!!] Failed to import Hkl library;"
        f" diffractometer support disabled ({ex})",
        file=sys.stderr,
        # fmt: on
    )

__all__ = """
    diffractometer_types
    get_position_tuple
    Lattice
    list_orientation_runs
    new_detector
    restore_constraints
    restore_energy
    restore_orientation
    restore_reflections
    restore_sample
    restore_UB
    run_orientation_info
""".split()
logger = logging.getLogger(__name__)


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


Lattice = namedtuple("LatticeTuple", "a b c alpha beta gamma")


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

            list_orientation_runs("class_name", energy", "energy_units", "lattice")

    catalog : object
        Instance of a databroker catalog.
    limit : int
        Limit the list to the first ``limit`` rows. (default=20)
    """
    buffer = []
    _count = 0
    default_columns = "sample_name diffractometer_name geometry_name".split()
    display_columns = default_columns + list(args)
    for run in catalog.v2.values():
        info = run_orientation_info(run)
        if len(info):
            scan_id = run.metadata["start"]["scan_id"]
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
    run_conf = run.primary.config
    for device in sorted(run_conf):
        conf = run_conf[device].read()
        if f"{device}_orientation_attrs" in conf:
            # fmt:off
            devices[device] = {
                item[len(device)+1:]: conf[item].to_dict()["data"][0]
                for item in conf
            }
            # fmt:on
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
    for attr in "energy energy_units energy_offset".split():
        _smart_signal_update(orientation[attr], getattr(diffractometer, attr))


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
    # remember this wavelength
    wavelength0 = diffractometer.calc.wavelength

    # short aliases
    pseudos = orientation["_pseudos"]
    reals = orientation["_reals"]
    orientation_reflections = []

    for ref_base in orientation["reflections_details"]:
        # every reflection has its own wavelength
        diffractometer.calc.wavelength = ref_base["wavelength"]

        # Order of the items is important.
        # Can't just use the dictionaries in ``orientation``.
        # Get the canonical order from the orientation data.
        miller_indices = [ref_base["reflection"][key] for key in pseudos]
        positions = [ref_base["position"][key] for key in reals]
        ppp = namedtuple("PositionTuple", tuple(reals))(*positions)

        # assemble the final form of the reflection for add_reflection()
        reflection = tuple([*miller_indices, ppp])
        r = diffractometer.calc.sample.add_reflection(*reflection)
        if ref_base["orientation_reflection"]:
            orientation_reflections.append(r)

    if len(orientation_reflections) > 1:
        # compute **UB** from the last two orientation reflections
        diffractometer.calc.sample.compute_UB(*orientation_reflections[-2:])

    # restore previous wavelength
    if diffractometer.calc.wavelength != wavelength0:
        diffractometer.calc.wavelength = wavelength0


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
