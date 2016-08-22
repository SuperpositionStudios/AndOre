import uuid
from master_game.corporation import Corporation


class Player:

    def __init__(self, _corp: Corporation):
        self.node = 'Panagoul'
        self.corp = _corp
        self.uid = str(uuid.uuid4())
