# HeartDSP -- Diseño de Clases, Responsabilidades e Interrelaciones

Este documento describe el **núcleo DSP** para generación procedural de
sonidos cardíacos con: - **8 stems fijos**: S1, S2, S3, S4,
MURMUR_1..MURMUR_4 - **OUT externo** (no es un stem) - **1 Voice por
stem** - **1 resonador por Voice (por canal/stem)** - **Modelo
pull-based**: el sistema de audio demanda bloques `N` y el DSP responde
generando `N` samples

------------------------------------------------------------------------

## 1) Visión general

### Flujo de audio (por bloque)

1.  El host de audio pide `N` frames.
2.  El DSP genera los **8 buffers de stems**.
3.  El Mixer combina stems → `out[N]`.
4.  (Opcional) PostChain procesa `out[N]`.
5.  El host consume `out[N]` (DAC/BT).

------------------------------------------------------------------------

## 2) Clases principales y responsabilidades

### 2.1 `StemId`

**Responsabilidad** - Enumerar de forma **fija** los 8 canales lógicos
(stems).

**Por qué existe** - Impone un layout estable, RT-friendly y
testeable. - Evita stems dinámicos (que complican memoria/RT).

------------------------------------------------------------------------

### 2.2 `IAudioBusFixed` / `FixedAudioBus`

**Responsabilidad** - Mantener **8 buffers preasignados** (capacidad
`max_block_size`). - Exponer: - `clear_all(n_frames)` -
`buffer(stem) -> AudioBlock`

**Reglas** - No mezcla. - No asigna memoria dentro de
`clear_all`/`buffer` (RT-friendly).

**Interacción** - Consumido por `Dsp` (escritura) y `Mixer` (lectura).

------------------------------------------------------------------------

### 2.3 `IDspStemGenerator` / `Dsp`

**Responsabilidad** - Orquestar `IStemVoice` (una por stem) y
**escribir** en el `IAudioBusFixed`. - No mezcla. - No postprocesa.

**Contrato** - `render(bus, n_frames)`: 1) limpia bus\
2) llama a cada voice para que escriba su stem

**Nota** - La temporización clínica (BPM, respiración) no vive aquí;
llegará desde fuera mediante triggers/eventos.

------------------------------------------------------------------------

### 2.4 `IStemVoice` / `StemVoice`

**Responsabilidad** - Generar audio para **un stem concreto**. -
Composición interna: - `Exciter` → `Resonator` → `OutEnvelope`
(opcional)

**Contrato** - `render(out, n_frames)` sobrescribe el buffer del stem. -
`start(payload)` arma el estado interno para empezar a emitir. -
`is_active()` indica si sigue generando.

**Estado interno típico** - fase del exciter - estado del resonador
(memorias del filtro) - fase de la envelope de salida (si aplica)

------------------------------------------------------------------------

### 2.5 `IExciter` + implementaciones (`BurstExciter`, `TrainExciter`)

**Responsabilidad** - Generar **excitación cruda** (no resonada), que
alimenta el resonador. - No mezcla.

**Implementaciones** - `BurstExciter`: excitación breve para S1--S4
(ruido/click + envelope). - `TrainExciter`: excitación larga para
murmullos (turbulencia + envelope).

**Contrato** - `start(config, assets)` - `render(out, n_frames)`
sobrescribe `out` - `is_active()`

------------------------------------------------------------------------

### 2.6 `IResonator` / `Resonator`

**Responsabilidad** - Convertir excitación en señal oscilante
amortiguada. - **1 resonador por stem**.

**Contrato** - `set_params(f0_hz, q, gain)` -
`process(inp, out, n_frames)` sobrescribe `out`

**Nota** - En esta versión, el "cuerpo" de cada stem se modela con un
único resonador.

------------------------------------------------------------------------

### 2.7 `IEnvelopeLUT` / `EnvelopeLUT`

**Responsabilidad** - LUT inmutable (asset) para shapes de
envolventes. - Solo expone acceso por índice/longitud.

**Regla** - La LUT **no** tiene fase; la fase vive en quien la usa
(`StemVoice` o `Exciter`).

------------------------------------------------------------------------

### 2.8 `INoiseSource`

**Responsabilidad** - Proveer ruido (white/pink/tilt/band-limited) según
implementación. - Contrato mínimo y portable a C/ESP32: -
`reset(seed)` - `next_block(out, n_frames)`

------------------------------------------------------------------------

### 2.9 `IMixer` / `Mixer`

**Responsabilidad** - Combinar los 8 stems en un buffer final
**externo** `out[N]`. - Aplicar ganancias por stem (y, si se desea, una
matriz en el futuro).

**Contrato** - `mix(bus, out, n_frames)` sobrescribe `out`

**Regla** - OUT no es un stem; es el resultado final de mezcla.

------------------------------------------------------------------------

### 2.10 `IAudioProcessor` / `PostChain` (opcional)

**Responsabilidad** - Procesar `out[N]` después de la mezcla: - HP/LP
tipo fonendo - softclip / limiter suave - etc.

**Contrato** - `process_in_place(out, n_frames)`

