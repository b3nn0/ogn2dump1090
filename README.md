# ogn2dump1090
Simple tool to inject OpenGliderNet Data into a `dump1090-fa` instance (optionally with `tar1090` as an additional webinterface) for display on a unified map

# Getting started
## Manual Setup on an existing dump1090-fa instance
```
sudo apt install --yes python3-pip
sudo pip3 install ogn-client
git clone https://github.com/wiedehopf/mlat-client.git
cd mlat-client && sudo python3 setup.py install
```
Now install the OGN Client as described here: http://wiki.glidernet.org/wiki:manual-installation-guide
(Don't let ogn-rf/ogn-decode start on boot. ogn2dump1090 will start these processes)
You can use the ogn_setup.conf configuration as a starting point (but be sure to put the correct coordinates in there).
Now open config.py and set the path to your OGN installation.
Afterwards, you can simply run `./ogn2dump1090.py` and should be fine.
This requires an already running dump1090-mutability or dump1090-fa instance with the --net argument.

## Half-Automatic Setup
This repository contains a simple half-automatic setup script to install everything that's needed (including the latest dump1090-fa version)
on a Pi3B or Pi4B with a fresh RasPiOS installed. It requires basic RasPiOS knowledge (i.e. installation connect via SSH and basic Linux shell stuff)
To use it, follow these steps:
- Flash a micro SD Card with the latest RasPiOS Image and enable ssh by placing an empty file called ssh to its boot partition
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
After a reboot, you should be able to open http://raspberrypi/skyaware/ (or optionally http://raspberrypi/tar1090)
and see Mode-S, ADS-B and OGN/FLARM aircraft on the web interface.

## Full-Automatic Setup
- no interaction besides configuration credentials, best for a fresh install on RasPiOS 64bit Bookworm
- run these commands:
```
sudo apt update
sudo apt install --yes git
git clone https://github.com/b3nn0/ogn2dump1090.git
cd ogn2dump1090
./install-full.sh
```

For further configuration modifications, please edit:

### OGN configuration:
`/home/pi/ogn2dump1090/ogn_setup.conf`

### dump1090 configuration (up to dump1090 verison 5)
`/etc/default/dump1090-fa` needs to be modified according to your setup, e.g.
```
RECEIVER_OPTIONS="--device-index 0 --gain 28.0 --ppm 0 --lat 50.0 --lon 10.0"
```

### dump1090 configuration (dump1090 as of version 6)
`/etc/default/dump1090-fa.default` has been modified accordingly in the underlying dump1090-fa fork

`/etc/default/dump1090-fa` needs to be modified according to your setup, e.g.
```
RECEIVER_SERIAL=1090
RECEIVER_LAT=50.0
RECEIVER_LON=10.0
```

## mlat support
You can run mlat-client to connect to your favourite mlat server. The results will be seen on the web interface.

## Adding OpenAIP Airspaces to the map - work in progress!!
go to /usr/share/skyaware/html and edit layers.js.
At the end of the file, right before the line that says `return layers;`, add this code:
```
        layers.push(new ol.layer.Tile({
                source: new ol.source.XYZ({url: "http://2.tile.maps.openaip.net/geowebcache/service/tms/1.0.0/openaip_basemap@EPSG%3A900913@png/{z}/{x}/{-y}.png", visible:true, opaque:false}),
                name: 'openaip',
                title: 'OpenAIP',
                type: 'overlay',
        }));
```
After refreshing the page, OpenAIP should now load above the OSM base layer.
