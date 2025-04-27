import datetime
import random
import asyncio
import logging
from typing import Awaitable, Callable, List


defaultAprsServers = ['glidern1.glidernet.org','glidern2.glidernet.org','glidern3.glidernet.org','glidern4.glidernet.org','glidern5.glidernet.org']


class AprsClient:
    serverAddrs : List[str]
    aprsFilter : str

    msgCallback : Callable[[bytes], Awaitable[None]]
    upstreamReader : asyncio.StreamReader | None = None
    upstreamWriter : asyncio.StreamWriter | None = None

    reconnectImmediate : bool = False

    aprsUser : str = "anon"
    aprsPass : str = "-1"

    def __init__(self, serverAddrs : List[str] = defaultAprsServers, aprsFilter : str | None = None):
        self.serverAddrs = serverAddrs
        if aprsFilter is None or len(aprsFilter) == 0:
            self.aprsFilter = "g/ALL"
        else:
            self.aprsFilter = aprsFilter


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
            err = None
            try:
                host = random.choice(self.serverAddrs)
                port = 14580
                if ':' in host:
                    hp = host.split(':')
                    host = hp[0]
                    port = int(hp[1])

                self.upstreamReader, self.upstreamWriter = await asyncio.open_connection(host, port)
                logging.info(f"Connected to upstream APRS Server {host}:{port}")
                aprsLogin = f"user {self.aprsUser} pass {self.aprsPass} vers ogn2dump1090 0.0.1 filter {self.aprsFilter}\n"
                logging.info(f"logging in: {aprsLogin.strip()}")
                self.upstreamWriter.write(aprsLogin.encode("utf-8"))

                while not self.upstreamReader.at_eof():
                    line = await self.upstreamReader.readline()
                    if not line:
                        break
                    if self.msgCallback:
                        await self.msgCallback(line)
                    
            except Exception as e:
                err = e

            self.upstreamWriter = None
            if self.reconnectImmediate:
                self.reconnectImmediate = False
                logging.info(f"Upstream connection intentionally closed. Reconnecting...")
            else:
                logging.warning(f"Upstream APRS Connection closed: {err}. Retrying in 10...")
                await asyncio.sleep(10)


    async def sendMessage(self, msg : bytes):
        # Try to parse login data from ogn-decode if given. Otherwise APRS server will eventually cut us off
        # if we stay on anon/-1.
        # Once we have the data, force a reconnect once
        msgStr = msg.decode("utf-8")
        if msgStr.startswith("user"):
            msgSplit = msgStr.split(" ")
            changed = self.aprsUser != msgSplit[1]
            self.aprsUser = msgSplit[1]
            self.aprsPass = msgSplit[3]
            if changed and self.upstreamWriter is not None:
                self.reconnectImmediate = True
                self.upstreamWriter.close()
                return # Wait for reconnect

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
