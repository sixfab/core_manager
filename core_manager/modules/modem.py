#!/usr/bin/python3

from os import name
import time
import usb.core
import os.path

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import shell_command, send_at_com
from helpers.yamlio import read_yaml_all, write_yaml_all, DIAG_FOLDER_PATH, MONITOR_PATH
from helpers.exceptions import *
from helpers.sbc_support import supported_sbcs

old_monitor = {}
if os.path.isfile(MONITOR_PATH):
    try:
        old_monitor = read_yaml_all(MONITOR_PATH)
    except Exception as e:
        logger.warning("Old monitor data in monitor.yaml file couln't be read!")


def parse_output(output, header, end):
    header += " "
    header_size = len(header)
    index_of_data = output[0].find(header) + header_size
    end_of_data = index_of_data + output[0][index_of_data:].find(end)
    sig_data = output[0][index_of_data:end_of_data]
    return sig_data


class Modem(object):
    # main properties
    vendor = ""
    vendor_id = ""
    model = ""
    product_id = ""
    imei = ""
    iccid = ""
    sw_version = ""

    # monitoring properties
    monitor = {
        "cellular_connection" : None,
        "cellular_latency" : None,
        "fixed_incident": old_monitor.get("fixed_incident", 0),
    }

    # additional properties
    interface_name = ""
    mode_status_command = ""
    ecm_mode_response = ""
    ecm_mode_setter_command = ""
    reboot_command = ""
    pdp_activate_command = ""
    pdp_status_command = ""
    incident_flag = False

    diagnostic = {
        "con_interface" : True,
        "modem_reachable" : True,
        "usb_driver" : True,
        "modem_driver" : True,
        "pdp_context" : True,
        "network_reqister" : True,
        "sim_ready" : True,
        "modem_mode" : True,
        "modem_apn" : True,
    }


    def update(self, vendor, model, imei, iccid, sw_version, vendor_id, product_id):
        self.vendor = vendor
        self.model = model
        self.imei = imei
        self.iccid = iccid
        self.sw_version = sw_version
        self.vendor_id = vendor_id
        self.product_id = product_id

        if vendor == "Quectel":
            self.interface_name = "usb0"
            self.mode_status_command = "AT+QCFG=\"usbnet\""
            self.reboot_command = "AT+CFUN=1,1"
            self.pdp_activate_command = "AT"
            self.pdp_status_command = "AT+CGACT?"
            self.ecm_mode_setter_command = "AT+QCFG=\"usbnet\",1"
            self.ecm_mode_response = "\"usbnet\",1"

        elif vendor == "Telit":
            self.interface_name = "wwan0"
            self.mode_status_command = "AT#USBCFG?"
            self.reboot_command = "AT#REBOOT"
            self.pdp_activate_command = "AT#ECM=1,0"
            self.pdp_status_command = "AT#ECM?"

            if model == "ME910C1-WW":
                self.ecm_mode_setter_command = "AT#USBCFG=3"
                self.ecm_mode_response = "3"
            else:
                self.ecm_mode_setter_command = "AT#USBCFG=4"
                self.ecm_mode_response = "4"


    def detect_modem(self):
        output = shell_command("lsusb")
        if output[2] == 0:
            if output[0].find(self.vendor_id) != -1:
                return self.vendor_id
            else:
                raise ModemNotFound("Modem couldn't be detected!")
        else:
            raise ModemNotFound("Modem couldn't be detected!")


    def configure_apn(self):
        apn_with_quotes = '\"%s\"' % conf.apn
        output = send_at_com("AT+CGDCONT?", apn_with_quotes)

        if output[2] == 0:
            logger.info("APN is up-to-date.") 
        else:
            output = send_at_com("AT+CGDCONT=1,\"IPV4V6\",\"" + conf.apn + "\"","OK")

            if(output[2] == 0):
                logger.info("APN is updated succesfully : " + conf.apn)
            else:
                raise ModemNotReachable("APN couldn't be set successfully!")


    def configure_modem(self):
        force_reset = 0
        logger.info("Modem configuration started.")

        try:
            self.configure_apn()
        except Exception as e:
            raise e

        logger.info("Checking the mode of modem...")
        output = send_at_com(self.mode_status_command, self.ecm_mode_response)

        if output[2] != 0:
            logger.info("Modem mode is not set. ECM mode will be activated soon.")
            output = send_at_com(self.ecm_mode_setter_command, "OK")
            
            if output[2] == 0:
                logger.info("ECM mode is activated.")
                logger.info("The modem will reboot to apply changes.")
            else:
                raise ModemNotReachable("Error occured while setting mode configuration! " + output[0])

            try:
                time.sleep(20)
                self.wait_until_modem_started()
            except Exception as e:
                logger.warning("wait_until_modem_started() -> " + str(e))
                force_reset = 1
            
            if force_reset == 1:
                force_reset = 0
                try:
                    self.reset_modem_softly()
                except Exception as e:
                    raise e


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
        if (output[2] == 0):
            if(output[0].find("+CREG: 0,1") != -1 or output[0].find("+CREG: 0,5") != -1):
                logger.info("Network is registered.")
            else:
                logger.error(output[0])
                raise NetworkRegFailed(output[0])
        else:
            logger.error(output[0])
            raise NetworkRegFailed(output[0])


    def initiate_ecm(self):
        logger.info("Checking the ECM initialization...")
        output = send_at_com(self.pdp_status_command, "OK")
        if output[2] == 0:
            if(output[0].find("0,1") != -1 or output[0].find("1,1") != -1):
                logger.info("ECM is already initiated.")
                time.sleep(10)
                return 0
    
        logger.info("ECM Connection is initiating...")
        output = send_at_com(self.pdp_activate_command,"OK")
            
        if output[2] == 0:
            for i in range(2):
                output = send_at_com(self.pdp_status_command, "OK")

                if output[2] == 0:
                    if(output[0].find("0,1") != -1 or output[0].find("1,1") != -1):
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
        output = shell_command("ping -q -c 1 -s 8 -w "  + str(timeout) + " -I " + str(interface) + " 8.8.8.8")

        if output[2] == 0:
            pass
        else:
            raise NoInternet("No internet!")


    def check_internet(self):
        try:
            self.check_interface_health(self.interface_name, conf.ping_timeout)
        except:
            self.monitor["cellular_connection"] = False
            raise NoInternet("No internet!")
        else:
            self.monitor["cellular_connection"] = True
            

    def diagnose(self, diag_type=0):
        
        self.diagnostic = {
            "con_interface" : "",
            "modem_reachable" : "",
            "usb_driver" : "",
            "pdp_context" : "",
            "network_reqister" : "",
            "sim_ready" : "",
            "modem_mode" : "",
            "modem_apn" : "",
            "timestamp" : "",
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
            if output[0].find(self.vendor_id) != -1:
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
        
        apn_with_quotes = '\"%s\"' % conf.apn
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
            logger.info("Creating diagnostic report on --> " + str(diag_file_path))
            write_yaml_all(diag_file_path, self.diagnostic)
        else:
            diag_file_name = "cm-diag-repeated.yaml"
            diag_file_path = DIAG_FOLDER_PATH + diag_file_name
            logger.info("Creating diagnostic report on --> " + str(diag_file_path))
            write_yaml_all(diag_file_path, self.diagnostic)

        

        if conf.debug_mode == True and conf.verbose_mode == True:
            print("")
            print("********************************************************************")
            print("[?] DIAGNOSTIC REPORT")
            print("---------------------")
            for x in self.diagnostic.items():
                print(str("[+] " + x[0]) + " --> " + str(x[1]))
            print("********************************************************************")
            print("")


    def reset_connection_interface(self):
        down = "sudo ifconfig " + str(self.interface_name) + " down"
        up = "sudo ifconfig " + str(self.interface_name) + " up"

        logger.info("Connection interface is reset...")

        output = shell_command(down)
        if output[2] == 0:
           logger.info("Interface " + str(self.interface_name) + " is down.")
        else:
            raise RuntimeError("Error occured while interface getting down!")
        
        time.sleep(5)

        output = shell_command(up)
        if output[2] == 0:
           logger.info("Interface " + str(self.interface_name) + " is up.")
        else:
            raise RuntimeError("Error occured while interface getting up!")

        try:
            self.wait_until_modem_interface_up()
        except Exception as e:
            raise e


    def reset_usb_interface(self):
        logger.info("USB interface is reset...")
        
        vendor_id = self.vendor_id
        product_id = self.product_id

        vendor_id_int = int(vendor_id, 16)
        product_id_int = int(product_id, 16)

        try:
            dev = usb.core.find(idVendor=vendor_id_int, idProduct=product_id_int)
            dev.reset()
        except Exception as e:
            raise RuntimeError("Message: ", str(e))


    def wait_until_modem_turned_off(self):
        counter = 0
        for i in range(20):
            output = shell_command("lsusb")   
            if output[0].find(self.vendor_id) != -1:
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
        for i in range(120):
            output = shell_command("lsusb")   
            if output[0].find(self.vendor_id) != -1:
                logger.debug("Modem USB interface detected.")
                counter = 0
                result += 1
                break
            else:
                time.sleep(1)
                counter += 1

        # Check modem AT FW
        for i in range(10):
            output = send_at_com("AT", "OK")   
            if output[2] == 0:
                logger.debug("Modem AT FW is working.")
                counter = 0
                result += 1
                break
            else:
                time.sleep(1)
                counter += 1

        # Check modem connection interface
        for i in range(20):
            output = shell_command("route -n")   
            if output[0].find(self.interface_name) != -1:
                logger.info("Modem started.")
                counter = 0
                result += 1
                break
            else:
                time.sleep(1)
                counter += 1

        if result != 3:
            raise ModemNotFound("Modem couldn't be started!")


    def wait_until_modem_interface_up(self):
        counter = 0
        logger.debug("Interface Name: " + str(self.interface_name))
        # Check modem connection interface
        for i in range(20):
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
            except Exception as e:
                raise e
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
        sig_data = output[0][index_of_data:end_of_data].replace("\"", "").split(",")
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
                return operator
        else:
            raise RuntimeError("Error occured on \"AT+CSQ\" command!")


    def get_signal_quality(self):
        output = send_at_com("AT+CSQ", "OK")
        if output[2] == 0:
            data = self.get_significant_data(output, "+CSQ:")

            try:
                sq = int(data[0])
            except:
                sq = None
            else:
                return sq
        else:
            raise RuntimeError("Error occured on \"AT+CSQ\" command!")


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
            raise RuntimeError("Error occured on \"AT+CSQ\" command!")

    
    def get_fixed_incident_count(self):
        count = self.monitor.get("fixed_incident", 0)
        return count


    def get_apn(self):
        return conf.apn
