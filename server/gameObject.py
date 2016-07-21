import uuid


class GameObject:
    def __init__(self):
        self.obj_id = str(uuid.uuid4())
        self.passable = True


class OreDeposit(GameObject):

    def __init__(self, _cell):
        super().__init__()
        self.icon = '$'
        self.cell = _cell
        self.passable = False


class EmptySpace(GameObject):
    def __init__(self, _cell):
        super().__init__()
        self.icon = '#'
        self.cell = _cell
