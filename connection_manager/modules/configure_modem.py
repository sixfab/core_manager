from helpers.logger import initialize_logger
from helpers.serial import shell_command, send_at_com
from helpers.config import read_config
import time

config = read_config()

DEBUG = config["debug_mode"]
APN = config["apn"]

logger = initialize_logger(DEBUG)

QUECTEL_ECM_MODE = "1"
TELIT_ECM_MODE = "4"

QUECTEL = 1
TELIT = 2

DET_RETRY_COUNT = 10


def detect_modem():
    for i in range(DET_RETRY_COUNT):
        
        output = shell_command("lsusb")[0]
        
        if (output.find("Quectel") != -1):
            return 1
        elif(output.find("Telit") != -1):
            return 2

        time.sleep(1)
    
    return -1


def configure_modem():
    logger.info("Modem configuration is Started...")

    modem = None

    try:
        modem = detect_modem()
    except Exception as e:
        print(e)
        logger.error("Modem detection failure...")
        modem = -1

    ### Modem configuration for ECM mode ##################################
    logger.info("Checking APN and Modem Mode...") 

    # APN Configuration
    # -----------------
    output = send_at_com("AT+CGDCONT?", APN)

    if( output[2] == 0 ):
        logger.info("APN is up-to-date.") 
    else:
        output = send_at_com("AT+CGDCONT=1,\"IPV4V6\",\"super\"","OK")

        if(output[2] == 0):
            logger.info("APN is updated succesfully : " + APN)
        else:
            logger.error("Message: " + output[0])


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
    else:
        logger.error("Modem is unknown or unsupported!")
    
    ### End of Modem configuration for ECM mode ############################
    


    
    

