# NOTE: MUST call gi.require_version() BEFORE import hkl
import gi

gi.require_version("Hkl", "5.0")


from bluesky import RunEngine
from hkl.calc import A_KEV
from hkl.geometries import SimulatedE4CV
from hkl.geometries import SimulatedK4CV
from ophyd.sim import hw
import bluesky.plan_stubs as bps
import bluesky.plans as bp
import bluesky.preprocessors as bpp
import databroker
import hkl.util
import numpy.testing
import pytest


class Fourc(SimulatedE4CV):
    ...


class Kappa(SimulatedK4CV):
    ...


@pytest.fixture(scope="function")
def fourc():
    fourc = Fourc("", name="fourc")
    fourc.wait_for_connection()
    fourc._update_calc_energy()

    fourc.energy.put(A_KEV / 1.54)
    a0 = 5.4310196
    sample = fourc.calc.new_sample("Si", lattice=(a0, a0, a0, 90, 90, 90))
    r_400 = sample.add_reflection(4, 0, 0, (-145.451, 0, 0, 69.0966))
    r_040 = sample.add_reflection(0, 4, 0, (-145.451, 0, 90, 69.0966))
    fourc.calc.sample.compute_UB(r_400, r_040)

    return fourc


@pytest.fixture(scope="function")
def kappa():
    kappa = Kappa("", name="kappa")
    kappa.wait_for_connection()
    kappa._update_calc_energy()

    kappa.energy.put(A_KEV / 1.54)
    a0 = 5.4310196
    sample = kappa.calc.new_sample("Si", lattice=(a0, a0, a0, 90, 90, 90))
    r_400 = sample.add_reflection(4, 0, 0, (55.4507, 0, 90, -69.0966))
    r_040 = sample.add_reflection(0, 4, 0, (-1.5950, 134.7568, 123.3554, -69.0966))

    kappa.calc.sample.compute_UB(r_400, r_040)

    return kappa


def test_basic_setup(fourc, kappa):
    assert fourc is not None
    assert kappa is not None
    assert fourc != kappa
    assert fourc._reals != kappa._reals

    assert fourc.calc.wavelength == 1.54
    assert fourc.calc.wavelength == kappa.calc.wavelength


def test_fourc_orientation_save(fourc):
    cat = databroker.temp().v2
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)

    assert len(cat) == 0
    det = hw().noisy_det

    # this run will not save orientation information
    _uids = RE(bp.count([det]))
    assert len(_uids) == 1
    assert len(cat) == 1
    assert "fourc" not in cat[1].primary.config

    # this run _will_ save orientation information
    _uids = RE(bp.count([det, fourc]))
    assert len(_uids) == 1
    assert len(cat) == 2
    xarray_data = cat[2].primary.config["fourc"].read()
    assert not isinstance(xarray_data, dict)
    descriptors = xarray_data.to_dict()
    assert isinstance(descriptors, dict)
    assert list(descriptors.keys()) == "coords attrs dims data_vars".split()
    key_list = """
        _pseudos
        _reals
        class_name
        diffractometer_name
        geometry_name
        lattice
        orientation_attrs
        reflections_details
        sample_name
        UB
    """.split()
    for key in key_list:
        key_name = f"fourc_{key}"
        assert hasattr(xarray_data, key_name)
        assert key_name in descriptors["data_vars"]
    assert xarray_data.fourc_class_name == "Fourc"
    assert xarray_data.fourc_geometry_name == "E4CV"
    assert xarray_data.fourc_diffractometer_name == "fourc"
    assert xarray_data.fourc_sample_name == "Si"
    numpy.testing.assert_array_equal(xarray_data.fourc__pseudos, ["h k l".split()])
    numpy.testing.assert_array_equal(xarray_data.fourc__reals, ["omega chi phi tth".split()])


def test_fourc_run_orientation_info(fourc):
    cat = databroker.temp().v2
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)

    _uids = RE(bp.count([fourc]))
    info = hkl.util.run_orientation_info(cat[1])
    assert info is not None
    assert isinstance(info, dict)
    assert "fourc" in info
    fourc_info = info["fourc"]
    assert "orientation_attrs" in fourc_info


def test_list_orientation_runs(fourc, kappa):
    cat = databroker.temp().v2
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)
    det = hw().noisy_det

    def scans():
        yield from bp.count([det])
        yield from bp.count([fourc])
        yield from bp.count([kappa])
        yield from bp.count([fourc, kappa])

    _uids = RE(scans())
    runs = hkl.util.list_orientation_runs(cat)
    # four sets of orientation info
    # (last scan has 2, first scan has none)
    assert len(runs.scan_id) == 4
    assert 1 not in runs.scan_id.to_list() # no orientation
    assert runs.scan_id.to_list() == [2, 3, 4, 4]
    assert runs.diffractometer_name.to_list() == "fourc kappa fourc kappa".split()


def test_restore_orientation(fourc, kappa):
    cat = databroker.temp().v2
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)
    det = hw().noisy_det

    def scans():
        yield from bp.count([det])
        yield from bp.count([fourc])
        yield from bp.count([kappa])
        yield from bp.count([fourc, kappa])

    _uids = RE(scans())
    assert len(_uids) == 4

    info = hkl.util.run_orientation_info(cat[2])
    e4cv = Fourc("", name="e4cv")
    # TODO: This should succeed.
    # hkl.util.restore_orientation(info["fourc"], e4cv)

    k4cv = Kappa("", name="k4cv")
    # TODO: This should fail with ValueError exception.
    # hkl.util.restore_orientation(info["fourc"], k4cv)
