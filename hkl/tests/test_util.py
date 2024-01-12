"""Test the hkl.util module."""

import json
import time

import databroker
import pytest
from bluesky import plans as bp
from bluesky.run_engine import RunEngine
from packaging import version
from tiled.utils import safe_json_dump

from .. import util
from .tools import DocsCollector
from .tools import validate_descriptor_doc_content

NO_SUCH_PACKAGE_NAME = "no-such-package"


@pytest.fixture(scope="function")
def cat():
    yield databroker.temp().v2


@pytest.fixture(scope="function")
def RE(cat):
    import bluesky

    engine = bluesky.RunEngine()
    engine.subscribe(cat.v1.insert)
    yield engine


@pytest.fixture(scope="function")
def fourc():
    """4-circle with renamed axes and oriented sample."""
    from ophyd import Component
    from ophyd import SoftPositioner

    from hkl import E4CV
    from hkl import SimMixin

    class FourCircle(SimMixin, E4CV):
        theta = Component(SoftPositioner, kind="hinted", init_pos=0)
        chi = Component(SoftPositioner, kind="hinted", init_pos=0)
        phi = Component(SoftPositioner, kind="hinted", init_pos=0)
        ttheta = Component(SoftPositioner, kind="hinted", init_pos=0)

    fourc = FourCircle("", name="fourc")
    # rename the physical axes
    fourc.calc.physical_axis_names = {
        # E4CV: local
        "omega": "theta",
        "chi": "chi",
        "phi": "phi",
        "tth": "ttheta",
    }

    # fourc.wait_for_connection()
    fourc._update_calc_energy()
    crystal_setup(fourc)

    yield fourc


def crystal_setup(diffractometer):
    from hkl import Lattice

    diffractometer.calc.wavelength = 1.0
    a0 = 5.4321
    # fmt: off
    diffractometer.calc.new_sample(
        "vibranium",
        lattice=Lattice(a=a0, b=a0, c=a0, alpha=90, beta=90, gamma=90)
    )

    diffractometer.calc.sample.add_reflection(
        1, 2, 3,
        position=diffractometer.calc.Position(
            ttheta=60,
            theta=40,
            chi=0,
            phi=0,
        ),
    )
    # fmt: on


def test__package_info_states():
    assert util._package_info is None
    util.get_package_info("hkl")
    assert util._package_info is not None


@pytest.mark.parametrize(
    "package_name, minimum_version",
    [
        ("bluesky", "1.6"),
        ("pygobject", "3.40"),
        ("hkl", "5.0.0"),
        ("hklpy", "0"),  # minimum test for unversioned use
        (NO_SUCH_PACKAGE_NAME, "---"),
        # ("ophyd", "1.6"),  conda has right version but pip has 0.0.0
    ],
)
def test_get_package_info(package_name, minimum_version):
    v = util.get_package_info(package_name)
    if v is None:
        assert package_name in ("hklpy", NO_SUCH_PACKAGE_NAME)
    else:
        assert "version" in v
        v_string = v.get("version", "unknown")

        if package_name == "hkl":
            assert v_string.startswith("5.0.0.")

        v_package = version.parse(v_string)
        assert v_package >= version.parse(minimum_version)


@pytest.mark.parametrize(
    # fmt: off
    "case",
    [
        (None),
        ([]),
        ("")
    ],
    # fmt: on
)
def test_software_versions_default_list(case):
    v = util.software_versions(case)
    assert isinstance(v, dict)
    expected = sorted(util.DEFAULT_PACKAGE_LIST)
    assert sorted(v.keys()) == expected


@pytest.mark.parametrize(
    "package_name, minimum_version",
    [
        ("bluesky", "1.6"),
        ("pygobject", "3.40"),
        ("hkl", "5.0.0"),
        ("hklpy", "0"),  # minimum test for unversioned use
        (NO_SUCH_PACKAGE_NAME, "---"),
        # ("ophyd", "1.6"),  conda has right version but pip has 0.0.0
    ],
)
def test_software_versions_items(package_name, minimum_version):
    v = util.software_versions([package_name])
    if package_name in v:
        v_string = v[package_name]
        v_package = version.parse(v_string)
        assert v_package >= version.parse(minimum_version)
    else:
        assert package_name in ("hklpy", NO_SUCH_PACKAGE_NAME)


