#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aprsproxy
import ognreader
import dump1090writer
import os
import argparse
import logging
import asyncio
import sys
import config

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class ogn2dump1090:
    def __init__(self):
        self.sbswriter = dump1090writer.Dump1090Writer()
        self.ognreader = ognreader.OgnReader(self.onParsedMsg)
        self.aprsserver = aprsproxy.AprsServer().onMessage(self.onAprsFromOgnDecode)
        self.aprsclient = aprsproxy.AprsClient(config.aprs_servers, config.aprs_subscribe_filter).onMessage(self.onAprsFromUpstream)

    async def start(self):
        await asyncio.gather(self.sbswriter.start(), self.ognreader.start(), self.aprsserver.start(), self.aprsclient.start())

    
    async def onParsedMsg(self, msgDict : dict):
        await self.sbswriter.send_msg(msgDict)
        
    
    async def onAprsFromOgnDecode(self, msg : bytes):
        #logging.debug(f"decode > {msg.decode('utf-8').strip()}")
        await self.ognreader.aprsmessage(msg)
        await self.aprsclient.sendMessage(msg)


    async def onAprsFromUpstream(self, msg : bytes):
        #logging.debug(f"upstream > {msg.decode('utf-8').strip()}")
        await self.ognreader.aprsmessage(msg)



if __name__ == '__main__':
    m = ogn2dump1090()
    asyncio.run(m.start())