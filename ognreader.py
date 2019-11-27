import threading
import config
import subprocess
import re
import os
import json
import ogn.parser.telnet_parser
from ogn.parser.pattern import PATTERN_TELNET_50001

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
                if res['address'] in self.ogn_devicedb:
                    res['registration'] = self.ogn_devicedb[res['address']]
                else:
                    res['registration'] = None
                self.callback(res)
        except:
            pass
        
