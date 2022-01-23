from helpers.modem_support.quectel import Quectel
from helpers.modem_support.telit import Telit, LE910CXThreadX, ME910C1WW
from helpers.modem_support.thales import Thales

# Products
# Vendor: Quectel
quectel_default = Quectel("Unknown-Quectel-Modem", "ffff")
ec25 = Quectel("EC25", "0125")
ec21 = Quectel("EC21", "0121")

# Vendor: Telit
telit_default = Telit("Unknown-Telit-Modem", "ffff")
le910cx_comp_1 = Telit("LE910CX", "1201")
le910cx_comp_2 = Telit("LE910CX", "1206")
le910cx_wwx_comp0 = LE910CXThreadX("LE910CX-ThreadX", "1031")
le910cx_wwx_comp1 = LE910CXThreadX("LE910CX-ThreadX", "1033")
me910c1_ww_comp_1 = ME910C1WW("ME910C1-WW", "1101")
me910c1_ww_comp_2 = ME910C1WW("ME910C1-WW", "1102")

# Vendor: Thales
thales_default = Thales("Unknown-Thales-Modem", "ffff")
plsx3_comp_1 = Thales("PLSX3-Series", "0069")
plsx3_comp_2 = Thales("PLSX3-Series", "006f")

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
