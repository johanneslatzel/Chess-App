from dataclasses import dataclass
from enum import Enum
from typing import Generator, Mapping
from chess import Board
from tinydb import TinyDB, Query, where
from tinydb.table import Table
from chessapp.util.paths import get_db_folder
from datetime import datetime, timedelta
import requests
from os.path import join, exists
from os import makedirs
from chessapp.util.pgn import split_pgn, pgn_mainline_to_moves
from chess.pgn import Game
from time import sleep
from chessapp.util.fen import reduce_fen


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


class TimeControl(Enum):
    BULLET = "bullet"
    BLITZ = "blitz"
    RAPID = "rapid"
    CLASSICAL = "classical"
    CORRESPONDENCE = "correspondence"

    def from_time_string(time_control: str) -> "TimeControl":
        seconds: int = int(time_control.split("+")[0])
        if seconds < 180:
            return TimeControl.BULLET
        if seconds < 600:
            return TimeControl.BLITZ
        if seconds < 1800:
            return TimeControl.RAPID
        if seconds < 10800:
            return TimeControl.CLASSICAL
        return TimeControl.CORRESPONDENCE


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
    link: str = ""
    black_elo: int = 0
    white_elo: int = 0
    id: str = ""
    starting_position: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def get_timecontrol(self) -> TimeControl:
        return TimeControl.from_time_string(self.time_control)

    def convert_from_game(game: Game) -> "GameDocument":
        game_document: GameDocument = GameDocument(pgn_mainline_to_moves(game))
        if "Site" in game.headers:
            game_document.site = game.headers["Site"]
        if "Link" in game.headers:
            game_document.link = game.headers["Link"]
        if "UTCDate" in game.headers and "UTCTime" in game.headers:
            # iso 8601 datetime format
            game_document.when = game.headers["UTCDate"].replace(".", "-") + \
                "T" + game.headers["UTCTime"]
        if "White" in game.headers:
            game_document.white = game.headers["White"]
        if "Black" in game.headers:
            game_document.black = game.headers["Black"]
        if "Result" in game.headers:
            game_document.result = game.headers["Result"]
        if "Termination" in game.headers:
            game_document.termination = game.headers["Termination"]
        if "TimeControl" in game.headers:
            game_document.time_control = game.headers["TimeControl"]
        if "Variant" in game.headers:
            game_document.variant = game.headers["Variant"]
        if "BlackElo" in game.headers and game.headers["BlackElo"] != "?":
            game_document.black_elo = int(game.headers["BlackElo"])
        if "WhiteElo" in game.headers and game.headers["WhiteElo"] != "?":
            game_document.white_elo = int(game.headers["WhiteElo"])
        if "FEN" in game.headers:
            game_document.starting_position = game.headers["FEN"]
        return game_document


@dataclass
class IndexEntry():
    fen: str
    reduced_fen: str
    game_id: str
    moves_index: int


class ChessWebsiteDatabase(Database):
    def __init__(self, username: str, games_uri: str, user_uri: str, user_joined_keyword: str, db_filename_prefix: str):
        super().__init__(db_filename_prefix + "_" + username)
        self.username: str = username
        self.last_update: datetime = datetime.fromtimestamp(0)
        self.games_uri: str = games_uri
        self.user_uri: str = user_uri
        self.short_update_interval_days: int = 60
        self.long_update_interval_days: int = 365
        self.games_table: Table = None
        self.config_table: Table = None
        self.index_table: Table = None
        self.user_joined_keyword: str = user_joined_keyword
        self.update_time_delta_hours: int = 1
        self.custom_user_agent: str = None
        self.created_at_divisor: int = 1

    def search_index(self, query: Query) -> list[IndexEntry]:
        indices: list[IndexEntry] = [IndexEntry(
            **doc) for doc in self.index_table.search(query)]
        game_ids: list[str] = [
            index_entry.game_id for index_entry in indices]
        return [
            GameDocument(**doc) for doc in self.games_table.search(where("id").one_of(game_ids))]

    def search_by_fen(self, fen: str) -> list[GameDocument]:
        return self.search_index(where("fen") == fen)

    def search_by_reduced_fen(self, fen: str) -> list[GameDocument]:
        return self.search_index(where("reduced_fen") == reduce_fen(fen))

    def search_by_datetime(self, start: datetime, end: datetime) -> list[GameDocument]:
        return [
            GameDocument(**doc) for doc in self.games_table.search(
                (where("when") >= start.isoformat()
                 ) & (where("when") < end.isoformat())
            )
        ]

    def search(self, predicate) -> Generator[GameDocument, None, None]:
        for game in self.games_table.all():
            game_document = GameDocument(**game)
            if predicate(game_document):
                yield game_document

    def get_user_data(self) -> dict:
        headers = dict()
        if self.custom_user_agent:
            headers["User-Agent"] = self.custom_user_agent
        response = requests.get(self.user_uri + self.username, headers=headers)
        if not response.ok:
            raise Exception(
                "unable to fetch data from lichess.org for reason: " + response.reason)
        return response.json()

    def init_db(self) -> None:
        self.games_table = self.db.table("games")
        self.config_table = self.db.table("config")
        self.index_table = self.db.table("index")
        for item in self.config_table:
            if item["name"] == "last_update":
                self.last_update = datetime.fromisoformat(item["value"])

    def index_documents(self, game_docs: list[Mapping]) -> None:
        board: Board = Board()
        new_index_entry_docs: list[Mapping] = []
        for doc in game_docs:
            game: GameDocument = GameDocument(**doc)
            board.reset()
            # set the board to the starting position using the position part of the fen
            # otherthise this function will raise an error
            board.set_board_fen(game.starting_position.split(" ")[0])
            moves_index: int = 0
            for move in game.moves:
                try:
                    board.push_san(move)
                except:
                    raise Exception("cannot interpret move " + str(move) +
                                    " with moves_index " + str(moves_index) + " in game " + game.id)
                fen: str = board.fen()
                reduced_fen: str = reduce_fen(fen)
                new_index_entry_docs.append(IndexEntry(
                    fen, reduced_fen, game.id, moves_index).__dict__)
                moves_index += 1
        self.index_table.insert_multiple(new_index_entry_docs)

    def init_last_update_datetime(self) -> None:
        data = self.get_user_data()
        if not data[self.user_joined_keyword]:
            return
        createdAt: datetime = datetime.fromtimestamp(
            float(data[self.user_joined_keyword]) / self.created_at_divisor)
        if self.last_update < createdAt:
            self.set_last_update(createdAt)

    def set_last_update(self, last_update: datetime) -> None:
        self.last_update = last_update
        self.config_table.upsert(
            {"name": "last_update", "value": self.last_update.isoformat()}, Query().name == "last_update")

    def on_open(self) -> None:
        self.init_db()
        self.init_last_update_datetime()

    def needs_updates(self) -> bool:
        return self.last_update + timedelta(hours=self.update_time_delta_hours) < datetime.now()

    def consume_games(self, pgn: str) -> None:
        games: list[Game] = split_pgn(pgn)
        game_docs: list[Mapping] = []
        game_document_ids: list[str] = []
        for doc in games:
            game_document = GameDocument.convert_from_game(doc)
            self.set_id_for_game_document(game_document)
            if not game_document.id:
                raise Exception("id is not set")
            game_document_ids.append(game_document.id)
            game_docs.append(game_document.__dict__)
        # insert all documents from game_document_mapping that are not already in the database
        docs = [
            doc for doc in game_docs if not doc["id"] in [
                doc["id"] for doc in self.games_table.search(
                    where("id").one_of(game_document_ids)
                )
            ]
        ]
        self.index_documents(docs)
        self.games_table.insert_multiple(docs)

    def update(self) -> int:
        raise NotImplementedError()

    def update_complete(self) -> None:
        raise NotImplementedError()

    def set_id_for_game_document(self, game_document: GameDocument) -> None:
        raise NotImplementedError()


