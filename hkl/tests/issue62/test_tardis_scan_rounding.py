"""
test for rounding issue with a tardis scan (NSLS-II)

Testing here with simulated positioners since that does
not require an EPICS IOC.
"""


from ophyd import Component as Cpt
from ophyd import PseudoSingle
from ophyd import SoftPositioner
import gi
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

# required BEFORE importing any hkl modules
gi.require_version("Hkl", "5.0")

from hkl.diffract import E6C
from hkl.util import Lattice


class SimTardis(E6C):
    h = Cpt(PseudoSingle, "")
    k = Cpt(PseudoSingle, "")
    l = Cpt(PseudoSingle, "")

    # theta
    theta = Cpt(SoftPositioner)
    mu = Cpt(SoftPositioner)
    chi = Cpt(SoftPositioner)
    phi = Cpt(SoftPositioner)
    # delta, gamma
    delta = Cpt(SoftPositioner)
    gamma = Cpt(SoftPositioner)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for p in self.real_positioners:
            p._set_position(0)  # give each a starting position


@pytest.fixture(scope="function")
def tardis():
    tardis = SimTardis("", name="tardis")
    # re-map Tardis' axis names onto what an E6C expects
    tardis.calc.physical_axis_names = {
        "mu": "theta",
        "omega": "mu",
        "chi": "chi",
        "phi": "phi",
        "gamma": "delta",
        "delta": "gamma",
    }
    tardis.wait_for_connection()
    tardis.calc.engine.mode = "lifting_detector_mu"
    return tardis


def sample1(tardis):
    # from supplied tardis.txt
    # https://github.com/bluesky/bluesky/issues/1196#issuecomment-500955292

    tardis.calc.new_sample(
        "test sample",
        lattice=Lattice(
            a=9.069, b=9.069, c=10.390, alpha=90.0, beta=90.0, gamma=120.0
        ),
    )

    tardis.calc.wavelength = 1.61198  # angstroms
    tardis.energy_units.put("eV")

    r1 = tardis.calc.sample.add_reflection(
        3, 3, 0,
        position=tardis.calc.Position(
            delta=64.449,
            theta=25.285,
            chi=0.0,
            phi=0.0,
            mu=0.0,
            gamma=-0.871,
        ),
    )

    r2 = tardis.calc.sample.add_reflection(
        5, 2, 0,
        position=tardis.calc.Position(
            delta=79.712,
            theta=46.816,
            chi=0.0,
            phi=0.0,
            mu=0.0,
            gamma=-1.374,
        ),
    )

    tardis.calc.sample.compute_UB(r1, r2)


def sample2(tardis):
    # from supplied tardis2.txt
    # https://github.com/bluesky/bluesky/issues/1196#issuecomment-500994794

    a0 = 4.128
    tardis.calc.new_sample(
        "sample_1",
        lattice=Lattice(
            a=a0, b=a0, c=a0, alpha=90.0, beta=90.0, gamma=90.0
        ),
    )

    tardis.energy_units.put("eV")
    tardis.energy_offset.put(1)
    tardis.energy.put(572)

    r14_20K_th0 = tardis.calc.sample.add_reflection(
        1, 1, 0,
        position=tardis.calc.Position(
            theta=52.8806-2.1039, mu=0.0, chi=0.0,
            phi=0.0, delta=107.411, gamma=-3.75)) #this might be -3.25
    r15_20K_th0 = tardis.calc.sample.add_reflection(
        1, 1, 1,
        position=tardis.calc.Position(
            theta=115.3521-2.1039, mu=0.0, chi=0.0,
            phi=0.0, delta=161.9392, gamma=-3.8716))

    tardis.calc.sample.compute_UB(r14_20K_th0, r15_20K_th0)


