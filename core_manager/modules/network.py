#!/usr/bin/python3

from helpers.commander import shell_command
from helpers.exceptions import NoInternet
from helpers.config_parser import PING_TIMEOUT, NETWORK_PRIORITIES
from helpers.config_parser import logger

def parse_output(output, header, end):
    header += " "
    header_size = len(header)
    index_of_data = output[0].find(header) + header_size
    end_of_data = index_of_data + output[0][index_of_data:].find(end)
    sig_data = output[0][index_of_data:end_of_data]
    return sig_data

class Network(object):
    def __init__(self):
        pass

    def check_interface_health(self, interface):
        output = shell_command("ping -q -c 1 -s 0 -w "  + str(PING_TIMEOUT) + " -I " + interface + " 8.8.8.8")
        #print(output)

        if output[2] == 0:
            ping_latency = parse_output(output, "time", "ms")
            #print(ping_latency)
            return (0, ping_latency)
        else:
            raise NoInternet("No internet!")


    def find_usable_interfaces(self):
        # Supported interfaces
        interfaces = ["eth0", "wlan0", "usb0", "wwan0"]
        usable_interafaces = []

        output = shell_command("route -n")
        
        if output[2] == 0:
            for i in interfaces:
                if output[0].find(i) != -1:
                    usable_interafaces.append(i)
        
        return usable_interafaces


    def find_active_interface(self):
        # Supported interfaces and locations
        interfaces = {"eth0": 10000, "wlan0": 10000, "usb0": 10000, "wwan0": 10000}

        output = shell_command("route -n")
        
        if output[2] == 0:
            for key in interfaces:
                location = output[0].find(key)
                if  location != -1:
                    interfaces[key] = location
        else:
            raise RuntimeError("Error occured on \"route -n\" command!")

        # find interface has highest priority
        last_location = 10000
        high = None
        for key in interfaces:
            if  interfaces[key] < last_location:
                last_location = interfaces[key] 
                high = key

        return high

    

    

    
