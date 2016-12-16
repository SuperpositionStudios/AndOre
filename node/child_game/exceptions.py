class CellCoordinatesOutOfBoundsError(Exception):
	def __init__(self, row, col):
		self.row = row
		self.col = col
		self.message = "You tried to get the cell at ({}, {}), which is out of bounds for the world".format(self.row,
																											self.col)


class CellCannotBeEnteredException(Exception):
	def __init__(self):
		self.message = "Cell cannot be entered"


class CorporationHasInsufficientFundsException(Exception):
	def __init__(self, corporation_id: str):
		self.message = "Corporation {} does not have enough funds".format(corporation_id)


class CellIsNotAdjacentToOreDepositException(Exception):
	def __init__(self):
		self.message = "Cell is not Adjacent to Ore Deposit"


class NoGameObjectOfThatClassFoundException(Exception):
	def __init__(self, base_class: str):
		self.message = "Did not find a game object whose base class is {}".format(base_class)


class NoGameObjectByThatObjectIDFoundException(Exception):
	def __init__(self):
		self.message = "Could not find a game object with the specified object id"


class CellIsNoneException(Exception):
	def __init__(self):
		self.message = "Cell is None"


class NoStarGatePresentException(Exception):
	def __init__(self):
		self.message = "No StarGate was found"


class NoPlayerFoundException(Exception):
	def __init__(self):
		self.message = "No player found"


class NoPlayersToAttackException(Exception):
	def __init__(self):
		self.message = "No players to attack"


class NoPharmacyFoundException(Exception):
	def __init__(self):
		self.message = "No Pharmacy Found"


class NoHospitalFoundException(Exception):
	def __init__(self):
		self.message = "No Hospital Found"


class NoCorporationOwnedBuildingFoundException(Exception):
	def __init__(self):
		self.message = "No Corporation Owned Building was Found"
