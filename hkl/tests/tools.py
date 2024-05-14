"""
Common code, setups, constants, ... for these tests.

Avoids direct imports of __init__.py.
"""

import json
import logging
from pathlib import Path  # noqa

import numpy
from tiled.utils import safe_json_dump

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
