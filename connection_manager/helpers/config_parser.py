
from helpers.yamlio import *
from helpers.logger import initialize_logger


config = {}
system_info = {} 

try:
    config = read_yaml_all(CONFIG_PATH)
except Exception as e:
    print(e)

try:
    system_info = read_yaml_all(SYSTEM_PATH)
except Exception as e:
    print(e)

VERBOSE_MODE = config.get("verbose_mode", False)
DEBUG = config.get("debug_mode", False)
APN = config.get("apn", "super")

logger = initialize_logger(DEBUG)


