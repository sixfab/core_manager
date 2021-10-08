#!/usr/bin/python3


class DefaultVendor(object):
    name = "default"
    vid = "0000"

    interface_name = ""
    mode_status_command = ""
    ecm_mode_response = ""
    ecm_mode_setter_command = ""
    reboot_command = ""
    pdp_activate_command = ""
    pdp_status_command = ""
    ccid_command = ""


class DefaultProduct(DefaultVendor):
    product_name = "default"
    pid = "0000"

    def __init__(self, product_name, pid, vendor_object):
        self.product_name = product_name
        self.pid = pid
        self.name = vendor_object.name
        self.vid = vendor_object.vid
        self.interface_name = vendor_object.interface_name
        self.mode_status_command = vendor_object.mode_status_command
        self.ecm_mode_setter_command = vendor_object.ecm_mode_setter_command
        self.ecm_mode_response = vendor_object.ecm_mode_response
        self.reboot_command = vendor_object.reboot_command
        self.pdp_activate_command = vendor_object.pdp_activate_command
        self.pdp_status_command = vendor_object.pdp_status_command
        self.ccid_command = vendor_object.ccid_command
    

class Quectel(DefaultVendor):
    name ="Quectel"
    vid = "2c7c"

    interface_name = "usb0"
    mode_status_command = "AT+QCFG=\"usbnet\""
    reboot_command = "AT+CFUN=1,1"
    pdp_activate_command = "AT"
    pdp_status_command = "AT+CGACT?"
    ecm_mode_setter_command = "AT+QCFG=\"usbnet\",1"
    ecm_mode_response = "\"usbnet\",1"
    ccid_command = "AT+ICCID"


class Telit(object):
    name ="Telit"
    vid = "1bc7"

    interface_name = "wwan0"
    mode_status_command = "AT#USBCFG?"
    reboot_command = "AT#REBOOT"
    pdp_activate_command = "AT#ECM=1,0"
    pdp_status_command = "AT#ECM?"
    ecm_mode_setter_command = "AT#USBCFG=4"
    ecm_mode_response = "4"
    ccid_command = "AT+ICCID"


class Thales(object):
    name ="Thales/Cinterion"
    vid = "1e2d"

    interface_name = "eth1"
    mode_status_command = "AT^SSRVSET=\"actSrvSet\""
    reboot_command = "AT+CFUN=1,1"
    pdp_activate_command = "AT^SWWAN=1,1"
    pdp_status_command = "AT^SWWAN?"
    ecm_mode_setter_command = "AT^SSRVSET=\"actSrvSet\",1"
    ecm_mode_response = "^SSRVSET: 1\n"
    ccid_command = "AT+CCID"


# Products
# Vendor: Quectel
quectel_default = DefaultProduct("Unknown-Quectel-Modem", "ffff", Quectel())
ec25 = DefaultProduct("EC25", "0125", Quectel())
ec21 = DefaultProduct("EC21", "0121", Quectel())

# Vendor: Telit
telit_default = DefaultProduct("Unknown-Telit-Modem", "ffff", Telit())
le910cx_comp_1 = DefaultProduct("LE910CX-Series", "1201", Telit())
le910cx_comp_2 = DefaultProduct("LE910CX-Series", "1206", Telit())

me910c1_ww_comp_1 = DefaultProduct("ME910C1-WW", "1101", Telit())
me910c1_ww_comp_1.ecm_mode_setter_command = "AT#USBCFG=3"
me910c1_ww_comp_1.ecm_mode_response = "3"

me910c1_ww_comp_2 = DefaultProduct("ME910C1-WW", "1102", Telit())
me910c1_ww_comp_2.ecm_mode_setter_command = "AT#USBCFG=3"
me910c1_ww_comp_2.ecm_mode_response = "3"

# Vendor: Thales
thales_default = DefaultProduct("Unknown-Thales-Modem", "ffff", Thales())
plsx3_comp_1 = DefaultProduct("PLSX3-Series", "0069", Thales())
plsx3_comp_2 = DefaultProduct("PLSX3-Series", "006f", Thales())


# default modules for vendors
default_modules = {
    "2c7c": quectel_default,
    "1bc7" : telit_default,
    "1e2d" : thales_default,
}


# Supported modules
modules = {
    ec25,
    ec21,
    le910cx_comp_1,
    le910cx_comp_2,
    me910c1_ww_comp_1,
    me910c1_ww_comp_2,
    plsx3_comp_1,
    plsx3_comp_2,
}
