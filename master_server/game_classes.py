from typing import Dict, List
import uuid
import requests


class Player:
    def __init__(self):
        self.node = 'Panagoul'
        self.aid = None
        self.username = None
        self.corp = None
        self.uid = str(uuid.uuid4())  # TODO: Rename this to gid (game id) to differentiate between aid (auth id)

    def assign_aid(self, new_aid: str) -> None:
        self.aid = new_aid

    def assign_username(self, new_username: str) -> None:
        self.username = new_username

    def assign_corp(self, new_corp: 'Corporation'):
        if self.corp is not None:
            self.corp.remove_player(self)
        new_corp.add_member(self)
        self.corp = new_corp

    def assign_node(self, new_node: str) -> None:
        self.node = new_node


class Corporation:
    def __init__(self):
        self.assets = {
            'ore': 0,
            'inventory': {
                'HealthPotion': 6,
                'HealthCapPotion': 0,
                'AttackPowerPotion': 0,
                'MinerMultiplierPotion': 0
            }
        }
        self.members = []  # type: List[Player]
        self.corp_id = str(uuid.uuid4())

    def apply_inventory_delta_multiple(self, deltas: Dict[str, int]) -> None:
        for item_name in deltas:
            self.apply_inventory_delta(item_name, deltas.get(item_name, 0))
        return None

    def apply_child_server_deltas(self, data: Dict) -> None:
        self.apply_ore_delta(data.get('ore_delta', 0))
        self.apply_inventory_delta_multiple(data.get('inventory_deltas', {}))
        return None

    def apply_inventory_delta(self, item: str, delta: int) -> None:
        self.assets['inventory'][item] = self.assets['inventory'].get(item, 0) + delta
        return None

    def apply_ore_delta(self, delta: float) -> None:
        self.assets['ore'] = self.assets.get('ore', 0) + delta
        return None

    def add_member(self, member: Player) -> None:
        self.members.append(member)
        return None

    def remove_player(self, member: Player) -> None:
        self.members.remove(member)
        return None

    def members_to_json(self) -> Dict[str, List[str]]:
        response = {
            'members': []
        }  # type: Dict[str, List[str]]
        for member in self.members:
            response['members'].append(member.uid)
        return response

    def set_ore_quantity(self, amount: float):
        self.assets['ore'] = amount

    def amount_of_ore(self) -> float:
        return self.assets['ore']

    def gain_ore(self, amount: float) -> None:
        self.assets['ore'] += amount
        return None

    def lose_ore(self, amount: float) -> None:
        self.assets['ore'] -= amount
        return None

    def can_afford(self, price: float) -> bool:
        return self.amount_of_ore() >= price


class Node:
    def __init__(self, node_name: str, address: str, sleipnir_address: str, sleipnir_key: str, node_key: str):
        self.name = node_name
        self.address = address
        self.sleipnir_key = sleipnir_key
        self.node_key = node_key
        self.sleipnir_address = sleipnir_address
        self.queue = []  # type: List[Dict]

    def get_queue(self) -> List[Dict]:
        return self.queue

    def empty_queue(self) -> None:
        self.queue = [{
            'type': 'verification_key',
            'key': self.sleipnir_key
        }]  # type: List[Dict]

    def add_to_queue(self, x: Dict) -> None:
        self.queue.append(x)

    def send_message(self, endpoint, data):
        try:
            req = requests.post(self.address + endpoint, json=data)
            response = req.json()
            if response is None:
                return [False, {}]
            else:
                return [True, response]
        except:
            return [False, {}]

    def send_queue(self) -> bool:
        response = self.send_message('/update/nodes', self.get_queue())
        return response[0]

    def update_address(self, new_address):
        self.address = new_address


class NodeList:
    def __init__(self, sleipnir_address: str, sleipnir_key: str, node_key: str):
        self.nodes = dict()  # type: Dict[str, Node]
        self.sleipnir_key = sleipnir_key
        self.node_key = node_key
        self.sleipnir_address = sleipnir_address

    def get_node(self, node_name: str):
        if self.nodes.get(node_name, None) is not None:
            return self.nodes.get(node_name)
        else:
            print("Couldn't find node: ", node_name)
            return None

    def node_exists(self, node_name: str):
        return node_name in self.nodes

    def add_to_all_node_queues(self, req: Dict, exclude_list: List[str]):
        for node_name, node in self.nodes.items():
            if node_name in exclude_list is False:
                node.add_to_queue(req)

    def send_queues(self, exclude_list: List[str]):
        for node_name, node in self.nodes.items():
            if node_name in exclude_list is False:
                node.send_queue()

    def update_node_lists(self):
        node_list = {}
        for node_name, node in self.nodes.items():
            node_list[node_name] = {
                'name': node_name,
                'address': node.address
            }
        req = {
            'type': 'node_list_update',
            'key': self.sleipnir_key,
            'nodes': node_list,
            'master': {
                'name': 'Sleipnir',
                'address': self.sleipnir_address
            }
        }
        self.add_to_all_node_queues(req, [])
        self.send_queues([])

    def add_node(self, node_name: str, address: str, overwrite: bool) -> None:
        if self.get_node(node_name) is not None:
            if overwrite:
                self.nodes[node_name] = Node(node_name, address, self.sleipnir_address, self.sleipnir_key, self.node_key)
            else:
                self.get_node(node_name).update_address(address)
        else:
            self.nodes[node_name] = Node(node_name, address, self.sleipnir_address, self.sleipnir_key, self.node_key)
        self.update_node_lists()

    def remove_node(self, node_name) -> None:
        self.nodes.pop(node_name)


class Sleipnir:
    def __init__(self, sleipnir_key: str, node_key: str, address: str):
        self.sleipnir_key = sleipnir_key
        self.node_key = node_key
        self.nodes = NodeList(address, self.sleipnir_key, self.node_key)
        self.corporations = dict()  # type: Dict[str, Corporation]
        self.players = dict()  # type: Dict[str, Player]

    def valid_id(self, gid: str):
        return gid in self.players

    def valid_node_key(self, key):
        return key == self.node_key

    def new_node(self, key: str, node_name: str, node_address: str):
        if self.valid_node_key(key):
            self.nodes.add_node(node_name, node_address, False)
