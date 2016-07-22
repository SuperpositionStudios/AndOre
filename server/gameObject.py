import uuid


class GameObject:

    def __init__(self, _cell):
        self.cell = _cell
        self.col = self.cell.col
        self.row = self.cell.row
        self.obj_id = str(uuid.uuid4())
        self.passable = True
        self.blocking = False

    def leave_cell(self):
        self.cell.remove_object(self.obj_id)
        self.cell = None

    def change_cell(self, new_cell):
        if self.cell is not None and new_cell is not None:
            self.leave_cell()
        new_cell.add_game_object(self)
        self.cell = new_cell
        self.row = self.cell.row
        self.col = self.cell.col

    def tick(self):
        return


class OreDeposit(GameObject):

    def __init__(self, _cell):
        super().__init__(_cell)
        self.icon = '$'
        self.cell = _cell
        self.passable = False
        self.blocking = True
        self.ore_per_turn = 3


class Hospital(GameObject):

    def __init__(self, _cell):
        super().__init__(_cell)
        self.icon = '+'
        self.cell = _cell
        self.passable = False
        self.blocking = True
        self.health_regen_per_turn = 5
