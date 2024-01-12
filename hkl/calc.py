"""
Calculation support for diffractometers

.. autosummary::

    ~default_decision_function
    ~UnreachableError
    ~CalcRecip

**Specific Geometries**

.. autosummary::

    ~CalcE4CH
    ~CalcE4CV
    ~CalcE6C
    ~CalcK4CV
    ~CalcK6C
    ~CalcPetra3_p09_eh2
    ~CalcPetra3_p23_4c
    ~CalcPetra3_p23_6c
    ~CalcSoleilMars
    ~CalcSoleilNanoscopiumRobot
    ~CalcSoleilSiriusKappa
    ~CalcSoleilSiriusTurret
    ~CalcSoleilSixsMed1p2
    ~CalcSoleilSixsMed2p2
    ~CalcSoleilSixsMed2p3
    ~CalcSoleilSixsMed2p3v2
    ~CalcZaxis

"""

import functools
import logging
from collections import OrderedDict
from threading import RLock

import numpy as np

from . import util
from .context import UsingEngine
from .engine import CalcParameter
from .engine import Engine
from .sample import HklSample
from .util import libhkl

__all__ = """
    A_KEV
    CalcE4CH
    CalcE4CV
    CalcE6C
    CalcK4CV
    CalcK6C
    CalcPetra3_p09_eh2
    CalcPetra3_p23_4c
    CalcPetra3_p23_6c
    CalcRecip
    CalcSoleilMars
    CalcSoleilNanoscopiumRobot
    CalcSoleilSiriusKappa
    CalcSoleilSiriusTurret
    CalcSoleilSixsMed1p2
    CalcSoleilSixsMed2p2
    CalcSoleilSixsMed2p3
    CalcZaxis
    default_decision_function
    NM_KEV
    UnreachableError
""".split()
logger = logging.getLogger(__name__)

# per NIST publication of CODATA Fundamental Physical Constants
# https://www.nist.gov/programs-projects/codata-values-fundamental-physical-constants
A_KEV = 12.39841984  # 1 Angstrom ~= 12.39842 keV
NM_KEV = A_KEV * 0.1  # 1 nm ~= 1.239842 keV
# Note: NM_KEV is not used by hklpy now, remains here as legacy


def default_decision_function(position, solutions):
    """The default decision function - returns the first solution."""
    return solutions[0]


# This is used below by CalcRecip.
def _locked(func):
    """a decorator for running a method with the instance's lock"""

    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        with self._lock:
            return func(self, *args, **kwargs)

    return wrapped


# This is used below by CalcRecip.
def _keep_physical_position(func):
    """
    decorator: stores/restores the physical motor position during calculations
    """

    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        with self._lock:
            initial_pos = self.physical_positions
            try:
                return func(self, *args, **kwargs)
            finally:
                self.physical_positions = initial_pos

    return wrapped


class UnreachableError(ValueError):
    """Position is unreachable.

    Attributes
    ----------
    pseudo : sequence
        Last reachable pseudo position in the trajectory
    physical : sequence
        Corresponding physical motor positions
    """

    def __init__(self, msg, pseudo, physical):
        super().__init__(msg)
        self.pseudo = pseudo
        self.physical = physical


