import gameObject, uuid


class Corporation:

    def __init__(self, initial_member, _world):
        assert(initial_member.__class__.__name__ == 'Player')

        self.corp_id = str(uuid.uuid4())
        self.world = _world
        self.members = []
        self.ore_quantity = 0
        self.sent_merge_invites = []  # A list containing ids of corps that have been sent merge invites
        self.received_merge_invites = []  # A list containing ids of corps that have sent use merge invites

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

    def check_if_in_corp(self, player_id):
        for member in self.members:
            if player_id == member.obj_id:
                return True
        return False

    def receive_merge_invite(self, corp_id):
        self.received_merge_invites.append(corp_id)

    def send_merge_invite(self, corp_id):
        self.sent_merge_invites.append(corp_id)
        self.world.corporations[corp_id].receive_merge_invite(self.corp_id)
