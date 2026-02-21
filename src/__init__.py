"""heartdsp: núcleo DSP por stems (sin mezcla) para sonidos cardíacos.

API pública:
- StemId, STEM_ORDER
- FixedAudioBus
- Dsp
- Mixer
- EnvelopeLUT
"""

from .core.stems import StemId, STEM_ORDER
from .core.bus import FixedAudioBus, IAudioBusFixed
from .core.dsp import Dsp, IDspStemGenerator
from .core.mixer import Mixer, IMixer

from .dsp_blocks.envelope import EnvelopeLUT, IEnvelopeLUT
from .dsp_blocks.noise import INoiseSource
from .dsp_blocks.exciter_base import IExciter
from .dsp_blocks.burst_exciter import BurstExciter, BurstConfig, BurstAssets
from .dsp_blocks.train_exciter import TrainExciter, TrainConfig, TrainAssets
from .dsp_blocks.resonator import (
    ResonatorParams,
    ResonatorBankConfig,
    IResonatorBank,
    ResonatorBank,
)
from .dsp_blocks.voice import VoiceStartPayload, IStemVoice, StemVoice
