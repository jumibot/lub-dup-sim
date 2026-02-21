from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Sequence

from ..core.stems import StemId
from ..core.types import AudioBlock
from .envelope import IEnvelopeLUT
from .exciter_base import IExciter
from .resonator import IResonator, ResonatorParams


@dataclass(frozen=True)
class VoiceStartPayload:
    """Payload genérico para arrancar una Voice.

    En una fase posterior lo especializarás (S1/S2/S3/S4/MurmurX).
    """

    exciter_config: object
    exciter_assets: object
    resonator_params: ResonatorParams
    out_env: Optional[IEnvelopeLUT] = None


class IStemVoice(ABC):
    @abstractmethod
    def stem_id(self) -> StemId: ...

    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def start(self, payload: VoiceStartPayload) -> None: ...

    @abstractmethod
    def render(self, out: AudioBlock, n_frames: int) -> None: ...

    @abstractmethod
    def is_active(self) -> bool: ...


class StemVoice(IStemVoice):
    """Voice genérica por stem: Exciter -> Resonator -> outEnv opcional."""

    def __init__(
        self,
        stem: StemId,
        exciter: IExciter,
        resonator: IResonator,
        max_block_size: int,
    ) -> None:
        self._stem = stem
        self._exciter = exciter
        self._resonator = resonator
        self._out_env: Optional[IEnvelopeLUT] = None
        self._active = False

        self._max_block = int(max_block_size)
        self._exc_buf: List[float] = [0.0] * self._max_block
        self._res_buf: List[float] = [0.0] * self._max_block
        self._env_phase = 0

    def stem_id(self) -> StemId:
        return self._stem

    def reset(self) -> None:
        self._exciter.reset()
        self._resonator.reset()
        self._out_env = None
        self._active = False
        self._env_phase = 0

    def start(self, payload: VoiceStartPayload) -> None:
        self._resonator.set_params(payload.resonator_params)
        self._out_env = payload.out_env
        self._env_phase = 0

        # Nota: IExciter base no fija start(); cada implementación concreta lo define.
        # Aquí asumimos que el exciter tiene start(cfg, assets). (duck typing)
        self._exciter.start(payload.exciter_config, payload.exciter_assets)  # type: ignore[attr-defined]
        self._active = True

    def is_active(self) -> bool:
        return self._active

    def render(self, out: AudioBlock, n_frames: int) -> None:
        n = int(n_frames)
        if n > self._max_block:
            raise ValueError(f"n_frames={n} > max_block_size={self._max_block}")

        if not self._active:
            for i in range(n):
                out[i] = 0.0
            return

        # 1) Excitación (sobrescribe exc_buf)
        self._exciter.render(self._exc_buf, n)

        # 2) Resonancia (sobrescribe res_buf)
        self._resonator.process(self._exc_buf, self._res_buf, n)

        # 3) Envelope de salida opcional
        if self._out_env is not None:
            lut = self._out_env
            L = lut.length()
            for i in range(n):
                idx = self._env_phase
                g = lut.value_at_index(idx) if 0 <= idx < L else 0.0
                out[i] = self._res_buf[i] * g
                self._env_phase += 1
        else:
            for i in range(n):
                out[i] = self._res_buf[i]

        # 4) Estado activo: por ahora simplificado
        if not self._exciter.is_active():
            # Si quieres colas largas del resonador, este apagado se refinará después.
            self._active = False
