from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..core.types import AudioBlock
from .envelope import IEnvelopeLUT
from .noise import INoiseSource


@dataclass(frozen=True)
class BurstConfig:
    level: float
    duration_samples: int
    noise_mix: float
    click_mix: float


@dataclass(frozen=True)
class TrainConfig:
    level: float
    duration_samples: int
    roughness: float


@dataclass(frozen=True)
class BurstAssets:
    noise: INoiseSource
    in_env: IEnvelopeLUT


@dataclass(frozen=True)
class TrainAssets:
    noise: INoiseSource
    in_env: IEnvelopeLUT


class IExciter(ABC):
    """Genera excitación (no resonada). render() sobrescribe out."""

    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def is_active(self) -> bool: ...

    @abstractmethod
    def render(self, out: AudioBlock, n_frames: int) -> None: ...

