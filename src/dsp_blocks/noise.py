from __future__ import annotations

from typing import Protocol

from ..core.types import AudioBlock


class INoiseSource(Protocol):
    """Fuente de ruido. Implementación decide white/pink/band-limited/etc."""

    def reset(self, seed: int) -> None: ...
    def next_block(self, out: AudioBlock, n_frames: int) -> None: ...
