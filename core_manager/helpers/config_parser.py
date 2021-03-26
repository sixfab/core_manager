import os.path

from helpers.yamlio import read_yaml_all, CONFIG_PATH
from helpers.logger import initialize_logger
from helpers.config import Config


config = {}
conf = None

def get_configs():
    global conf
    
    if conf:
        if not conf.reload_required:
            print("SAME")
            return conf
        else:
            print("reload is req: ", conf.reload_required)
    
    conf = Config()

    # Check the config file exist.
    if os.path.isfile(CONFIG_PATH):
        try:
            config = read_yaml_all(CONFIG_PATH)
        except Exception as e:
            print(str(e))
    else:
        print("Config file doesn't exist! Restoring default configs...")
        conf.restore_defaults()
        conf.reload_required = False
        return conf
    
    conf.set_verbose_mode_config(config.get("verbose_mode"))
    conf.set_debug_mode_config(config.get("debug_mode"))
    conf.set_apn_config(config.get("apn"))
    conf.set_ping_timeout_config(config.get("ping_timeout"))
    conf.set_other_ping_timeout_config(config.get("other_ping_timeout"))
    conf.set_check_internet_interval_config(config.get("check_internet_interval"))
    conf.set_send_monitoring_data_interval_config(config.get("send_monitoring_data_interval"))
    conf.set_network_priority_config(config.get("network_priority"))
    conf.set_cellular_interfaces_config(config.get("cellular_interfaces"))
    
    conf.reload_required = False
    print("reload is req: ", conf.reload_required)
    return conf


conf = get_configs()
logger = initialize_logger(conf.get_debug_mode_config())


