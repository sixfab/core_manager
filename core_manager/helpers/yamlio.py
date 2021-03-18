#!/usr/bin/python3

import yaml
import os.path

ENV_PATH = "/opt/sixfab/.env.yaml"
TEMP_FOLDER_PATH =  os.path.expanduser("~")
CONNECT_FOLDER_PATH = TEMP_FOLDER_PATH + "/.core/"
DIAG_FOLDER_PATH = CONNECT_FOLDER_PATH + "diagnostics/"
CONFIG_FOLDER_PATH = CONNECT_FOLDER_PATH + "configs/"

CONFIG_PATH = CONFIG_FOLDER_PATH + "config.yaml"
SYSTEM_PATH = CONNECT_FOLDER_PATH + "system.yaml"
MONITOR_PATH = CONNECT_FOLDER_PATH + "monitor.yaml"

if not os.path.exists(TEMP_FOLDER_PATH):
    os.mkdir(TEMP_FOLDER_PATH)

if not os.path.exists(CONNECT_FOLDER_PATH):
    os.mkdir(CONNECT_FOLDER_PATH)

if not os.path.exists(DIAG_FOLDER_PATH):
    os.mkdir(DIAG_FOLDER_PATH)

if not os.path.exists(CONFIG_FOLDER_PATH):
    os.mkdir(CONFIG_FOLDER_PATH)


def read_yaml_all(file):
    with open(file) as f:
        data = yaml.safe_load(f)
        return data

def write_yaml_all(file, items, clear = True):
    if clear == True:
        with open(file, 'w') as f:
            yaml.dump(items, f, default_flow_style=False)
    else:
        with open(file, 'a') as f:
            yaml.dump(items, f, default_flow_style=False)

