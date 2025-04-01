"""
ValueError from run.primary.read() with reflections.

2025-03-31

User reports receiving a ``ValueError: different number of dimensions on data
and dims: 3 vs 2`` when using a diffractometer with a Bluesky run. However, the
older v1 API Table (``cat.v1["3d837ad1"].table()``) has no such exception and
produces useful info.

The error is reproducible. No error (from ``run.primary.read()``) from a run when no
reflections are defined. Once at least one reflection is defined, then the
ValueError is raised.
"""

from contextlib import nullcontext as does_not_raise

import databroker
from bluesky import RunEngine
from bluesky import plans as bp
from ophyd.sim import noisy_det

from .. import SimulatedE4CV
from ..diffract import Diffractometer
from ..util import run_orientation_info

cat = databroker.temp().v2
RE = RunEngine()
RE.subscribe(cat.v1.insert)


def test_i350():
    e4cv = SimulatedE4CV("", name="e4cv")
    assert isinstance(e4cv, Diffractometer)

    with does_not_raise():
        # None of these actions should raise an exception
        e4cv.calc.new_sample("STO", (3.905, 3.905, 3.905, 90, 90, 90))
        e4cv.forward(0, 0, 1)
        (uid,) = RE(bp.scan([noisy_det, e4cv], e4cv.omega, 1, 0, 5))
        cat.v1[uid].table()
        run = cat[uid]
        run.primary.read()
        info = run_orientation_info(run)
        assert e4cv.name in info

    # ValueError: different number of dimensions on data and dims: 3 vs 2
    # Happens when one or more reflections are added.
    r1 = e4cv.calc.sample.add_reflection(0, 0, 1, (11.45, -90, 0, 22.91))
    r2 = e4cv.calc.sample.add_reflection(0, 1, 0, (11.45, 0, 0, 22.91))
    e4cv.calc.sample.compute_UB(r1, r2)
    e4cv.forward(0, 0, 1)
    (uid,) = RE(bp.scan([noisy_det, e4cv], e4cv.omega, 1, 0, 5))
    cat.v1[uid].table()
    run = cat[uid]

    # with pytest.raises(ValueError) as exinfo:  # original problem
    #     run.primary.read()
    # assert "different number of dimensions on data and dims" in str(exinfo)

    # Test that the problem has been fixed.
    with does_not_raise():
        descriptor = run._descriptors[0]
        # When this key is in the descriptor, ``run.primary.read()`` fails.
        problem_key = f"{e4cv.name}_reflections"
        assert problem_key not in descriptor["configuration"][e4cv.name]
        run.primary.read()

    info = run_orientation_info(run)
    assert e4cv.name in info
