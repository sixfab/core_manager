from helpers.logger import initialize_logger
from helpers.serial import shell_command, send_at_com
from helpers.config import *
from helpers.exceptions import *
import time

config = read_yaml_all(CONFIG_PATH)
system_info = read_yaml_all(SYSTEM_PATH)

MODEM = system_info.get("modem_vendor", "modem_info")
DEBUG = config["debug_mode"]
APN = config["apn"]

logger = initialize_logger(DEBUG)

QUECTEL_ECM_MODE = "1"
TELIT_ECM_MODE = "4"

QUECTEL = "Quectel"
TELIT = "Telit"


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
       
    output = shell_command("lsusb")

    if output[2] == 0:
        if (output[0].find("Quectel") != -1):
            return "Quectel"
        elif(output[0].find("Telit") != -1):
            return "Telit"
    else:
        raise ModemNotFound("ModemNotFound: Modem couldn't be detected!")
        
def configure_modem():
    logger.info("Modem configuration started.")

    try:
        _configure_apn()
    except Exception as e:
        raise e

    # Modem Mode Configuration
    # ------------------------
    if MODEM == QUECTEL:
        output = send_at_com("AT+QCFG=\"usbnet\"", QUECTEL_ECM_MODE)

        if output[2] != 0:
            output = send_at_com("AT+QCFG=\"usbnet\",1", "OK")
           
            if output[2] == 0:
               logger.info("ECM mode is activated.")
               logger.info("The modem is rebooting to apply chnages...")
            else:
                raise ModemNotReachable(output[0])

            time.sleep(20)

            output = shell_command("route -n")

            if output[0].find("usb0"):
                logger.info("Modem started.")
            else:
                output = send_at_com("AT+CFUN=1,1", "OK")
                time.sleep(20)

                # Check modem is started!
                for i in range(120):
                    output = shell_command("route -n")     
                    if output[0].find("usb0"):
                        logger.info("Modem started.")
                        break
                    else:
                        time.sleep(1)
                        print("*", end="", flush=True)
                
                time.sleep(5)

    elif MODEM == TELIT:
        output = send_at_com("AT#USBCFG?", TELIT_ECM_MODE)

        if output[2] != 0:
            output = send_at_com("AT#USBCFG=4", "OK")
            
            if output[2] == 0:
                logger.info("ECM mode is activated.")
                logger.info("The modem is rebooting to apply chnages...")
            else:
                raise ModemNotReachable(output[0]) 

            time.sleep(20)

            output = shell_command("route -n")

            if output[0].find("wwan0"):
                logger.info("Modem started.")
            else:                
                # Check modem is started!
                for i in range(120):
                    output = shell_command("route -n")     
                    if(output[0].find("wwan0")):
                        logger.info("Modem started.")
                        break
                    else:
                        time.sleep(1)
                        print("*", end="", flush=True)
                
                time.sleep(5)
    elif MODEM == "":
        logger.error("Modem couldn't be detected!")
        raise ModemNotFound("Modem couldn't be detected!")

    else:
        logger.error("Modem is unknown or unsupported!")
        raise ModemNotSupported("Modem is unknown or unsupported!")
    
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
            logger.info("Network is registerated.")
            network_reg = 1
        else:
            logger.error(output[0])
            raise NetworkRegFailed(output[0])
    else:
        logger.error(output[0])
        raise NetworkRegFailed(output[0])