class LichessDatabase(ChessWebsiteDatabase):

    def __init__(self, username: str):
        super().__init__(username, "https://lichess.org/api/games/user/",
                         "https://lichess.org/api/user/", "createdAt", "lichess")
        self.created_at_divisor = 1000

    def update(self) -> int:
        until_datetime: datetime = datetime.now()
        difference = until_datetime - self.last_update
        if difference.days > self.short_update_interval_days:
            target_delta_days: int = self.short_update_interval_days
            if difference.days > self.long_update_interval_days:
                target_delta_days = self.long_update_interval_days
            delta: timedelta = timedelta(days=target_delta_days)
            until_datetime = self.last_update + delta
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

    def set_id_for_game_document(self, game_document: GameDocument) -> None:
        if not game_document.site:
            raise Exception("site is not set")
        game_document.id = game_document.site[len("https://lichess.org/"):]


class ChessDotComDatabase(ChessWebsiteDatabase):

    def __init__(self, username: str):
        super().__init__(username, "https://api.chess.com/pub/player/",
                         "https://api.chess.com/pub/player/", "joined", "chess_dot_com")
        self.custom_user_agent = "chessapp"

    def download_month(self, year: int, month: int) -> int:
        response = requests.get(
            f"{self.games_uri}{self.username}/games/{year}/{month}/pgn",
            headers={"User-Agent": self.custom_user_agent}
        )
        if response.ok:
            self.consume_games(response.text)
        return response.status_code

    def update(self) -> int:
        until_now: datetime = datetime.now()
        target_month: int = until_now.month
        target_year: int = until_now.year
        skip_to_next_month: bool = False
        if until_now.year != self.last_update.year or until_now.month != self.last_update.month:
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
                    skip_to_year += 1
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

    def set_id_for_game_document(self, game_document: GameDocument) -> None:
        if not game_document.link:
            raise Exception("link is not set")
        game_document.id = game_document.link[len(
            "https://www.chess.com/game/live/"):]


def update_table(table: Table, documents: list[Mapping], id_field: str = "id"):
    """ This method updates the table such that. The id_field is used to identify the
    documents. If a document with the same id_field value exists in the table, it is updated, otherwise it is inserted.
    All documents have to contain the id_field. Otherwise the documents cannot be identified.


    Args:
        table (Table): target table
        documents (list[Mapping]): documents to update or insert
        id_field (str, optional): id_field used to identify identical documents

    Raises:
        ValueError: if a document does not contain the id_field
    """
    if len(documents) == 0:
        return

    # Get the IDs of all documents in the index table
    existing_ids = [doc[id_field] for doc in table.all()]

    # Split documents into existing and new entries
    existing_entries = [
        doc for doc in documents if doc[id_field] in existing_ids]
    new_entries = [
        doc for doc in documents if doc[id_field] not in existing_ids]

    # Update existing entries and insert new entries
    for doc in existing_entries:
        if not id_field in doc:
            raise ValueError("id_field " + id_field +
                             " not found in document " + str(doc))
        table.update(doc, cond=where(id_field) == doc[id_field])
    table.insert_multiple(new_entries)
