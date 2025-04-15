import datetime
import random
import asyncio
import logging
from typing import Awaitable, Callable, List


defaultAprsServers = ['glidern1.glidernet.org','glidern2.glidernet.org','glidern3.glidernet.org','glidern4.glidernet.org','glidern5.glidernet.org']

class ClientHandler():
    clientReader : asyncio.StreamReader | None = None
    clientWriter : asyncio.StreamWriter | None = None
    upstreamReader : asyncio.StreamReader | None = None
    upstreamWriter : asyncio.StreamWriter | None = None

    forwardAddrs : List[str]
    msgCallback : Callable[[bytes], Awaitable[None]]




    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, forwardAddrs: List[str], msgCallback: Callable[[bytes], Awaitable[None]]):
        self.clientReader = reader
        self.clientWriter = writer
        self.forwardAddrs = forwardAddrs
        self.msgCallback = msgCallback


    def start(self):
        asyncio.create_task(self.upstreamConnector())
        asyncio.create_task(self.heartbeatSender())
        asyncio.create_task(self.readClient())

    def is_client_connected(self):
        return self.clientReader is not None and self.clientWriter is not None and not self.clientReader.at_eof() and not self.clientWriter.is_closing()
    
    def is_upstream_connected(self):
        return self.upstreamReader is not None and self.upstreamWriter is not None and not self.upstreamReader.at_eof() and not self.upstreamWriter.is_closing()

    async def heartbeatSender(self):
        await asyncio.sleep(20)
        while self.is_client_connected():
            if not self.is_upstream_connected():
                # Standalone - send heartbeat
                heartbeat = '# ogn2dump1090 1.0 %s OGN2DUMP1090 127.0.0.1:14580\r\n' % datetime.datetime.now(datetime.timezone.utc).isoformat()
                assert self.clientWriter is not None
                self.clientWriter.write(heartbeat.encode("utf-8"))
            await asyncio.sleep(20)

    async def upstreamConnector(self):
        if self.forwardAddrs is None or len(self.forwardAddrs) == 0:
            logging.info("No upstream APRS Server configured. Using standalone mode")

        while self.is_client_connected():
            try:
                host = random.choice(self.forwardAddrs)
                port = 14580
                if ':' in host:
                    hp = host.split(':')
                    host = hp[0]
                    port = int(hp[1])

                self.upstreamReader, self.upstreamWriter = await asyncio.open_connection(host, port)
                logging.info(f"Connected to upstream APRS Server {host}:{port}")
                while self.is_client_connected() and not self.upstreamReader.at_eof():
                    line = await self.upstreamReader.readline()
                    if line is None or not self.is_client_connected():
                        break
                    assert self.clientWriter is not None
                    self.clientWriter.write(line)

                logging.info(f"Upstream APRS Connection closed")
            except Exception as e:
                logging.warning(f"Upstream APRS connection error: {e}. Retrying in 10..")
            await asyncio.sleep(10)

    async def readClient(self):
        while self.is_client_connected():
            assert self.clientReader is not None
            line = await self.clientReader.readline()
            if line is None or not self.is_client_connected():
                break
            await self.msgCallback(line)

            if self.is_upstream_connected():
                assert self.upstreamWriter is not None
                self.upstreamWriter.write(line)
        
        # Client no longer connected. Close upstream
        if self.is_upstream_connected():
            logging.info("APRS client connection lost. Disconnecting upstream")
            assert self.upstreamWriter is not None
            self.upstreamWriter.close()
    



class AprsProxy():
    forwardAddrs : List[str]
    msgCallback : Callable[[bytes], Awaitable[None]]

    def __init__(self, msgcallback : Callable[[bytes], Awaitable[None]], forwardAddrs : List[str]=defaultAprsServers):
        self.forwardAddrs = forwardAddrs
        self.msgcallback = msgcallback
    
    async def start(self):
        await self.start_server()

    async def start_server(self):
        server = await asyncio.start_server(self.handle_client, "0.0.0.0", 14580)
        await server.serve_forever()

    
    async def handle_client(self, reader, writer):
        logging.info("APRS client connected")
        clientHandler = ClientHandler(reader, writer, self.forwardAddrs, self.msgcallback)
        clientHandler.start()
        
