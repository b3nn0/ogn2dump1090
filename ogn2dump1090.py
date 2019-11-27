#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aprsserver
import ognreader
import dump1090writer
import asyncore
import os

if __name__ == '__main__':
    dir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(dir)
    print('Switched to ' + dir)
    
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