@pytest.fixture(scope="function")
def constrain(tardis):
    calc = tardis.calc
    # apply some constraints
    calc["theta"].limits = (-181, 181)
    calc["theta"].value = 0
    calc["theta"].fit = True

    # we don't have it!! Fix to 0
    calc["mu"].limits = (0, 0)
    calc["mu"].value = 0
    calc["mu"].fit = False

    # we don't have it. Fix to 0
    calc["chi"].limits = (0, 0)
    calc["chi"].value = 0
    calc["chi"].fit = False

    # we don't have it. Fix to 0
    calc["phi"].limits = (0, 0)
    calc["phi"].value = 0
    calc["phi"].fit = False

    # Attention naming convention inverted at the detector stages!
    # delta
    calc["delta"].limits = (-5, 180)
    calc["delta"].value = 0
    calc["delta"].fit = True

    # gamma
    calc["gamma"].limits = (-5, 180)
    calc["gamma"].value = 0
    calc["gamma"].fit = True


def test_rounding_issue(tardis, constrain):
    sample1(tardis)
    tolerance = 0.001  # this is what we might expect

    def check(h, k, l, delta, theta, mu, chi, phi, gamma):
        expect = dict(
            theta=theta, mu=mu, chi=chi, phi=phi, delta=delta, gamma=gamma
        )
        pos = tardis.forward(h, k, l)
        for nm, v in expect.items():
            calc = getattr(pos, nm)
            msg = f"({h}, {k}, {l}): {calc} !~ {v} within {tolerance}"
            assert abs(calc - v) <= tolerance, msg

    tolerance = 0.12  # this is what works

    # Experimentally found reflections @ Lambda = 1.61198 A
    # NOTE:        delta   theta   mu chi phi gamma
    # (4, 4, 0) = [90.628, 38.373, 0, 0, 0, -1.156]
    # (4, 1, 0) = [56.100, 40.220, 0, 0, 0, -1.091]
    # @ Lambda = 1.60911
    # (6, 0, 0) = [75.900, 61.000, 0, 0, 0, -1.637]
    # @ Lambda = 1.60954
    # (3, 2, 0) = [53.090, 26.144, 0, 0, 0, -.933]
    # (5, 4, 0) = [106.415, 49.900, 0, 0, 0, -1.535]
    # (4, 5, 0) = [106.403, 42.586, 0, 0, 0, -1.183]
    tardis.calc.wavelength = 1.61198
    check(4, 4, 0, 90.628, 38.373, 0, 0, 0, -1.156)
    check(4, 1, 0, 56.100, 40.220, 0, 0, 0, -1.091)

    tardis.calc.wavelength = 1.60911
    check(6, 0, 0, 75.900, 61.000, 0, 0, 0, -1.637)

    tardis.calc.wavelength = 1.60954
    check(3, 2, 0, 53.090, 26.144, 0, 0, 0, -0.933)
    check(5, 4, 0, 106.415, 49.900, 0, 0, 0, -1.535)
    check(4, 5, 0, 106.403, 42.586, 0, 0, 0, -1.183)


def interpret_LiveTable(text, prefix="tardis_"):
    rows = text.strip().splitlines()
    labels = rows[1].replace("|", " ").strip().split()
    # only pick out the columns that start with the prefix
    xref = {
        nm[len(prefix):] : i
        for i, nm in enumerate(labels)
        if nm.startswith(prefix)
    }
    data = {
        k: []
        for k in xref.keys()
    }
    for row in rows[3:-1]:
        values = row.replace("|", " ").strip().split()
        for k, column in xref.items():
            data[k].append(float(values[column]))
    return data


