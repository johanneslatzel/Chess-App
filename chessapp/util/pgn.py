def moves_to_pgn(moves, white_first_move: bool) -> str:
    """ this method converts a list of moves to a pgn string

    Args:
        moves ([str]): array of moves as strings
        white_first_move (bool): whether the first move is a move of the player with the white pieces

    Returns:
        str: the pgn string
    """
    pgn = ""
    for i in range(0, len(moves)):
        if (i % 2 == 0 and white_first_move) or (i % 2 != 0 and not white_first_move):
            pgn += " " + str(i // 2 + 1) + "."
        if i == 0 and not white_first_move:
            pgn += ".."
        pgn += " " + str(moves[i])
    return pgn
