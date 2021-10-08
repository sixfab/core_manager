from helpers.modem_support.default import DefaultVendor

class Telit(DefaultVendor):
    vendor_name ="Telit"
    vid = "1bc7"

    interface_name = "wwan0"
    mode_status_command = "AT#USBCFG?"
    reboot_command = "AT#REBOOT"
    pdp_activate_command = "AT#ECM=1,0"
    pdp_status_command = "AT#ECM?"
    ecm_mode_setter_command = "AT#USBCFG=4"
    ecm_mode_response = "4"
    ccid_command = "AT+ICCID"