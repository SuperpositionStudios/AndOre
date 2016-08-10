import uuid
import child_server_config as config
from child_game import gameObject


class Corporation:

    def __init__(self, _world, corp_id=None):
        if corp_id is None:
            self.corp_id = str(uuid.uuid4())
        else:
            self.corp_id = corp_id
        self.world = _world
        self.members = []  # Members of the corporation, the actual Player objects are stored here, not just their ids.
        self.buildings = []  # Buildings owned by the corporation, building objects are stored here, not just their ids.
        self.inventory = dict()  # Items owned are stored here
        """
        Example:
        self.inventory = {
            'Consumables': {
                'HealthPotion': [HealthPotion(), HealthPotion()],
            },
            'Deployables': {
                'Fence': [Fence(), Fence()]
            }
        }
        """
        self.usage_inventory = []
        self.ore_quantity = 0
        if config.developing:
            self.ore_quantity += 10000
        self.sent_merge_invites = []  # A list containing ids of corps that have been sent merge invites
        self.received_merge_invites = []  # A list containing ids of corps that have sent use merge invites
        self.standings = dict()

    def render_inventory(self):
        rendered_inventory = ''
        self.usage_inventory = []
        # Loop through item type names
        for item_type in self.inventory:
            # Loop through item's arrays
            for item_name in self.inventory[item_type]:
                quantity = len(self.inventory[item_type][item_name])
                if quantity > 0:
                    icon = self.inventory[item_type][item_name][0].icon
                    rendered_inventory += '{icon}: {quantity} '.format(icon=icon, quantity=quantity)
                    self.usage_inventory.append(self.inventory[item_type][item_name][0])
        return rendered_inventory.ljust(self.world.cols)

    def return_obj_selected_in_rendered_inventory(self, selected):
        # Selected are the Secondary Modifier Keys for the Usage Inventory Modifier key, so 1, 2, 3, 4, 5, 6, 7, 8, 9, 0
        # 1 refers to self.usage_inventory[0]
        # 0 refers to self.usage_inventory[9]
        # 1 -> 0
        # 2 -> 1
        # 3 -> 2
        # 4 -> 3
        # 5 -> 4
        # 6 -> 5
        # 7 -> 6
        # 8 -> 7
        # 9 -> 8
        # 0 -> 9
        if selected == 0:
            return self.usage_inventory[9]
        else:
            return self.usage_inventory[selected - 1]

    def remove_from_inventory(self, item_obj):
        item_type_storage = self.inventory.get(item_obj.item_type, None)
        if item_type_storage is not None:
            item_storage = item_type_storage.get(item_obj.__class__.__name__, None)
            if item_storage is not None:
                for i in range(0, len(item_storage)):
                    if item_storage[i].obj_id == item_obj.obj_id:
                        del item_storage[i]
                        return
            else:
                self.inventory[item_obj.item_type][item_obj.__class__.__name__] = []
        else:
            self.inventory[item_obj.item_type] = dict()
            self.remove_from_inventory(item_obj)

    def add_to_inventory(self, item_obj):
        item_type_storage = self.inventory.get(item_obj.item_type, None)
        if item_type_storage is not None:
            item_storage = item_type_storage.get(item_obj.__class__.__name__, None)
            if item_storage is not None:
                item_storage.append(item_obj)
            else:
                self.inventory[item_obj.item_type][item_obj.__class__.__name__] = [item_obj]
        else:
            self.inventory[item_obj.item_type] = dict()
            self.add_to_inventory(item_obj)

    def tick_buildings(self):
        for building in self.buildings:
            building.tick()

    def add_corp_building(self, building_object):
        self.buildings.append(building_object)

    def remove_corp_building(self, building_object):
        obj_id = building_object.obj_id
        for i in range(0, len(self.buildings)):
            if self.buildings[i].obj_id == obj_id:
                del self.buildings[i]
                return

    def get_respawn_cell(self):
        for building in self.buildings:
            if building.__class__.__name__ == 'RespawnBeacon':
                return building.cell
        return self.world.random_can_enter_cell()

    def destroy_other_respawn_beacons(self, new_beacon):
        for building in self.buildings:
            if building.__class__.__name__ == 'RespawnBeacon' and building.obj_id != new_beacon.obj_id:
                building.delete()

    def fetch_standing(self, corp_id):
        if corp_id == self.corp_id:
            return 'M'
        elif corp_id in self.standings:
            return self.standings[corp_id]
        else:
            return 'N'

    def fetch_standing_for_player(self, player_id):
        player_object = self.world.players[player_id]
        if player_object is not None:
            return self.fetch_standing(player_object.corp.corp_id)
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
        _other_corp = self.world.corporations[other_corp_id]

        #print("Old corp size: {}".format(len(self.members)))
        self.sent_merge_invites = list([])  # Empties the sent merge invites list
        self.received_merge_invites = list([])  # Empties the received merge invites list

        # Incorporating their ore bank into our ore bank
        self.gain_ore(self.world.corporations[other_corp_id].ore_quantity)

        # Setting the other corp's members corp to our corp
        for member in self.world.corporations[other_corp_id].members:
            member.corp = self
            self.members.append(member)

        # Copying their inventory to ours
        # Loop through item type names
        for item_type in _other_corp.inventory:
            # Loop through item's arrays
            for item_name in _other_corp.inventory[item_type]:
                try:
                    for item in _other_corp.inventory[item_type][item_name]:
                        self.add_to_inventory(item)
                except Exception as e:
                    print(str(e))

        # Setting the other corp's buildings corp to our corp
        for building in self.world.corporations[other_corp_id].buildings:
            building.owner_corp = self
            self.buildings.append(building)

        # Deletes the other corp to save memory
        self.world.corporations.pop(other_corp_id)
        #print("New corp size: {}".format(len(self.members)))
