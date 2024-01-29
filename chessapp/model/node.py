from chessapp.model.move import Move
from chessapp.model.sourcetype import SourceType
from random import Random
from chessapp.configuration import QUIZ_ACCEPT_EVAL_DIFF, QUIZ_ACCEPT_EVAL_DIFF_RELAXED, QUIZ_ACCEPT_RELAXED_SOURCES
from dataclasses import dataclass


@dataclass
class Backlink:
    """ A backlink links a node A to a previous node B such that playing the move in B leads to A.
    """
    node: object
    move: Move


class Node:
    """ A node represents a position in the chess tree. It contains the following information:
    - state: the fen of the position
    - eval: the evaluation of the position
    - eval_depth: the depth of the evaluation
    - is_mate: whether the position is a mate position or not
    - moves: the known moves of the position
    - backlinks: the links pointing to the known nodes leading to this node
    """

    def __init__(self, tree, fen: str, eval: float = 0, eval_depth: int = -1, is_mate: bool = False):
        """ creates a new node with the given fen

        Args:
            tree (ChessTree): the tree in which this node is contained
            fen (str): fen of the position
            eval (float, optional): evaluation of the position
            eval_depth (int, optional): depth of the evaluation
            is_mate (bool, optional): whether the position is a mate position or not
        """
        self.tree = tree
        self.state: str = fen
        self.moves = []
        self.backlinks = []
        self.eval: float = eval
        self.eval_depth: float = eval_depth
        self.is_mate: bool = is_mate

    def update(self, eval: float, eval_depth: int, is_mate: bool):
        """ updates the evaluation of this node if the given evaluation depth is deeper than the current one or
        if the new evaluation is a mate and the current evaluation is not a mate

        Args:
            eval (float): evaluation of the position
            eval_depth (int): depth of the evaluation
            is_mate (bool): whether the position is a mate position or not
        """
        if eval_depth > self.eval_depth or (not self.is_mate and is_mate):
            self.eval_depth = eval_depth
            self.eval = eval
            self.is_mate = is_mate

    def add(self, move: Move):
        """ adds a move to the node. if the move is already known, the source and the comment are updated if applicable

        Args:
            move (Move): _description_
        """
        for m in self.moves:
            if m.is_equivalent_to(move):
                if m.source.value < move.source.value:
                    m.source = move.source
                if move.comment and not m.comment:
                    m.comment = move.comment
                return
        self.moves.append(move)
        self.tree.get(move.result).backlink(self, move)

    def backlink(self, node, move: Move):
        """ adds a backlink to the node.
        TODO: this is kinda ugly. the backlink should be added to the node when the move is added to the node. Should Move know the fen of the positon it is played in?>

        Args:
            node (Node): previous node
            move (Move): move that leads from the previous node to this node
        """
        self.backlinks.append(Backlink(node, move))

    def knows_move(self, move: Move) -> bool:
        """ checks whether the node knows the given move

        Args:
            move (Move): move to check

        Returns:
            bool: True if the node knows the move, False otherwise
        """
        return self.get_equivalent_move(move) != None

    def get_equivalent_move(self, move: Move) -> Move | None:
        """ returns the equivalent move if the node knows the given move, None otherwise

        Args:
            move (Move): move to check

        Returns:
            Move | None: the equivalent move if the node knows the given move, None otherwise
        """
        for m in self.moves:
            if m.is_equivalent_to(move):
                return m
        return None

    def has_move(self) -> bool:
        """ checks whether the node knows at least one move

        Returns:
            bool: True if the node knows at least one move, False otherwise
        """
        return len(self.moves) != 0

    def total_frequency(self) -> int:
        """ returns the total frequency of all moves of the node (the sum of the frequencies of all moves)

        Returns:
            int: the total frequency of all moves of the node
        """
        sum: int = 0
        for move in self.moves:
            sum += move.frequency
        return sum

    def has_frequency(self) -> bool:
        """ checks whether the node has at least one move with a frequency > 0

        Returns:
            bool: True if the node has at least one move with a frequency > 0, False otherwise
        """
        return self.total_frequency() > 0

    def random_move(self, random: Random, use_frequency: bool = False) -> Move:
        """ returns a random move of the node. if use_frequency is True, the probability of a move to be chosen is
        proportional to the frequency of the move. if use_frequency is False, all moves have the same probability.
        TODO: move this method in a different module.

        Args:
            random (Random): _description_
            use_frequency (bool, optional): _description_. Defaults to False.

        Raises:
            Exception: _description_

        Returns:
            Move: _description_
        """
        if not use_frequency:
            return self.moves[random.randint(0, len(self.moves) - 1)]
        chosen_move = None
        total = self.total_frequency()
        sum = 0
        target = random.randint(0, total - 1)
        for move in self.moves:
            if sum + move.frequency > target:
                chosen_move = move
                break
            sum += move.frequency
        if chosen_move == None:
            raise Exception(
                "cannot chose a move. check frequencies of the moves of node " + self.state)
        return chosen_move

    def is_white_turn(self) -> bool:
        """ checks whether it is white's turn in the node. 
        TODO: decide if this method should be more efficient. Every time this method is called the fen of the node is split. Instead this could be a simple bool that is set on __init__.

        Returns:
            bool: True if it is white's turn in the node, False otherwise
        """
        return self.state.split(" ")[1] == "w"

    def get_cp_loss(self, move: Move) -> int:
        """ returns the centipawn loss of the given move. the centipawn loss is the difference between the evaluation
        of the node and the evaluation of the node that results from playing the specified move.
        TODO: figure out if this method has to be moved to a different module.

        Args:
            move (Move): move to check

        Returns:
            int: the centipawn loss of the given move
        """
        return round(abs(self.eval - move.eval()) * 100)

    def get_move_by_san(self, move_san: str) -> Move | None:
        """ returns the move with the given san if the node knows the move, None otherwise

        Args:
            move_san (str): san of the move to get

        Returns:
            Move | None: the move with the given san if the node knows the move, None otherwise
        """
        for move in self.moves:
            if move.san == move_san:
                return move
        return None

    def is_acceptable_move(self, move: Move) -> bool:
        """ checks whether the given move is acceptable. a move is acceptable if the difference between the evaluation
        of the node and the evaluation of the move is not too high. the maximum difference is defined in the configuration
        as QUIZ_ACCEPT_EVAL_DIFF. if the move is a move from a relaxed source, the maximum difference is defined in the
        configuration as QUIZ_ACCEPT_EVAL_DIFF_RELAXED. a source is relaxed if it is contained in the list
        QUIZ_ACCEPT_RELAXED_SOURCES in configuration.
        TODO: move this method in a different module.

        Args:
            move (Move): move to check

        Returns:
            bool: True if the move is acceptable, False otherwise
        """
        if move.eval_depth() < 0:
            return False
        eval_diff_accept = QUIZ_ACCEPT_EVAL_DIFF
        if move.source in QUIZ_ACCEPT_RELAXED_SOURCES:
            eval_diff_accept = QUIZ_ACCEPT_EVAL_DIFF_RELAXED
        # check turn player
        eval_best = self.eval
        if self.eval_depth < 0:
            best_move = self.get_best_move()
            if best_move != None:
                if best_move.eval_depth() > 0:
                    eval_best = best_move.eval()
            else:
                return True
        if self.is_white_turn():
            return eval_best - move.eval() <= eval_diff_accept
        else:
            return move.eval() - eval_best <= eval_diff_accept

    def has_acceptable_move(self) -> bool:
        """ checks whether the node has at least one acceptable move. @see is_acceptable_move.
        TODO: move this method in a different module.

        Returns:
            bool: True if the node has at least one acceptable move, False otherwise
        """
        for move in self.moves:
            if self.is_acceptable_move(move):
                return True
        return False

    def get_best_move(self, min_depth: int = 0) -> Move | None:
        """ returns the best move of the node. the best move is the move with the highest evaluation value amongst
        the moves with highest depth. if there is no move with at least a depth of min_depth, None is returned.


        Args:
            min_depth (int, optional): the minimum depth of the move to be returned.

        Returns:
            Move | None: the best move of the node
        """
        if len(self.moves) == 0:
            return None
        best_move = None
        # first search for a node as a baseline that has at least a depth of min_depth
        for move in self.moves:
            if not best_move or move.eval_depth() > best_move.eval_depth():
                best_move = move
        if not best_move:
            return None
        is_white_turn = self.is_white_turn()
        # now find a move that not only satisfies with depth min_depth but also has a better eval value
        for move in self.moves:
            if move.eval_depth() >= min_depth:
                if is_white_turn:
                    if move.eval() > best_move.eval():
                        best_move = move
                else:
                    if move.eval() < best_move.eval():
                        best_move = move
        return best_move

    def source(self) -> SourceType:
        """ returns the source of the node. the source is the highest source of all moves of the node.

        Returns:
            SourceType: the source of the node
        """
        source = SourceType.ENGINE_SYNTHETIC
        for backlink in self.backlinks:
            if backlink.move.source.value > source.value:
                source = backlink.move.source
        return source
