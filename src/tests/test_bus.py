from __future__ import annotations
from heartdsp.core.bus import FixedAudioBus
from heartdsp.core.stems import STEM_ORDER

def test_bus_clear_and_buffer():
    bus = FixedAudioBus(max_block_size=64)
    bus.clear_all(16)
    for stem in STEM_ORDER:
        buf = bus.buffer(stem)
        assert len(buf) >= 64
        assert all(buf[i] == 0.0 for i in range(16))
