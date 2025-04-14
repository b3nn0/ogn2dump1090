# ogn2dump1090 - aprsproxy branch
simple Python tool to inject Open Glider Network Traffic (from an existing local OGN decoder instance) into an existing readsb ADSB decoder instance for display on a unified tar1090 map. OGN traffic will be displayed as **other** traffic in combination with ADSB traffic, using the **readsb tar1090 webinterface** (e.g. https://yourRaspberryPi.local/tar1090/)

### prerequisites
- running rtlsdr-ogn instance (e.g. based on https://github.com/VirusPilot/ogn-pi34)
- running readsb instance (based on https://github.com/wiedehopf/readsb)

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
pip3 install . --break-system-packages
```

### enable local OGN APRS proxy (optional)
you need to add the following line to the OGN APRS configuration section:
```
APRS:
{
  Server = "localhost:14580";
};
```
followed by a
```
sudo service rtlsdr-ogn restart
```

### modify readsb config
you need to add `--net-sbs-in-port=30008` to the `NET_OPTIONS` of your readsb configuration:
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
git switch aprsproxy
wget -O ddb.json http://ddb.glidernet.org/download/?j=1
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
wget -O ddb.json http://ddb.glidernet.org/download/?j=1
sudo systemctl restart ogn2dump1090
```

### implementation details
ogn2dump1090 is parsing one or both of the following two datastreams:
- APRS (through the enabled local OGN APRS proxy, see above)
- direct output from ogn-decode port 50001
and forwarding it to the readsb sbs input port (e.g. 30008)
