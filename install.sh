#!/bin/bash
echo TODO
exit 0
echo Simple installer script to work on a CLEAN raspbian buster image.
echo Tested on RaspberryPi 3b+
echo If you e.g. already have dump1090-fa or dump1090-mutability running, you can skip these steps

read -p "Install base dependencies? [y/n]" -n 1 -r
if [[ $REPLAY =~ ^[Yy]$ ]]; then
    echo "installing base dependencies"
    sudo apt update
    sudo apt install --yes python3-pip
    sudo pip3 install ogn-client
    git clone https://github.com/mutability/mlat-client.git
    cd mlat-client
    sudo python3 setup.py install
    cd ..
fi

read -p "Install and setup dump1090-fa? [y/n]" -n 1 -r
if [[ $REPLAY =~ ^[Yy]$ ]]; then
    git clone https://github.com/flightaware/dump1090.git

fi