import asyncio
import json
import logging
import socket
import config

class DroneAwareReader:
    def __init__(self, callback):
        self.callback = callback

    async def start(self):
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: DroneAwareProtocol(self.callback),
            local_addr=('0.0.0.0', config.DRONEAWARE_UDP_PORT)
        )
        logging.info(f"DroneAware UDP reader started on port {config.DRONEAWARE_UDP_PORT}")
        try:
            await asyncio.Future()  # run forever
        finally:
            transport.close()

class DroneAwareProtocol(asyncio.DatagramProtocol):
    def __init__(self, callback):
        self.callback = callback

    def datagram_received(self, data, addr):
        try:
            msg = json.loads(data.decode('utf-8'))
            # Map DroneAware fields to the expected format for dump1090writer
            # DroneAware: {"t":1745000000.0,"mac":"fa:0b:bc:12:34:56","radio":"wifi_beacon","rssi":-68,"type":"Location/Vector","lat":40.7128,"lon":-74.0060,"alt":120.5,"speed":8.25,"hdg":270.0,"id":null}
            
            # Convert MAC to integer address and mangle to 24 bits for ADS-B compatibility
            mac = msg.get("mac", "")
            if mac:
                try:
                    addr = int(mac.replace(':', ''), 16) & 0xFFFFFF
                except ValueError:
                    addr = 0
            else:
                addr = 0

            # Map fields
            msg_dict = {
                "address": addr,
                "lat": msg.get("lat"),
                "lon": msg.get("lon"),
                "altFt": msg.get("alt") * 3.28084 if msg.get("alt") is not None else None,
                "speedKt": msg.get("speed") * 1.94384 if msg.get("speed") is not None else None,
                "track": msg.get("hdg"),
                "registration": msg.get("id"), # DroneAware 'id' seems to be the registration/id
                "squawk": "", # DroneAware doesn't seem to provide squawk in this sample
                "climbRateFtMin": None,
            }
            
            # Add timestamp if not present, though DroneAware provides 't'
            if "t" in msg:
                msg_dict["rcvts"] = msg["t"]

            asyncio.create_task(self.callback(msg_dict))
        except Exception as e:
            logging.error(f"Error parsing DroneAware message: {e}")
