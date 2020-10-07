#!/usr/bin/env bash

CMAN_PATH="/opt/sixfab/connection_manager"
ATCOM_PATH="~/atcom_api"

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
    echo "Creating setup.info done..."
fi

# Check setup.config file exist
if [[ -e $CMAN_PATH/setup.config ]]; then
    echo "setup.config already exist"
else 
    touch $CMAN_PATH/setup.config
    echo "Creating setup.config done..."
fi
 
# Get HW Info
echo "" >> $CMAN_PATH/setup.info
echo "Computer Hardware Details: " >> $CMAN_PATH/setup.info
cat /proc/cpuinfo | tail -4 >> $CMAN_PATH/setup.info

# Get OS and Distribution Info
echo "" >> $CMAN_PATH/setup.info
echo "OS: " $(uname) >> $CMAN_PATH/setup.info
echo "Kernel Release: " $(uname -r) >> $CMAN_PATH/setup.info
echo $(lsb_release -d) >> $CMAN_PATH/setup.info
echo "Host Name: " $(uname -n) >> $CMAN_PATH/setup.info

# Get Sixfab device info if is existed 
echo "" >> $CMAN_PATH/setup.info
echo "Sixfab HAT: " >> $CMAN_PATH/setup.info

if [[ -e /proc/device-tree/hat/product ]]; then
    cat /proc/device-tree/hat/product >> $CMAN_PATH/setup.info
    echo "" >> $CMAN_PATH/setup.info
else
    echo "Unknown or not exist" >> $CMAN_PATH/setup.info
fi

# Check USB driver is exist for ECM mode
lsmod | grep cdc_ether >> /dev/null
F_ECM_DR=$? >> /dev/null

if [[ $F_ECM_DR -eq "0" ]]; then
    echo "ECM driver is exist.."
else
    echo "ECM driver is not Exist!"
fi

# Check the USB is plugged
ls /dev/tty* | grep USB >> /dev/null

if [[ $? -eq 0 ]]; then
    echo "USB cable is plugged.. Available USB Ports:"
    USB_PORTS=$(ls /dev/ttyUSB*)
    echo $USB_PORTS
else
    echo "USB cable is not plugged or modem is powered down!"
fi

# Check Module Provider
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


# Check Modem Model
MODEM_STR=$(atcom ATI OK ERR)

echo "$MODEM_STR" | grep "EC25" >> /dev/null
if [[ $? -eq 0 ]]; then
    echo "Quectel EC25"
fi

echo "$MODEM_STR" | grep "EC21" >> /dev/null
if [[ $? -eq 0 ]]; then
    echo "Quectel EC21"
fi

echo "$MODEM_STR" | grep "LE910-C1" >> /dev/null
if [[ $? -eq 0 ]]; then
    echo "Telit LE910-C1"
fi

echo "$MODEM_STR" | grep "LE910-C4" >> /dev/null
if [[ $? -eq 0 ]]; then
    echo "Telit LE910-C4"
fi

# Identifying Modem and SIM Card
MODEM_IMEI=$(atcom AT+CGSN OK ERROR | tr -d -c 0-9) >> /dev/null
echo "Modem IMEI: $MODEM_IMEI"

MODEM_UCCID=$(atcom AT+CCID OK ERROR | tr -d -c 0-9) >> /dev/null
echo "SIM UCCID: $MODEM_UCCID"

MODEM_SW_VER=$(atcom AT+CGMR OK ERROR | sed -n '2p') >> /dev/null
echo "MODEM SW VER: $MODEM_SW_VER"

# Get configurations from setup.config
CFG_MODE=$(cat $CMAN_PATH/setup.config | sed -n '1p' | cut -d'=' -f2)
CFG_APN=$(cat $CMAN_PATH/setup.config | sed -n '2p' | cut -d'=' -f2)
CFG_PRIVATE_APN=$(cat $CMAN_PATH/setup.config | sed -n '3p' | cut -d'=' -f2)
CFG_USERNAME=$(cat $CMAN_PATH/setup.config | sed -n '4p' | cut -d'=' -f2)
CFG_PASSWORD=$(cat $CMAN_PATH/setup.config | sed -n '5p' | cut -d'=' -f2)

echo "CFG Modem USB Mode: $CFG_MODE"
echo "CFG APN: $CFG_APN"

echo "$PRIVATE_APN" | grep "YES" >> /dev/null
if [[ $? -eq 0 ]]; then 
    echo "CFG_PRIVATE_APN: $CFG_PRIVATE_APN"
    echo "CFG_USERNAME: $CFG_USERNAME"
    echo "CFG_PASSWORD: $CFG_PASSWORD"
fi

# *************************
# Get modem configuraitons 
# *************************

# for Quectel EC25 Only for now
MODEM_MODE_NO=$(atcom AT+QCFG=\"usbnet\" OK ERROR | sed -n '2p' | cut -d',' -f2)
MODEM_MODE="UNKNOWN"

echo $MODEM_MODE_NO | grep 0 >> /dev/null
if [[ $? -eq 0 ]]; then
    MODEM_MODE="RMNET"
fi 

echo $MODEM_MODE_NO | grep 1 >> /dev/null
if [[ $? -eq 0 ]]; then
    MODEM_MODE="ECM"
fi 

echo $MODEM_MODE_NO | grep 2 >> /dev/null
if [[ $? -eq 0 ]]; then
    MODEM_MODE="UNSUPPORTED"
fi 

echo $MODEM_MODE_NO | grep 3 >> /dev/null
if [[ $? -eq 0 ]]; then
    MODEM_MODE="UNSUPPORTED"
fi 

echo "Modem Actual Mode: $MODEM_MODE"

# Get modem APN
MODEM_APN=$(atcom AT+CGDCONT? OK ERROR | sed -n '2p' | cut -d',' -f3 | tr -d '"')
echo "Modem Actual APN: "$MODEM_APN

# If required, Configure Modem
echo $CFG_MODE | grep $MODEM_MODE >> /dev/null  # USB MODE
if [[ $? -ne 0 ]]; then
    atcom "AT+QCFG=\"usbnet\"=1" "OK" "ERR"
    if [[ $? -eq 0 ]]; then
        echo "Modem mode is configurated : ECM"
    else
        echo "Modem mode Conf. is failed!"
    fi
fi

echo $CFG_APN | grep $MODEM_APN >> /dev/null  # APN
if [[ $? -ne 0 ]]; then
    atcom "AT+CGDCONT=1,\"IPV4V6\",\"$CFG_APN\"" "OK" "ERROR" 
    if [[ $? -eq 0 ]]; then
        echo "APN is configurated : $CFG_APN"
    else
        echo "APN Conf. is failed!"
    fi
fi


