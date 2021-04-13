#!/usr/bin/python3


class Quectel(object):

    name ="Quectel"
    vendor_id = "2c7c"

    modules = {
        "EC25" : "0125",
        "EG25" : "0125",
        "EC21" : "0121",
    }  


class Telit(object):

    name ="Telit"
    vendor_id = "1bc7"

    modules = {
        "LE910C1-EU_COMP_1" : "1201",
        "LE910C1-EU_COMP_2" : "1206",
        "LE910C4-EU_COMP_1" : "1201",
        "LE910C4-EU_COMP_2" : "1206",
        "LE910C1-NF_COMP_1" : "1201",
        "LE910C1-NF_COMP_2" : "1206",
        "LE910C4-NF_COMP_1" : "1201",
        "LE910C4-NF_COMP_2" : "1206",
        "ME910_COMP_1" : "1101",
        "ME910_COMP_2" : "1102",
    }  


quectel = Quectel()
telit = Telit()

class ModemSupport(object):    
    
    vendors = [quectel, telit]

