#!/usr/bin/python3

from modules.network import Network
from helpers.config_parser import logger

network = Network()
usable_interfaces = []

def manage_network():
    
    try:
        output = network.find_usable_interfaces()
    except Exception as e:
        logger.error("find_usable_interfaces() -> " + str(e))
    else:
        usable_interfaces = output

    for i in usable_interfaces:
        if i == "eth0":
            # eth0
            try:
                output = network.check_interface_health("eth0")
            except:
                network.monitor["eth0_connection"] = False
                network.monitor["eth0_latency"] = None
            else:
                network.monitor["eth0_connection"] = True
                network.monitor["eth0_latency"] = output[1]
        elif i == "wlan0":
            # wlan0
            try:
                output = network.check_interface_health("wlan0")
            except:
                network.monitor["wlan0_connection"] = False
                network.monitor["wlan0_latency"] = None
            else:
                network.monitor["wlan0_connection"] = True
                network.monitor["wlan0_latency"] = output[1]

    print(network.monitor["wlan0_connection"], network.monitor["wlan0_latency"])
    print(network.monitor["eth0_connection"], network.monitor["eth0_latency"])

if __name__  == "__main__":
    manage_network()
