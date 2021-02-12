#!/usr/bin/python3

import subprocess
from .config_parser import logger 

def shell_command(command):
    try:
        com = command.split(" ")
        cp = subprocess.run(com, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        logger.error("Message: " + str(e))
        return ("", "", 1)
    else:
        return (cp.stdout, cp.stderr, cp.returncode)


def send_at_com(command, desired):
    try:
        cp = subprocess.run(["atcom", command, "--find", desired], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        logger.error("Message: " + str(e))
        return ("", "", 1)
    else:
        if cp.returncode == 0:
            return (cp.stdout, cp.stderr, cp.returncode)
        else:
            return ("", "", 1) 