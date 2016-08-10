import uuid


class Corporation:

    def __init__(self):
        self.assets = {
            'ore': 0
        }
        self.members = []
        self.corp_id = str(uuid.uuid4())

    def add_member(self, member):
        member.corp = self
        self.members.append(member)

    def members_to_json(self):
        response = {
            'members': []
        }
        for member in self.members:
            response['members'].append(member.uid)
        return response

    def set_ore_quantity(self, amount):
        self.assets['ore'] = amount

    def amount_of_ore(self):
        return self.assets['ore']

    def gain_ore(self, amount):
        self.assets['ore'] += amount

    def lose_ore(self, amount):
        self.assets['ore'] -= amount

    def can_afford(self, price):
        return self.amount_of_ore() >= price
