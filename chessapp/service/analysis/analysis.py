import asyncio
from dataclasses import dataclass
from chessapp.model.database.database import Evaluation, GameDocument


@dataclass
class GameAnalysis:
    game: GameDocument
    evaluations: list[Evaluation]


class AnalysisService():

    def __init__(self):
        pass

    async def analyse_game(self, game: GameDocument) -> None:
        pass

    def dispatch_game(self, game: GameDocument) -> None:
        pass
