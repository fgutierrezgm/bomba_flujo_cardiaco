# FICHA DE DISEÑO - Adaptador del retén, sufrideras y sensor pistón (Planos Nº 5a y 5b)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (páginas 54 y 55, correspondientes a los **Planos Nº 5a y 5b - Adaptador del retén y sufrideras**, Escala 2:1):
  - **Plano Nº 5a (pág. 54):**
    1. **Tapa sufridera int (`Tapa_Sufridera_Int_05a`):** vista frontal y `SECTION N-N`.
    2. **Sufridera eje ext. (`Sufridera_Eje_Ext_05a`):** vista frontal y `SECTION P-P`.
  - **Plano Nº 5b (pág. 55):**
    3. **Sufridera int. (`Sufridera_Int_05b`):** vista frontal y `SECTION R-R`.
    4. **Sensor pistón (`Sensor_Piston_05b`):** vista superior y `SECTION T-T`.
    5. **Sufridera guía (`Sufridera_Guia_05b`):** vista frontal y `SECTION U-U`.

## 2. Función y contexto
Conjunto de 5 piezas auxiliares de guiado, retención de sello y detección de posición de carrera:
1. **`Tapa_Sufridera_Int_05a` (`Ø45 x 2.00 mm`):** disco de cierre axial que retiene el retén radial (`14x30x7`) dentro de su alojamiento en `Sufridera_Int_05b`, fijado mediante 4 tornillos M3 de cabeza fresada (`Ø3.00`, avellanado `Ø4.00 x 90°`) sobre círculo de `Ø37.50 mm`. El eje pasa por su agujero central con holgura (`Ø15.10 mm`).
2. **`Sufridera_Eje_Ext_05a` (`Ø40 / Ø18 x 13.00 mm`):** buje/sufridera escalonado que se aloja en las cavidades 3 (`Ø40.10 x 5.00 mm`) y 4 (`Ø18.00 x 8.00 mm`) de la Tapa Exterior (Plano 16a/16b). Fijado por 4 tornillos M3 de cabeza fresada sobre `Ø29.00 mm`. Guía el eje principal en el tramo `Ø12.20 mm` con rebaje `Ø13.10 mm`.
3. **`Sufridera_Int_05b` (`Ø45 x 8.50 mm`):** portarretén ("adaptador del retén") que aloja el retén de labio `14x30x7` en su cavidad de `Ø30.00 x 7.00 mm`. Se vincula por su cara inferior mediante 4 roscas `M3x0.5` sobre `Ø22.50 mm` y recibe en su cara superior a `Tapa_Sufridera_Int_05a` mediante 4 roscas `M3x0.5` sobre `Ø37.50 mm`.
4. **`Sensor_Piston_05b` (`Ø20 x 15.00 mm`, vástago `M8`):** tope metálico ferromagnético/inoxidable (2 unidades por bomba) que se rosca en el émbolo/pistón para activar los sensores inductivos de fin de carrera.
5. **`Sufridera_Guia_05b` (`Ø20 x 3.00 mm`):** arandela/placa de retención con agujero central `Ø10.10 mm` y 4 agujeros pasantes `Ø3.10 mm` sobre `Ø15.00 mm` para fijación asociada a las guías lineales.

## 3. Datos generales
- **Material:**
  - Sufrideras y portarretén (`5a.1`, `5a.2`, `5b.1`, `5b.3`): polímero técnico de bajo rozamiento (PTFE / Delrin POM / Grilón) o bronce/aluminio según interfaz (no indicado en rótulo; en el informe se mencionan sufrideras poliméricas/bronce y adaptador de retén).
  - `Sensor_Piston_05b` (`5b.2`): acero inoxidable (necesario para detección por sensor inductivo y resistencia a la corrosión).
