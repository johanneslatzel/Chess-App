from chess import Board


def reduce_fen(fen: str) -> str:
    """ removes the last two parts of the fen string (halfmove clock and fullmove number)

    Args:
        fen (str): fen string

    Returns:
        str: fen string without the last two parts
    """
    fen_arr = fen.split(" ")
    del fen_arr[-1]
    del fen_arr[-1]
    return " ".join(fen_arr)


def get_reduced_fen_from_board(board: Board) -> str:
    """ returns the reduced fen string of a board

    Args:
        board (Board): the board

    Returns:
        str: the reduced fen string
    """
    return reduce_fen(board.fen())
