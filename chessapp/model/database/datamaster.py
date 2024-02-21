from typing import Generator
from chessapp.model.database.database import Database, ChessWebsiteDatabase, LichessDatabase, ChessDotComDatabase
from tinydb.table import Table
from concurrent.futures import ThreadPoolExecutor


s_max_threadpool_workers: int = 4


class DatamasterConfigDatabase(Database):

    def __init__(self) -> None:
        super().__init__("datamaster_config")
        self.lichess_databases: Table = None
        self.chess_dot_com_databases: Table = None

    def on_open(self) -> None:
        self.lichess_databases = self.db.table("lichess_databases")
        self.chess_dot_com_databases = self.db.table("chess_dot_com_databases")

    def all_lichess_databases(self) -> Generator[str, None, None]:
        for entry in self.lichess_databases.all():
            if entry["username"]:
                yield entry["username"]

    def all_chess_com_databases(self) -> Generator[str, None, None]:
        for entry in self.chess_dot_com_databases.all():
            if entry["username"]:
                yield entry["username"]


class Datamaster():

    def __init__(self):
        self.config_db = DatamasterConfigDatabase()
        self.game_databases: list[ChessWebsiteDatabase] = []
        self.threadpool: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=s_max_threadpool_workers)

    def add_lichess_database(self, username: str) -> None:
        self.config_db.lichess_databases.insert({"username": username})
        lichess_db: LichessDatabase = LichessDatabase(username)
        lichess_db.open()
        self.game_databases.append(lichess_db)

    def add_chess_com_database(self, username: str) -> None:
        self.config_db.chess_dot_com_databases.insert({"username": username})
        lichess_db: ChessDotComDatabase = ChessDotComDatabase(username)
        lichess_db.open()
        self.game_databases.append(lichess_db)

    def update_game_databases(self) -> None:
        for db in self.game_databases:
            self.threadpool.submit(db.update_complete)

    def open(self) -> None:
        self.config_db.open()
        for username in self.config_db.all_lichess_databases():
            lichess_db: LichessDatabase = LichessDatabase(username)
            lichess_db.open()
            self.game_databases.append(lichess_db)

    def close(self) -> None:
        self.config_db.close()
