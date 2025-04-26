import datetime
import random
import asyncio
import logging
from typing import Awaitable, Callable, List


defaultAprsServers = ['glidern1.glidernet.org','glidern2.glidernet.org','glidern3.glidernet.org','glidern4.glidernet.org','glidern5.glidernet.org']


class AprsClient:
    serverAddrs : List[str]
    aprsMessage : str | None

    msgCallback : Callable[[bytes], Awaitable[None]]
    upstreamReader : asyncio.StreamReader | None = None
    upstreamWriter : asyncio.StreamWriter | None = None

    def __init__(self, serverAddrs : List[str] = defaultAprsServers, aprsMessage : str | None = None):
        self.serverAddrs = serverAddrs
        self.aprsMessage = aprsMessage


    def onMessage(self, msgCallback : Callable[[bytes], Awaitable[None]]):
        self.msgCallback = msgCallback
        return self


    async def start(self):
        await self.upstreamConnector()
    
    async def upstreamConnector(self):
        if self.serverAddrs is None or len(self.serverAddrs) == 0:
            logging.info("No upstream APRS Server configured. Using standalone mode")
            return
        
        while True:
            try:
                host = random.choice(self.serverAddrs)
                port = 14580
                if ':' in host:
                    hp = host.split(':')
                    host = hp[0]
                    port = int(hp[1])

                self.upstreamReader, self.upstreamWriter = await asyncio.open_connection(host, port)
                logging.info(f"Connected to upstream APRS Server {host}:{port}")
                if self.aprsMessage is not None:
                    await self.sendMessage((self.aprsMessage + "\n").encode("utf-8"))

                while not self.upstreamReader.at_eof():
                    line = await self.upstreamReader.readline()
                    if not line:
                        break
                    if self.msgCallback:
                        await self.msgCallback(line)
                    

                logging.info(f"Upstream APRS Connection closed. Retrying in 10...")
            except Exception as e:
                logging.warning(f"Upstream APRS connection error: {e}. Retrying in 10...")
            self.upstreamWriter = None
            await asyncio.sleep(10)

    async def sendMessage(self, msg : bytes):
        if self.upstreamWriter is not None and not self.upstreamWriter.is_closing():
            self.upstreamWriter.write(msg)

class AprsServer:
    msgCallback : Callable[[bytes], Awaitable[None]]

    def __init__(self):
        pass

    def onMessage(self, msgCallback : Callable[[bytes], Awaitable[None]]):
        self.msgCallback = msgCallback
        return self

    
    async def start(self):
        await self.start_server()

    async def start_server(self):
        server = await asyncio.start_server(self.handle_client, "0.0.0.0", 14580)
        await server.serve_forever()

    
    async def handle_client(self, reader, writer):
        logging.info("APRS client connected")
        clientHandler = ClientHandler(reader, writer, self.msgCallback)
        clientHandler.start()


        
class ClientHandler:
    clientReader : asyncio.StreamReader | None = None
    clientWriter : asyncio.StreamWriter | None = None
    msgCallback : Callable[[bytes], Awaitable[None]]


    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, msgCallback: Callable[[bytes], Awaitable[None]]):
        self.clientReader = reader
        self.clientWriter = writer
        self.msgCallback = msgCallback


    def start(self):
        asyncio.create_task(self.heartbeatSender())
        asyncio.create_task(self.readClient())

    def is_client_connected(self):
        return self.clientReader is not None and self.clientWriter is not None and not self.clientReader.at_eof() and not self.clientWriter.is_closing()


    async def heartbeatSender(self):
        await asyncio.sleep(20)
        while self.is_client_connected():
            assert self.clientWriter is not None
            heartbeat = '# ogn2dump1090 1.0 %s OGN2DUMP1090 127.0.0.1:14580\r\n' % datetime.datetime.now(datetime.timezone.utc).isoformat()
            self.clientWriter.write(heartbeat.encode("utf-8"))
            await asyncio.sleep(20)


    async def readClient(self):
        while self.is_client_connected():
            assert self.clientReader is not None
            line = await self.clientReader.readline()
            if line is None or not self.is_client_connected():
                break
            if self.msgCallback:
                await self.msgCallback(line)
