"""
diffract
--------

Support for diffractometer instances

BASE CLASS

.. autosummary::

    ~Diffractometer

DIFFRACTOMETER GEOMETRIES

.. autosummary::

    ~E4CH
    ~E4CV
    ~E6C
    ~K4CV
    ~K6C
    ~TwoC
    ~Zaxis

SPECIAL-USE DIFFRACTOMETER GEOMETRIES

.. autosummary::

    ~Med2p3
    ~Petra3_p09_eh2
    ~SoleilMars
    ~SoleilSiriusKappa
    ~SoleilSiriusTurret
    ~SoleilSixs
    ~SoleilSixsMed1p2
    ~SoleilSixsMed2p2

"""

from ophyd import Component as Cpt
from ophyd import PositionerBase
from ophyd import PseudoPositioner
from ophyd import Signal
from ophyd.pseudopos import pseudo_position_argument
from ophyd.pseudopos import real_position_argument
from ophyd.signal import ArrayAttributeSignal
from ophyd.signal import AttributeSignal
import logging
import pint
import pyRestTable

from . import calc


logger = logging.getLogger(__name__)


class Diffractometer(PseudoPositioner):
    """Diffractometer pseudopositioner

    .. autosummary::

        ~calc
        ~engine
        ~forward
        ~inverse
        ~pa
        ~wh
        ~_energy_changed
        ~_update_calc_energy

    This has a corresponding calculation engine from **hklpy** that does
    forward and inverse calculations.

    If instantiating a specific diffractometer class such as `E4C`, `E6C`,
    neither the `calc_inst` or the `calc_kw` parameters are required.

    However, there is the option to either pass in a calculation
    instance (with `calc_inst`) or keywords for the default calculation
    class (using `calc_kw`) to instantiate a new one.

    Parameters
    ----------
    prefix : str
        PV prefix for all components
    calc_kw : dict, optional
        Initializer arguments for the calc class
    decision_fcn : callable, optional
        The decision function to use when multiple solutions exist for a given
        forward calculation. Defaults to arbitrarily picking the first
        solution.
    read_attrs : list, optional
        Read attributes default to all pseudo and real positioners
    configuration_attrs : list, optional
        Defaults to the UB matrix and energy
    parent : Device, optional
        Parent device
    name : str, optional
        Device name

    Attributes
    ----------
    calc_class : sub-class of CalcRecip
        Reciprocal calculation class used with this diffractometer.
        If None (as in `hkl.diffract.Diffractometer`, `calc_inst` must be
        specified upon initialization.

    See Also
    --------
    :class:`hkl.diffract.E4CH`
    :class:`hkl.diffract.E4CV`
    :class:`hkl.diffract.E6C`
    :class:`hkl.diffract.K4CV`
    :class:`hkl.diffract.K6C`
    :class:`hkl.diffract.Med2p3`
    :class:`hkl.diffract.Petra3_p09_eh2`
    :class:`hkl.diffract.SoleilMars`
    :class:`hkl.diffract.SoleilSiriusKappa`
    :class:`hkl.diffract.SoleilSiriusTurret`
    :class:`hkl.diffract.SoleilSixs`
    :class:`hkl.diffract.SoleilSixsMed1p2`
    :class:`hkl.diffract.SoleilSixsMed2p2`
    :class:`hkl.diffract.TwoC`
    :class:`hkl.diffract.Zaxis`
    """

    calc_class = None

    # see: Documentation has examples to use an EPICS PV for energy.
    energy = Cpt(Signal, value=8.0, doc="Energy (in keV)")
    energy_units = Cpt(Signal, value="keV")
    energy_offset = Cpt(Signal, value=0)
    energy_update_calc_flag = Cpt(Signal, value=True)

    geometry_name = Cpt(
        AttributeSignal,
        attr="calc.geometry_name",
        doc="Diffractometer Geometry name",
    )
    class_name = Cpt(
        AttributeSignal,
        attr="__class__.__name__",
        doc="Diffractometer class name",
    )

    sample_name = Cpt(
        AttributeSignal, attr="calc.sample_name", doc="Sample name"
    )
    lattice = Cpt(
        ArrayAttributeSignal,
        attr="calc.sample.lattice",
        doc="Sample lattice",
    )
    lattice_reciprocal = Cpt(
        AttributeSignal,
        attr="calc.sample.reciprocal",
        doc="Reciprocal lattice",
    )
    U = Cpt(AttributeSignal, attr="calc.sample.U", doc="U matrix")
    UB = Cpt(AttributeSignal, attr="calc.sample.UB", doc="UB matrix")
    reflections = Cpt(
        ArrayAttributeSignal,
        attr="calc.sample.reflections",
        doc="Reflections",
    )
    ux = Cpt(
        AttributeSignal,
        attr="calc.sample.ux.value",
        doc="ux portion of the U matrix",
    )
    uy = Cpt(
        AttributeSignal,
        attr="calc.sample.uy.value",
        doc="uy portion of the U matrix",
    )
    uz = Cpt(
        AttributeSignal,
        attr="calc.sample.uz.value",
        doc="uz portion of the U matrix",
    )

    def __init__(
        self,
        prefix,
        calc_kw=None,
        decision_fcn=None,
        calc_inst=None,
        *,
        configuration_attrs=None,
        read_attrs=None,
        **kwargs,
    ):
        if calc_inst is not None:
            if not isinstance(calc_inst, self.calc_class):
                raise ValueError(
                    "Calculation instance must be derived "
                    f"from the class {self.calc_class}"
                )
            self._calc = calc_inst

        else:
            if calc_kw is None:
                calc_kw = {}

            self._calc = self.calc_class(lock_engine=True, **calc_kw)

        if not self.calc.engine_locked:
            # Reason for this is that the engine determines the pseudomotor
            # names, so if the engine is switched from underneath, the
            # pseudomotor will no longer function properly
            raise ValueError(
                "Calculation engine must be locked"
                " (CalcDiff.lock_engine set)"
            )

        if configuration_attrs is None:
            configuration_attrs = ["UB", "energy"]

        if decision_fcn is None:
            # the default decision function is to just grab solution #1:
            decision_fcn = calc.default_decision_function

        self._decision_fcn = decision_fcn

        super().__init__(
            prefix,
            read_attrs=read_attrs,
            configuration_attrs=configuration_attrs,
            **kwargs,
        )

        if read_attrs is None:
            # if unspecified, set the read attrs to the pseudo/real motor
            # positions once known
            self.read_attrs = list(self.PseudoPosition._fields) + list(
                self.RealPosition._fields
            )

        self.energy.subscribe(
            self._energy_changed, event_type=Signal.SUB_VALUE
        )

        self.energy_offset.subscribe(
            self._energy_offset_changed, event_type=Signal.SUB_VALUE
        )

        self.energy_units.subscribe(
            self._energy_units_changed, event_type=Signal.SUB_VALUE
        )

    @property
    def _calc_energy_update_permitted(self):
        """return boolean `True` if permitted"""
        acceptable_values = (1, "Yes", "locked", "OK", True, "On")
        return self.energy_update_calc_flag.get() in acceptable_values

    def _energy_changed(self, value=None, **kwargs):
        """
        Callback indicating that the energy signal was updated

        .. note::
            The `energy` signal is subscribed to this method
            in the :meth:`Diffractometer.__init__()` method.
        """
        if not self.connected:
            logger.warning(
                "%s not fully connected, %s.calc.energy not updated",
                self.name,
                self.name,
            )
            return

        if self._calc_energy_update_permitted:
            self._update_calc_energy(value)

    def _energy_offset_changed(self, value=None, **kwargs):
        """
        Callback indicating that the energy offset signal was updated

        .. note::
            The `energy_offset` signal is subscribed to this method
            in the :meth:`Diffractometer.__init__()` method.
        """
        if not self.connected:
            logger.warning(
                (
                    "%s not fully connected,"
                    " '%s.calc.energy_offset' not updated"
                ),
                self.name,
                self.name,
            )
            return

        # TODO: is there a loop back through _update_calc_energy?
        energy = pint.Quantity(self.calc.energy, "keV").to(
            self.energy_units.get()
        )
        self.energy.put(energy.magnitude - value)

    def _energy_units_changed(self, value=None, **kwargs):
        """
        Callback indicating that the energy units signal was updated

        .. note::
            The `energy_units` signal is subscribed to this method
            in the :meth:`Diffractometer.__init__()` method.
        """
        if not self.connected:
            logger.warning(
                (
                    "%s not fully connected,"
                    " '%s.calc.energy_units' not updated"
                ),
                self.name,
                self.name,
            )
            return

        # TODO: is there a loop back through _update_calc_energy?
        energy = pint.Quantity(self.calc.energy, "keV").to(value)
        self.energy.put(energy.magnitude - self.energy_offset.get())

    def _update_calc_energy(self, value=None, **kwargs):
        """
        writes self.calc.energy from value or self.energy
        """
        if not self.connected:
            logger.warning(
                "%s not fully connected, %s.calc.energy not updated",
                self.name,
                self.name,
            )
            return

        # use either supplied value or get from signal
        value = float(value or self.energy.get())

        # energy_offset has same units as energy
        value += self.energy_offset.get()

        # comment these lines to skip unit conversion
        units = self.energy_units.get()
        if units != "keV":
            keV = pint.Quantity(value, units).to("keV")
            value = keV.magnitude

        logger.debug("setting %s.calc.energy = %f (keV)", self.name, value)
        self.calc.energy = value
        self._update_position()

    @property
    def calc(self):
        """The calculation instance"""
        return self._calc

    @property
    def engine(self):
        """The calculation engine associated with the diffractometer"""
        return self.calc.engine

    # TODO so these calculations change the internal state of the hkl
    # calculation class, which is probably not a good thing
    # -- it becomes a problem when someone uses these functions
    # outside of move()

    @pseudo_position_argument
    def forward(self, pseudo):
        solutions = self.calc.forward_iter(
            start=self.position, end=pseudo, max_iters=100
        )
        logger.debug("pseudo to real: {}".format(solutions))
        return self._decision_fcn(pseudo, solutions)

    @real_position_argument
    def inverse(self, real):
        self.calc.physical_positions = real
        return self.PseudoPosition(*self.calc.pseudo_positions)

    def check_value(self, pos):
        """
        Raise exception if pos is not within limits.

        In a scan, a subset of the pseudo axes may be directed,
        which are given in a dict from a set message from the
        bluesky RunEngine.

        It is not permitted to scan both pseudo and real positioners.
        """
        if isinstance(pos, dict):
            # Redefine and fill in any missing values.

            for axis, target in pos.items():
                if hasattr(self, axis):
                    p = getattr(self, axis)
                    if p in self.real_positioners:
                        p.check_value(target)
                else:
                    raise KeyError(f"{axis} not in {self.name}")

            pos = [
                pos.get(p.attr_name, p.position)
                for p in self.pseudo_positioners
            ]
        super().check_value(pos)

    def pa(self, all_samples=False, printing=True):
        """
        Print All the diffractometer settings.

        EXAMPLE::
        ========================== =================================================================================
        term                       value
        ========================== =================================================================================
        diffractometer             fourc
        geometry                   E4CV
        class                      Fourc
        energy (keV)               8.0
        energy offset (keV)        0
        wavelength (angstrom)      1.54
        calc energy (keV)          8.05092
        calc wavelength (angstrom) 1.54
        calc engine                hkl
        mode                       bissector
        positions                  ===== =======
                                   name  value
                                   ===== =======
                                   omega 0.00000
                                   chi   0.00000
                                   phi   0.00000
                                   tth   0.00000
                                   ===== =======
                                   ============================= ===================================================
                                   term                          value
                                   ============================= ===================================================
                                   unit cell lengths (angstroms) a=1.54, b=1.54, c=1.54
                                   unit cell angles (degrees)    alpha=90.0, beta=90.0, gamma=90.0
                                   [U]                           [[1. 0. 0.]
                                                                  [0. 1. 0.]
                                                                  [0. 0. 1.]]
                                   [UB]                          [[ 4.07999046e+00 -2.49827363e-16 -2.49827363e-16]
                                                                  [ 0.00000000e+00  4.07999046e+00 -2.49827363e-16]
                                                                  [ 0.00000000e+00  0.00000000e+00  4.07999046e+00]]
                                   ============================= ===================================================
        ========================== =================================================================================

        Out[3]: <pyRestTable.rest_table.Table at 0x7f2c14764c40>
        """

        def addTable(tbl):
            return str(tbl).strip()

        def Package(**kwargs):
            return ", ".join([f"{k}={v}" for k, v in kwargs.items()])

        table = pyRestTable.Table()
        table.labels = "term value".split()

        table.addRow(("diffractometer", self.name))
        table.addRow(("geometry", self.geometry_name.get()))
        table.addRow(("class", self.class_name.get()))
        table.addRow(
            (
                f"energy ({self.energy_units.get()})",
                float(f"{self.energy.get():.5f}"),
            )
        )
        table.addRow(
            (
                f"energy offset ({self.energy_units.get()})",
                self.energy_offset.get(),
            )
        )
        table.addRow(
            ("wavelength (angstrom)", float(f"{self.calc.wavelength:.5f}"))
        )
        table.addRow(
            ("calc energy (keV)", float(f"{self.calc.energy:.5f}"))
        )
        table.addRow(
            (
                "calc wavelength (angstrom)",
                float(f"{self.calc.wavelength:.5f}"),
            )
        )
        table.addRow(("calc engine", self.calc.engine.name))
        table.addRow(("mode", self.calc.engine.mode))

        pt = pyRestTable.Table()
        pt.labels = "name value".split()
        if self.calc._axis_name_to_original:
            pt.addLabel("original name")
        for item in self.real_positioners:
            row = [item.attr_name, f"{item.position:.5f}"]
            k = self.calc._axis_name_to_original.get(item.attr_name)
            if k is not None:
                row.append(k)
            pt.addRow(row)
        table.addRow(("positions", addTable(pt)))

        # t = self.showConstraints(printing=False)
        # table.addRow(("constraints", addTable(t)))

        if all_samples:
            samples = self.calc._samples.values()
        else:
            samples = [self.calc._sample]
        for sample in samples:
            t = pyRestTable.Table()
            t.labels = "term value".split()
            nm = sample.name
            if all_samples and sample == self.calc.sample:
                nm += " (*)"

            t.addRow(
                (
                    "unit cell lengths (angstroms)",
                    Package(
                        **{
                            k: getattr(sample.lattice, k)
                            for k in "a b c".split()
                        }
                    ),
                )
            )
            t.addRow(
                (
                    "unit cell angles (degrees)",
                    Package(
                        **{
                            k: getattr(sample.lattice, k)
                            for k in "alpha beta gamma".split()
                        }
                    ),
                )
            )

            for i, ref in enumerate(sample._sample.reflections_get()):
                h, k, l = ref.hkl_get()
                pos_arr = ref.geometry_get().axis_values_get(
                    self.calc._units
                )
                t.addRow(
                    (f"ref {i+1} (hkl)", Package(**dict(h=h, k=k, l=l)))
                )
                t.addRow(
                    (
                        f"ref {i+1} positioners",
                        Package(
                            **{
                                k: f"{v:.5f}"
                                for k, v in zip(
                                    self.calc.physical_axis_names, pos_arr
                                )
                            }
                        ),
                    )
                )

            t.addRow(("[U]", sample.U))
            t.addRow(("[UB]", sample.UB))

            table.addRow((f"sample: {nm}", addTable(t)))

        if printing:
            print(table)

        return table

    def wh(self, printing=True):
        """
        WHere is the diffractometer?  Print a brief report.

        EXAMPLE::

            In [3]: e4cv.wh()
            ===================== =========
            term                  value
            ===================== =========
            diffractometer        e4cv
            sample name           main
            energy (keV)          8.0509
            energy offset (keV)   0.0
            wavelength (angstrom) 1.54000
            calc engine           hkl
            mode                  bissector
            h                     0.0
            k                     0.0
            l                     0.0
            omega                 0
            chi                   0
            phi                   0
            tth                   0
            ===================== =========

            Out[3]: <pyRestTable.rest_table.Table at 0x7f55c4775cd0>

        compare with similar function in SPEC (different geometry)::

            1117.KAPPA> wh
            H K L =  0  0  1.7345
            Alpha = 20  Beta = 20  Azimuth = 90
            Omega = 32.952  Lambda = 1.54
            Two Theta       Theta         Chi         Phi     K_Theta       Kappa       K_Phi
            40.000000   20.000000   90.000000   57.048500   77.044988  134.755995  114.093455
        """
        table = pyRestTable.Table()
        table.labels = "term value axis_type".split()
        table.addRow(("diffractometer", self.name, ""))
        table.addRow(("sample name", self.calc.sample.name, ""))
        table.addRow(
            (
                f"energy ({self.energy_units.get()})",
                float(f"{self.energy.get():.5f}"),
                "",
            )
        )
        table.addRow(
            (
                f"energy offset ({self.energy_units.get()})",
                self.energy_offset.get(),
                "",
            )
        )
        table.addRow(
            (
                "wavelength (angstrom)",
                float(f"{self.calc.wavelength:.5f}"),
                "",
            )
        )
        table.addRow(("calc engine", self.calc.engine.name, ""))
        table.addRow(("mode", self.calc.engine.mode, ""))

        pseudo_axes = [v.attr_name for v in self._pseudo]
        real_axes = [v.attr_name for v in self._real]
        for k in self._sig_attrs.keys():
            v = getattr(self, k)
            if not issubclass(v.__class__, PositionerBase):
                continue
            if k in real_axes:
                label = "real"
            elif k in pseudo_axes:
                label = "pseudo"
            else:
                label = "additional"
            table.addRow((k, v.position, label))

        if printing:
            print(table)

        return table


