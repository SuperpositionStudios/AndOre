import uuid
from child_game import standing_colors


class GameObject:

    def __init__(self, _cell):
        assert(_cell.__class__.__name__ == 'Cell')
        self.cell = _cell
        self.col = self.cell.col
        self.row = self.cell.row
        self.obj_id = str(uuid.uuid4())
        self.passable = {
            'M': True,
            'A': True,
            'N': True,
            'E': True
        }
        self.blocking = False

    def leave_cell(self):
        self.cell.remove_object(self.obj_id)
        self.cell = None

    def delete(self):
        self.leave_cell()
        # hopefully garbage collection kicks in

    def change_cell(self, new_cell):
        if self.cell is not None and new_cell is not None:
            self.leave_cell()
        new_cell.add_game_object(self)
        self.cell = new_cell
        self.row = self.cell.row
        self.col = self.cell.col

    def tick(self):
        return


class CorpOwnedBuilding(GameObject):

    construction_cost = 0

    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell)

        self.cell = _cell
        self.owner_corp = _corp
        self.health = 10000

        self.owner_corp.add_corp_building(self)

    def take_damage(self, damage, attacking_corp):
        assert(attacking_corp.__class__.__name__ == 'Corporation')
        # Standings related thing
        self.owner_corp.worsen_standing(attacking_corp.corp_id)
        attacking_corp.worsen_standing(self.owner_corp.corp_id)

        # Damage Taking related thing
        self.health -= damage
        if self.check_if_dead():
            self.died()

    def check_if_dead(self):
        if self.health <= 0:
            return True
        else:
            return False

    def died(self):
        self.delete()

    def check_if_dead_and_if_so_die(self):
        if self.check_if_dead():
            self.delete()

    def tick(self):
        # Something the building needs to every tick
        return

    def delete(self):
        self.drop_ore()
        self.leave_cell()
        self.owner_corp.remove_corp_building(self)

    def drop_ore(self):
        loot_object = Loot(self.cell)

        ore_loss = int(self.construction_cost / 3)

        loot_object.ore_quantity = ore_loss

        self.cell.add_game_object(loot_object)


class OreDeposit(GameObject):

    def __init__(self, _cell):
        super().__init__(_cell)
        self.icon = '$'
        self.cell = _cell
        self.passable = {
            'M': False,
            'A': False,
            'N': False,
            'E': False
        }
        self.blocking = True
        self.ore_per_turn = 3


class OreGenerator(CorpOwnedBuilding):

    construction_cost = 100

    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)
        self.icon = '🏭'
        self.icons = {
            'M': ['🏭', standing_colors.mane['M']],
            'A': ['🏭', standing_colors.mane['A']],
            'N': ['🏭', standing_colors.mane['N']],
            'E': ['🏭', standing_colors.mane['E']]
        }

        self.passable = {
            'M': False,
            'A': False,
            'N': False,
            'E': False
        }
        self.blocking = True

        self.ore_generated_per_tick = 3
        self.price_to_construct = OreGenerator.construction_cost
        self.health = 225


    def tick(self):
        self.owner_corp.gain_ore(self.ore_generated_per_tick)
        self.health -= 1
        self.check_if_dead_and_if_so_die()


class CorpOwnedStore(CorpOwnedBuilding):
    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.icon = '|'

        self.icons = {
            'M': ['|', standing_colors.mane['M']],
            'A': ['|', standing_colors.mane['A']],
            'N': ['|', standing_colors.mane['N']],
            'E': ['|', standing_colors.mane['E']]
        }

        self.products = dict()

    def add_product(self, item, profits):
        index = len(self.products)
        self.products[index] = {
            'prices': {
                'M': item.construction_cost + profits['M'],
                'A': item.construction_cost + profits['A'],
                'N': item.construction_cost + profits['N'],
                'E': item.construction_cost + profits['E']
            },
            'profits': profits,
            'item': item
        }

    def get_price(self, _corp, item_num):
        return self.products[item_num]['prices'][self.owner_corp.fetch_standing(_corp.corp_id)]

    def get_profit(self, _corp, item_num):
        return self.products[item_num]['profits'][self.owner_corp.fetch_standing(_corp.corp_id)]

    def product_price_from_product_num(self, item_num):
        return self.products[item_num]['item'].construction_cost

    def buy_item(self, _corp, item_num):
        # Item num out of range
        if item_num >= len(self.products):
            return False

        # _corp refers to the corp buying the item
        assert(_corp.__class__.__name__ == 'Corporation')

        # Checking if both parties are able to pay
        if (_corp.amount_of_ore() >= self.get_price(_corp, item_num) and self.owner_corp.amount_of_ore() >= self.product_price_from_product_num(item_num)) is False:
            return False

        # Financial Transfers
        _corp.lose_ore(self.get_price(_corp, item_num))  # Buyer Pays
        self.owner_corp.gain_ore(self.get_price(_corp, item_num))  # Owner gets Profit
        self.owner_corp.lose_ore(self.product_price_from_product_num(item_num))  # Owner pays for goods that were sold to the Buyer
        _corp.queue_inventory_delta(self.products[item_num]['item'].__name__, 1)  # Buyer gets their goods

        return True


