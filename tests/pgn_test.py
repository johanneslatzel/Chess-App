from io import StringIO
import unittest
from chess.pgn import Game, read_game
from chessapp.util.pgn import pgn_mainline_to_moves, split_pgn

s_game_1: str = """
[Event "Rated Blitz game"]
[Site "https://lichess.org/013rQeTS"]
[Date "2024.02.17"]
[White "Tonwa"]
[Black "johannes_latzel"]
[Result "0-1"]
[UTCDate "2024.02.17"]
[UTCTime "23:18:42"]
[WhiteElo "1488"]
[BlackElo "1518"]
[WhiteRatingDiff "-5"]
[BlackRatingDiff "+5"]
[Variant "Standard"]
[TimeControl "180+2"]
[ECO "B10"]
[Opening "Caro-Kann Defense: Accelerated Panov Attack, Modern Variation"]
[Termination "Normal"]
[Annotator "lichess.org"]

1. e4 c6 2. c4 d5 3. exd5 cxd5 4. cxd5 Nf6 { B10 Caro-Kann Defense: Accelerated Panov Attack, Modern Variation } 5. d4 Nxd5 6. Nc3 e6 7. Nf3 Nc6 8. Bb5 Bd7 9. Qe2 Be7 10. Bxc6 Bxc6 11. Ne5 O-O 12. Qg4 Nf6 13. Qg3 Re8 14. Bh6 g6 15. Nxc6 bxc6 16. Qe5 Bf8 17. Bg5 Bg7 18. Bxf6 Bxf6 19. Qf4 Bxd4 20. Ne4 Bxb2 21. Ng5 Qa5+ 22. Ke2 f5 23. Qh4 Qe5+ 24. Kf3 Qc3+ 25. Kf4 Qc4+ 26. Kg3 Qxh4+ 27. Kxh4 Bxa1 28. Rxa1 e5 29. Rc1 Rac8 30. Rc5 e4 31. Kg3 h6 32. Nh3 Kg7 33. Kf4 Re6 34. Ng1 Rb8 35. a4 Rb2 36. Nh3 a6 37. a5 Rb5 38. Rc3 Rxa5 { White resigns. } 0-1
"""
s_game_2: str = """
[Event "Rated Blitz game"]
[Site "https://lichess.org/4DOtc3Li"]
[Date "2024.02.17"]
[White "johannes_latzel"]
[Black "mdvjk"]
[Result "0-1"]
[UTCDate "2024.02.17"]
[UTCTime "23:18:13"]
[WhiteElo "1523"]
[BlackElo "1554"]
[WhiteRatingDiff "-5"]
[BlackRatingDiff "+6"]
[Variant "Standard"]
[TimeControl "180+2"]
[ECO "D06"]
[Opening "Queen's Gambit Declined: Marshall Defense"]
[Termination "Normal"]
[Annotator "lichess.org"]

1. d4 d5 2. c4 Nf6 { D06 Queen's Gambit Declined: Marshall Defense } 3. cxd5 Nxd5 4. Nf3 e6 5. e4 Nb4 6. Qa4+ Bd7 7. Qxb4 Bxb4+ { White resigns. } 0-1
"""
s_games: str = s_game_1 + "\n\n" + s_game_2
s_short_pgn: str = "1. d4 d5 2. c4 Nf6"
s_short_longer_pgn: str = "1. e4 c6 2. c4 d5 3. exd5 cxd5 4. cxd5 Nf6 5. d4 Nxd5 6. Nc3 e6 7. Nf3"
s_variations: str = "1. d4 (1. e4 e5 2. Nf3 (2. d4 exd4 3. Qxd4) 2... Nc6) 1... d5 (1... Nf6 2. c4 e6 3. Nc3 Bb4) 2. c4 e6"


class TestSplitPgn(unittest.TestCase):

    def test_game_1(self):
        games: list[Game] = split_pgn(s_game_1)
        self.assertEqual(len(games), 1)

    def test_game_2(self):
        games: list[Game] = split_pgn(s_game_2)
        self.assertEqual(len(games), 1)

    def test_game_3(self):
        games: list[Game] = split_pgn(s_games)
        self.assertEqual(len(games), 2)


class TestPgnToMainlineMoves(unittest.TestCase):

    def test_1(self):
        game = read_game(StringIO(s_short_pgn))
        moves: list[str] = pgn_mainline_to_moves(game)
        self.assertEqual(moves, ["d4", "d5", "c4", "Nf6"])

    def test_2(self):
        game = read_game(StringIO(s_short_longer_pgn))
        moves: list[str] = pgn_mainline_to_moves(game)
        self.assertEqual(moves, ["e4", "c6", "c4", "d5", "exd5",
                         "cxd5", "cxd5", "Nf6", "d4", "Nxd5", "Nc3", "e6", "Nf3"])

    def test_3(self):
        game = read_game(StringIO(s_variations))
        moves: list[str] = pgn_mainline_to_moves(game)
        self.assertEqual(moves, ["d4", "d5", "c4", "e6"])
