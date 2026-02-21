"""Tipos compartidos del core.

Nota: evitamos numpy a propósito (portabilidad / ESP32 / C).
"""

from __future__ import annotations
from typing import MutableSequence

AudioBlock = MutableSequence[float]
