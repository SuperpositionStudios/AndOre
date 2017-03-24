from node_starter import NodeStarter
import urllib.request
import os

star_gates = {
	'Scipio': ['Toivo'],
	'Siwash': ['Toivo'],
	'Toivo': ['Scipio', 'Siwash', 'Voytek', 'Wojtek'],
	'Voytek': ['Toivo'],
	'Wojtek': ['Toivo']
}

public_address = os.environ['public_address'] if 'public_address' in os.environ else 'ws://' + urllib.request.urlopen('http://ident.me').read().decode('utf8')


scipio = NodeStarter(node_name=os.environ['node_name'],
					 node_port=os.environ['node_port'],
					 public_address=public_address,
					 sleipnir_address=os.environ['sleipnir_address'],
					 erebus_address=os.environ['erebus_address'],
					 star_gates=star_gates.get(os.environ['node_name'], []),
					 node_key=os.environ['node_key']
					 )
