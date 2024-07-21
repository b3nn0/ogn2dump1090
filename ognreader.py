import threading
import config
import subprocess
import re
import os
import json
import logging
import aprslib


# Shamelessly taken from https://github.com/glidernet/python-ogn-client/blob/master/ogn/parser/pattern.py
# and adapted for OGN 0.3.2 stack (and reduced a bit for fields we don't need)
PATTERN_TELNET_50001 = re.compile(r"""
    (?P<pps_offset>\d\.\d+)sec:(?P<frequency>\d+\.\d+)MHz:\s+
    (?P<aircraft_type>.):(?P<address_type>\d:)?(?P<address>[A-F0-9]{6})\s
    (?P<timestamp>\d{6}):\s
    \[\s*(?P<latitude>[+-]\d+\.\d+),\s*(?P<longitude>[+-]\d+\.\d+)\]deg\s*
    (?P<altitude>\d+)m\s*
    (?P<climb_rate>[+-]\d+\.\d+)m/s\s*
    (?P<ground_speed>\d+\.\d+)m/s\s*
    (?P<track>\d+\.\d+)deg\s*
    .*
""", re.VERBOSE | re.MULTILINE)

class OgnReader(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.proc_rf = None
        self.proc_decode = None
        self.callback = callback
        self.ogn_devicedb = {}
        self.read_ognddb()
    
    def __del__(self):
        if self.proc_rf is not None:
            self.proc_rf.kill()
        if self.proc_decode is not None:
            self.proc_decode.kill()
    
    def read_ognddb(self):
        try:
            ddb = json.loads(open('ddb.json', 'r').read())
            for dev in ddb['devices']:
                devid = dev['device_id']
                call = dev['registration']
                self.ogn_devicedb[devid] = call
        except:
            logging.warn('Failed to read device db')
    
    def run(self):
        logging.info('OgnReader startup')
        while True:
            self.proc_rf = subprocess.Popen([config.ogn_rf_cmd, config.ogn_config], stdin=subprocess.PIPE)
            logging.info('Started OGN-RF')
            self.proc_decode = subprocess.Popen([config.ogn_decode_cmd, config.ogn_config], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            logging.info('Started OGN-Decode')
            try:
                for line in iter(self.proc_decode.stdout.readline, b''):
                    #print(line)
                    self.parse_line(line)
            except:
                logging.error('OGN error.. restarting')
                self.proc_rf.kill()
                self.proc_decode.kill()
            logging.warn('OGN process finished. Restarting.')


    def parse_line(self, line):
        try:
            search = re.search(PATTERN_TELNET_50001, str(line))
            if search is not None:
                msg = search.groupdict()
                addr = int(msg['address'], 16)
                lat = float(msg['latitude'])
                lon = float(msg['longitude'])
                altFt = float(msg['altitude']) * 3.28084 # in ft
                speedKt = float(msg['ground_speed']) * 1.94384 # m/s in kt
                climb = int(float(msg['climb_rate']) * 196.85)
                track = float(msg['track'])
                anon = False
                if msg['address'].lower()[0:2] == 'dd' or msg['address'].lower()[0:1] == '1':
                    anon = True

                registration = None

                if msg['address'] in self.ogn_devicedb:
                    registration = self.ogn_devicedb[msg['address']]

                self.callback(addr, lat, lon, altFt, speedKt, climb, track, registration, anon)
        except:
            pass

    def aprsmessage(self, msg):
        strmsg = msg.decode('utf-8')
        if len(strmsg) == 0:
            return
        try:
            message = aprslib.parse(strmsg)
            # additional info seems to be in here...
            comment = message['comment'].split(' ')
            if comment[0].startswith('id'):
                addrStr = comment[0][2:]
            else:
                addrStr = message['from'][3:]
            addr = int(addrStr, 16)

            climb = 0
            if comment[1].endswith('fpm'):
                climb = int(comment[1][0:-3])

            lat = message['latitude']
            lon = message['longitude']
            altFt = message['altitude'] * 3.28084 # in ft
            speedKt = message['ground_speed'] * 1.94384 if 'ground_speed' in message else 0
            track = message['course'] if 'course' in message else 0

            registration = None
            if addrStr in self.ogn_devicedb:
                registration = self.ogn_devicedb[addrStr]

            self.callback(addr, lat, lon, altFt, speedKt, climb, track, registration, False)
        except Exception as e:
            logging.warn(f'not parsable as APRS message: {strmsg}')
            print(e)

        
