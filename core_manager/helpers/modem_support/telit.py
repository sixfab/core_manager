from helpers.modem_support.default import BaseModule


class Telit(BaseModule):
    """
    Telit vendor class that contains default parameters
    and methods of Telit modules.
    """

    vendor_name = "Telit"
    vid = "1bc7"

    interface_name = "wwan0"
    mode_status_command = "AT#USBCFG?"
    reboot_command = "AT#REBOOT"
    pdp_activate_command = "AT#ECM=1,0"
    pdp_status_command = "AT#ECM?"
    ecm_mode_setter_command = "AT#USBCFG=4"
    ecm_mode_response = "4"
    ccid_command = "AT+ICCID"
    eps_mode_status_command="AT+CEMODE?"
    eps_mode_setter_command="AT+CEMODE=2"
    eps_data_centric_response="2"
