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

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

async def main():
    #import ptvsd; ptvsd.enable_attach(address=('0.0.0.0', 3000)); ptvsd.wait_for_attach()
    parser = argparse.ArgumentParser(prog='ogn2dump1090')
    parser.add_argument('-a', '--aprs-servers',
        help='List of upstream APRS servers. Defaults to glidern1-5.glidernet.org. Use -a \'\' to not connect to upstream APRS',
        default='glidern1.glidernet.org,glidern2.glidernet.org,glidern3.glidernet.org,glidern4.glidernet.org,glidern5.glidernet.org',
        dest='aprsservers',
        type=str)
    args = parser.parse_args()

    
    d = os.path.abspath(os.path.dirname(__file__))
    os.chdir(d)
    logging.info('Switched to ' + d)
    logging.info('Starting up')

    # dump1090 writer
    w = dump1090writer.Dump1090Writer()
    writer = w.start()

    # Start the OGN reader
    r = ognreader.OgnReader(w.send_msg)
    ogn_reader = r.start()
    
    # Start dummy APRS server
    aprsservers = args.aprsservers.split(',')
    a = aprsproxy.AprsProxy(r.aprsmessage, forwardAddrs=aprsservers)
    aprs_proxy = a.start()

    await asyncio.gather(writer, ogn_reader, aprs_proxy)


    logging.info('Startup complete')


if __name__ == '__main__':
    asyncio.run(main())