class E4CH(Diffractometer):
    calc_class = calc.CalcE4CH


class E4CV(Diffractometer):
    calc_class = calc.CalcE4CV


class E6C(Diffractometer):
    calc_class = calc.CalcE6C


class K4CV(Diffractometer):
    calc_class = calc.CalcK4CV


class K6C(Diffractometer):
    calc_class = calc.CalcK6C


class Petra3_p09_eh2(Diffractometer):
    calc_class = calc.CalcPetra3_p09_eh2


class SoleilMars(Diffractometer):
    calc_class = calc.CalcSoleilMars


class SoleilSiriusKappa(Diffractometer):
    calc_class = calc.CalcSoleilSiriusKappa


class SoleilSiriusTurret(Diffractometer):
    calc_class = calc.CalcSoleilSiriusTurret


class SoleilSixsMed1p2(Diffractometer):
    calc_class = calc.CalcSoleilSixsMed1p2


class SoleilSixsMed2p2(Diffractometer):
    calc_class = calc.CalcSoleilSixsMed2p2


class SoleilSixs(Diffractometer):
    calc_class = calc.CalcSoleilSixs


class Med2p3(Diffractometer):
    calc_class = calc.CalcMed2p3


class TwoC(Diffractometer):
    calc_class = calc.CalcTwoC


class Zaxis(Diffractometer):
    calc_class = calc.CalcZaxis
