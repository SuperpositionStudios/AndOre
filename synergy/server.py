import asyncio
import html
import json
import requests
import websockets
import os
import string

erebus_address = 'http://localhost:7004'
public_address = 'localhost'
server_port = 7005

connected = set()


def path_to_this_files_directory():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path + '/'

# Generate whitelisted_words set
with open(path_to_this_files_directory() + 'word_whitelist.json') as json_data:
    d = json.load(json_data)
    whitelisted_words = set()

    # List of characters we're excluding (punctuation)
    punctiation_set = set(string.punctuation)
    punctiation_set.add('"')
    punctiation_set.add("'")
    punctiation_set.add('-')

    # Looping through all the stories in the json file
    stories = d.get('stories', [])
    for story in stories:
        sanitized_string = ''.join(ch for ch in story if ch not in punctiation_set)  # Removing the punctuation from the story
        sanitized_string = sanitized_string.lower()
        whitelisted_words = whitelisted_words | set(sanitized_string.split(' '))  # Merging sets

    # Adding the whitelisted words to our set
    whitelisted_words = whitelisted_words | set(d.get('approved_words', []))

    # Adding the game specific words to our set
    whitelisted_words = whitelisted_words | set(d.get('game_terms', []))

    # For our information
    whitelisted_words.remove('')
    whitelisted_words.remove(' ')
    print("Whitelist includes {} words".format((whitelisted_words.__len__())))


def filter_word(word: str):
    sanitized_word = str(word).lower()
    sanitized_word = ''.join(ch for ch in sanitized_word if ch not in punctiation_set)
    try:
        val = int(sanitized_word)
        return val
    except ValueError:
        if sanitized_word in whitelisted_words:
            return word
        else:
            return 'heck'


def filter_sentence(sentence: str):
    words = sentence.split(' ')
    new_words = []
    for word in words:
        new_words.append(filter_word(word))
    new_sentence = ""
    for word in new_words:
        new_sentence += word + " "
    return new_sentence


def dumps(obj: dict):
    try:
        return json.dumps(obj)
    except:
        return "{}"


def loads(obj: str):
    try:
        return json.loads(obj)
    except:
        return {}


def get_username(aid):
    req = requests.get('http://localhost:7004/get/username', params={'aid': aid}).json()
    return req

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
                    erebus_response = get_username(message[10:])
                    if erebus_response.get('valid_aid', False):
                        username = erebus_response.get('username', '')
                        aid = message[10:]
                        await websocket.send(dumps({
                            'author': 'Synergy',
                            'color': 'red',
                            'authenticated': True,
                            'message': 'Welcome to And/Ore. Official Accounts have red names.'
                        }))
                    else:
                        await websocket.send(dumps({
                            'author': 'Synergy',
                            'color': 'red',
                            'authenticated': False,
                            'message': "Invalid aid"
                        }))
                else:
                    await websocket.send(dumps({
                        'author': 'Synergy',
                        'color': 'red',
                        'message': "You must send over an aid first"
                    }))
            else:
                if message[:6] == '/chat ':
                    await asyncio.wait([ws.send(dumps({
                        'author': username,
                        'color': 'green',
                        'message': html.escape(filter_sentence(message[6:]))
                    })) for ws in connected])
                else:
                    await websocket.send(json.dumps({
                        'author': 'Synergy',
                        'color': 'red',
                        'message': 'Unknown command "{}"'.format(html.escape(message))
                    }))
    finally:
        # Unregister.
        connected.remove(websocket)

print("Running Synergy on port {}".format(server_port))
start_server = websockets.serve(handler, public_address, server_port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
