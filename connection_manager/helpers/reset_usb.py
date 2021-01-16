#!/usr/bin/python
from usb.core import find as finddev
from yamlio import read_yaml_all

# Change it according to user
SYSTEM_YAML_PATH = "/home/pi/.sixfab/connect/system.yaml"

temp = {}

try:
    temp = read_yaml_all(SYSTEM_YAML_PATH)
except Exception as e:
    exit(1)

vendor_id = temp.get("modem_vendor_id", "")
product_id = temp.get("modem_product_id", "")

vendor_id_int = int(vendor_id, 16)
product_id_int = int(product_id, 16)

try:
    dev = finddev(idVendor=vendor_id_int, idProduct=product_id_int)
    dev.reset()
except Exception as e:
    exit(1)
else:
    exit(0)
