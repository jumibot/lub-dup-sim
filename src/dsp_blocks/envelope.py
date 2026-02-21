from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Tuple


class IEnvelopeLUT(Protocol):
    """LUT inmutable (asset). No mantiene fase/estado."""

    def length(self) -> int: ...
    def value_at_index(self, i: int) -> float: ...


@dataclass(frozen=True)
class EnvelopeLUT(IEnvelopeLUT):
    table: Tuple[float, ...]

    def length(self) -> int:
        return len(self.table)

    def value_at_index(self, i: int) -> float:
        return self.table[i]
