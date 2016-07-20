import uuid, random
import gameObject


class Cell:
    def __init__(self, _row, _col):
        self.obj_id = str(uuid.uuid4())
        self.row = _row
        self.col = _col
        self.contents = []

        empty_space = gameObject.EmptySpace(self)
        self.contents.append(empty_space)

    def add_game_object(self, x):
        self.contents.append(x)

    def add_ore_deposit(self):
        a = gameObject.OreDeposit(self)
        self.contents.append(a)

    def remove_object(self, object_id):
        for i in range(0, len(self.contents)):
            if self.contents[i].obj_id == object_id:
                del self.contents[i]

    def contains_object_type(self, obj_type_name):
        for obj in self.contents:
            if obj.__class__.__name__ == obj_type_name:
                return True, obj.obj_id
            else:
                return False, ''

    def render(self):
        priority = ['Player', 'OreDeposit', 'EmptySpace']
        for i in priority:
            if self.contains_object_type(i)[0]:
                for obj in self.contents:
                    if obj.__class__.__name__ == i:
                        return obj.icon
