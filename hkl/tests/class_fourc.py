import pytest
from ophyd import Component as Cpt
from ophyd import (PseudoSingle, SoftPositioner)

import gi
gi.require_version('Hkl', '5.0')
# NOTE: MUST call gi.require_version() BEFORE import hkl
from hkl.diffract import E4CV


class Fourc(E4CV):
    h = Cpt(PseudoSingle, '')
    k = Cpt(PseudoSingle, '')
    l = Cpt(PseudoSingle, '')

    omega = Cpt(SoftPositioner)
    chi = Cpt(SoftPositioner)
    phi = Cpt(SoftPositioner)
    tth = Cpt(SoftPositioner)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for p in self.real_positioners:
            p._set_position(0)  # give each a starting position


@pytest.fixture(scope='function')
def fourc():
    fourc = Fourc('', name='fourc')
    fourc.wait_for_connection()
    # fourc._update_calc_energy()
    return fourc
