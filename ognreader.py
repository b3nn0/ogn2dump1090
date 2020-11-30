import threading
import config
import subprocess
import re
import os
import json


# Shamelessly taken from https://github.com/glidernet/python-ogn-client/blob/master/ogn/parser/pattern.py
# and adapted for OGN 2.8 stack (and reduced a bit for fields we don't need)
PATTERN_TELNET_50001 = re.compile(r"""
    (?P<pps_offset>\d\.\d+)sec:(?P<frequency>\d+\.\d+)MHz:\s+
    (?P<aircraft_type>.):(?P<address_type>\d):(?P<address>[A-F0-9]{6})\s
    (?P<timestamp>\d{6}):\s
    \[\s*(?P<latitude>[+-]\d+\.\d+),\s*(?P<longitude>[+-]\d+\.\d+)\]deg\s*
    (?P<altitude>\d+)m\s*
    (?P<climb_rate>[+-]\d+\.\d+)m/s\s*
    (?P<ground_speed>\d+\.\d+)m/s\s*
    (?P<track>\d+\.\d+)deg\s*
    (?P<turn_rate>[+-]\d+\.\d+)deg/s\s*
    (?P<magic_number>[0-9a-zA-Z]+)\s*
    (?P<gps_status>[0-9x]+)m\s*
    (?P<channelinfo>.+?:\S+)\s*
    (?P<frequency_offset>[+-]\d+\.\d+)kHz\s*
    (?P<decode_quality>\d+\.\d+)/(?P<signal_quality>\d+\.\d+)dB/(?P<demodulator_type>\d+)\s+
    (?P<error_count>\d+)e\s*
    (?P<distance>\d+\.\d+)km\s*
    (?P<bearing>\d+\.\d+)deg\s*
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
            print('Failed to read device db')
    
    def run(self):
        print('OgnReader startup')
        while True:
            self.proc_rf = subprocess.Popen([config.ogn_rf_cmd, config.ogn_config], stdin=subprocess.PIPE)
            print('Started OGN-RF')
            self.proc_decode = subprocess.Popen([config.ogn_decode_cmd, config.ogn_config], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            print('Started OGN-Decode')
            try:
                for line in iter(self.proc_decode.stdout.readline, b''):
                    #print(line)
                    self.parse_line(line)
            except:
                print('OGN error.. restarting')
                self.proc_rf.kill()
                self.proc_decode.kill()
            print('OGN process finished. Restarting.')


    def parse_line(self, line):
        try:
            search = re.search(PATTERN_TELNET_50001, str(line))
            if search is not None:
                res = search.groupdict()
                #print(str(res))
                if res['address'] in self.ogn_devicedb:
                    res['registration'] = self.ogn_devicedb[res['address']]
                else:
                    res['registration'] = None
                self.callback(res)
        except:
            pass
        
