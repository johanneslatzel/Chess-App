from chess import Board
from chess.engine import Limit, SimpleEngine
from chessapp.model.chesstree import get_fen_from_board
from chessapp.util.paths import get_stockfish_exe

s_analyse_desired_time_seconds: int = 30
s_analyse_desired_depth: int = 30
s_engine_number_of_threads: int = 14
s_multi_pv: int = 1


class MoveDescriptor:
    """a descriptor for a move, containing the evaluation, depth, whether it is a mate, the pv (array of chess.Move) and the fen of the board before the move was made
    """

    def __init__(self, eval: float, depth: int, is_mate: bool, pv, origin_fen: str):
        """_summary_

        Args:
            eval (float): evaluation of the move (which is the resulting positon after the move was made) in centipawns/100 or as 100 if mate
            depth (int): depth of the evaluation
            is_mate (bool): whether the move is a mate
            pv ([chess.Move]): array of chess.Move in the principal variation (pv)
            origin_fen (str): the fen of the board before the move was made
        """
        self.eval: float = eval
        self.depth: int = depth
        self.is_mate: bool = is_mate
        self.pv = pv
        self.origin_fen: str = origin_fen


class Engine:
    """a wrapper for the stockfish engine
    """

    def __init__(self) -> None:
        """ initializes the engine (e.g. opens stockfish)
        """
        self.engine = SimpleEngine.popen_uci(get_stockfish_exe())

    def find_best_moves(self, board: Board, time: int = s_analyse_desired_time_seconds, depth: int = s_analyse_desired_depth, multipv: int = s_multi_pv) -> [MoveDescriptor]:
        """finds the best moves for the given board

        Args:
            board (Board): the board to find the best moves for
            time (int, optional): Defaults to s_analyse_desired_time_seconds. the time in seconds the engine is given to analyse the position.
            depth (int, optional): Defaults to s_analyse_desired_depth. the depth the engine is given to analyse the position.
            multipv (int, optional): Defaults to s_multi_pv. the number of principal variations to return (e.g. the number of best moves + their specific variations)

        Returns:
            [MoveDescriptor]: array of MoveDescriptor for the best moves
        """
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

    def score(self, board: Board, time: int = s_analyse_desired_time_seconds, depth: int = s_analyse_desired_depth):
        """scores the given board. @see https://stackoverflow.com/questions/58556338/python-evaluating-a-board-position-using-stockfish-from-the-python-chess-librar

        Args:
            board (Board): the board to score
            time (int, optional): Defaults to s_analyse_desired_time_seconds. the time in seconds the engine is given to analyse the position.
            depth (int, optional): Defaults to s_analyse_desired_depth. the depth the engine is given to analyse the position.

        Returns:
            tuple: (eval, depth, is_mate) where eval is the evaluation of the board in centipawns/100 or as 100 if mate, depth is the depth of the evaluation and is_mate is whether the board is a mate
        """
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
        """closes the engine (closes stockfish)
        """
        self.engine.close()
