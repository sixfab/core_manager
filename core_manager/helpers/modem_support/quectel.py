import time

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
    desired_pdp_status = "1,1"
    ecm_mode_setter_command = 'AT+QCFG="usbnet",1'
    ecm_mode_response = '"usbnet",1'
    ccid_command = "AT+ICCID"
    eps_mode_status_command='AT+QNVFW="/nv/item_files/modem/mmode/ue_usage_setting"'
    eps_mode_setter_command='AT+QNVFW="/nv/item_files/modem/mmode/ue_usage_setting",01'
    eps_data_centric_response="01"
    

    # +QENG: "servingcell" response map for different technologies
    serving_cell_response_map = {
        "nr5g": {
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
        }
    }


    def read_geoloc_data(self):
        """
        Reads required data from modem in order to use at geolocation API
        """
        logger.info("Getting raw geolocation data...")
        radio_type_id = 2

        output = send_at_com('AT+QENG="servingcell"', "OK")
        if output[2] == 0:
            data = output[0].split(",")
            radio_type = data[radio_type_id].replace('"','').casefold()

            try:
                for key in self.serving_cell_response_map:
                    if key.find(radio_type) != -1:
                        temp = self.serving_cell_response_map.get(key, {})

                for key in temp:
                    self.geolocation[key] = data[temp[key]].replace('"','').casefold()
            except:
                raise ValueError("Geolocation data is broken")
        else:
            raise RuntimeError(output[0])

        # str/hex/int conversation
        try:
            for key in self.geolocation:
                if key in ["tac", "lac", "psc", "cid"]:
                    self.geolocation[key] = int(self.geolocation[key], 16)
                elif key in ["mcc", "mnc"]:
                    self.geolocation[key] = int(self.geolocation[key])
        except:
            raise ValueError("read_geoloc_data --> error occured converting hex to int")
