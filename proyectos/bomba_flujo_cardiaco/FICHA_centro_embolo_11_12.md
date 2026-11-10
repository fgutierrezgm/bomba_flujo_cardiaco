# FICHA DE DISEÑO - Centro del Émbolo Parte 1 y Parte 2 (Planos Nº 11 y Nº 12)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 61, Plano Nº 11 "Centro del embolo parte 1"): vista frontal lado brida, vista lateral, vista frontal lado vástago y corte `SECTION D-D` (Escala 2:1).
- `entradas/informe_y_planos_bomba.pdf` (pág. 62, Plano Nº 12 "Centro del embolo parte 2"): vista frontal exterior, corte `SECTION E-E` y vista posterior (Escala 2:1).
- Memoria descriptiva del informe: conjunto metálico central (latón / acero inoxidable) que vincula rígidamente el disco de Delrin (Plano 10) con la tuerca/husillo de bolas de `M14x2` que transmite el movimiento axial.

## 2. Función y contexto
El núcleo metálico del émbolo está dividido en dos piezas (Parte 1 y Parte 2) que abrazan y se fijan al disco de Delrin (`h = 20.00 mm`, Plano 10):
- **Parte 1 (Plano Nº 11):** Pieza tipo brida con vástago tubular roscado interiormente (`M14x2`). La brida (`Ø45.00 mm`, espesor `6.00 mm`) apoya contra una cara del disco de Delrin y se fija a este mediante 4 tornillos `M3` que pasan por los 4 agujeros de `Ø3.50 mm` sobre `Ø37.50 mm`. El vástago de `Ø30.00 mm` atraviesa el agujero central de `Ø30.00 mm` del disco de Delrin.
- **Parte 2 (Plano Nº 12):** Brida anular plana (`Ø45.00 mm`, agujero interior `Ø15.00 mm`, espesor `5.00 mm`) que se acopla en el extremo frontal del vástago de la Parte 1 mediante 3 tornillos `M3` (agujeros pasantes `Ø3.50 mm` avellanados a `Ø5.00 x 0.75 mm` a `120°` sobre `Ø21.00 mm`), que roscan en los 3 agujeros `M3x0.5` (prof. `15.00 mm`) de la cara superior de la Parte 1.

## 3. Datos generales
Material: Latón (densidad `8.50 g/cm³` = `0.00000850 kg/mm³`) o Acero Inoxidable (densidad `7.85 - 7.90 g/cm³` = `0.00000785 kg/mm³`) | Proceso previsto: torneado + taladrado/roscado | Cantidad: 1 de cada pieza (1x Plano 11 + 1x Plano 12) | Tolerancias: no especificadas en plano | Acabado: torneado fino.

## 4. Cotas y elementos

### 4.1. Parte 1 (`Centro_Embolo_1_11`, Plano Nº 11)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro de brida (`d_brida`) | `Ø45.00 mm` | plano | alta | Apoya sobre el disco de Delrin |
| Espesor de brida (`h_brida`) | `6.00 mm` | plano | alta | En `SECTION D-D` |
| Diámetro de vástago (`d_vast`) | `Ø30.00 mm` | plano | alta | Entra en el agujero `Ø30.00 mm` del Delrin |
| Altura total (`h_total`) | `24.80 mm` | plano | alta | De extremo a extremo (`Z = 0` a `Z = 24.80 mm`) |
| Cota parcial vástago | `19.80 mm` | plano | media | Ver sección 5: `6.00 + 19.80 = 25.80 != 24.80` (solapamiento de `1.00 mm` o `2 x 0.50 mm`) |
| Rosca central (`d_m14`) | `M14x2` pasante | plano + norma | alta | Mecha `Ø12.00 mm` |
| Corona agujeros brida (`d_cor_brida`) | `Ø37.50 mm` | plano | alta | 4x a `0°, 90°, 180°, 270°` |
| Agujeros pasantes brida (`d_aguj_brida`) | `4x Ø3.50 mm` | plano | alta | Con avellanado a `90°` de `0.50 mm` desde `Z = 0` |
| Corona roscas superiores (`d_cor_sup`) | `Ø21.00 mm` | plano | alta | 3x a `120°` (`90°, 210°, 330°`) |
| Roscas superiores (`d_m3`, `p_m3`) | `3x M3x0.5`, prof. `15.00 mm` | plano + norma | alta | Mecha `Ø2.50 mm`, desde `Z = h_total` |
| Chaflanes exteriores e int. (`c_ch`) | `0.50 x 45°` | plano | alta | En aristas de brida, tope de vástago y entrada de `M14x2` |

