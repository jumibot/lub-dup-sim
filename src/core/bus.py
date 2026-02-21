from __future__ import annotations

from typing import Dict, List, Protocol, Sequence

from .stems import StemId, STEM_ORDER
from .types import AudioBlock


class IAudioBusFixed(Protocol):
    """Contenedor de buffers de stems fijos.

    Contrato:
    - clear_all(n) pone a 0 todos los buffers de stems.
    - buffer(stem) devuelve referencia a un buffer con longitud >= nFrames del bloque.
    - No asigna memoria dentro de clear_all()/buffer() en tiempo real.
    """

    def clear_all(self, n_frames: int) -> None: ...
    def buffer(self, stem: StemId) -> AudioBlock: ...


class FixedAudioBus(IAudioBusFixed):
    """Implementación simple con buffers pre-alocados."""

    def __init__(self, max_block_size: int, stems: Sequence[StemId] = STEM_ORDER) -> None:
        self._max_block_size = int(max_block_size)
        self._buffers: Dict[StemId, List[float]] = {s: [0.0] * self._max_block_size for s in stems}

    @property
    def max_block_size(self) -> int:
        return self._max_block_size

    def clear_all(self, n_frames: int) -> None:
        n = int(n_frames)
        if n > self._max_block_size:
            raise ValueError(f"n_frames={n} > max_block_size={self._max_block_size}")
        for buf in self._buffers.values():
            for i in range(n):
                buf[i] = 0.0

    def buffer(self, stem: StemId) -> AudioBlock:
        try:
            return self._buffers[stem]
        except KeyError as e:
            raise KeyError(f"Stem no soportado: {stem}") from e
