import uuid


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
        self.icon = '€'
        self.icons = {
            'M': 'Ƀ',
            'A': '₳',
            'N': '€',
            'E': '€'
        }

        self.passable = {
            'M': False,
            'A': False,
            'N': False,
            'E': False
        }
        self.blocking = True

        self.ore_generated_per_tick = 1
        self.price_to_construct = OreGenerator.construction_cost
        self.health = 300

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
            'M': '|',
            'A': '|',
            'N': '|',
            'E': '|'
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

    def asd(self, item_num):
        return self.products[item_num]['item'].construction_cost

    def buy_item(self, _corp, item_num):
        # Item num out of range
        if item_num >= len(self.products):
            return False

        # _corp refers to the corp buying the item
        assert(_corp.__class__.__name__ == 'Corporation')

        # Checking if both parties are able to pay
        if (_corp.amount_of_ore() >= self.get_price(_corp, item_num) and self.owner_corp.amount_of_ore() >= self.asd(item_num)) is False:
            return False

        # Payment
        _corp.lose_ore(self.get_price(_corp, item_num))
        self.owner_corp.gain_ore(self.get_price(_corp, item_num))

        # Manufacturing & delivery
        self.owner_corp.lose_ore(self.asd(item_num))
        manufactured_item = self.products[item_num]['item'](_corp)

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

        self.add_product(MinerMultiplierPotion, {
            'M': 0,
            'A': 30,
            'N': 50,
            'E': 200
        })

        self.health = 180

        self.icons = {
            'M': '⚕',
            'A': '⚕',
            'N': '⚕',
            'E': '⚕'
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

    def __init__(self, _corp):
        self.owner_corp = _corp
        self.item_type = 'Consumable'
        self.obj_id = str(uuid.uuid4())
        self.icon = '?'  # Icon Displayed in Inventory
        self.effects = {
            'Health Delta': 0,  # Modifies the Health of the Player
            'Ore Delta': 0,  # Modifies the ore amount of the Player
            'Attack Power Delta': 0,  # Modifies the attack power of the Player
            'Health Cap Delta': 0,  # Modifies the max health of the Player
            'Ore Multiplier Delta': 0
        }
        self.owner_corp.add_to_inventory(self)

    def consume(self):
        self.owner_corp.remove_from_inventory(self)
        return self.effects


class HealthCapPotion(Consumable):

    construction_cost = 500

    def __init__(self, _corp):
        super().__init__(_corp)
        self.effects['Health Cap Delta'] = 10
        self.icon = 'HC'


class MinerMultiplierPotion(Consumable):

    construction_cost = 300

    def __init__(self, _corp):
        super().__init__(_corp)
        self.effects['Ore Multiplier Delta'] = 1
        self.icon = 'MM'


class AttackPowerPotion(Consumable):

    construction_cost = 200

    def __init__(self, _corp):
        super().__init__(_corp)
        self.effects['Attack Power Delta'] = 5
        self.icon = '⚒'


class HealthPotion(Consumable):

    construction_cost = 50

    def __init__(self, _corp):
        super().__init__(_corp)
        self.effects['Health Delta'] = 15
        self.icon = '♥'


class RespawnBeacon(CorpOwnedBuilding):
    construction_cost = 5

    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.icon = '𝌩'
        self.health = 1000

        self.icons = {
            'M': '𝌩',
            'A': '𝌩',
            'N': '𝌩',
            'E': '𝌩'
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
            'M': '=',
            'A': '=',
            'N': '-',
            'E': '-'
        }

        self.passable = {
            'M': True,
            'A': True,
            'N': False,
            'E': False
        }


class Hospital(CorpOwnedBuilding):

    construction_cost = 200

    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.icon = '+'  # Deprecated

        self.icons = {
            'M': '⊞',
            #'M': '🏥',
            'A': '±',
            'N': '+',
            'E': '∓'
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
