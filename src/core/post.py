from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from .types import AudioBlock


class IAudioProcessor(ABC):
    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def process_in_place(self, x: AudioBlock, n_frames: int) -> None: ...


class PostChain(IAudioProcessor):
    def __init__(self, stages: Sequence[IAudioProcessor]) -> None:
        self._stages: List[IAudioProcessor] = list(stages)

    def reset(self) -> None:
        for s in self._stages:
            s.reset()

    def process_in_place(self, x: AudioBlock, n_frames: int) -> None:
        for s in self._stages:
            s.process_in_place(x, n_frames)
