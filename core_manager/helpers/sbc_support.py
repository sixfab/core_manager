import subprocess
import time
import os
import signal
from helpers.logger import logger


class SBC:
    name = ""
    os = ""

    def __init__(self, name, os, disable_pin, chip_name="gpiochip0"):
        self.name = name
        self.os = os
        self.disable_pin = disable_pin
        self.chip_name = chip_name
        self.process = None

    def gpio_check(self):
        # Check if the GPIO is accessible using gpiod CLI.
        pin_name = f"{self.chip_name} {self.disable_pin}"
        try:
            status, output = subprocess.getstatusoutput(f"gpioinfo {self.chip_name}")
            if status != 0 or f"{self.disable_pin}" not in output:
                logger.warning(f"GPIO {pin_name} not accessible or not available.")
        except Exception as e:
            logger.exception(f"gpio_check --> {e}")

    def modem_power_enable(self):
        # Set GPIO LOW (Enable modem) and wait 2 seconds before killing gpioset.
        comm = f"gpioset --mode=signal {self.chip_name} {self.disable_pin}=0"
        try:
            self.process = subprocess.Popen(comm, shell=True, preexec_fn=os.setsid)  # Run gpioset in the background
            logger.info("Modem power enabled (GPIO LOW).")
            time.sleep(2)
            self.kill_gpioset()
        except Exception as e:
            logger.exception(f"modem_power_enable --> {e}")

    def modem_power_disable(self):
        # Set GPIO HIGH (Disable modem) and wait 2 seconds before killing gpioset.
        comm = f"gpioset --mode=signal {self.chip_name} {self.disable_pin}=1"
        try:
            self.process = subprocess.Popen(comm, shell=True, preexec_fn=os.setsid)  # Run gpioset in the background
            logger.info("Modem power disabled (GPIO HIGH).")
            time.sleep(2)
            self.kill_gpioset()
        except Exception as e:
            logger.exception(f"modem_power_disable --> {e}")

    def kill_gpioset(self):
        # Kill the running gpioset process.
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                logger.info("Successfully killed gpioset process.")
            except ProcessLookupError:
                logger.info("No running gpioset process found to kill.")
            except Exception as e:
                logger.exception(f"kill_gpioset --> {e}")
        else:
            logger.info("No process stored to terminate.")

# SBC configurations for different boards
rpi4_raspbian = SBC("Raspberry Pi 4", "Raspberry Pi OS (Raspbian)", 26)  # Use BCM pin number on Raspberry Pi
jetson_nano_ubuntu = SBC("Nvidia Jetson Nano", "Ubuntu", 194)  # GPIO pin on Jetson Nano
rpi5_raspbian = SBC("Raspberry Pi 5", "Raspberry Pi OS (Raspbian)", 26)  # Use BCM pin number on Raspberry Pi

# Supported SBCs mapping
supported_sbcs = {
    "rpi4": rpi4_raspbian,
    "RaspberryPi4": rpi4_raspbian,
    "Jetson": jetson_nano_ubuntu,
    "rpi5": rpi5_raspbian,
}