- **Proceso previsto:** torno paralelo/CNC + taladrado/roscado en fresadora.
- **Cantidad:** 1 juego de sufrideras/portarretén por cabezal; **2 unidades** de `Sensor_Piston_05b` por bomba.
- **Tolerancias:** `6g` indicada en la rosca `M8x0.5 - 6g` de `Sensor_Piston_05b`; resto de cotas sin tolerancia explícita (se asume ISO 2768-m).
- **Acabado:** no indicado en los planos 5a y 5b.

## 4. Cotas y elementos

### 4.1 Pieza 5a.1: `Tapa_Sufridera_Int_05a` (Plano Nº 5a)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior (`d_ext`) | `45.00 mm` | plano | alta | Coincide con `d_ext` de `Sufridera_Int_05b` |
| Espesor total (`h_total`) | `2.00 mm` | plano | alta | En `SECTION N-N` |
| Agujero central (`d_int`) | `15.10 mm` | plano | alta | Holgura para paso de eje Ø14/Ø15 |
| Círculo de agujeros (`d_cor`) | `37.50 mm` | plano | alta | 4 agujeros a 0°, 90°, 180°, 270° |
| Agujeros pasantes (`d_aguj`) | `3.00 mm` | plano | alta | Para tornillo M3 (justo sin holgura nominal) |
| Avellanado cónico (`d_avell`, ángulo) | `4.00 mm x 90°` | plano | alta | Profundidad calculada `p_avell = 0.50 mm` |
| Chaflanes (interior y exterior) | `0.50 x 45°` | plano | alta | Indicados en `SECTION N-N` |

### 4.2 Pieza 5a.2: `Sufridera_Eje_Ext_05a` (Plano Nº 5a)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro brida (`d_brida`) | `40.00 mm` | plano | alta | Encastra en Cavidad 3 (`Ø40.10`) de Tapa 16a |
| Espesor brida (`h_brida`) | `5.00 mm` | plano | alta | En `SECTION P-P` (`z = 0..5 mm`) |
| Diámetro vástago (`d_vast`) | `18.00 mm` | plano | alta | Encastra en Cavidad 4 (`Ø18.00`) de Tapa 16a |
| Longitud vástago (`h_vast`) | `8.00 mm` | plano | alta | Largo total `5.00 + 8.00 = 13.00 mm` |
| Agujero lado brida (`d_int_brida`) | `13.10 mm` | plano | alta | Profundidad `5.00 mm` (`z = 0..5 mm`) |
| Agujero pasante vástago (`d_int_vast`) | `12.20 mm` | plano | alta | Pasante en todo el largo |
| Círculo de agujeros (`d_cor`) | `29.00 mm` | plano | alta | 4 agujeros a 0°, 90°, 180°, 270° |
| Agujeros pasantes (`d_aguj`) | `3.50 mm` | plano | alta | Holgura estándar para M3 |
| Avellanado cónico (`d_avell`, ángulo) | `5.00 mm x 90°` | plano | alta | Profundidad calculada `p_avell = 0.75 mm` en cara `z = 0` |
| Chaflanes | `0.50 x 45°` | plano | alta | 4 llamadas en `SECTION P-P` |

### 4.3 Pieza 5b.1: `Sufridera_Int_05b` (Plano Nº 5b)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior (`d_ext`) | `45.00 mm` | plano | alta | |
| Altura total (`h_total`) | `8.50 mm` | plano | alta | En `SECTION R-R` |
| Agujero central (`d_int`) | `15.10 mm` | plano | alta | Pasante |
| Alojamiento de retén (`d_reten`) | `30.00 mm` | plano | alta | Para retén `14x30x7` |
| Profundidad alojamiento (`p_reten`) | `7.00 mm` | plano | alta | Desde cara superior `z = 8.50 mm` |
| Corona exterior 4x M3 (`d_cor_ext`) | `37.50 mm` | plano | alta | Desde cara superior (`z = 8.50 mm`), prof. `5.00 mm` |
| Corona interior 4x M3 (`d_cor_int`) | `22.50 mm` | plano | alta | Desde cara inferior (`z = 0`), prof. indicada `5.00 mm` |
| Rosca (`d_m3`) | `M3x0.5` | plano + norma | alta | Ø nominal `3.00 mm`, mecha `2.50 mm` |
| Chaflanes | `0.50 x 45°` | plano | alta | 3 llamadas en `SECTION R-R` |

