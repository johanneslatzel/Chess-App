from chessapp.model.sourcetype import SourceType


class Move:
    def __init__(self, tree, san: str, result: str, comment: str = "", source: SourceType = SourceType.default_value(), frequency: int = 0):
        """ creates a new move in the tree with the given SAN and resulting fen

        Args:
            tree (ChessTree): the tree in which this move is contained
            san (str): SAN of the move
            result (str): resulting fen after this move is played
            comment (str, optional): Defaults to "". comment for this move. this can be anything that might be useful to users that explore this move.
            source (SourceType, optional): Defaults to SourceType.default_value(). source of this move.
            frequency (int, optional): Defaults to 0. frequency of this move (how many times it has been played)
        """
        self.tree = tree
        self.san: str = san
        self.result: str = result
        self.comment: str = comment
        self.source: SourceType = source
        self.frequency: int = frequency

    def is_equivalent_to(self, other) -> bool:
        """ two moves are equivalent if they have the same SAN and resulting fen.

        Args:
            other (Move): the other move to compare to

        Returns:
            bool: True if the two moves are equivalent, False otherwise
        """
        return other != None and self.san == other.san and self.result == other.result

    def get_info(self, node) -> str:
        """ returns a string formatting information about this move in human readable form

        Args:
            node (Node): the node from which this move originates

        Returns:
            str: the information string in human readable form
        """
        info: str = self.san + " with eval " + str(self.eval()) + " at depth " + str(self.eval_depth(
        )) + " (cp loss = " + str(node.get_cp_loss(self)) + ") from source " + self.source.sformat()
        return info

    def eval(self) -> float:
        """ returns the evaluation of this move

        Returns:
            float: the evaluation of this move
        """
        return self.tree.get(self.result).eval

    def eval_depth(self) -> int:
        """ returns the evaluation depth of this move

        Returns:
            int: the evaluation depth of this move
        """
        return self.tree.get(self.result).eval_depth
