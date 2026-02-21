# HeartDSP -- Diseño de Clases (compacto)

## Foto general

**DSP (stems) → Mixer (OUT) → Post (opcional) → Host (DAC/BT)**

-   8 stems fijos: **S1, S2, S3, S4, MURMUR_1..MURMUR_4**
-   **OUT no es un stem**
-   **1 Voice por stem**
-   **1 resonador por Voice**

------------------------------------------------------------------------

## Grid 1 --- Componentes principales

  -------------------------------------------------------------------------------------------
  Componente        Qué hace (1      Entrada             Salida           Estado interno
                    frase)                                                
  ----------------- ---------------- ------------------- ---------------- -------------------
  `Dsp`             Rellena el bus   `IAudioBusFixed`,   8 buffers de     contador opcional
                    de stems por     `N`                 stems (en el     de samples
                    bloque (no                           bus)             generados, lista de
                    mezcla)                                               voices

  `FixedAudioBus`   Contiene 8       `N`                 `buffer(stem)`   buffers 8×max_block
                    buffers                                               
                    prealocados                                           

  `StemVoice`       Genera **un**    `N` (+ start        `stem[N]`        fase exciter,
                    stem             payload)                             estado resonador,
                                                                          fase envelope

  `Mixer`           Combina stems →  bus + `N`           `out[N]`         ganancias por stem
                    OUT                                                   

  `PostChain`       Procesa OUT      `out[N]`            `out[N]`         estados de
  (opc.)            (fonendo/clip)                                        filtros/limitador
  -------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## Grid 2 --- Composición por stem (lo que ocurre dentro de una Voice)

  ----------------------------------------------------------------------------
  Elemento interno  Rol               Ajustes típicos        Comentario
  ----------------- ----------------- ---------------------- -----------------
  `Exciter`         Genera excitación level, duración,       aquí se gana
  (Burst/Train)     (energía)         roughness, click/noise mucho realismo
                                      mix                    

  `Resonator`       Da "cuerpo"       f0, Q, gain            1 resonador por
  (único)           amortiguado                              stem

  `OutEnvelope`     Control de        shape, duración        la LUT es asset;
  (LUT opc.)        ataque/cola final                        fase vive en
                                                             Voice

  `NoiseSource` (en Ruido base        white/pink/tilt/band   contrato mínimo,
  exciter)                                                   implementación
                                                             intercambiable
  ----------------------------------------------------------------------------

------------------------------------------------------------------------

## Grid 3 --- Interrelaciones (dependencias reales)

  -----------------------------------------------------------------------
  Quién                   Depende de              Para qué
  ----------------------- ----------------------- -----------------------
  `Dsp`                   `IAudioBusFixed`,       escribir stems por
                          `IStemVoice`            bloque

  `StemVoice`             `IExciter`,             generar audio del stem
                          `IResonator`,           
                          `IEnvelopeLUT?`         

  `BurstExciter` /        `INoiseSource`,         crear excitación
  `TrainExciter`          `IEnvelopeLUT`          controlada
                          (entrada)               

  `Mixer`                 `IAudioBusFixed` +      producir mezcla final
                          `out[]` externo         

  `PostChain`             `out[]` externo         postprocesar salida
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## Modelo de ejecución (pull-based, por bloques)

1)  Host pide **N** frames (callback/loop).\
2)  `bus.clear_all(N)`\
3)  `dsp.render(bus, N)` → llena stems\
4)  `mixer.mix(bus, out, N)` → genera OUT\
5)  `post.process(out, N)` (opcional)\
6)  Host consume `out` (DAC/BT)

**Nota:** el "reloj duro" es el de reproducción; el DSP solo genera
**samples consecutivos**.

------------------------------------------------------------------------

## UML (Mermaid) -- Solo clases "concretas" (interfaces en segundo plano)

``` mermaid
classDiagram
direction LR

class Dsp
class FixedAudioBus
class StemVoice
class Mixer
class PostChain
class BurstExciter
class TrainExciter
class Resonator
class EnvelopeLUT
class NoiseSource
class OutputBuffer

Dsp o-- StemVoice : 1 por stem
Dsp ..> FixedAudioBus : escribe stems
Mixer ..> FixedAudioBus : lee stems
Mixer ..> OutputBuffer : escribe OUT
PostChain ..> OutputBuffer : procesa OUT

StemVoice o-- BurstExciter : (S1..S4)
StemVoice o-- TrainExciter : (Murmurs)
StemVoice o-- Resonator : 1 por stem
StemVoice o-- EnvelopeLUT : out env (opc.)

BurstExciter ..> NoiseSource
TrainExciter ..> NoiseSource
BurstExciter ..> EnvelopeLUT : in env
TrainExciter ..> EnvelopeLUT : in env
```

> `NoiseSource` es conceptual: en código es una implementación de
> `INoiseSource` (contrato).\
> Idem para exciter/resonator/envelope: arriba se muestra lo "concreto"
> para simplificar lectura.

------------------------------------------------------------------------

## Interfaces (referencia rápida, segundo plano)

  Interfaz              Uso
  --------------------- ------------------------------
  `IAudioBusFixed`      buffers prealocados de stems
  `IDspStemGenerator`   contrato de `Dsp.render()`
  `IStemVoice`          contrato de voice por stem
  `IExciter`            burst/train
  `IResonator`          resonador único
  `IEnvelopeLUT`        LUT asset
  `INoiseSource`        fuente de ruido
  `IMixer`              mezcla stems→OUT
  `IAudioProcessor`     post en OUT
