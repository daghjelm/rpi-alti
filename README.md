# rpi-alti

A program that meassures altitude using the yoctopuce altitude sensor and plays video based on if the altitude sensor moves up or down.

## How to run

Assuming to you have python3 installed.

Install vlc, for raspbian: `apt-get install vlc`

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

## Documentation for apis
vlc-python: https://www.olivieraubert.net/vlc/python-ctypes/doc/index.html https://github.com/oaubert/python-vlc
yoctopuce: https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html


## Production
Edit the startPlayer.desktop file with the apropriate file paths and arguments.
Copy the desktop file to desktop ex:
`cp startPlayer.desktop ~/Desktop/`

If you want the script to auto restart with systemctl:
* Edit the .service file with the proper arguments to the python script
* Copy the .service file to /etc/systemd/system:
`sudo cp altiplayer_python_script.service /etc/systemd/system/`
* copy start player forever desktop file:
`cp startPlayerForever.desktop ~/Desktop/`