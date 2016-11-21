class CellCoordinatesOutOfBoundsError(Exception):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.message = "You tried to get the cell at ({}, {}), which is out of bounds for the world".format(self.row,
                                                                                                            self.col)
