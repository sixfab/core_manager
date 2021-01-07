from helpers.logger import initialize_logger
from helpers.serial import shell_command, send_at_com
from helpers.config import read_config
import time

config = read_config()

DEBUG = config["debug_mode"]
APN = config["apn"]

logger = initialize_logger(DEBUG)

NET_RETRY_COUNT = 20

def check_network():

    sim_ready = 0
    network_reg = 0
    network_ready = 0

    # Check the network is ready
    logger.info("Checking the network is ready...")

    for i in range(NET_RETRY_COUNT):
        output = send_at_com("AT+CPIN?", "CPIN: READY")

        if(output[2] == 0):
            logger.info("SIM is ready.")
            sim_ready = 1
        else:
            logger.error("Error occured when getting SIM Status!")

        output = send_at_com("AT+CREG?", "OK")

        if (output[2] == 0):
            if(output[0].find("+CREG: 0,1") or output[0].find("+CREG: 0,5")):
                logger.info("Network is registerated.")
                network_reg = 1
            else:
                logger.error("Message: " + output[0])
        else:
            logger.error("Error occured when getting network registeration!")

        if((sim_ready == 1) and (network_reg == 1)):
            logger.info("Network is ready.")
            network_ready = 1
            return 0
        else:
            logger.info("Retrying network registeration...")
        
        time.sleep(2)

    logger.error("Network registeration is failed! Please check SIM card, data plan, antennas etc.")
    return 1