### 4.2. Parte 2 (`Centro_Embolo_2_12`, Plano Nº 12)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior (`d_ext`) | `Ø45.00 mm` | plano | alta | Igual al diámetro de brida de la Parte 1 |
| Espesor total (`h_total`) | `5.00 mm` | plano | alta | Ancho axial del disco |
| Agujero central (`d_int`) | `Ø15.00 mm` | plano | alta | Pasa con holgura sobre la rosca `M14x2` |
| Corona de agujeros (`d_cor`) | `Ø21.00 mm` | plano | alta | 3x a `120°` (`90°, 210°, 330°`), coincide con Parte 1 |
| Agujeros pasantes (`d_aguj`) | `3x Ø3.50 mm` | plano | alta | Para tornillos `M3` |
| Avellanado/cajeado (`d_caj`, `p_caj`) | `Ø5.00 mm`, prof. `0.75 mm` a `90°` | plano | alta | Geométricamente exacto: `(5.00 - 3.50) / 2 = 0.75 mm` a `90°` |
| Chaflanes (`c_ch`) | `0.50 x 45°` | plano | alta | En borde exterior e interior de cara `Z = 0` |

## 5. Verificación de coherencia
- **Incoherencia en cadena axial del Plano Nº 11 (`6.00 + 19.80 = 25.80 mm != 24.80 mm`):**
  - En la vista lateral superior del Plano 11 se acota simultáneamente la longitud total `24.80 mm` y la longitud del vástago `19.80 mm`, mientras que en `SECTION D-D` el espesor de la brida es `6.00 mm`. La suma `6.00 + 19.80 = 25.80 mm` excede en `1.00 mm` la altura total de `24.80 mm` (lo que equivale a que la cota `19.80 mm` haya sido tomada desde un plano interior o sumando erróneamente los dos chaflanes de `0.50 mm`). Se adopta como cota rectora `h_total = 24.80 mm` y `h_brida = 6.00 mm` (quedando el vástago saliente de `18.80 mm`), lo que deja `20.00 - 18.80 = 1.20 mm` de huelga axial dentro del disco de Delrin (`20.00 mm`) para asegurar que la Parte 2 (`Plano 12`) apriete contra el Delrin sin hacer tope rígido metal-metal sobre el vástago.
- **Coherencia del avellanado en Plano Nº 12:** El agujero pasante es `Ø3.50 mm` y el avellanado a `90°` tiene `Ø5.00 mm` y profundidad `0.75 mm`: `(5.00 - 3.50) / (2 * tan(45°)) = 0.75 mm`, por lo que las tres cotas son geométricamente consistentes entre sí.
- **Coherencia de interfaz Parte 1 ↔ Parte 2:** Ambas comparten `Ø21.00 mm` y distribución de 3 agujeros a `120°`.

## 6. Supuestos y dudas (priorizadas)
1. **Longitud saliente del vástago en Parte 1 (`18.80 mm` vs `19.80 mm`):** Se modeló respetando `h_total = 24.80 mm` y `h_brida = 6.00 mm` (`vástago saliente = 18.80 mm`). Si por el contrario el vástago saliente fuera `19.80 mm` (total `25.80 mm`), también quedaría `0.20 mm` bajo la cara del Delrin (`20.00 mm`) permitiendo el apriete de la Parte 2.
2. **Cabeza de los tornillos `M3` en Parte 1 y Parte 2:** Los avellanados de `0.50 mm` (Parte 1) y `0.75 mm` (Parte 2, `Ø5.00 mm`) son pequeños para alojar al ras una cabeza fresada `M3` DIN 7991 (`Ø6.0 mm`, altura `1.7 mm`), por lo que la cabeza sobresaldrá parcialmente o actúa solo como matado de canto para tornillo cilíndrico/gota de sebo.

## 7. Detalles pendientes de modelar
Ninguno: ambas piezas incluyen sus chaflanes de `0.50 x 45°`, avellanados cónicos a `90°` y agujeros roscados/pasantes posicionados paramétricamente.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Sobre-restricción e incoherencia axial (`6.00 + 19.80 != 24.80`) en Plano 11 | Eliminar la cota redundante `19.80` o corregir `h_total` en el plano constructivo para que el tornero no tenga ambigüedad | Alto (evita error de mecanizado) | Nulo | propuesta |
| 2 | Avellanados `Ø4.5 / Ø5.0 mm` insuficientes para ocultar cabezas `M3` estándar DIN 7991 (`Ø6.0 mm`) | Ampliar los avellanados a `90°` hasta `Ø6.3 mm` (prof. `1.4 mm`) si se usan tornillos Allen de cabeza fresada DIN 7991 | Medio (cabezas al ras) | Bajo | propuesta |
| 3 | Posible fuga de fluido entre el vástago `Ø30.00 mm` y el disco de Delrin | Incorporar un o-ring axial en la cara de asiento de la brida de `Ø45 mm` o aplicar sellador anaeróbico/silicona en el montaje | Alto (estanqueidad a través del centro del émbolo) | Bajo | propuesta |
