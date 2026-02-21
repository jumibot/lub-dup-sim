from __future__ import annotations

from typing import Optional

from ..core.types import AudioBlock
from .exciter_base import BurstAssets, BurstConfig, IExciter


class BurstExciter(IExciter):
    """Excitación breve (S1/S2/S3/S4 típicamente)."""

    def __init__(self) -> None:
        self._active = False
        self._phase = 0
        self._cfg: Optional[BurstConfig] = None
        self._assets: Optional[BurstAssets] = None

    def reset(self) -> None:
        self._active = False
        self._phase = 0
        self._cfg = None
        self._assets = None

    def start(self, cfg: BurstConfig, assets: BurstAssets) -> None:
        self._cfg = cfg
        self._assets = assets
        self._phase = 0
        self._active = True

    def is_active(self) -> bool:
        return self._active

    def render(self, out: AudioBlock, n_frames: int) -> None:
        # TODO: ruido + click + envelope de entrada (LUT)
        n = int(n_frames)
        for i in range(n):
            out[i] = 0.0

        if self._cfg is None:
            self._active = False
            return

        self._phase += n
        if self._phase >= self._cfg.duration_samples:
            self._active = False
