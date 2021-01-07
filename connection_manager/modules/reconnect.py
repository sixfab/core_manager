from helpers.logger import initialize_logger
from helpers.serial import shell_command, send_at_com
from helpers.config import read_config
import time

config = read_config()

DEBUG = config["debug_mode"]
APN = config["apn"]

logger = initialize_logger(DEBUG)

QUECTEL = 1
TELIT = 2

PING_TIMEOUT = 9
INTERFACE = "usb0"

def initiate_ecm(modem):
    if modem == QUECTEL:
        logger.info("ECM Connection is initiating automatically...")
    elif modem == TELIT:
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
    # print(output)

    if output[2] == 0:
        return 0
    else:
        return 1


def reconnect(modem):
    # 1 - Get modem diagnostics
    logger.info("Cellular connection is lost. Testing modem configurations...")
        
    # 2 - Reset USB interfaces of modem 

    # 3 - Reboot modem and re-initialize pdp context
    logger.info("Modem restarting...")
    if modem == QUECTEL:
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
                print("*", end="", flush=True)

        if check_network() == 0:
            initiate_ecm()
            return 0
        else:
            logger.error("Error occured while initiating ecm!")

    elif modem == TELIT:
        logger.info("Telit doesn't supported yet!")
        return 1
    
    else:
        logger.info("Unknown or unspoorted modem!")
        return 2
        



