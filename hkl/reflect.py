import logging


logger = logging.getLogger(__name__)


class Reflection:
    """
    A crystal orientation reflection.
    """

    wavelength = None
    pseudos = []
    reals = []

    def __init__(self, pseudos, reals, wavelength) -> None:
        # fmt: off
        # confirm pseudos and reals are lists of appropriate objects
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
