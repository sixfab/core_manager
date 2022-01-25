#!/usr/bin/python3
import time
import os.path

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.yamlio import read_yaml_all, write_yaml_all, MONITOR_PATH


# monitoring properties
monitor_data = {
    "cellular_connection": None,
    "usable_interfaces": None,
    "active_interface": None,
    "signal_quality": None,
    "roaming_operator": None,
    "active_lte_tech": None,
    "fixed_incident": 0,
}


def monitor(modem, network):
    # Get old system setup if it is exist
    old_monitor = {}
    if os.path.isfile(MONITOR_PATH):
        try:
            old_monitor = read_yaml_all(MONITOR_PATH)
        except:
            logger.warning("Old monitor data in monitor.yaml file couln't be read!")

    monitor_data["last_update"] = old_monitor.get("last_update", int(time.time()))

    # Modem Manager monitoring data
    try:
        monitor_data["cellular_connection"] = modem.monitor.get("cellular_connection")
        monitor_data["selected_apn"] = modem.get_apn()

        incident_count = monitor_data.get("fixed_incident", 0)
        old_incident_count = old_monitor.get("fixed_incident", 0)

        if incident_count >= old_incident_count:
            monitor_data["fixed_incident"] = modem.get_fixed_incident_count()
        else:
            monitor_data["fixed_incident"] = old_incident_count

    except Exception as error:
        logger.error("monitor() @modem -> %s", error)

    try:
        monitor_data["signal_quality"] = modem.get_signal_quality()
    except Exception as error:
        logger.error("monitor() @modem -> %s", error)

    try:
        monitor_data["roaming_operator"] = modem.get_roaming_operator()
    except Exception as error:
        logger.error("monitor() @modem -> %s", error)

    try:
        monitor_data["active_lte_tech"] = modem.get_active_lte_tech()
    except Exception as error:
        logger.error("monitor() @modem -> %s", error)

    # Network Manager monitoring data
    try:
        monitor_data["usable_interfaces"] = network.find_usable_interfaces()
        monitor_data["active_interface"] = network.find_active_interface()
        monitor_data["ifs_status"] = network.monitor
    except Exception as error:
        logger.error("monitor() @network -> %s", error)

    if monitor_data != old_monitor:

        monitor_data["last_update"] = int(time.time())

        # Save ID's to file
        try:
            write_yaml_all(MONITOR_PATH, monitor_data)
        except Exception as error:
            logger.error("write_yaml_all(MONITOR_PATH, modem.monitor) -> %s", error)
        else:
            logger.info("Monitoring data updated with changes.")

            # MONITOR REPORT
            if conf.debug_mode and conf.verbose_mode:
                print("")
                print("********************************************************************")
                print("[?] MONITOR REPORT")
                print("-------------------------")
                for item in monitor_data.items():
                    print(f"[+] {item[0]} --> {item[1]}")
                print("********************************************************************")
                print("")
            # END OF MONITOR REPORT
    else:
        # logger.debug("No change on monitoring data.")
        pass
