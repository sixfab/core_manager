import yaml
import os

from helpers.logger import initialize_logger

logger = initialize_logger()

CM_PATH = os.path.expanduser("~") + "/connection_manager/"
CONFIG_PATH = CM_PATH + "config.yaml"

def read_config():    
    try:
        with open(CONFIG_PATH) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data
    except Exception as e:
        print(e)
        return {}

