# HeartDSP -- Modelo Temporal y Flujo de Bloques

## 1. Fundamento: Qué es un Sample

En audio digital, cada sample representa el valor de la señal en un
instante discreto del tiempo.

Si la frecuencia de muestreo es:

fs = 48.000 Hz

Entonces el intervalo temporal entre samples es:

Δt = 1 / fs ≈ 20.833 µs

Por lo tanto:

-   Sample 0 → t = 0
-   Sample 1 → t = 1/fs
-   Sample 2 → t = 2/fs
-   ...
-   Sample n → t = n/fs

El tiempo en el sistema está completamente definido por el índice de
muestra.

No es necesario un reloj físico dentro del DSP.

------------------------------------------------------------------------

## 2. Tiempo lógico vs tiempo físico

### Tiempo físico

Lo impone el hardware de reproducción (DAC / I2S / Bluetooth).

Es el único reloj "duro".\
Si no se entregan muestras a tiempo → glitch.

### Tiempo lógico

Es el contador de samples generados por el DSP.

generated_sample_count = número total de muestras generadas desde reset.

Este contador define el eje temporal interno del sistema.

------------------------------------------------------------------------

## 3. Modelo Pull-Based

El DSP funciona bajo demanda.

Flujo típico:

Audio Host → pide N samples\
DSP → genera N samples\
Mixer → mezcla stems\
Post → procesa\
Audio Host → reproduce

Ejemplo:

render(256) render(256) render(256)

Internamente el tiempo avanza:

samples 0..255\
samples 256..511\
samples 512..767

Aunque se generen por bloques, el tiempo es continuo.

------------------------------------------------------------------------

## 4. Bloques y Continuidad Temporal

Aunque el cálculo se haga en bloques:

-   No existe salto temporal.
-   No existe reinicio de fase.
-   El estado interno continúa.

Condiciones necesarias:

✔ No perder muestras\
✔ No duplicar muestras\
✔ Mantener orden secuencial

Si se cumplen, el tiempo es perfecto.

------------------------------------------------------------------------

## 5. Ciclo de Vida de Generación

Inicialización:

-   Se fija sample_rate.
-   Se define max_block_size.
-   Se prealocan buffers.

En cada callback:

1.  bus.clear_all(N)
2.  dsp.render(bus, N)
3.  mixer.mix(bus, out, N)
4.  post.process(out, N)
5.  El host reproduce out

El DSP no controla el reloj. Solo responde a la demanda.

------------------------------------------------------------------------

## 6. Offset Intra-Bloque

Un evento puede ocurrir dentro de un bloque.

Ejemplo:

Se generan 256 samples y S1 debe comenzar en el sample 37.

La voice debe:

-   Escribir ceros en \[0..36\]
-   Generar señal desde 37 hasta 255

Esto preserva precisión temporal sin necesidad de reloj real.

------------------------------------------------------------------------

## 7. Qué NO necesita el DSP

El DSP no necesita:

-   Reloj en milisegundos
-   Timer interno
-   BPM global
-   Conocimiento del mundo real

El DSP solo necesita coherencia en el índice de muestra.

------------------------------------------------------------------------

## 8. Separación de Responsabilidades

Tiempo físico → Sistema de reproducción\
Tiempo lógico (samples) → DSP\
Fase cardiaca / BPM → Scheduler

Separar estas capas mantiene la arquitectura limpia.

------------------------------------------------------------------------

## 9. Conclusión

En HeartDSP:

-   El tiempo es discreto.
-   Cada sample corresponde a un instante exacto.
-   Los samples están uniformemente espaciados.
-   El DSP genera bajo demanda.
-   El reloj real pertenece al sistema de reproducción.
-   El contador de muestras generadas define el eje temporal interno.

Si la secuencia de muestras es continua y ordenada, el tiempo es
matemáticamente exacto.
