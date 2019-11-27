# ogn2dump1090
Simple tool to inject OpenGliderNet Data into a dump1090 instance for display on a unified map

WORK IN PROGRESS DO NOT USE YET

# Getting started
## Manual Setup
### Dependencies
```
sudo apt install --yes python3-pip
sudo pip3 install ogn-client
git clone https://github.com/mutability/mlat-client.git
cd mlat-client && sudo python3 setup.py install
```
If you know what you are doing, you can simply run `./ogn2dump1090.py` and should be fine.
This requires an already running dump1090-mutability or dump1090-fa instance with the --net argument.
If you want to simply setup

## Automatic Setup
This repository contains a simple setup script to install everything that's needed (including dump1090-fa)
to a clean Raspbian Buster Raspberry Pi. It requires basic Raspberry Pi knowledge (i.e. installation connect via SSH and basic Linux shell stuff)
To use it, follow these steps:
- Flash a micro SD Card with Raspbian Buster and enable ssh by placing an empty file called ssh to its boot partition
- Connect to it via ssh
- run these commands:
```
sudo apt update
sudo apt install --yes git
git clone https://github.com/b3nn0/ogn2dump1090.git
cd ogn2dump1090
./install.sh
```
and press `y` a couple of times