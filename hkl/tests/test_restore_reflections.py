"""
Test that reflections from one sample are not restored to other samples.
"""

from .. import DiffractometerConfiguration
from .tools import sample_kryptonite
from .tools import sample_silicon
from .tools import sample_vibranium


def test_issue289(e4cv):
    assert e4cv is not None

    # setup four samples with reflections, all of them different
    main = e4cv.calc.sample  # the default sample
    assert len(main.reflections) == 0
    m_100 = main.add_reflection(1, 0, 0, (-45, 0, 0, 0))
    m_010 = main.add_reflection(0, 1, 0, (45, 0, 0, 0))
    main.compute_UB(m_100, m_010)

    kryptonite = sample_kryptonite(e4cv)
    assert len(kryptonite.reflections) == 0
    k_200 = kryptonite.add_reflection(2, 0, 0, (30, 0, 10, 60))
    k_020 = kryptonite.add_reflection(0, 2, 0, (30, 90, 10, 60))
    kryptonite.compute_UB(k_200, k_020)

    vibranium = sample_vibranium(e4cv)
    assert len(vibranium.reflections) == 0
    v_003 = vibranium.add_reflection(0, 0, 3, (20.33, 4.33, 8.33, 40.33))
    v_033 = vibranium.add_reflection(0, 3, 3, (20.33, -94.33, 8.33, 40.33))
    vibranium.compute_UB(v_003, v_033)

    silicon = sample_silicon(e4cv)
    assert len(silicon.reflections) == 0
    s_440 = silicon.add_reflection(4, 4, 0, (34, 44, 54, 64))
    s_444 = silicon.add_reflection(4, 4, 4, (34, 134, 54, 64))
    silicon.compute_UB(s_440, s_444)

    n_saved_reflections = 2
    assert len(main.reflections) == n_saved_reflections
    assert len(kryptonite.reflections) == n_saved_reflections
    assert len(silicon.reflections) == n_saved_reflections
    assert len(vibranium.reflections) == n_saved_reflections
    # same test, using diffractometer sample dictionary now.
    for sample in e4cv.calc._samples.values():
        assert len(sample.reflections) == n_saved_reflections, f"{sample.name=}"
    assert len(e4cv.calc._samples) == 4

    agent = DiffractometerConfiguration(e4cv)
    assert agent is not None
    config = agent.export()
    assert isinstance(config, str)

    # Restore the configuration without clearing the diffractometer first.
    # This should not change the number of samples or the number of
    # reflections for any of the samples.
    agent.restore(config, clear=False)

    assert len(e4cv.calc._samples) == 4
    for sample in e4cv.calc._samples.values():
        assert len(sample.reflections) == 2 * n_saved_reflections
