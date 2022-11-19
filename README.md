# rpi-alti

A program that meassures altitude using the yoctopuce altitude sensor and plays video based on if the altitude sensor moves up or down.

## How to run

Assuming to you have python3 installed.

Install the yoctopuce package: 
`pip3 install yoctopuce`

Install vlc, for raspbian: `apt-get install vlc`

Install python vlc bindings: `pip3 install python-vlc`

## Running on raspian over ssh
Set default display: `export DISPLAY=:0`

Set permissions for usb devices by creating a file in `/etc/udev/rules.d`

`cd /etc/udev/rules.d`

create a file on the form ##-name.rules, ex: `vim 98-usbperm.rules`
Add this on one line: 
```
# udev rules to allow write access to all users for Yoctopuce USB devices SUBSYSTEM=="usb", ATTR{idVendor}=="24e0", MODE="0666" 
```
Save and restart the pi: `sudo reboot`

## Documentation for apis
vlc-python: https://www.olivieraubert.net/vlc/python-ctypes/doc/index.html https://github.com/oaubert/python-vlc
yoctopuce: https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html
