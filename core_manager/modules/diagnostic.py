import time

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import send_at_com, shell_command
from helpers.yamlio import write_yaml_all, DIAG_FOLDER_PATH

class Diagnostic:
    diagnostic = {}
    diagnostic_zip = 0
    diagnostic_map = {
        "modem_reachable" : 0,
        "modem_apn": 1,
        "modem_mode": 2,
        "sim_ready": 3,
        "network_reqister": 4,
        "pdp_context": 5,
        "usb_driver": 6,
        "con_interface": 7,
        "usb_interface": 8
    }

    def __init__(self, modem):
        self.modem = modem

    def diagnose(self, diag_type=0):
        logger.info("Diagnostic is working...")
        self.diag_modem_reachable()
        self.diag_apn_set()
        self.diag_modem_mode()
        self.diag_sim_ready()
        self.diag_network_register()
        self.diag_ecm_pdp_context()
        self.diag_usb_driver()
        self.diag_connection_interface()
        self.diag_usb_interface()

        for key, value in self.diagnostic.items(): # little endian
            if value is True:
                self.diagnostic_zip |= (1 << self.diagnostic_map[key])
            elif value is False:
                self.diagnostic_zip &= ~(1 << self.diagnostic_map[key])

        timestamp = int(time.time())
        self.diagnostic["timestamp"] = timestamp

        diag = {
            "last_update": timestamp,
            "value": self.diagnostic_zip
        }

        if diag_type == 0:
            diag_file_name = "diagnostic.yaml"
            diag_file_path = DIAG_FOLDER_PATH + diag_file_name
            logger.info("Creating diagnostic report on --> %s", diag_file_path)
            write_yaml_all(diag_file_path, diag)
        else:
            diag_file_name = "diagnostic-repeated.yaml"
            diag_file_path = DIAG_FOLDER_PATH + diag_file_name
            logger.info("Creating diagnostic report on --> %s", diag_file_path)
            write_yaml_all(diag_file_path, diag)

        if conf.debug_mode and conf.verbose_mode:
            print("")
            print("********************************************************************")
            print("[?] DIAGNOSTIC REPORT")
            print("---------------------")
            for item in self.diagnostic.items():
                print(f"[+] {item[0]} --> {item[1]}")
            print("********************************************************************")
            print("")

    def diag_connection_interface(self):
        logger.debug("[-] : Is connection interface exist?")

        output = shell_command("route -n")
        if output[2] == 0:
            if output[0].find(self.modem.interface_name) != -1:
                self.diagnostic["con_interface"] = True
            else:
                self.diagnostic["con_interface"] = False
        else:
            raise RuntimeError("Error occured processing shell command!")

    def diag_usb_interface(self):
        logger.debug("[-] : Is USB interface exist?")

        output = shell_command("lsusb")

        if output[2] == 0:
            if output[0].find(self.modem.vid) != -1:
                self.diagnostic["usb_interface"] = True
            else:
                self.diagnostic["usb_interface"] = False
        else:
            raise RuntimeError("Error occured processing shell command!")

    def diag_usb_driver(self):
        logger.debug("[-] : Is USB driver exist?")

        output = shell_command("usb-devices")
        if output[2] == 0:
            if output[0].find("cdc_ether") != -1:
                if output[0].count("cdc_ether") >= 2:
                    self.diagnostic["usb_driver"] = True
                else:
                    self.diagnostic["usb_driver"] = False
            else:
                self.diagnostic["usb_driver"] = False
        else:
            raise RuntimeError("Error occured processing shell command!")

    def diag_modem_reachable(self):
        logger.debug("[-] : Is modem reachable?")

        output = send_at_com("AT", "OK")
        if output[2] == 0:
            self.diagnostic["modem_reachable"] = True
        else:
            self.diagnostic["modem_reachable"] = False

    def diag_ecm_pdp_context(self):
        logger.debug("[-] : Is ECM PDP Context is active?")

        output = send_at_com(self.modem.pdp_status_command, self.modem.desired_pdp_status)
        if output[2] == 0:
            self.diagnostic["pdp_context"] = True
        else:
            self.diagnostic["pdp_context"] = False

    def diag_network_register(self):
        logger.debug("[-] : Is the network is registered?")

        try:
            self.modem.check_network()
        except:
            self.diagnostic["network_reqister"] = False
        else:
            self.diagnostic["network_reqister"] = True

    def diag_apn_set(self):
        logger.debug("[-] : Is the APN is OK?")

        apn_with_quotes = '"%s"' % conf.apn
        output = send_at_com("AT+CGDCONT?", apn_with_quotes)
        if output[2] == 0:
            self.diagnostic["modem_apn"] = True
        else:
            self.diagnostic["modem_apn"] = False

    def diag_modem_mode(self):
        logger.debug("[-] : Is the modem mode OK?")

        output = send_at_com(self.modem.mode_status_command, self.modem.ecm_mode_response)
        if output[2] == 0:
            self.diagnostic["modem_mode"] = True
        else:
            self.diagnostic["modem_mode"] = False

    def diag_sim_ready(self):
        logger.debug("[-] : Is the SIM ready?")

        output = send_at_com("AT+CPIN?", "READY")
        if output[2] == 0:
            self.diagnostic["sim_ready"] = True
        else:
            self.diagnostic["sim_ready"] = False
