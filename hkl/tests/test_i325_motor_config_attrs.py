import pytest
from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import Kind

import hkl

from .common import IOC_PV_PREFIX_GP

OMEGA_PV = f"{IOC_PV_PREFIX_GP}m1"
CHI_PV = f"{IOC_PV_PREFIX_GP}m2"
PHI_PV = f"{IOC_PV_PREFIX_GP}m3"
TTH_PV = f"{IOC_PV_PREFIX_GP}m4"

MOTOR_RECORD_CONFIG_ATTRS = sorted(
    """
        acceleration
        motor_egu
        user_offset
        user_offset_dir
        velocity
    """.split()
)


class FourC(hkl.SimMixin, hkl.E4CV):
    omega = Component(EpicsMotor, OMEGA_PV)
    chi = Component(EpicsMotor, CHI_PV)
    phi = Component(EpicsMotor, PHI_PV)
    tth = Component(EpicsMotor, TTH_PV)


class MyDevice(Device):
    omega = Component(EpicsMotor, OMEGA_PV)


device = MyDevice("", name="device")
fourc = FourC("", name="fourc")
motor = EpicsMotor(OMEGA_PV, name="motor")


@pytest.mark.parametrize("attr", MOTOR_RECORD_CONFIG_ATTRS)
@pytest.mark.parametrize(
    "motor, parent",
    [
        [motor, motor],
        [device.omega, device],
        [fourc.omega, fourc],
        [fourc.chi, fourc],
        [fourc.phi, fourc],
        [fourc.tth, fourc],
    ],
)
def test_i325(attr, motor, parent):
    """
    Check the configuration_attrs for EpicsMotor itself and as Component.

    https://github.com/bluesky/hklpy/issues/325

    EPICS IOC and motor records are necessary to demonstrate this problem. We
    prove the problem is NOT in the ophyd Devices by including them in the
    tests.

    Comparison of device's ``.read_configuration()`` output can show this
    problem. Compare EpicsMotor with any/all Diffractometer motors.
    """
    parent.wait_for_connection()
    motor.wait_for_connection()

    device_configuration = parent.read_configuration()
    device_configuration_keys = sorted(list(device_configuration))
    expected_key = f"{motor.name}_{attr}"
    assert attr in motor.component_names, f"{expected_key=!r}"
    component = getattr(motor, attr)
    assert isinstance(component, EpicsSignal)
    assert component.kind == Kind.config, f"{component.kind=!r}"

    assert expected_key in device_configuration_keys, f"{expected_key=!r}"
    # assert (
    #     sorted(motor.configuration_attrs) == MOTOR_RECORD_CONFIG_ATTRS
    # ), f"{motor.name=!r}"
