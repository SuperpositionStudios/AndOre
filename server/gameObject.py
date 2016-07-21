import uuid


class GameObject:

    def __init__(self):
        self.cell = None
        self.obj_id = str(uuid.uuid4())
        self.passable = True
        self.blocking = False

    def leave_cell(self, cell):
        self.cell.remove_object(self)
        self.cell = None

    def change_cell(self, new_cell):
        if self.cell is not None:
            self.leave_cell(self)
        new_cell.add_game_object(self)


class OreDeposit(GameObject):

    def __init__(self, _cell):
        super().__init__()
        self.icon = '$'
        self.cell = _cell
        self.passable = False
        self.blocking = True

"""
class EmptySpace(GameObject):
    def __init__(self, _cell):
        super().__init__()
        self.icon = '#'
        self.cell = _cell
        self.blocking = True
"""
