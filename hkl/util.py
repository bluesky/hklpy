from __future__ import print_function
import logging
import sys
from collections import namedtuple
import numpy as np
import pandas as pd

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
    Pandas DataFrame object

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
            for device, orientation in info.items():
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

    Parameters
    ----------
    run : from Databroker
        A Bluesky run, from databroker v2, such as ``cat.v2[-1]``.

    Dictionary is keyed by "detector" name (in case more than one
    diffractometer was added as a "detector" to the run).

    The orientation information is found in the descriptor document
    of the primary stream.
    """
    devices = {}
    run_conf = run.primary.config
    for device in run_conf:
        conf = run_conf[device].read()
        if f"{device}_orientation_attrs" in conf:
            # fmt:off
            devices[device] = {
                item[len(device)+1:]: conf[item].to_dict()["data"][0]
                for item in conf
            }
            # fmt:on
    return devices
