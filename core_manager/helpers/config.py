#!/usr/bin/python3

import os.path

from helpers.yamlio import read_yaml_all, ENV_PATH, CONFIG_PATH

env = {}
core_env = {}

# Check the .env.yaml file exist.
if os.path.isfile(ENV_PATH):
    try:
        env = read_yaml_all(ENV_PATH)
    except Exception as e:
        print(str(e))
    else:
        core_env = env.get("core", {})
else:
    print(".env.yaml file doesn't exist!")


class Config(object):
    
    reload_required = True

    default_config = {
        "apn" : core_env.get("apn", "super"),
        "debug_mode": False,
        "verbose_mode": False,
        "check_internet_interval": 60,
        "send_monitoring_data_interval": 60,
        "ping_timeout": 9,
        "other_ping_timeout": 3,
        "network_priority": { "eth0" : 1, "wlan0" : 2, "wwan0" : 3, "usb0": 4},
        "cellular_interfaces": ["wwan0", "usb0"]  
    }

    acceptible_apns = ["super", "de1.super", "sg1.super"]
    
    apn = None
    debug_mode = None 
    verbose_mode = None
    check_internet_interval = None
    send_monitoring_data_interval = None
    ping_timeout = None
    other_ping_timeout = None
    network_priority = None
    cellular_interfaces = None


    def __init__(self):
        pass

    
    def restore_defaults(self):
        self.apn = self.default_config.get("apn")
        self.debug_mode = self.default_config.get("debug_mode")
        self.verbose_mode = self.default_config.get("verbose_mode")
        self.check_internet_interval = self.default_config.get("check_internet_interval")
        self.send_monitoring_data_interval = self.default_config.get("send_monitoring_data_interval")
        self.ping_timeout = self.default_config.get("ping_timeout")
        self.other_ping_timeout = self.default_config.get("other_ping_timeout")
        self.network_priority = self.default_config.get("network_priority")
        self.cellular_interfaces = self.default_config.get("cellular_interfaces")


    def is_reload_required(self):
        return self.reload_required
    
    
    def get_apn_config(self):
        return self.apn


    def set_apn_config(self, value):
        if value:
            if value in self.acceptible_apns:
                self.apn = value
            else:
                self.apn = self.default_config.get("apn")
        else:
            self.apn = self.default_config.get("apn")

    
    def get_debug_mode_config(self):
        return self.debug_mode


    def set_debug_mode_config(self, value):
        if type(value) is bool:
            self.debug_mode = value
        else:
            self.debug_mode = self.default_config.get("debug_mode")
    

    def get_verbose_mode_config(self):
        return self.verbose_mode


    def set_verbose_mode_config(self, value):
        if type(value) is bool:
            self.verbose_mode = value
        else:
            self.verbose_mode = self.default_config.get("verbose_mode")


    def get_check_internet_interval_config(self):
        return self.check_internet_interval

    
    def set_check_internet_interval_config(self, value):
        if value:
            if (value >= 10) and (value <= 3600):
                self.check_internet_interval = value
            else:
                self.check_internet_interval = self.default_config.get("check_internet_interval")
        else:
            self.check_internet_interval = self.default_config.get("check_internet_interval")


    def get_send_monitoring_data_interval_config(self):
        return self.send_monitoring_data_interval

    
    def set_send_monitoring_data_interval_config(self, value):
        if value:
            if (value >= 10) and (value <= 3600):
                self.send_monitoring_data_interval = value
            else:
                self.send_monitoring_data_interval = self.default_config.get("send_monitoring_data_interval")
        else:
            self.send_monitoring_data_interval = self.default_config.get("send_monitoring_data_interval")


    def get_ping_timeout_config(self):
        return self.ping_timeout


    def set_ping_timeout_config(self, value):
        if value:
            if (value >= 1) and (value <= 60):
                self.ping_timeout = value
            else:
                self.ping_timeout = self.default_config.get("ping_timeout")
        else:
            self.ping_timeout = self.default_config.get("ping_timeout")

    
    def get_other_ping_timeout_config(self):
        return self.other_ping_timeout


    def set_other_ping_timeout_config(self, value):
        if value:
            if (value >= 1) and (value <= 60):
                self.other_ping_timeout = value
            else:
                self.other_ping_timeout = self.default_config.get("other_ping_timeout")
        else:
            self.other_ping_timeout = self.default_config.get("other_ping_timeout") 

    
    def get_network_priority_config(self):
        return self.network_priority


    def set_network_priority_config(self, value):
        if type(value) is dict:
            self.network_priority = value
        else:
            self.network_priority = self.default_config.get("network_priority")

    
    def get_cellular_interfaces_config(self):
        return self.cellular_interfaces


    def set_cellular_interfaces_config(self, value):
        if type(value) is dict:
            self.cellular_interfaces = value
        else:
            self.cellular_interfaces = self.default_config.get("cellular_interfaces")