------------------------------------------------------------------------

## 3) Interrelaciones (quién depende de quién)

-   `Dsp` depende de:
    -   `IAudioBusFixed` (para escribir stems)
    -   `IStemVoice` (para generar cada stem)
-   `StemVoice` depende de:
    -   `IExciter` (excitación)
    -   `IResonator` (resonancia)
    -   `IEnvelopeLUT` opcional (envelope de salida)
-   `BurstExciter` / `TrainExciter` dependen de:
    -   `INoiseSource`
    -   `IEnvelopeLUT` (envelope de entrada)
-   `Mixer` depende de:
    -   `IAudioBusFixed` (lee stems)
    -   `out[N]` externo (escribe mezcla)
-   `PostChain` depende de:
    -   `out[N]` externo (procesa in-place)

------------------------------------------------------------------------

## 4) UML (Mermaid)

> Nota: Mermaid se renderiza en GitHub y muchos visores Markdown; si tu
> visor no lo soporta, el diagrama se verá como texto.

``` mermaid
classDiagram

class StemId {
  <<enumeration>>
  S1
  S2
  S3
  S4
  MURMUR_1
  MURMUR_2
  MURMUR_3
  MURMUR_4
}

class IAudioBusFixed {
  <<interface>>
  +clear_all(nFrames: int)
  +buffer(stem: StemId) float[]
}

class IDspStemGenerator {
  <<interface>>
  +reset()
  +render(bus: IAudioBusFixed, nFrames: int)
}

class Dsp {
  -voices: IStemVoice[8]
  +reset()
  +render(bus: IAudioBusFixed, nFrames: int)
}

class IStemVoice {
  <<interface>>
  +stem_id() StemId
  +reset()
  +start(payload)
  +render(out: float[], nFrames: int)
  +is_active() bool
}

class StemVoice {
  -stem: StemId
  -exciter: IExciter
  -resonator: IResonator
  -outEnv: IEnvelopeLUT?
  +start(payload)
  +render(out: float[], nFrames: int)
}

class IExciter {
  <<interface>>
  +reset()
  +start(config, assets)
  +render(out: float[], nFrames: int)
  +is_active() bool
}

class BurstExciter {
  +start(BurstConfig, BurstAssets)
  +render(out: float[], nFrames: int)
}

class TrainExciter {
  +start(TrainConfig, TrainAssets)
  +render(out: float[], nFrames: int)
}

class IResonator {
  <<interface>>
  +reset()
  +set_params(f0_hz: float, q: float, gain: float)
  +process(inp: float[], out: float[], nFrames: int)
}

class Resonator {
  +set_params(...)
  +process(...)
}

class IEnvelopeLUT {
  <<interface>>
  +length() int
  +value_at_index(i: int) float
}

class EnvelopeLUT {
  -table: float[]
  +length() int
  +value_at_index(i: int) float
}

class INoiseSource {
  <<interface>>
  +reset(seed: int)
  +next_block(out: float[], nFrames: int)
}

class IMixer {
  <<interface>>
  +reset()
  +mix(bus: IAudioBusFixed, out: float[], nFrames: int)
}

class Mixer {
  -gains: Map~StemId,float~
  +mix(bus: IAudioBusFixed, out: float[], nFrames: int)
}

class OutputBuffer {
  <<external>>
  float[] out
}

class IAudioProcessor {
  <<interface>>
  +reset()
  +process_in_place(x: float[], nFrames: int)
}

class PostChain {
  -stages: IAudioProcessor[]
  +process_in_place(x: float[], nFrames: int)
}

Dsp ..|> IDspStemGenerator
Dsp o-- IStemVoice
Dsp ..> IAudioBusFixed

StemVoice ..|> IStemVoice
StemVoice o-- IExciter
StemVoice o-- IResonator
StemVoice o-- IEnvelopeLUT

BurstExciter ..|> IExciter
TrainExciter ..|> IExciter
BurstExciter ..> INoiseSource
TrainExciter ..> INoiseSource
BurstExciter ..> IEnvelopeLUT
TrainExciter ..> IEnvelopeLUT

Resonator ..|> IResonator
EnvelopeLUT ..|> IEnvelopeLUT

Mixer ..|> IMixer
Mixer ..> IAudioBusFixed
Mixer ..> OutputBuffer

PostChain ..|> IAudioProcessor
PostChain ..> OutputBuffer
```

------------------------------------------------------------------------

## 5) Reglas prácticas para mantenerlo "RT-safe"

-   Prealocar buffers:
    -   bus (8×max_block_size)
    -   out (max_block_size)
    -   scratch internos en cada voice (si aplica)
-   No asignar memoria dentro de `render()` / `mix()`.
-   Mantener LUTs como assets inmutables.
-   1 voice por stem evita sumas internas y simplifica.

------------------------------------------------------------------------

## 6) Qué queda fuera a propósito (capa superior)

-   Scheduler (BPM, respiración, split, etc.)
-   Gestión de presets clínicos (compilación de LUTs)
-   IO (WAV, reproducción, streaming BT)

Todo eso se enchufa por encima mediante triggers/eventos y
configuración.
