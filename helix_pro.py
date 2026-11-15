# HELIX-Pro - Spiral memory with full-record storage and integrity reporting
# Part of the Kapildhinwa2010-dev Toolkit.

"""HELIX-Pro - spiral-addressed memory with integrity reporting.

Lineage: reserv.dean-part-2 (helix.py). Records are written across
consecutive spiral cells (wrapping at the edge) and rows carry XOR
parity, so odd-parity corruption is detectable by verify().

Pro additions over HELIX-Lib: read_record() round-trip and
integrity_report(), an honest health summary (parity status, usage,
stored keys). Parity still cannot locate or repair corruption - that is
a documented limit, not a feature.
"""

from __future__ import annotations

import numpy as np

__all__ = ["spiral_coordinates", "HelixMemory"]


def spiral_coordinates(size: int):
    """Clockwise spiral walk of a size x size grid from the center."""
    if size < 1:
        raise ValueError("size must be >= 1")
    coords = []
    x = y = size // 2
    coords.append((x, y))
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # right, down, left, up
    step = 1
    while len(coords) < size * size:
        for d_index, (dx, dy) in enumerate(directions):
            for _ in range(step):
                if len(coords) >= size * size:
                    return coords
                x += dx
                y += dy
                if 0 <= x < size and 0 <= y < size:
                    coords.append((x, y))
            if d_index % 2 == 1:
                step += 1
    return coords


def _xor_parity(block: np.ndarray) -> int:
    parity = 0
    for value in block:
        parity ^= int(value)
    return parity


class HelixMemory:
    """Byte arena with spiral addressing, XOR parity rows and reporting."""

    def __init__(self, size: int = 8, record_size: int = 4) -> None:
        if size < 1 or record_size < 1:
            raise ValueError("size and record_size must be >= 1")
        self.size = int(size)
        self.record_size = int(record_size)
        self.coords = spiral_coordinates(size)
        self.arena = np.zeros((size, size), dtype=np.uint8)
        self.parity = np.zeros(size, dtype=np.uint8)
        self._used: set = set()

    def address(self, key: str) -> int:
        """Deterministic spiral index for a string key."""
        digest = sum(ord(c) for c in key)
        return digest % len(self.coords)

    def write(self, key: str, record: bytes) -> None:
        """Write record bytes across consecutive spiral cells (with wrap)."""
        record = bytes(record)
        if len(record) != self.record_size:
            raise ValueError("record must be exactly {} bytes".format(self.record_size))
        index = self.address(key)
        touched_rows = set()
        for offset, byte in enumerate(record):
            x, y = self.coords[(index + offset) % len(self.coords)]
            self.arena[x, y] = byte
            touched_rows.add(x)
        for row in touched_rows:
            self.parity[row] = _xor_parity(self.arena[row])
        self._used.add(key)

    def read_record(self, key: str) -> bytes:
        """Read back the record bytes written at this key."""
        index = self.address(key)
        out = []
        for offset in range(self.record_size):
            x, y = self.coords[(index + offset) % len(self.coords)]
            out.append(int(self.arena[x, y]))
        return bytes(out)

    def read_cell(self, key: str) -> int:
        """First cell byte of the record (kept for compatibility)."""
        index = self.address(key)
        x, y = self.coords[index]
        return int(self.arena[x, y])

    def verify(self) -> bool:
        """True when every row matches its XOR parity.

        Detects odd numbers of flipped bits per row; even flips cancel out
        and pass. Parity does not locate the corrupted cell.
        """
    # (docstring above belongs to verify)
        for row in range(self.size):
            if _xor_parity(self.arena[row]) != int(self.parity[row]):
                return False
        return True

    def corrupt(self, key: str) -> None:
        """Flip one byte; parity is left stale so verify() detects it."""
        index = self.address(key)
        x, y = self.coords[index]
        self.arena[x, y] ^= 0xFF

    def integrity_report(self) -> dict:
        """Honest health summary: parity status, usage, stored keys.

        corrupt_rows counts rows whose parity no longer matches. verify()
        cannot say which cell is bad, and neither can this report.
        """
        corrupt_rows = [
            row for row in range(self.size)
            if _xor_parity(self.arena[row]) != int(self.parity[row])
        ]
        return {
            "size": self.size,
            "record_size": self.record_size,
            "stored_keys": len(self._used),
            "usage": self.usage(),
            "parity_ok": not corrupt_rows,
            "corrupt_rows": corrupt_rows,
        }

    def usage(self) -> float:
        return len(self._used) / (self.size * self.size)

    def __len__(self) -> int:
        return len(self._used)
