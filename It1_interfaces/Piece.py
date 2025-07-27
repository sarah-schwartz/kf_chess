import PhysicsFactory
from Board import Board
from Command import Command
from State import State
from typing import Optional
import cv2

class Piece:
    nextCode = 0
    def __init__(self, piece_id: str, init_state: State):
        self._id = piece_id
        self._uniqueNumber = Piece.nextCode
        Piece.nextCode += 1
        self._state = init_state
        self._current_cmd: Optional[Command] = None
        self._has_moved = False  # מעקב אחר האם הכלי זז כבר
        count = 0


    def on_command(self, cmd: Command, now_ms: int):
        # הוסרה בדיקת is_command_possible כי זה נעשה ב-Game
        self._current_cmd = cmd
        self._state = self._state.process_command(cmd, now_ms)
        # סימון שהכלי זז
        if cmd.type == "move":
            self._has_moved = True

    def is_command_possible(self, cmd: Command) -> bool:
        if cmd.type == "move":
            src = self._state._physics.start_cell
            dst = self._state._physics.board.algebraic_to_cell(cmd.params[1])
            # העברת מידע על האם הכלי זז כבר למחלקת Moves
            legal = self._state._moves.get_moves(*src, self._has_moved)
            if dst not in legal:
                return False

        return cmd is not None and cmd.type in self._state.transitions

    def reset(self, start_ms: int):
        if self._current_cmd:
            self._state.reset(self._current_cmd)

    def update(self, now_ms: int):
        self._state = self._state.update(now_ms)
        if self._state._physics.finished:
            next_state =  next(iter(self._state.transitions.keys()))
            new_cell = self._state._physics.get_pos_in_cell()
            cmd = Command(now_ms, self._id, next_state, [new_cell, new_cell])
            self.on_command(cmd, now_ms)

    def draw_on_board(self, board: Board, now_ms: int):
        pos = self._state._physics.get_pos()
        img = self._state._graphics.get_img().img
        if img is not None:
            h, w = img.shape[:2]
            x, y = int(pos[0]), int(pos[1])

            board_img = board.img.img

            # התאמה אם חורג מגבולות
            h = min(h, board_img.shape[0] - y)
            w = min(w, board_img.shape[1] - x)

            if h > 0 and w > 0:
                piece_img = img[:h, :w]
                base = board_img[y:y + h, x:x + w]

                # התאמת ערוצים
                target_channels = base.shape[2]
                piece_img = self._match_channels(piece_img, target_channels)

                board_img[y:y + h, x:x + w] = self._blend(base, piece_img)

    def _blend(self, base, overlay):
        alpha = 0.8  # Simple fixed alpha
        return cv2.addWeighted(overlay, alpha, base, 1 - alpha, 0)

    def _match_channels(self, img, target_channels=3):
        """Convert image to target_channels (3=BGR, 4=BGRA)."""
        if img.shape[2] == target_channels:
            return img
        if target_channels == 3 and img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        if target_channels == 4 and img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        return img

    def get_id(self):
        return self._id

    def get_unique(self):
        return self._uniqueNumber

    def get_command(self):
        return self._state.get_command()

    def clone_to(self, cell: tuple[int, int], physics_factory: PhysicsFactory) -> "Piece":
        """
        Clone this piece to a new piece at a different cell.
        Graphics is copied, physics is recreated (new cell), moves are shared.
        """
        # מעתיק את הגרפיקה
        graphics_copy = self._state._graphics.copy()

        # יוצר פיזיקס חדש – משתמש בנתונים שכבר קיימים באובייקט
        state_name = self._state._physics.__class__.__name__.replace("Physics", "").lower()
        speed = getattr(self._state._physics, "speed", 1.0)
        # אין לנו cfg, אז נבנה מינימלי
        cfg = {"physics": {"speed_m_per_sec": speed}}

        new_physics = physics_factory.create(state_name, cell, cfg)

        # יוצר סטייט חדש
        new_state = State(self._state._moves, graphics_copy, new_physics)

        # מעתיק את הטרנזישנים הקיימים
        for event, target in self._state.transitions.items():
            new_state.set_transition(event, target)

        new_piece = Piece(self._id, new_state)
        new_piece._has_moved = self._has_moved  # העתקת מצב התנועה
        return new_piece