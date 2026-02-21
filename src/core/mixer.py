from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional

from .bus import IAudioBusFixed
from .stems import StemId, STEM_ORDER
from .types import AudioBlock


class IMixer(ABC):
    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def mix(self, bus: IAudioBusFixed, out: AudioBlock, n_frames: int) -> None: ...


class Mixer(IMixer):
    """Mixer externo: stems -> out[]. OUT no es un stem."""

    def __init__(self, gains: Optional[Dict[StemId, float]] = None) -> None:
        self._gains: Dict[StemId, float] = dict(gains) if gains else {s: 1.0 for s in STEM_ORDER}

    def reset(self) -> None:
        # Sin estado por ahora
        pass

    def set_gain(self, stem: StemId, gain: float) -> None:
        self._gains[stem] = float(gain)

    def mix(self, bus: IAudioBusFixed, out: AudioBlock, n_frames: int) -> None:
        n = int(n_frames)
        for i in range(n):
            out[i] = 0.0

        for stem in STEM_ORDER:
            g = self._gains.get(stem, 0.0)
            if g == 0.0:
                continue
            buf = bus.buffer(stem)
            for i in range(n):
                out[i] += buf[i] * g
