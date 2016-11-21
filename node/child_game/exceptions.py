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