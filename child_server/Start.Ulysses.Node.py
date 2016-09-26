import child_server_config as config
import node as _node
import requests

# Config for the node
node_port = 7102
node_name = 'Ulysses'
node_address = '{domain}:{port}'.format(domain=config.address, port=node_port)

# Global Variables
node = None

# Communicate to Master Server
req = requests.post(config.master_address + '/register/node', json={
    'key': config.keys['node'],
    'name': node_name,
    'address': node_address
})
master_response = req.json()
if master_response['Successful_Request']:
    print('Successfully Communicated with Master Server')
    print('Nodes: ', master_response['nodes'])
    node = _node.Node(config.address, master_response['nodes'], node_name, config.keys, port=node_port)
else:
    print('Failed to establish connection to Master Server')
