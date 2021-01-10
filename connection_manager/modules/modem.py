from helpers.logger import initialize_logger
from helpers.serial import shell_command, send_at_com
from helpers.config import *
from helpers.exceptions import *
import time

PING_TIMEOUT = 9

config = read_yaml_all(CONFIG_PATH)
system_info = read_yaml_all(SYSTEM_PATH)

DEBUG = config.get("debug_mode", False)
APN = config.get("apn", "super")

logger = initialize_logger(DEBUG)

class ModemSetup(object):
    # main properties
    vendor = ""
    model = ""
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

    def __init__(self, vendor, model, imei, ccid, sw_version):
        self.vendor = vendor
        self.model = model
        self.imei = imei
        self.ccid = ccid
        self.sw_version = sw_version

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
    
modem_setup = ModemSetup(
    vendor = system_info.get("modem_vendor", "Quectel"),
    model = "EC25",
    imei = system_info.get("imei", ""),
    ccid = system_info.get("ccid", ""),
    sw_version = system_info.get("sw_version", ""),
)

# attrs = vars(modem_setup)
# print('\n'.join("%s: %s" % item for item in attrs.items()))
# exit()


def initiate_ecm():
    global modem_setup

    logger.info("ECM Connection is initiating...")
    output = send_at_com(modem_setup.pdp_activate_command,"OK")
        
    if output[2] == 0:
        logger.info("ECM Connection is initiated.")
    else:
        raise PDPContextFailed("ECM initiation failed!")

def check_internet():
    global modem_setup

    output = shell_command("ping -q -c 1 -s 0 -w "  + str(PING_TIMEOUT) + " -I " + modem_setup.interface_name + " 8.8.8.8")
    #print(output)

    if output[2] == 0:
        return 0
    else:
        raise NoInternet("no internet")

def diagnose():
    global modem_setup

    con_interface = True
    usb_interface = True
    modem_reachable = True
    usb_driver = True
    modem_driver = True
    pdp_context = True
    network_reqister = True
    sim_ready = True
    modem_mode = True
    modem_apn = True

    logger.info("Diagnostic is working...")
    
    # 1 - Is connection interface exist?
    logger.info("[1] : Is connection interface exist?")

    output = shell_command("route -n")
    if output[2] == 0:
        if output[0].find(modem_setup.interface_name) != -1:
            con_interface = True
        else: 
            con_interface = False
    else:
        raise RuntimeError("Error occured processing shell command!")
    
    # 2 - Is USB interface exist?
    logger.info("[2] : Is USB interface exist?")

    output = shell_command("lsusb")
    if output[2] == 0:
        if output[0].find(modem_setup.vendor) != -1:
            usb_interface = True
        else: 
            usb_interface = False
    else:
        raise RuntimeError("Error occured processing shell command!")

    # 3 - Is modem reachable?
    logger.info("[3] : Is modem reachable?")
    
    output = send_at_com("AT", "OK")
    if output[2] == 0:
        modem_reachable = True
    else:
        modem_reachable = False

    # 3 - Is ECM PDP Context is active?
    logger.info("[4] : Is ECM PDP Context is active?")
    
    output = send_at_com(modem_setup.pdp_status_command, "1,1")
    if output[2] == 0:
        pdp_context = True
    else:
        pdp_context = False
    
    diagnostic = {
        "con_interface" : con_interface,
        "usb_interface" : usb_interface,
        "modem_reachable" : modem_reachable,
        "pdp_context" : pdp_context,
    }

    print(diagnostic)

def reconnect():
    global modem_setup

    logger.info("Modem restarting...")
    
    output = send_at_com(modem_setup.reboot_command, "OK")
    if output[2] == 0:
        time.sleep(20)
    else:
        raise ModemNotReachable("Reboot message couldn't be reach to modem!")

    # Check modem is started!
    for i in range(120):
        output = shell_command("route -n")   
        if output[0].find(modem_setup.interface_name) != -1:
            logger.info("Modem started.")
            time.sleep(5)
            break
        else:
            time.sleep(1)
            print("*", end="", flush=True)  # debug
        
        raise ModemNotFound("Modem couldn't be started after reboot!")

def _configure_apn():
    output = send_at_com("AT+CGDCONT?", APN)

    if( output[2] == 0 ):
        logger.info("APN is up-to-date.") 
    else:
        output = send_at_com("AT+CGDCONT=1,\"IPV4V6\",\"" + APN + "\"","OK")

        if(output[2] == 0):
            logger.info("APN is updated succesfully : " + APN)
        else:
            raise ModemNotReachable("APN couldn't be set successfully!")

def detect_modem():
    global modem_setup

    output = shell_command("lsusb")
    if output[2] == 0:
        if output[0].find(modem_setup.vendor) != -1:
            return modem_setup.vendor
        else:
            raise ModemNotFound("Modem couldn't be detected!")
    else:
        raise ModemNotFound("Modem couldn't be detected!")
        
def configure_modem():
    global modem_setup

    logger.info("Modem configuration started.")

    try:
        _configure_apn()
    except Exception as e:
        raise e

    output = send_at_com(modem_setup.mode_status_command, modem_setup.ecm_mode_response)

    if output[2] != 0:
        output = send_at_com(modem_setup.ecm_mode_setter_command, "OK")
           
        if output[2] == 0:
            logger.info("ECM mode is activated.")
            logger.info("The modem is rebooting to apply changes...")
        else:
            raise ModemNotReachable(output[0])

        time.sleep(20)

        output = shell_command("route -n")

        if output[0].find(modem_setup.interface_name):
            logger.info("Modem started.")
        else:
            output = send_at_com(modem_setup.reboot_command, "OK")
            time.sleep(20)

            # Check modem is started!
            for i in range(120):
                output = shell_command("route -n")     
                if output[0].find(modem_setup.reboot_command):
                    logger.info("Modem started.")
                    break
                else:
                    time.sleep(1)
                    print("*", end="", flush=True)
            
            time.sleep(5)

def check_network():
    
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





