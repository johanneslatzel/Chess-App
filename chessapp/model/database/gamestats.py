from chessapp.model.database.database import GameDocument


s_low_elo_bound: float = 0
s_high_elo_bound: float = 4000
s_elo_accuracy: float = 0.01


def expected_score(games: list[GameDocument], player_name: str, proposed_elo: float) -> float:
    """ this function calculates the expected performance of a player based on a list of games by the player
    player_name. Read (https://en.wikipedia.org/wiki/Performance_rating_(chess))[https://en.wikipedia.org/wiki/Performance_rating_(chess)]
    for further information on the algorithm. 

    Args:
        games (list[GameDocument]): list of the games
        player_name (str): target player whose expected performance is calculated

    Returns:
        float: expected performance of the player over the games
    """
    score: float = 0
    for game in games:
        opponent_elo: float = 0
        if game.white == player_name:
            opponent_elo = game.black_elo
        elif game.black == player_name:
            opponent_elo = game.white_elo
        else:
            raise Exception("player not in game " + game.id)
        score += 1 / (1 + 10 ** ((opponent_elo - proposed_elo) / 400))
    return score


def interpret_game_result(game: GameDocument, player_name: str) -> float:
    """interprets the result of a game for a player with player_name. The result is returned as a float
    where 1 is a win, 0 is a loss and 0.5 is a draw.

    Args:
        game (GameDocument): the game
        player_name (str): the player

    Raises:
        Exception: game result is not 1-0, 0-1 or 1/2-1/2
        Exception: game is not played by player_name

    Returns:
        float: the result of the game for the player
    """
    result: float = 0
    if game.result == "1-0":
        result = 1
    elif game.result == "0-1":
        result = 0
    elif game.result == "1/2-1/2":
        result = 0.5
    else:
        raise Exception("game result " + game.result +
                        " not interpretable " + game.id)
    if game.white == player_name:
        return result
    if game.black == player_name:
        return 1 - result
    raise Exception("player not in game " + game.id)


def game_score(games: list[GameDocument], player_name: str) -> float:
    """ this function calculates a players score based on a list of games by the player (e.g. the sum of the results of the games)

    Args:
        games (list[GameDocument]): the games
        player_name (str): name of the player

    Returns:
        float: the score of the player over the games
    """
    score: float = 0
    for game in games:
        score += interpret_game_result(game, player_name)
    return score


def game_performance(games: list[GameDocument], player_name: str) -> float:
    """ this function calculates a players performance based on a list of games by the player
    player_name. Read (https://en.wikipedia.org/wiki/Performance_rating_(chess))[https://en.wikipedia.org/wiki/Performance_rating_(chess)]
    for further information on the algorithm. 

    Args:
        games (list[GameDocument]): list of the games
        player_name (str): target player whose performance is calculated

    Returns:
        float: performance of the player over the games
    """
    score: float = game_score(games, player_name)
    if score == 0:
        return float("-inf")
    if int(score) == len(games):
        return float("inf")
    low: float = s_low_elo_bound
    high: float = s_high_elo_bound
    while high - low > s_elo_accuracy:
        mid: float = (low + high) / 2
        if expected_score(games, player_name, mid) < score:
            low = mid
        else:
            high = mid
    return high
