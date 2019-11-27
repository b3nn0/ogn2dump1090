import socket
import time
import sys
import os
import asyncore
import threading
import mlat.client.output
#import output
import math

class Dump1090Writer:
    def __init__(self):
        self.conn = None
        self.sock = None
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 30004))
        self.conn = mlat.client.output.BeastConnection(None, self.sock, socket.AF_INET, socket.SOCK_STREAM, ('127.0.0.1', 30004))
        
        #self.conn.connect_now()
        #self.conn.connected = True

    
    def send_msg(self, msg):
        # Format as beast message
        speed = float(msg['ground_speed']) * 1.94384 # m/s in kt
        track = math.radians(float(msg['track']))
        ns = speed * math.cos(track)
        ew = speed * math.sin(track)
        #print('send_position')
        self.conn.send_position(None, int(msg['address'], 16), float(msg['latitude']), float(msg['longitude']), float(msg['altitude']) * 3.28084,
            ns, ew, int(float(msg['climb_rate']) * 196.85), None, None, None, None, False, False)
        asyncore.loop(count=1)

if __name__ == '__main__':
    # Only for testing
    w = Dump1090Writer()
    w.connect()
    print(w.conn.connected)
    while True:
        w.send_msg({
            'pps_offset': '0.842',
            'frequency': '868.191',
            'aircraft_type': '8',
            'address_type': '2',
            'address': 'AAAAAA',
            'timestamp': '145021',
            'latitude': '+50.36201',
            'longitude': '+9.22168',
            'altitude': '555',
            'climb_rate': '+0.0',
            'ground_speed': '100',
            'track': '270.0',
            'turn_rate': '+0.0',
            'magic_number': '4',
            'gps_status': '03x05',
            'channel': '00',
            'flarm_timeslot': '_',
            'ogn_timeslot': 'o',
            'frequency_offset': '-9.23',
            'decode_quality': '50.8',
            'signal_quality': '67.0',
            'demodulator_type': '0',
            'error_count': '0',
            'distance': '0.0',
            'bearing': '000.0',
            'phi': '+80.4',
            'multichannel': None,
            'baro_altitude': None})
        time.sleep(0.1)