# ogn2readsb (aka. ogn2dump1090)
- simple Python tool to inject Open Glider Network Traffic (from an existing local OGN decoder instance) into an existing **readsb** ADS-B decoder instance for display on a unified **tar1090** map
- furthermore online aggregated traffic from OGN will also be injected for a reasonably selected radius around a given location
- OGN traffic will be displayed as **other** traffic alongside with ADS-B traffic, using the **readsb tar1090 webinterface** (e.g. https://yourRaspberryPi.local/tar1090/); you can relabel OGN traffic e.g. to **OGN** by adding `jaeroLabel = "OGN";` to `/usr/local/share/tar1090/html/config.js`

any combination of the following modes is possible, for more details see `config.py`:
- Read data from ogn-decode telnet port 50001
- Pretend to be an APRS Server and have a locally running ogn-decode connect to it
- Connect to a remote APRS server and subscribe to data from it

If ogn2readsb acts as a local APRS Server AND upstream APRS client in parallel, it will automatically act as an APRS proxy and forward locally received data to OGN upstream.

### prerequisites
- running **rtlsdr-ogn** instance (e.g. based on https://github.com/VirusPilot/ogn-pi34)
- running **readsb** instance, e.g. based on:
  - https://github.com/wiedehopf/readsb
  - https://github.com/wiedehopf/airspy-conf (in case you are using an AirSpy SDR)

### prepare
```
sudo apt update
sudo apt install python3-pip python3-aiohttp git telnet -y
```

### install python-ogn-client
```
cd ~/
git clone https://github.com/glidernet/python-ogn-client
cd python-ogn-client/
pip3 install --break-system-packages .
```

### enable local OGN APRS proxy (optional)
you need to add the following line to the OGN APRS configuration section after your station callsign:
```
APRS:
{
  Call   = "NewOGNrx";
  Server = "localhost:14580";
};
```
followed by a:
```
sudo service rtlsdr-ogn restart
```

### modify readsb config
you need to add `--net-sbs-jaero-in-port 30008 --jaero-timeout 1` to the `NET_OPTIONS` section of your readsb configuration:
```
sudo nano /etc/default/readsb
```
followed by a:
```
sudo service readsb restart
```

### install ogn2dump1090 service and adjust settings in config.py
```
git clone https://github.com/b3nn0/ogn2dump1090
cd ogn2dump1090/
nano config.py
```
modify the GNSS coordinates in the `aprs_subscribe_filter` section according to your GNSS station coordinates, e.g `"r/48.0/10.0/20"` for a 20km radius around your selected location and add a the ICAO code of a nearby airport that provides METAR so that baro and GNSS altitude can be converted by ogn2dump1090

download the latest OGN database:
```
wget -O ddb.json http://ddb.glidernet.org/download/?j=1
```
prepare and install ogn2dump1090 service:
```
OGN2DUMP1090DIR=$(pwd) envsubst < ogn2dump1090.service.template > ogn2dump1090.service
sudo mv ogn2dump1090.service /etc/systemd/system/
sudo systemctl enable ogn2dump1090
sudo systemctl start ogn2dump1090
```

### verify
```
sudo systemctl status ogn2dump1090
https://yourRaspberryPi.local/tar1090/
```

### OGN database update
the OGN database is not automatically updated, therefore a regular manual update is recommended:
```
cd ~/ogn2dump1090/
wget -O ddb.json http://ddb.glidernet.org/download/?j=1
sudo systemctl restart ogn2dump1090
```
### readsb/tar1090 database update
the readsb/tar1090 database is not automatically updated, therefore a regular manual update is recommended:
```
sudo bash -c "$(wget -O - https://github.com/wiedehopf/adsb-scripts/raw/master/readsb-install.sh)"
```

### remarks
- if an OGN traffic target also transmitts Mode-S, the displayed RSSI values are related to the Mode-S signal, not to the OGN signal
- for a fresh install you may consider trying the following script: [script that installs rtlsrd-ogn, readsb and ogn2dump1090](https://github.com/VirusPilot/ogn-pi34?tab=readme-ov-file#automatic-setup-2-alternative-script-that-installs-rtlsrd-ogn-readsb-and-ogn2dump1090), a screen recording of all steps required can be found here: https://youtu.be/5kWt9rtBNwU
