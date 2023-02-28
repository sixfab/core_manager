import os.path

from helpers.yamlio import read_yaml_all, write_yaml_all, CONFIG_PATH
from helpers.config import Config, configs_showed_at_frontend


config = {}
old_config = {}
conf = Config()


def get_configs():

    if os.path.isfile(CONFIG_PATH):
        try:
            config.update(read_yaml_all(CONFIG_PATH))
        except Exception as error:
            print(str(error))
    else:
        print("Config file doesn't exist! Restoring default configs...")
        conf.restore_defaults()
        config.update({})
        old_config.update(config)

        try:
            print("Creating config.yaml with default configs...")

            default_conf = {}
            for item in vars(conf):
                if item in configs_showed_at_frontend:
                    default_conf[item] = conf.__getattribute__(item)

            write_yaml_all(CONFIG_PATH, default_conf)
        except Exception as error:
            print(str(error))

        return conf

    if config == old_config:
        return conf

    conf.set_verbose_mode_config(config.get("verbose_mode"))
    conf.set_debug_mode_config(config.get("debug_mode"))
    conf.set_acceptable_apns_config(config.get("acceptable_apns"))
    conf.set_apn_config(config.get("apn"))
    conf.set_ping_timeout_config(config.get("ping_timeout"))
    conf.set_other_ping_timeout_config(config.get("other_ping_timeout"))
    conf.set_check_internet_interval_config(config.get("check_internet_interval"))
    conf.set_send_monitoring_data_interval_config(config.get("send_monitoring_data_interval"))
    conf.set_network_priority_config(config.get("network_priority"))
    conf.set_cellular_interfaces_config(config.get("cellular_interfaces"))
    conf.set_logger_level_config(config.get("logger_level"))
    conf.set_sbc_config()
    conf.set_network_interface_exceptions_config(config.get("network_interface_exceptions"))

    conf.config_changed = True
    old_config.update(config)
    return conf


conf.update_config(get_configs())
conf.config_changed = False
