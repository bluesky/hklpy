#!/usr/bin/env pytest

import pytest
# from _pytest.pytester import Testdir as testdir


FOURC_SETUP_CODE = """
from bluesky import plans as bp
from bluesky.simulators import check_limits
from ophyd import (PseudoSingle, SoftPositioner)
from ophyd import Component as Cpt
from ophyd.positioner import LimitError
from warnings import warn
import numpy.testing
import pytest

import gi
gi.require_version('Hkl', '5.0')
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.calc import UnreachableError
from hkl.diffract import E4CV
from hkl.util import Lattice

class Fourc(E4CV):
    h = Cpt(PseudoSingle, '')
    k = Cpt(PseudoSingle, '')
    l = Cpt(PseudoSingle, '')

    omega = Cpt(SoftPositioner)
    chi = Cpt(SoftPositioner)
    phi = Cpt(SoftPositioner)
    tth = Cpt(SoftPositioner)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for p in self.real_positioners:
            p._set_position(0)  # give each a starting position
"""


def test_plain_fourc_ok(testdir):
    test_code = FOURC_SETUP_CODE
    test_code += "\n" + "fourc = Fourc('', name='fourc')"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    result.stderr.no_fnmatch_line("*Fatal Python error*")


def test_extra_real_fatal(testdir):
    test_code = FOURC_SETUP_CODE
    test_code += "\n" + "class FourcSub(Fourc):"
    test_code += "\n" + "    extra = Cpt(SoftPositioner)"
    test_code += "\n" + "fourc = FourcSub('', name='fourc')"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(["*Fatal Python error*"])


def test_extra_real_ok(testdir):
    test_code = FOURC_SETUP_CODE
    test_code += "\n" + "class FourcSub(Fourc):"
    test_code += "\n" + "    _real = ['omega', 'chi', 'phi', 'tth', ]"
    test_code += "\n" + "    extra = Cpt(SoftPositioner)"
    test_code += "\n" + "fourc = FourcSub('', name='fourc')"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    result.stderr.no_fnmatch_line("*Fatal Python error*")


def test_extra_pseudo_TypeError(testdir):
    test_code = FOURC_SETUP_CODE
    test_code += "\n" + "class FourcSub(Fourc):"
    test_code += "\n" + "    extra = Cpt(PseudoSingle, '')"
    test_code += "\n" + "fourc = FourcSub('', name='fourc')"
    test_code += "\n" + "assert fourc.position == (0, 0, 0)"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    result.stderr.no_fnmatch_line(["*Fatal Python error*"])
    result.stdout.fnmatch_lines([
        "*TypeError: __new__() missing 1 required positional argument*"
    ])


def test_extra_pseudo_ok(testdir):
    test_code = FOURC_SETUP_CODE
    test_code += "\n" + "class FourcSub(Fourc):"
    test_code += "\n" + "    _pseudo = ['h', 'k', 'l', ]"
    test_code += "\n" + "    extra = Cpt(PseudoSingle, '')"
    test_code += "\n" + "fourc = FourcSub('', name='fourc')"
    testdir.makepyfile(test_code)
    result = testdir.runpytest_subprocess()
    result.stderr.no_fnmatch_line("*Fatal Python error*")
