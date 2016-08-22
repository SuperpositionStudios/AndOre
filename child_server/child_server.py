import child_server_config as config
import node as _node
import requests

# Config for the node
node_port = 7101
node_name = 'Cistuvaert'
node_address = '{domain}:{port}'.format(domain=config.address, port=node_port)

node = None

# Communicate to Master Server
req = requests.post(config.master_address + '/register/node', json={
    'key': config.keys['node'],
    'name': 'Cistuvaert',
    'address': node_address
})
master_response = req.json()
if master_response['Successful_Request']:
    print('Successfully Communicated with Master Server')
    print('Nodes: ', master_response['nodes'])
    node = _node.Node(config.address, master_response['nodes'], 'Cistuvaert', config.keys, port=7101)
else:
    print('Failed to establish connection to Master Server')