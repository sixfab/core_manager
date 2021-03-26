#!/usr/bin/python3
import time
import os.path

from helpers.yamlio import read_yaml_all, write_yaml_all, MONITOR_PATH
from helpers.exceptions import ModemNotFound
from helpers.config_parser import logger, conf, get_configs
from cm import modem
from nm import network

# monitoring properties
monitor_data = {
    "cellular_connection" : None,
    "usable_interfaces" : None,
    "active_interface" : None,
    "signal_quality" : None,
    "roaming_operator" : None,
    "active_lte_tech": None,
    "fixed_incident": 0,
}

def monitor():
    conf = get_configs()

    # Get old system setup if it is exist
    old_monitor = {}
    if os.path.isfile(MONITOR_PATH):
        try:
            old_monitor = read_yaml_all(MONITOR_PATH)
        except Exception as e:
            logger.warning("Old monitor data in monitor.yaml file couln't be read!")

    try:
        monitor_data["cellular_connection"] = modem.monitor.get("cellular_connection")
        monitor_data["cellular_latency"] = modem.monitor.get("cellular_latency")
        monitor_data["active_lte_tech"] = modem.get_active_lte_tech()
        monitor_data["roaming_operator"] = modem.get_roaming_operator()
        monitor_data["signal_quality"] = modem.get_signal_quality()
        monitor_data["selected_apn"] = modem.get_apn()

        incident_count = monitor_data.get("fixed_incident", 0)
        old_incident_count = old_monitor.get("fixed_incident", 0)

        if incident_count >= old_incident_count:
            monitor_data["fixed_incident"] = modem.get_fixed_incident_count()
        else:
            monitor_data["fixed_incident"] = old_incident_count
            
    except Exception as e:
        logger.error("monitor() @modem -> " + str(e))
        
    try:    
        monitor_data["usable_interfaces"] = network.find_usable_interfaces()
        monitor_data["active_interface"] = network.find_active_interface()
        monitor_data["ifs_status"] = network.monitor
    except Exception as e:
        logger.error("monitor() @network -> " + str(e))

    if monitor_data != old_monitor:
        # Save ID's to file
        try:
            write_yaml_all(MONITOR_PATH, monitor_data)
        except Exception as e:
            logger.error("write_yaml_all(MONITOR_PATH, modem.monitor) -> " + str(e))
        else:
            logger.debug("Monitoring data updated with changes.")

            # IDENTIFICATION REPORT
            if conf.debug_mode == True and conf.verbose_mode == True:
                print("")
                print("********************************************************************")
                print("[?] MONITOR REPORT")
                print("-------------------------")
                for x in monitor_data.items():
                    print(str("[+] " + x[0]) + " --> " + str(x[1]))
                print("********************************************************************")
                print("")
            # END OF IDENTIFICATION REPORT
    else:
        #logger.debug("No change on monitoring data.")
        pass

    return conf.send_monitoring_data_interval

if __name__  == "__main__":
    monitor()

