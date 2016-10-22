import asyncio
import websockets
import requests

erebus_address = 'http://localhost:7004'
sleipnir_address = 'http://localhost:'
public_address = 'localhost'
server_port = 8101

connected = set()

async def handler(websocket, path):
    global connected
    # Register.
    connected.add(websocket)
    try:
        # Implement logic here.
        aid = None
        username = None
        while True:
            message = await websocket.recv()
            if aid is None:
                if message[:10] == '/register ':
                    attemped_aid = message[10:]
                    req = requests.get('http://localhost:7004/get/username', params={'aid': attemped_aid}).json()
                    if req.get('valid_aid', False):
                        username = req.get('username', '')
                        aid = attemped_aid
                        await websocket.send("Welcome {}".format(username))
                    else:
                        await websocket.send("Invalid aid")
                else:
                    await websocket.send("You must send over an aid first")
            else:
                if message[:6] == '/chat ':
                    await asyncio.wait([ws.send(username + ": " + message[6:]) for ws in connected])
    finally:
        # Unregister.
        connected.remove(websocket)

start_server = websockets.serve(handler, public_address, server_port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


