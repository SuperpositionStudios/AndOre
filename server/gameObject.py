import uuid


class GameObject:
    def __init__(self):
        self.obj_id = str(uuid.uuid4())


class OreDeposit(GameObject):

    def __init__(self, _cell):
        super().__init__()
        self.icon = '$'
        self.cell = _cell


class EmptySpace(GameObject):
    def __init__(self, _cell):
        super().__init__()
        self.icon = '#'
        self.cell = _cell
