from chessapp.model.chesstree import ChessTree, get_fen_from_board
from chessapp.view.chessboardwidget import PieceMovement
from chess import Board
import chess
import chessapp.model.move
from chessapp.view.module import ChessboardAndLogModule, create_method_action, MethodAction
from chessapp.controller.engine import Engine, MoveDescriptor
import traceback
from chessapp.model.node import Node
import chess
from chessapp.model.sourcetype import SourceType

s_eval_time_seconds = 60
s_eval_depth = 20
s_best_moves_eval_depth = 30
s_best_moves_multipv = 3


class Explorer(ChessboardAndLogModule):
    """ Explore the ChessTree by playing moves on the board. The quality of the moves will be analysed by the engine and icons
    indicating the quality will be shown on the board. An evalbar is shown to further indicate the position evaluation. This
    module has several actions to both analyse a positon and show moves for a position that already have been found and analysed.
    """

    def __init__(self, app, tree: ChessTree):
        """ Create a new Explorer module. 

        Args:
            app (_type_): _description_
            tree (ChessTree): _description_
        """
        super().__init__(app, "Explorer", [
            create_method_action(app, "Analyse d=25", self.analyse_d25),
            create_method_action(app, "Analyse d=30", self.analyse_d30),
            create_method_action(app, "Analyse d=35", self.analyse_d35),
            create_method_action(app, "Back", self.back),
            create_method_action(app, "Find Best Moves: d=" + str(s_best_moves_eval_depth) +
                                 ", multipv=" + str(s_best_moves_multipv), self.find_best_moves),
            create_method_action(app, "Flip Board", self.flip_board),
            create_method_action(app, "Reset", self.reset_board),
            create_method_action(app, "Show FEN", self.show_fen),
            create_method_action(app, "Show Known Moves",
                                 self.show_known_moves)
        ])
        self.app = app
        self.tree = tree
        self.board = Board()
        self.engine = Engine()
        self.previous_node = None
        self.last_move = None

    def on_register(self):
        self.chess_board_widget.back_actions.append(self.back)
        self.reset_board()
        self.chess_board_widget.view_white()
        self.chess_board_widget.eval_bar.is_visible = True
        self.chess_board_widget.board.show_best_move = True

    def find_best_moves(self):
        base_fen = get_fen_from_board(self.board)
        base_board = Board(base_fen)
        node: Node = self.tree.get(base_fen)
        self.log_message("finding up to " + str(s_best_moves_multipv) + " best moves for position " +
                         str(node.state) + " at depth " + str(s_best_moves_eval_depth))
        try:
            best_moves = self.engine.find_best_moves(
                base_board, s_eval_time_seconds, s_best_moves_eval_depth, multipv=s_best_moves_multipv)
        except Exception as e:
            print("error while analysing position in explorer")
            print(e)
            return
        for move_descriptor in best_moves:
            self.consume_move_descriptor(move_descriptor)
        self.display()

    def back(self):
        try:
            self.board.pop()
            self.reset_last_move()
            self.display(False)
        except IndexError:
            pass

    def analyse_d25(self):
        self.analyse_position(25)

    def analyse_d30(self):
        self.analyse_position(30)

    def analyse_d35(self):
        self.analyse_position(35)

    def consume_move_descriptor(self, move_descriptor: MoveDescriptor):
        copy_board = Board(move_descriptor.origin_fen)
        san: str = copy_board.san(move_descriptor.pv[0])
        copy_board.push_san(san)
        fen_result = get_fen_from_board(copy_board)
        node_result = self.tree.get(fen_result)
        if node_result.eval_depth < move_descriptor.depth:
            node_result.update(
                move_descriptor.eval, move_descriptor.depth - 1, move_descriptor.is_mate)
        origin_node = self.tree.get(move_descriptor.origin_fen)
        origin_node.update(move_descriptor.eval,
                           move_descriptor.depth, move_descriptor.is_mate)
        move = chessapp.model.move.Move(self.tree, san, fen_result,
                                        source=SourceType.ENGINE_SYNTHETIC)
        origin_node.add(move)
        self.log_message("found move " + san + " with score " + str(move_descriptor.eval) +
                         " and cp loss " + str(origin_node.get_cp_loss(move)) + " at depth " + str(origin_node.eval_depth) + (
            " (which is a forced mate)" if origin_node.is_mate else "")
            + " from source " + node_result.source().sformat())

    def analyse_position(self, depth: int = s_eval_depth):
        base_fen = get_fen_from_board(self.board)
        base_board = Board(base_fen)
        node: Node = self.tree.get(base_fen)
        if (node.eval_depth < depth or len(node.moves) == 0) and not node.is_mate:
            self.log_message("analysing position")
            try:
                best_moves = self.engine.find_best_moves(
                    base_board, s_eval_time_seconds, depth, multipv=1)
                for best_move in best_moves:
                    self.consume_move_descriptor(best_move)
            except Exception as e:
                print("error while analysing position in explorer")
                print(e)
                return
            self.display(perform_analysis=False)
            self.log_message("position analysed")

    def flip_board(self):
        self.chess_board_widget.flip_board()

    def set_board(self, board: Board):
        if not board:
            return
        self.reset_board()
        self.board = board.copy()
        self.display()

    def set_position(self, fen: str):
        self.reset_board()
        self.board = Board(fen)
        self.display()

    def display(self, perform_analysis: bool = True, play_sound: bool = False):
        node = self.tree.get(get_fen_from_board(self.board))
        self.chess_board_widget.display(
            self.board, node, self.previous_node, self.last_move, play_sound=play_sound)
        if perform_analysis:
            self.app.threadpool.start(MethodAction(self.analyse_d25))

    def show_fen(self):
        self.log_message(get_fen_from_board(self.board))

    def show_known_moves(self):
        self.show_fen()
        node = self.tree.get(get_fen_from_board(self.board))
        if node.has_move():
            for move in node.moves:
                self.log_message(move.get_info(node))
        else:
            self.log_message("no moves known for this node")

    def on_piece_movement(self, piece_movement: PieceMovement):
        if self.about_to_close():
            return
        self.last_move = None
        self.previous_node = None
        try:
            fen = get_fen_from_board(self.board)
            node = self.tree.get(fen)
            san = self.board.san(chess.Move.from_uci(
                piece_movement.uci_format()))
            board_copy = Board(fen)
            board_copy.push_san(san)
            result = get_fen_from_board(board_copy)
            move = chessapp.model.move.Move(
                self.tree, san, result, source=SourceType.MANUAL_EXPLORATION)
            if not node.knows_move(move):
                node.add(move)
            self.board.push_san(san)
            self.previous_node = node
            self.last_move = move
            self.display(play_sound=True)
        except Exception as e:
            print("error while exploring")
            print(traceback.format_exc())

    def reset_last_move(self):
        self.last_move = None
        self.previous_node = None

    def reset_board(self):
        self.board = Board()
        self.reset_last_move()
        self.chess_board_widget.reset()
        self.display()

    def on_close(self):
        self.engine.close()
