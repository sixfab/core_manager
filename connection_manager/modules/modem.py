#!/usr/bin/python3

import time
from usb.core import find as finddev

from helpers.logger import initialize_logger
from helpers.commander import shell_command, send_at_com
from helpers.yamlio import *
from helpers.exceptions import *
from helpers.config_parser import *

BASE_HAT_DISABLE_PIN = 26 # For raspberry pi

class Modem(object):
    # main properties
    vendor = ""
    vendor_id = ""
    model = ""
    product_id = ""
    imei = ""
    ccid = ""
    sw_version = ""

    # additional properties
    interface_name = ""
    mode_status_command = ""
    ecm_mode_response = ""
    ecm_mode_setter_command = ""
    reboot_command = ""
    pdp_activate_command = ""
    pdp_status_command = ""

    diagnostic = {
            "con_interface" : True,
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

    def __init__(self, vendor, model, imei, ccid, sw_version, vendor_id, product_id):
        self.vendor = vendor
        self.model = model
        self.imei = imei
        self.ccid = ccid
        self.sw_version = sw_version
        self.vendor_id = vendor_id
        self.product_id = product_id

        if vendor == "Quectel":
            self.interface_name = "usb0"
            self.mode_status_command = "AT+QCFG=\"usbnet\""
            self.ecm_mode_response = "\"usbnet\",1"
            self.ecm_mode_setter_command = "AT+QCFG=\"usbnet\",1"
            self.reboot_command = "AT+CFUN=1,1"
            self.pdp_activate_command = "AT"
            self.pdp_status_command = "AT+CGACT?"
        
        elif vendor == "Telit":
            self.interface_name = "wwan0"
            self.mode_status_command = "AT#USBCFG?"
            self.ecm_mode_response = "4"
            self.ecm_mode_setter_command = "AT#USBCFG=4"
            self.reboot_command = "AT#REBOOT"
            self.pdp_activate_command = "AT#ECM=1,0,\"\",\"\",0"
            self.pdp_status_command = "AT#ECM?"
    

    def update(self, vendor, model, imei, ccid, sw_version, vendor_id, product_id):
        self.__init__(vendor, model, imei, ccid, sw_version, vendor_id, product_id)


    def detect_modem(self):
        output = shell_command("lsusb")
        if output[2] == 0:
            if output[0].find(self.vendor) != -1:
                return self.vendor
            else:
                raise ModemNotFound("Modem couldn't be detected!")
        else:
            raise ModemNotFound("Modem couldn't be detected!")


    def configure_apn(self):
        output = send_at_com("AT+CGDCONT?", APN)

        if( output[2] == 0 ):
            logger.info("APN is up-to-date.") 
        else:
            output = send_at_com("AT+CGDCONT=1,\"IPV4V6\",\"" + APN + "\"","OK")

            if(output[2] == 0):
                logger.info("APN is updated succesfully : " + APN)
            else:
                raise ModemNotReachable("APN couldn't be set successfully!")


    def configure_modem(self):
        force_reset = 0
        logger.info("Modem configuration started.")

        try:
            self.configure_apn()
        except Exception as e:
            raise e

        output = send_at_com(self.mode_status_command, self.ecm_mode_response)

        if output[2] != 0:
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
                logger.warning(str(e))
                force_reset = 1
            
            if force_reset == 1:
                force_reset = 0
                try:
                    self.reset_modem_softly()
                except Exception as e:
                    raise e
            

    def check_network(self):
        
        sim_ready = 0
        network_reg = 0
        network_ready = 0

        # Check the network is ready
        logger.info("Checking the network is ready...")

        # SIM
        output = send_at_com("AT+CPIN?", "CPIN: READY")
        if output[2] == 0:
            logger.info("SIM is ready.")
            sim_ready = 1
        else:
            logger.error(output[0])
            raise SIMNotReady(output[0])

        # Network Registeration
        output = send_at_com("AT+CREG?", "OK")
        if (output[2] == 0):
            if(output[0].find("+CREG: 0,1") or output[0].find("+CREG: 0,5")):
                logger.info("Network is registered.")
                network_reg = 1
            else:
                logger.error(output[0])
                raise NetworkRegFailed(output[0])
        else:
            logger.error(output[0])
            raise NetworkRegFailed(output[0])


    def initiate_ecm(self):
        output = send_at_com(self.pdp_status_command, "1,1")
        if output[2] == 0:
           logger.info("ECM is already initiated.")
           time.sleep(10)
           return 0

        logger.info("ECM Connection is initiating...")
        output = send_at_com(self.pdp_activate_command,"OK")
            
        if output[2] == 0:
            for i in range(60):
                output = send_at_com(self.pdp_status_command, "1,1")

                if output[2] == 0:
                    logger.info("ECM Connection is initiated.")
                    time.sleep(5)
                    return 0
                else:
                    time.sleep(1)
            
            raise PDPContextFailed("ECM initiation timeout!")       
        else:
            raise PDPContextFailed("ECM initiation failed!")


    def check_internet(self):

        output = shell_command("ping -q -c 1 -s 0 -w "  + str(PING_TIMEOUT) + " -I " + self.interface_name + " 8.8.8.8")
        #print(output)

        if output[2] == 0:
            return 0
        else:
            raise NoInternet("No internet!")


    def diagnose(self):
        
        self.diagnostic = {
            "con_interface" : True,
            "con_interface" : True,
            "modem_reachable" : True,
            "usb_driver" : True,
            "pdp_context" : True,
            "network_reqister" : True,
            "sim_ready" : True,
            "modem_mode" : True,
            "modem_apn" : True,
            "kernel_ver" : "",
            "modem_fw_ver" : "",
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
            if output[0].find(self.vendor) != -1:
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
                self.diagnostic["usb_driver"] = True
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
        except Exception as e:
            self.diagnostic["network_reqister"] = False
        else:
            self.diagnostic["network_reqister"] = True

        # 7 - Is the APN OK?
        logger.debug("[7] : Is the APN is OK?")
        
        output = send_at_com("AT+CGDCONT?", APN)
        if output[2] == 0:
            modem_apn = True
        else:
            modem_apn = False
        
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
        diag_file_name = "cm-diag_" + str(timestamp) + ".yaml"
        diag_file_path = DIAG_FOLDER_PATH + diag_file_name
        logger.info("Creating diagnostic report on --> " + str(diag_file_path))
        write_yaml_all(diag_file_path, self.diagnostic)

        if DEBUG == True and VERBOSE_MODE == True:
            print("")
            print("********************************************************************")
            print("[?] DIAGNOSTIC REPORT")
            print("---------------------")
            for x in self.diagnostic.items():
                print(str("[+] " + x[0]) + " --> " + str(x[1]))
            print("********************************************************************")
            print("")


    def reconnect(self):
        pass
       

    def reset_connection_interface(self):
        down = "sudo ifconfig " + str(self.interface_name) + " down"
        up = "sudo ifconfig " + str(self.interface_name) + " up"
        print(up)
        print(down)
        output = shell_command(down)
        print(output)
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
        vendor_id_int = int(self.vendor_id, 16)
        product_id_int = int(self.product_id, 16)

        try:
            dev = finddev(idVendor=vendor_id_int, idProduct=product_id_int)
            dev.reset()
        except Exception as e:
            raise e

        try:
            self.wait_until_modem_interface_up()
        except Exception as e:
            raise e


    def wait_until_modem_turned_off(self):
        counter = 0
        for i in range(20):
            output = shell_command("lsusb")   
            if output[0].find(self.vendor) != -1:
                time.sleep(1)
                counter += 1
                print(str(counter) + " - ", end="", flush=True)  # debug
            else:
                print() # debug
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
            if output[0].find(self.vendor) != -1:
                print() # debug
                logger.debug("Modem USB interface detected.")
                counter = 0
                result += 1
                break
            else:
                time.sleep(1)
                counter += 1
                print(str(counter) + " + ", end="", flush=True)  # debug

        # Check modem AT FW
        for i in range(10):
            output = send_at_com("AT", "OK")   
            if output[2] == 0:
                print() # debug
                logger.debug("Modem AT FW is working.")
                counter = 0
                result += 1
                break
            else:
                time.sleep(1)
                counter += 1
                print(str(counter) + " * ", end="", flush=True)  # debug

        # Check modem connection interface
        for i in range(20):
            output = shell_command("route -n")   
            if output[0].find(self.interface_name) != -1:
                print() # debug
                logger.info("Modem started.")
                counter = 0
                result += 1
                break
            else:
                time.sleep(1)
                counter += 1
                print(str(counter) + " : ", end="", flush=True)  # debug

        if result != 3:
            raise ModemNotFound("Modem couldn't be started!")


    def wait_until_modem_interface_up(self):
        counter = 0
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
                print(str(counter) + " : ", end="", flush=True)  # debug

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

        # Pin direction
        output = shell_command("gpio -g mode " + str(BASE_HAT_DISABLE_PIN) + " out")
        if output[2] == 0:
            pass
        else:
            raise RuntimeError("Error occured gpio command!")

        # Disable power
        output = shell_command("gpio -g write " + str(BASE_HAT_DISABLE_PIN) + " 1")
        if output[2] == 0:
            time.sleep(2)
        else:
            raise RuntimeError("Error occured gpio command!")

        # Enable power
        output = shell_command("gpio -g write " + str(BASE_HAT_DISABLE_PIN) + " 0")
        if output[2] == 0:
            time.sleep(2)
        else:
            raise RuntimeError("Error occured gpio command!")


    





        








