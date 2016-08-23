from typing import Dict, List
import uuid

# Class Prototypes needed since Player refers to Corporation and Corporation refers to Player


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
