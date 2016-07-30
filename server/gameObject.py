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

    def tick(self):
        # Something the building needs to every tick
        return


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

        self.icons = {
            'M': 'Ƀ',
            'A': '₳',
            'N': '€',
            'E': '€'
        }


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
