import socket
import time
import sys
import os
import threading
import math
import config


class Dump1090Writer:
    def __init__(self):
        self.sock = None
    
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((config.sbs_destination_host, config.sbs_destination_port))
        except:
            self.sock = None
            print('Cannot connect to dump1090 (yet?)')
        


    
    def send_msg(self, address, lat, lon, altFt, speedKt, climbRateFtMin=0, track=0, registration='', anon=False, addrtype=0):
        if self.sock is None:
            self.connect()
        if self.sock is None:
            return

        now = time.time()
        rcvts = now # todo

        if anon or addrtype != 1:
            addrtype = '~'
        else:
            addrtype = ''

        rcv_date = self.format_date(rcvts)
        rcv_time = self.format_time(rcvts)
        now_date = self.format_date(now)
        now_time = self.format_time(now)
        squawk = ""
        fs = ""
        emerg = ""
        ident = ""
        aog = ""
        # readsb doesn't like - in registration (D-XXX -> DXXX)
        registration = self.csv_quote(self.sanitize(registration))

        msg = f"MSG,3,1,1,{addrtype}{address:06X},1,{rcv_date},{rcv_time},{now_date},{now_time},{registration},{int(altFt)},{int(speedKt)},{int(track)},{lat},{lon},{int(climbRateFtMin)},{squawk},{fs},{emerg},{ident},{aog}\n"
        try:
            #print(msg)
            self.sock.send(msg.encode("utf-8"))
        except Exception as e:
            print('Failed to send SBS message: ' + str(e))
            self.sock = None


    def format_time(self, timestamp):
        return time.strftime("%H:%M:%S", time.gmtime(timestamp)) + ".{0:03.0f}".format(math.modf(timestamp)[0] * 1000)


    def format_date(self, timestamp):
        return time.strftime("%Y/%m/%d", time.gmtime(timestamp))

    def csv_quote(self, s):
        if s is None:
            return ''
        if s.find('\n') == -1 and s.find('"') == -1 and s.find(',') == -1:
            return s
        else:
            return '"' + s.replace('"', '""') + '"'
    
    def sanitize(self, s):
        return ''.join(c for c in s if c.isalnum())

if __name__ == '__main__':
    import ognreader
    # Only for testing
    w = Dump1090Writer()
    w.connect()

    r = ognreader.OgnReader(w.send_msg)
    while True:
        r.aprsmessage(b"ICA4BAA85>OGADSB:/104518h5014.85N/00925.61E^297/417/A=035793 !W48! id254BAA85 -64fpm FL359.75 A3:THY7DH Sq3203")
        r.aprsmessage(b"ICA3D24FE>OGFLR,qAS:/085537h4812.03N/00748.45E'209/087/A=003754 !W04! id053D24FE +099fpm +0.0rot 0.0dB 1e +4.0kHz gps1x2")
        r.aprsmessage(b"PAW404BF0>OGPAW,qAS:/085536h4913.52N\\01244.77E^117/082/A=004049 !W60! id21404BF0 15.5dB +10.0kHz")
        r.aprsmessage(b"FNT11189E>OGNFNT,qAS:/085536h4731.16N\\01226.94En !W36! id3E11189E FNT71 sF1 cr4 5.4dB -19.4kHz 4e")
        r.aprsmessage(b"FNT0113A5>OGNFNT,qAS:/085536h4727.91N/01232.96Eg090/020/A=003977 !W38! id1F0113A5 -314fpm FNT11 sF1 cr4 -0.6dB -17.9kHz")
        r.aprsmessage(b"OGN2D4072>OGNTRK,qAS:/085535h5025.64N/01610.00E'032/059/A=002786 !W40! id0B2D4072 +416fpm -1.8rot 2.8dB 6e -7.7kHz gps3x5")
        r.aprsmessage(b"ICA25A33C>OGFLR,qOR:/113138h4821.11N/01012.70E'000/000/A=001631 !W72! id0525A33C +000fpm +0.0rot 53.5dB -8.1kHz gps3x5")
        time.sleep(1)
