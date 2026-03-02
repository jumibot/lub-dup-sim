from __future__ import annotations

"""Resonador (único) por stem.

Decisión de arquitectura:
- 1 Voice por Stem
- 1 Resonator por Voice

Este módulo fija el contrato y deja un esqueleto de implementación.
La implementación DSP real (biquad/resonator 2º orden) se añadirá en una fase posterior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from ..core.types import AudioBlock


@dataclass(frozen=True)
class ResonatorParams:
    """Parámetros de un resonador de 2º orden (conceptualmente).

    - f0_hz: frecuencia central
    - q: factor de calidad (relacionado con amortiguación/decay)
    - gain: ganancia aplicada a la salida del resonador
    """

    f0_hz: float
    q: float
    gain: float


class IResonator(ABC):
    """Contrato de resonador único.

    process() escribe 'out' (sobrescribe) y no asigna memoria.
    """

    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def set_params(self, params: ResonatorParams) -> None: ...

    @abstractmethod
    def process(self, inp: Sequence[float], out: AudioBlock, n_frames: int) -> None: ...


class Resonator(IResonator):
    """Resonador único (esqueleto).

    Nota: aquí NO implementamos DSP real todavía.
    El objetivo es dejar el contrato estable y portable.
    """

    def __init__(self, sample_rate_hz: float) -> None:
        self._fs = float(sample_rate_hz)
        self._params: Optional[ResonatorParams] = None
        # TODO: estados internos (x1, x2, y1, y2) y coeficientes

    def reset(self) -> None:
        # TODO: reset estados internos
        pass

    def set_params(self, params: ResonatorParams) -> None:
        self._params = params
        # TODO: precalcular coeficientes a partir de f0/Q y fs

    def process(self, inp: Sequence[float], out: AudioBlock, n_frames: int) -> None:
        # TODO: aplicar resonancia real
        n = int(n_frames)
        for i in range(n):
            out[i] = 0.0
