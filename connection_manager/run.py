#!/usr/bin/python3

from helpers.serial import send_at_com
from helpers.config import read_config
from helpers.logger import initialize_logger

from modules.configure_modem import configure_modem, detect_modem

logger = initialize_logger(True)

logger.info("Connection Manager is started...")

configure_modem()
