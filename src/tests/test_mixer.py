from __future__ import annotations
from heartdsp.core.bus import FixedAudioBus
from heartdsp.core.mixer import Mixer
from heartdsp.core.stems import StemId

def test_mixer_basic_gain():
    bus = FixedAudioBus(max_block_size=16)
    n = 8
    bus.clear_all(n)
    s1 = bus.buffer(StemId.S1)
    for i in range(n):
        s1[i] = 1.0

    mix = Mixer(gains={StemId.S1: 0.5})
    out = [0.0]*16
    mix.mix(bus, out, n)
    assert all(abs(out[i]-0.5) < 1e-9 for i in range(n))
