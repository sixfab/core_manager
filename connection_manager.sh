#!/usr/bin/env bash

CMAN_PATH="/opt/sixfab/connection_manager"

# Check connection_manager folder exist
if [[ ! -e $CMAN_PATH ]]; then
    mkdir -p $CMAN_PATH
    echo "Path created."
fi

# Check setup.info file exist
if [[ -e $CMAN_PATH/setup.info ]]; then
    echo "setup.info already exist"
else 
    touch $CMAN_PATH/setup.info
    echo "Creating setup.info done..." >> $CMAN_PATH/setup.info
fi
 
# Get HW Info
echo "" >> $CMAN_PATH/setup.info
echo "Computer Hardware Details: " >> $CMAN_PATH/setup.info
cat /proc/cpuinfo | tail -4 >> $CMAN_PATH/setup.info

# Get Sixfab device info if is existed 
echo "" >> $CMAN_PATH/setup.info
echo "Sixfab HAT: " >> $CMAN_PATH/setup.info

if [[ -e /proc/device-tree/hat/product ]]; then
    cat /proc/device-tree/hat/product >> $CMAN_PATH/setup.info
    echo "" >> $CMAN_PATH/setup.info
else
    echo "Unknown or not exist" >> $CMAN_PATH/setup.info
fi

# Get OS and Distribution Info
echo "" >> $CMAN_PATH/setup.info
echo "OS: " $(uname) >> $CMAN_PATH/setup.info
echo "Kernel Release: " $(uname -r) >> $CMAN_PATH/setup.info
echo $(lsb_release -d) >> $CMAN_PATH/setup.info
echo "Host Name: " $(uname -n) >> $CMAN_PATH/setup.info

# Check USB driver is exist for ECM mode
lsmod | grep cdc_ether >> /dev/null
F_ECM_DR=$? >> /dev/null

if [[ $F_ECM_DR -eq "0" ]]; then
    echo "ECM driver is exist.."
else
    echo "ECM driver is not Exist!"
fi

# Check Modul Provider
lsusb | grep Quectel >> /dev/null
IS_QUECTEL=$?

lsusb | grep Telit >> /dev/null
IS_TELIT=$?

if [[ IS_TELIT -ne 0 ]] && [[ IS_QUECTEL -ne 0 ]]; then
    echo "Module is not exist or provider is unknown!"
elif [[ IS_TELIT -eq 0 ]]; then
    echo "Telit Module"
elif [[ IS_QUECTEL -eq 0 ]]; then
    echo "Quectel Module"
fi

# Check the USB is plugged
ls /dev/tty* | grep USB >> /dev/null

if [[ $? -eq 0 ]]; then
    echo "USB cable is plugged.. Available USB Ports:"
    ls /dev/tty* | grep USB
else
    echo "USB cable is not plugged or modem is powered down!"
fi

# Check Modem Model



