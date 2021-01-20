#!/usr/bin/python3
import time

from helpers.yamlio import *
from helpers.exceptions import *
from helpers.config_parser import *
from cm import modem


def monitor():
    # Get old system setup if it is exist
    old_monitor = {}
    if os.path.isfile(MONITOR_PATH):
        try:
            old_monitor = read_yaml_all(MONITOR_PATH)
        except Exception as e:
            logger.warning("Old monitor data in monitor.yaml file couln't be read!")


    try:
        modem.monitor["cellular_connection"] = modem.get_cellular_status()
        modem.monitor["usable_interfaces"] = modem.find_usable_interfaces()
        modem.monitor["active_interface"] = modem.find_active_interface()
        modem.monitor["active_lte_tech"] = modem.get_active_lte_tech()
        modem.monitor["roaming_operator"] = modem.get_roaming_operator()
        modem.monitor["signal_quality"] = modem.get_signal_quality()
    except Exception as e:
        logger.error(str(e))

    if modem.monitor != old_monitor:
        # Save ID's to file
        try:
            write_yaml_all(MONITOR_PATH, modem.monitor)
        except Exception as e:
            logger.error(str(e))
        else:
            logger.info("Monitoring data updated with changes.")
    else:
        logger.info("No change on monitoring data.")


    # IDENTIFICATION REPORT
    if DEBUG == True and VERBOSE_MODE == True:
        print("")
        print("********************************************************************")
        print("[?] MONITOR REPORT")
        print("-------------------------")
        for x in modem.monitor.items():
            print(str("[+] " + x[0]) + " --> " + str(x[1]))
        print("********************************************************************")
        print("")


if __name__  == "__main__":
    interval = monitor()

