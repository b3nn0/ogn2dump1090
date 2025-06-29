# Host/Port where readsb is running with something like --net-sbs-in-port=30008
sbs_destination_host = "127.0.0.1"
sbs_destination_port = 30008


# Host/Port where ogn-decode telnet listens. Leave empty or set to None if you only want APRS functionality
TELNET_SERVER_HOST = "127.0.0.1"
TELNET_SERVER_PORT = 50001


# Upstream APRS Servers. Leave empty or None to run in standalone mode without upstream APRS connection
aprs_servers = ['glidern1.glidernet.org','glidern2.glidernet.org','glidern3.glidernet.org','glidern4.glidernet.org','glidern5.glidernet.org']

# Use generic APRS Server address instead of the list above
# aprs_servers = ['aprs.glidernet.org']


# Subscribe to positions with a 20km radius around the given location. None if you don't want to subscribe to anything
aprs_subscribe_filter = "r/48.0/10.0/100"

# Optional:
# ADS-B Data is usually based on pressure altitude, but OGN is based on GPS altitude.
# ogn2dump1090 can convert it for you, by fetching METARS from a nearby airport via https://aviationweather.gov/data/api/
# Must be the 4 letter ICAO code of a nearby airport, e.g. "EDNY". Test the request via https://aviationweather.gov/api/data/metar?ids=EDNY
metar_source = None


# APRS Server is always active. If you want to use it, and have ogn2readsb act as an APRS proxy, change your rtlsdr-ogn configuration to include
# something like
# APRS:
# {
#   Call   = "NewOGNrx";
#   Server = "localhost:14580";
# };