def test_tardis2(tardis, constrain):
    tardis.calc['gamma'].limits = (-2.81, 183.1)
    sample2(tardis)
    tolerance = 0.01    # goal

    assert round(tardis.calc.energy, 5) == 0.573

    # simulate the scan, computing hkl from angles
    # RE(scan([hw.det, tardis],tardis.theta, 0, 0.3, tardis.delta,0,0.5, num=5))
    # values as reported from LiveTable
    data = """
    +-----------+------------+--------------+--------------+------------+------------+------------+------------+--------------+
    |   seq_num |       time | tardis_theta | tardis_delta |        det |   tardis_h |   tardis_k |   tardis_l | tardis_gamma |
    +-----------+------------+--------------+--------------+------------+------------+------------+------------+--------------+
    |         1 | 15:09:51.6 |        0.000 |        0.000 |      1.000 |      0.000 |      0.000 |      0.000 |        0.000 |
    |         2 | 15:09:52.2 |        0.075 |        0.125 |      1.000 |     -0.006 |      0.013 |      0.000 |        0.000 |
    |         3 | 15:09:52.8 |        0.150 |        0.250 |      1.000 |     -0.013 |      0.026 |      0.000 |        0.000 |
    |         4 | 15:09:53.5 |        0.225 |        0.375 |      1.000 |     -0.019 |      0.038 |      0.000 |        0.000 |
    |         5 | 15:09:54.0 |        0.300 |        0.500 |      1.000 |     -0.025 |      0.051 |      0.000 |        0.000 |
    +-----------+------------+--------------+--------------+------------+------------+------------+------------+--------------+
    """
    a = interpret_LiveTable(data)
    tolerance = 0.05    # empirical
    mu, chi, phi = 0, 0, 0  # constant
    targets = list(zip(a["theta"], a["delta"], a["gamma"], a["h"], a["k"], a["l"]))
    for theta, delta, gamma, h, k, l in targets:
        ref = tardis.inverse(theta, mu, chi, phi, delta, gamma)
        assert abs(ref.h - h) <= tolerance
        assert abs(ref.k - k) <= tolerance
        assert abs(ref.l - l) <= tolerance

    # check values reported by tardis.read()
    h = .1
    k = .51
    l = 0
    theta = 41.996
    delta = 6.410
    gamma = 0
    ref = tardis.inverse(theta, mu, chi, phi, delta, gamma)
    assert abs(ref.h - h) <= tolerance
    assert abs(ref.k - k) <= tolerance
    assert abs(ref.l - l) <= tolerance
    pos = tardis.forward(h, k, l)
    assert abs(pos["theta"] - theta) <= tolerance
    assert abs(pos["delta"] - delta) <= tolerance
    assert abs(pos["gamma"] - gamma) <= tolerance

    # simulate the scan, computing angles from hkl
    # RE(scan([hw.det, tardis],tardis.h, 0.0001, -0.025, tardis.k, 0.0001, 0.51, num=5))
    data = """
    +-----------+------------+------------+------------+------------+------------+--------------+--------------+--------------+
    |   seq_num |       time |   tardis_h |   tardis_k |        det |   tardis_l | tardis_theta | tardis_delta | tardis_gamma |
    +-----------+------------+------------+------------+------------+------------+--------------+--------------+--------------+
    |         1 | 15:23:27.2 |      0.000 |      0.000 |      1.000 |      0.000 |       60.001 |        0.002 |        0.000 |
    |         2 | 15:23:27.9 |     -0.006 |      0.128 |      1.000 |      0.000 |       28.245 |        1.409 |        0.000 |
    |         3 | 15:23:28.5 |     -0.012 |      0.255 |      1.000 |      0.000 |       28.927 |        2.816 |        0.000 |
    |         4 | 15:23:29.1 |     -0.019 |      0.383 |      1.000 |      0.000 |       29.624 |        4.224 |        0.000 |
    |         5 | 15:23:29.7 |     -0.025 |      0.510 |      1.000 |      0.000 |       30.324 |        5.632 |        0.000 |
    +-----------+------------+------------+------------+------------+------------+--------------+--------------+--------------+
    """
    tardis.theta.move(0.3)
    tardis.delta.move(0.5)
    tardis.gamma.move(0.0)
    a = interpret_LiveTable(data)
    mu, chi, phi = 0, 0, 0  # constant
    targets = list(zip(a["theta"], a["delta"], a["gamma"], a["h"], a["k"], a["l"]))
    for theta, delta, gamma, h, k, l in targets:
        pos = tardis.forward(h, k, l)
        assert abs(pos["theta"] - theta) <= tolerance
        assert abs(pos["delta"] - delta) <= tolerance
        assert abs(pos["gamma"] - gamma) <= tolerance
