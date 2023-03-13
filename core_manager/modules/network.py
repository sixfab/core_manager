#!/usr/bin/python3

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import shell_command
from helpers.exceptions import NoInternet
from helpers.netiface import NetInterface

LOWEST_PRIORTY_FACTOR = 100

class InterfaceTypes:
    CELLULAR = 'C'
    ETHERNET = 'E'
    WIFI = 'W'


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
    cellular_interfaces = []

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

    def get_interface_type(self):
        output = shell_command("lshw -C Network")

        if output[2] == 0:
            networks = output[0].split("*-network")

            for network in networks:
                for interface in self.interfaces:
                    if network.find(interface.name) >= 0:
                        if network.find("Ethernet interface") >= 0:
                            if network.find("driver=cdc_ether") >= 0:
                                interface.if_type=InterfaceTypes.CELLULAR
                                self.modem.interface_name = interface.name
                            else:
                                interface.if_type=InterfaceTypes.ETHERNET
                        elif network.find("Wireless interface") >= 0:
                            interface.if_type=InterfaceTypes.WIFI
        else:
            logger.warning("Error occured on --> get_interface_type")

    def get_interface_priority(self):
        try:
            usables = self.find_usable_interfaces()
        except Exception as error:
            logger.error("find_usable_interfaces() --> %s", error)

        for if_name in usables:
            for interface in self.interfaces:
                if if_name == interface.name:
                    priority = usables.index(if_name)+1
                    interface.priority = priority

    def check_interface_health(self, interface):

        health_check = f"ping -q -c 1 -s 8 -w {conf.other_ping_timeout} -I {interface} 8.8.8.8"
        output = shell_command(health_check)

        if output[2] == 0:
            pass
        else:
            raise NoInternet("No internet!")

    def find_active_interface(self):
        interfaces = {}

        for ifs in self.interfaces:
            interfaces[ifs.name] = 10000

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
        output = shell_command(f"sudo ifmetric {interface} {metric}")

        if output[2] == 0:
            return 0
        else:
            raise RuntimeError('Error occured on "route -n" command!')

    def check_and_create_monitoring(self):
        self.monitor.clear()
        self.get_interface_type()
        self.get_interface_priority()

        for ifs in self.interfaces:
            if ifs.if_type == InterfaceTypes.CELLULAR:
                ifs.connection_status = self.modem.monitor.get("cellular_connection")

                self.monitor[ifs.name] = [ifs.connection_status, ifs.if_type, ifs.priority]
            else:
                try:
                    self.check_interface_health(ifs.name)
                except:
                    ifs.connection_status = False
                    self.monitor[ifs.name] = [False, ifs.if_type, ifs.priority]
                else:
                    ifs.connection_status = True
                    self.monitor[ifs.name] = [True, ifs.if_type, ifs.priority]

    def get_interface_metrics(self):
        output = shell_command("ip route list")

        if output[2] != 0:
            raise RuntimeError('Error occured on "ip route list" command!')

        for line in output[0].splitlines():
            for ifs in self.interfaces:
                if ifs.name in line and "default" in line:
                    try:
                        metric = parse_output(line, "metric", " ")
                        ifs.actual_metric = int(metric)
                    except Exception as error:
                        logger.warning("Interface metrics couldn't be read! %s", error)

    def adjust_priorities(self):
        default_metric_factor = 10

        for ifs in self.interfaces:
            ifs.metric_factor = conf.network_priority.get(ifs.name, default_metric_factor)

        for iface in self.interfaces:
            # action when connection status changes
            if not iface.connection_status:
                iface.desired_metric = LOWEST_PRIORTY_FACTOR * 100
            else:
                iface.desired_metric = iface.metric_factor * 100

            # do changes
            if iface.actual_metric != iface.desired_metric:
                try:
                    self.adjust_metric(iface.name, iface.desired_metric)
                except:
                    logger.error("Error occured changing metric : %s", iface.name)
                else:
                    logger.info("%s metric changed : %s", iface.name, iface.desired_metric)

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
