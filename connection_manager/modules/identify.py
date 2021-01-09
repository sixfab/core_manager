
import platform 
from helpers.serial import send_at_com
from helpers.config import *
from helpers.queue import queue
from helpers.exceptions import *
from modules.modem import detect_modem

def identify_setup():

    send_at_com("ATE0", "OK") # turn off modem input echo

    # Modem identification
    # -----------------------------------------

    try:
        modem_vendor = detect_modem()
    except Exception as e:
        raise e

    output = send_at_com("ATI", "OK")
    modem_info = output[0].replace("\n", " ") if output[2] == 0 else ""
    # IMEI
    output = send_at_com("AT+CGSN","OK")
    raw_imei = output[0] if output[2] == 0 else ""
    imei_filter = filter(str.isdigit, raw_imei)
    imei = "".join(imei_filter)
    # SW version
    output = send_at_com("AT+CGMR","OK")
    sw_ver = output[0].split("\n")[1] if output[2] == 0 else ""

    # SIM identification
    # -----------------------------------------
    # CCID
    output = send_at_com("AT+CCID","OK")
    raw_ccid = output[0] if output[2] == 0 else ""
    ccid_filter = filter(str.isdigit, raw_ccid)
    ccid = "".join(ccid_filter)

    # OS identification
    # -----------------------------------------
    try:
        architecture = str(platform.architecture()[0])
        kernel_release = str(platform.release())
        host_name = str(platform.node())
        os_platform = str(platform.platform())
    except Exception as e:
        logger.error("Error occured while getting OS identification!")
        raise RuntimeError("Error occured while getting OS identification!")

    system_id = {}
    system_id.update(
        {
            "platform" : os_platform,
            "arc" : architecture,
            "kernel" : kernel_release,
            "host_name" : host_name,
            "modem_info" : modem_info,
            "modem_vendor" : modem_vendor,
            "imei" : imei,
            "ccid" : ccid,
            "sw_version" : sw_ver,
        }
    )

    for key in system_id:
        if system_id[key] == "":
            logger.error("Modem identification failed!")
            raise RuntimeError("Modem identification failed!")

    try:
        write_yaml_all(SYSTEM_PATH, system_id)
    except Exception as e:
        logger.error(e)
        raise RuntimeError(e)
    
    return system_id