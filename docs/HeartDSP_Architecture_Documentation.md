# HeartDSP -- Arquitectura del Núcleo DSP (Versión Simplificada)

## 1. Filosofía de Diseño

El DSP está diseñado bajo los siguientes principios:

-   Generación procedural 100% (sin samples WAV).
-   Separación estricta entre generación (DSP) y mezcla.
-   Una Voice por Stem.
-   Un único resonador por Stem.
-   Límite duro de stems:
    -   S1
    -   S2
    -   S3
    -   S4
    -   MURMUR_1
    -   MURMUR_2
    -   MURMUR_3
    -   MURMUR_4
-   OUT no es un stem.
-   Sin allocations en tiempo real.
-   Interfaces pequeñas y testeables.
-   Portabilidad futura a C / ESP32.

------------------------------------------------------------------------

## 2. Arquitectura General

DSP genera 8 stems fijos → Mixer mezcla → PostChain procesa → OUT final

Dsp → AudioBus (8 stems) → Mixer → OUT\[\] → PostChain

Cada stem tiene exactamente:

Exciter → Resonator → OutEnvelope (opcional)

------------------------------------------------------------------------

## 3. Core

### 3.1 StemId

Enumeración fija con 8 pistas.

### 3.2 IAudioBusFixed

Contenedor de buffers preasignados.

Responsabilidades: - clear_all(nFrames) - buffer(stem)

No realiza mezcla.

------------------------------------------------------------------------

### 3.3 IDspStemGenerator

Interfaz del DSP.

Responsabilidades: - reset() - render(bus, nFrames)

El DSP: 1. Limpia el bus. 2. Pide a cada Voice que escriba su stem.

No mezcla.

------------------------------------------------------------------------

### 3.4 IMixer

Responsabilidades: - mix(bus, out, nFrames)

Mezcla stems → buffer externo OUT\[\].

OUT no pertenece al bus.

------------------------------------------------------------------------

## 4. Bloques DSP

### 4.1 EnvelopeLUT

Asset inmutable.

-   table: tuple\[float\]
-   value_at_index(i)

El estado (fase) vive en la Voice, no en la LUT.

------------------------------------------------------------------------

### 4.2 INoiseSource

Contrato mínimo:

-   reset(seed)
-   next_block(out, nFrames)

El tipo de ruido (white/pink/band) es implementación concreta.

------------------------------------------------------------------------

### 4.3 IExciter

Genera excitación cruda.

-   reset()
-   start(config, assets)
-   render(out, nFrames) \# sobrescribe
-   is_active()

Implementaciones: - BurstExciter (S1-S4) - TrainExciter (murmullos)

------------------------------------------------------------------------

### 4.4 IResonator

Convierte excitación en oscilación amortiguada.

Responsabilidades:

-   reset()
-   set_params(f0_hz, q, gain)
-   process(inp, out, nFrames)

Es un único resonador por stem.

------------------------------------------------------------------------

### 4.5 StemVoice

Composición interna:

Exciter → Resonator → OutEnvelope opcional

Responsabilidades:

-   render(out, nFrames) \# sobrescribe stem
-   is_active()

Una instancia por Stem. Un único resonador por Voice.

------------------------------------------------------------------------

## 5. Flujo de Señal

Para cada bloque:

1.  DSP limpia bus.
2.  Cada Voice:
    -   genera excitación
    -   pasa por resonador único
    -   aplica envelope de salida (si existe)
    -   escribe en su stem
3.  Mixer combina stems en OUT.
4.  PostChain opcional procesa OUT.

------------------------------------------------------------------------

## 6. Decisiones Arquitectónicas Clave

✔ 1 DSP por paciente\
✔ 1 Voice por Stem\
✔ 1 Resonador por Stem\
✔ Bus fijo (8 stems)\
✔ Mixer separado\
✔ OUT externo

Simplicidad estructural como prioridad.

------------------------------------------------------------------------

## 7. Razonamiento Acústico

Un único resonador por stem es suficiente para:

-   Modelar el "cuerpo" dominante del sonido.
-   Mantener coherencia espectral.
-   Reducir complejidad y CPU.
-   Facilitar afinado clínico por oído.

La riqueza tímbrica adicional proviene de:

-   Diseño del Exciter.
-   Forma de las Envelopes.
-   Filtro tipo fonendoscopio en post.
-   Softclip o limitador suave.

------------------------------------------------------------------------

## 8. Extensibilidad

Si en el futuro se necesitara mayor complejidad:

-   Se puede sustituir IResonator por una implementación más compleja.
-   No es necesario cambiar la arquitectura base.

------------------------------------------------------------------------

## 9. Portabilidad a ESP32

El diseño facilita:

-   Buffers prealocados.
-   Un único biquad por stem.
-   Cálculo eficiente.
-   Baja carga de CPU.
-   Fácil reimplementación en C.

------------------------------------------------------------------------

## 10. Próximos Pasos

-   Implementación concreta del Resonator (biquad 2º orden).
-   Implementación real de NoiseSource.
-   Definir presets clínicos iniciales (f0 y Q por stem).
-   Añadir limitador suave en PostChain.
-   Test auditivo iterativo.
