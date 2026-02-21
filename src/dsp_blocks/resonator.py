from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, Sequence, Tuple

from ..core.types import AudioBlock


@dataclass(frozen=True)
class ResonatorParams:
    f0_hz: float
    q: float
    gain: float


@dataclass(frozen=True)
class ResonatorBankConfig:
    modes: Tuple[ResonatorParams, ...]


class IResonatorBank(ABC):
    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def set_config(self, config: ResonatorBankConfig) -> None: ...

    @abstractmethod
    def process(self, inp: Sequence[float], out: AudioBlock, n_frames: int) -> None: ...


class ResonatorBank(IResonatorBank):
    """Banco de resonadores.

    Nota: implementación DSP real pendiente. Este esqueleto solo fija el contrato.
    """

    def __init__(self, sample_rate_hz: float) -> None:
        self._fs = float(sample_rate_hz)
        self._config: Optional[ResonatorBankConfig] = None

    def reset(self) -> None:
        # TODO: reset estados internos
        pass

    def set_config(self, config: ResonatorBankConfig) -> None:
        self._config = config
        # TODO: precalcular coeficientes, preparar estados

    def process(self, inp: Sequence[float], out: AudioBlock, n_frames: int) -> None:
        # TODO: out = suma(resonator_i(inp))
        n = int(n_frames)
        for i in range(n):
            out[i] = 0.0
