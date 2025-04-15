import threading
from typing import Awaitable, Callable
import config
import subprocess
import re
import os
import socket
import json
import logging
import time
import ogn.parser
import asyncio


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

class OgnReader():
    callback : Callable[[int, float, float, float, float, float, float, str, bool, int], Awaitable[None]]
    ogn_devicedb : dict[str, str]

    def __init__(self, callback):
        self.callback = callback
        self.ogn_devicedb = {}
        self.read_ognddb()

    async def start(self):
        if config.TELNET_SERVER_HOST is None or config.TELNET_SERVER_HOST == "":
            logging.info("Ogn telnet reader disabled")
            return

        await self.ognreader()
    
    async def ognreader(self):
        while True:
            try:
                reader, writer = await asyncio.open_connection(config.TELNET_SERVER_HOST, config.TELNET_SERVER_PORT)
                logging.info('OGN telnet connection established')
                while True:
                    line = await reader.readline()
                    if not line:
                        raise Exception("EOF")
                    
                    await self.parse_line(line.strip())


            except Exception as e:
                logging.info('Telnet connection closed. Retrying in 5... Error: ' + str(e))
                await asyncio.sleep(5)

    
    
    def read_ognddb(self):
        try:
            ddb = json.loads(open('ddb.json', 'r').read())
            for dev in ddb['devices']:
                devid = dev['device_id']
                call = dev['registration']
                self.ogn_devicedb[devid] = call
        except:
            logging.warn('Failed to read device db')
    

    async def parse_line(self, line):
        try:
            search = re.search(PATTERN_TELNET_50001, str(line))
            if search is not None:
                msg = search.groupdict()
                addrStr = msg['address']
                addr = int(addrStr, 16)

                addrtype = msg.get('address_type', None)
                addrtype = 0 if addrtype is None else int(addrtype[0])
                lat = float(msg['latitude'])
                lon = float(msg['longitude'])
                altFt = float(msg['altitude']) * 3.28084 # in ft
                speedKt = float(msg['ground_speed']) * 1.94384 # m/s in kt
                climb = int(float(msg['climb_rate']) * 196.85)
                track = float(msg['track'])
                anon = False
                if msg['address'].lower()[0:2] == 'dd' or msg['address'].lower()[0:1] == '1':
                    anon = True

                registration = ''
                if msg['address'] in self.ogn_devicedb:
                    registration = self.ogn_devicedb[msg['address']]
                #logging.info("TELNET " + addrStr)
                await self.callback(addr, lat, lon, altFt, speedKt, climb, track, registration, anon, addrtype)
        except Exception as e:
            pass

    async def aprsmessage(self, msg):
        strmsgs = msg.decode('utf-8')
        if len(strmsgs) == 0:
            return
        for strmsg in strmsgs.splitlines():
            try:
                if ":" not in strmsg:
                    continue # ???
                # python ogn lib doesn't like that there is no receiver string in our local messages.. fake one in
                while strmsg.split(':')[0].count(',') <= 1:
                    strmsg = strmsg.replace(':', ',XXX:', 1)


                msg = ogn.parser.parse(strmsg)
                if msg['aprs_type'] != 'position' or msg.get('altitude') is None:
                    return
                addrStr = msg['address'] if 'address' in msg else msg['name'][3:]
                addr = int(addrStr, 16)
                lat = msg['latitude']
                lon = msg['longitude']
                track = msg['track']
                altFt = msg['altitude'] * 3.28084 # in ft

                speedKt = msg.get('ground_speed', 0) if msg.get('ground_speed') is not None else 0
                climb = msg.get('climb_rate', 0) * 3.28084 if msg.get('climb_rate') is not None else 0

                anon = False
                if addrStr.lower()[0:2] == 'dd' or addrStr.lower()[0:1] == '1':
                    anon = True

                registration = ''
                if addrStr in self.ogn_devicedb:
                    registration = self.ogn_devicedb[addrStr]

                addrtype = msg.get('address_type', '0')
                addrtype = 0 if addrtype is None else int(addrtype)

                #logging.info("APRS " + addrStr)
                await self.callback(addr, lat, lon, altFt, speedKt, climb, track, registration, anon, addrtype)
            except Exception as e:
                logging.warn(f'not parsable as APRS message: ' + str(e))

        
