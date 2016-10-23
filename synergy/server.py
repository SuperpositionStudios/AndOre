import asyncio
import websockets
import requests
import json

erebus_address = 'http://localhost:7004'
public_address = 'localhost'
server_port = 7005

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
                    req = requests.get(erebus_address + '/get/username', params={'aid': attemped_aid}).json()
                    if req.get('valid_aid', False):
                        username = req.get('username', '')
                        aid = attemped_aid
                        await websocket.send(json.dumps({'author': 'Synergy', 'color': 'red', 'message': 'Hello'}))
                    else:
                        await websocket.send(json.dumps({'author': 'Synergy', 'color': 'red', 'message': "Invalid aid"}))
                else:
                    await websocket.send(json.dumps({'author': 'Synergy', 'color': 'red', 'message': "You must send over an aid first"}))
            else:
                if message[:6] == '/chat ':
                    await asyncio.wait([ws.send(json.dumps({'author': username, 'color': 'green', 'message': message[6:]})) for ws in connected])
                else:
                    await websocket.send(json.dumps({'author': 'Synergy', 'color': 'red', 'message': 'Unknown command "{}"'.format(message)}))
    finally:
        # Unregister.
        connected.remove(websocket)

print("Running Synergy on port {}".format(server_port))
start_server = websockets.serve(handler, public_address, server_port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


