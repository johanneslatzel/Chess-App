import unittest
from chessapp.model.database.database import GameDocument
from chessapp.model.database.gamestats import game_performance, interpret_game_result, game_score


s_games = [
    GameDocument([], white="a", black="b", result="1-0",
                 white_elo=1577, black_elo=1851),
    GameDocument([], white="c", black="a", result="1-0",
                 white_elo=2457, black_elo=1577),
    GameDocument([], white="a", black="d", result="1/2-1/2",
                 white_elo=1577, black_elo=1700),
    GameDocument([], white="a", black="e", result="0-1",
                 white_elo=1577, black_elo=2020),
    GameDocument([], white="b", black="a", result="1/2-1/2",
                 white_elo=1851, black_elo=1577)
]


class TestGameScore(unittest.TestCase):

    def test_games(self):
        self.assertEqual(game_score(s_games, "a"), 2)
        self.assertEqual(game_score([s_games[0], s_games[4]], "b"), 0.5)


class TestInterpretGameResult(unittest.TestCase):

    def test_result_game1(self):
        self.assertEqual(interpret_game_result(s_games[0], "a"), 1)
        self.assertEqual(interpret_game_result(s_games[0], "b"), 0)

    def test_result_game2(self):
        self.assertEqual(interpret_game_result(s_games[1], "a"), 0)
        self.assertEqual(interpret_game_result(s_games[1], "c"), 1)

    def test_result_game3(self):
        self.assertEqual(interpret_game_result(s_games[2], "a"), 0.5)
        self.assertEqual(interpret_game_result(s_games[2], "d"), 0.5)

    def test_result_game4(self):
        self.assertEqual(interpret_game_result(s_games[3], "a"), 0)
        self.assertEqual(interpret_game_result(s_games[3], "e"), 1)

    def test_result_game5(self):
        self.assertEqual(interpret_game_result(s_games[4], "b"), 0.5)
        self.assertEqual(interpret_game_result(s_games[4], "a"), 0.5)


class TestExpectedScore(unittest.TestCase):

    def test_expected_score(self):
        self.assertEqual(int(game_performance(s_games, "a")), 1849)
        self.assertEqual(int(game_performance(
            [s_games[0], s_games[4]], "b")), 1386)
