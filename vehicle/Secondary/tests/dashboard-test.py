import asyncio
import json
import websockets
from random import randint

def generateDashState():
    dashState = {}
    dashState['speedSI'] = randint(0, 30)

    return json.dumps(dashState)

async def echo(websocket, path):
    print("Began Connection")
    while True:
        await websocket.send(str(generateDashState()))

asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 8765))
asyncio.get_event_loop().run_forever()
