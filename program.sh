#!/bin/sh

DATE=`date "+(%Y, %m, %d, %w, %H, %M, %S, 0)"`

sed -i -r "s/utc = .*/utc = ${DATE}/" IoTDevice.py

ampy --port /dev/ttyUSB0 put IoTDevice.py 

screen /dev/ttyUSB0 115200
