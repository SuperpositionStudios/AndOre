class InvalidAid(Exception):
	def __init__(self, aid: str):
		self.message = "The supplied aid {} was invalid".format(aid)
