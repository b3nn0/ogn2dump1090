# ogn2dump1090
Simple tool to inject Open Glider Network Traffic into a `dump1090-fa` instance for display on a unified map (will be displayed as "MLAT" traffic). It contains setup scripts to install everything that's needed (including a modified dump1090-fa instance) on a Pi3B or Pi4B with a fresh RasPiOS (idealy 64bit Bookworm) installed. It requires basic RasPiOS knowledge (i.e. connecting via SSH and basic Linux shell stuff)

## preparation of credentials
During the setup process you will be automatically asked to edit `/home/pi/ogn2dump1090/ogn_setup.conf` and `/etc/default/dump1090-fa` for which you should have the following credentials at hand:
- SDR index numbers **or** SDR serial numbers (SN) for both the OGN and ADS-B SDRs
- SDR ppm calibration (only required for non-TCXO SDRs), this can also be measured and modified accordingly post install if unknown
- OGN station name, e.g. your local airport ICAO code (max. 9 characters), please refer to http://wiki.glidernet.org/receiver-naming-convention
- station coordinates and altitude for both the OGN and ADS-B configuration file

## Full-Automatic Setup
- no interaction besides configuration credentials, for a fresh install on RasPiOS 64bit Bookworm (32bit Bookworm and 32/64bit Bullseye are also supported but without RTL-SDR Blog V4 dongle support)
- connect via ssh
- run these commands:
```
sudo apt update
sudo apt full-upgrade --yes
sudo apt install --yes git
git clone -b aprsproxy https://github.com/b3nn0/ogn2dump1090.git
cd ogn2dump1090
./install-full.sh
```
## Half-Automatic Setup
- connect via ssh
- run these commands:
```
sudo apt update
sudo apt install --yes git
git clone https://github.com/b3nn0/ogn2dump1090.git
cd ogn2dump1090
./install.sh
```

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

## For further configuration modifications, please edit:
- OGN configuration: `/home/pi/ogn2dump1090/ogn_setup.conf`
- dump1090-fa configuration: `/etc/default/dump1090-fa`

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
