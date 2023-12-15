"""
(Re)create the geometry_tables.rst document.

Run this manually, as needed::

    python \
        ./docs/make_geometry_tables.py \
        | tee ./docs/source/geometry_tables.rst

"""

import sys

import pyRestTable

from hkl import calc

PAGE_HEAD = f"""
.. this page created by {sys.argv[0]}

.. _geometry_tables:

=================================
Tables of Diffractometer Geometry
=================================

Tables are provided for the different geometries and then, for each
geometry, the calculation engines, pseudo axes required, modes of
operation, and any additional parameters required by the mode.

Geometries indexed by number of circles
---------------------------------------

The different diffractometer geometries are distinguished, primarily, by
the number of axes (circles) and the names of each.  This table is
sorted first by the number of circles, and then the geometry name (as
used here in *hklpy*).

"""

TABLES_HEAD = """

.. _geometry_tables.tables:

Tables for each geometry
------------------------

A table is provided for each diffractometer geometry listing the calculation
engines, pseudo axes required, modes of operation, and any additional parameters
required by the mode.

* *engine* : Defines the names (and order) of the pseudo axes.
* *pseudo axes* : The engine performs
  :meth:`~hkl.diffract.Diffractometer.forward()` (pseudo-to-real) and
  :meth:`~hkl.diffract.Diffractometer.inverse()` (real-to-pseudo)
  transformations between the real-space axes and the *pseudo* (typically
  reciprocal-space) axes.  The *engine* defines the *pseudo axes* to be used.
* *mode* : Defines which axes are used for the ``forward()`` computation.
* *axes read* : Axes used in the ``forward()`` computation.
* *axes written* : Axes computed by the ``forward()`` computation.
* *extra parameters* : Any necessary additional parameters.
"""


def goniometers():
    for cname in dir(calc):
        if cname.startswith("Calc"):
            try:
                yield getattr(calc, cname)()
            except TypeError:
                pass


def print_summary_table():
    def format_name_list(names):
        names = [f"``{k}``" for k in names]
        return ", ".join(names)

    db = {
        gonio.geometry_name: {
            "real_axes": gonio.physical_axis_names,
            "cname": gonio.__class__.__name__[4:],  # 4 = len("Calc") as in "CalcE4CV"
        }
        for gonio in goniometers()
    }

    def sorter(gname):
        return f"{len(db[gname]['real_axes'])}-{gname}"

    table = pyRestTable.Table()
    table.addLabel("#circles")
    table.addLabel("geometry")
    table.addLabel("real_axes")
    for gname in sorted(db.keys(), key=sorter):
        gname_safe = gname.replace(" ", "_")
        entry = db[gname]
        real_axes = entry["real_axes"]
        table.addRow(
            [
                len(real_axes),
                f":ref:`{gname} <{gname_safe}_table>`",
                format_name_list(real_axes),
            ]
        )
    print(table)


def print_geometry_tables(rst=True):
    for gonio in goniometers():
        gonio.geometry_table(rst=rst)


if __name__ == "__main__":
    print(PAGE_HEAD.lstrip())
    print_summary_table()
    print(TABLES_HEAD)
    print_geometry_tables(rst=True)
