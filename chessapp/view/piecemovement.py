class PieceMovement():
    def __init__(self, source_square: str, destination_square: str):
        self.source_square = source_square
        self.destination_square = destination_square
    
    def uci_format(self):
        return self.source_square + self.destination_square

    def __str__(self):
        return self.uci_format()
