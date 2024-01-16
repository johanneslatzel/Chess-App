from pathlib import Path
from os.path import join
from chessapp.configuration import ROOT_DIR


def get_audio_folder() -> Path:
    return join(get_assets_folder(), "audio")


def get_assets_folder() -> Path:
    return join(ROOT_DIR, "assets")


def get_images_folder() -> Path:
    return join(get_assets_folder(), "img")


def get_chess_pieces_folder() -> Path:
    return join(get_images_folder(), "chessboard", "pieces", "default")


def get_data_folder() -> Path:
    return join(ROOT_DIR, "data")


def get_openings_folder() -> Path:
    return join(get_data_folder(), "openings")


def get_opening_tree_folder() -> Path:
    return join(get_data_folder(), "opening_tree")

def get_stockfish_exe() -> Path:
    return join(ROOT_DIR, "engine", "stockfish", "16", "stockfish-windows-x86-64-avx2.exe")

def get_puzzles_folder() -> Path:
    return join(get_data_folder(), "puzzles")