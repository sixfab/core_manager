from helpers.logger import initialize_logger
from helpers.serial import shell_command, send_at_com
from helpers.config import *
from helpers.exceptions import *
from modules.modem import check_network
import time

QUECTEL = "Quectel"
TELIT = "Telit"
PING_TIMEOUT = 9

config = read_yaml_all(CONFIG_PATH)
system_info = read_yaml_all(SYSTEM_PATH)


MODEM = system_info.get("modem_vendor", "Quectel")
DEBUG = config.get("debug_mode", False)
APN = config.get("apn", "super")
INTERFACE = "usb0" if MODEM == QUECTEL else "wwan0"

logger = initialize_logger(DEBUG)

def initiate_ecm():
    global MODEM

    if MODEM == QUECTEL:
        logger.info("ECM Connection is initiating automatically...")
    elif MODEM == TELIT:
        logger.info("ECM Connection is initiating...")

        output = send_at_com("AT#ECM=1,0,\"\",\"\",0","OK")
        
        if output[2] == 0:
            logger.info("ECM Connection is initiated.")
        else:
            logger.error("Message: " + output[0])
    else:
        logger.warning("Modem is unknown or unsupported!")

def check_internet():

    output = shell_command("ping -q -c 1 -s 0 -w "  + str(PING_TIMEOUT) + " -I " + INTERFACE + " 8.8.8.8")
    #print(output)

    if output[2] == 0:
        return 0
    else:
        raise NoInternet("no internet")

def diagnose():
    global MODEM

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
        if output[0].find(INTERFACE) != -1:
            con_interface = True
        else: 
            con_interface = False
    else:
        raise RuntimeError("Error occured processing shell command!")
    
    # 2 - Is USB interface exist?
    logger.info("[2] : Is USB interface exist?")

    output = shell_command("lsusb")
    if output[2] == 0:
        if output[0].find(MODEM) != -1:
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

    
    diagnostic = {
        "con_interface" : con_interface,
        "usb_interface" : usb_interface,
        "modem_reachable" : modem_reachable,
    }

    print(diagnostic)


def reconnect():
    global MODEM

    logger.info("Modem restarting...")
    if MODEM == QUECTEL:
        output = send_at_com("AT+CFUN=1,1", "OK")

        if output[2] == 0:
            time.sleep(20)
        else:
            logger.error("Message: " + output[0])

        # Check modem is started!
        for i in range(120):
            output = shell_command("route -n")   
            if output[0].find("usb0") != -1:
                logger.info("Modem started.")
                time.sleep(5)
                break
            else:
                time.sleep(1)
                print("*", end="", flush=True)  # debug

    elif MODEM == TELIT:
        logger.info("Telit doesn't supported yet!")
        return 1
    
    else:
        logger.info("Unknown or unspoorted modem!")
        return 2






