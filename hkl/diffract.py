import logging

from . import calc
from ophyd import (Signal, PseudoPositioner)
from ophyd import (Component as Cpt)

logger = logging.getLogger(__name__)


class Diffractometer(PseudoPositioner):
    calc_class = None

    # NOTE: you can override the `energy` component here with your own
    #       EpicsSignal, for example, in your own subclass. You could then
    #       tie it to a pre-existing EPICS representation of the energy.
    #       This replaces the old 'energy_signal' parameter.
    energy = Cpt(Signal, value=8.0, doc='Energy (in keV)')

    def __init__(self, prefix, calc_kw=None, decision_fcn=None,
                 calc_inst=None,
                 **kwargs):
        if calc_inst is not None:
            if not isinstance(calc_inst, self.calc_class):
                raise ValueError('Calculation instance must be derived from '
                                 'the class {}'.format(self.calc_class))
            self._calc = calc_inst

        else:
            if calc_kw is None:
                calc_kw = {}

            calc_kw = dict(calc_kw)
            self._calc = self.calc_class(lock_engine=True, **calc_kw)

        if not self._calc.engine_locked:
            # Reason for this is that the engine determines the pseudomotor
            # names, so if the engine is switched from underneath, the
            # pseudomotor will no longer function properly
            raise ValueError('Calculation engine must be locked'
                             ' (CalcDiff.lock_engine set)')

        if decision_fcn is None:
            # the default decision function is to just grab solution #1:
            decision_fcn = calc.default_decision_function

        self._decision_fcn = decision_fcn

        super().__init__(prefix, **kwargs)

        self.energy.subscribe(self._energy_changed,
                              event_type=Signal.SUB_VALUE)

    def _energy_changed(self, value=None, **kwargs):
        '''
        Callback indicating that the energy signal was updated
        '''
        energy = value

        logger.debug('{0.name} energy changed: {1}'.format(self, value))
        self._calc.energy = energy
        self._update_position()

    @property
    def calc(self):
        return self._calc

    @property
    def engine(self):
        return self._calc.engine

    # TODO so these calculations change the internal state of the hkl
    # calculation class, which is probably not a good thing -- it becomes a
    # problem when someone uses these functions outside of move()

    def forward(self, pseudo):
        solutions = self._calc.forward_iter(start=self.position, end=pseudo,
                                            max_iters=100)
        logger.debug('pseudo to real: {}'.format(solutions))
        return self._decision_fcn(pseudo, solutions)

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
