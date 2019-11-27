#!/bin/bash
echo TODO
exit 0
echo "Simple installer script to work on a CLEAN raspbian buster image."
echo "Tested on RaspberryPi 3b+"
echo "if you e.g. already have dump1090-fa or dump1090-mutability running, you can skip these steps"
read -p "Press return to continue"
sudo apt update

read -p "Install base dependencies? [y/n]" -n 1 -r
if [[ $REPLAY =~ ^[Yy]$ ]]; then
    echo "installing base dependencies"
    sudo apt install --yes python3-pip rtl-sdr
    sudo pip3 install ogn-client
    git clone https://github.com/mutability/mlat-client.git
    cd mlat-client
    sudo python3 setup.py install
    cd ..
fi

read -p "Install and setup dump1090-fa? [y/n]" -n 1 -r
if [[ $REPLAY =~ ^[Yy]$ ]]; then
    sudo apt install --yes libncurses-dev librtlsdr-dev libbladerf-dev lighttpd debhelper dh-systemd
    git clone https://github.com/flightaware/dump1090.git
    cd dump1090
    ./prepare-build.sh stretch
    cd package-stretch
    dpkg-buildpackage -uc -us
    cd ..
    sudo dpkg -i dump1090-fa_*.deb
    echo "I will now open the dump1090-fa configuration for you in nano. Please modify as needed (especially the --device-index"
    echo "parameter to resolve the potential conflict with OGN)."
    echo "Then save the file (Crtl+O, Return) and quit nano (Ctrl+X)."
    read -p "Press return to continue"
    sudo nano /etc/default/dump1090-fa
fi

read -p "Install OGN Client? [y/n]" -n 1 -r
if [[ $REPLAY =~ ^[Yy]$ ]]; then
    sudo bash -c "cat >> /etc/modprobe.d/rtl-glidernet-blacklist.conf <<EOF
blacklist rtl2832
blacklist r820t
blacklist rtl2830
blacklist dvb_usb_rtl28xxu
EOF"
    sudo apt install --yes libconfig9 libjpeg8 lynx ntpdate ntp
    # Need to use older libfftw for now because the one in raspbian stretch makes OGN hang on startup...
    wget http://ftp.debian.org/debian/pool/main/f/fftw3/libfftw3-bin_3.3.5-3_armhf.deb
    wget http://ftp.debian.org/debian/pool/main/f/fftw3/libfftw3-dev_3.3.5-3_armhf.deb
    wget http://ftp.debian.org/debian/pool/main/f/fftw3/libfftw3-double3_3.3.5-3_armhf.deb
    wget http://ftp.debian.org/debian/pool/main/f/fftw3/libfftw3-single3_3.3.5-3_armhf.deb
    sudo dpkg -i libfftw*.deb
    rm libfftw*.deb

    wget http://download.glidernet.org/rpi-gpu/rtlsdr-ogn-bin-RPI-GPU-latest.tgz
    tar xzf rtlsdr-ogn-bin-RPI-GPU-latest.tgz
    rm rtlsdr-ogn-bin-RPI-GPU-latest.tgz
    cd rtlsdr-ogn
    sudo chown root gsm_scan
    sudo chmod a+s gsm_scan
    sudo chown root ogn-rf
    sudo chmod a+s  ogn-rf
    cd ..

    echo "I will now open the OGN configuration file in nano. Please make proper adjustments."
    echo "Most importantly, check latitude, longitude and altitude."
    echo "You might also want to change the Device = 1 to something else to not conflict with dump1090."
    echo "If you want to feed to OpenGliderNet aswell, you can change the APRS section "
    echo "and give your receiver a Call and remove the Server=localhost.. line"
    echo "Then save the file (Crtl+O, Return) and quit nano (Ctrl+X)."
    read -p "Press return to continue"
    nano ogn_setup.conf  
fi

read -p "Install service file/start ogn2dump1090 on boot [y/n]" -n 1 -r
if [[ $REPLAY =~ ^[Yy]$ ]]; then
    OGN2DUMP1090DIR=$(pwd) envsubst < ogn2dump1090.service.template > ogn2dump1090.service
    sudo mv ogn2dump1090.service /etc/systemd/system/
    sudo systemctl enable ogn2dump1090
    sudo systemctl start ogn2dump1090
fi

read -p "The RaspberryPi now needs to be rebooted to make sure all permissions are set correctly. Reboot now? [y/n]"
if [[ $REPLAY =~ ^[Yy]$ ]]; then
    sudo reboot
fi