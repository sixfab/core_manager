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

        incident_count = modem.monitor.get("fixed_incident", 0)
        old_incident_count = old_monitor.get("fixed_incident", 0)

        print("HELLO: ", incident_count, " ", old_incident_count)

        if incident_count >= old_incident_count:
            modem.monitor["fixed_incident"] = modem.get_fixed_incident_count()
        else:
            modem.monitor["fixed_incident"] = old_incident_count

    except Exception as e:
        logger.error("monitor() -> " + str(e))

    if modem.monitor != old_monitor:
        # Save ID's to file
        try:
            write_yaml_all(MONITOR_PATH, modem.monitor)
        except Exception as e:
            logger.error("write_yaml_all(MONITOR_PATH, modem.monitor) -> " + str(e))
        else:
            logger.debug("Monitoring data updated with changes.")

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
            # END OF IDENTIFICATION REPORT
    else:
        #logger.debug("No change on monitoring data.")
        pass

if __name__  == "__main__":
    interval = monitor()

