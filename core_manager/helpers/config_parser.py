import os.path

from helpers.yamlio import read_yaml_all, write_yaml_all, ENV_PATH, CONFIG_PATH
from helpers.logger import initialize_logger

env = {}
config = {}
connect_dict = {}

# Check the .env.yaml file exist.
if os.path.isfile(ENV_PATH):
    try:
        env = read_yaml_all(ENV_PATH)
    except Exception as e:
        print(e) # debug
    else:
        connect_dict = env.get("core", {})
else:
    print(".env.yaml file doesn't exist!")

# default configurations
default_config = {
    "apn" : connect_dict.get("apn", "super"),

    "debug_mode" : False,
    "verbose_mode" : False,

    "check_internet_interval" : 60,
    "send_monitoring_data_interval" : 60,
    "network_manager_interval" : 30,

    "cell_ping_timeout" : 9,
    "other_ping_timeout" : 3,

    "network_priority" : { "eth0" : 1, "wlan0" : 2, "wwan0" : 3, "usb0": 4}   
}

# Check the config file exist.
if os.path.isfile(CONFIG_PATH):
    try:
        config = read_yaml_all(CONFIG_PATH)
    except Exception as e:
        print(e) # debug
else:
    print("Config file doesn't exist! Restoring default configs...") # debug
    config = default_config

VERBOSE_MODE = config.get("verbose_mode", default_config.get("verbose_mode"))
DEBUG = config.get("debug_mode", default_config.get("debug_mode"))
APN = config.get("apn", default_config.get("apn"))
PING_TIMEOUT = config.get("cell_ping_timeout", default_config.get("cell_ping_timeout"))
OTHER_PING_TIMEOUT = config.get("other_ping_timeout", default_config.get("other_ping_timeout"))
INTERVAL_CHECK_INTERNET = config.get("check_internet_interval", default_config.get("check_internet_interval"))
INTERVAL_SEND_MONITOR = config.get("send_monitoring_data_interval", default_config.get("send_monitoring_data_interval"))
INTERVAL_MANAGE_NETWORK = config.get("send_monitoring_data_interval", default_config.get("send_monitoring_data_interval"))
NETWORK_PRIORTY = config.get("network_priority", default_config.get("network_priority"))

logger = initialize_logger(DEBUG)

