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
        "LE910CX-Series_COMP_1" : "1201",
        "LE910CX-Series_COMP_2" : "1206",
        "ME910C1-WW_COMP_1" : "1101",
        "ME910C1-WW_COMP_2" : "1102",
    }  


quectel = Quectel()
telit = Telit()

class ModemSupport(object):    
    vendors = [quectel, telit]
