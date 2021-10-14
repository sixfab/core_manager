#!/usr/bin/python3

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import shell_command
from helpers.exceptions import NoInternet
from helpers.netiface import NetInterface
from cm import modem


LOWEST_PRIORTY_FACTOR = 100


def parse_output(string, header, end):
    header += " "
    header_size = len(header)
    index_of_data = string.find(header) + header_size
    end_of_data = index_of_data + string[index_of_data:].find(end)
    sig_data = string[index_of_data:end_of_data]
    return sig_data


class Network(object):

    # monitoring properties
    monitor = {}
    interfaces = []
    cellular_interfaces = []

    def __init__(self):
        pass

    def find_usable_interfaces(self):
        ifs = []
        output = shell_command("ip route list")

        if output[2] != 0:
            raise RuntimeError('Error occured on "ip route list" command!')

        for line in output[0].splitlines():
            try:
                dev = parse_output(line, "dev", " ")
                if dev not in ifs:
                    ifs.append(dev)
            except Exception as error:
                raise RuntimeError("Interface dev couldn't be read!") from error

        return ifs

    def create_interface(self, name):
        interface = NetInterface()
        interface.name = name
        self.interfaces.append(interface)

    def remove_interface(self, value):
        self.interfaces.remove(value)

    def check_interfaces(self):
        actual = []

        try:
            usables = self.find_usable_interfaces()
        except Exception as error:
            logger.error("find_usable_interfaces() --> %s", error)

        for interface in self.interfaces:
            actual.append(interface.name)

        for x in usables:
            if x not in actual:
                self.create_interface(x)

        for x in actual:
            if x not in usables:
                for y in self.interfaces:
                    if y.name == x:
                        self.remove_interface(y)

    def get_cellular_interface_name(self):
        output = shell_command("lshw -C Network")

        if output[2] == 0:
            networks = output[0].split("*-network:")

            for x in networks:
                if x.find("driver=cdc_ether") >= 0:
                    if_name = parse_output(x, "logical name:", "\n")
                    self.cellular_interfaces.append(if_name)

            return self.cellular_interfaces
        else:
            return []

    def check_interface_health(self, interface):

        health_check = f"ping -q -c 1 -s 8 -w {conf.other_ping_timeout} -I {interface} 8.8.8.8"
        output = shell_command(health_check)

        if output[2] == 0:
            pass
        else:
            raise NoInternet("No internet!")

    def find_active_interface(self):
        interfaces = {}

        for x in self.interfaces:
            interfaces[x.name] = 10000

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
        output = shell_command("sudo ifmetric " + str(interface) + " " + str(metric))

        if output[2] == 0:
            return 0
        else:
            raise RuntimeError('Error occured on "route -n" command!')

    def check_and_create_monitoring(self):
        self.monitor.clear()
        cellular_interfaces = []

        try:
            cellular_interfaces = self.get_cellular_interface_name()

            if cellular_interfaces == []:
                cellular_interfaces = conf.cellular_interfaces
        except:
            cellular_interfaces = conf.cellular_interfaces

        if modem.interface_name not in cellular_interfaces:
            modem.interface_name = cellular_interfaces[0]

        for x in self.interfaces:
            if x.name in cellular_interfaces:
                x.connection_status = modem.monitor.get("cellular_connection")
                self.monitor[x.name] = [x.connection_status, modem.monitor.get("cellular_latency")]
            else:
                try:
                    self.check_interface_health(x.name)
                except:
                    x.connection_status = False
                    self.monitor[x.name] = [False, 0]
                else:
                    x.connection_status = True
                    self.monitor[x.name] = [True, 0]

    def get_interface_metrics(self):
        output = shell_command("ip route list")

        if output[2] != 0:
            raise RuntimeError('Error occured on "ip route list" command!')

        for line in output[0].splitlines():
            for x in self.interfaces:
                if x.name in line and "default" in line:
                    try:
                        metric = parse_output(line, "metric", " ")
                        x.actual_metric = int(metric)
                    except Exception as error:
                        logger.warning("Interface metrics couldn't be read! %s", error)

    def adjust_priorities(self):
        default_metric_factor = 10

        for x in self.interfaces:
            x.metric_factor = conf.network_priority.get(x.name, default_metric_factor)

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
                return 0
            else:
                raise RuntimeError('Error occured on "route -n" command!')
