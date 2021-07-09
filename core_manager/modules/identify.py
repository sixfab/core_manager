#!/usr/bin/python3

import os.path
import platform 

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import send_at_com, shell_command
from helpers.yamlio import read_yaml_all, write_yaml_all, SYSTEM_PATH
from helpers.exceptions import ModemNotReachable, ModemNotSupported
from helpers.modem_support import ModemSupport
from __version__ import version


system_id = {
    "platform" : "",
    "arc" : "",
    "machine": "",
    "kernel" : "",
    "host_name" : "",
    "modem_vendor" : "",
    "modem_vendor_id" : "",
    "modem_product_id" : "",
    "imei" : "",
    "iccid" : "",
    "sw_version" : "",
    "manager_version" : version, 
    "board" : "",
}


def _turn_off_echo():
    output = send_at_com("ATE0", "OK")

    if output[2] == 0:
        pass
    else:
        raise ModemNotReachable("Error occured turning of AT echo : send_at_com -> ATE0")

def _identify_vendor_name(method=0):
    system_id["modem_vendor"] = ""

    output = shell_command("lsusb")

    if output[2] == 0:
        for vendor in ModemSupport.vendors:
            if output[0].find(vendor.vid) != -1:
                system_id["modem_vendor"] = vendor.name

        if system_id["modem_vendor"] == "":
            logger.warning("Modem vendor couldn't be found!")
    else:
        raise RuntimeError("Modem vendor couldn't be found!")

    if system_id["modem_vendor"] == "":
        raise ModemNotSupported("Modem vendor couldn't be found!")


def _identify_product_name(method=0):
    system_id["modem_name"] = ""

    output = shell_command("lsusb")
    if output[2] == 0:     
        for vendor in ModemSupport.vendors:
            for key in vendor.modules:
                if output[0].find(vendor.modules[key]) != -1:
                    system_id["modem_name"] = key.split("_")[0]
    else:
        raise RuntimeError("Error occured on lsusb command!")
    
    output = send_at_com("AT+GMM","OK")
    if output[2] == 0:
        try:
            system_id["modem_name"] += " " +  str(output[0].split("\n")[1] or "")
        except:
            pass
        
    if system_id["modem_name"] == "":
        raise ModemNotSupported("Modem name couldn't be found!")


def _identify_usb_vid_pid():
    system_id["modem_vendor_id"] = ""
    system_id["modem_product_id"] = ""

    output = shell_command("lsusb")
    if output[2] == 0:
        for vendor in ModemSupport.vendors:
            if output[0].find(vendor.vid) != -1:
                system_id["modem_vendor_id"] = vendor.vid
                
        for vendor in ModemSupport.vendors:
            for key in vendor.modules:
                if output[0].find(vendor.modules[key]) != -1:
                    system_id["modem_product_id"] = str(vendor.modules[key])
            
        if system_id["modem_vendor_id"] == "" or system_id["modem_product_id"] == "":
            raise ModemNotSupported("Modem is not supported!")
        else:
            return (system_id["modem_vendor_id"], system_id["modem_product_id"])
    else:
        raise RuntimeError("Error occured on lsusb command!")


def _identify_imei():
    output = send_at_com("AT+CGSN","OK")
    raw_imei = output[0] if output[2] == 0 else "" 
    
    if raw_imei != "":
        imei_filter = filter(str.isdigit, raw_imei)
        system_id["imei"] = "".join(imei_filter)
        return system_id["imei"]
    else: 
        raise ModemNotReachable("IMEI couldn't be detected!")


def _identify_fw_version():
    output = send_at_com("AT+CGMR","OK")
    system_id["sw_version"] = output[0].split("\n")[1] if output[2] == 0 else ""
    
    if system_id["sw_version"] != "":
        return system_id["sw_version"]
    else: 
        raise ModemNotReachable("Firmware Ver. couldn't be detected!")


