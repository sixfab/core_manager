#!/usr/bin/python3

import subprocess
from helpers.logger import logger


def shell_command(command):
    try:
        com = command.split(" ")
        cp = subprocess.run(
            com, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except Exception as error:
        logger.error("Message: %s", error)
        return ("", "", 1)
    else:
        return (cp.stdout, cp.stderr, cp.returncode)


def send_at_com(command, desired):
    try:
        cp = subprocess.run(
            ["atcom", command, "--find", desired],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as error:
        logger.error("Message: %s", error)
        return ("", "", 1)
    else:
        if cp.returncode == 0:
            return (cp.stdout, cp.stderr, cp.returncode)
        else:
            return ("", "", 1)


def parse_output(output, header, end):
    header += " "
    header_size = len(header)
    index_of_data = output[0].find(header) + header_size
    end_of_data = index_of_data + output[0][index_of_data:].find(end)
    sig_data = output[0][index_of_data:end_of_data]
    return sig_data
