#!/usr/bin/python3

from helpers.commander import shell_command
from helpers.exceptions import NoInternet
from helpers.config_parser import logger, PING_TIMEOUT, NETWORK_PRIORITIES
from helpers.netiface import NetInterface
from cm import modem

lowest_priority_factor = 100

def parse_output(output, header, end):
    header += " "
    header_size = len(header)
    index_of_data = output[0].find(header) + header_size
    end_of_data = index_of_data + output[0][index_of_data:].find(end)
    sig_data = output[0][index_of_data:end_of_data]
    return sig_data


class Network(object):
    
    # monitoring properties
    monitor = {
        "wlan0_status" : None,
        "wlan0_connection" : None,
        "wlan0_latency" : None,
        "eth0_status" : None,
        "eth0_connection": None,
        "eth0_latency" : None,
    }

    cell = NetInterface()
    eth = NetInterface()
    wlan = NetInterface()
    
    def __init__(self):
        pass

    def check_interface_health(self, interface):
        output = shell_command("ping -q -c 1 -s 8 -w "  + str(PING_TIMEOUT) + " -I " + interface + " 8.8.8.8")
        #print(output)

        if output[2] == 0:
            
            try:
                ping_latencies = parse_output(output, "min/avg/max/mdev =", "ms")
                min_latency = float(ping_latencies.split("/")[0])
            except:
                raise RuntimeError("Error occured while getting ping latency!")
            
            return (0, min_latency)
        else:
            raise NoInternet("No internet!")


    def find_usable_interfaces(self):
        # Supported interfaces
        interfaces = ["eth0", "wlan0", "usb0", "wwan0"]
        usable_interfaces = []

        output = shell_command("route -n")
        
        if output[2] == 0:
            for i in interfaces:
                if output[0].find(i) != -1:
                    usable_interfaces.append(i)
        
            return usable_interfaces
        else:
            raise RuntimeError("Error occured on \"route -n\" command!")


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

    
    def get_wlan0_connection(self):
        return self.monitor.get("wlan0_connection")


    def get_wlan0_latency(self):
        return self.monitor.get("wlan0_latency")


    def get_eth0_connection(self):
        return self.monitor.get("eth0_connection")

    
    def get_eth0_latency(self):
        return self.monitor.get("eth0_latency")


    def adjust_metric(self, interface, metric_factor):
        metric = metric_factor * 100

        output = shell_command("sudo ifmetric " + str(interface) + " " + str(metric))

        if output[2] == 0:
            return 0
        else:
            raise RuntimeError("Error occured on \"route -n\" command!")


    def check_and_create_monitoring(self):
        try:
            output = self.find_usable_interfaces()
        except Exception as e:
            logger.error("find_usable_interfaces() -> " + str(e))
        else:
            usable_interfaces = output

        for x in usable_interfaces:
            if x == self.eth.name:   
                try:
                    output = self.check_interface_health("eth0")
                except:
                    self.monitor["eth0_connection"] = False
                    self.monitor["eth0_latency"] = None
                else:
                    self.monitor["eth0_connection"] = True
                    self.monitor["eth0_latency"] = output[1]

            elif x == self.wlan.name:
                try:
                    output = self.check_interface_health("wlan0")
                except:
                    self.monitor["wlan0_connection"] = False
                    self.monitor["wlan0_latency"] = None
                else:
                    self.monitor["wlan0_connection"] = True
                    self.monitor["wlan0_latency"] = output[1]

 
    def adjust_priorities(self):
        
        self.eth.connection_status = self.get_eth0_connection()
        self.wlan.connection_status = self.get_wlan0_connection()
        self.cell.connection_status = modem.get_cellular_status()
        
        self.eth.name = "eth0"
        self.wlan.name = "wlan0"
        self.cell.name = modem.interface_name
        
        self.eth.metric_factor = NETWORK_PRIORITIES.get(self.eth.name)
        self.wlan.metric_factor = NETWORK_PRIORITIES.get(self.wlan.name)
        self.cell.metric_factor = NETWORK_PRIORITIES.get(self.cell.name)

        ifaces = [self.eth, self.wlan, self.cell]

        for iface in ifaces:
            if iface.connection_status != iface.last_connection_status:
                logger.info(str(iface.name) + " connection status changed : " + str(iface.connection_status))
                if iface.connection_status != True:
                    try:
                        self.adjust_metric(iface.name, lowest_priority_factor)
                    except:
                        logger.error("Error occured changing metric : " + str(iface.name)) 
                    else:
                        iface.last_connection_status = iface.connection_status
                else:
                    try:
                        self.adjust_metric(iface.name, iface.metric_factor)
                    except:
                        logger.error("Error occured changing metric : " + str(iface.name)) 
                    else:
                        iface.last_connection_status = iface.connection_status


        
    def debug_routes(self):
        output = shell_command("route -n")

        if output[2] == 0:
            print("")
            print("*****************************************************************")
            print(output[0])
            print("*****************************************************************")
            print("")
            return 0
        else:
            raise RuntimeError("Error occured on \"route -n\" command!")

        


    

    
