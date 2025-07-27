import queue
import threading
import time
from typing import Optional, Tuple

import keyboard

from Board import Board
from Command import Command


class InputHandler:
    def __init__(self, user_input_queue: queue.Queue, board: Board, game):
        self.user_input_queue = user_input_queue
        self.board = board
        self.game = game  # To access pos_to_piece, game_time_ms, and _running
        self._lock = threading.Lock()

        # --- User 1 state ---
        self.focus_cell = (0, 0)
        self._selection_mode = "source"
        self._selected_source: Optional[Tuple[int, int]] = None

        # --- User 2 state ---
        self.focus_cell2 = (self.board.H_cells - 1, 0)
        self._selection_mode2 = "source"
        self._selected_source2: Optional[Tuple[int, int]] = None

    def start_keyboard_thread(self):
        threading.Thread(target=self._keyboard_loop, daemon=True).start()

    def _keyboard_loop(self):
        while self.game._running:
            time.sleep(0.05)
            with self._lock:
                self._handle_user1_input()
                self._handle_user2_input()

    def _handle_user1_input(self):
        if keyboard.is_pressed('esc'):
            self.game._running = False
            return

        dy, dx = 0, 0
        if keyboard.is_pressed('left'): dx = -1
        elif keyboard.is_pressed('right'): dx = 1
        if keyboard.is_pressed('up'): dy = -1
        elif keyboard.is_pressed('down'): dy = 1

        if dx != 0 or dy != 0:
            h, w = self.board.H_cells, self.board.W_cells
            y, x = self.focus_cell
            self.focus_cell = ((y + dy) % h, (x + dx) % w)
            time.sleep(0.2)

        if keyboard.is_pressed('enter'):
            self._on_enter_pressed()
            time.sleep(0.2)

    def _handle_user2_input(self):
        dy2, dx2 = 0, 0
        if keyboard.is_pressed('a'): dx2 = -1
        elif keyboard.is_pressed('d'): dx2 = 1
        if keyboard.is_pressed('w'): dy2 = -1
        elif keyboard.is_pressed('s'): dy2 = 1

        if dx2 != 0 or dy2 != 0:
            h, w = self.board.H_cells, self.board.W_cells
            y2, x2 = self.focus_cell2
            self.focus_cell2 = ((y2 + dy2) % h, (x2 + dx2) % w)
            time.sleep(0.2)

        if keyboard.is_pressed('space'):
            self._on_space_pressed()
            time.sleep(0.2)

    def _on_enter_pressed(self):
        if self._selection_mode == "source":
            if self.focus_cell in self.game.pos_to_piece:
                piece = self.game.pos_to_piece[self.focus_cell]
                if piece.get_id()[1] == 'B':
                    src_alg = self.board.cell_to_algebraic(self.focus_cell)
                    print(f"User 1 source selected at {self.focus_cell} -> {src_alg}")
                    self._selected_source = self.focus_cell
                    self._selection_mode = "dest"
                else:
                    print("User 1 cannot select this piece.")
        elif self._selection_mode == "dest":
            if self._selected_source is None:
                self._reset_selection()
                return

            src_cell = self._selected_source
            dst_cell = self.focus_cell
            src_alg = self.board.cell_to_algebraic(src_cell)
            dst_alg = self.board.cell_to_algebraic(dst_cell)
            print(f"User 1 destination selected at {dst_cell} -> {dst_alg}")

            piece = self.game.pos_to_piece.get(src_cell)
            if piece:
                cmd = Command(
                    timestamp=self.game.game_time_ms(),
                    piece_id=piece.get_unique(),
                    type="move",
                    params=[src_alg, dst_alg]
                )
                self.user_input_queue.put(cmd)
            self._reset_selection()

    def _on_space_pressed(self):
        if self._selection_mode2 == "source":
            if self.focus_cell2 in self.game.pos_to_piece:
                piece = self.game.pos_to_piece[self.focus_cell2]
                if piece.get_id()[1] == 'W':
                    src_alg = self.board.cell_to_algebraic(self.focus_cell2)
                    print(f"User 2 source selected at {self.focus_cell2} -> {src_alg}")
                    self._selected_source2 = self.focus_cell2
                    self._selection_mode2 = "dest"
                else:
                    print("User 2 cannot select this piece.")
        elif self._selection_mode2 == "dest":
            if self._selected_source2 is None:
                self._reset_selection2()
                return

            src_cell = self._selected_source2
            dst_cell = self.focus_cell2
            src_alg = self.board.cell_to_algebraic(src_cell)
            dst_alg = self.board.cell_to_algebraic(dst_cell)
            print(f"User 2 destination selected at {dst_cell} -> {dst_alg}")

            piece = self.game.pos_to_piece.get(src_cell)
            if piece:
                cmd = Command(
                    timestamp=self.game.game_time_ms(),
                    piece_id=piece.get_unique(),
                    type="move",
                    params=[src_alg, dst_alg]
                )
                self.user_input_queue.put(cmd)
            self._reset_selection2()

    def _reset_selection(self):
        self._selection_mode = "source"
        self._selected_source = None

    def _reset_selection2(self):
        self._selection_mode2 = "source"
        self._selected_source2 = None
