from chessapp.chessapp import ChessApp
from chessapp.model.chesstree import ChessTree
import sys
from chessapp.util.paths import get_openings_folder

tree = ChessTree(get_openings_folder())
tree.load()
qtapp = ChessApp(tree, sys.argv)
qtapp.aboutToQuit.connect(qtapp.close)
qtapp.exec_()
