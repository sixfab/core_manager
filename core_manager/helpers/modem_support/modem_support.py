from helpers.modem_support.default import BaseModule
from helpers.modem_support.quectel import Quectel
from helpers.modem_support.telit import Telit
from helpers.modem_support.thales import Thales

# Products
# Vendor: Quectel
quectel_default = Quectel("Unknown-Quectel-Modem", "ffff")
ec25 = Quectel("EC25", "0125")
ec21 = Quectel("EC21", "0121")

# Vendor: Telit
telit_default = BaseModule("Unknown-Telit-Modem", "ffff")
le910cx_comp_1 = BaseModule("LE910CX-Series", "1201")
le910cx_comp_2 = BaseModule("LE910CX-Series", "1206")

le910cx_wwx_comp0 = BaseModule("LE910CX-Series", "1031")
le910cx_wwx_comp0.ecm_mode_setter_command = "AT#USBCFG=1"
le910cx_wwx_comp0.ecm_mode_response = "0"

le910cx_wwx_comp1 = BaseModule("LE910CX-Series", "1033")
le910cx_wwx_comp1.ecm_mode_setter_command = "AT#USBCFG=1"
le910cx_wwx_comp1.ecm_mode_response = "1"

me910c1_ww_comp_1 = BaseModule("ME910C1-WW", "1101")
me910c1_ww_comp_1.ecm_mode_setter_command = "AT#USBCFG=3"
me910c1_ww_comp_1.ecm_mode_response = "3"

me910c1_ww_comp_2 = BaseModule("ME910C1-WW", "1102")
me910c1_ww_comp_2.ecm_mode_setter_command = "AT#USBCFG=3"
me910c1_ww_comp_2.ecm_mode_response = "3"

# Vendor: Thales
thales_default = BaseModule("Unknown-Thales-Modem", "ffff")
plsx3_comp_1 = BaseModule("PLSX3-Series", "0069")
plsx3_comp_2 = BaseModule("PLSX3-Series", "006f")


# default modules for vendors
default_modules = {
    "2c7c": quectel_default,
    "1bc7" : telit_default,
    "1e2d" : thales_default,
}


# Supported modules
modules = [
    ec25,
    ec21,
    le910cx_comp_1,
    le910cx_comp_2,
    le910cx_wwx_comp0,
    le910cx_wwx_comp1,
    me910c1_ww_comp_1,
    me910c1_ww_comp_2,
    plsx3_comp_1,
    plsx3_comp_2,
]
