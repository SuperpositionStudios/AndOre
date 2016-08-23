from typing import Dict, List
import uuid

# Class Prototypes


class Player: pass


class Corporation: pass
# Class Definition


class Player:
    def __init__(self):
        self.node = 'Panagoul'
        self.corp = None
        self.uid = str(uuid.uuid4())

    def assign_corp(self, new_corp: Corporation):
        if self.corp is not None:
            self.corp.remove_player(self)
        new_corp.add_member(self)
        self.corp = new_corp


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

    def apply_inventory_delta_multiple(self, deltas: Dict[str, int]):
        for item_name in deltas:
            self.apply_inventory_delta(item_name, deltas.get(item_name, 0))
        return None

    def apply_child_server_deltas(self, data: Dict):
        self.apply_ore_delta(data.get('ore_delta', 0))
        self.apply_inventory_delta_multiple(data.get('inventory_deltas', {}))

    def apply_inventory_delta(self, item: str, delta: int):
        self.assets['inventory'][item] = self.assets['inventory'].get(item, 0) + delta

    def apply_ore_delta(self, delta: float):
        self.assets['ore'] = self.assets.get('ore', 0) + delta

    def add_member(self, member: Player) -> None:
        self.members.append(member)
        return None

    def remove_player(self, member: Player) -> None:
        self.members.remove(member)
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