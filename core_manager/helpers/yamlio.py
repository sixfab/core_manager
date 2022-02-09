import os.path
import yaml


ENV_PATH = "/opt/sixfab/.env.yaml"
TEMP_FOLDER_PATH = os.path.expanduser("~")
CONNECT_FOLDER_PATH = TEMP_FOLDER_PATH + "/.core/"
DIAG_FOLDER_PATH = CONNECT_FOLDER_PATH + "diagnostics/"
CONFIG_FOLDER_PATH = CONNECT_FOLDER_PATH + "configs/"

CONFIG_PATH = CONFIG_FOLDER_PATH + "config.yaml"
SYSTEM_PATH = CONNECT_FOLDER_PATH + "system.yaml"
MONITOR_PATH = CONNECT_FOLDER_PATH + "monitor.yaml"
GEOLOCATION_PATH = CONNECT_FOLDER_PATH + "geolocation.yaml"

if not os.path.exists(TEMP_FOLDER_PATH):
    os.mkdir(TEMP_FOLDER_PATH)

if not os.path.exists(CONNECT_FOLDER_PATH):
    os.mkdir(CONNECT_FOLDER_PATH)

if not os.path.exists(DIAG_FOLDER_PATH):
    os.mkdir(DIAG_FOLDER_PATH)

if not os.path.exists(CONFIG_FOLDER_PATH):
    os.mkdir(CONFIG_FOLDER_PATH)


def read_yaml_all(file):
    with open(file) as file_object:
        data = yaml.safe_load(file_object)
        return data or {}


def write_yaml_all(file, items, clear=True):
    if clear:
        with open(file, "w") as file_object:
            yaml.dump(items, file_object, default_flow_style=False)
    else:
        with open(file, "a") as file_object:
            yaml.dump(items, file_object, default_flow_style=False)
