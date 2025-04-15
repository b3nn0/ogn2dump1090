import time
import math
import config
import logging
import asyncio

class Dump1090Writer:
    msgqueue : asyncio.Queue

    def __init__(self):
        self.msgqueue = asyncio.Queue()
    
    async def start(self):
        await self.msgsender()
        

    async def msgsender(self):
        while True:
            try:
                reader, writer = await asyncio.open_connection(config.sbs_destination_host, config.sbs_destination_port)
                logging.info(f"SBS Out connection to {config.sbs_destination_host}:{config.sbs_destination_port} established")
                while True:
                    msg = await self.msgqueue.get()
                    if writer.is_closing():
                        self.msgqueue = asyncio.Queue()
                        raise Exception("Connection unexpectedly closed")

                    writer.write(msg)
            except Exception as e:
                logging.info("No SBS Out connection. Retry in 5...: " + str(e))
            await asyncio.sleep(5)

    
    async def send_msg(self, address : int, lat : float, lon : float, altFt : float|None, speedKt : float|None,
            climbRateFtMin : float|None = None, track : float|None = None, registration : str ='', anon : bool = False, addrtype : int = 0):
        now = time.time()
        rcvts = now # todo

        addrTypeStr = '~' if anon or addrtype != 1 else ''

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

        altFtStr = int(altFt) if altFt is not None else ''
        speedKtStr = int(speedKt) if speedKt is not None else ''
        trackStr = int(track) if track is not None else ''
        altclimbRateFtMinStr = int(climbRateFtMin) if climbRateFtMin is not None else ''

        msg = f"MSG,3,1,1,{addrTypeStr}{address:06X},1,{rcv_date},{rcv_time},{now_date},{now_time},{registration},{altFtStr},{speedKtStr},{trackStr},{lat},{lon},{altclimbRateFtMinStr},{squawk},{fs},{emerg},{ident},{aog}\n"
        while self.msgqueue.qsize() > 10: # Don't queue data that's too old
            await self.msgqueue.get()
        await self.msgqueue.put(msg.encode("utf-8"))
        


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

async def main():

    import ognreader
    # Only for testing
    w = Dump1090Writer()
    asyncio.create_task(w.start())

    r = ognreader.OgnReader(w.send_msg)
    while True:
        await r.aprsmessage(b"ICA39D2B0>OGADSB:/120154h4848.01N/01258.60E^/A=040787 !W78! id0139D2B0 FL400.00")
        await r.aprsmessage(b"ICA4CA766>OGADSB:/120414h4732.39N/01024.60E^/A=038787 !W61! id254CA766 FL380.00 A3:RYR17PJ")
        #await r.aprsmessage(b"ICA4BAA85>OGADSB:/104518h5014.85N/00925.61E^297/417/A=035793 !W48! id254BAA85 -64fpm FL359.75 A3:THY7DH Sq3203")
        #await r.aprsmessage(b"ICA3D24FE>OGFLR,qAS:/085537h4812.03N/00748.45E'209/087/A=003754 !W04! id053D24FE +099fpm +0.0rot 0.0dB 1e +4.0kHz gps1x2")
        #await r.aprsmessage(b"PAW404BF0>OGPAW,qAS:/085536h4913.52N\\01244.77E^117/082/A=004049 !W60! id21404BF0 15.5dB +10.0kHz")
        #await r.aprsmessage(b"FNT11189E>OGNFNT,qAS:/085536h4731.16N\\01226.94En !W36! id3E11189E FNT71 sF1 cr4 5.4dB -19.4kHz 4e")
        #await r.aprsmessage(b"FNT0113A5>OGNFNT,qAS:/085536h4727.91N/01232.96Eg090/020/A=003977 !W38! id1F0113A5 -314fpm FNT11 sF1 cr4 -0.6dB -17.9kHz")
        #await r.aprsmessage(b"OGN2D4072>OGNTRK,qAS:/085535h5025.64N/01610.00E'032/059/A=002786 !W40! id0B2D4072 +416fpm -1.8rot 2.8dB 6e -7.7kHz gps3x5")
        #await r.parse_line(b"0.567sec:868.393MHz: 3:25A33C 110606: [ +48.35199, +10.21162]deg   485m  +0.0m/s   0.0m/s 000.0deg   -.-      __0 03x15m L_:___o_ -7.02kHz 52.2/67.5dB/0  0e     0.0km 000.0deg -43.3deg")
        #await r.parse_line(b"0.117sec:868.193MHz: 1:3:25A33C 110606: [ +48.35199, +10.21161]deg   481m  +0.0m/s   0.0m/s 000.0deg  +0.0deg/s __0 03x05m F :00_o_ -7.04kHz 52.5/66.0dB/0  0e     0.0km 000.0deg -49.1deg           B0613")
        await asyncio.sleep(1)
    


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    asyncio.run(main())