from helpers.logger import initialize_logger
from helpers.serial import shell_command, send_at_com
from helpers.config import *
from helpers.exceptions import *
import time

config = read_yaml_all(CONFIG_PATH)

DEBUG = config["debug_mode"]
APN = config["apn"]

logger = initialize_logger(DEBUG)

QUECTEL_ECM_MODE = "1"
TELIT_ECM_MODE = "4"

QUECTEL = 1
TELIT = 2

NET_RETRY_COUNT = 20
DET_RETRY_COUNT = 10

def _configure_apn(apn):
    output = send_at_com("AT+CGDCONT?", apn)

    if( output[2] == 0 ):
        logger.info("APN is up-to-date.") 
    else:
        output = send_at_com("AT+CGDCONT=1,\"IPV4V6\",\"" + apn + "\"","OK")

        if(output[2] == 0):
            logger.info("APN is updated succesfully : " + apn)
        else:
            logger.error("Message: " + output[0])

def _detect_modem():
    for i in range(DET_RETRY_COUNT):
        
        output = shell_command("lsusb")

        if output[2] == 0:
            if (output[0].find("Quectel") != -1):
                return 1
            elif(output[0].find("Telit") != -1):
                return 2
        else:
            raise RuntimeError("RuntimeError: Shell command couldn't be succesfully run!")
        
        time.sleep(1)
    
    raise ModemNotFound("ModemNotFound: Modem couldn't be detected!")

def configure_modem():
    logger.info("Modem configuration started...")

    modem = None

    try:
        modem = _detect_modem()
    except Exception as e:
        logger.error(str(e))
        modem = -1
    else:
        logger.info("Modem detected. Modem ID: " + str(modem))

    ### Modem configuration for ECM mode ##################################
    logger.info("Checking APN and Modem Mode...") 

    _configure_apn("super")

    # Modem Mode Configuration
    # ------------------------
    if modem is QUECTEL:
        output = send_at_com("AT+QCFG=\"usbnet\"", QUECTEL_ECM_MODE)

        if(output[2] != 0):
            output = send_at_com("AT+QCFG=\"usbnet\",1", "OK")
           
            if( output[2] == 0):
               logger.info("ECM mode is activated.")
               logger.info("The modem is rebooting to apply chnages...")
            else:
                logger.error("Message: " + output[0]) 

            time.sleep(20)

            output = shell_command("route -n")

            if(output[0].find("usb0")):
                logger.info("Modem started.")
            else:
                output = send_at_com("AT+CFUN=1,1", "OK")
                time.sleep(20)

                # Check modem is started!
                for i in range(120):
                    output = shell_command("route -n")     
                    if(output[0].find("usb0")):
                        logger.info("Modem started.")
                        break
                    else:
                        time.sleep(1)
                        print("*", end="", flush=True)
                
                time.sleep(5)

    elif modem is TELIT:
        output = send_at_com("AT#USBCFG?", TELIT_ECM_MODE)

        if(output[2] != 0):
            output = send_at_com("AT#USBCFG=4", "OK")
            
            if(output[2] == 0):
                logger.info("ECM mode is activated.")
                logger.info("The modem is rebooting to apply chnages...")
            else:
                logger.error("Message: " + output[0]) 

            time.sleep(20)

            output = shell_command("route -n")

            if(output[0].find("wwan0")):
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
    elif modem is -1:
        logger.error("Modem couldn't be detected!")
        raise ModemNotFound

    else:
        logger.error("Modem is unknown or unsupported!")
        raise ModemNotSupported
    
    ### End of Modem configuration for ECM mode ############################

    

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