import gi
gi.require_version("Hkl", "5.0")
# import pytest

# FIXME: comment remainder for now until #185 is resolved

def test_true():
    assert True
    # FIXME: remove when #185 is solved.

# from hkl.util import get_package_info, _package_info


# def test__package_info_states():
#     assert _package_info is None
#     get_package_info()
#     assert _package_info is not None


# def test_get_package_info():
#     v = get_package_info("hkl")
#     assert v.startswith("5.0.0.")
#     assert get_package_info("no-such-package") is None
#     # TODO: assert get_package_info("hklpy")["version"] >= "0.3.16"


# def test_software_versions_default():
#     v = software_versions()
#     assert v["hkl"].startswith("5.0.0.")
#     # TODO: assert v.get("no-such-package") is None
#     # TODO: assert v.get("hklpy") >= "0.3.16"

