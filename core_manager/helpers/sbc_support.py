
class SBC():

    name =""
    os = ""

    def __init__(self, name, os):
        self.name = name
        self.os = os


    def modem_power_enable(self):
        pass


    def modem_power_disable(self):
        pass


rpi4_raspbian = SBC("Raspberry Pi 4", "Raspberry Pi OS (Raspbian)")
jetson_nano_ubuntu = SBC("Nvidia Jetson Nano", "Ubuntu")

supported_sbcs = [
    rpi4_raspbian, 
    jetson_nano_ubuntu
    ]
