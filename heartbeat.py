#Check in with nodeJS Server
import asyncio
import socket

async def heartbeat(message, loop):
    reader, writer = await asyncio.open_connection('192.168.20.2', 10000,
                                                   loop=loop)
    writer.write(message.encode())
    data = await reader.read(100)
    writer.close()

hostname = socket.gethostname()
message = hostname + ' is online!'
loop = asyncio.get_event_loop()
loop.run_until_complete(heartbeat(message, loop))
loop.close()