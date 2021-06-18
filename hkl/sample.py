from __future__ import print_function
import logging

import numpy as np

from .engine import Parameter
from .util import libhkl
from . import util
from .util import Lattice
from .context import TemporaryGeometry


__all__ = """
    check_lattice
    HklSample
""".split()
logger = logging.getLogger(__name__)


def check_lattice(lattice):
    """Check an Hkl.Lattice for validity

    Raises
    ------
    ValueError
    """

    # TODO: assertion is raised if alpha/beta/gamma are invalid,
    #       which is not propagated back as a Python exception but a segfault.
    a = lattice.a_get()
    b = lattice.b_get()
    c = lattice.c_get()
    alpha = lattice.alpha_get()
    beta = lattice.beta_get()
    gamma = lattice.gamma_get()

    lt = Lattice(a, b, c, alpha, beta, gamma)
    for k, v in lt._asdict().items():
        if v is None:
            raise ValueError(f'Lattice parameter "{k}" unset or invalid')

    lt = Lattice(
        a.value_get(util.units["user"]),
        b.value_get(util.units["user"]),
        c.value_get(util.units["user"]),
        alpha.value_get(util.units["user"]),
        beta.value_get(util.units["user"]),
        gamma.value_get(util.units["user"]),
    )
    logger.debug("Lattice OK: %s", lt)


