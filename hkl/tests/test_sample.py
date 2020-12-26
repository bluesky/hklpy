import pytest
import numpy.testing

from .class_fourc import fourc
from hkl import sample


def test_compute_UB(fourc):
    fourc.energy.put(8.0)
    r1 = fourc.calc.sample.add_reflection(0, 0, 1, (30, 0, 0, 60))
    r2 = fourc.calc.sample.add_reflection(0, 1, 1, (45, 45, 0, 90))
    result = fourc.calc.sample.compute_UB(r1, r2)
    assert result is not None
    assert isinstance(result, numpy.ndarray)

    r3 = fourc.calc.sample.add_reflection(0, 0, .5, (30/2, 0, 0, 60/2))
    del result
    with pytest.raises(Exception) as exinfo:
        result = fourc.calc.sample.compute_UB(r1, r3)
    assert "given reflections are colinear" in str(exinfo.value)
