from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
import hkl


M1_PV = "gp:m1"
M2_PV = "gp:m2"
M3_PV = "gp:m3"
M4_PV = "gp:m4"
CONFIG_ATTRS_EXPECTED = (
    "user_offset user_offset_dir velocity acceleration motor_egu".split()
)


def test_i325():
    """
    Check the configuration_attrs for EpicsMotor itself and as Component.

    https://github.com/bluesky/hklpy/issues/325
    """

    # First, we prove the problem is NOT in the ophyd Devices.
    class MyDevice(Device):
        motor = Component(EpicsMotor, "")

    motor_device = MyDevice(M1_PV, name="motor_device")
    motor_object = EpicsMotor(M1_PV, name="motor_object")
    motor_device.wait_for_connection()
    motor_object.wait_for_connection()
    assert motor_object.configuration_attrs == CONFIG_ATTRS_EXPECTED
    assert motor_device.motor.configuration_attrs == motor_object.configuration_attrs

    # But the original statement of the problem is for data from databroker after a run.
    # motor: list(db[-1].descriptors[0]['configuration']['es_diag1_y']['data'] )
    # tardis: list(db[-1].descriptors[0]['configuration']['tardis']['data'] )
    # In the second case, only some of the config attrs are present for each motor.
    # Different ones for each motor are reported.

    # Comparison of device's .read_configuration() output can show this problem.
    # Compare EpicsMotor with any/all Diffractometer motor.

    class Fourc(hkl.SimMixin, hkl.E4CV):
        omega = Component(EpicsMotor, M1_PV)
        chi = Component(EpicsMotor, M2_PV)
        phi = Component(EpicsMotor, M3_PV)
        tth = Component(EpicsMotor, M4_PV)

    fourc = Fourc("", name="fourc")
    fourc.wait_for_connection()

    def check_config_attrs(device):
        device_configuration = device.read_configuration()
        for attr in CONFIG_ATTRS_EXPECTED:
            expected_key = f"{device.name}_{attr}"
            assert expected_key in device_configuration, f"{expected_key=!r}"

    for item in (
        motor_object,
        motor_device.motor,
        fourc.omega,
        fourc.chi,
        fourc.phi,
        fourc.tth,
    ):
        check_config_attrs(item)
