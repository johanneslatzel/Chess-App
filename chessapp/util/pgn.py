from chess import Board
from chess.pgn import read_game
from io import StringIO
from chess.pgn import Game, GameNode


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


def pgn_mainline_to_moves(game: Game) -> list[str]:
    """ this method converts the mainline of a game to a list of moves (in SAN notation and ignoring all other variations)

    Args:
        game (Game): the game

    Returns:
        list[str]: the list of moves
    """
    line: list[str] = []
    node: GameNode = game
    board: Board = Board()
    while node != None:
        if not (node.variations and len(node.variations) > 0):
            break
        line.append(board.san(node.variations[0].move))
        board.push(node.variations[0].move)
        node = node.variations[0]
    return line


def split_pgn(pgn: str) -> list[Game]:
    """ this method splits a pgn string into a list of games

    Args:
        pgn (str): the pgn string

    Returns:
        list[Game]: the list of games
    """
    games: list[Game] = []
    input_str = StringIO(pgn)
    game = read_game(input_str)
    while game != None:
        games.append(game)
        game = read_game(input_str)
    return games
