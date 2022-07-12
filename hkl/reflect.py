"""
Crystalline Sample Reflections on a Diffractometer

A reflection represents a specific coordination between:

* a set of diffractometer angles in real-space (known here as *reals*)
* a set of crystalline coordinates in reciprocal-space (known here as *pseudos*)
* an incident wavelength

The names and ordering of the reals is specified by the diffractometer. The
names and ordering of the pseudos is specified by the reciprocal-space
computational engine.

A diffractometer may have several samples, each with their own list of
reflections.  The reciprocal-space computational engine cannot be changed once
the diffractometer object is created.
"""

import logging


logger = logging.getLogger(__name__)


class Reflection:
    """
    A crystalline sample orientation reflection.

    Associates reciprocal-space positions (pseudos)
    with real-space positions (reals) and a wavelength.

    Use Reflection (here) instead of libhkl.SampleReflection to keep this info
    in Python.
    """

    wavelength = None
    pseudos = []
    reals = []

    def __init__(self, pseudos, reals, wavelength, diffractometer=None) -> None:
        if diffractometer is not None:
            if isinstance(pseudos, (list, tuple)):
                pseudos = diffractometer.PseudoPosition(*pseudos)
            if isinstance(reals, (list, tuple)):
                reals = diffractometer.RealPosition(*reals)

        self.diffractometer = diffractometer
        self.pseudos = pseudos
        self.reals = reals
        self.wavelength = wavelength

    def _repr_info(self):
        return [
            repr(self.pseudos),
            repr(self.reals),
            f"wavelength={self.wavelength!r}",
        ]

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self._repr_info())})"

    def __eq__(self, refl):
        return (
            isinstance(refl, self.__class__)
            and self.pseudos == refl.pseudos
            and self.reals == refl.reals
            and self.wavelength == refl.wavelength
        )


class ReflectionManager:
    """
    Manage a set of Reflection objects for a diffractometer sample.
    """

    # TODO: refactor as dict? {sample: value is dict(reflections, UB_reflections)}
    _reflections = []
    _UB_reflections = []

    def __init__(self, diffractometer) -> None:
        from .diffract import Diffractometer

        if not isinstance(diffractometer, Diffractometer):
            raise TypeError(
                "'diffractometer' must be a subclass of Diffractometer. "
                f" Received: {type(diffractometer)}"
            )
        self.diffractometer = diffractometer
        self.clear()

    def __len__(self) -> None:
        return len(self._reflections)

    def add(self, pseudos, reals, wavelength, use_UB=True):
        """
        Add a reflection to the list.
        """
        # TODO: sample
        # TODO: do not add same reflection twice
        # TODO: support this existing use:
        #     r1 = sample.add_reflection(-1, 0, 0, (30, 0, -90, 60))
        #     r2 = sample.add_reflection(0, 1, 1, (45, 45, 0, 90))

        reflection = Reflection(
            pseudos, reals, wavelength, diffractometer=self.diffractometer
        )
        self._reflections.append(reflection)
        if use_UB:
            self._UB_reflections.append(reflection)
        return reflection

    @property
    def all_reflections(self):
        return self._reflections

    @property
    def UB_reflections(self):
        return self._UB_reflections

    def clear(self):
        """Clear the list of reflections."""
        self._reflections = []
        self._UB_reflections = []

    def remove(self, reflection):
        """Remove a reflection from the list."""

        def pop_it(r, rlist):
            if r in rlist:
                reflection_index = rlist.index(r)
                rlist.pop(reflection_index)

        pop_it(reflection, self._reflections)
        pop_it(reflection, self._UB_reflections)

    def _repr_info(self):
        s = []
        for reflection in self._reflections:
            t = [f"reflection={reflection!r}"]
            if reflection in self._UB_reflections:
                reflection_index = self._reflections.index(reflection)
                t.append(f"UB_calc={reflection_index}")
            s.append(", ".join(t))
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self._repr_info())})"
