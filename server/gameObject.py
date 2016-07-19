import uuid, random
class GameObject:
    def __init__(self):
        self.obj_id = str(uuid.uuid4())


class OreDeposit(GameObject):

    def __init__(self):
        super().__init__()
        self.icon = '$'


class EmptySpace(GameObject):
    def __init__(self):
        super().__init__()
        self.icon = '#'