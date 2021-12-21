from helpers.modem_support.default import DefaultModule
from helpers.modem_support.quectel import Quectel
from helpers.modem_support.telit import Telit
from helpers.modem_support.thales import Thales

# Products
# Vendor: Quectel
quectel_default = DefaultModule("Unknown-Quectel-Modem", "ffff", Quectel())
ec25 = DefaultModule("EC25", "0125", Quectel())
ec21 = DefaultModule("EC21", "0121", Quectel())

# Vendor: Telit
telit_default = DefaultModule("Unknown-Telit-Modem", "ffff", Telit())
le910cx_comp_1 = DefaultModule("LE910CX-Series", "1201", Telit())
le910cx_comp_2 = DefaultModule("LE910CX-Series", "1206", Telit())

le910cx_wwx_comp0 = DefaultModule("LE910CX-Series", "1031", Telit())
le910cx_wwx_comp0.ecm_mode_setter_command = "AT#USBCFG=1"
le910cx_wwx_comp0.ecm_mode_response = "1"

le910cx_wwx_comp1 = DefaultModule("LE910CX-Series", "1033", Telit())
le910cx_wwx_comp1.ecm_mode_setter_command = "AT#USBCFG=1"
le910cx_wwx_comp1.ecm_mode_response = "1"

me910c1_ww_comp_1 = DefaultModule("ME910C1-WW", "1101", Telit())
me910c1_ww_comp_1.ecm_mode_setter_command = "AT#USBCFG=3"
me910c1_ww_comp_1.ecm_mode_response = "3"

me910c1_ww_comp_2 = DefaultModule("ME910C1-WW", "1102", Telit())
me910c1_ww_comp_2.ecm_mode_setter_command = "AT#USBCFG=3"
me910c1_ww_comp_2.ecm_mode_response = "3"

# Vendor: Thales
thales_default = DefaultModule("Unknown-Thales-Modem", "ffff", Thales())
plsx3_comp_1 = DefaultModule("PLSX3-Series", "0069", Thales())
plsx3_comp_2 = DefaultModule("PLSX3-Series", "006f", Thales())


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
    le910cx_wwx_comp0,
    le910cx_wwx_comp1,
    me910c1_ww_comp_1,
    me910c1_ww_comp_2,
    plsx3_comp_1,
    plsx3_comp_2,
}
