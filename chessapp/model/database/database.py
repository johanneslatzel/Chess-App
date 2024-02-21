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


class LichessDatabase(Database):
    def __init__(self, username: str, last_update: datetime = datetime.fromtimestamp(0)):
        super().__init__("lichess_" + username)
        self.username = username
        self.last_update: datetime = last_update
        self.games_uri: str = "https://lichess.org/api/games/user/"
        self.user_uri: str = "https://lichess.org/api/user/"
        self.update_interval_days: int = 14
        self.long_update_interval_days: int = 365
        self.games_table: Table = None
        self.config_table: Table = None

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
        if not data["createdAt"]:
            return
        createdAt: datetime = datetime.fromtimestamp(
            float(data["createdAt"]) / 1000)
        if self.last_update < createdAt:
            self.set_last_update(createdAt)

    def set_last_update(self, last_update: datetime) -> None:
        self.config_table.upsert(
            {"name": "last_update", "value": self.last_update.isoformat()}, Query().name == "last_update")
        self.last_update = last_update

    def open(self) -> None:
        super().open()
        self.init_db()
        self.init_last_update_datetime()

    def needs_updates(self) -> bool:
        return self.last_update + timedelta(hours=1) < datetime.now()

    def consume_game(self, pgn: str) -> None:
        games: list[Game] = split_pgn(pgn)
        for game in games:
            game_document = GameDocument.convert_from_game(game)
            self.games_table.upsert(
                game_document.__dict__, Query().id == game_document.id)

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
                self.consume_game(response.text)
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

    def close(self) -> None:
        super().close()
