"""Small, explicit 2-D layout algebra used by the formal-layout lab."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Layout2D:
    rows: int
    cols: int
    forward: callable
    name: str

    @property
    def size(self):
        return self.rows * self.cols

    def offset(self, row: int, col: int) -> int:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError((row, col))
        value = int(self.forward(row, col))
        if not 0 <= value < self.size:
            raise ValueError(f"layout offset {value} outside [0, {self.size})")
        return value

    def offsets(self):
        return [self.offset(row, col) for row in range(self.rows) for col in range(self.cols)]

    def inverse(self):
        inverse = {}
        for row in range(self.rows):
            for col in range(self.cols):
                value = self.offset(row, col)
                if value in inverse:
                    raise ValueError(f"alias at offset {value}: {inverse[value]} and {(row, col)}")
                inverse[value] = (row, col)
        if set(inverse) != set(range(self.size)):
            missing = sorted(set(range(self.size)) - set(inverse))
            raise ValueError(f"layout is not onto; missing offsets {missing[:8]}")
        return inverse

    def check_bijection(self):
        self.inverse()
        return {"name": self.name, "shape": [self.rows, self.cols], "size": self.size, "bijection": True}


def row_major(rows, cols):
    return Layout2D(rows, cols, lambda row, col: row * cols + col, "row-major")


def blocked_2d(rows, cols, tile_rows, tile_cols):
    if rows % tile_rows or cols % tile_cols:
        raise ValueError("blocked layout requires tile-divisible shape")
    tiles_per_row = cols // tile_cols

    def forward(row, col):
        tile = (row // tile_rows) * tiles_per_row + (col // tile_cols)
        local = (row % tile_rows) * tile_cols + (col % tile_cols)
        return tile * tile_rows * tile_cols + local

    return Layout2D(rows, cols, forward, f"blocked-{tile_rows}x{tile_cols}")


def xor_swizzled_2d(rows, cols, tile_rows, tile_cols):
    """XOR low tile-column bits with the local row; XOR is self-inverse."""
    base = blocked_2d(rows, cols, tile_rows, tile_cols)

    def forward(row, col):
        local_row, local_col = row % tile_rows, col % tile_cols
        swizzled_col = local_col ^ (local_row & (tile_cols - 1))
        tile_base = base.offset(row - local_row, col - local_col)
        return tile_base + local_row * tile_cols + swizzled_col

    return Layout2D(rows, cols, forward, f"xor-swizzled-{tile_rows}x{tile_cols}")
