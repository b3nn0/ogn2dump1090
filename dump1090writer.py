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
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 30004))
            self.conn = mlat.client.output.BeastConnection(None, self.sock, socket.AF_INET, socket.SOCK_STREAM, ('127.0.0.1', 30004))
            #self.conn = mlat.client.output.BasestationConnection(None, self.sock, socket.AF_INET, socket.SOCK_STREAM, ('127.0.0.1', 30004))
        except:
            print('Cannot connect to dump1090 (yet?)')
        
        #self.conn.connect_now()
        #self.conn.connected = True

    
    def send_msg(self, address, lat, lon, altFt, speedKt, climbRateFtMin=0, track=0, registration=None, anon=False):
        if self.conn is None or not self.conn.connected:
            self.connect()

        # Format as beast message
        track = math.radians(track)
        ns = speedKt * math.cos(track)
        ew = speedKt * math.sin(track)

        self.conn.send_position(None, address, lat, lon, altFt,
            ns, ew, climbRateFtMin, registration, None, None, None, anon, False)
        asyncore.loop(count=1)

if __name__ == '__main__':
    import ognreader
    # Only for testing
    w = Dump1090Writer()
    w.connect()

    r = ognreader.OgnReader(w.send_msg)
    while True:
        r.aprsmessage(b"ICA3D24FE>OGFLR,qAS,Kippenhm:/085537h4812.03N/00748.45E'209/087/A=003754 !W04! id053D24FE +099fpm +0.0rot 0.0dB 1e +4.0kHz gps1x2")
        r.aprsmessage(b"PAW404BF0>OGPAW,qAS,reg3:/085536h4913.52N\\01244.77E^117/082/A=004049 !W60! id21404BF0 15.5dB +10.0kHz")
        r.aprsmessage(b"FNT11189E>OGNFNT,qAS,LOIJ:/085536h4731.16N\\01226.94En !W36! id3E11189E FNT71 sF1 cr4 5.4dB -19.4kHz 4e")
        r.aprsmessage(b"FNT0113A5>OGNFNT,qAS,LOIJ:/085536h4727.91N/01232.96Eg090/020/A=003977 !W38! id1F0113A5 -314fpm FNT11 sF1 cr4 -0.6dB -17.9kHz")
        r.aprsmessage(b"OGN2D4072>OGNTRK,qAS,LKPN:/085535h5025.64N/01610.00E'032/059/A=002786 !W40! id0B2D4072 +416fpm -1.8rot 2.8dB 6e -7.7kHz gps3x5")
        time.sleep(1)
