from dataclasses import dataclass
import copy
from typing import Tuple

from img import Img

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    cell_H_m: int
    cell_W_m: int
    W_cells: int
    H_cells: int
    img: Img

    def clone(self) -> "Board":
        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            cell_H_m=self.cell_H_m,
            cell_W_m=self.cell_W_m,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=copy.deepcopy(self.img)
        )
    def cell_to_world(self, cell: tuple[int, int]) -> tuple[int, int]:
        row, col = cell
        x = col * self.cell_W_pix
        y = row * self.cell_H_pix
        return x, y
    def algebraic_to_cell(self, notation: str) -> Tuple[int, int]:
        """
        Converts algebraic notation (e.g., "a1") to board coordinates.
        Example: "a1" -> (7, 0) if (0,0) is top-left
        """
        if len(notation) != 2:
            raise ValueError("Invalid algebraic notation format")
        
        col_char = notation[0].lower()
        if col_char < 'a' or col_char > 'h':
            raise ValueError("Invalid column in algebraic notation")
            
        try:
            row_num = int(notation[1])
            if row_num < 1 or row_num > 8:
                raise ValueError("Invalid row in algebraic notation")
        except ValueError:
            raise ValueError("Invalid row number in algebraic notation")
            
        col = ord(col_char) - ord('a')
        row = 8 - row_num  # Assuming board is 8x8
        return row, col
    def world_to_cell(self, pos: Tuple[float, float]) -> Tuple[int, int]: # Convert pixel coordinates to cell coordinates
        x, y = pos
        col = int(x // self.cell_W_pix)
        row = int(y // self.cell_H_pix)
        return row, col

    def cell_to_algebraic(self, cell: Tuple[int, int]) -> str:
        row, col = cell
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError("Cell coordinates out of bounds")
        col_letter = chr(ord('a') + col)
        row_number = str(8 - row)  # assuming 8x8 board
        return f"{col_letter}{row_number}"
    
    def cell_to_pix(self, cell: Tuple[int, int]) -> Tuple[int, int]:
        """Convert cell coordinates to pixel coordinates"""
        col, row = cell  # Treating cell as (col, row) to match test expectations
        x = col * self.cell_W_pix
        y = row * self.cell_H_pix
        return x, y
        
    def pix_to_cell(self, pix: Tuple[int, int]) -> Tuple[int, int]:
        """Convert pixel coordinates to cell coordinates"""
        x, y = pix  # Standard (x, y) pixel format
        col = x // self.cell_W_pix
        row = y // self.cell_H_pix
        return col, row  # Return (col, row) to match test expectations
        
    def is_valid_cell(self, cell: Tuple[int, int]) -> bool:
        """Check if cell coordinates are within board bounds"""
        row, col = cell
        return 0 <= row < self.H_cells and 0 <= col < self.W_cells

