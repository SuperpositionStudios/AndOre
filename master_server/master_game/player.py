import uuid


class Player:

    def __init__(self, _corp):
        self.node = 'Cistuvaert'
        self.corp = _corp
        self.uid = str(uuid.uuid4())
