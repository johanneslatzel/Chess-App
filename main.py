from chessapp.chessapp import ChessApp
from chessapp.model.chesstree import ChessTree
import sys
from chessapp.util.paths import get_openings_folder
from chessapp.view.pieces import load_pieces
from qt_material import apply_stylesheet

tree = ChessTree(get_openings_folder())
tree.load()
qtapp = ChessApp(tree, sys.argv)
qtapp.aboutToQuit.connect(qtapp.close)
apply_stylesheet(qtapp, theme='dark_teal.xml')
load_pieces()
qtapp.exec_()