class Pharmacy(CorpOwnedStore):
    # Class-Wide Variables
    construction_price = 1000
    construction_cost = construction_price

    def __init__(self, _cell, _corp):
        assert (_cell.__class__.__name__ == 'Cell')
        assert (_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.add_product(HealthPotion, {
            'M': 0,
            'A': 1,
            'N': 5,
            'E': 10
        })
        self.add_product(HealthCapPotion, {
            'M': 0,
            'A': 50,
            'N': 100,
            'E': 250
        })

        self.add_product(AttackPowerPotion, {
            'M': 0,
            'A': 20,
            'N': 100,
            'E': 500
        })
        """  Disabled until https://github.com/baxter-oop/AndOre/issues/154 is resolved
        self.add_product(MinerMultiplierPotion, {
            'M': 0,
            'A': 30,
            'N': 50,
            'E': 200
        })
        """

        self.health = 180

        self.icons = {
            'M': ['🏥', standing_colors.mane['M']],
            'A': ['🏥', standing_colors.mane['A']],
            'N': ['🏥', standing_colors.mane['N']],
            'E': ['🏥', standing_colors.mane['E']]
        }
        self.passable = {
            'M': False,
            'A': False,
            'N': False,
            'E': False
        }


class Consumable:
    item_type = 'Consumable'
    construction_cost = 0
    icon = '?'  # Icon to represent item in inventory

    def __init__(self):
        self.item_type = 'Consumable'
        self.obj_id = str(uuid.uuid4())
        self.effects = {
            'Health Delta': 0,  # Modifies the Health of the Player
            'Ore Delta': 0,  # Modifies the ore amount of the Player
            'Attack Power Delta': 0,  # Modifies the attack power of the Player
            'Health Cap Delta': 0,  # Modifies the max health of the Player
            'Ore Multiplier Delta': 0,  # Adds this to the player's ore multiplier
            'Ore Multiplier Multiplier Delta': 0  # Multiplies the player's ore multiplier by this + 1.
        }

    def consume(self):
        return self.effects


class HealthCapPotion(Consumable):

    construction_cost = 500
    icon = 'HC'

    def __init__(self):
        super().__init__()
        self.effects['Health Cap Delta'] = 10


class MinerMultiplierPotion(Consumable):

    construction_cost = 300
    icon = 'MM'

    def __init__(self):
        super().__init__()
        self.effects['Ore Multiplier Multiplier Delta'] = .15


class AttackPowerPotion(Consumable):

    construction_cost = 200
    icon = '⚒'

    def __init__(self):
        super().__init__()
        self.effects['Attack Power Delta'] = 4


class HealthPotion(Consumable):

    construction_cost = 50
    icon = '♥'

    def __init__(self):
        super().__init__()
        self.effects['Health Delta'] = 15


class RespawnBeacon(CorpOwnedBuilding):
    construction_cost = 5

    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.icon = '𝌩'
        self.health = 1000

        self.icons = {
            'M': ['𝌩', standing_colors.mane['M']],
            'A': ['𝌩', standing_colors.mane['A']],
            'N': ['𝌩', standing_colors.mane['N']],
            'E': ['𝌩', standing_colors.mane['E']]
        }

        self.passable = {
            'M': True,
            'A': True,
            'N': True,
            'E': True
        }

        self.owner_corp.destroy_other_respawn_beacons(self)


class Door(CorpOwnedBuilding):
    # Class-Wide Variables
    construction_price = 1000
    construction_cost = construction_price

    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.icon = 'D'  # Deprecated
        self.health = 250

        self.icons = {
            'M': ['=', standing_colors.mane['M']],
            'A': ['=', standing_colors.mane['A']],
            'N': ['=', standing_colors.mane['N']],
            'E': ['=', standing_colors.mane['E']]
        }

        self.passable = {
            'M': True,
            'A': True,
            'N': False,
            'E': False
        }


class SentryTurret(CorpOwnedBuilding):

    construction_cost = 500

    def __init__(self, _cell, _corp):
        assert (_cell.__class__.__name__ == 'Cell')
        assert (_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.health = 80

        self.icons = {
            'M': ['T', standing_colors.mane['M']],
            'A': ['T', standing_colors.mane['A']],
            'N': ['T', standing_colors.mane['N']],
            'E': ['T', standing_colors.mane['E']]
        }

        self.passable = {
            'M': False,
            'A': False,
            'N': False,
            'E': False
        }

        self.attack_power = 5

        self.nearby_cells = []
        for tup in [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1]]:
            _cell = self.cell.try_get_cell_by_offset(tup[0], tup[1])
            if _cell is not False:
                self.nearby_cells.append(_cell)

    def tick(self):
        # Attacks 1 non-friendly player in a nearby cell
        for cell in self.nearby_cells:
            if cell.damage_first_player(self.owner_corp, self.attack_power):
                return True


class SpikeTrap(CorpOwnedBuilding):

    construction_cost = 150

    def __init__(self, _cell, _corp):
        assert (_cell.__class__.__name__ == 'Cell')
        assert (_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.health = 40

        self.icons = {
            'M': ['S', standing_colors.mane['M']],
            'A': ['S', standing_colors.mane['A']],
            'N': ['S', standing_colors.mane['N']],
            'E': ['S', standing_colors.mane['E']]
        }

        self.passable = {
            'M': True,
            'A': True,
            'N': True,
            'E': True
        }

        self.attack_power = 5

    def tick(self):
        # Attacks 1 non-friendly player in the cell the Spiketrap is residing in
        self.cell.damage_first_player(self.owner_corp, self.attack_power)


class Hospital(CorpOwnedBuilding):

    construction_cost = 200

    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.icon = '+'  # Deprecated

        self.icons = {
            'M': ['⚕', standing_colors.mane['M']],
            'A': ['⚕', standing_colors.mane['A']],
            'N': ['⚕', standing_colors.mane['N']],
            'E': ['⚕', standing_colors.mane['E']]
        }

        self.prices_to_use = {
            'M': 5,
            'A': 6,
            'N': 10,
            'E': 15
        }

        self.profits_per_use = {
            'M': 0,
            'A': 1,
            'N': 5,
            'E': 10
        }

        self.passable = {
            'M': False,
            'A': False,
            'N': False,
            'E': False
        }
        self.blocking = True
        self.health_regen_per_turn = 5
        self.ore_usage_cost = 10
        self.price_to_construct = 200
        self.health = 200

    def give_profit_to_owners(self, standing):
        self.owner_corp.gain_ore(self.profits_per_use[standing])


class Loot(GameObject):

    def __init__(self, _cell):
        super().__init__(_cell)
        self.icon = '%'
        self.passable = {
            'M': False,
            'A': False,
            'N': False,
            'E': False
        }  # False until we have a 'below' direction key
        self.ore_quantity = 0


class HealthPack(Loot):
    def __init__(self, _cell):
        super().__init__(_cell)
        self.health_quantity = 0
        self.icon = '⨮'


class Fence(GameObject):

    construction_cost = 30

    def __init__(self, _cell):
        super().__init__(_cell)
        self.health = 60
        self.icon = '#'
        self.ore_cost_to_deploy = 30
        self.passable = {
            'M': False,
            'A': False,
            'N': False,
            'E': False
        }

    def take_damage(self, damage):
        self.health -= damage
        if self.check_if_dead():
            self.died()

    def check_if_dead(self):
        if self.health <= 0:
            return True
        else:
            return False

    def died(self):
        self.delete()
