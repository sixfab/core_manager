import time
import usb.core

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import shell_command, send_at_com
from helpers.yamlio import write_yaml_all, DIAG_FOLDER_PATH
from helpers.exceptions import *
from helpers.sbc_support import supported_sbcs


class BaseModule:
    """
    Base module class that contains default parameters
    """
    # Module Identification variables
    vendor_name = "default"
    vid = "ffff"
    product_name = "default"
    pid = "ffff"
    imei = ""
    iccid = ""
    sw_version = ""

    # Module spesific parameters
    interface_name = ""
    mode_status_command = ""
    ecm_mode_response = ""
    ecm_mode_setter_command = ""
    reboot_command = ""
    pdp_activate_command = ""
    pdp_status_command = ""
    ccid_command = ""
    eps_mode_status_command = ""
    eps_mode_setter_command = ""
    eps_data_centric_response = ""

    # Module runtime memory
    incident_flag = False

    monitor = {
        "cellular_connection": None,
        "cellular_latency": None,
        "fixed_incident": 0,
    }

    diagnostic = {
        "con_interface": True,
        "modem_reachable": True,
        "usb_driver": True,
        "modem_driver": True,
        "pdp_context": True,
        "network_reqister": True,
        "sim_ready": True,
        "modem_mode": True,
        "modem_apn": True,
    }

    geolocation = {}


    def __init__(self, module_name="default", pid="ffff"):
        self.module_name = module_name
        self.pid = pid


    def detect_modem(self):
        output = shell_command("lsusb")
        if output[2] == 0:
            if output[0].find(self.vid) != -1:
                return self.vid
            else:
                raise ModemNotFound("Modem couldn't be detected!")
        else:
            raise ModemNotFound("Modem couldn't be detected!")

    def configure_apn(self):
        apn_with_quotes = '"%s"' % conf.apn
        output = send_at_com("AT+CGDCONT?", apn_with_quotes)

        if output[2] == 0:
            logger.info("APN is up-to-date.")
        else:
            output = send_at_com(f'AT+CGDCONT=1,"IPV4V6","{conf.apn}"', "OK")

            if output[2] == 0:
                logger.info("APN is updated succesfully : %s", conf.apn)
            else:
                raise ModemNotReachable("APN couldn't be set successfully!")

    def configure_modem(self):
        force_reset = 0
        logger.info("Modem configuration started.")

        try:
            self.configure_apn()
        except Exception as error:
            raise error

        try:
            self.set_modem_eps_data_centric()
        except Exception as error:
            raise error

        logger.info("Checking the mode of modem...")
        output = send_at_com(self.mode_status_command, self.ecm_mode_response)

        if output[2] != 0:
            logger.info("Modem mode is not set. ECM mode will be activated soon.")
            output = send_at_com(self.ecm_mode_setter_command, "OK")

            if output[2] == 0:
                logger.info("ECM mode is activating...")
                logger.info("The modem will reboot to apply changes.")
            else:
                raise ModemNotReachable("Error occured while setting mode configuration!")

            try:
                self.wait_until_modem_turned_off()
            except Exception as error:
                logger.warning("wait_until_modem_turned_off() -> %s", error)
                force_reset = 1
            else:
                try:
                    self.wait_until_modem_started()
                except Exception as error:
                    logger.warning("wait_until_modem_started() -> %s", error)
                    force_reset = 2

            if force_reset == 1:
                force_reset = 0
                try:
                    self.reset_modem_softly()
                except Exception as error:
                    raise error

            elif force_reset == 2:
                force_reset = 0
                try:
                    self.reset_modem_hardly()
                except Exception as error:
                    raise error

            logger.info("Re-checking the mode of modem...")
            output = send_at_com(self.mode_status_command, self.ecm_mode_response)

            if output[2] != 0:
                logger.error("Activation of ECM mode is failed!")
                raise RuntimeError
            else:
                logger.info("ECM mode activation is successful.")

    def check_sim_ready(self):
        logger.info("Checking the SIM is ready...")

        output = send_at_com("AT+CPIN?", "CPIN: READY")
        if output[2] == 0:
            logger.info("SIM is ready.")
        else:
            logger.error(output[0])
            raise SIMNotReady(output[0])

    def check_network(self):
        logger.info("Checking the network is ready...")

        output = send_at_com("AT+CREG?", "OK")
        if output[2] == 0:
            if output[0].find("+CREG: 0,1") != -1 or output[0].find("+CREG: 0,5") != -1:
                logger.info("Network is registered")
            else:
                logger.error("Network not registered: %s", output)
                raise NetworkRegFailed(output[0])
        else:
            logger.error(output[0])
            raise NetworkRegFailed(output[0])

    def initiate_ecm(self):
        logger.info("Checking the ECM initialization...")
        output = send_at_com(self.pdp_status_command, "OK")
        if output[2] == 0:
            if output[0].find("0,1") != -1 or output[0].find("1,1") != -1:
                logger.info("ECM is already initiated.")
                time.sleep(10)
                return 0

        logger.info("ECM Connection is initiating...")
        output = send_at_com(self.pdp_activate_command, "OK")

        if output[2] == 0:
            for _ in range(2):
                output = send_at_com(self.pdp_status_command, "OK")

                if output[2] == 0:
                    if output[0].find("0,1") != -1 or output[0].find("1,1") != -1:
                        logger.info("ECM is initiated.")
                        time.sleep(10)
                        return 0
                    else:
                        time.sleep(5)
                else:
                    time.sleep(2)

            raise PDPContextFailed("ECM initiation timeout!")
        else:
            raise PDPContextFailed("ECM initiation failed!")

    def check_interface_health(self, interface, timeout):
        output = shell_command(f"ping -q -c 1 -s 8 -w {timeout} -I {interface} 8.8.8.8")

        if output[2] != 0:
            raise NoInternet("No internet!")

    def check_internet(self):
        try:
            self.check_interface_health(self.interface_name, conf.ping_timeout)
        except Exception as error:
            self.monitor["cellular_connection"] = False
            raise NoInternet("No internet!") from error
        else:
            self.monitor["cellular_connection"] = True

    def diagnose(self, diag_type=0):

        self.diagnostic = {
            "con_interface": "",
            "modem_reachable": "",
            "usb_driver": "",
            "pdp_context": "",
            "network_reqister": "",
            "sim_ready": "",
            "modem_mode": "",
            "modem_apn": "",
            "timestamp": "",
        }

        logger.info("Diagnostic is working...")

        # 1 - Is connection interface exist?
        logger.debug("[1] : Is connection interface exist?")

        output = shell_command("route -n")
        if output[2] == 0:
            if output[0].find(self.interface_name) != -1:
                self.diagnostic["con_interface"] = True
            else:
                self.diagnostic["con_interface"] = False
        else:
            raise RuntimeError("Error occured processing shell command!")

        # 2 - Is USB interface exist?
        logger.debug("[2] : Is USB interface exist?")

        output = shell_command("lsusb")
        if output[2] == 0:
            if output[0].find(self.vid) != -1:
                self.diagnostic["usb_interface"] = True
            else:
                self.diagnostic["usb_interface"] = False
        else:
            raise RuntimeError("Error occured processing shell command!")

        # 3 - Is USB driver exist?
        logger.debug("[3] : Is USB driver exist?")

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

        # 4 - Is modem reachable?
        logger.debug("[4] : Is modem reachable?")

        output = send_at_com("AT", "OK")
        if output[2] == 0:
            self.diagnostic["modem_reachable"] = True
        else:
            self.diagnostic["modem_reachable"] = False

        # 5 - Is ECM PDP Context active?
        logger.debug("[5] : Is ECM PDP Context is active?")

        output = send_at_com(self.pdp_status_command, "1,1")
        if output[2] == 0:
            self.diagnostic["pdp_context"] = True
        else:
            self.diagnostic["pdp_context"] = False

        # 6 - Is the network registered?
        logger.debug("[6] : Is the network is registered?")

        try:
            self.check_network()
        except:
            self.diagnostic["network_reqister"] = False
        else:
            self.diagnostic["network_reqister"] = True

        # 7 - Is the APN OK?
        logger.debug("[7] : Is the APN is OK?")

        apn_with_quotes = '"%s"' % conf.apn
        output = send_at_com("AT+CGDCONT?", apn_with_quotes)
        if output[2] == 0:
            self.diagnostic["modem_apn"] = True
        else:
            self.diagnostic["modem_apn"] = False

        # 8 - Is the modem mode OK?
        logger.debug("[8] : Is the modem mode OK?")

        output = send_at_com(self.mode_status_command, self.ecm_mode_response)
        if output[2] == 0:
            self.diagnostic["modem_mode"] = True
        else:
            self.diagnostic["modem_mode"] = False

        # 9 - Is the SIM ready?
        logger.debug("[9] : Is the SIM ready?")

        output = send_at_com("AT+CPIN?", "READY")
        if output[2] == 0:
            self.diagnostic["sim_ready"] = True
        else:
            self.diagnostic["sim_ready"] = False

        timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
        self.diagnostic["timestamp"] = timestamp

        if diag_type == 0:
            diag_file_name = "cm-diag_" + str(timestamp) + ".yaml"
            diag_file_path = DIAG_FOLDER_PATH + diag_file_name
            logger.info("Creating diagnostic report on --> %s", diag_file_path)
            write_yaml_all(diag_file_path, self.diagnostic)
        else:
            diag_file_name = "cm-diag-repeated.yaml"
            diag_file_path = DIAG_FOLDER_PATH + diag_file_name
            logger.info("Creating diagnostic report on --> %s", diag_file_path)
            write_yaml_all(diag_file_path, self.diagnostic)

        if conf.debug_mode and conf.verbose_mode:
            print("")
            print("********************************************************************")
            print("[?] DIAGNOSTIC REPORT")
            print("---------------------")
            for item in self.diagnostic.items():
                print(f"[+] {item[0]} --> {item[1]}")
            print("********************************************************************")
            print("")

    def reset_connection_interface(self):
        down_command = f"sudo ifconfig {self.interface_name} down"
        up_command = f"sudo ifconfig {self.interface_name} up"

        logger.info("Connection interface is reset...")

        output = shell_command(down_command)
        if output[2] == 0:
            logger.info("Interface %s is down.", self.interface_name)
        else:
            raise RuntimeError("Error occured while interface getting down!")

        time.sleep(5)

        output = shell_command(up_command)
        if output[2] == 0:
            logger.info("Interface %s is up.", self.interface_name)
        else:
            raise RuntimeError("Error occured while interface getting up!")

        try:
            self.wait_until_modem_interface_up()
        except Exception as error:
            raise error

    def reset_usb_interface(self):
        logger.info("USB interface is reset...")

        vendor_id = self.vid
        product_id = self.pid

        vendor_id_int = int(vendor_id, 16)
        product_id_int = int(product_id, 16)

        try:
            dev = usb.core.find(idVendor=vendor_id_int, idProduct=product_id_int)
            dev.reset()
        except Exception as error:
            raise error

    def wait_until_modem_turned_off(self):
        counter = 0
        for _ in range(20):
            output = shell_command("lsusb")
            if output[0].find(self.vid) != -1:
                time.sleep(1)
                counter += 1
            else:
                logger.debug("Modem turned off.")
                counter = 0
                return 0
        raise RuntimeError("Modem didn't turn off as expected!")

    def wait_until_modem_started(self):
        result = 0
        counter = 0
        # Check modem USB interface
        for _ in range(120):
            output = shell_command("lsusb")
            if output[0].find(self.vid) != -1:
                logger.debug("Modem USB interface detected.")
                counter = 0
                result += 1
                break
            else:
                time.sleep(1)
                counter += 1

        # Check modem AT FW
        for _ in range(10):
            output = send_at_com("AT", "OK")
            if output[2] == 0:
                logger.debug("Modem AT FW is working.")
                counter = 0
                result += 1
                break
            else:
                time.sleep(1)
                counter += 1

        if result != 2:
            raise ModemNotFound("Modem couldn't be started!")

    def wait_until_modem_interface_up(self):
        counter = 0
        logger.debug("Interface Name: %s", self.interface_name)
        # Check modem connection interface
        for _ in range(20):
            output = shell_command("route -n")
            if output[0].find(self.interface_name) != -1:
                logger.info("Modem interface is detected.")
                counter = 0
                break
            else:
                time.sleep(1)
                counter += 1

        if counter != 0:
            raise ModemNotFound("Modem interface couln't be detected.")

    def reset_modem_softly(self):
        logger.info("Modem is resetting softly...")
        output = send_at_com(self.reboot_command, "OK")
        if output[2] == 0:
            try:
                self.wait_until_modem_turned_off()
                self.wait_until_modem_started()
            except Exception as error:
                raise error
        else:
            raise RuntimeError("Reboot command couldn't be reach to the modem!")

    def reset_modem_hardly(self):
        logger.info("Modem is resetting via hardware...")

        sbc = supported_sbcs.get(conf.sbc)
        sbc.modem_power_disable()
        time.sleep(2)
        sbc.modem_power_enable()

    def get_significant_data(self, output, header):
        header += " "
        header_size = len(header)
        index_of_data = output[0].find(header) + header_size
        end_of_data = index_of_data + output[0][index_of_data:].find("\n")
        sig_data = output[0][index_of_data:end_of_data].replace('"', "").split(",")
        return sig_data

    def get_roaming_operator(self):
        output = send_at_com("AT+COPS?", "OK")
        if output[2] == 0:
            data = self.get_significant_data(output, "+COPS:")

            try:
                operator = data[2]
            except:
                operator = None
            else:
                operator = operator.replace("Twilio", "")
                operator = operator.replace("twilio", "")
                return operator
        else:
            raise RuntimeError('Error occured on --> get_roaming_operator')

    def get_signal_quality(self):
        sq_lables = {
            "poor" : range(0,7),
            "fair" : range(7,12),
            "good" : range(12,20),
            "excellent": range(20,33)
        }

        output = send_at_com("AT+CSQ", "OK")
        if output[2] == 0:
            data = self.get_significant_data(output, "+CSQ:")

            try:
                signal_quality = int(data[0])
            except:
                signal_quality = None
            else:
                for key, value in sq_lables.items():
                    if signal_quality in value:
                        signal_quality = key
                        break
                else:
                    signal_quality = "unknown"
                return signal_quality
        else:
            raise RuntimeError('Error occured on --> get_signal_quality')

    def get_active_lte_tech(self):
        techs = {
            "0": "GSM",
            "2": "UTRAN",
            "3": "GSM W/EGPRS",
            "4": "UTRAN W/HSDPA",
            "5": "UTRAN W/HSUPA",
            "6": "UTRAN W/HSDPA and HSUPA",
            "7": "E-UTRAN",
            "8": "CAT-M1",
            "9": "CAT-NB1",
        }

        output = send_at_com("AT+COPS?", "OK")

        if output[2] == 0:
            data = self.get_significant_data(output, "+COPS:")

            try:
                tech_id = data[3]
            except:
                return None
            else:
                return techs.get(tech_id, "Unknown")
        else:
            raise RuntimeError('Error occured on --> get_active_lte_tech')

    def get_fixed_incident_count(self):
        count = self.monitor.get("fixed_incident", 0)
        return count

    def get_apn(self):
        return conf.apn

    def set_modem_eps_data_centric(self):
        output = send_at_com(self.eps_mode_status_command, self.eps_data_centric_response)

        if output[2] == 0:
            logger.info("Modem mode for EPS is OK")
        else:
            output = send_at_com(self.eps_mode_setter_command, "OK")

            if output[2] == 0:
                logger.info("Modem mode for EPS updated succesfully")
            else:
                raise ModemNotReachable("Modem mode for EPS couldn't be set successfully!")

    def read_geoloc_data(self):
        """
        Reads required data from modem in order to use at geolocation API
        """
        # Overrite it on module classes
