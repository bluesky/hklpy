import gi
from ophyd import Component as Cpt
from ophyd import PseudoSingle

gi.require_version("Hkl", "5.0")
from hkl import SimulatedE4CV


class Fourc(SimulatedE4CV):
    ...


FOURC_SETUP_CODE = """
from ophyd import Component as Cpt
from ophyd import SoftPositioner
import gi
gi.require_version('Hkl', '5.0')
from hkl import SimulatedE4CV

class Fourc(SimulatedE4CV):
    ...
"""


def test_plain_fourc_not_fatal(testdir):
    test_code = FOURC_SETUP_CODE
    test_code += "\n" + "fourc = Fourc('', name='fourc')"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    result.stderr.no_fnmatch_line("*Fatal Python error*")


def test_extra_real_but_not_fatal(testdir):
    test_code = FOURC_SETUP_CODE
    test_code += "\n" + "class FourcSub(Fourc):"
    test_code += "\n" + "    extra = Cpt(SoftPositioner, init_pos=0)"
    test_code += "\n" + "fourc = FourcSub('', name='fourc')"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    # result.stderr.no_fnmatch_line("*Fatal Python error*")
    result.stderr.str().startswith("Fatal Python error: Aborted")


def test_extra_real_not_fatal(testdir):
    test_code = FOURC_SETUP_CODE
    test_code += "\n" + "class FourcSub(Fourc):"
    test_code += "\n" + "    _real = ['omega', 'chi', 'phi', 'tth', ]"
    test_code += "\n" + "    extra = Cpt(SoftPositioner, init_pos=0)"
    test_code += "\n" + "fourc = FourcSub('', name='fourc')"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    result.stderr.no_fnmatch_line("*Fatal Python error*")


def test_extra_pseudo_not_fatal(testdir):
    test_code = FOURC_SETUP_CODE + "\n"
    test_code += "class FourcSub(Fourc):" + "\n"
    test_code += "    _pseudo = ['h', 'k', 'l', ]" + "\n"
    test_code += "    extra = Cpt(PseudoSingle, '')" + "\n"
    test_code += "fourc = FourcSub('', name='fourc')" + "\n"
    test_code += "print(fourc.position)" + "\n"
    test_code += "print(fourc.extra.position)" + "\n"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    result.stderr.no_fnmatch_line("*Fatal Python error*")


def test_fourc_position():
    fourc = Fourc("", name="fourc")
    assert fourc.position == (0, 0, 0)


def test_fourc_extra_pseudo():
    class FourcSub(Fourc):
        _pseudo = "h k l".split()
        p_extra = Cpt(PseudoSingle, "")

    fourc = FourcSub("", name="fourc")
    assert fourc.position == (0, 0, 0)
    assert hasattr(fourc.p_extra, "_idx")
    # TODO: this feature is broken in ophyd at this time
    # https://github.com/bluesky/hklpy/issues/48
    # https://github.com/bluesky/ophyd/issues/924
    assert fourc.p_extra._idx is None
