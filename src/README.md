# heartdsp

Núcleo DSP por stems (S1..S4 + 4 murmullos) y Mixer externo.

## Principios
- El DSP genera stems fijos. **No mezcla**.
- `out[]` no es un stem: lo produce `Mixer`.
- Una voice por stem.
- LUTs (envelopes) entran como assets; el DSP no compila LUTs.

## Uso mínimo (esqueleto)
```python
from heartdsp import FixedAudioBus, Dsp, Mixer, StemId

bus = FixedAudioBus(max_block_size=256)
dsp = Dsp(voices=[])  # TODO: inyectar voices reales
mixer = Mixer()

dsp.render(bus, n_frames=128)
out = [0.0]*256
mixer.mix(bus, out, n_frames=128)
```
