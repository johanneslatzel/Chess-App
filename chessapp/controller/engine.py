from chess import Board
from chess.engine import Limit, SimpleEngine
from chessapp.model.chesstree import get_fen_from_board
from chessapp.util.paths import get_stockfish_exe

s_analyse_desired_time_seconds: int = 30
s_analyse_desired_depth: int = 30
s_engine_number_of_threads: int = 14
s_multi_pv: int = 1


class MoveDescriptor:

    def __init__(self, eval: float, depth: int, is_mate: bool, pv, origin_fen: str):
        self.eval: float = eval
        self.depth: int = depth
        self.is_mate: bool = is_mate
        self.pv = pv
        self.origin_fen = origin_fen


class Engine:

    def __init__(self) -> None:
        self.engine = SimpleEngine.popen_uci(get_stockfish_exe())

    def find_best_moves(self, board: Board, time: int = s_analyse_desired_time_seconds, depth: int = s_analyse_desired_depth, multipv: int = s_multi_pv):
        result = self.engine.analyse(board, Limit(
            time=time, depth=depth), options={"Threads": s_engine_number_of_threads}, multipv=multipv)
        best_moves = []
        for i in range(0, len(result)):
            eval = 0
            pov_score = result[i]["score"]
            if pov_score.is_mate():
                eval = float(100)
                if not pov_score.turn:
                    eval = -eval
            else:
                eval = pov_score.white().score() / 100.0
            best_moves.append(MoveDescriptor(
                eval, result[i]["depth"], pov_score.is_mate(), result[i]["pv"], get_fen_from_board(board)))
        return best_moves

    # https://stackoverflow.com/questions/58556338/python-evaluating-a-board-position-using-stockfish-from-the-python-chess-librar
    def score(self, board: Board, time: int = s_analyse_desired_time_seconds, depth: int = s_analyse_desired_depth):
        result = self.engine.analyse(board, Limit(
            time=time, depth=depth), options={"Threads": s_engine_number_of_threads}, multipv=s_multi_pv)
        best_eval = 0
        is_mate = False
        for i in range(0, len(result)):
            eval = 0
            pov_score = result[i]["score"]
            if pov_score.is_mate():
                is_mate = True
                eval = float(100)
                if not pov_score.turn:
                    eval = -eval
            else:
                eval = pov_score.white().score() / 100.0
            # best move is first entry in result array
            if i == 0:
                best_eval = eval
        return best_eval, result[0]["depth"], is_mate

    def close(self):
        self.engine.close()
