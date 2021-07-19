# NOTE: MUST call gi.require_version() BEFORE import hkl
import gi

gi.require_version("Hkl", "5.0")


from bluesky import RunEngine
from hkl.calc import A_KEV
from hkl import SimulatedE4CV
from hkl import SimulatedK4CV
from hkl import SI_LATTICE_PARAMETER
from ophyd.sim import hw
import bluesky.plans as bp
import databroker
import hkl.util
import numpy.testing
import pytest


class Fourc(SimulatedE4CV):
    ...


class Kappa(SimulatedK4CV):
    ...


@pytest.fixture
def cat():
    return databroker.temp().v2


@pytest.fixture
def RE(cat):
    engine = RunEngine({})
    engine.subscribe(cat.v1.insert)
    return engine


@pytest.fixture(scope="function")
def fourc():
    fourc = Fourc("", name="fourc")
    fourc.wait_for_connection()
    fourc._update_calc_energy()

    fourc.energy.put(A_KEV / 1.54)
    a0 = SI_LATTICE_PARAMETER
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
    a0 = SI_LATTICE_PARAMETER
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


def test_fourc_orientation_save(cat, RE, fourc):
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

    assert len(xarray_data.fourc__pseudos) == 1
    assert xarray_data.fourc__pseudos[0].values.tolist() == "h k l".split()
    assert len(xarray_data.fourc__reals) == 1
    assert xarray_data.fourc__reals.values[0].tolist() == "omega chi phi tth".split()


def test_fourc_run_orientation_info(cat, RE, fourc):
    RE(bp.count([fourc]))
    info = hkl.util.run_orientation_info(cat[1])
    assert info is not None
    assert isinstance(info, dict)
    assert "fourc" in info
    fourc_orient = info["fourc"]
    assert "orientation_attrs" in fourc_orient
    assert "reflections_details" in fourc_orient["orientation_attrs"]
    assert "reflections_details" in fourc_orient
    refls = fourc_orient["reflections_details"]
    assert len(refls) == 2
    assert "wavelength" in refls[0]
    assert refls[0]["wavelength"] == 1.54


def test_list_orientation_runs(cat, RE, fourc, kappa):
    det = hw().noisy_det

    def scans():
        yield from bp.count([det])
        yield from bp.count([fourc])
        yield from bp.count([kappa])
        yield from bp.count([fourc, kappa])

    RE(scans())
    runs = hkl.util.list_orientation_runs(cat)
    # four sets of orientation info
    # (last scan has 2, first scan has none)
    assert len(runs.scan_id) == 4
    assert 1 not in runs.scan_id.to_list()  # no orientation
    assert runs.scan_id.to_list() == [2, 3, 4, 4]
    assert runs.diffractometer_name.to_list() == "fourc kappa fourc kappa".split()


def test_restore_orientation(cat, RE, fourc):
    RE(bp.count([fourc]))
    fourc_orient = hkl.util.run_orientation_info(cat[-1])["fourc"]

    e4cv = Fourc("", name="e4cv")
    assert len(e4cv.calc._samples) == 1

    # typical case : good match, restores successfully
    hkl.util.restore_orientation(fourc_orient, e4cv)
    assert len(e4cv.calc._samples) == 2
    sample = e4cv.calc.sample
    assert sample.name == "Si"
    assert len(sample.reflections) == 2
    numpy.testing.assert_array_equal(sample.reflections, [[4, 0, 0], [0, 4, 0]])
    # fmt: off
    numpy.testing.assert_array_almost_equal(
        fourc.calc.sample.UB,
        e4cv.calc.sample.UB,
    )
    # fmt: on

    # geometry mismatch, cannot restore
    k4cv = Kappa("", name="k4cv")
    assert len(k4cv.calc._samples) == 1
    assert len(k4cv.calc.sample.reflections) == 0
    with pytest.raises(ValueError) as exinfo:
        hkl.util.restore_orientation(fourc_orient, k4cv)
    args = exinfo.value.args
    assert len(args) == 1
    expected = "Geometries do not match: Orientation=E4CV, k4cv=K4CV, will not restore."
    assert args[0] == expected

    # different class name, restores successfully
    e4cv = SimulatedE4CV("", name="e4cv")
    assert len(e4cv.calc._samples) == 1
    assert len(e4cv.calc.sample.reflections) == 0
    hkl.util.restore_orientation(fourc_orient, e4cv)
    assert len(e4cv.calc._samples) == 2
    assert len(e4cv.calc.sample.reflections) == 2
    # fmt: off
    numpy.testing.assert_array_almost_equal(
        fourc.calc.sample.UB,
        e4cv.calc.sample.UB,
    )
    # fmt: on

    # different real axis names, restores successfully
    e4cv = Fourc("", name="e4cv")
    # change the real axis names
    e4cv.calc.physical_axis_names = {
        "omega": "john",
        "chi": "paul",
        "phi": "george",
        "tth": "ringo",
    }
    assert len(e4cv.calc._samples) == 1
    assert len(e4cv.calc.sample.reflections) == 0
    hkl.util.restore_orientation(fourc_orient, e4cv)
    assert len(e4cv.calc._samples) == 2
    assert len(e4cv.calc.sample.reflections) == 2
    # fmt: off
    numpy.testing.assert_array_almost_equal(
        fourc.calc.sample.UB,
        e4cv.calc.sample.UB,
    )
    # fmt: on


def test_restore_sample(cat, RE, fourc):
    RE(bp.count([fourc]))
    fourc_orient = hkl.util.run_orientation_info(cat[-1])["fourc"]

    # Add sample to new diffractometer.
    e4cv = Fourc("", name="e4cv")
    hkl.util.restore_sample(fourc_orient, e4cv)
    assert len(e4cv.calc._samples) == 2
    assert len(e4cv.calc.sample.reflections) == 0
    assert e4cv.calc.sample.name == fourc.calc.sample.name

    # Sample already defined, will not make another.
    with pytest.raises(ValueError) as exinfo:
        hkl.util.restore_sample(fourc_orient, e4cv)
    expected = "Sample 'Si' already exists in e4cv."
    assert exinfo.value.args[0] == expected
