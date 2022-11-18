#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys

# add ../../Sources to the PYTHONPATH
sys.path.append(os.path.join("..", "..", "Sources"))

from yoctopuce.yocto_api import *
from yoctopuce.yocto_altitude import *
import sys

def die(msg):
    sys.exit(msg + ' (check USB cable)')

errmsg = YRefParam()

# Setup the API to use local USB devices
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("init error" + errmsg.value)

# retreive any altitude sensor
sensor = YAltitude.FirstAltitude()
if sensor is None:
    die('No module connected')
m = sensor.get_module()
target = m.get_serialNumber()

altSensor = YAltitude.FindAltitude(target + '.altitude')

while sensor.isOnline():
    print(altSensor.getCurrentValue())
    YAPI.sleep(1000)