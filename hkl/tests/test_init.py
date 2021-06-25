import gi
import pytest


gi.require_version("Hkl", "5.0")
# NOTE: MUST call gi.require_version() BEFORE any import from hkl

import hkl
import hkl.calc
import hkl.diffract
import hkl.geometries
import hkl.user
import hkl.util


@pytest.mark.parametrize(
    "module_name, attribute",
    [
        ("calc", "A_KEV"),
        ("calc", "UnreachableError"),
        ("geometries", "E4CH"),
        ("geometries", "E4CV"),
        ("geometries", "E6C"),
        ("geometries", "K4CV"),
        ("geometries", "K6C"),
        ("geometries", "Petra3_p09_eh2"),
        ("geometries", "SimMixin"),
        ("geometries", "SimulatedE4CV"),
        ("geometries", "SimulatedE6C"),
        ("geometries", "SimulatedK4CV"),
        ("geometries", "SimulatedK6C"),
        ("geometries", "SoleilMars"),
        ("geometries", "SoleilSiriusKappa"),
        ("geometries", "SoleilSiriusTurret"),
        ("geometries", "SoleilSixsMed1p2"),
        ("geometries", "SoleilSixsMed2p2"),
        ("geometries", "SoleilSixsMed2p3"),
        ("geometries", "Zaxis"),
        ("user", "cahkl_table"),
        ("user", "cahkl"),
        ("user", "calc_UB"),
        ("user", "change_sample"),
        ("user", "list_samples"),
        ("user", "new_sample"),
        ("user", "or_swap"),
        ("user", "pa"),
        ("user", "select_diffractometer"),
        ("user", "set_energy"),
        ("user", "setor"),
        ("user", "show_sample"),
        ("user", "show_selected_diffractometer"),
        ("user", "update_sample"),
        ("user", "wh"),
        ("util", "Constraint"),
        ("util", "diffractometer_types"),
        ("util", "get_position_tuple"),
        ("util", "Lattice"),
        ("util", "list_orientation_runs"),
        ("util", "list_orientation_runs"),
        ("util", "restore_constraints"),
        ("util", "restore_energy"),
        ("util", "restore_orientation"),
        ("util", "restore_reflections"),
        ("util", "restore_reflections"),
        ("util", "restore_UB"),
        ("util", "run_orientation_info"),
        ("util", "software_versions"),
    ],
)
def test_shortcuts(module_name, attribute):
    assert hasattr(hkl, module_name)
    module = getattr(hkl, module_name)

    assert hasattr(module, attribute)
    actual = getattr(module, attribute)

    assert hasattr(hkl, attribute)
    shortcut = getattr(hkl, attribute)

    assert shortcut is actual
