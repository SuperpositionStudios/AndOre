import gameObject, uuid


class Corporation:

    def __init__(self, initial_member, _world):
        assert(initial_member.__class__.__name__ == 'Player')

        self.corp_id = str(uuid.uuid4())
        self.world = _world
        self.members = []  # Members of the corporation, the actual Player objects are stored here, not just their ids.
        self.buildings = []  # Buildings owned by the corporation, building objects are stored here, not just their ids.
        self.ore_quantity = 0
        self.sent_merge_invites = []  # A list containing ids of corps that have been sent merge invites
        self.received_merge_invites = []  # A list containing ids of corps that have sent use merge invites
        self.standings = dict()

        self.add_member(initial_member)

    def fetch_standing(self, corp_id):
        if corp_id in self.standings:
            return self.standings[corp_id]
        else:
            return 'N'

    def worsen_standing(self, corp_id):
        self.standings[corp_id] = self.calculate_standing(self.fetch_standing(corp_id), -1)

    def improve_standing(self, corp_id):
        self.standings[corp_id] = self.calculate_standing(self.fetch_standing(corp_id), 1)

    def calculate_standing(self, standing, modifier):
        if standing == 'E' and modifier == 1:
            return 'N'
        elif standing == 'E' and modifier == -1:
            return 'E'
        elif standing == 'N' and modifier == 1:
            return 'A'
        elif standing == 'N' and modifier == -1:
            return 'E'
        elif standing == 'A' and modifier == 1:
            return 'A'
        elif standing == 'A' and modifier == -1:
            return 'N'
        else:
            return 'N'

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
        self.check_if_corp_can_merge_and_if_so_merge()

    def send_merge_invite(self, corp_id):
        if self.corp_id != corp_id:
            self.sent_merge_invites.append(corp_id)
            self.world.corporations[corp_id].receive_merge_invite(self.corp_id)

    def check_if_corp_can_merge_and_if_so_merge(self):
        for received in self.received_merge_invites:
            if received in self.sent_merge_invites:
                corp_id_to_merge_with = received
                self.world.corporations[corp_id_to_merge_with].merge_me(self.corp_id)

    # Another corp will call this with their corp id to indicate that they want to be merged into our corp
    def merge_me(self, other_corp_id):
        #print("Old corp size: {}".format(len(self.members)))
        self.sent_merge_invites = list([])  # Empties the sent merge invites list
        self.received_merge_invites = list([])  # Empties the received merge invites list
        # Incorporating their ore bank into our ore bank
        self.gain_ore(self.world.corporations[other_corp_id].ore_quantity)

        # Setting the other corp's members corp to our corp
        for member in self.world.corporations[other_corp_id].members:
            member.corp = self
            self.members.append(member)

        # Deletes the other corp to save memory
        self.world.corporations.pop(other_corp_id)
        #print("New corp size: {}".format(len(self.members)))
