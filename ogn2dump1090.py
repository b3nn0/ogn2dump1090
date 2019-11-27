#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aprsserver
import ognreader
import dump1090writer
import asyncore
import os

if __name__ == '__main__':
    #import ptvsd; ptvsd.enable_attach(address=('0.0.0.0', 3000)); ptvsd.wait_for_attach()
    
    d = os.path.abspath(os.path.dirname(__file__))
    os.chdir(d)
    print('Switched to ' + d)
    print('Starting up')
    
    # Start dummy APRS server
    aprs_server = aprsserver.AprsServer()
    aprs_server.start()

    # dump1090 writer
    writer = dump1090writer.Dump1090Writer()
    writer.connect()

    # Start the OGN reader
    ogn_reader = ognreader.OgnReader(writer.send_msg)
    ogn_reader.start()
    print('Startup complete')
