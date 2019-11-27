import threading
import socket
import time
import datetime

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
    def run(self):
        next_heartbeat = time.time() + 20
        try:
            while True:
                self.conn.settimeout(next_heartbeat - time.time())
                try:
                    # Receive everything and ignore
                    data = self.conn.recv(1024)
                    #print('Got APRS: ' + str(data))
                except socket.timeout:
                    pass
                if time.time() >= next_heartbeat:
                    #print('Send heartbeat...')
                    heartbeat = '# ogn2dump1090 1.0 %s OGN2DUMP1090 127.0.0.1:14580\r\n' % datetime.datetime.utcnow().isoformat()
                    self.conn.send(heartbeat.encode('utf-8'))
                    next_heartbeat = time.time() + 20
                    # %s %s %s %s %s\r\n"
        finally:
            self.conn.close()

    

class AprsServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', 14580))
        while True:
            sock.listen()
            conn, addr = sock.accept()
            ClientHandler(conn, addr).start()