class CalcRecip(object):
    """Reciprocal space calculations

    .. autosummary::

        ~add_sample
        ~calc_linear_path
        ~energy
        ~engine
        ~engine_locked
        ~engines
        ~forward
        ~forward_iter
        ~geometry_name
        ~geometry_table
        ~get_path
        ~inverse
        ~inverted_axes
        ~new_sample
        ~parameters
        ~physical_axes
        ~physical_axis_names
        ~physical_positions
        ~Position
        ~pseudo_axes
        ~pseudo_axis_names
        ~pseudo_positions
        ~sample
        ~sample_name
        ~units
        ~update
        ~wavelength

    Parameters
    ----------
    dtype : str
        Diffractometer type (usually specified by a subclass)
    engine : str, optional
        'hkl', for example
    sample : str, optional
        Default sample name (default: 'main')
    lattice : Lattice, optional
        Lattice to use with the default sample
    degrees : bool, optional
        Use degrees instead of radians (default: True)
    units : {'user', }
        The type of units to use internally
    lock_engine : bool, optional
        Don't allow the engine to be changed during
        the life of this object
    inverted_axes : list, optional
        Names of axes to invert the sign
    """

    def __init__(
        self,
        dtype,
        engine="hkl",
        sample="main",
        lattice=None,
        degrees=True,
        units="user",
        lock_engine=False,
        inverted_axes=None,
    ):
        self._engine = None  # set below with property
        self._detector = util.new_detector()
        self._degrees = bool(degrees)
        self._sample = None
        self._samples = {}
        self._unit_name = units
        self._units = util.units[self._unit_name]
        self._lock_engine = bool(lock_engine)
        self._lock = RLock()
        self._axis_name_to_renamed = {}
        self._axis_name_to_original = {}
        self._inverted_axes = inverted_axes or []

        try:
            self._factory = libhkl.factories()[dtype]
        except KeyError:
            types = ", ".join(util.diffractometer_types)
            raise ValueError(f"Invalid diffractometer type {types!r};  choose from: {types}")

        self._geometry = self._factory.create_new_geometry()
        self._engine_list = self._factory.create_new_engine_list()
        self._engine_names = [e.name_get() for e in self._engine_list.engines_get()]

        if sample is not None:
            if isinstance(sample, HklSample):
                if lattice is not None:
                    sample.lattice = lattice
                self.add_sample(sample)
            else:
                self.new_sample(sample, lattice=lattice)

        self.engine = engine

    @property
    def Position(self):
        """Dynamically-generated physical motor position class"""
        # I know, I know, could be done more cleanly...
        name = f"Pos{self.__class__.__name__}"
        return util.get_position_tuple(self.physical_axis_names, class_name=name)

    @property
    def wavelength(self):
        """The wavelength associated with the geometry, in angstrom"""
        return self._geometry.wavelength_get(self._units)

    @wavelength.setter
    def wavelength(self, wavelength):
        self._geometry.wavelength_set(wavelength, self._units)

    @property
    def energy(self):
        """The energy associated with the geometry, in keV"""
        return A_KEV / self.wavelength

    @energy.setter
    def energy(self, energy):
        self.wavelength = A_KEV / energy

    @property
    def engine_locked(self):
        """If set, do not allow the engine to be changed post-initialization"""
        return self._lock_engine

    @property
    def engine(self):
        """ """
        return self._engine

    @engine.setter
    @_locked
    def engine(self, engine):
        if engine is self._engine:
            return

        if self._lock_engine and self._engine is not None:
            raise ValueError("Engine is locked on this %s instance" % self.__class__.__name__)

        if isinstance(engine, libhkl.Engine):
            self._engine = engine
        else:
            engines = self.engines
            try:
                self._engine = engines[engine]
            except KeyError:
                raise ValueError("Unknown engine name or type")

        self._re_init()

    def _canonical2user(self, canonical):
        """Convert canonical axis names to user (renames)."""
        if len(self._axis_name_to_renamed) > 0:
            axis = self._axis_name_to_renamed[canonical]
        else:
            axis = canonical
        return axis

    @property
    def axes_r(self):
        """User-defined real-space axes used for forward() calculation."""
        return [self._canonical2user(ax) for ax in self._engine.axes_r]

    @property
    def axes_w(self):
        """User-defined real-space axes written by forward() calculation."""
        return [self._canonical2user(ax) for ax in self._engine.axes_w]

    @property
    def axes_c(self):
        """User-defined real-space axes held constant during forward() calculation."""
        return [self._canonical2user(ax) for ax in self._engine.axes_c]

    @property
    def geometry_name(self):
        """Name of this geometry, as defined in **libhkl**."""
        return self._geometry.name_get()

    def geometry_table(self, rst=False):
        """
        Describe this geometry in a table.

        Parameters
        ----------
        rst : *bool*
            When True, format using restructured text.  Otherwise,
            use a simpler representation
        """
        import sys

        import pyRestTable

        def format_name_list(names):
            if rst:
                names = [f"``{k}``" for k in names]
            return ", ".join(names)

        cname = self.__class__.__name__
        gname = self.geometry_name
        engines = list(self.engines.keys())
        real_axes = format_name_list(self.physical_axis_names)

        table = pyRestTable.Table()
        table.addLabel("engine")
        table.addLabel("pseudo axes")
        table.addLabel("mode")
        table.addLabel("axes read")
        table.addLabel("axes written")
        table.addLabel("extra parameters")
        for engine in sorted(engines):
            # Engine setting is locked when class is created.  Default is "hkl".
            # make new goniometer with chosen engine.  The "trick" here
            # is to get the class from __this__ module.
            # See: https://stackoverflow.com/a/7668273/1046449
            gonio = getattr(sys.modules[__name__], cname)(engine=engine)
            for mode in sorted(gonio.engine.modes):
                gonio.engine.mode = mode  #
                axes_r = format_name_list(gonio.engine._engine.axis_names_get(0))
                axes_w = format_name_list(gonio.engine._engine.axis_names_get(1))
                parameters = format_name_list(gonio.parameters)
                pseudo_axes = format_name_list(gonio.pseudo_axis_names)
                row = [engine, pseudo_axes, mode, axes_r, axes_w, parameters]
                table.addRow(row)

        if rst:
            gname_safe = gname.replace(" ", "_")
            print(f".. index:: {gname_safe}, geometry; {gname_safe}")
            print()
            print(f".. _{gname_safe}_table:")
            print()
            title = f"Geometry: ``{self.geometry_name}``"
            print(title)
            print("+" * len(title))
            print()
            print(f"* real axes: {real_axes}")
            print("* pseudo axes: depends on the engine")
        else:
            print(f"Geometry: {self.geometry_name}")
            print(f"  real axes: {real_axes}")
            print("  pseudo axes: depends on the engine")
        print()
        print(table)

    def _get_sample(self, name):
        if isinstance(name, libhkl.Sample):
            return name

        return self._samples[name]

    @property
    def sample_name(self):
        """The name of the currently selected sample."""
        return self._sample.name

    @sample_name.setter
    @_locked
    def sample_name(self, new_name):
        sample = self._sample
        sample.name = new_name

    @property
    def sample(self):
        """Currently selected sample."""
        return self._sample

    @sample.setter
    @_locked
    def sample(self, sample):
        if sample is self._sample:
            return
        elif sample == self._sample.name:
            return

        if isinstance(sample, HklSample):
            if sample not in self._samples.values():
                self.add_sample(sample, select=False)
        elif sample in self._samples:
            name = sample
            sample = self._samples[name]
        else:
            raise ValueError("Unknown sample type (expected HklSample)")

        self._sample = sample
        self._re_init()

    def add_sample(self, sample, select=True):
        """Add an HklSample

        Parameters
        ----------
        sample : HklSample instance
            The sample name, or optionally an already-created HklSample
            instance
        select : bool, optional
            Select the sample to focus calculations on
        """
        if not isinstance(sample, (HklSample, libhkl.Sample)):
            raise ValueError("Expected either an HklSample or a Sample instance")

        if isinstance(sample, libhkl.Sample):
            sample = HklSample(calc=self, sample=sample, units=self._unit_name)

        if sample.name in self._samples:
            raise ValueError('Sample of name "%s" already exists' % sample.name)

        self._samples[sample.name] = sample
        if select:
            self._sample = sample
            self._re_init()

        return sample

    def new_sample(self, name, select=True, **kwargs):
        """Convenience function to add a sample by name

        Keyword arguments are passed to the new HklSample initializer.

        Parameters
        ----------
        name : str
            The sample name
        select : bool, optional
            Select the sample to focus calculations on
        """
        units = kwargs.pop("units", self._unit_name)
        sample = HklSample(self, sample=libhkl.Sample.new(name), units=units, **kwargs)

        return self.add_sample(sample, select=select)

    @_locked
    def _re_init(self):
        if self._engine is None:
            return

        if self._geometry is None or self._detector is None or self._sample is None:
            raise ValueError("Not all parameters set (geometry, detector, sample)")
            # pass
        else:
            self._engine_list.init(self._geometry, self._detector, self._sample.hkl_sample)

    @property
    def engines(self):
        return dict(
            (engine.name_get(), Engine(self, engine, self._engine_list))
            for engine in self._engine_list.engines_get()
        )

    @property
    def parameters(self):
        return self._engine.parameters

    @property
    def physical_axis_names(self):
        if self._axis_name_to_renamed:
            return list(self._axis_name_to_renamed.values())
        else:
            return self._geometry.axis_names_get()

    @physical_axis_names.setter
    def physical_axis_names(self, axis_name_map):
        """Set a persistent re-map of physical axis names

        Resets `inverted_axes`.

        Parameters
        ----------
        axis_name_map : dict
            {orig_axis_1: new_name_1, ...}
        """
        internal_axis_names = self._geometry.axis_names_get()
        if set(axis_name_map.keys()) != set(internal_axis_names):
            raise ValueError("Every axis name has to have a remapped name")

        self._axis_name_to_original = OrderedDict((axis_name_map[axis], axis) for axis in internal_axis_names)
        self._axis_name_to_renamed = OrderedDict((axis, axis_name_map[axis]) for axis in internal_axis_names)

        self._inverted_axes = []

    @property
    def inverted_axes(self):
        """The physical axis names to invert"""
        return self._inverted_axes

    @inverted_axes.setter
    def inverted_axes(self, to_invert):
        for axis in to_invert:
            assert axis in self.physical_axis_names

        self._inverted_axes = to_invert

    def _invert_physical_positions(self, pos):
        """Invert the physical axis positions based on the settings

        Parameters
        ----------
        pos : OrderedDict
            NOTE: Modified in-place
        """
        for axis in self._inverted_axes:
            pos[axis] = -pos[axis]
        return pos

    @property
    def physical_positions(self):
        """Physical (real) motor positions"""
        pos = self.physical_axes
        if self._inverted_axes:
            pos = self._invert_physical_positions(pos)

        return self.Position(*pos.values())

    @physical_positions.setter
    @_locked
    def physical_positions(self, positions):
        if self._inverted_axes:
            pos = self.Position(*positions)._asdict()
            pos = self._invert_physical_positions(pos)
            positions = list(pos.values())

        # Set the physical motor positions and calculate the pseudo ones
        self._geometry.axis_values_set(positions, self._units)
        self.update()

    @property
    def physical_axes(self):
        """Physical (real) motor positions as an OrderedDict"""
        return OrderedDict(
            # fmt: off
            zip(
                self.physical_axis_names,
                self._geometry.axis_values_get(self._units),
            )
            # fmt: on
        )

    @property
    def pseudo_axis_names(self):
        """Pseudo axis names from the current engine"""
        return self._engine.pseudo_axis_names

    @property
    def pseudo_positions(self):
        """Pseudo axis positions/values from the current engine"""
        return self._engine.pseudo_positions

    @property
    def pseudo_axes(self):
        """Ordered dictionary of axis name to position"""
        return self._engine.pseudo_axes

    def update(self):
        """Calculate the pseudo axis positions from the real axis positions"""
        return self._engine.update()

    def _get_axis_by_name(self, name):
        """Given an axis name, return the HklParameter

        Parameters
        ----------
        name : str
            If a name map is specified, this is the mapped name.
        """
        name = self._axis_name_to_original.get(name, name)
        return self._geometry.axis_get(name)

    @property
    def units(self):
        """The units used for calculations"""
        return self._unit_name

    def __getitem__(self, axis):
        return CalcParameter(
            self._get_axis_by_name(axis),
            units=self._unit_name,
            name=axis,
            inverted=axis in self._inverted_axes,
            geometry=self._geometry,
        )

    def __setitem__(self, axis, value):
        param = self[axis]
        param.value = value

    @_keep_physical_position
    def forward_iter(self, start, end, max_iters, *, threshold=0.99, decision_fcn=None):
        """Iteratively attempt to go from a pseudo start -> end position

        For every solution failure, the position is moved back.
        For every success, the position is moved closer to the destination.

        After up to max_iters, the position can be reached, the solutions will
        be returned. Otherwise, ValueError will be raised stating the last
        position that was reachable and the corresponding motor positions.

        Parameters
        ----------
        start : Position
        end : Position
        max_iters : int
            Maximum number of iterations
        threshold : float, optional
            Normalized proximity to `end` position to stop iterating
        decision_fcn : callable, optional
            Function to choose a solution from several. Defaults to picking the
            first solution. Here is the default ``decision_fcn()``::

                def decision(pseudo_position, solution_list):
                    return solution_list[0]

        Returns
        -------
        solutions : list

        Raises
        ------
        UnreachableError (ValueError)
            Position cannot be reached
            The last valid HKL position and motor positions are accessible
            in this exception instance.
        """
        start = np.array(start)
        end = np.array(end)

        if decision_fcn is None:
            decision_fcn = default_decision_function

        min_t = 0.0

        t = 1.0
        iters = 0
        valid_pseudo = None
        valid_real = None
        while iters < max_iters:
            try:
                pos = (1.0 - t) * start + t * end
                self.engine.pseudo_positions = pos
            except ValueError:
                # couldn't calculate - step back half-way
                t = (min_t + t) / 2.0
            else:
                if t > min_t:
                    min_t = t

                # successful calculation - move forward
                t = (t + 1) / 2.0

                valid_pseudo = self.engine.pseudo_positions
                valid_real = decision_fcn(valid_pseudo, self.engine.solutions)
                self.physical_positions = valid_real

                if t >= threshold:
                    break

            iters += 1

        try:
            self.engine.pseudo_positions = end
            return self.engine.solutions
        except ValueError:
            raise UnreachableError(
                f"Unable to solve. iterations={iters}/{max_iters}\n"
                f"Last valid position: {valid_pseudo}\n{valid_real} ",
                pseudo=valid_pseudo,
                physical=valid_real,
            )

    @_keep_physical_position
    def forward(self, position, engine=None):
        """Calculate real positions from pseudo positions."""

        with UsingEngine(self, engine):
            if self.engine is None:
                raise ValueError("Engine unset")

            self.engine.pseudo_positions = position
            return self.engine.solutions

    @_keep_physical_position
    def inverse(self, real):
        """Calculate pseudo positions from real positions."""
        self.physical_positions = real
        # self.update()  # done implicitly in setter
        return self.pseudo_positions

    def calc_linear_path(self, start, end, n, num_params=0, **kwargs):
        """
        Construct a trajectory from start to end with n steps (n+1 points).

        Example (for ``hkl`` engine)::

            >>> e4cv.calc.calc_linear_path((1,1,0), (1,-1,0), 4, num_params=3)
            [(1.0, 1.0, 0.0),
            (1.0, 0.5, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, -0.5, 0.0),
            (1.0, -1.0, 0.0)]
        """

        # from start to end, in a linear path
        singles = [np.linspace(start[i], end[i], n + 1) for i in range(num_params)]

        return list(zip(*singles))

    def _get_path_fcn(self, path_type):
        try:
            return getattr(self, "calc_%s_path" % (path_type))
        except AttributeError:
            raise ValueError("Invalid path type specified (%s)" % path_type)

    def get_path(self, start, end=None, n=100, path_type="linear", **kwargs):
        """ """
        num_params = len(self.pseudo_axis_names)

        start = np.array(start)

        path_fcn = self._get_path_fcn(path_type)

        if end is not None:
            end = np.array(end)
            if start.size == end.size == num_params:
                return path_fcn(start, end, n, num_params=num_params, **kwargs)

        else:
            positions = np.array(start)
            if positions.ndim == 1 and positions.size == num_params:
                # single position
                return [list(positions)]
            elif positions.ndim == 2:
                if positions.shape[0] == 1 and positions.size == num_params:
                    # [[h, k, l], ]
                    return [positions[0]]
                elif positions.shape[0] == num_params:
                    # [[h, k, l], [h, k, l], ...]
                    return [positions[i, :] for i in range(num_params)]

        raise ValueError("Invalid set of %s positions" % ", ".join(self.pseudo_axis_names))

    def __call__(
        # fmt: off
        self,
        start,
        end=None,
        n=100,
        engine=None,
        path_type="linear",
        **kwargs,
        # fmt: on
    ):
        with UsingEngine(self, engine):
            for pos in self.get_path(start, end=end, n=n, path_type=path_type, **kwargs):
                yield self.forward(pos, engine=None, **kwargs)

    def _repr_info(self):
        r = [
            f"engine={self.engine.name!r}",
            f"detector={self._detector!r}",
            f"sample={self._sample!r}",
            f"samples={self._samples!r}",
        ]

        return r

    def __repr__(self):
        return f"{self.__class__.__name__} ({', '.join(self._repr_info())})"

    def __str__(self):
        return repr(self)

    @property
    def _cfg_reciprocal(self):
        """Return reciprocal lattice to save as configuration."""
        return tuple(list(self.sample.reciprocal))


