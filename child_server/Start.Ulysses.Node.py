import config
import node as _node
import requests

# Config for the node
node_port = 7102
node_name = 'Ulysses'
production_public_node_address = 'http://ulysses.iwanttorule.space'
developing_public_node_address = 'http://localhost:7102'

if config.developing:
    public_node_address = developing_public_node_address
else:
    public_node_address = production_public_node_address

# Global Variables
node = None

# Communicate to Master Server
req = requests.post(config.sleipnir_address + '/register/node', json={
    'key': config.keys['node'],
    'name': node_name,
    'address': public_node_address
})
master_response = req.json()
if master_response['Successful_Request']:
    print('Successfully Communicated with Master Server')
    print('Nodes: ', master_response['nodes'])
    node = _node.Node(public_node_address, master_response['nodes'], node_name, config.keys, port=node_port)
else:
    print('Failed to establish connection to Master Server')
