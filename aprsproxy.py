import threading
import socket
import select
import time
import datetime
import random
import logging


defaultAprsServers = ['glidern1.glidernet.org','glidern2.glidernet.org','glidern3.glidernet.org','glidern4.glidernet.org','glidern5.glidernet.org']

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, forwardAddrs, msgcallback):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.forwardAddrs = forwardAddrs
        self.msgcallback = msgcallback
        

    def tryAprsConnect(self):
        if self.forwardAddrs is None or len(self.forwardAddrs) == 0:
            return None

        host = random.choice(self.forwardAddrs)
        port = 14580
        if ':' in host:
            hp = host.split(':')
            host = hp[0]
            port = int(hp[1])
        
        try:
            sock = socket.socket()
            sock.connect((host, port))
            sock.setblocking(False)
            return sock
        except Exception as e:
            logging.error(f'Failed to connect to upstream APRS server {host}: {e}')
        return None


    def run(self):
        next_heartbeat = time.time() + 1

        clientSocket = self.tryAprsConnect()
        try:
            while clientSocket is None:
                # Standalone mode without forward connection because not configured or no internet
                self.conn.settimeout(next_heartbeat - time.time())
                try:
                    # Receive everything and ignore
                    data = self.conn.recv(1024)
                    self.msgcallback(data)
                    #print('Got APRS: ' + str(data))
                except socket.timeout:
                    pass
                if time.time() >= next_heartbeat:
                    #print('Send heartbeat...')
                    heartbeat = '# ogn2dump1090 1.0 %s OGN2DUMP1090 127.0.0.1:14580\r\n' % datetime.datetime.utcnow().isoformat()
                    self.conn.send(heartbeat.encode('utf-8'))
                    next_heartbeat = time.time() + 20
                    clientSocket = self.tryAprsConnect()
                    # %s %s %s %s %s\r\n"

            while clientSocket is not None:
                # Proxying mode with upstream APRS connection
                self.conn.setblocking(False)
                sockets = [clientSocket, self.conn]
                read_sockets, write_sockets, error_sockets = select.select(sockets, [], sockets)
                
                for s in error_sockets:
                    if s is clientSocket:
                        clientSocket.close()
                        clientSocket = None # Fall back to proxy mode
                        logging.error('Upstream APRS connection closed. Falling back to standalone mode')
                        break
                    elif s is self.conn:
                        raise Exception("downstream connection closed")

                if clientSocket is None: # break outer to get back to standalone mode
                    break

                for s in read_sockets:
                    if s is clientSocket:
                        data = clientSocket.recv(1024)
                        self.conn.send(data)
                    elif s is self.conn:
                        data = self.conn.recv(1024)
                        self.msgcallback(data)
                        try:
                            clientSocket.send(data)
                        except Exception as e:
                            logging.error('Upstream APRS connection error {e}. Falling back to standalone mode')
                            clientSocket.close()
                            clientSocket = None
                            break


        finally:
            self.conn.close()
            if clientSocket is not None:
                clientSocket.close()

    

class AprsProxy(threading.Thread):
    def __init__(self, msgcallback, forwardAddrs=defaultAprsServers):
        threading.Thread.__init__(self)
        self.forwardAddrs = forwardAddrs
        self.msgcallback = msgcallback
    
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', 14580))
        while True:
            sock.listen()
            conn, addr = sock.accept()
            ClientHandler(conn, addr, self.forwardAddrs, self.msgcallback).start()

