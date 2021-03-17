#!/usr/bin/python3

import netifaces

from helpers.commander import shell_command
from helpers.exceptions import NoInternet
from helpers.config_parser import logger, OTHER_PING_TIMEOUT, NETWORK_PRIORTY, DEBUG, VERBOSE_MODE
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
    monitor = {}
    interfaces = []

    cell = NetInterface()
    eth = NetInterface()
    wlan = NetInterface()
    

    def __init__(self):
        pass


    def find_usable_interfaces(self):
        try:
            ifs = netifaces.interfaces()
        except:
            raise RuntimeError("Error occured getting usable interfaces!")
        else:
            ifs.remove("lo")
            return ifs


    def createInterface(self, name):
        interface = NetInterface()
        interface.name = name
        self.interfaces.append(interface)

    
    def removeInterface(self, value):
        self.interfaces.remove(value)


    def check_interfaces(self):
        usables = self.find_usable_interfaces()
        print("Usables: ", usables)
        actual = []

        for interface in self.interfaces:
            actual.append(interface.name)

        print("Actuals: ", actual) 

        for x in usables:
            if x not in actual:
                self.createInterface(x)
                
        for x in actual:
            if x not in usables:
                for y in self.interfaces:
                    if y.name == x:
                        self.removeInterface(y)
        
        # DEBUG
        for i in self.interfaces:
            print(i.name)
            

    def check_interface_health(self, interface):
        output = shell_command("ping -q -c 1 -s 8 -w "  + str(OTHER_PING_TIMEOUT) + " -I " + interface + " 8.8.8.8")
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
    
    
    def find_active_interface(self):
        
        interfaces = {}

        for x in self.interfaces:
            interfaces[x.name] = 10000
        
        print(interfaces)

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

    
    def adjust_metric(self, interface, metric_factor):
        metric = metric_factor * 100

        output = shell_command("sudo ifmetric " + str(interface) + " " + str(metric))

        if output[2] == 0:
            return 0
        else:
            raise RuntimeError("Error occured on \"route -n\" command!")


    def check_and_create_monitoring(self):
    
        for x in self.interfaces:
            try:
                output = self.check_interface_health(x.name)
            except:
                x.connection_status = False
                self.monitor[x.name] = [False, None]
            else:
                x.connection_status = True
                self.monitor[x.name] = [True, output[1]]

        print(self.monitor)


    def adjust_priorities(self):
        default_metric_factor = 10

        for x in self.interfaces:
            x.metric_factor = NETWORK_PRIORTY.get(x.name, default_metric_factor)
        
        for iface in self.interfaces:
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
        if DEBUG == True and VERBOSE_MODE == True:
            output = shell_command("route -n")

            if output[2] == 0:
                print("")
                print("*****************************************************************")
                print("[?] NETWORK MANAGER REPORT")
                print("---------------------------")
                print(output[0])
                print("*****************************************************************")
                print("")
                return 0
            else:
                raise RuntimeError("Error occured on \"route -n\" command!")

        


    

    
