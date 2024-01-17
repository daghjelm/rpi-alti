# rpi-alti

A program that meassures altitude using the yoctopuce altitude sensor and plays video based on if the altitude sensor moves up or down.

## How to run

These instructions are for running the program on raspberry pi os Buster.
Similar should work for other linux distros but is not tested.

Assuming to you have python3 installed.

Install vlc, for raspberry pi os: `apt-get install vlc`

I recommend to create a venv:
Create a venv with `python3 -m venv .venv`, and source `source path/to/.venv`

Install packages from requirements.txt
`pip3 install -r requirements.txt`

## Running on raspian over ssh
Set default display: `export DISPLAY=:0`

Set permissions for usb devices by creating a file in `/etc/udev/rules.d`

`cd /etc/udev/rules.d`

create a file on the form ##-name.rules, ex: `vim 98-usbperm.rules`
Add this on one line: 
```
# udev rules to allow write access to all users for Yoctopuce USB devices
SUBSYSTEM=="usb", ATTR{idVendor}=="24e0", MODE="0666" 
```
Save and restart the pi: `sudo reboot`

Run the script with default values `python3 main/main.py --video_path=video.mp4`

## Run the script with the bash run script
Fill in the appriate paths in run.sh 
Make run.sh executable `sudo chmod +x run.sh`
Run the program with `./run.sh`

## Systemd service
I'm running the programs as systemd services in raspberry pi OS buster
If you want to do this yourself, you can copy the example service file "alti-player.service" to systemd
`sudo cp alti-player.service /etc/systemd/system/`

## Documentation for apis
vlc-python: https://www.olivieraubert.net/vlc/python-ctypes/doc/index.html https://github.com/oaubert/python-vlc
yoctopuce: https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html