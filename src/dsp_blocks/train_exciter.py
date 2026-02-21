from __future__ import annotations

from typing import Optional

from ..core.types import AudioBlock
from .exciter_base import IExciter, TrainAssets, TrainConfig


class TrainExciter(IExciter):
    """Excitación larga (turbulencia para soplos)."""

    def __init__(self) -> None:
        self._active = False
        self._phase = 0
        self._cfg: Optional[TrainConfig] = None
        self._assets: Optional[TrainAssets] = None

    def reset(self) -> None:
        self._active = False
        self._phase = 0
        self._cfg = None
        self._assets = None

    def start(self, cfg: TrainConfig, assets: TrainAssets) -> None:
        self._cfg = cfg
        self._assets = assets
        self._phase = 0
        self._active = True

    def is_active(self) -> bool:
        return self._active

    def render(self, out: AudioBlock, n_frames: int) -> None:
        # TODO: ruido + modulación caótica + envelope de entrada (LUT)
        n = int(n_frames)
        for i in range(n):
            out[i] = 0.0

        if self._cfg is None:
            self._active = False
            return

        self._phase += n
        if self._phase >= self._cfg.duration_samples:
            self._active = False
