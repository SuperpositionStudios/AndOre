import gameObject, uuid


class Corporation:

    def __init__(self, initial_member):
        assert(initial_member.__class__.__name__ == 'Player')

        self.corp_id = str(uuid.uuid4())
        self.members = []
        self.ore_quantity = 0

        self.add_member(initial_member)

    def add_member(self, member):
        assert(member.__class__.__name__ == 'Player')
        self.members.append(member)

    def gain_ore(self, amount):
        self.ore_quantity += amount

    def lose_ore(self, amount):
        self.ore_quantity -= amount

    def amount_of_ore(self):
        return self.ore_quantity

    def calculate_ore_loss_on_death(self):
        return int(self.ore_quantity / len(self.members))
