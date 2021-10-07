#!/usr/bin/python3


class Quectel(object):

    name ="Quectel"
    vid = "2c7c"

    modules = {
        "EX25-Series" : "0125",
        "EC21" : "0121",
    }


class Telit(object):

    name ="Telit"
    vid = "1bc7"

    modules = {
        "PLSX3-W-Series_COMP_1" : "1201",
        "PLSX3-W-Series_COMP_2" : "1206",
        "ME910C1-WW_COMP_1" : "1101",
        "ME910C1-WW_COMP_2" : "1102",
    }  


class Thales(object):
    name ="Thales/Cinterion"
    vid = "1e2d"

    modules = {
        "LE910CX-Series_COMP_1" : "0069", # ECM/NCM
        "LE910CX-Series_COMP_2" : "006f", # RMNET
    }


quectel = Quectel()
telit = Telit()
thales = Thales()

class ModemSupport(object):    
    vendors = [quectel, telit, thales]
