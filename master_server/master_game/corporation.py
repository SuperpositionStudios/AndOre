import uuid
from master_game.player import Player
from typing import Dict


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
        self.members = []
        self.corp_id = str(uuid.uuid4())

    def apply_inventory_delta_multiple(self, deltas: Dict[str, int]):
        for item_name in deltas:
            self.apply_inventory_delta(item_name, deltas.get(item_name, 0))
        return None

    def apply_child_server_deltas(self, data: Dict):
        self.apply_ore_delta(data.get('ore_delta', 0))
        self.apply_inventory_delta_multiple(data.get('inventory_deltas', {}))

    def apply_inventory_delta(self, item, delta):
        self.assets['inventory'][item] = self.assets['inventory'].get(item, 0) + delta

    def apply_ore_delta(self, delta):
        self.assets['ore'] = self.assets.get('ore', 0) + delta

    def add_member(self, member: Player):
        member.corp = self
        self.members.append(member)
        return None

    def members_to_json(self):
        response = {
            'members': []
        }
        for member in self.members:
            response['members'].append(member.uid)
        return response

    def set_ore_quantity(self, amount: float):
        self.assets['ore'] = amount

    def amount_of_ore(self):
        return self.assets['ore']

    def gain_ore(self, amount: float):
        self.assets['ore'] += amount

    def lose_ore(self, amount):
        self.assets['ore'] -= amount

    def can_afford(self, price):
        return self.amount_of_ore() >= price
