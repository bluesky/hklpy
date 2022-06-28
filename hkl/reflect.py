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

    def __init__(self, pseudos, reals, wavelength) -> None:
        # fmt: off
        # confirm pseudos and reals are lists of appropriate objects
        # TODO: must generalize to allow pseudos = (0, 0, 1), for example
        for var in (pseudos, reals):
            for obj in var:
                for attr in "attr_name position".split():
                    if not hasattr(obj, attr):
                        raise AttributeError(f"{var}, '{obj}.{attr}' not found")
        # fmt: on

        self.pseudos = pseudos
        self.reals = reals
        self.wavelength = wavelength

    def _repr_info(self):
        p = [f"{obj.attr_name}={obj.position}" for obj in self.pseudos]
        r = [f"{obj.attr_name}={obj.position}" for obj in self.reals]

        s = [
            f"({', '.join(p)})",
            f"({', '.join(r)})",
            f"wavelength={self.wavelength!r}",
        ]

        return s

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self._repr_info())})"


class ReflectionManager:
    """
    Manage a set of Reflection objects.
    """

    _reflections = []
    _UB_reflections = []

    def __init__(self) -> None:
        self.clear()

    def __len__(self) -> None:
        return len(self._reflections)

    def add(self, pseudos, reals, wavelength, use_UB=True):
        """
        Add a reflection to the list.
        """
        # TODO: do not add same reflection twice
        # TODO: support this existing use:
        #     r1 = sample.add_reflection(-1, 0, 0, (30, 0, -90, 60))
        #     r2 = sample.add_reflection(0, 1, 1, (45, 45, 0, 90))

        reflection = Reflection(pseudos, reals, wavelength)
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
