from helpers.modem_support.default import BaseModule
from helpers.logger import logger
from helpers.commander import send_at_com, parse_output


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
    desired_pdp_status = "1,1,1"
    ecm_mode_setter_command = 'AT^SSRVSET="actSrvSet",1'
    ecm_mode_response = "^SSRVSET: 1\n"
    ccid_command = "AT+CCID"
    eps_mode_status_command="AT+CEMODE?"
    eps_mode_setter_command="AT" # temporary workaround
    eps_data_centric_response="1" # temporary workaround

    # ^SMONI response map for different technologies
    smoni_response_map = {
        "lte": {
            "radio_type": 0,
            "mcc": 6,
            "mnc": 7,
            "tac": 8,
            "cid": 9,
            "psc": 10,
        },
        "wcdma": {
            "radio_type": 0,
            "mcc": 5,
            "mnc": 6,
            "lac": 7,
            "cid": 8,
            "psc": 2,
        },
        "gsm": {
            "radio_type": 0,
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
        radio_type_id = 0

        output = send_at_com("AT^SMONI", "OK")
        if output[2] == 0:
            data = parse_output(output, "^SMONI:", "\n").split(",")
            radio_type = data[radio_type_id].replace('"','').casefold()

            if radio_type == "4g":
                radio_type = "lte"
            elif radio_type == "3g":
                radio_type = "wcdma"
            elif radio_type == "2g":
                radio_type = "gsm"

            try:
                for key in self.smoni_response_map:
                    if key.find(radio_type) != -1:
                        temp = self.smoni_response_map.get(key, {})

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
                elif key == "radio_type":
                    self.geolocation[key] = radio_type
        except:
            raise ValueError("read_geoloc_data --> error occured converting hex to int")
        