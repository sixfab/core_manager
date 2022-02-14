#!/usr/bin/python3

import time
import os.path
import platform

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import send_at_com, shell_command
from helpers.yamlio import read_yaml_all, write_yaml_all, SYSTEM_PATH
from helpers.exceptions import ModemNotReachable, ModemNotSupported
from helpers.modem_support.modem_support import modules, default_modules
from __version__ import version

identified_module = None

system_id = {
    "manager_version": version,
}


# Save ID's to file
try:
    write_yaml_all(SYSTEM_PATH, system_id)
except Exception as error:
    raise RuntimeError("Save ID's to file") from error


def identify_modem():
    global identified_module

    # Get old system setup if it is exist
    old_system_id = {}
    if os.path.isfile(SYSTEM_PATH):
        try:
            old_system_id = read_yaml_all(SYSTEM_PATH)
        except Exception as error:
            logger.warning("Old system_id in system.yaml file couln't be read!")

    system_id["modem_vendor"] = ""
    system_id["modem_name"] = ""
    system_id["modem_vendor_id"] = ""
    system_id["modem_product_id"] = ""

    logger.info("Tyring to detect modem...")

    output = shell_command("lsusb")

    if output[2] == 0:
        for module in modules:
            if output[0].find(module.pid) != -1:
                system_id["modem_vendor"] = module.vendor_name
                system_id["modem_name"] = module.module_name
                system_id["modem_vendor_id"] = module.vid
                system_id["modem_product_id"] = module.pid
                identified_module = module
                return identified_module
        logger.warning("Modem don't exist in list of supported modems!")

        for module in modules:
            if output[0].find(module.vid) != -1:
                system_id["modem_vendor"] = module.vendor_name
                system_id["modem_name"] = default_modules.get(str(module.vid)).module_name
                system_id["modem_vendor_id"] = module.vid
                system_id["modem_product_id"] = default_modules.get(str(module.vid)).pid
                identified_module = default_modules.get(str(module.vid))
                return identified_module
        logger.warning("Modem vendor couldn't be found!")

        # clear modem identification data
        system_id["modem_vendor"] = None
        system_id["modem_name"] = None
        system_id["modem_vendor_id"] = None
        system_id["modem_product_id"] = None
        system_id["iccid"] = None
        system_id["imei"] = None
        system_id["sw_version"] = None

        if old_system_id.get("modem_vendor") is not None:
            try:
                write_yaml_all(SYSTEM_PATH, system_id)
            except Exception as error:
                raise RuntimeError("Save ID's to file") from error

        raise RuntimeError("Modem vendor couldn't be found!")
    else:
        raise RuntimeError("lsusb command error!")


def _turn_off_echo():
    output = send_at_com("ATE0", "OK")

    if output[2] == 0:
        pass
    else:
        raise ModemNotReachable("Error occured turning of AT echo : send_at_com -> ATE0")


def _identify_product_name():
    output = send_at_com("AT+GMM", "OK")
    if output[2] == 0:
        raw = output[0].split("\n")

        for _, value in enumerate(raw):
            if value != "":
                system_id["modem_name"] += " " + value
                break

    if system_id["modem_name"] == "":
        raise ModemNotSupported("Modem name couldn't be found!")


def _identify_imei():
    output = send_at_com("AT+CGSN", "OK")
    raw_imei = output[0] if output[2] == 0 else ""

    if raw_imei != "":
        imei_filter = filter(str.isdigit, raw_imei)
        system_id["imei"] = "".join(imei_filter)
        return system_id["imei"]
    else:
        raise ModemNotReachable("IMEI couldn't be detected!")


def _identify_fw_version():
    output = send_at_com("AT+CGMR", "OK")
    if output[2] == 0:
        raw = output[0].split("\n")

        for _, value in enumerate(raw):
            if value != "":
                system_id["sw_version"] = value
                break

        if system_id["sw_version"] != "":
            return system_id["sw_version"]
    else:
        raise ModemNotReachable("Firmware Ver. couldn't be detected!")


def _identify_iccid():
    output = send_at_com(identified_module.ccid_command, "OK")
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
    except Exception as error:
        raise RuntimeError("Error occured while getting OS identification!") from error


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
        except Exception as error:
            logger.warning("Old system_id in system.yaml file couln't be read!")

    logger.info("[?] System identifying...")

    # Turn off AT command echo (Required)
    logger.debug("[+] Turning off AT command echo")
    try:
        _turn_off_echo()
    except Exception as error:
        raise error

    # Product Name (Optional)
    logger.debug("[+] Product Name")
    try:
        _identify_product_name()
    except Exception as error:
        logger.warning("Modem name identification failed!")
        system_id["modem_name"] = "Unknown"

    # IMEI (Optional)
    logger.debug("[+] IMEI")
    try:
        _identify_imei()
    except Exception as error:
        logger.warning("IMEI identification failed!")
        system_id["imei"] = "Unknown"

    # SW version (Optional)
    logger.debug("[+] Modem firmware revision")
    try:
        _identify_fw_version()
    except Exception as error:
        logger.warning("Modem firmware ver. identification failed!")
        system_id["sw_version"] = "Unknown"

    # ICCID (Optional)
    logger.debug("[+] SIM ICCID")
    try:
        _identify_iccid()
    except Exception as error:
        logger.warning("SIM ICCID identification failed!")
        system_id["iccid"] = "Unknown"

    # OS (Optional)
    logger.debug("[>] OS Identification")
    try:
        _identify_os()
    except Exception as error:
        logger.warning("OS identification failed!")

    # Board (Optional)
    logger.debug("[+] Board Identification")
    try:
        _identify_board()
    except Exception as error:
        logger.warning("Board identification failed!")

    try:
        system_id["last_update"] = int(time.time())
    except Exception as error:
        logger.error("identify() timestamp -> %s", error)

    # IDENTIFICATION REPORT
    if conf.debug_mode and conf.verbose_mode:
        print("")
        print("********************************************************************")
        print("[?] IDENTIFICATION REPORT")
        print("-------------------------")
        for item in system_id.items():
            print(f"[+] {item[0]} --> {item[1]}")
        print("********************************************************************")
        print("")

    # Save ID's to file
    try:
        write_yaml_all(SYSTEM_PATH, system_id)
    except Exception as error:
        raise error

    if system_id != old_system_id:
        logger.warning("System setup has changed!")

    return system_id or {}
