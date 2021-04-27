from __future__ import print_function
import logging
import sys
from collections import namedtuple

import numpy as np

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
    new_detector
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
    """ """
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
    """ """
    global _position_tuples

    key = frozenset(axis_names)
    if key not in _position_tuples:
        _position_tuples[key] = namedtuple(class_name, tuple(axis_names))

    return _position_tuples[key]
