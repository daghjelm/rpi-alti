#!/bin/bash
export DISPLAY=:0
# for testing
# python3 main.py -v=/home/pi/Desktop/5NY_PALMER.mp4 -a=/home/pi/Desktop/PALMER.wav -k -s=10 -t -d -p=5 -b=60
# for prod
python3 /home/pi/Documents/rpi-alti/main.py -v=/home/pi/Desktop/5NY_PALMER.mp4 -a=/home/pi/Desktop/PALMER.wav -s=10 -t -p=5 -b=600 --diff=0.7 -i=1
