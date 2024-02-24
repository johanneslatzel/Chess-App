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
s_ambigous_rook_moves: str = """
[Event "Live Chess"]
[Site "Chess.com"]
[Date "2023.04.07"]
[Round "?"]
[White "johanneslatzel"]
[Black "stiixto"]
[Result "1/2-1/2"]
[SetUp "1"]
[FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w KQkq -"]
[ECO "A00"]
[WhiteElo "858"]
[BlackElo "504"]
[TimeControl "300"]
[EndTime "10:39:00 PDT"]
[Termination "Game drawn by insufficient material"]

1. d3 {[%timestamp 1]} 1... e5 {[%timestamp 1]} 2. Nf3 {[%timestamp 8]} 2... Nc6
{[%timestamp 19]} 3. g3 {[%timestamp 17]} 3... Nd4 {[%timestamp 31]} 4. Nxd4
{[%timestamp 113]} 4... exd4 {[%timestamp 1]} 5. Bg2 {[%timestamp 10]} 5... Bb4+
{[%timestamp 16]} 6. c3 {[%timestamp 26]} 6... Ba5 {[%timestamp 19]} 7. Bd2
{[%timestamp 23]} 7... d5 {[%timestamp 58]} 8. cxd4 {[%timestamp 30]} 8... Bg4
{[%timestamp 42]} 9. Bxa5 {[%timestamp 21]} 9... Nf6 {[%timestamp 63]} 10. f3
{[%timestamp 14]} 10... Bh5 {[%timestamp 51]} 11. O-O {[%timestamp 20]} 11...
O-O {[%timestamp 24]} 12. Bb4 {[%timestamp 45]} 12... Re8 {[%timestamp 19]} 13.
e4 {[%timestamp 39]} 13... c6 {[%timestamp 63]} 14. Bc3 {[%timestamp 69]} 14...
h6 {[%timestamp 55]} 15. Nd2 {[%timestamp 26]} 15... Qb6 {[%timestamp 183]} 16.
Nb3 {[%timestamp 63]} 16... a5 {[%timestamp 115]} 17. a4 {[%timestamp 128]}
17... Qxb3 {[%timestamp 83]} 18. Ra3 {[%timestamp 132]} 18... Qc2 {[%timestamp
69]} 19. Raa1 {[%timestamp 87]} 19... Qxd3 {[%timestamp 34]} 20. Rad1
{[%timestamp 42]} 20... Qe3+ {[%timestamp 32]} 21. Kh1 {[%timestamp 35]} 21...
g5 {[%timestamp 128]} 22. Rfe1 {[%timestamp 16]} 22... Qxe1+ {[%timestamp 91]}
23. Rxe1 {[%timestamp 11]} 23... g4 {[%timestamp 32]} 24. Rf1 {[%timestamp 116]}
24... dxe4 {[%timestamp 130]} 25. fxg4 {[%timestamp 88]} 25... Bxg4 {[%timestamp
35]} 26. d5 {[%timestamp 14]} 26... cxd5 {[%timestamp 18]} 27. Bxf6 {[%timestamp
12]} 27... e3 {[%timestamp 53]} 28. Re1 {[%timestamp 58]} 28... e2 {[%timestamp
24]} 29. h3 {[%timestamp 32]} 29... Bh5 {[%timestamp 22]} 30. g4 {[%timestamp
14]} 30... Bg6 {[%timestamp 88]} 31. Bxd5 {[%timestamp 55]} 31... Bd3
{[%timestamp 34]} 32. g5 {[%timestamp 156]} 32... Rab8 {[%timestamp 133]} 33.
gxh6 {[%timestamp 36]} 33... b5 {[%timestamp 55]} 34. Rg1+ {[%timestamp 368]}
34... Bg6 {[%timestamp 139]} 35. Rxg6+ {[%timestamp 125]} 35... Kh7 {[%timestamp
61]} 36. Rg1 {[%timestamp 306]} 36... Kxh6 {[%timestamp 79]} 37. Re1
{[%timestamp 263]} 37... bxa4 {[%timestamp 18]} 38. Bxf7 {[%timestamp 41]} 38...
a3 {[%timestamp 23]} 39. bxa3 {[%timestamp 41]} 39... a4 {[%timestamp 38]} 40.
Bxe8 {[%timestamp 13]} 40... Rb3 {[%timestamp 73]} 41. Rxe2 {[%timestamp 26]}
41... Rxa3 {[%timestamp 17]} 42. Bf7 {[%timestamp 20]} 42... Rxh3+ {[%timestamp
36]} 43. Kg2 {[%timestamp 15]} 43... Rh5 {[%timestamp 20]} 44. Ra2 {[%timestamp
39]} 44... a3 {[%timestamp 97]} 45. Kg3 {[%timestamp 12]} 45... Rf5 {[%timestamp
63]} 46. Bg5+ {[%timestamp 50]} 46... Kxg5 {[%timestamp 27]} 47. Bc4
{[%timestamp 16]} 47... Rc5 {[%timestamp 54]} 48. Rxa3 {[%timestamp 11]} 48...
Rxc4 {[%timestamp 15]} 49. Rf3 {[%timestamp 13]} 49... Rc5 {[%timestamp 39]} 50.
Re3 {[%timestamp 9]} 50... Rf5 {[%timestamp 8]} 51. Rf3 {[%timestamp 16]} 51...
Rf6 {[%timestamp 11]} 52. Rxf6 {[%timestamp 11]} 52... Kxf6 {[%timestamp 16]}
1/2-1/2
"""


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


class TestQueenlessGameWithAmbigiousRookMove(unittest.TestCase):

    def test_queenless_game_with_ambigous_rook_moves(self):
        game = read_game(StringIO(s_ambigous_rook_moves))
        moves: list[str] = pgn_mainline_to_moves(game)
        self.assertEqual(moves[36], "Raa1")
        self.assertEqual(moves[38], "Rad1")
