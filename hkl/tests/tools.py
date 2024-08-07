"""
Common code, setups, constants, ... for these tests.

Avoids direct imports of __init__.py.
"""

import json
import logging
from pathlib import Path  # noqa

import numpy

from ..util import new_lattice

logger = logging.getLogger("ophyd_session_test")

TARDIS_TEST_MODE = "lifting_detector_mu"
TWO_PI = 2 * numpy.pi


class DocsCollector:
    """Collect representative documents from the RE."""

    def __init__(self) -> None:
        self.raw = {}
        self.safe_json = {}

    def receiver(self, key, doc):
        self.raw[key] = doc
        self.safe_json[key] = safe_json_dump(doc)

    def to_file(self, fpath: (Path, str), indent: int = 2) -> None:  # type: ignore
        """Write collected docs to a file."""
        with open(fpath, "w") as f:
            dd = {k: json.loads(v.decode("utf8")) for k, v in self.safe_json.items()}
            json.dump(dd, f, indent=indent)


def new_sample(diffractometer, name, lattice):
    return diffractometer.calc.new_sample(name, lattice=lattice)


def sample_kryptonite(diffractometer):
    triclinic = new_lattice(4, 5, 6, 75, 85, 95)
    return new_sample(diffractometer, "kryptonite", lattice=triclinic)


def sample_silicon(diffractometer):
    from .. import SI_LATTICE_PARAMETER

    cubic = new_lattice(SI_LATTICE_PARAMETER)
    return new_sample(diffractometer, "silicon", lattice=cubic)


def sample_vibranium(diffractometer):
    a0 = TWO_PI
    cubic = new_lattice(a0)
    return new_sample(diffractometer, "vibranium", lattice=cubic)


def validate_descriptor_doc_content(gname, descriptor):
    """Validate the descriptor document content."""
    assert isinstance(descriptor, dict)

    config = descriptor.get("configuration")
    assert isinstance(config, dict)

    diffractometer_config = config.get(gname)
    assert isinstance(diffractometer_config, dict)

    assert "data" in diffractometer_config
    data = diffractometer_config.get("data")
    assert isinstance(data, dict)

    attrs = [
        ["sample_name", str],
        ["lattice", (numpy.ndarray, list)],
        ["lattice_reciprocal", (tuple, list)],
        ["U", (numpy.ndarray, list)],
        ["UB", (numpy.ndarray, list)],
        ["reflections_details", list],
        ["_pseudos", (tuple, list)],
        ["_reals", (tuple, list)],
        ["_constraints", (numpy.ndarray, list)],
        ["ux", float],
        ["uy", float],
        ["uz", float],
        ["orientation_attrs", list],
    ]
    for attr, struct in attrs:
        assert isinstance(data.get(f"{gname}_{attr}"), struct), f"{attr=!r} {list(data)=!r}"


def safe_json_dump(content):
    """
    Vendored from tiled.utils

    https://github.com/bluesky/tiled/blob/15abbc98df9bfd25f8c713656f664a558136e26f/tiled/utils.py#L526

    Base64-encode raw bytes, and provide a fallback if orjson numpy handling fails.
    """
    import base64
    import sys

    import orjson

    def default(content):
        if isinstance(content, bytes):
            content = f"data:application/octet-stream;base64,{base64.b64encode(content).decode('utf-8')}"
            return content
        if isinstance(content, Path):
            return str(content)
        # No need to import numpy if it hasn't been used already.
        numpy = sys.modules.get("numpy", None)
        if numpy is not None:
            if isinstance(content, numpy.ndarray):
                # If we make it here, OPT_NUMPY_SERIALIZE failed because we have hit some edge case.
                # Give up on the numpy fast-path and convert to Python list.
                # If the items in this list aren't serializable (e.g. bytes) we'll recurse on each item.
                return content.tolist()
            elif isinstance(content, (bytes, numpy.bytes_)):
                return content.decode("utf-8")
        raise TypeError

    # Not all numpy dtypes are supported by orjson.
    # Fall back to converting to a (possibly nested) Python list.
    return orjson.dumps(content, option=orjson.OPT_SERIALIZE_NUMPY, default=default)
