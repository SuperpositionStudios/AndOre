import child_server_config as config
import node as _node
import requests

node = None

# Communicate to Master Server
req = requests.post(config.master_address + '/register/node', json={
    'key': config.keys['node'],
    'name': 'Cistuvaert',
    'address': config.address
})
master_response = req.json()
if master_response['Successful_Request']:
    print('Op Success')
    print(master_response['nodes'])
    node = _node.Node(config.address, master_response['nodes'], 'Cistuvaert', config.keys)
else:
    print('Failed to establish connection to Master Server')