def test_issue215(cat, RE, fourc):
    """restore_reflections(orientation, fourc) cannot find renamed positioner."""
    from bluesky import plans as bp

    canonical_names = "omega chi phi tth".split()
    our_names = "theta chi phi ttheta".split()
    assert our_names != canonical_names
    assert fourc.calc.physical_axis_names != canonical_names
    assert fourc.calc.physical_axis_names == our_names

    problem_reflection_dict = {
        "reflection": {"h": 1.0, "k": -3.0, "l": -1.0},
        "flag": 1,
        "wavelength": 1.1169734383241103,
        "position": {
            "omega": -8.208399999999983,
            "chi": -47.47651999999994,
            "phi": -5.684341886080802e-14,
            "tth": 25.09473789610388,
        },
        "orientation_reflection": False,
    }
    problem_positioner_names = list(problem_reflection_dict["position"].keys())
    assert problem_positioner_names == canonical_names

    assert len(cat) == 0
    uids = RE(bp.count([fourc]))
    time.sleep(1)
    assert len(uids) == 1
    assert len(cat) == 1

    orientation = util.run_orientation_info(cat[-1])
    assert isinstance(orientation, dict)
    assert fourc.name in orientation
    # assert list(orientation.keys()) == []

    orient = orientation[fourc.name]
    assert orient["_reals"] != canonical_names
    assert orient["_reals"] == our_names
    for reflection in orient["reflections_details"]:
        assert list(reflection["position"].keys()) == canonical_names

    success = False
    try:
        # since it is just a problem of motor names in reflections ...
        util.restore_reflections(orient, fourc)
        success = True
    finally:
        assert success, "Could not restore orientation reflections."


@pytest.mark.parametrize("use_refl", [None, "short", "long"])
def test_RE_documents(use_refl, e4cv):
    """Issue #316."""

    docs = DocsCollector()  # capture the raw document stream directly
    assert len(docs.raw) == 0

    # add a reflection?
    if use_refl == "short":
        e4cv.calc.sample.add_reflection(1, 2, 3, (40, 0, 0, 60))
    elif use_refl == "long":
        # fmt: off
        e4cv.calc.sample.add_reflection(
            1, 2, 3,
            position=e4cv.calc.Position(tth=60, omega=40, chi=0, phi=0),
        )
        # fmt: on
    refs = e4cv.reflections.get()
    assert isinstance(refs, list)
    assert len(refs) == len(e4cv.calc.sample.reflections)
    if len(refs) > 0:
        assert list(refs[0]) == [1.0, 2.0, 3.0]

    safe = safe_json_dump(refs)
    assert isinstance(safe, bytes)

    assert isinstance(safe_json_dump(e4cv.reflections_details.get()), bytes)
    # assert f"{refs=!r}" == "debug"

    RE = RunEngine()
    cat = databroker.temp().v2
    RE.subscribe(cat.v1.insert)

    uids = RE(bp.count([e4cv]), docs.receiver)
    assert len(uids) == 1
    assert len(docs.raw) == 4

    # Get the configuration from the raw document stream
    validate_descriptor_doc_content(e4cv.name, docs.raw.get("descriptor"))

    # Get the configuration from the safe_json version of the document stream
    # difference: np.ndarray --> list
    # difference: tuple --> list
    descriptor = docs.safe_json.get("descriptor")
    assert isinstance(descriptor, bytes)
    validate_descriptor_doc_content(e4cv.name, json.loads(docs.safe_json.get("descriptor")))

    # Get the configuration from the databroker document stream
    for key, doc in cat.v1[uids[0]].documents():
        if key == "descriptor":
            validate_descriptor_doc_content(e4cv.name, doc)

    orientation = util.run_orientation_info(cat[uids[0]])
    assert isinstance(orientation, dict)
    assert e4cv.name in orientation