### 4.4 Pieza 5b.2: `Sensor_Piston_05b` (Plano Nº 5b)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Rosca vástago (`d_m8`) | `M8x0.5 - 6g` | plano | media | Contradicción con Plano 10 (`M8x1.25 - 6H`) |
| Longitud vástago (`l_vast`) | `8.00 mm` | plano | alta | De `z = 0` a `z = 8.00 mm` |
| Diámetro cabeza (`d_cab`) | `20.00 mm` | plano | alta | |
| Altura cabeza (`h_cab`) | `7.00 mm` | plano | alta | De `z = 8.00` a `z = 15.00 mm` |
| Chaflán cabeza (`c_cab`) | `0.50 x 45°` | plano | alta | En borde superior de la cabeza |

### 4.5 Pieza 5b.3: `Sufridera_Guia_05b` (Plano Nº 5b)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior (`d_ext`) | `20.00 mm` | plano | alta | |
| Espesor total (`h_total`) | `3.00 mm` | plano | alta | En `SECTION U-U` |
| Agujero central (`d_int`) | `10.10 mm` | plano | alta | Pasante |
| Círculo de agujeros (`d_cor`) | `15.00 mm` | plano | alta | 4 agujeros a 0°, 90°, 180°, 270° |
| Agujeros pasantes (`d_aguj`) | `3.10 mm` | plano | alta | En `SECTION U-U` indica `90.0°` sin diámetro de avellanado |
| Chaflanes | `0.50 x 45°` | plano | alta | 2 llamadas en `SECTION U-U` |

## 5. Verificación de coherencia
1. **Acoplamiento `Tapa_Sufridera_Int_05a` ↔ `Sufridera_Int_05b`:** coinciden exactamente el diámetro exterior (`Ø45.00`), el agujero central (`Ø15.10`) y el círculo de 4 agujeros M3 (`Ø37.50 mm`).
2. **Interferencia / perforación del piso en `Sufridera_Int_05b` (hallazgo crítico):**
   - El alojamiento del retén tiene `Ø30.00 mm` y profundidad `7.00 mm` en un cuerpo de `8.50 mm` de altura, dejando un piso de apenas **`1.50 mm` de espesor** entre `Ø15.10` y `Ø30.00 mm`.
   - La corona interior de 4 roscas `M3x0.5` está sobre `Ø22.50 mm` (es decir, **dentro** de la zona del piso de `1.50 mm` bajo el retén), pero el plano acota una profundidad de rosca de `5.00 mm` desde la cara inferior (y en `SECTION R-R` dibuja erróneamente el agujero desplazado hacia la pared gruesa exterior). En la geometría real 3D, estos 4 agujeros atraviesan por completo el piso de `1.50 mm` y salen dentro del alojamiento del retén.
3. **Discrepancia menor de círculo de agujeros `Sufridera_Eje_Ext_05a` ↔ `Tapa_Exterior_16a`:**
   - En `Sufridera_Eje_Ext_05a` (Plano 5a) la corona de 4 agujeros pasantes de `Ø3.50 mm` está acotada a **`Ø29.00 mm`**, mientras que en la `Tapa_Exterior_16a` (Plano 16a) las 4 roscas M3 correspondientes están a **`Ø29.10 mm`** (`0.05 mm` de diferencia radial; absorbibles por la holgura de `Ø3.50 mm` para M3, pero conviene unificar).
   - Además, el vástago `Ø18.00 mm` entra en la Cavidad 4 (`Ø18.00 mm` nominales en Plano 16a) sin holgura nominal declarada.
