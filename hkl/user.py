"""
Provide a simplified UI for hklpy diffractometer users.

The user must define a diffractometer instance, then
register that instance here calling `select_diffractometer(instance)`.

FUNCTIONS

.. autosummary::

    ~cahkl
    ~cahkl_table
    ~calc_UB
    ~list_samples
    ~new_sample
    ~or_swap
    ~select_diffractometer
    ~set_energy
    ~setor
    ~show_sample
    ~show_selected_diffractometer
    ~update_sample
    ~wh
    ~pa
"""

__all__ = """
    cahkl
    cahkl_table
    calc_UB
    change_sample
    list_samples
    new_sample
    or_swap
    pa
    select_diffractometer
    set_energy
    setor
    show_sample
    show_selected_diffractometer
    update_sample
    wh
""".split()

import logging
import gi

gi.require_version("Hkl", "5.0")
logger = logging.getLogger(__name__)

from .diffract import Diffractometer
from .util import Lattice
import numpy
import pyRestTable


_geom_ = None  # selected diffractometer geometry


def _check_geom_selected(*args, **kwargs):
    """Raise ValueError if no diffractometer geometry is selected."""
    if _geom_ is None:
        raise ValueError(
            "No diffractometer selected."
            " Call 'select_diffractometer(diffr)' where"
            " 'diffr' is a diffractometer instance."
        )


def cahkl(h, k, l):
    """
    Calculate motor positions for one reflection.

    Returns a namedtuple.
    Does not move motors.
    """
    _check_geom_selected()
    # TODO: make certain this will not move the motors!
    return _geom_.forward(h, k, l)


def cahkl_table(reflections, digits=5):
    """
    Print a table with motor positions for each reflection given.

    Parameters
    ----------
    reflections : list(tuple(number,number,number))
        This is a list of reflections where
        each reflection is a tuple of 3 numbers
        specifying (h, k, l) of the reflection
        to compute the ``forward()`` computation.

        Example:  ``[(1,0,0), (1,1,1)]``
    digits : int
        Number of digits to roundoff each position
        value.  Default is 5.
    """
    _check_geom_selected()
    print(_geom_.forward_solutions_table(reflections, digits=digits))


# def calc_energy():
#     # TODO: should this be added?
#     raise NotImplementedError


def calc_UB(r1, r2, wavelength=None):
    """Compute the UB matrix with two reflections."""
    _check_geom_selected()
    _geom_.calc.sample.compute_UB(r1, r2)
    print(_geom_.calc.sample.UB)


def change_sample(sample):
    """Pick a known sample to be the current selection."""
    _check_geom_selected()
    if sample not in _geom_.calc._samples:
        # fmt: off
        raise KeyError(
            f"Sample '{sample}' is unknown."
            f"  Known samples: {list(_geom_.calc._samples.keys())}"
        )
        # fmt: on
    _geom_.calc.sample = sample
    show_sample(sample)


def list_samples(verbose=True):
    """List all defined crystal samples."""
    _check_geom_selected()
    # always show the default sample first
    current_name = _geom_.calc.sample_name
    show_sample(current_name, verbose=verbose)

    # now, show any other samples
    for sample in _geom_.calc._samples.keys():
        if sample != current_name:
            if verbose:
                print("")
            show_sample(sample, verbose=verbose)


def new_sample(nm, a, b, c, alpha, beta, gamma):
    """Define a new crystal sample."""
    _check_geom_selected()
    if nm in _geom_.calc._samples:
        logger.warning(
            (
                "Sample '%s' is already defined."
                "  Use 'update_sample()' to change lattice parameters"
                " on the *current* sample."
            ),
            nm,
        )
    else:
        lattice = Lattice(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)
        _geom_.calc.new_sample(nm, lattice=lattice)
    show_sample()


def or_swap():
    """Swap the 2 [UB] reflections, re-compute & return new [UB]."""
    # note: or_swap is how the community of SPEC users knows this function
    _check_geom_selected()
    return _geom_.calc.sample.swap_orientation_reflections()


def select_diffractometer(instrument=None):
    """Name the diffractometer to be used."""
    global _geom_
    if instrument is None or isinstance(instrument, Diffractometer):
        _geom_ = instrument
    else:
        raise TypeError(f"{instrument} must be a 'Diffractometer' subclass")


def set_energy(value, units=None, offset=None):
    """
    Set the energy (thus wavelength) to be used.
    """
    _check_geom_selected()
    if units is not None:
        _geom_.energy_units.put(units)
    if offset is not None:
        _geom_.energy_offset.put(offset)
    _geom_.energy.put(value)


def setor(h, k, l, *args, wavelength=None, **kwargs):
    """Define a crystal reflection and its motor positions."""
    _check_geom_selected()
    if len(args) == 0:
        if len(kwargs) == 0:
            pos = _geom_.real_position
        else:
            # fmt: off
            pos = [
                kwargs[m]
                for m in _geom_.calc.physical_axis_names
                if m in kwargs
            ]
            # fmt: on
    else:
        pos = args

    # NOTE: libhkl gets the wavelength on a reflection from hkl.calc
    # when the wavelength is set, it calls libhkl directly
    # as self._geometry.wavelength_set(wavelength, self._units)
    # The code here uses that procedure.
    if wavelength not in (None, 0):
        _geom_.calc.wavelength = wavelength

    refl = _geom_.calc.sample.add_reflection(h, k, l, position=pos)
    return refl


def show_sample(sample_name=None, verbose=True):
    """Print the default sample name and crystal lattice."""
    _check_geom_selected()
    sample_name = sample_name or _geom_.calc.sample_name
    sample = _geom_.calc._samples[sample_name]

    title = sample_name
    if sample_name == _geom_.calc.sample.name:
        title += " (*)"

    # Print Lattice more simply (than as a namedtuple).
    lattice = [getattr(sample.lattice, parm) for parm in sample.lattice._fields]
    if verbose:
        tbl = pyRestTable.Table()
        tbl.addLabel("key")
        tbl.addLabel("value")
        tbl.addRow(("name", sample_name))
        tbl.addRow(("lattice", lattice))
        for i, r in enumerate(sample.reflections):
            tbl.addRow((f"reflection {i+1}", r))
        tbl.addRow(("U", numpy.round(sample.U, 5)))
        tbl.addRow(("UB", numpy.round(sample.UB, 5)))

        print(f"Sample: {title}\n")
        print(tbl)
    else:
        print(f"{title}: {lattice}")


def show_selected_diffractometer(instrument=None):
    """Print the name of the selected diffractometer."""
    if _geom_ is None:
        print("No diffractometer selected.")
    print(_geom_.name)


def update_sample(a, b, c, alpha, beta, gamma):
    """Update current sample lattice."""
    _check_geom_selected()
    _geom_.calc.sample.lattice = (
        a,
        b,
        c,
        alpha,
        beta,
        gamma,
    )  # define the current sample
    show_sample(_geom_.calc.sample.name, verbose=False)


def pa():
    """Report (all) the diffractometer settings."""
    _check_geom_selected()
    _geom_.pa()


def wh():
    """Report (brief) where is the diffractometer."""
    _check_geom_selected()
    _geom_.wh()
