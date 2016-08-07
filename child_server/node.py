from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import game.world


class Node:
    def __init__(self, address, nodes, name, keys):
        print('Starting node...')
        self.keys = keys
        self.address = address
        self.name = name
        self.nodes = nodes
        self.world = game.world.World()
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

        app.run(debug=True, host='0.0.0.0', port=7101)

    def home_cor(self, obj):
        return_response = make_response(obj)
        return_response.headers['Access-Control-Allow-Origin'] = '*'
        return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
        return return_response