"""
unit test: examples/tst_e6c_test_calculations.ipynb
"""

# Import the Python libraries needed

import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import gi
gi.require_version('Hkl', '5.0')
from hkl.calc import CalcE6C
from hkl.util import Lattice
from hkl.calc import A_KEV

def test_example():
    # Initialize the calculation engine
    calc = CalcE6C(engine='hkl')
    calc.engine.mode = 'constant_chi_vertical'
    calc.wavelength = 1.  # Angstrom
    assert calc.physical_axes == dict(
        mu=0, omega=0, chi=0, phi=0, gamma=0, delta=0
    )
    assert calc.pseudo_axes == dict(h=0, k=0, l=0)
    assert calc["omega"].name == "omega"
    assert calc["omega"].limits == (-180, 180)
    assert calc["omega"].value == 0
    assert calc["omega"].fit == True
    assert calc["omega"].inverted == False
    assert calc["omega"].units == "user"

    # Setup the crystal lattice
    lattice = Lattice(a=1, b=1, c=1, alpha=90, beta=90, gamma=90)
    assert lattice.a == 1
    assert lattice.b == 1
    assert lattice.c == 1
    assert lattice.alpha == 90
    assert lattice.beta == 90
    assert lattice.gamma == 90
    sample = calc.new_sample('sample0', lattice=lattice)
    assert sample.name == "sample0"
    assert sample.lattice == lattice

    # define the wavelength
    calc.wavelength = 1.0
    assert calc.wavelength == 1.0
    assert calc.energy == A_KEV

    # define two reflections
    assert len(sample.reflections) == 0
    r1p = calc.Position(mu=0.0, omega=30.0, chi=0.0, phi=0.0, gamma=0., delta=60.)
    assert r1p.mu == 0
    assert r1p.omega == 30
    assert r1p.chi == 0
    assert r1p.phi == 0
    assert r1p.gamma == 0
    assert r1p.delta == 60
    r1 = sample.add_reflection(0, 0, 1, position=r1p)
    assert len(sample.reflections) == 1
    assert sample.reflections[-1] == (0, 0, 1)

    r2 = sample.add_reflection(1, 0, 0, (0.0, 120.0, 0.0, 0.0, 0, 60.))
    assert len(sample.reflections) == 2
    assert sample.reflections[-1] == (1, 0, 0)

    # Compute the UB matrix from the two reflections
    sample.compute_UB(r1, r2)
    np.testing.assert_array_almost_equal(sample.U, np.identity(3))
    B = 2 * math.pi / calc.wavelength   # treat here as scalar
    np.testing.assert_array_almost_equal(sample.UB, sample.U * B)

    # (010)
    calc.physical_positions = calc.Position(
        mu=0.0, omega=30.0, chi=90.0, phi=0.0, gamma=0., delta=60.
    )
    assert round(calc.pseudo_axes["h"], 5) == 0
    assert round(calc.pseudo_axes["k"], 5) == 1
    assert round(calc.pseudo_axes["l"], 5) == 0

    # (010) with delta=0
    calc.physical_positions = calc.Position(
        mu=30.0, omega=0.0, chi=0.0, phi=0.0, gamma=60., delta=0.
    )
    assert round(calc.pseudo_axes["h"], 5) == 0
    assert round(calc.pseudo_axes["k"], 5) == 1
    assert round(calc.pseudo_axes["l"], 5) == 0

    # (0 -1 0)
    calc.physical_positions = calc.Position(
        mu=0.0, omega=30.0, chi=-90.0, phi=0.0, gamma=0., delta=60.
    )
    assert round(calc.pseudo_axes["h"], 5) == 0
    assert round(calc.pseudo_axes["k"], 5) == -1
    assert round(calc.pseudo_axes["l"], 5) == 0

    # (-1 0 0)
    calc.physical_positions = calc.Position(
        mu=0.0, omega=-60.0, chi=0.0, phi=0.0, gamma=0, delta=60.
    )
    assert round(calc.pseudo_axes["h"], 5) == -1
    assert round(calc.pseudo_axes["k"], 5) == 0
    assert round(calc.pseudo_axes["l"], 5) == 0

    # (001) upside-down: |omega + phi| = 120
    calc.physical_positions = calc.Position(
        mu=0.0, omega=-50.0, chi=0.0, phi=-70.0, gamma=0, delta=-60.
    )
    assert round(calc.pseudo_axes["h"], 5) == 1
    assert round(calc.pseudo_axes["k"], 5) == 0
    assert round(calc.pseudo_axes["l"], 5) == 0
    calc.physical_positions = calc.Position(
        mu=0.0, omega=-100.0, chi=0.0, phi=-20.0, gamma=0, delta=-60.
    )
    assert round(calc.pseudo_axes["h"], 5) == 1
    assert round(calc.pseudo_axes["k"], 5) == 0
    assert round(calc.pseudo_axes["l"], 5) == 0
    calc.physical_positions = calc.Position(
        mu=0.0, omega=100.0, chi=0.0, phi=-220.0, gamma=0, delta=-60.
    )
    assert round(calc.pseudo_axes["h"], 5) == 1
    assert round(calc.pseudo_axes["k"], 5) == 0
    assert round(calc.pseudo_axes["l"], 5) == 0

    # (011)
    calc.physical_positions = calc.Position(
        mu=0.0, omega=45.0, chi=45.0, phi=0.0, gamma=0, delta=90.
    )
    assert round(calc.pseudo_axes["h"], 5) == 0
    assert round(calc.pseudo_axes["k"], 5) == 1
    assert round(calc.pseudo_axes["l"], 5) == 1

    # FIXME:
    # # check all solutions for (100)
    # r = (0, 0, 1)
    # for sol in calc.forward(r):
    #     m = str(sol)
    #     assert round(abs(sol.omega + sol.phi), 5) == 120, m