class CalcE4CH(CalcRecip):
    """Geometry: E4CH"""

    def __init__(self, **kwargs):
        super().__init__("E4CH", **kwargs)


class CalcE4CV(CalcRecip):
    """Geometry: E4CV"""

    def __init__(self, **kwargs):
        super().__init__("E4CV", **kwargs)


class CalcE6C(CalcRecip):
    """Geometry: E6C"""

    def __init__(self, **kwargs):
        super().__init__("E6C", **kwargs)


class CalcK4CV(CalcRecip):
    """Geometry: K4CV"""

    def __init__(self, **kwargs):
        super().__init__("K4CV", **kwargs)


class CalcK6C(CalcRecip):
    """Geometry: K6C"""

    def __init__(self, **kwargs):
        super().__init__("K6C", **kwargs)


class CalcPetra3_p09_eh2(CalcRecip):
    """Geometry: PETRA3 P09 EH2"""

    def __init__(self, **kwargs):
        super().__init__("PETRA3 P09 EH2", **kwargs)


class CalcPetra3_p23_4c(CalcRecip):
    """Geometry: PETRA3 P23 4C"""

    def __init__(self, **kwargs):
        super().__init__("PETRA3 P23 4C", **kwargs)


class CalcPetra3_p23_6c(CalcRecip):
    """Geometry: PETRA3 P23 6C"""

    def __init__(self, **kwargs):
        super().__init__("PETRA3 P23 6C", **kwargs)


