import asyncio
from chessapp.model.database.database import GameDocument

class AnalysisService():

    def __init__(self):
        pass

    async def analyse_game(self, game: GameDocument) -> None:
        pass

    def dispatch_game(self, game: GameDocument) -> None:
        pass
