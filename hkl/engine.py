"""
Low-level support to Hkl computation engine support for diffractometers

.. autosummary::

    ~CalcParameter
    ~Engine
    ~Parameter
    ~Solution

"""

from __future__ import print_function
from . import util
from collections import OrderedDict
import logging

__all__ = """
    CalcParameter
    Engine
    Parameter
    Solution
""".split()
logger = logging.getLogger(__name__)


class Parameter(object):
    """HKL library parameter object

    .. autosummary::

        ~inverted
        ~hkl_parameter
        ~units
        ~name
        ~value
        ~user_units
        ~default_units
        ~limits

    Example::

        Parameter(
                name='None (internally: ux)',
                limits=(min=-180.0, max=180.0),
                value=0.0,
                fit=True,
                inverted=False,
                units='Degree')

    """

    def __init__(self, param, units="user", name=None, inverted=False):
        self._param = param
        self._unit_name = units
        self._units = util.units[units]
        self._name = name
        self._inverted = inverted

    @property
    def inverted(self):
        """Is the value inverted internally?"""
        return self._inverted

    @property
    def hkl_parameter(self):
        """The HKL library parameter object"""
        return self._param

    @property
    def units(self):
        """Either ``user`` or ``default``."""
        return self._unit_name

    @property
    def name(self):
        """ """
        name = self._param.name_get()
        if self._name != name:
            return f"{self._name} (internally: {name})"
        return name

    @property
    def value(self):
        """ """
        return self._param.value_get(self._units)

    @property
    def user_units(self):
        """A string representing the user unit type"""
        return self._param.user_unit_get()

    @property
    def default_units(self):
        """A string representing the default unit type"""
        return self._param.default_unit_get()

    @value.setter
    def value(self, value):
        if self._inverted:
            value *= -1.0

        self._param.value_set(value, self._units)

    @property
    def fit(self):
        """True if the parameter can be fit or not"""
        return bool(self._param.fit_get())

    @fit.setter
    def fit(self, fit):
        self._param.fit_set(int(fit))

    @property
    def limits(self):
        """(low, high)"""
        if self._inverted:
            low, high = self._param.min_max_get(self._units)
            return (-high, -low)
        else:
            return self._param.min_max_get(self._units)

    @limits.setter
    def limits(self, lims):
        low, high = lims
        if self._inverted:
            self._param.min_max_set(-high, -low, self._units)
        else:
            self._param.min_max_set(low, high, self._units)

    def _repr_info(self):
        r = [
            f"name={self.name!r}",
            f"limits={self.limits!r}",
            f"value={self.value!r}",
            f"fit={self.fit!r}",
            f"inverted={self.inverted!r}",
        ]

        if self._unit_name == "user":
            r.append(f"units={self.user_units!r}")
        else:
            r.append(f"units={self.default_units!r}")

        return r

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self._repr_info())})"

    def __str__(self):
        info = self._repr_info()
        # info.append(self.)
        return f"{self.__class__.__name__}({', '.join(info)})"


class Solution(object):
    """
    Solution of the conversion from (hkl) to axes.

    .. autosummary::

        ~axis_names
        ~positions
        ~select
        ~units
    """

    def __init__(self, engine, list_item, class_):
        self._class = class_
        self._list_item = list_item.copy()
        self._geometry = list_item.geometry_get().copy()
        self._engine = engine

    def __getitem__(self, axis):
        return self._geometry.axis_get(axis)

    @property
    def axis_names(self):
        """List real axis names of the solution."""
        return self._geometry.axis_names_get()

    @property
    def positions(self):
        """List real axis values of the solution."""
        return self._class(*self._geometry.axis_values_get(self._engine._units))

    @property
    def units(self):
        """ """
        return self._engine.units

    def select(self):
        """Select a solution."""
        self._engine._engine_list.select_solution(self._list_item)

    def _repr_info(self):
        r = [
            repr(self.positions),
            f"units={self._engine.units!r}",
        ]

        return r

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self._repr_info())})"


