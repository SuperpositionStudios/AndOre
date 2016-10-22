import child_server_config as config
import node as _node
import requests

# Config for the node
node_port = 7101
node_name = 'Panagoul'
node_address = '{domain}:{port}'.format(domain=config.address, port=node_port)

# Global Variables
node = None


try:
    # Communicate to Master Server
    req = requests.post(config.master_address + '/register/node', json={
        'key': config.keys['node'],
        'name': node_name,
        'address': node_address
    })
    master_response = req.json()
    if master_response['Successful_Request']:
        print('Successfully Communicated with Sleipnir')
        print('Nodes: ', master_response['nodes'])
        node = _node.Node(config.address, master_response['nodes'], node_name, config.keys, port=node_port)
    else:
        print('Communicated with Sleipnir, but register node request failed')
except:
    print('Failed to establish connection to Sleipnir')
