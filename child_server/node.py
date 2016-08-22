from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
from child_game import world
import child_server_config as config
import datetime
import requests


class Node:
    def __init__(self, address, nodes, name, keys, port=7101):
        print('Starting node...')
        self.keys = keys
        self.address = "{domain}:{port}".format(domain=address, port=port)
        self.name = name
        self.nodes = nodes
        self.world = world.World(self.nodes['master']['address'], self.message_master_node)
        self.world.spawn_ore_deposits(5)
        app = Flask(__name__)

        # Should only be called by master server to update the listing of nodes.
        @app.route('/update/nodes', methods=['POST', 'OPTIONS'])
        def update_nodes():
            response = dict()
            data = request.json
            node_key = data.get('key', None)
            nodes = data.get('nodes', None)
            # Checking that none of the required inputs are None
            if node_key is None or nodes is None:
                response['Successful_Request'] = False
                return self.home_cor(jsonify(**response))
            # Official Server Confirming
            if node_key != self.keys['master']:
                response['Successful_Request'] = False
                return self.home_cor(jsonify(**response))
            self.nodes = nodes
            response['Successful_Request'] = True
            return self.home_cor(jsonify(**response))

        @app.route('/action')
        def action():
            # start_of_request = datetime.datetime.now()
            self.tick_server_if_needed()
            response = dict()

            _id = request.args.get('id', '')
            if self.world.valid_player_id(_id) is False:
                response["error"] = "Invalid ID"
                response["world"] = ''
                return self.home_cor(jsonify(**response))

            _act = request.args.get('action', '')
            re_render_world = self.world.players[_id].action(_act)
            # request_time = datetime.datetime.now() - start_of_request
            # print("Time to answer action request: {} milliseconds".format(request_time.microseconds / 1000))

            _sendState = request.args.get('sendState', 'false')

            if _sendState == 'true' and re_render_world:
                return send_state(_id=_id)
            else:
                response['id'] = _id
                response['vitals'] = self.world.players[_id].get_vitals()
                response['world'] = ''
                return self.home_cor(jsonify(**response))

        @app.route('/sendState')
        def send_state(**keyword_parameters):
            # start_of_request = datetime.datetime.now()

            self.tick_server_if_needed()
            response = dict()

            if '_id' in keyword_parameters:
                _id = keyword_parameters['_id']
            else:
                _id = request.args.get('id', '')

            if self.world.valid_player_id(_id) is False:
                response['error'] = "Invalid ID"
                response['world'] = ''
                return self.home_cor(jsonify(**response))

            response = dict()
            response['world'] = self.world.players[_id].world_state()
            response['inventory'] = self.world.players[_id].corp.render_inventory()
            response['id'] = _id
            response['vitals'] = self.world.players[_id].get_vitals()

            # request_time = datetime.datetime.now() - start_of_request
            # print("Time to answer sendState request: {}".format(request_time.microseconds / 1000))
            return self.home_cor(jsonify(**response))

        @app.route('/join')
        def join():
            self.tick_server_if_needed()
            response = dict()

            new_player_id = self.world.new_player()

            response['id'] = new_player_id

            _sendState = request.args.get('sendState', 'false')

            if _sendState == 'true':
                response['world'] = self.world.players[new_player_id].world_state()
                return send_state(_id=new_player_id)
            else:
                return self.home_cor(jsonify(**response))

        @app.route('/player/enter', methods=['POST', 'OPTIONS'])
        def player_enter():
            self.tick_server_if_needed()
            data = request.json
            response = dict()
            if data is not None and data.get('player', None) is not None:
                # Creating the player object on this node
                response['Successful_Request'] = True
                new_player_obj = self.world.new_player(player_id=data['player']['uid'],
                                                       corp_id=data['player']['corporation']['corp_id'],
                                                       corp_ore_quantity=data['player']['corporation']['ore_quantity'])
                return self.home_cor(jsonify(**response))

        @app.route('/player/leave', methods=['POST', 'OPTIONS'])
        def player_leave():
            self.tick_server_if_needed()
            data = request.json
            response = dict()
            if data is not None and data.get('player', None) is not None:
                response['Successful_Request'] = True
                player_id = data.get('player', None).get('uid', None)
                if player_id is not None:
                    self.world.despawn_player(player_id)
            return self.home_cor(jsonify(**response))

        @app.route('/transfer_assets', methods=['POST', 'OPTIONS'])
        def transfer_assets():
            self.tick_server_if_needed()
            data = request.json
            response = {
                'Successful_Request': False
            }
            if data is not None:
                acquiree_id = data.get('acquiree_id', None)
                acquirer_id = data.get('acquirer_id', None)
                master_key = data.get('master_key', None)
                if acquiree_id is not None and acquirer_id is not None and master_key == config.keys['master']:
                    self.world.transfer_corp_assets(acquirer_id, acquiree_id)
                    response['Successful_Request'] = True
            return jsonify(**response)

        app.run(debug=True, host='0.0.0.0', port=7101, threaded=True)

    def home_cor(self, obj):
        return_response = make_response(obj)
        return_response.headers['Access-Control-Allow-Origin'] = '*'
        return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
        return return_response

    def tick_server_if_needed(self):
        now = datetime.datetime.now()
        if (now - self.world.last_tick).microseconds >= self.world.microseconds_per_tick:
            self.world.tick()

    def message_master_node(self, endpoint, data):
        req = requests.post(self.nodes['master']['address'] + endpoint, json=data)
        node_response = req.json()
        if node_response['Successful_Request'] is False:
            print('Failed to message master node with {data}'.format(data=str(data)))
