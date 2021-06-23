import gi

gi.require_version("Hkl", "5.0")
import pytest

import hkl.util
from packaging import version


NO_SUCH_PACKAGE_NAME = "no-such-package"


def test__package_info_states():
    assert hkl.util._package_info is None
    hkl.util.get_package_info("hkl")
    assert hkl.util._package_info is not None


@pytest.mark.parametrize(
    "package_name, minimum_version",
    [
        ("bluesky", "1.6"),
        ("gobject-introspection", "1.68.0"),
        ("hkl", "5.0.0"),
        ("hklpy", "0"),  # minimum test for unversioned use
        (NO_SUCH_PACKAGE_NAME, "---"),
        ("ophyd", "1.6"),
    ],
)
def test_get_package_info(package_name, minimum_version):
    v = hkl.util.get_package_info(package_name)
    if v is None:
        assert package_name == NO_SUCH_PACKAGE_NAME
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
    v = hkl.util.software_versions(case)
    assert isinstance(v, dict)
    expected = sorted(hkl.util.DEFAULT_PACKAGE_LIST)
    assert sorted(v.keys()) == expected


@pytest.mark.parametrize(
    "package_name, minimum_version",
    [
        ("bluesky", "1.6"),
        ("gobject-introspection", "1.68.0"),
        ("hkl", "5.0.0"),
        ("hklpy", "0"),  # minimum test for unversioned use
        (NO_SUCH_PACKAGE_NAME, "---"),
        ("ophyd", "1.6"),
    ],
)
def test_software_versions_items(package_name, minimum_version):
    v = hkl.util.software_versions([package_name])
    if package_name in v:
        v_string = v[package_name]
        v_package = version.parse(v_string)
        assert v_package >= version.parse(minimum_version)
    else:
        assert package_name == NO_SUCH_PACKAGE_NAME
