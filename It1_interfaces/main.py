import csv, pathlib, time, queue, threading, cv2
from typing import List, Dict, Tuple
from Board import Board
from pathlib import Path
from Board import Board
from Game import Game
from img import Img
if __name__ == "__main__":
    # Initialize paths
    base_path = Path(__file__).resolve().parent
    pieces_root = base_path.parent / "PIECES"
    placement_csv = base_path / "board.csv"
    image_path = base_path.parent / "board.png"  # עולה תיקייה אחת למעלה ומוסיף board.png

    board = Board(
        cell_H_pix=80,
        cell_W_pix=80,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        # img=Img().read("../board.png", size=(640, 640))
        img=Img().read(str(image_path), size=(640, 640))
    )
    # paths
    # base_path = Path(__file__).resolve().parent
    # pieces_root = base_path.parent / "PIECES"
    # placement_csv = base_path / "board.csv"

    # board = Board(
    #     cell_H_pix=80,
    #     cell_W_pix=80,
    #     cell_H_m=1,
    #     cell_W_m=1,
    #     W_cells=8,
    #     H_cells=8,
    #     img=Img().read(str(base_path.parent / "board.png"), size=(640, 640))
    # )

    game = Game(board, pieces_root, placement_csv)
    game.run()

