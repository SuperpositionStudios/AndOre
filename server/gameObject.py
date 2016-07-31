import uuid


class GameObject:

    def __init__(self, _cell):
        assert(_cell.__class__.__name__ == 'Cell')
        self.cell = _cell
        self.col = self.cell.col
        self.row = self.cell.row
        self.obj_id = str(uuid.uuid4())
        self.passable = True
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

    def tick(self):
        # Something the building needs to every tick
        return

    def delete(self):
        self.leave_cell()
        self.owner_corp.remove_corp_building(self)


class OreDeposit(GameObject):

    def __init__(self, _cell):
        super().__init__(_cell)
        self.icon = '$'
        self.cell = _cell
        self.passable = False
        self.blocking = True
        self.ore_per_turn = 3


class OreGenerator(CorpOwnedBuilding):

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

        self.passable = False
        self.blocking = True

        self.ore_generated_per_tick = 1
        self.price_to_construct = 100
        self.health = 80

    def tick(self):
        self.owner_corp.gain_ore(self.ore_generated_per_tick)


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

        self.price_to_make = 5  # The number of ore it costs to produce the item
        self.item = Consumable
        self.item_type = self.item.item_type

        self.profits = {  # How much profit you'll make from selling this item
            'M': 0,  # Charging Corp Members Cost, should always be 0 because since the corporation wallet is used
                     # to pay for the purchase, you don't make anything by making this higher.
            'A': 1,  # Charging People The Owners Considers Allies Cost + 1
            'N': 5,  # Charging Neutrals Cost + 5
            'E': 10  # Charging Enemies Cost + 10 (Hey you gotta make money somehow)
        }

        self.prices = {  # How much it'll cost to buy items from here, don't edit this.
            'M': self.price_to_make + self.profits['M'],
            'A': self.price_to_make + self.profits['A'],
            'N': self.price_to_make + self.profits['N'],
            'E': self.price_to_make + self.profits['E']
        }

    def get_price(self, _corp):
        return self.prices[self.owner_corp.fetch_standing(_corp.corp_id)]

    def get_profit(self, _corp):
        return self.profits[self.owner_corp.fetch_standing(_corp.corp_id)]

    def buy_item(self, _corp):
        # _corp refers to the corp buying the item
        assert(_corp.__class__.__name__ == 'Corporation')

        # Checking if both parties are able to pay
        if _corp.amount_of_ore() > self.get_price(_corp) is False or self.owner_corp.amount_of_ore() >= self.price_to_make is False:
            return

        # Manufacturing of item
        self.owner_corp.lose_ore(self.price_to_make)
        manufactured_item = self.item()

        # Payment
        _corp.lose_ore(self.get_price(_corp))
        self.owner_corp.gain_ore(self.get_profit(_corp))

        # Delivery
        _corp.add_to_inventory(manufactured_item)


class Pharmacy(CorpOwnedStore):
    # Class-Wide Variables
    price_to_make = 10

    def __init__(self, _cell, _corp):
        assert (_cell.__class__.__name__ == 'Cell')
        assert (_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.item = HealthPotion
        self.price_to_make = 10

        self.profits = {  # How much profit you'll make from selling this item
            'M': 0,
            'A': 1,
            'N': 5,
            'E': 10
        }


class Consumable:
    item_type = 'Consumable'

    def __init__(self, _corp):
        self.owner_corp = _corp
        self.item_type = 'Consumable'
        self.obj_id = str(uuid.uuid4())
        self.icon = '?'  # Icon Displayed in Inventory
        self.effects = {
            'Health Delta': 0,
            'Ore Delta': 0
        }
        self.owner_corp.add_to_inventory(self)

    def consume(self):
        self.owner_corp.remove_from_inventorry(self)
        return self.effects


class HealthPotion(Consumable):

    def __init__(self, _corp):
        super().__init__(_corp)
        self.effects['Health Delta'] = 15
        self.icon = 'H'


class Hospital(CorpOwnedBuilding):

    def __init__(self, _cell, _corp):
        assert(_cell.__class__.__name__ == 'Cell')
        assert(_corp.__class__.__name__ == 'Corporation')

        super().__init__(_cell, _corp)

        self.icon = '+'  # Deprecated

        self.icons = {
            'M': '⊞',
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

        self.passable = False
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
        self.passable = False  # False until we have a 'below' direction key
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
        self.passable = False

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
