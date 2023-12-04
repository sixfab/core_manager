#!/usr/bin/python3
import os 

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import shell_command
from helpers.exceptions import NoInternet
from helpers.netiface import InterfaceTypes, NetInterface, interface_types

LOWEST_PRIORTY_METRIC = 10000

def parse_output(string, header, end):
    header += " "
    header_size = len(header)
    index_of_data = string.find(header) + header_size
    end_of_data = index_of_data + string[index_of_data:].find(end)
    sig_data = string[index_of_data:end_of_data]
    return sig_data


class Network():

    # monitoring properties
    monitor = {}
    interfaces = []
    configured_by_name = []
    configured_by_type = []

    def __init__(self, modem):
        self.modem = modem

    def find_usable_interfaces(self):
        ifs = []
        output = shell_command("ip route list")

        if output[2] != 0:
            raise RuntimeError('Error occured on "ip route list" command!')

        for line in output[0].splitlines():
            try:
                dev = parse_output(line, "dev", " ")
                if (
                    dev not in ifs and
                    dev not in conf.network_interface_exceptions
                    ):
                    ifs.append(dev)
            except Exception as error:
                raise RuntimeError("Interface dev couldn't be read!") from error

        return ifs

    def create_interface(self, name):
        interface = NetInterface()
        interface.name = name
        self.interfaces.append(interface)

    def remove_interface(self, name):
        for iface in self.interfaces:
            if iface.name == name:
                self.interfaces.remove(iface)

    def check_interfaces(self):
        try:
            usables = self.find_usable_interfaces()
        except Exception as error:
            logger.error("find_usable_interfaces() --> %s", error)

        actual = [ interface.name for interface in self.interfaces ]

        for usable_if in usables:
            if usable_if not in actual:
                self.create_interface(usable_if)

        for actual_if in actual:
            if actual_if not in usables:
                self.remove_interface(actual_if)

    def _get_interface_type(interface):
            eth_drivers = "macb bcmgenet, e1000e, r8169, igb"
            wifi_drivers =  "brcmfmac, ath9k, ath10k, iwlwifi, rtl8192ce"
            cellular_drivers = "cdc_ether, cdc_ncm, qmi_wwan"

            info_file = f'/sys/class/net/{interface}/device/uevent'
            info_data = {}

            # Get interface info from uevent file
            if os.path.exists(info_file):
                with open(info_file, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            parts = line.split('=')
                            if len(parts) == 2:
                                info_data[parts[0]] = parts[1]

            driver = info_data.get('DRIVER')
    
            # Decide interface type according to DRIVER info
            if driver in wifi_drivers:
                return InterfaceTypes.WIFI
            elif driver in cellular_drivers:
                return InterfaceTypes.CELLULAR
            elif driver in eth_drivers:
                return InterfaceTypes.ETHERNET
            else:
                return InterfaceTypes.UNKNOWN
            
    def get_interface_type(self):
        for interface in self.interfaces:
            try:
                interface.if_type = Network._get_interface_type(interface.name)
            except Exception as error:
                logger.error("get_interface_type() --> %s", error)

    def check_interface_health(self, interface):

        health_check = f"ping -q -c 1 -s 8 -w {conf.other_ping_timeout} -I {interface} 8.8.8.8"
        output = shell_command(health_check)

        if output[2] == 0:
            pass
        else:
            raise NoInternet("No internet!")

    def find_active_interface(self):
        interfaces = {}

        for iface in self.interfaces:
            interfaces[iface.name] = 10000

        output = shell_command("route -n")

        if output[2] == 0:
            for key in interfaces:
                location = output[0].find(key)
                if location != -1:
                    interfaces[key] = location
        else:
            raise RuntimeError('Error occured on "route -n" command!')

        # find interface has highest priority
        last_location = 10000
        high = None
        for key in interfaces:
            if interfaces[key] < last_location:
                last_location = interfaces[key]
                high = key

        return high

    def adjust_metric(self, interface, metric):
        """
        Function for adjusting interface metrics by using ifmetric tool
        """
        output = shell_command(f"sudo ifmetric {interface} {metric}")

        if output[2] == 0:
            return 0
        else:
            raise RuntimeError('Error occured on "route -n" command!')

    def check_connection_status(self):
        for iface in self.interfaces:
            if iface.if_type == InterfaceTypes.CELLULAR:
                iface.connection_status = self.modem.monitor.get("cellular_connection")
            else:
                try:
                    self.check_interface_health(iface.name)
                except:
                    iface.connection_status = False
                else:
                    iface.connection_status = True

    def get_interface_metrics(self):
        output = shell_command("ip route list")

        if output[2] != 0:
            raise RuntimeError('Error occured on "ip route list" command!')

        for line in output[0].splitlines():
            for iface in self.interfaces:
                if iface.name in line and "default" in line:
                    try:
                        metric = parse_output(line, "metric", " ")
                        iface.actual_metric = int(metric)
                    except Exception as error:
                        logger.warning("Interface metrics couldn't be read! %s", error)

    def get_interface_priority(self):
        for iface in self.interfaces:
            try:
                self.get_interface_metrics()
                iface.priority = int(iface.actual_metric/10)
            except Exception as error:
                logger.error("get_interface_priority() --> %s", error)

    def update_int_type_priorities(self):
        """
        Function for updating priority of the interface types if they are changed
        by configurator.
        """
        for if_type in interface_types.values():
            if if_type.name in conf.network_priority:
                if if_type.priority != conf.network_priority.get(if_type.name):
                    new_priority = conf.network_priority.get(if_type.name)
                    if_type.update_priority(new_priority)

                    # Remove configured priorities according to old config
                    for iface in self.configured_by_type:
                        if iface.if_type == if_type.name:
                            self.configured_by_type.remove(iface)

    def decide_metric_factors(self):
        """
        Function for deciding priority of the actual interfaces. This function
        supports assigning priority both by name and by type.
        """
        self.update_int_type_priorities()

        for iface in self.interfaces:
            if iface.name in conf.network_priority:
                iface.metric_factor = conf.network_priority.get(iface.name)
                if iface not in self.configured_by_name:
                    self.configured_by_name.append(iface)
            else:
                # remove interface from configured_by_name if it no longer have 
                # configuration by name in global conf dictionary
                if iface in self.configured_by_name:
                    self.configured_by_name.remove(iface)

                if_type = interface_types[iface.if_type]
                if iface not in self.configured_by_type:
                    try:
                        iface.metric_factor = if_type.add_child_interface(iface.name)
                    except Exception as error:
                        logger.error("decide_metric_factors() --> %s", error)
                    else:
                        self.configured_by_type.append(iface)
                else:
                    iface.metric_factor = if_type.child_int_table.get(iface.name)

        # remove child interface if it is not existed or moved
        for iface in self.configured_by_type:
            if iface not in self.interfaces or iface in self.configured_by_name:
                if_type = interface_types[iface.if_type]
                if_type.remove_child_interface(iface.name)
                self.configured_by_type.remove(iface)

    def adjust_priorities(self):
        """
        Function for adjusting priority of interfaces according to internet
        connection status and metric factor.
        """
        self.decide_metric_factors()
        for iface in self.interfaces:
            # action when connection status changes
            if not iface.connection_status:
                iface.desired_metric = LOWEST_PRIORTY_METRIC
            else:
                iface.desired_metric = iface.metric_factor * 10

            # do changes
            if iface.actual_metric != iface.desired_metric:
                try:
                    self.adjust_metric(iface.name, iface.desired_metric)
                except:
                    logger.error("Error occured changing metric : %s", iface.name)
                else:
                    logger.info("%s metric changed : %s", iface.name, iface.desired_metric)

    def create_monitoring_data(self):
        self.monitor.clear()
        for iface in self.interfaces:
            self.monitor[iface.name] = [
                iface.connection_status,
                iface.if_type,
                iface.priority
                ]
        # # Don't add interface types to monitor data
        # for iface_types in interface_types.values():
        #     self.monitor[iface_types.name] = [
        #         iface_types.priority
        #     ]

    def debug_routes(self):
        if conf.debug_mode and conf.verbose_mode:
            output = shell_command("route -n")

            if output[2] == 0:
                print("")
                print("*****************************************************************")
                print("[?] NETWORK MANAGER REPORT")
                print("---------------------------")
                print(output[0])
                print("*****************************************************************")
                print("")
            else:
                raise RuntimeError('Error occured on "route -n" command!')
