import uuid, random
class GameObject:
	def __init__(self):
		self.cell = None
		self.obj_id = str(uuid.uuid4())
		self.blocking = False

	def leave_cell(self, cell):
		self.cell.remove_object(self)
		self.cell = None

	def change_cell(self, new_cell):
		if self.cell != None:
			self.leave_cell(self)
		new_cell.add_object(self)


class OreDeposit(GameObject):

    def __init__(self):
        super().__init__()
        self.icon = '$'
        self.blocking = True