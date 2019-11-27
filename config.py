# Requirements:
# sudo pip3 install ogn-client
# Also, install mlat-client:
# git clone https://github.com/mutability/mlat-client.git && cd mlat-client && sudo python3 setup.py install

ogn_rf_cmd = '/usr/bin/ogn-rf'
ogn_decode_cmd = '/usr/bin/ogn-decode'


# Important: configure this file as needed. As APRS Server you can either use the official gliderNet servers
# if you want to feed to OGN and the device has an internet connection. If you want to work offline,
# use localhost:14580 as APRS server
ogn_config = 'path_to_ogn_config.conf'