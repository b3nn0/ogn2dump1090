import asyncio
import logging
import config
import aiohttp





class AviationWeather():
    gnssBaroDiffFt : float = 0


    async def run(self):
        if not hasattr(config, "metar_source") or config.metar_source is None or len(config.metar_source) != 4:
            logging.info("No metar source defined. Using GNSS altitudes")
            return
        
        while True:
            try:
                logging.info("Updating METAR...")
                await self.fetch_data()
                await asyncio.sleep(30 * 60)
            except Exception as e:
                logging.warning("Failed to fetch METAR: " + str(e) + ", retrying in 3 minutes")
                await asyncio.sleep(3 * 60)
                
    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://aviationweather.gov/api/data/metar?ids={config.metar_source}") as resp:
                text = await resp.text()
                logging.info(f"METAR for {config.metar_source} received: {text.strip()}")
                elems = text.split(" ")
                for elem in elems:
                    elem = elem.strip()
                    if (len(elem) == 4 or len(elem) == 5) and elem[0] == "Q":
                        qnh = int(elem[1:])
                        pressureDiff = 1013 - qnh
                        self.gnssBaroDiffFt = -pressureDiff * 28
                        logging.info(f"gnssBaroDiff: {self.gnssBaroDiffFt}ft")


