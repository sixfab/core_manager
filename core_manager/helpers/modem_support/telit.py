import time

from helpers.modem_support.default import BaseModule
from helpers.logger import logger
from helpers.commander import send_at_com, parse_output


# Telit Vendor Default Module Class
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

    radio_type_table = {
        0 : "gsm",
        2 : "wcdma/umtc",
        7 : "lte",
        12 : "ng-ran",
        13 : "e-ultra-nr dual"
    }

    rfsts_response_map = {
        "nr5g": {
            "mcc-mnc": 0,
            "tac": 5,
            "cid": 11,
            "operator" : 13,
        },
        "lte": {
            "mcc-mnc": 0,
            "tac": 5,
            "cid": 10,
            "operator" : 12,
        },
        "wcdma/umtc": {
            "mcc-mnc": 0,
            "lac": 6,
            "cid": 14,
            "operator" : 16,
        },
        "gsm": {
            "mcc-mnc": 0,
            "lac": 3,
            "cid": 9,
            "ta": 19,
            "operator" : 11,
        }
    }

    servinfo_response_map = {
        "nr5g": {
            "psc": 4,
        },
        "lte": {
            "psc" : 4,
        },
        "wcdma/umtc": {
            "psc" : 4,
        }
    }


    def read_geoloc_data(self):
        """
        Reads required data from modem in order to use at geolocation API
        """
        old_geolocation = self.geolocation

        logger.info("Getting raw geolocation data...")
        radio_type_id = 3
        radio_type = None

        output = send_at_com("AT+COPS?", "OK")
        if output[2] == 0:
            try:
                data = parse_output(output, "COPS:", "\n").split(",")
                radio_type_index = int(data[radio_type_id])
                radio_type = self.radio_type_table.get(radio_type_index)
            except:
                raise ValueError("read_geoloc_data --> error occured parsing radio type data")
        else:
            raise RuntimeError(output[0])

        output = send_at_com("AT#RFSTS", "OK")
        if output[2] == 0:
            data = parse_output(output, "RFSTS:", "\n").split(",")

            for key in self.rfsts_response_map:
                if key.find(radio_type) != -1:
                    temp = self.rfsts_response_map.get(key, {})

            for key in temp:
                if key == "mcc-mnc":
                    try:
                        mcc = int(data[temp[key]].replace('"','').split(" ")[0])
                        mnc = int(data[temp[key]].replace('"','').split(" ")[1])
                        self.geolocation["mcc"] = mcc
                        self.geolocation["mnc"] = mnc
                    except:
                        raise ValueError("read_geoloc_data --> error occured parsing rfsts data")
                else:
                    self.geolocation[key] = data[temp[key]].replace('"','')
        else:
            raise RuntimeError(output[0])

        output = send_at_com("AT#SERVINFO", "OK")
        if output[2] == 0:
            data = parse_output(output, "SERVINFO:", "\n").split(",")

            for key in self.servinfo_response_map:
                if key.find(radio_type) != -1:
                    temp = self.servinfo_response_map.get(key, {})

            for key in temp:
                self.geolocation[key] = data[temp[key]].replace('"','')
        else:
            raise RuntimeError(output[0])

        # hex/int conversation
        try:
            for key in self.geolocation:
                if key in ["tac", "lac", "psc", "cid"]:
                    self.geolocation[key] = int(self.geolocation[key], 16)
        except:
            raise ValueError("read_geoloc_data --> error occured converting hex to int")

        if self.geolocation != old_geolocation:
            self.geolocation["last_update"] == int(time.time())


# Module Classes
class LE910CXThreadX(Telit):
    ecm_mode_setter_command = "AT#USBCFG=1"
    ecm_mode_response = "1"


class ME910C1WW(Telit):
    ecm_mode_setter_command = "AT#USBCFG=3"
    ecm_mode_response = "3"
