from helpers.modem_support.default import BaseModule
from helpers.logger import logger
from helpers.commander import send_at_com

class Quectel(BaseModule):
    """
    Quectel vendor class that contains default parameters
    and methods of Quectel modules.
    """

    vendor_name = "Quectel"
    vid = "2c7c"

    interface_name = "usb0"
    mode_status_command = 'AT+QCFG="usbnet"'
    reboot_command = "AT+CFUN=1,1"
    pdp_activate_command = "AT"
    pdp_status_command = "AT+CGACT?"
    ecm_mode_setter_command = 'AT+QCFG="usbnet",1'
    ecm_mode_response = '"usbnet",1'
    ccid_command = "AT+ICCID"
    eps_mode_status_command='AT+QNVFW="/nv/item_files/modem/mmode/ue_usage_setting"'
    eps_mode_setter_command='AT+QNVFW="/nv/item_files/modem/mmode/ue_usage_setting",01'
    eps_data_centric_response="01"

    # +QENG: "servingcell" response map for different technologies
    serving_cell_response_map = {
        "nr5g-sa": {
            "radio_type": 2,
            "mcc": 4,
            "mnc": 5,
            "tac": 8,
            "cid": 6,
            "psc": 7,
        },
        "lte": {
            "radio_type": 2,
            "mcc": 4,
            "mnc": 5,
            "tac": 12,
            "cid": 6,
            "psc": 7,
        },
        "wcdma": {
            "radio_type": 2,
            "mcc": 3,
            "mnc": 4,
            "lac": 5,
            "cid": 6,
            "psc": 8,
        },
        "gsm": {
            "radio_type": 2,
            "mcc": 3,
            "mnc": 4,
            "lac": 5,
            "cid": 6,
            "ta": 19,
        }
    }
    

    def read_geoloc_data(self):
        """
        Reads required data from modem in order to use at geolocation API
        """
        logger.info("Getting raw geolocation data...")
        print("OKKKKKKKKKKKKKKKKKKK")

        output = send_at_com('AT+QENG="servingcell"', "OK")
        if output[2] == 0:
            print(output[0])
        else:
            raise RuntimeError(output[0])
