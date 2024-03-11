#!/bin/bash
#set -x
echo "Simple installer script to work on a CLEAN RasPiOS Lite Image."
echo "Tested on RaspberryPi 3b, 3b+ and 4b"
echo "if you e.g. already have dump1090-fa or dump1090-mutability running, you can skip these steps"
read -p "Press return to continue"

echo
read -t 1 -n 10000 discard # discard input buffer
read -p "Install mlat-client? [y/n]" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt update
    sudo apt install --yes python3-pip
    git clone https://github.com/wiedehopf/mlat-client.git
    cd mlat-client
    sudo python3 setup.py build
    sudo python3 setup.py install
    cd ..
fi

echo
read -t 1 -n 10000 discard 
read -p "Install and setup dump1090-fa? [y/n]" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt update
    sudo apt install --yes libncurses-dev librtlsdr-dev lighttpd debhelper
    mkdir dump1090 && cd dump1090
    git clone https://github.com/VirusPilot/dump1090.git
    cd dump1090
    dpkg-buildpackage -b --no-sign --build-profiles=custom,rtlsdr
    cd ..
    sudo dpkg -i dump1090-fa_*.deb
    cd ..
    echo "I will now open the dump1090-fa configuration for you in nano."
    echo "Please modify as needed, e.g.:"
    echo "RECEIVER_SERIAL=1090 (to resolve a potential conflict with the SDR used by OGN)"
    echo "RECEIVER_LAT=48.0 and RECEIVER_LON=10.0 (receiver location required to show distance from receiver)"
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
    
    # download and unpack version 0.3.0
    ARCH=$(getconf LONG_BIT)
    DIST=$(lsb_release -r -s)
    if [ $ARCH -eq 64 ]; then
        echo
        echo "installing 64bit version on" "$ARCH""bit" "Debian" "$DIST"
        read -p "Press any key to continue"
        echo
        wget http://download.glidernet.org/arm64/rtlsdr-ogn-bin-arm64-0.3.0.tgz
    else
        echo
        echo "installing 32bit version on" "$ARCH""bit" "Debian" "$DIST"
        read -p "Press any key to continue"
        echo
        wget  http://download.glidernet.org/arm/rtlsdr-ogn-bin-ARM-0.3.0.tgz
    fi
    tar xvf *.tgz
    rm -f *.tgz
    cd rtlsdr-ogn
    /bin/bash ./setup-rpi.sh
    cd ..

   # download for automatic geoid sep
    wget http://download.glidernet.org/common/WW15MGH.DAC

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
http://raspberrypi/skyaware.
Reboot now? [y/n]" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo reboot
fi
