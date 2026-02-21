from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from .bus import IAudioBusFixed
from .stems import StemId
from ..dsp_blocks.voice import IStemVoice


class IDspStemGenerator(ABC):
    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def render(self, bus: IAudioBusFixed, n_frames: int) -> None: ...


class Dsp(IDspStemGenerator):
    """Dsp = genera stems fijos. NO mezcla. NO post-procesa."""

    def __init__(self, voices: Sequence[IStemVoice]) -> None:
        self._voices: List[IStemVoice] = list(voices)
        self._validate_unique_stems()

    def _validate_unique_stems(self) -> None:
        stems = [v.stem_id() for v in self._voices]
        if len(set(stems)) != len(stems):
            raise ValueError("Hay stems duplicados: se esperaba 1 voice por stem.")

    def reset(self) -> None:
        for v in self._voices:
            v.reset()

    def render(self, bus: IAudioBusFixed, n_frames: int) -> None:
        bus.clear_all(n_frames)
        for v in self._voices:
            out_buf = bus.buffer(v.stem_id())
            v.render(out_buf, n_frames)
