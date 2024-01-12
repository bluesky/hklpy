"""
Common code, setups, constants, ... for these tests.

Avoids direct imports of __init__.py.
"""

import logging

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

    assert isinstance(data[f"{gname}_sample_name"], str)
    assert isinstance(data[f"{gname}_lattice"], (numpy.ndarray, list))
    assert isinstance(data[f"{gname}_lattice_reciprocal"], (tuple, list))
    assert isinstance(data[f"{gname}_U"], (numpy.ndarray, list))
    assert isinstance(data[f"{gname}_UB"], (numpy.ndarray, list))
    assert isinstance(data[f"{gname}_reflections_details"], list)
    assert isinstance(data[f"{gname}__pseudos"], (tuple, list))
    assert isinstance(data[f"{gname}__reals"], (tuple, list))
    assert isinstance(data[f"{gname}__constraints"], (numpy.ndarray, list))
    assert isinstance(data[f"{gname}_ux"], float)
    assert isinstance(data[f"{gname}_uy"], float)
    assert isinstance(data[f"{gname}_uz"], float)
    assert isinstance(data[f"{gname}_orientation_attrs"], list)
