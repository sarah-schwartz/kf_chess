import csv
import pathlib
import time
import queue
import cv2
from typing import Dict, Tuple, Optional
import threading

from Board import Board
from Command import Command
from Piece import Piece
from PieceFactory import PieceFactory
from InputHandler import InputHandler
from GameRenderer import GameRenderer
from CommandHandler import CommandHandler

class Game:
    def __init__(self, board: Board, pieces_root: pathlib.Path, placement_csv: pathlib.Path):
        self.board = board
        self.user_input_queue = queue.Queue()
        self.start_time = time.monotonic()
        self.piece_factory = PieceFactory(board, pieces_root)
        self.pieces: Dict[str, Piece] = {}
        self.pos_to_piece: Dict[Tuple[int, int], Piece] = {}
        self._load_pieces_from_csv(placement_csv)
        
        self._running = True
        self.input_handler = InputHandler(self.user_input_queue, self.board, self)
        self.renderer = GameRenderer(self.board)
        self.command_handler = CommandHandler(self.board, self.pos_to_piece)


    def _load_pieces_from_csv(self, csv_path: pathlib.Path):
        with csv_path.open() as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                for col_idx, code in enumerate(row):
                    code = code.strip()
                    if not code:
                        continue
                    cell = (row_idx, col_idx)
                    piece = self.piece_factory.create_piece(code, cell)
                    self.pieces[piece.get_unique()] = piece
                    self.pos_to_piece[cell] = piece

    def game_time_ms(self) -> int:
        return int((time.monotonic() - self.start_time) * 1000)

    def run(self):
        self.input_handler.start_keyboard_thread()

        start_ms = self.game_time_ms()
        for piece in self.pieces.values():
            piece.reset(start_ms)

        while self._running and not self._is_win():
            now = self.game_time_ms()

            for piece in self.pieces.values():
                piece.update(now)

            self._update_position_mapping()

            while not self.user_input_queue.empty():
                cmd = self.user_input_queue.get()
                self.command_handler.handle_command(cmd, now)

            # Drawing
            current_board_img = self.renderer.draw(
                self.pieces,
                self.input_handler.focus_cell,
                self.input_handler.focus_cell2,
                self.input_handler._selected_source,
                self.input_handler._selected_source2,
                now
            )
            self.renderer.show(current_board_img)

        self._announce_win()
        self._running = False
        self.renderer.destroy_windows()

    def _update_position_mapping(self):
        self.pos_to_piece.clear()
        to_remove = set()

        for piece in list(self.pieces.values()):
            x, y = map(int, piece._state._physics.get_pos())
            cell_x = x // self.board.cell_W_pix
            cell_y = y // self.board.cell_H_pix
            pos = (cell_y, cell_x)

            if pos in self.pos_to_piece:
                opponent = self.pos_to_piece[pos]
                if (not opponent._state._current_command or
                    opponent._state._current_command.type in ["idle", "long_rest", "short_rest"] or
                        (piece._state._current_command and
                         piece._state._current_command.type not in ["idle", "long_rest", "short_rest"] and
                        opponent._state._physics.start_time > piece._state._physics.start_time)):
                    self.pos_to_piece[pos] = piece
                    to_remove.add(opponent.get_unique())
                else:
                    to_remove.add(piece.get_unique())
            else:
                self.pos_to_piece[pos] = piece

        for k in to_remove:
            self.pieces.pop(k, None)

    def _is_win(self) -> bool:
        kings = [p for p in self.pieces.values() if p.get_id().lower().startswith("k")]
        return len(kings) <= 1

    def _announce_win(self):
        kings = [p for p in self.pieces.values() if p.get_id().lower().startswith("k")]
        if not kings:
             print("Draw.")
        elif len(kings) == 1:
            winner_color = "White" if kings[0].get_id()[1] == 'W' else "Black"
            print(f"{winner_color} wins!")
        else: # Should not happen if _is_win is correct
            print("Game over.")
