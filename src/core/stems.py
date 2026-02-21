from __future__ import annotations
from enum import Enum
from typing import Tuple

class StemId(Enum):
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"
    MURMUR_1 = "MURMUR_1"
    MURMUR_2 = "MURMUR_2"
    MURMUR_3 = "MURMUR_3"
    MURMUR_4 = "MURMUR_4"

STEM_ORDER: Tuple[StemId, ...] = (
    StemId.S1,
    StemId.S2,
    StemId.S3,
    StemId.S4,
    StemId.MURMUR_1,
    StemId.MURMUR_2,
    StemId.MURMUR_3,
    StemId.MURMUR_4,
)
