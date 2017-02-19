#!/bin/sh

#program.sh
#FPJA group
#Feb 2017
#
#Script to load the current version of the IoTDevice to the ESP8266. It also 
#updates to the current UTC time to start the device RTC clock.

DATE=`date "+(%Y, %m, %d, %w, %H, %M, %S, 0)"`

sed -i -r "s/utc = .*/utc = ${DATE}/" IoTDevice.py

#Preprocess file (delete comments) to save space in the device
#cat IoTDevice.py | sed -r "s/\#.*//g" | sed -r "s/^$//g" > p_IoTDevice.py

ampy --port /dev/ttyUSB0 put IoTDevice.py 

screen /dev/ttyUSB0 115200