class Engine(object):
    """
    HKL calculation engine

    .. autosummary::

        ~engine
        ~mode
        ~name
        ~parameters
        ~parameters_values
        ~pseudo_axes
        ~pseudo_axis_names
        ~pseudo_positions
        ~solutions
        ~units
        ~update
    """

    def __init__(self, calc, engine, engine_list):
        self._calc = calc
        self._engine = engine
        self._engine_list = engine_list

    @property
    def name(self):
        """Name of this engine."""
        return self._engine.name_get()

    @property
    def mode(self):
        """HKL calculation mode (see also `HklCalc.modes`)"""
        return self._engine.current_mode_get()

    @mode.setter
    def mode(self, mode):
        if mode not in self.modes:
            raise ValueError("Unrecognized mode %r; choose from: %s" % (mode, ", ".join(self.modes)))

        return self._engine.current_mode_set(mode)

    @property
    def modes(self):
        return self._engine.modes_names_get()

    @property
    def solutions(self):
        """Allowed real solutions given the pseudo position."""
        return tuple(self._solutions)

    def update(self):
        """Calculate the pseudo axis positions from the real axis positions."""
        # TODO: though this works, maybe it could be named better on the hkl
        # side? either the 'get' function name or the fact that the EngineList
        # is more than just a list...

        self._engine_list.get()

    @property
    def parameters(self):
        """List the names of the additional parameters."""
        return self._engine.parameters_names_get()

    @property
    def parameters_values(self):
        """List the values of the additional parameters."""
        return self._engine.parameters_values_get(self._units)

    @property
    def pseudo_axis_names(self):
        """List the names of the pseudo axes."""
        return self._engine.pseudo_axis_names_get()

    @property
    def pseudo_axes(self):
        """List of pseudo axes as tuples: ``[(name, value)]``."""
        return OrderedDict(zip(self.pseudo_axis_names, self.pseudo_positions))

    @property
    def pseudo_positions(self):
        """List the values of the pseudo positioners."""
        return self._engine.pseudo_axis_values_get(self._units)

    @pseudo_positions.setter
    def pseudo_positions(self, values):
        try:
            geometry_list = self._engine.pseudo_axis_values_set(values, self._units)
        except util.GLib.GError as ex:
            raise ValueError("Calculation failed (%s)" % ex)

        Position = self._calc.Position

        def get_position(item):
            return Position(*item.geometry_get().axis_values_get(self._units))

        self._solutions = [get_position(item) for item in geometry_list.items()]

    def __getitem__(self, name):
        try:
            return self.pseudo_axes[name]
        except KeyError:
            raise ValueError("Unknown axis name: %s" % name)

    def __setitem__(self, name, value):
        values = self.pseudo_positions
        try:
            idx = self.pseudo_axis_names.index(name)
        except IndexError:
            raise ValueError("Unknown axis name: %s" % name)

        values[idx] = float(value)
        self.pseudo_positions = values

    @property
    def units(self):
        """The units used for calculations"""
        return self._calc.units

    @property
    def _units(self):
        """The (internal) units used for calculations"""
        return self._calc._units

    @property
    def engine(self):
        """The calculation engine"""
        return self._engine

    def _repr_info(self):
        r = [
            f"parameters={self.parameters!r}",
            f"pseudo_axes={self.pseudo_axes!r}",
            f"mode={self.mode!r}",
            f"modes={self.modes!r}",
            f"units={self.units!r}",
        ]

        return r

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self._repr_info())})"


# when updating parameters we need to update the parent geometry object
class CalcParameter(Parameter):
    """
    Like calc parameter but needs reference to a geometry object.
    Updates to the parameter should be propagated back to the geometry.

    .. autosummary::

        ~fit
        ~limits
        ~value

    Parameters
    ----------
        param : HklParameter
        geometry: Geometry object
    """

    def __init__(self, param, geometry, *args, **kwargs):
        super().__init__(param, *args, **kwargs)
        self.param_name = param.name_get()
        # you may wonder why we stash geometry object rather than axis
        # this is because the axis params can only be updated from the geometry
        self._geometry = geometry

    @property
    def limits(self):
        """Allowed range of values (low, high)."""
        axis = self._geometry.axis_get(self.param_name)
        low, high = axis.min_max_get(self._units)
        if self._inverted:
            return (-high, -low)
        return low, high

    @limits.setter
    def limits(self, lims):
        low, high = lims
        if self._inverted:
            low, high = -high, -low
        self._param.min_max_set(low, high, self._units)
        # param name is the true name of axis
        axis = self._geometry.axis_get(self.param_name)
        axis.min_max_set(low, high, self._units)
        self._geometry.axis_set(self.param_name, axis)

    @property
    def value(self):
        """Position of this axis."""
        axis = self._geometry.axis_get(self.param_name)
        return axis.value_get(self._units)

    @value.setter
    def value(self, value):
        if self._inverted:
            value *= -1.0

        # param name is the true name of axis
        axis = self._geometry.axis_get(self.param_name)
        axis.value_set(value, self._units)
        self._geometry.axis_set(self.param_name, axis)

    @property
    def fit(self):
        """True if the parameter can be fit or not"""
        axis = self._geometry.axis_get(self.param_name)
        return bool(axis.fit_get())

    @fit.setter
    def fit(self, fit):
        # param name is the true name of axis
        axis = self._geometry.axis_get(self.param_name)
        axis.fit_set(fit)
        self._geometry.axis_set(self.param_name, axis)
