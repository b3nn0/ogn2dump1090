#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aprsproxy
import ognreader
import dump1090writer
import os
import argparse
import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
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
    writer = dump1090writer.Dump1090Writer()
    writer.connect()

    # Start the OGN reader
    ogn_reader = ognreader.OgnReader(writer.send_msg)
    ogn_reader.start()
    
    # Start dummy APRS server
    aprsservers = args.aprsservers.split(',')
    aprs_proxy = aprsproxy.AprsProxy(ogn_reader.aprsmessage, forwardAddrs=aprsservers)
    aprs_proxy.start()


    logging.info('Startup complete')
