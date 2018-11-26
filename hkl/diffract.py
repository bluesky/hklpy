import logging
import numpy as np

from ophyd import (Signal, PseudoPositioner, Component as Cpt)
from ophyd.pseudopos import (pseudo_position_argument, real_position_argument)
from ophyd.utils.epics_pvs import (data_type, data_shape)
from ophyd.ophydobj import OphydObject, Kind
from ophyd.signal import AttributeSignal, ArrayAttributeSignal
from . import calc

logger = logging.getLogger(__name__)


class Diffractometer(PseudoPositioner):
    '''Diffractometer pseudopositioner

    This has a corresponding calculation engine from hklpy that does forward
    and inverse calculations.

    If instantiating a specific diffractometer class such as E4C, E6C, neither
    the `calc_inst` or the `calc_kw` parameters are required.

    However, there is the option to either pass in a calculation instance (with
    `calc_inst`) or keywords for the default calculation class (using
    `calc_kw`) to instantiate a new one.

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
    `hkl.diffract.E4CH`
    `hkl.diffract.E4CV`
    `hkl.diffract.E6C`
    `hkl.diffract.K4CV`
    `hkl.diffract.K6C`
    `hkl.diffract.Petra3_p09_eh2`
    `hkl.diffract.SoleilMars`
    `hkl.diffract.SoleilSiriusKappa`
    `hkl.diffract.SoleilSiriusTurret`
    `hkl.diffract.SoleilSixsMed1p2`
    `hkl.diffract.SoleilSixsMed2p2`
    `hkl.diffract.SoleilSixs`
    `hkl.diffract.Med2p3`
    `hkl.diffract.TwoC`
    `hkl.diffract.Zaxis`
    '''
    calc_class = None

    # NOTE: you can override the `energy` component here with your own
    #       EpicsSignal, for example, in your own subclass. You could then
    #       tie it to a pre-existing EPICS representation of the energy.
    #       This replaces the old 'energy_signal' parameter.
    energy = Cpt(Signal, value=8.0, doc='Energy (in keV)')
    sample_name = Cpt(AttributeSignal, attr='calc.sample_name',
                      doc='Sample name')
    lattice = Cpt(ArrayAttributeSignal, attr='calc.sample.lattice',
                  doc='Sample lattice')
    lattice_reciprocal = Cpt(AttributeSignal, attr='calc.sample.reciprocal',
                             doc='Reciprocal lattice')
    U = Cpt(AttributeSignal, attr='calc.sample.U', doc='U matrix')
    UB = Cpt(AttributeSignal, attr='calc.sample.UB', doc='UB matrix')
    reflections = Cpt(ArrayAttributeSignal, attr='calc.sample.reflections',
                      doc='Reflections')
    ux = Cpt(AttributeSignal, attr='calc.sample.ux.value',
             doc='ux portion of the U matrix')
    uy = Cpt(AttributeSignal, attr='calc.sample.uy.value',
             doc='uy portion of the U matrix')
    uz = Cpt(AttributeSignal, attr='calc.sample.uz.value',
             doc='uz portion of the U matrix')

    def __init__(self, prefix, calc_kw=None, decision_fcn=None,
                 calc_inst=None, *, configuration_attrs=None,
                 read_attrs=None,
                 **kwargs):
        if calc_inst is not None:
            if not isinstance(calc_inst, self.calc_class):
                raise ValueError('Calculation instance must be derived from '
                                 'the class {}'.format(self.calc_class))
            self._calc = calc_inst

        else:
            if calc_kw is None:
                calc_kw = {}

            self._calc = self.calc_class(lock_engine=True, **calc_kw)

        if not self._calc.engine_locked:
            # Reason for this is that the engine determines the pseudomotor
            # names, so if the engine is switched from underneath, the
            # pseudomotor will no longer function properly
            raise ValueError('Calculation engine must be locked'
                             ' (CalcDiff.lock_engine set)')

        if configuration_attrs is None:
            configuration_attrs = ['UB', 'energy']

        if decision_fcn is None:
            # the default decision function is to just grab solution #1:
            decision_fcn = calc.default_decision_function

        self._decision_fcn = decision_fcn

        super().__init__(prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         **kwargs)

        if read_attrs is None:
            # if unspecified, set the read attrs to the pseudo/real motor
            # positions once known
            self.read_attrs = (list(self.PseudoPosition._fields) +
                               list(self.RealPosition._fields))

        self.energy.subscribe(self._energy_changed,
                              event_type=Signal.SUB_VALUE)

    def _energy_changed(self, value=None, **kwargs):
        '''
        Callback indicating that the energy signal was updated
        '''
        logger.debug('{0.name} energy changed: {1}'.format(self, value))
        self._calc.energy = value
        self._update_position()

    @property
    def calc(self):
        '''The calculation instance'''
        return self._calc

    @property
    def engine(self):
        '''The calculation engine associated with the diffractometer'''
        return self._calc.engine

    # TODO so these calculations change the internal state of the hkl
    # calculation class, which is probably not a good thing -- it becomes a
    # problem when someone uses these functions outside of move()

    @pseudo_position_argument
    def forward(self, pseudo):
        solutions = self._calc.forward_iter(start=self.position, end=pseudo,
                                            max_iters=100)
        logger.debug('pseudo to real: {}'.format(solutions))
        return self._decision_fcn(pseudo, solutions)

    @real_position_argument
    def inverse(self, real):
        self._calc.physical_positions = real
        return self.PseudoPosition(*self._calc.pseudo_positions)


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
