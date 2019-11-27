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
Now install the OGN Client as described here: http://wiki.glidernet.org/wiki:manual-installation-guide
(Don't let ogn-rf/ogn-decode start on boot. ogn2dump1090 will start these processes)
You can use the ogn_setup.conf configuration as a starting point (but be sure to put the correct coordinates in there).
Now open config.py and set the path to your OGN installation.
Afterwards, you can simply run `./ogn2dump1090.py` and should be fine.
This requires an already running dump1090-mutability or dump1090-fa instance with the --net argument.

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
After a reboot, you should be able to open http://raspberrypi/dump1090-fa/
and see both, dump1090 AND flarm aircraft on the web interface.

## Mlat support
TODO
you can run mlat-client to connect to your favourite mlat server. The results will be seen on the web interface.

## Adding OpenAIP Airspaces to the map
go to /usr/share/dump1090-fa/html and edit layers.js.
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