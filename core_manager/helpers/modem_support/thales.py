from helpers.modem_support.default import BaseModule


class Thales(BaseModule):
    """
    Thales vendor class that contains default parameters
    and methods of Thales modules.
    """

    vendor_name = "Thales/Cinterion"
    vid = "1e2d"

    interface_name = "eth1"
    mode_status_command = 'AT^SSRVSET="actSrvSet"'
    reboot_command = "AT+CFUN=1,1"
    pdp_activate_command = "AT^SWWAN=1,1"
    pdp_status_command = "AT^SWWAN?"
    ecm_mode_setter_command = 'AT^SSRVSET="actSrvSet",1'
    ecm_mode_response = "^SSRVSET: 1\n"
    ccid_command = "AT+CCID"
    eps_mode_status_command="AT+CEMODE?"
    eps_mode_setter_command="AT+CEMODE=2"
    eps_data_centric_response="2"
