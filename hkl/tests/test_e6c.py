# Modified in order to create a safe simulation environment 2018/01/30
#from ophyd.sim import SynAxis
from ophyd import Component as Cpt
from ophyd import (PseudoSingle, EpicsMotor, SoftPositioner, Signal)
from hkl.diffract import E6C  #this works for mu=0
#from hkl.diffract import E6C  #this works for any mu
from ophyd.pseudopos import (pseudo_position_argument, real_position_argument)


# TODO: fix upstream!!
class NullMotor(SoftPositioner):
    @property
    def connected(self):
        return True

class Tardis(E6C):  #this works for mu=0
    h = Cpt(PseudoSingle, '')
    k = Cpt(PseudoSingle, '')
    l = Cpt(PseudoSingle, '')

    theta = Cpt(NullMotor, name='theta')
    mu = Cpt(NullMotor, name='mu')
    chi =   Cpt(NullMotor, name='chi')
    phi =   Cpt(NullMotor, name='phi')
    delta = Cpt(NullMotor, name='delta')
    gamma = Cpt(NullMotor, name='gamma')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @pseudo_position_argument
    def set(self, position):
        return super().set([float(_) for _ in position])

# tardis = Tardis('', name='tardis', calc_inst=tardis_calc)
tardis = Tardis('', name='tardis')
# re-map Tardis' axis names onto what an E6C expects
#name_map = {'mu': 'theta', 'omega': 'mu', 'chi': 'chi', 'phi': 'phi', 'gamma': 'delta', 'delta': 'gamma'}
name_map = {'mu': 'theta', 'omega': 'mu', 'chi': 'chi', 'phi': 'phi', 'gamma': 'delta', 'delta': 'gamma'}
tardis.calc.physical_axis_names = name_map
#tardis.calc.engine.mode = 'lifting_detector_mu'  #THis is for E6C, it exists for petra3_09..., but not loaded
tardis.calc.engine.mode = 'lifting_detector_mu'  #THis is for E6C, it exists for petra3_09..., but not loaded


test_lims = (-10, 12.123)
tardis.calc['delta'].limits = test_lims
assert tardis.calc['delta'].limits == test_lims

test_value = 123.321312
tardis.calc['delta'].value = test_value
assert tardis.calc['delta'].value == test_value

test_fit = False
tardis.calc['delta'].fit = test_fit
assert tardis.calc['delta'].fit == test_fit

test_fit = True
tardis.calc['delta'].fit = test_fit
assert tardis.calc['delta'].fit == test_fit
