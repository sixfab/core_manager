
import time

from subprocess import check_output, getstatusoutput
from helpers.logger import logger


class SBC():

    name =""
    os = ""

    def __init__(self, name, os, disable_pin):
        self.name = name
        self.os = os
        self.disable_pin = disable_pin


    def gpio_init(self, pin):
        pin_name = "gpio" + str(pin)

        status = getstatusoutput("ls /sys/class/gpio/" + pin_name)[0]

        if status != 0:
            comm = "echo " + str(pin) + " > /sys/class/gpio/export"

            try:
                check_output(comm, shell=True)
            except:
                logger.warning("gpio_init --> export gpio")

            time.sleep(0.2)
            
        comm = "echo out > /sys/class/gpio/gpio" + str(pin) + "/direction"
        try:
            check_output(comm, shell=True)
        except:
            logger.exception("gpio_init -->")
        
        time.sleep(0.1)


    def gpio_del(self):
        comm = "echo " + str(self.disable_pin) + " > /sys/class/gpio/unexport"
        try:
            check_output(comm, shell=True)
        except:
            logger.warning("gpio_del --> unexport gpio")


    def modem_power_enable(self):
        self.gpio_init(self.disable_pin)

        comm = "echo 0 > /sys/class/gpio/gpio" + str(self.disable_pin) + "/value"
        try:
            check_output(comm, shell=True)
        except:
            logger.exception("modem_power_enable -->")



    def modem_power_disable(self):
        self.gpio_init(self.disable_pin)
        
        comm = "echo 1 > /sys/class/gpio/gpio" + str(self.disable_pin) + "/value"
        try:
            check_output(comm, shell=True)
        except:
            logger.exception("modem_power_disable -->")



rpi4_raspbian = SBC("Raspberry Pi 4", "Raspberry Pi OS (Raspbian)", 26)  # Use BCM on Raspberry Pi
jetson_nano_ubuntu = SBC("Nvidia Jetson Nano", "Ubuntu", 12)  # Use SYSFS on Jetson   

supported_sbcs = {
        "rpi4": rpi4_raspbian,
        "jetson_nano_ubuntu": jetson_nano_ubuntu,
    } 