4. **Contradicción de paso de rosca en `Sensor_Piston_05b` (Plano 5b vs Plano 10):**
   - En el **Plano 5b**, la rosca exterior del vástago de `Sensor_Piston_05b` está acotada como **`M8x0.5 - 6g`** (paso extrafino).
   - En el **Plano 10 (Soporte / Émbolo)**, el agujero roscado receptor está acotado como **`M8x1.25 - 6H`** (paso grueso estándar ISO). Ambas piezas no pueden roscar entre sí si no se unifica el paso a `M8x1.25`.
5. **Avellanado incompleto en `Sufridera_Guia_05b` (Plano 5b):**
   - En `SECTION U-U` se acota el ángulo `90.0°` en los 4 agujeros de `Ø3.10 mm`, pero falta la cota del diámetro mayor del avellanado.

## 6. Supuestos y dudas (máx. 5 dudas, priorizadas)
1. **Paso de rosca de `Sensor_Piston_05b`:** ¿Se confirma unificar a **`M8x1.25`** (paso grueso comercial estándar del Plano 10) descartando el `M8x0.5` del Plano 5b?
2. **Espesor de piso en `Sufridera_Int_05b`:** ¿El espesor bajo el retén (`1.50 mm`) es suficiente para las 4 roscas `M3x0.5` sobre `Ø22.50 mm` (solo 3 filetes útiles), o deben ser agujeros pasantes en `Sufridera_Int_05b` y roscar en la pieza contigua?
3. **Corona `Ø29.00` (Plano 5a) vs `Ø29.10` (Plano 16a):** ¿Cuál de los dos valores nominales manda para el círculo de fijación de `Sufridera_Eje_Ext_05a`?
4. **Avellanado en `Sufridera_Guia_05b`:** ¿Los 4 agujeros de `Ø3.10 mm` llevan avellanado (p. ej. `Ø5.00 x 90°`) o son cilíndricos rectos?

