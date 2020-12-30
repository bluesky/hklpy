from ophyd import Component as Cpt
from ophyd import (PseudoSingle, EpicsMotor, SoftPositioner, Signal)
import gi
gi.require_version('Hkl', '5.0')
from hkl.diffract import E6C  #this works for mu=0
from ophyd.pseudopos import (pseudo_position_argument, real_position_argument)

from ophyd.positioner import SoftPositioner

## convert all the motors below to sim motors

# Add MuR and MuT to bluesky list of motors and detectors.
#muR = EpicsMotor('XF:23ID1-ES{Dif-Ax:MuR}Mtr', name='muR')
muR = SoftPositioner(name='muR', labels={'muR'})
muR.set(0.0)
# use the line below if very paranoid
# muR = EpicsSignal('XF:23ID1-ES{Dif-Ax:MuR}Mtr.RBV', name='muR')
#muT = EpicsMotor('XF:23ID1-ES{Dif-Ax:MuT}Mtr', name='muT')
muT = SoftPositioner(name='muT', labels={'muT'})
muT.set(0.0)

# TODO: fix upstream!!
class NullMotor(SoftPositioner):
    @property
    def connected(self):
        return True


class Tardis(E6C):  #this works for mu=0
    h = Cpt(PseudoSingle, '', labels=['tardis'])
    k = Cpt(PseudoSingle, '', labels=['tardis'])
    l = Cpt(PseudoSingle, '', labels=['tardis'])

    # theta = Cpt(EpicsMotor, 'XF:23ID1-ES{Dif-Ax:Th}Mtr', labels=['tardis'])
    theta = Cpt(SoftPositioner, name= 'theta', labels=['tardis'])
    mu = Cpt(NullMotor, labels=['tardis'])

    chi =   Cpt(NullMotor, labels=['tardis'])
    phi =   Cpt(NullMotor, labels=['tardis'])
    #delta = Cpt(EpicsMotor, 'XF:23ID1-ES{Dif-Ax:Del}Mtr', labels=['tardis'])
    delta = Cpt(SoftPositioner, name='delta', labels=['tardis'])
    #gamma = Cpt(EpicsMotor, 'XF:23ID1-ES{Dif-Ax:Gam}Mtr', labels=['tardis'])
    gamma = Cpt(SoftPositioner, name='delta', labels=['tardis'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # prime the 3 null-motors with initial values
        # otherwise, position == None --> describe, etc gets borked
        self.chi.move(0.0)
        self.phi.move(0.0)

        #added for simulated tardis
        self.theta.move(0.0)
        self.delta.move(0.0)
        self.gamma.move(0.0)

        # we have to use a motor for omega to keep hkl happy,
        # but want to keep omega as read-only and to follow muR
        def muR_updater(value, **kwargs):
            self.mu.move(value)

        muR.subscribe(muR_updater)

    @pseudo_position_argument
    def set(self, position):
        return super().set([float(_) for _ in position])

# FIXME: hack to get around what should have been done at init of tardis_calc instance
# tardis_calc._lock_engine = True

# tardis = Tardis('', name='tardis', calc_inst=tardis_calc)
tardis = Tardis('', name='tardis')

# re-map Tardis' axis names onto what an E6C expects
name_map = {'mu': 'theta', 'omega': 'mu', 'chi': 'chi', 'phi': 'phi', 'gamma': 'delta', 'delta': 'gamma'}


tardis.calc.physical_axis_names = name_map

tardis.calc.engine.mode = 'lifting_detector_mu'  #THis is for E6C, it exists for petra3_09..., but not loaded

# from this point, we can configure the Tardis instance
from hkl.util import Lattice

## lengths are in Angstrom, angles are in degrees
lattice = Lattice(a=4.128, b=4.128, c=4.128, alpha=90.0, beta=90.0, gamma=90.0)
#
## add the sample to the calculation engine
tardis.calc.new_sample('sample_1', lattice=lattice)

# apply some constraints

# Theta
tardis.calc['theta'].limits = (-181, 181)
tardis.calc['theta'].value = 0
tardis.calc['theta'].fit = True

# we don't have it. Fix to 0
tardis.calc['phi'].limits = (0, 0)
tardis.calc['phi'].value = 0
tardis.calc['phi'].fit = False

# we don't have it. Fix to 0
tardis.calc['chi'].limits = (0, 0)
tardis.calc['chi'].value = 0
tardis.calc['chi'].fit = False

# we don't have it!! Fix to 0
tardis.calc['mu'].limits = (0, 0)
tardis.calc['mu'].value = 0#tardis.omega.position.real
tardis.calc['mu'].fit = False

# Attention naming convention inverted at the detector stages!
# delta
tardis.calc['delta'].limits = (-5, 180)
tardis.calc['delta'].value = 0
tardis.calc['delta'].fit = True

# gamma
tardis.calc['gamma'].limits = (-2.81, 183.1)
tardis.calc['gamma'].value = 0
tardis.calc['gamma'].fit = True

tardis.calc.energy = (572 + 1.0)/10000

r14_20K_th0 = tardis.calc.sample.add_reflection(1, 1, 0,
    position=tardis.calc.Position(theta=52.8806-2.1039, mu=0.0, chi=0.0,
    phi=0.0, delta=107.411, gamma=-3.75)) #this might be -3.25
r15_20K_th0 = tardis.calc.sample.add_reflection(1, 1, 1,
    position=tardis.calc.Position(theta=115.3521-2.1039, mu=0.0, chi=0.0,
    phi=0.0, delta=161.9392, gamma=-3.8716))

tardis.calc.sample.compute_UB(r14_20K_th0, r15_20K_th0)

tardis.lattice.put(lattice)
