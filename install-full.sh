#!/bin/bash
#set -x
echo "Simple installer script to work on a CLEAN RasPiOS Lite Image."
echo "Tested on RaspberryPi 3b, 3b+ and 4b"
read -p "Press return to continue"

sudo apt update
sudo apt install cmake python3-pip git lighttpd build-essential fakeroot pkg-config libncurses5-dev libfftw3-bin libusb-1.0-0-dev lynx ntp ntpdate procserv telnet -y
sudo apt install debhelper -y

ARCH=$(getconf LONG_BIT)
DIST=$(lsb_release -r -s)

# remove installed librtlsdr
sudo apt purge ^librtlsdr
sudo rm -rf /usr/lib/librtlsdr*
sudo rm -rf /usr/include/rtl-sdr*
sudo rm -rf /usr/local/lib/librtlsdr*
sudo rm -rf /usr/local/lib/aarch64-linux-gnu/librtlsdr*
sudo rm -rf /usr/local/include/rtl-sdr*
sudo rm -rf /usr/local/include/rtl_*
sudo rm -rf /usr/local/bin/rtl_*

# compile and install latest librtlsdr from https://github.com/osmocom/rtl-sdr
cd
git clone https://github.com/osmocom/rtl-sdr
cd rtl-sdr
sudo dpkg-buildpackage -b --no-sign
cd
sudo dpkg -i *.deb
rm -f *.deb
rm -f *.buildinfo
rm -f *.changes

echo blacklist rtl2832 | sudo tee /etc/modprobe.d/rtl-sdr-blacklist.conf
echo blacklist r820t | sudo tee -a /etc/modprobe.d/rtl-sdr-blacklist.conf
echo blacklist rtl2830 | sudo tee -a /etc/modprobe.d/rtl-sdr-blacklist.conf
echo blacklist dvb_usb_rtl28xxu | sudo tee -a /etc/modprobe.d/rtl-sdr-blacklist.conf
echo blacklist dvb_usb_v2 | sudo tee -a /etc/modprobe.d/rtl-sdr-blacklist.conf
echo blacklist rtl8xxxu | sudo tee -a /etc/modprobe.d/rtl-sdr-blacklist.conf

# install mlat-client
echo "installing mlat-client"
git clone https://github.com/wiedehopf/mlat-client.git
cd mlat-client
sudo python3 setup.py build
sudo python3 setup.py install
cd ..

# install aprslib
git clone https://github.com/rossengeorgiev/aprs-python
cd aprs-python
sudo python3 setup.py build
sudo python3 setup.py install
cd .. 

# install dump1090-fa fork
mkdir dump1090 && cd dump1090
git clone https://github.com/VirusPilot/dump1090.git
cd dump1090
dpkg-buildpackage -b --no-sign --build-profiles=custom,rtlsdr
cd ..
sudo dpkg -i dump1090-fa_*.deb
cd ..

# dump1090-fa configuration
echo "I will now open the dump1090-fa configuration in nano."
echo "Please modify as needed, e.g.:"
echo "RECEIVER_SERIAL=1090 (to resolve a potential conflict with the SDR used by OGN)"
echo "RECEIVER_LAT=48.0 and RECEIVER_LON=10.0 (receiver location required to show distance from receiver)"
echo "Then save the file (Crtl+O, Return) and quit nano (Ctrl+X)."
read -p "Press return to continue"
sudo nano /etc/default/dump1090-fa

# install OGN
if [ "$ARCH" -eq 64 ] && [ "$DIST" -ge 12 ]; then
  wget http://download.glidernet.org/arm64/rtlsdr-ogn-bin-arm64-0.3.2.tgz
else
  if [ "$ARCH" -eq 32 ] && [ "$DIST" -ge 11 ]; then
    wget http://download.glidernet.org/arm/rtlsdr-ogn-bin-ARM-0.3.2.tgz
  else
    echo
    echo "wrong platform for this script, exiting"
    echo
    exit
  fi
fi
tar xvf *.tgz
rm -f *.tgz
cd rtlsdr-ogn
sudo chown root gsm_scan ogn-rf rtlsdr-ogn
sudo chmod a+s gsm_scan ogn-rf rtlsdr-ogn
sudo mknod gpu_dev c 100 0
cd ..

# download for automatic geoid sep
wget http://download.glidernet.org/common/WW15MGH.DAC

# ogn configuration
echo "I will now open the OGN configuration file in nano. Please make proper adjustments."
echo "Most importantly, check latitude, longitude and altitude."
echo "You might also want to change the Device = 0 to something else to not conflict with dump1090."
echo "If you want to feed to OpenGliderNet aswell, you can change the APRS section "
echo "and give your receiver a Call and remove the Server=localhost.. line"
echo "Then save the file (Crtl+O, Return) and quit nano (Ctrl+X)."
read -t 1 -n 10000 discard
read -p "Press return to continue"
nano ogn_setup.conf

# install service
OGN2DUMP1090DIR=$(pwd) envsubst < ogn2dump1090.service.template > ogn2dump1090.service
sudo mv ogn2dump1090.service /etc/systemd/system/
sudo systemctl enable ogn2dump1090
sudo systemctl start ogn2dump1090

# reboot
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
