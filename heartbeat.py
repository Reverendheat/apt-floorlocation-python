#Check in with nodeJS Server
import asyncio
import socket
from config import settings

async def heartbeat(message, loop):
    reader, writer = await asyncio.open_connection(settings["DevServer"], settings["Port"],
                                                   loop=loop)
    writer.write(message.encode())
    data = await reader.read(100)
    writer.close()

hostname = socket.gethostname()
message = hostname + ' is online! ' + settings["Version"]
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(heartbeat(message, loop))
    loop.close()
except:
    print("Could not connect")