## 7. Detalles pendientes de modelar
- Chaflanes menores de borde `.50 x 45°` en las sufrideras `5a.1`, `5a.2`, `5b.1` y `5b.3` (en `Sensor_Piston_05b` sí se modela el chaflán `.50 x 45°` con `cono`).
- Avellanado de `Sufridera_Guia_05b` (sin diámetro acotado en el plano; se modela el agujero pasante `Ø3.10 mm`).

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Contradicción de rosca `M8x0.5` (Plano 5b) vs `M8x1.25` (Plano 10) en `Sensor_Piston_05b` | Unificar a **`M8x1.25`** (paso grueso estándar IRAM/ISO), evitando machos e hilleras especiales de paso 0.5 mm | Crítico (ensamblabilidad y costo) | Bajo | propuesta |
| 2 | En `Sufridera_Int_05b`, las roscas `M3x0.5` sobre `Ø22.50` solo tienen `1.50 mm` de pared (3 filetes) y perforan el asiento del retén | Hacer pasantes de `Ø3.40 mm` los agujeros en `Ø22.50` con cabeza fresada desde el interior del alojamiento antes de montar el retén, o aumentar la altura total de `8.50` a `11.50 mm` si el espacio axial lo permite | Alto (resistencia de rosca y protección del retén) | Medio | propuesta |
| 3 | En `Tapa_Sufridera_Int_05a`, el agujero `Ø3.00` con avellanado `Ø4.00` es chico para tornillos estándar DIN 7991 / ISO 10642 M3 (cabeza `Ø6.0 mm`) | Pasar agujero a `Ø3.40 mm` y avellanado a `Ø6.00 x 90°` (o usar espesor `3.00 mm`) para que la cabeza M3 quede al ras | Medio (uso de bulonería estándar sin retocar cabezas) | Bajo | propuesta |
| 4 | Falta ranura o ranuras de sujeción para llave en `Sensor_Piston_05b` (`Ø20` liso) | Agregar dos planos paralelos entre caras (`SW 17 mm`) o hexágono Allen en la cara superior para poder apretarlo contra el pistón | Medio (facilidad de montaje) | Bajo | propuesta |
| 5 | En el prototipo impreso 3D (`Escala 0.755`), colocar `Sufridera_Guia_05b_3D` (`Ø15.10 mm`) del lado superior (`+Z`) sobre el rebaje `Ø13.59 mm` de `Tapa_Interior_16b_3D` es innecesario y las aristas de `Tuerca_Guia_08_3D` (`e = 15.01 mm`) dañarían el plástico de la tapa al ajustar | Conservar **2× `Sufridera_Guia_05b_3D`** únicamente en los bolsillos inferiores (`-Z`, lado cámara, fijadas con 8× M2×5) y añadir **2× `Arandela_Guia_08_3D`** (`Ø13.59 × Ø7.20 × 4.00 mm`, impresa en 3D) alojadas en los rebajes superiores `Ø13.59 × 1.744 mm` (`+Z`) sobresaliendo `2.256 mm` como asiento de las tuercas | Alto (protege la tapa al ajustar las tuercas de guía y simplifica el montaje) | Bajo | aceptada (implementada en `generar_arandela_guia_08_3d.py` y `Piloto_Impresion_3D_Assembly.FCStd`) |
| 6 | Al unificar la espiga inferior de `Tornillo_Sin_Fin_14_3D` a **`Ø8.80 mm`** (Opción 2), el paso original escalonado de `Sufridera_Eje_Ext_05a_3D` (`Ø10.22 / Ø9.46 mm` CAD) quedaba con juego radial excesivo (~0.70 mm en radio) | Rellenar el escalonado previo y mecanizar/modelar en `Sufridera_Eje_Ext_05a_3D` un agujero pasante uniforme **`Ø9.20 mm` CAD** (`d_eje_punta = 8.80 mm` + `2 × holgura_fdm 0.20 mm`), conservando íntegras las cotas exteriores (`Ø30.20 / Ø13.59 mm`) que encastran en `Tapa_Exterior_16a_3D` | Alto (centra la punta del sinfín `Ø8.80 mm` sin modificar la tapa exterior ya impresa; repasar con mecha Ø9.0–9.2 mm si la contracción FDM supera 0.20 mm) | Bajo | aceptada (implementada en `importar_modelo_3d_steps.py`) |
| 7 | Faltaban los 2 pequeños O-rings de estanqueidad sobre las barras guía (`Guia_1_08_3D` / `Guia_2_08_3D`, `Ø6.71 mm`) entre cada `Sufridera_Guia_05b_3D` inferior y los bolsillos ya impresos (`Ø15.50`, techo `Z = 13.70 mm`) de `Tapa_Interior_16b_3D` | Incorporar `2× ORing_6_0x1_5` (`Ø6.00 × cuerda 1.50 mm`, `OD 9.00 mm` NBR 70, `ORing_Guia_1` y `ORing_Guia_2`) centrados a `Z = 13.07 mm` en `(±28.31, 0)` y mecanizar en la cara superior (`+Z`) de `Sufridera_Guia_05b_3D` un escalón cilíndrico paramétrico **`Ø8.90 × prof. 1.15 mm`** (`Z_local = 1.115..2.265`, piso `Z_mundo = 12.445 mm`), generando una cámara axial de `1.255 mm` (`16.3%` de aplastamiento) libre de los 4 tornillos `M2×5` (`R_min = 4.79 > 4.50 mm`) y sin modificar `Tapa_Interior_16b_3D` | Crítico (estanqueidad de cámara sobre las 2 barras guía con tapa ya impresa) | Bajo | aceptada (implementada en `importar_modelo_3d_steps.py`, `generar_tornilleria_comercial.py` y `Piloto_Impresion_3D_Assembly.FCStd`) |

