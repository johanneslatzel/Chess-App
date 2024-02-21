from dataclasses import dataclass
from tinydb import TinyDB, Query
from tinydb.table import Table
from chessapp.util.paths import get_db_folder
from datetime import datetime, timedelta
import requests
from os.path import join, exists
from os import makedirs
from chessapp.util.pgn import split_pgn, pgn_mainline_to_moves
from chess.pgn import Game
from time import sleep


class Database():

    def __init__(self, name: str) -> None:
        self.name = name
        self.db = None

    def on_open(self) -> None:
        pass

    def on_close(self) -> None:
        pass

    def open(self) -> None:
        if not exists(get_db_folder()):
            makedirs(get_db_folder())
        self.db = TinyDB(join(get_db_folder(), f"{self.name}.json"))
        self.on_open()

    def close(self) -> None:
        self.db.close()
        self.on_close()


@dataclass
class GameDocument():
    moves: list[str]
    site: str = ""
    when: str = ""
    white: str = ""
    black: str = ""
    result: str = ""
    termination: str = ""
    time_control: str = ""
    variant: str = ""
    black_elo: int = 0
    white_elo: int = 0
    id = -1

    def convert_from_game(game: Game) -> "GameDocument":
        game_document: GameDocument = GameDocument(pgn_mainline_to_moves(game))
        if game.headers["Site"]:
            game_document.site = game.headers["Site"]
            if game_document.site.startswith("https://lichess.org/"):
                game_document.id = game_document.site[len(
                    "https://lichess.org/"):]
        if game.headers["UTCDate"] and game.headers["UTCTime"]:
            game_document.when = game.headers["UTCDate"] + \
                " " + game.headers["UTCTime"]
        if game.headers["White"]:
            game_document.white = game.headers["White"]
        if game.headers["Black"]:
            game_document.black = game.headers["Black"]
        if game.headers["Result"]:
            game_document.result = game.headers["Result"]
        if game.headers["Termination"]:
            game_document.termination = game.headers["Termination"]
        if game.headers["TimeControl"]:
            game_document.time_control = game.headers["TimeControl"]
        if game.headers["Variant"]:
            game_document.variant = game.headers["Variant"]
        if game.headers["BlackElo"] and game.headers["BlackElo"] != "?":
            game_document.black_elo = int(game.headers["BlackElo"])
        if game.headers["WhiteElo"] and game.headers["WhiteElo"] != "?":
            game_document.white_elo = int(game.headers["WhiteElo"])
        if not game_document.id:
            raise Exception("game id is not set")
        return game_document


class ChessWebsiteDatabase(Database):
    def __init__(self, username: str, games_uri: str, user_uri: str, user_joined_keyword: str, last_update: datetime = datetime.fromtimestamp(0)):
        super().__init__("lichess_" + username)
        self.username: str = username
        self.last_update: datetime = last_update
        self.games_uri: str = games_uri
        self.user_uri: str = user_uri
        self.update_interval_days: int = 14
        self.long_update_interval_days: int = 365
        self.games_table: Table = None
        self.config_table: Table = None
        self.user_joined_keyword: str = user_joined_keyword
        self.update_time_delta_hours: int = 1

    def get_user_data(self) -> dict:
        response = requests.get(self.user_uri + self.username)
        if not response.ok:
            raise Exception(
                "unable to fetch data from lichess.org for reason: " + response.reason)
        return response.json()

    def init_db(self) -> None:
        self.games_table = self.db.table("games")
        self.config_table = self.db.table("config")
        for item in self.config_table:
            if item["name"] == "last_update":
                self.last_update = datetime.fromisoformat(item["value"])

    def init_last_update_datetime(self) -> None:
        data = self.get_user_data()
        if not data[self.user_joined_keyword]:
            return
        createdAt: datetime = datetime.fromtimestamp(
            float(data[self.user_joined_keyword]) / 1000)
        if self.last_update < createdAt:
            self.set_last_update(createdAt)

    def set_last_update(self, last_update: datetime) -> None:
        self.config_table.upsert(
            {"name": "last_update", "value": self.last_update.isoformat()}, Query().name == "last_update")
        self.last_update = last_update

    def on_open(self) -> None:
        self.init_db()
        self.init_last_update_datetime()

    def needs_updates(self) -> bool:
        return self.last_update + timedelta(hours=self.update_time_delta_hours) < datetime.now()

    def consume_games(self, pgn: str) -> None:
        games: list[Game] = split_pgn(pgn)
        for game in games:
            game_document = GameDocument.convert_from_game(game)
            self.games_table.upsert(
                game_document.__dict__, Query().id == game_document.id)

    def update(self) -> int:
        raise NotImplementedError()

    def update_complete(self) -> None:
        raise NotImplementedError()


class LichessDatabase(ChessWebsiteDatabase):

    def __init__(self, username: str):
        super().__init__(username, "https://lichess.org/api/games/user/",
                         "https://lichess.org/api/user/", "createdAt")

    def update(self) -> int:
        until_datetime: datetime = datetime.now()
        difference = until_datetime - self.last_update
        if difference.days > self.update_interval_days:
            target_delta_days: int = self.update_interval_days
            if difference.days > self.long_update_interval_days:
                target_delta_days = self.long_update_interval_days
            until_datetime = self.last_update + \
                timedelta(days=target_delta_days)
        param = dict(
            since=int(datetime.timestamp(self.last_update) * 1000),
            until=int(datetime.timestamp(until_datetime) * 1000)
        )
        response = requests.get(self.games_uri + self.username, params=param)
        if response.ok:
            if response.text:
                self.consume_games(response.text)
            self.set_last_update(until_datetime)
        return response.status_code

    def update_complete(self) -> None:
        while self.needs_updates():
            return_code: int = self.update()
            if return_code == 429:
                print("received 429 by lichess, sleeping 60s")
                sleep(60)
            else:
                print("updated games to", str(self.last_update)
                      ), ", new number of games:", len(self.games_table)


class ChesscomDatabase(ChessWebsiteDatabase):

    def __init__(self, username: str):
        super().__init__(username, "https://api.chess.com/pub/player/",
                         "https://api.chess.com/pub/player", "joined")

    def download_month(self, year: int, month: int) -> int:
        response = requests.get(
            f"{self.games_uri}/{self.username}/games/{year}/{month}/pgn")
        if response.ok:
            self.consume_games(response.text)
        return response.status_code

    def update(self) -> int:
        until_now: datetime = datetime.now()
        target_month: int = until_now.month
        target_year: int = until_now.year
        skip_to_next_month: bool = False
        if until_now.year != self.last_update.year and until_now.month != self.last_update.month:
            target_month = self.last_update.month
            target_year = self.last_update.year
            skip_to_next_month = True
        return_code: int = self.download_month(target_year, target_month)
        if return_code == 200:
            if skip_to_next_month:
                skip_to_year: int = target_year
                skip_to_month: int = target_month + 1
                if skip_to_month > 12:
                    skip_to_month = 1
                    target_year += 1
                self.set_last_update(datetime(
                    year=skip_to_year, month=skip_to_month, day=1))
            else:
                self.set_last_update(until_now)
        return return_code

    def update_complete(self) -> None:
        while self.needs_updates():
            return_code: int = self.update()
            if return_code != 200:
                return
