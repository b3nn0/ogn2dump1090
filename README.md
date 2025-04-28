# ogn2readsb (aka. ogn2dump1090)
simple Python tool to inject Open Glider Network Traffic (from an existing local OGN decoder instance) into an existing readsb ADSB decoder instance for display on a unified tar1090 map. OGN traffic will be displayed as **other** traffic in combination with ADSB traffic, using the **readsb tar1090 webinterface** (e.g. https://yourRaspberryPi.local/tar1090/)

### prerequisites
- running rtlsdr-ogn instance (e.g. based on https://github.com/VirusPilot/ogn-pi34)
- running readsb instance, e.g. based on:
  - https://github.com/wiedehopf/readsb
  - https://github.com/wiedehopf/airspy-conf

### prepare
```
sudo apt update
sudo apt install python3-pip git telnet -y
```

### install python-ogn-client
```
cd ~/
git clone https://github.com/glidernet/python-ogn-client
cd python-ogn-client/
pip3 install --break-system-packages .
```

### enable local OGN APRS proxy
you need to add the following line to the OGN APRS configuration section after your station callsign:
```
APRS:
{
  Call   = "NewOGNrx";
  Server = "localhost:14580";
};
```
followed by a
```
sudo service rtlsdr-ogn restart
```

### modify readsb config
you need to add `--net-sbs-in-port=30008` to the `NET_OPTIONS` section of your readsb configuration:
```
sudo nano /etc/default/readsb
```
followed by a
```
sudo service readsb restart
```

### install ogn2dump1090 service
```
git clone https://github.com/b3nn0/ogn2dump1090
cd ogn2dump1090/
```
modify the GNSS coordinates in the config.py `aprs_subscribe_filter` section according to your GNSS station coordinates:
```
nano config.py
```
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

### OGN ddb update
the OGN database is not automatically updated, therefore a regular manual update is recommended:
```
cd ~/ogn2dump1090/
wget -O ddb.json http://ddb.glidernet.org/download/?j=1
sudo systemctl restart ogn2dump1090
```
