
from helpers.yamlio import *
from helpers.logger import initialize_logger

# default configurations
default_config = {
    "apn" : "super",

    "debug_mode" : True,
    "verbose_mode" : True,

    "check_internet_interval" : 10,
    "check_config_interval" : 60,
    "send_monitoring_data_interval" : 60,

    "ping_timeout" : 9,
}

config = {}

# Check the config file exist.
if os.path.isfile(CONFIG_PATH):
    pass
else:
    print("Config file doesn't exist! Restoring default configs...")
    try:
        config = default_config
        write_yaml_all(CONFIG_PATH, config)
    except Exception as e:
        print("Error occured when default config file is creating!")

try:
    config = read_yaml_all(CONFIG_PATH)
except Exception as e:
    print(e)

VERBOSE_MODE = config.get("verbose_mode", False)
DEBUG = config.get("debug_mode", False)
APN = config.get("apn", "super")
PING_TIMEOUT = config.get("ping_timeout", 9)

logger = initialize_logger(DEBUG)