class CalcSoleilMars(CalcRecip):
    """Geometry: SOLEIL MARS"""

    def __init__(self, **kwargs):
        super().__init__("SOLEIL MARS", **kwargs)


class CalcSoleilNanoscopiumRobot(CalcRecip):
    """Geometry: SOLEIL NANOSCOPIUM ROBOT"""

    def __init__(self, **kwargs):
        super().__init__("SOLEIL NANOSCOPIUM ROBOT", **kwargs)


class CalcSoleilSiriusKappa(CalcRecip):
    """Geometry: SOLEIL SIRIUS KAPPA"""

    def __init__(self, **kwargs):
        super().__init__("SOLEIL SIRIUS KAPPA", **kwargs)


class CalcSoleilSiriusTurret(CalcRecip):
    """Geometry: SOLEIL SIRIUS TURRET"""

    def __init__(self, **kwargs):
        super().__init__("SOLEIL SIRIUS TURRET", **kwargs)


class CalcSoleilSixsMed1p2(CalcRecip):
    """Geometry: SOLEIL SIXS MED1+2"""

    def __init__(self, **kwargs):
        super().__init__("SOLEIL SIXS MED1+2", **kwargs)


class CalcSoleilSixsMed2p2(CalcRecip):
    """Geometry: SOLEIL SIXS MED2+2"""

    def __init__(self, **kwargs):
        super().__init__("SOLEIL SIXS MED2+2", **kwargs)


class CalcSoleilSixsMed2p3(CalcRecip):
    """Geometry: SOLEIL SIXS MED2+3"""

    def __init__(self, **kwargs):
        super().__init__("SOLEIL SIXS MED2+3", **kwargs)


class CalcSoleilSixsMed2p3v2(CalcRecip):
    """Geometry: SOLEIL SIXS MED2+3 v2"""

    def __init__(self, **kwargs):
        super().__init__("SOLEIL SIXS MED2+3 v2", **kwargs)


class CalcZaxis(CalcRecip):
    """Geometry: ZAXIS"""

    def __init__(self, **kwargs):
        super().__init__("ZAXIS", **kwargs)
