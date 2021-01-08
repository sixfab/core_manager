import yaml
import os

from helpers.logger import initialize_logger

logger = initialize_logger(True)

CM_PATH = os.path.expanduser("~") + "/connection_manager/"
CONFIG_PATH = CM_PATH + "config.yaml"
SYSTEM_PATH = CM_PATH + "system.yaml"

def read_config():    
    try:
        with open(CONFIG_PATH) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data
    except Exception as e:
        print(e)
        return {}


def save_system_id(items, clear=False):
    try:
        if clear == True:
            with open(SYSTEM_PATH, 'w') as sys_file:
                yaml.dump(items, sys_file, default_flow_style=False, explicit_start=True)
        else:
            with open(SYSTEM_PATH, 'a') as sys_file:
                yaml.dump(items, sys_file, default_flow_style=False, explicit_start=True)
    except Exception as e:
        print(e)
        return 1
    else:
        return 0
