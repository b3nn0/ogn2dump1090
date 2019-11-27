#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aprsserver
import ognreader
import dump1090writer
import asyncore

if __name__ == '__main__':
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
