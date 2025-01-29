from subprocess import run, check_output, getstatusoutput, CalledProcessError
from helpers.logger import logger
import time


class SBC:
    name = ""
    os = ""

    def __init__(self, name, os, disable_pin, chip_name="gpiochip0"):
        self.name = name
        self.os = os
        self.disable_pin = disable_pin
        self.chip_name = chip_name

    def gpio_check(self, pin):
        # gpiod CLI does not need initialization, so we just check if the GPIO is accessible.
        pin_name = f"{self.chip_name} {pin}"

        try:
            status, output = getstatusoutput(f"gpioinfo {self.chip_name}")
            if status != 0 or f"line   {pin}" not in output:
                logger.warning(f"GPIO {pin_name} not accessible or not available.")
        except Exception as e:
            logger.exception(f"gpio_check --> {e}")

    def modem_hard_reset(self):
        self.gpio_check(self.disable_pin)

        self.kill_gpioset()
        self.modem_power_disable()
        time.sleep(2)
        self.kill_gpioset()
        self.modem_power_enable()
        self.kill_gpioset()
        
    def modem_power_enable(self):
        comm = f"gpioset --mode=wait {self.chip_name} {self.disable_pin}=0 &"
        try:
            check_output(comm, shell=True)
        except Exception as e:
            logger.exception(f"modem_power_enable --> {e}")

    def modem_power_disable(self):

        comm = f"gpioset --mode=wait {self.chip_name} {self.disable_pin}=1 &"
        try:
            check_output(comm, shell=True)
        except Exception as e:
            logger.exception(f"modem_power_disable --> {e}")

    def kill_gpioset():
        comm = 'pkill -9 -f "gpioset --mode=wait"'
        try:
            result = run(comm, shell=True, check=False)
            if result.returncode == 0:
                logger.info("Successfully killed gpioset process.")
            else:
                logger.warning("No running gpioset process found to kill.")
        except CalledProcessError as e:
            logger.exception(f"kill_gpioset --> {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in kill_gpioset --> {e}")
            
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
