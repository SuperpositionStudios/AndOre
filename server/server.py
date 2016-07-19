from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import uuid, random
app = Flask(__name__)

web_server_domain = "*"
world_size = {
    "row": 31,
    "col": 32  # an extra row is added in send state with player stats
}


class Cell:
    def __init__(self):
        self.contents = []
        empty_space = EmptySpace()
        self.contents.append(empty_space)

    def add_object(self, x):
        self.contents.append(x)

    def add_ore_deposit(self):
        a = OreDeposit()
        self.contents.append(a)

    def remove_object(self, object_id):
        for i in range(0, len(self.contents)):
            if self.contents[i].obj_id == object_id:
                del self.contents[i]

    def contains_object_type(self, obj_type_name):
        for obj in self.contents:
            if obj.__class__.__name__ == obj_type_name:
                return True

    def render(self):
        priority = ['Player', 'OreDeposit', 'EmptySpace']
        for i in priority:
            if self.contains_object_type(i):
                for obj in self.contents:
                    if obj.__class__.__name__ == i:
                        return obj.icon


class GameObject:
    def __init__(self):
        self.obj_id = str(uuid.uuid4())


class OreDeposit(GameObject):

    def __init__(self):
        super().__init__()
        self.icon = '$'


class EmptySpace(GameObject):
    def __init__(self):
        self.icon = '#'


class World:
    def __init__(self):
        self.world = []
        row = []
        for l in range(0, world_size['col']):
            a = Cell()
            row.append(a)
        for l in range(0, world_size['row']):
            self.world.append(row)

        print(len(self.world))

    def get_world(self):
        rendered_world = []
        e_r = []
        for l in range(0, world_size['col']):
            e_r.append(" ")

        for l in range(0, world_size['row']):
            rendered_world.append(e_r)

        for row in range(0, world_size['row']):
            for col in range(0, world_size['col']):
                rendered_world[row][col] = self.world[row][col].render()
                #print(row)
                #print(col)
                #print(self.world[row][col].render())
        return rendered_world


world = World()
world.world[4][4].add_ore_deposit()


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = web_server_domain
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
    return return_response


def generate_starting_x_position():
    return random.randint(0, world_size["row"])


def generate_starting_y_position():
    return random.randint(0, world_size["col"])


def move_in_bounds(pos, axis):
    if axis == 'col':
        if pos < 0:
            return 0
        elif pos > world_size['col']:
            return world_size['col']
        else:
            return pos
    elif axis == 'row':
        if pos < 0:
            return 0
        elif pos > world_size['row']:
            return world_size['row']
        else:
            return pos


class Player:

    def __init__(self, id):
        self.id = id
        self.health = 100
        self.ore_quantity = 0
        self.inner_icon = '@'
        self.icon = '!'
        self.x_position = generate_starting_x_position()
        self.y_position = generate_starting_y_position()

    def input(self, dir):
        if dir == 'w':
            self.y_position = move_in_bounds(self.y_position + 1, 'col')
        elif dir == 's':
            self.y_position = move_in_bounds(self.y_position - 1, 'col')
        elif dir == 'a':
            self.x_position = move_in_bounds(self.x_position - 1, 'row')
        elif dir == 'd':
            self.x_position = move_in_bounds(self.x_position + 1, 'row')

    def line_of_stats(self):
        return 'health: {health} ore: {ore} x: {x} y: {y}'.format(health=self.health,
                                                                  ore=self.ore_quantity,
                                                                  x=self.x_position,
                                                                  y=self.y_position)

    def world_state(self):
        los = self.line_of_stats().ljust(world_size['row'])
        los = list(los)
        worldmap = world.get_world()
        worldmap.append(los)
        return worldmap


players = dict()


@app.route('/join')
def join():
    response = dict()

    new_id = str(uuid.uuid4())
    new_player = Player(id)
    players[new_id] = new_player
    response['id'] = new_id

    _sendState = request.args.get('sendState', 'false')

    if _sendState == 'true':
        response['world'] = players[new_id].world_state()
        return home_cor(jsonify(**response))

    return home_cor(jsonify(**response))


@app.route('/action')
def action():
    response = dict()

    _id = request.args.get('id', '')
    if _id == '':
        response["error"] = "Error, too lazy to include what the error is"
        return home_cor(jsonify(**response))

    _act = request.args.get('act', '')
    players[_id].input(_act)

    _sendState = request.args.get('sendState', 'false')
    if _sendState == 'true':
        response['world'] = players[_id].world_state()
    return home_cor(jsonify(**response))


@app.route('/sendState')
def send_state():
    response = dict()

    _id = request.args.get('id', '')
    if _id == '':
        response['error'] = "Error, too lazy to include what the error is"
        return home_cor(jsonify(**response))

    response = dict()
    response['world'] = players[_id].world_state()
    return home_cor(jsonify(**response))


app.run(debug=True, host='0.0.0.0', port=7001,threaded=True)