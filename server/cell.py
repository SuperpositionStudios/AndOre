
import uuid, random
import gameObject
class Cell:
    def __init__(self, world, x, y):
        self.x = x
        self.y = y
        self.world = world
        self.obj_id = str(uuid.uuid4())
        self.contents = []

    def destroy(self):
        self.world = None
        self.contents = None
        for obj in self.contents:
            i.leave_cell(self)

    def add_object(self,obj):
        if(obj.cell != self):
            obj.cell = self

        self.contents.append(obj)

    def add_ore_deposit(self):
        ore = gameObject.OreDeposit()
        self.add_object(ore)

    def remove_object(self, object_id):
        for i in range(0, len(self.contents)):
            if self.contents[i].obj_id == object_id:
                del self.contents[i]

    def contains_object_type(self, obj_type_name):
        for obj in self.contents:
            if obj.__class__.__name__ == obj_type_name:
                return True, obj.obj_id
        return False, ''

    def can_enter(self):
        for obj in self.contents:
            if not obj.can_enter:
                return False

        return True


    def try_get_cell_by_offset(self, xOffset, yOffset):
        return self.world.get_cell(self.x + xOffset, self.y + yOffset)
        

    def render(self):
        priority = ['Player', 'OreDeposit']
        for i in priority:
            if self.contains_object_type(i)[0]:
                for obj in self.contents:
                    if obj.__class__.__name__ == i:
                        return obj.icon
        return '#'