class HklSample(object):
    """Represents a sample in diffractometer calculations

    Parameters
    ----------
    calc : instance of CalcRecip
        Reciprocal space calculation class
    name : str
        A user-defined name used to refer to the sample
    sample : Hkl.Sample, optional
        A Sample instance from the wrapped Hkl library. Created
        automatically if not specified.
    units : {'user', 'default'}
        Units to use
    lattice : np.ndarray, optional
        The lattice
    U : np.ndarray, optional
        The crystal orientation matrix, U
    UB : np.ndarray, optional
        The UB matrix, where U is the crystal orientation matrix and B is
        the transition matrix of a non-orthonormal (the reciprocal of the
        crystal) in an orthonormal system
    ux : np.ndarray, optional
        ux part of the U matrix
    uy : np.ndarray, optional
        uy part of the U matrix
    uz : np.ndarray, optional
        uz part of the U matrix
    reflections :
        All reflections for the current sample in the form::

            [(h, k, l), ...]

        This assumes the hkl engine is used; generally, the ordered set of
        positions for the engine in-use should be specified.

    """

    def __init__(self, calc, sample=None, units="user", **kwargs):
        if sample is None:
            sample = libhkl.Sample.new("")

        self._calc = calc
        self._sample = sample
        self._sample_dict = calc._samples

        self._unit_name = units
        try:
            self._units = util.units[self._unit_name]
        except KeyError:
            raise ValueError(
                f"Unit name '{self._unit_name}' not found.   Allowed names: {list(util.units.keys())}"
            )

        # List of reflections used in computing the U & UB matrices.
        # If UB is computed by refinement of more than two reflections,
        # the code that sets that up will also need to manage this list.
        self._orientation_reflections = []

        for name in "lattice name U UB ux uy uz reflections".split():
            value = kwargs.pop(name, None)
            if value is not None:
                try:
                    setattr(self, name, value)
                except Exception as ex:
                    # These kwargs are funneled down to the gi wrapper
                    # and could raise just about anything. Tack on the
                    # kwarg to help debugging if necessary:
                    ex.message = "%s (attribute=%s)" % (ex, name)
                    raise

        if kwargs:
            raise ValueError("Unsupported kwargs for HklSample: %s" % tuple(kwargs.keys()))

    @property
    def hkl_calc(self):
        """
        The HklCalc instance associated with the sample
        """
        return self._calc

    @property
    def hkl_sample(self):
        """
        The HKL library sample object
        """
        return self._sample

    @property
    def name(self):
        """
        The name of the currently selected sample
        """
        return self._sample.name_get()

    @name.setter
    def name(self, new_name):
        """Replace the current sample

        Parameters
        ----------
        new_name : str
        """
        if new_name in self._sample_dict:
            raise ValueError("Sample with that name already exists")
        sample = self._sample
        old_name = sample.name_get()

        sample.name_set(new_name)

        del self._sample_dict[old_name]
        self._sample_dict[new_name] = self

    @property
    def reciprocal(self):
        """The reciprocal lattice"""
        lattice = self._sample.lattice_get()
        reciprocal = lattice.copy()
        lattice.reciprocal(reciprocal)
        return reciprocal.get(self._units)

    @property
    def lattice(self):
        """The lattice (a, b, c, alpha, beta, gamma)

        a, b, c [nm]
        alpha, beta, gamma [deg]
        """
        lattice = self._sample.lattice_get()
        lattice = lattice.get(self._units)
        return Lattice(*lattice)

    @lattice.setter
    def lattice(self, lattice):
        if not isinstance(lattice, libhkl.Lattice):
            a, b, c, alpha, beta, gamma = lattice
            alpha, beta, gamma = np.radians((alpha, beta, gamma))
            lattice = libhkl.Lattice.new(a, b, c, alpha, beta, gamma)

        check_lattice(lattice)
        self._sample.lattice_set(lattice)
        # TODO: notes mention that lattice should not change, but is it alright
        #       if init() is called again? or should reflections be cleared,
        #       etc?

    @property
    def U(self):
        """
        The crystal orientation matrix, U
        """
        return util.to_numpy(self._sample.U_get())

    @U.setter
    def U(self, new_u):
        self._orientation_reflections = []
        self._sample.U_set(util.to_hkl(new_u))

    def _get_parameter(self, param):
        return Parameter(param, units=self._unit_name)

    @property
    def ux(self):
        """
        ux part of the U matrix
        """
        return self._get_parameter(self._sample.ux_get())

    @property
    def uy(self):
        """
        uy part of the U matrix
        """
        return self._get_parameter(self._sample.uy_get())

    @property
    def uz(self):
        """
        uz part of the U matrix
        """
        return self._get_parameter(self._sample.uz_get())

    @property
    def UB(self):
        """
        The UB matrix, where U is the crystal orientation matrix and B is the
        transition matrix of a non-orthonormal (the reciprocal of the crystal)
        in an orthonormal system

        If written to, the B matrix will be kept constant:
            U * B = UB -> U = UB * B^-1
        """
        return util.to_numpy(self._sample.UB_get())

    @UB.setter
    def UB(self, new_ub):
        self._orientation_reflections = []
        self._sample.UB_set(util.to_hkl(new_ub))

    def _create_reflection(self, h, k, l, detector=None):
        """
        Create a new reflection with the current geometry/detector
        """
        if detector is None:
            detector = self._calc._detector

        return libhkl.SampleReflection.new(self._calc._geometry, detector, h, k, l)

    def compute_UB(self, r1, r2):
        """Compute the UB matrix with two reflections.

        Using the Busing and Levy method, compute the UB matrix for two sample
        reflections, r1 and r2.

        Returns the UB matrix or raises gi.repository.GLib.GError
        (a change from 0.3.15 and before).  Returns ``None`` if no error
        raised but computation was not successful.

        Parameters
        ----------
        r1 : HklReflection
            Reflection 1
        r2 : HklReflection
            Reflection 2

        Returns
        -------
        UB matrix or raises ``gi.repository.GLib.GError``
        """
        if self._sample.compute_UB_busing_levy(r1, r2):
            # TODO: this list defines the order of the orientation reflections
            self._orientation_reflections = [r1, r2]
            return self.UB

    @property
    def reflections(self):
        """
        All reflections for the current sample in the form:
            [(h, k, l), ...]
        """
        return [refl.hkl_get() for refl in self._sample.reflections_get()]

    @reflections.setter
    def reflections(self, refls):
        self.clear_reflections()
        self._orientation_reflections = []
        for refl in refls:
            self.add_reflection(*refl)

    def add_reflection(self, h, k, l, position=None, detector=None, compute_ub=False):
        """Add a reflection, optionally specifying the detector to use

        Parameters
        ----------
        h : float
            Reflection h
        k : float
            Reflection k
        l : float
            Reflection l
        detector : Hkl.Detector, optional
            The detector
        position : tuple or namedtuple, optional
            The physical motor position that this reflection corresponds to
            If not specified, the current geometry of the calculation engine is
            assumed.
        compute_ub : bool, optional
            Calculate the UB matrix with the last two reflections
        """
        calc = self._calc
        if detector is None:
            detector = calc._detector

        if compute_ub and len(self.reflections) < 1:
            raise RuntimeError("Cannot calculate the UB matrix with less than two reflections")

        if compute_ub:
            r1 = self._sample.reflections_get()[-1]

        with TemporaryGeometry(calc):
            if position is not None:
                calc.physical_positions = position
            r2 = self._sample.add_reflection(calc._geometry, detector, h, k, l)

        if compute_ub:
            self.compute_UB(r1, r2)

        return r2

    def remove_reflection(self, refl):
        """Remove a specific reflection"""
        if not isinstance(refl, libhkl.SampleReflection):
            index = self.reflections.index(refl)
            refl = self._sample.reflections_get()[index]

        return self._sample.del_reflection(refl)

    def clear_reflections(self):
        """Clear all reflections for the current sample."""
        reflections = self._sample.reflections_get()
        for refl in reflections:
            self._sample.del_reflection(refl)
        self._orientation_reflections = []

    def _refl_matrix(self, fcn):
        """Get a reflection angle matrix."""
        sample = self._sample
        refl = sample.reflections_get()
        refl_matrix = np.zeros((len(refl), len(refl)))

        for i, r1 in enumerate(refl):
            for j, r2 in enumerate(refl):
                if i != j:
                    refl_matrix[i, j] = fcn(r1, r2)

        return refl_matrix

    @property
    def reflection_measured_angles(self):
        return self._refl_matrix(self._sample.get_reflection_measured_angle)

    @property
    def reflection_theoretical_angles(self):
        return self._refl_matrix(self._sample.get_reflection_theoretical_angle)

    def affine(self):
        """
        Make the sample transform affine
        """
        return self._sample.affine()

    def _repr_info(self):
        r = [
            f"name={self.name!r}",
            f"lattice={self.lattice!r}",
            f"ux={self.ux!r}",
            f"uy={self.uy!r}",
            f"uz={self.uz!r}",
            f"U={self.U!r}",
            f"UB={self.UB!r}",
            f"reflections={self.reflections!r}",
        ]

        return r

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self._repr_info())})"

    def __str__(self):
        info = self._repr_info()
        info.append(f"reflection_measured_angles={self.reflection_measured_angles!r}")
        info.append(f"reflection_theoretical_angles={self.reflection_theoretical_angles!r}")
        return f"{self.__class__.__name__}({', '.join(info)}))"

    def _get_reflection_dict(self, refl):
        """Return dictionary with reflection details."""
        h, k, l = refl.hkl_get()
        geom = refl.geometry_get()
        return dict(
            reflection=dict(h=h, k=k, l=l),
            flag=refl.flag_get(),
            wavelength=geom.wavelength_get(1),
            position={k: v for k, v in zip(geom.axis_names_get(), geom.axis_values_get(1))},
            orientation_reflection=refl in self._orientation_reflections,
        )

    @property
    def reflections_details(self):
        """
        Return a list with details of all reflections.

        NOTE: reflections_details() uses the canonical
        names for the real positioners.  The mapping
        to physical axis names happens in :mod`hkl.calc`.
        """
        refls = self._sample.reflections_get()
        for r in self._orientation_reflections:
            if r not in refls:
                # Edge case when orientation reflection was
                # deleted from the list in libhkl.
                refls.append(r)
        return [self._get_reflection_dict(r) for r in refls]

    def swap_orientation_reflections(self):
        """Swap the 2 [UB] reflections, re-compute & return new [UB]."""
        if len(self._orientation_reflections) != 2:
            raise ValueError(
                "Must have exactly 2 orientation reflections defined"
                " in order to make a swap and re-compute [UB]."
                f"  There are {len(self._orientation_reflections)}"
                " orientation reflection(s) defined now."
            )
        refls = self._orientation_reflections
        return self.compute_UB(*refls[::-1])