def _identify_iccid():
    output = send_at_com("AT+ICCID","OK")
    raw_iccid = output[0] if output[2] == 0 else ""

    if raw_iccid != "":
        iccid_filter = filter(str.isdigit, raw_iccid)
        system_id["iccid"] = "".join(iccid_filter)
        return system_id["iccid"]
    else: 
        raise ModemNotReachable("ICCID couldn't be detected!")


def _identify_os():
    try:
        logger.debug("[+] OS artchitecture")
        system_id["arc"] = str(platform.architecture()[0])
        
        logger.debug("[+] OS machine")
        system_id["machine"] = str(platform.machine())

        logger.debug("[+] Kernel version")
        system_id["kernel"] = str(platform.release())
        
        logger.debug("[+] Host name")
        system_id["host_name"] = str(platform.node())
        
        logger.debug("[+] OS platform")
        system_id["platform"] = str(platform.platform())
    except:
        raise RuntimeError("Error occured while getting OS identification!")
    

def _identify_board(): 
    output = shell_command("cat /sys/firmware/devicetree/base/model")

    if output[2] == 0:
        system_id["board"] = output[0]
    else:
        raise RuntimeError("Board couldn't be detected!")


def identify_setup():
    # Get old system setup if it is exist
    old_system_id = {}
    if os.path.isfile(SYSTEM_PATH):
        try:
            old_system_id = read_yaml_all(SYSTEM_PATH)
        except Exception as e:
            logger.warning("Old system_id in system.yaml file couln't be read!")

    logger.info("[?] System identifying...")
    
    # Modem vendor name (Required)
    logger.debug("[+] Modem vendor name")
    try:
        _identify_vendor_name()
    except Exception as e:
        logger.critical("Modem vendor identification failed!")
        raise ModemNotSupported("Modem is not supported!")

    # Turn off AT command echo (Required)
    logger.debug("[+] Turning off AT command echo")
    try:
        _turn_off_echo()
    except Exception as e:
        raise e
    
    # Product Name (Optional)
    logger.debug("[+] Product Name")
    try:
        _identify_product_name()
    except Exception as e:
        logger.warning("Modem name identification failed!")
        system_id["modem_name"] = "Unknown"

    # Vendor ID & Product ID (Required)
    logger.debug("[+] Modem USB VID and PID")
    try:
        _identify_usb_vid_pid()
    except Exception as e:
        logger.warning("Modem VID PID identification failed!")
        raise ModemNotSupported("Modem is not supported!")

    # IMEI (Optional)
    logger.debug("[+] IMEI")
    try:
        _identify_imei()
    except Exception as e:
        logger.warning("IMEI identification failed!")
        system_id["imei"] = "Unknown"
    
    # SW version (Optional)
    logger.debug("[+] Modem firmware revision")
    try:
        _identify_fw_version()
    except Exception as e:
        logger.warning("Modem firmware ver. identification failed!")
        system_id["sw_version"] = "Unknown"

    # ICCID (Optional)
    logger.debug("[+] SIM ICCID")
    try:
        _identify_iccid()
    except Exception as e:
        logger.warning("SIM ICCID identification failed!")
        system_id["iccid"] = "Unknown"

    # OS (Optional)
    logger.debug("[>] OS Identification")
    try:
        _identify_os()
    except Exception as e:
        logger.warning("OS identification failed!")
    
    # Board (Optional)
    logger.debug("[+] Board Identification")
    try:
        _identify_board()
    except Exception as e:
        logger.warning("Board identification failed!")

    # IDENTIFICATION REPORT
    if conf.debug_mode == True and conf.verbose_mode == True:
        print("")
        print("********************************************************************")
        print("[?] IDENTIFICATION REPORT")
        print("-------------------------")
        for x in system_id.items():
            print(str("[+] " + x[0]) + " --> " + str(x[1]))
        print("********************************************************************")
        print("")

    # Save ID's to file
    try:
        write_yaml_all(SYSTEM_PATH, system_id)
    except Exception as e:
        logger.error(e)
        raise e

    if system_id != old_system_id:
        logger.warning("System setup has changed!")
    
    return system_id or {}


if __name__ == "__main__":
    identify_setup()

    