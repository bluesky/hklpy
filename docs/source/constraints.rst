.. index:: !constraints

.. _constraints:

===========
Constraints
===========

Overview
--------

Computation of the real-space axis positions given a set of reciprocal-space
coordinates can have many solutions.  One or more constraints
(:class:`~hkl.util.Constraint`) (a.k.a, cut points), together with a choice of
operating :ref:`mode <overview.mode>`, can be applied to:

* limit the range of :ref:`constraints.forward` solutions accepted for that positioner
* declare the value to use when the positioner should be kept constant

Diffractometer constraints are described by:

.. autosummary::

    ~hkl.util.Constraint

These functions manage constraints:

.. autosummary::
    ~hkl.diffract.Diffractometer.apply_constraints
    ~hkl.diffract.Diffractometer.reset_constraints
    ~hkl.diffract.Diffractometer.show_constraints
    ~hkl.diffract.Diffractometer.undo_last_constraints
    ~hkl.util.restore_constraints

Diffractometer constraints can be exported and restored as part of a
:class:`~hkl.configuration.DiffractometerConfiguration`:

.. autosummary::
    ~hkl.configuration.DiffractometerConfiguration.export
    ~hkl.configuration.DiffractometerConfiguration.restore

.. this is coming in PR #299
    ~hkl.configuration.DiffractometerConfiguration.preview

.. index:: cut points
.. tip:: *Constraints* are implemented as *cut points* in other software.  Similar yet not identical.

Create a constraint
-------------------

A ``Constraint`` is defined as a :class:`~hkl.util.Constraint` object.  For
convenience, import directly from ``hkl.Constraint``::

    hkl.Constraint(0, 90, 0, True)

Consider a diffractometer object::

    from hkl import SimulatedE4CV
    e4cv = SimulatedE4CV("", name="e4cv")

The default constraints for this geometry are (using ``e4cv.show_constraints()``):

===== ========= ========== ===== ====
axis  low_limit high_limit value fit
===== ========= ========== ===== ====
omega -180.0    180.0      0.0   True
chi   -180.0    180.0      0.0   True
phi   -180.0    180.0      0.0   True
tth   -180.0    180.0      0.0   True
===== ========= ========== ===== ====

Apply the constraint
--------------------

Apply a constraint *just* to the `"tth"` axis such that :math:`0<=2\theta<=120`::

    e4cv.apply_constraints({"tth": Constraint(0, 120, 0, True)})

Show the constraints now (again, using ``e4cv.show_constraints()``):

===== ========= ================== ===== ====
axis  low_limit high_limit         value fit
===== ========= ================== ===== ====
omega -180.0    180.0              0.0   True
chi   -180.0    180.0              0.0   True
phi   -180.0    180.0              0.0   True
tth   0.0       119.99999999999999 0.0   True
===== ========= ================== ===== ====

Remove the constraint
---------------------

Remove the previous constraint::

    e4cv.undo_last_constraints()
    e4cv.show_constraints()

Back to the defaults again:

===== ========= ========== ===== ====
axis  low_limit high_limit value fit
===== ========= ========== ===== ====
omega -180.0    180.0      0.0   True
chi   -180.0    180.0      0.0   True
phi   -180.0    180.0      0.0   True
tth   -180.0    180.0      0.0   True
===== ========= ========== ===== ====

Example
-------

Using the default sample (`main`), show the possible ``forward()`` solutions for
a :math:`(100)` position with a :class:`hkl.geometries.E4CV` (4-circle) geometry
diffractometer with these constraints:

===== ========= ========== ===== ====
axis  low_limit high_limit value fit
===== ========= ========== ===== ====
omega 10.0      40.0       0.0   True
chi   -100.0    100.0      0.0   True
phi   -100.0    100.0      0.0   True
tth   10.0      92.4       0.0   True
===== ========= ========== ===== ====

First, make the diffractometer (simulator) and show the default constraints:

.. code-block::
    :linenos:

    from hkl import SimulatedE4CV

    e4cv = SimulatedE4CV("", name="e4cv")
    e4cv.show_constraints()

===== ========= ========== ===== ====
axis  low_limit high_limit value fit
===== ========= ========== ===== ====
omega -180.0    180.0      0.0   True
chi   -180.0    180.0      0.0   True
phi   -180.0    180.0      0.0   True
tth   -180.0    180.0      0.0   True
===== ========= ========== ===== ====

Make a convenience function to show all the possible :ref:`constraints.forward`
solutions in a table.  The complete list of possible solutions is provided by
the low-level :meth:`~hkl.calc.CalcRecip.forward` method:

.. code-block::
    :linenos:

    import pyRestTable

    def all_forward_solutions(hkl_position):
        axes = e4cv.calc.physical_axis_names
        table = pyRestTable.Table()
        table.labels = axes
        for sol in e4cv.calc.forward(hkl_position):
            table.addRow([round(getattr(sol, k), 2) for k in axes])
        print(f"solutions for forward({hkl_position}):")
        print(table)

Show all solutions for the :math:`(100)` position (note the inner set of parentheses):

.. code-block::

    all_forward_solutions((1, 0, 0))

solutions for forward((1, 0, 0)):

======= ===== ======= ======
omega   chi   phi     tth
======= ===== ======= ======
-30.21  0.0   -90.0   -60.42
30.21   0.0   90.0    60.42
-149.79 0.0   29.58   -60.42
-30.21  0.0   150.42  60.42
30.21   0.0   -150.42 -60.42
-149.79 0.0   -90.0   60.42
-30.21  180.0 90.0    -60.42
30.21   180.0 -90.0   60.42
-149.79 180.0 -29.58  -60.42
-30.21  180.0 -150.42 60.42
30.21   180.0 150.42  -60.42
-149.79 180.0 90.0    60.42
======= ===== ======= ======

Next, apply the new constraints and print the revised table:

.. code-block::
    :linenos:

    e4cv.apply_constraints(
        {
            "omega": Constraint(10, 40, 0, True),
            "chi": Constraint(-100, 100, 0, True),
            "phi": Constraint(-100, 100, 0, True),
            "tth": Constraint(10, 92.4, 0, True),
        }
    )
    all_forward_solutions((1, 0, 0))

solutions for forward((1, 0, 0)):

===== === ==== =====
omega chi phi  tth
===== === ==== =====
30.21 0.0 90.0 60.42
===== === ==== =====

Only one solution satisfies these constraints.

.. _constraints.forward:

``forward()``
-------------

Given a set of reciprocal-space coordinates (typically :math:`h`, :math:`k`, and
:math:`l`), compute the different sets of real-space coordinates which match.
In the general case, the problem is over-determined. Multiple solutions are
expected. These are the ``forward()`` computation methods:

* :class:`~hkl.diffract.Diffractometer` .
  :meth:`~hkl.diffract.Diffractometer.forward` - provides one solution, if possible
* (lower-level) :class:`~hkl.calc.CalcRecip` .
  :meth:`~hkl.calc.CalcRecip.forward` - provides a list of all *allowed* solutions

The :meth:`hkl.diffract.Diffractometer.forward` method selects the first
allowed solution from :meth:`hkl.calc.CalcRecip.forward`.  This is the default
choice as defined by :func:`hkl.calc.default_decision_function`. You can
replace it with your own function.  Then, either:

* (easier) set your diffractometer object's
  :attr:`~hkl.diffract.Diffractometer._decision_fcn` attribute, such as:
  ``e4cv._decision_fcn=your_function``
* (harder) pass it via the ``decision_fcn=your_function`` keyword when creating
  the :class:`~hkl.diffract.Diffractometer` object
