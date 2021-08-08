#!/bin/bash
#set -x
echo "Simple installer script to work on a CLEAN raspbian buster image."
echo "Tested on RaspberryPi 3b, 3b+ and 4b"
echo "if you e.g. already have dump1090-fa or dump1090-mutability running, you can skip these steps"
read -p "Press return to continue"
sudo apt update

echo
read -t 1 -n 10000 discard # discard input buffer
read -p "Install base dependencies? [y/n]" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "installing base dependencies"
    sudo apt install --yes python3-pip rtl-sdr
    git clone https://github.com/mutability/mlat-client.git
    cd mlat-client
    sudo python3 setup.py install
    cd ..
fi

echo
read -t 1 -n 10000 discard 
read -p "Install and setup dump1090-fa? [y/n]" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt install --yes libncurses-dev librtlsdr-dev libbladerf-dev lighttpd debhelper dh-systemd libhackrf-dev liblimesuite-dev
    mkdir dump1090 && cd dump1090
    git clone https://github.com/VirusPilot/dump1090.git
    cd dump1090
    dpkg-buildpackage -b --no-sign
    cd ..
    sudo dpkg -i dump1090-fa_*.deb
    cd ..
    echo "I will now open the dump1090-fa configuration for you in nano."
    echo "Please modify as needed, e.g. RECEIVER_OPTIONS:"
    echo "--device-index 0 (to resolve a potential conflict with the SDR used by OGN)"
    echo "--gain -10"
    echo "--ppm 0"
    echo "--lat 48.0000 --lon 10.0000 (receiver location required to show distance from receiver)"
    echo "Then save the file (Crtl+O, Return) and quit nano (Ctrl+X)."
    read -p "Press return to continue"
    sudo nano /etc/default/dump1090-fa
fi

echo
read -t 1 -n 10000 discard
read -p "Install OGN Client? [y/n]" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo blacklist rtl2832 | sudo tee /etc/modprobe.d/rtl-glidernet-blacklist.conf
    echo blacklist r820t | sudo tee -a /etc/modprobe.d/rtl-glidernet-blacklist.conf
    echo blacklist rtl2830 | sudo tee -a /etc/modprobe.d/rtl-glidernet-blacklist.conf
    echo blacklist dvb_usb_rtl28xxu | sudo tee -a /etc/modprobe.d/rtl-glidernet-blacklist.conf
    echo blacklist dvb_usb_v2 | sudo tee -a /etc/modprobe.d/rtl-glidernet-blacklist.conf
    echo blacklist rtl8xxxu | sudo tee -a /etc/modprobe.d/rtl-glidernet-blacklist.conf
    
    sudo apt install --yes libconfig9 libjpeg8 lynx ntpdate ntp

    if grep -q "Pi 4" /proc/device-tree/model; then
        wget http://download.glidernet.org/arm/rtlsdr-ogn-bin-ARM-latest.tgz
    else
        wget http://download.glidernet.org/rpi-gpu/rtlsdr-ogn-bin-RPI-GPU-latest.tgz
    fi
    tar xzf rtlsdr-ogn-bin-*.tgz
    rm rtlsdr-ogn-bin-*.tgz
    cd rtlsdr-ogn
    ./setup-rpi.sh
    cd ..

   # download for automatic geoid sep
    sudo wget http://download.glidernet.org/common/WW15MGH.DAC

    echo "I will now open the OGN configuration file in nano. Please make proper adjustments."
    echo "Most importantly, check latitude, longitude and altitude."
    echo "You might also want to change the Device = 0 to something else to not conflict with dump1090."
    echo "If you want to feed to OpenGliderNet aswell, you can change the APRS section "
    echo "and give your receiver a Call and remove the Server=localhost.. line"
    echo "Then save the file (Crtl+O, Return) and quit nano (Ctrl+X)."
    read -t 1 -n 10000 discard
    read -p "Press return to continue"
    nano ogn_setup.conf  
fi

echo
read -t 1 -n 10000 discard 
read -p "Install service file/start ogn2dump1090 on boot [y/n]" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    OGN2DUMP1090DIR=$(pwd) envsubst < ogn2dump1090.service.template > ogn2dump1090.service
    sudo mv ogn2dump1090.service /etc/systemd/system/
    sudo systemctl enable ogn2dump1090
    sudo systemctl start ogn2dump1090
fi

# TODO: can't transmit callsign via BEAST format...
#echo
#read -p "Install OGN Device DB for callsign lookup? [y/n]" -n 1 -r
#if [[ $REPLY =~ ^[Yy]$ ]]; then
#    wget -O ddb.json http://ddb.glidernet.org/download/?j=1
#fi


echo
read -t 1 -n 10000 discard 
read -p "The RaspberryPi now needs to be rebooted to make sure all permissions are set correctly. Afterwards 
you should be able to access the dump1090-fa interface on
http://raspberrypi/dump1090-fa.
Reboot now? [y/n]"
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo reboot
fi