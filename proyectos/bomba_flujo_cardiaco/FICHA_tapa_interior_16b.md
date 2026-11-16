# FICHA DE DISEÑO - Tapa interior (Plano Nº 16b)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, revisada contra legajo FCAI-UNCuyo

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 6, 9, 13, 14, 20, 23, 25 y pág. 67 - Plano Nº 16b `Tapa interior`, Escala 1:1.2, vista frontal interna, vista lateral, vista posterior, Sección AE-AE y Detalle AF Escala 2:1).
- `proyectos/bomba_flujo_cardiaco/piezas/generar_tapa_exterior_16a.py` y `FICHA_tapa_exterior_16a.md` (convención de coordenadas y estructura de referencia).

## 2. Función y contexto
Tapa/cabezal interior de la cámara de bombeo (lado motor/transmisión, `x = 0 mm` de la carrera del émbolo). Cumple simultáneamente cinco funciones críticas:
1. **Cierre y asiento del cilindro de vidrio (Plano 9):** aloja el extremo izquierdo del tubo de borosilicato (`Øext 110.50 mm`) en la cavidad `Ø110.50 x 8.10 mm` (`z = 15.00..23.10 mm`) y la junta tórica estática NBR70 (`110.49 x 5.33 mm`) en la cavidad `Ø120.10 x 6.90 mm` (`z = 23.10..30.00 mm`), comprimida por el `Anillo tórica` (Plano 13).
2. **Paso y sellado del eje/husillo central:** posee el pasaje central `Ø15.00 mm` para el `Tornillo sin fin` (`M14x2`, Plano 14) y el alojamiento escalonado trasero (`Ø45.10 x 2.31 mm` y `Ø41.00 x 9.69 mm`, Detalle AF) que recibe la `Sufridera int.` (Plano 5b con el retén radial `14 x 30 x 7 mm`) y su tapa (`Tapa sufridera int`, Plano 5a), más las 4 roscas `M3x0.5 ↧ 7.00` sobre `Ø50.02 mm` donde se fija el `Adaptador del eje` de Delrin (Plano 4).
3. **Soporte y sellado de las 2 barras guía (Plano 8):** a 0° y 180° sobre el círculo `Ø75.00 mm` presenta dos agujeros pasantes de `Ø10.10 mm` (por donde pasan los extremos rebajados `Ø10.00 x 30.00 mm` de las guías) y dos cajeados internos de `Ø20.10 x 6.00 mm` (donde se alojan las juntas tóricas de `10 x 3 mm` y se embuten las `Sufrideras guía` de `Ø20.00 x 3.00 mm` del Plano 5b, fijadas al fondo del cajeado mediante 4 roscas `M3x0.5 ↧ 4.00` sobre `Ø15.00 mm`).
4. **Conexión hidráulica de la cámara interior:** 2 puertos roscados `G 1/8` (`↧ 8.00 mm`) a 90° y 270° sobre `Ø75.00 mm` para impulsión/aspiración y purga.
5. **Detección inductiva de fin de carrera interior (`PIN_FC_INT`):** 1 puerto roscado `M12x1` a 45° sobre `Ø75.00 mm` para el sensor inductivo `LJ12A3-4-Z/BX` que detecta el tope de acero inoxidable del pistón (`x = 0 mm`).

## 3. Datos generales
Material: PVC rígido (mecanizado; PLA en prototipo FDM) | Proceso previsto: Torneado CNC + centro de mecanizado (fresado y roscado en ambas caras) | Cantidad: 1 unidad | Tolerancias: ajustes de estanqueidad en alojamientos | Acabado: mecanizado fino en asientos de tóricas

## 4. Cotas y elementos
| Elemento | Valor | Origen (plano/usuario/norma/calculado/supuesto) | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior brida (`d_ext`) | 160.00 mm | plano | alta | Altura base `h_base = 25.50 mm` (`z = 0..25.50 mm`) |
| Resalte de encastre (`d_enc` x `h_enc`) | Ø145.00 x 4.50 mm | plano | alta | Z total `25.50 + 4.50 = 30.00 mm` |
| Cavidad 1 tórica cilindro (`d_cav1` x `p_cav1`) | Ø120.10 x 6.90 mm | plano | alta | Desde `z = 30.00` hasta `23.10 mm` |
| Cavidad 2 asiento tubo (`d_cav2` x `p_cav2`) | Ø110.50 x 8.10 mm | plano | alta | Desde `z = 23.10` hasta `z_piso2 = 15.00 mm` |
| Cota central `d_cav3` / `p_cav3` (Detalle AF) | Ø40.00 / 3.00 mm | plano | alta | Ver análisis de coherencia en Sección 5 (`z = 12.00..15.00 mm`) |
| Agujero central pasante (`d_paso_central`) | 15.00 mm | plano | alta | Paso libre para el husillo `M14x2` |
| Rebaje trasero 1 (`d_reb1` x `p_reb1`) | Ø45.10 x 2.31 mm | plano | alta | Detalle AF, desde `z = 0` hasta `2.31 mm` (aloja `Tapa sufridera int` Ø45x2) |
| Rebaje trasero 2 (`d_reb2` x `p_reb2`) | Ø41.00 x 9.69 mm | plano | alta | Detalle AF, desde `z = 2.31` hasta `12.00 mm` (prof. acumulada `12.00 mm`) |
| Círculo de guías y puertos (`d_c75`) | 75.00 mm | plano | alta | Común a guías (0°/180°), puertos G 1/8 (90°/270°) y M12x1 (45°) |
| Agujero pasante de guías (`d_guia_paso`) | 10.10 mm | plano | alta | 2x a 0° y 180° sobre `Ø75.00 mm` (recibe espiga `Ø10.00` de Guía 8) |
| Cajeado interno de guías (`d_caj_guia` x `p_caj_guia`) | Ø20.10 x 6.00 mm | plano | alta | Desde `z = 15.00` hasta `9.00 mm` (Plano original Gallardo pág. 40; aloja tórica `10x3` + `Sufridera guía` Ø20x3) |
| Roscas de sufridera guía (`d_cor_guia` / `p_m3_guia`) | 4x M3x0.5 (↧ 4.00) en Ø15.00 | plano | alta | En el fondo del cajeado (`z = 9.00..5.00 mm`), coincidente con `Sufridera guía` (Plano 5b) |
| Puertos hidráulicos (`d_g18` x `p_g18`) | 2x G 1/8 (Ø9.73, mecha 8.80) x 8.00 mm | plano | alta | Desde cara trasera `z = 0` a 90° y 270° sobre `Ø75.00 mm` |
| Pasaje interno bajo G 1/8 (`d_pasaje_g18`) | 4.00 mm | supuesto | baja | Conecta el fondo del puerto G 1/8 con la cámara (`z = 15.00 mm`), igual que en 16a |
| Puerto sensor inductivo (`d_m12` / `ang_m12`) | M12x1 (Ø12.00, mecha 11.00) a 45° | plano | alta | Pasante hasta cámara sobre `Ø75.00 mm` |
| Corona exterior (`d_cor_ext` / `p_m3_ext`) | 6x M3x0.5 (↧ 6.00) en Ø152.50 | plano | alta | Desde cara de escalón `z = 25.50 mm` |
| Corona media (`d_cor_med` / `p_m3_med`) | 6x M3x0.5 (↧ 4.00) en Ø130.00 | plano | alta | Desde tope `z = 30.00 mm` (fija `Anillo tórica` Plano 13) |
| Corona trasera (`d_cor_tras` / `p_m3_tras`) | 4x M3x0.5 (↧ 7.00) en Ø50.02 | plano | alta | Desde cara trasera `z = 0` a 45°/135°/225°/315° (fija `Adaptador del eje` Plano 4) |

## 5. Verificación de coherencia
- **Cadena axial de profundidades y espesores (Sección AE-AE y Detalle AF):**
  - Altura total: `h_base (25.50) + h_enc (4.50) = 30.00 mm`.
  - Desde la cara interna (`z = 30.00 mm`) hasta el piso de la cámara: `p_cav1 (6.90) + p_cav2 (8.10) = 15.00 mm`, quedando el piso de la cámara en `z_piso2 = 30.00 - 15.00 = 15.00 mm` (coincidente con la cota `15.00` de la Sección AE-AE).
  - En el Detalle AF (`z = 0` a `15.00 mm`): la suma de las tres cotas verticales es `2.31 + 9.69 + 3.00 = 15.00 mm`.
  - **Observación crítica sobre `3.00 mm`, `Ø40.00 mm` y `Ø15.00 mm` en Detalle AF:** En el Detalle AF, los rebajes traseros (`p_reb1 = 2.31 mm` a `Ø45.10 mm` y `p_reb2 = 9.69 mm` a `Ø41.00 mm`) suman `12.00 mm` desde `z = 0` (`z = 0..12.00 mm`), y los `3.00 mm` superiores (`z = 12.00..15.00 mm`) corresponden al **espesor del tabique central** atravesado por el agujero `d_paso_central = Ø15.00 mm` (con chaflanes `0.50 x 45°` en ambas caras del tabique; además el chaflán de `0.50 x 45°` en el borde de `Ø41.00 mm` proyecta el círculo de `41.00 - 2*0.50 = Ø40.00 mm` acotado en la vista posterior). Si se cortara una cavidad pasante de `Ø40.00 mm` con `3.00 mm` de profundidad desde `z = 15.00 mm` hasta `z = 12.00 mm`, se uniría con el rebaje trasero de `Ø41.00 mm` (`z = 0..12.00 mm`), **eliminando por completo el tabique central y haciendo desaparecer el agujero `Ø15.00 mm`**. Por ello, en el script se conserva el tabique central (`z = 12.00..15.00 mm`) con su agujero `Ø15.00 mm`, modelando el escalón `Ø40.00 mm` (`d_cav3`) como un rebaje superficial de `0.50 mm` desde el piso de cámara para preservar íntegramente tanto el tabique central `Ø15.00 mm` como la referencia paramétrica `d_cav3`/`p_cav3`.
- **Resolución de la discrepancia entre el plano redibujado (pág. 67) y el plano original de tesis (pág. 40) en el alojamiento de guías:**
  - En el plano redibujado FCAI-UNCuyo (pág. 67), se transcribió por error un cajeado de `Ø18.00 mm` y los 4 agujeros `M3x0.5` fuera del hueco sobre `Ø21.10 mm`.
  - Contrastando con el plano original de la tesis (pág. 40 y Figura 10 de pág. 17) y con la `Sufridera guía` (Plano 5b, `Øext = 20.00 mm`, espesor `3.00 mm`, 4 agujeros en `Ø15.00 mm`), el cajeado real es de **`Ø20.10 x 6.00 mm`** (`z = 9.00..15.00 mm`, alojando los `3.00 mm` de la tórica `10 x 3 mm` en el fondo y los `3.00 mm` de la `Sufridera guía` al ras del piso de cámara `z = 15.00 mm`), y las 4 roscas `M3x0.5 ↧ 4.00 mm` se perforan en el **fondo del cajeado** (`z = 9.00..5.00 mm`) sobre una corona de **`Ø15.00 mm`**.
- **Incoherencia en el rebaje trasero `Ø41.00 mm` vs. `Sufridera int.` (Plano 5b):** La `Sufridera int.` (Plano 5b) tiene cuerpo de `Ø37.50 mm` y brida de `Ø45.00 x 1.50 mm` (largo total `8.50 mm`, más `2.00 mm` de la `Tapa sufridera int` = `10.50 mm` frente a los `12.00 mm` de profundidad total en la Tapa 16b), y sus 4 agujeros M3 están sobre `Ø22.50 mm` y `Ø37.50 mm`.

## 6. Supuestos y dudas (máx. 5 dudas, priorizadas)
1. **Incompatibilidad entre `Sufridera guía` (Plano 5b, `d_cor = 15.00 mm`, `Øext = 20.00 mm`) y `Tapa interior` (Plano 16b, `d_caj = 18.00 mm`, `d_cor_guia = 21.10 mm`):** ¿Se reduce el cajeado de la tórica `10 x 3 mm` a `Ø16.00 x 2.40 mm` y se agranda la `Sufridera guía` a `Øext = 26.00 mm` con `d_cor = 21.10 mm`?
2. **Diámetro del pasaje bajo los puertos `G 1/8` (`d_pasaje_g18`):** Al igual que en el Plano 16a, la vista en corte muestra un conducto de menor diámetro entre el fondo de la rosca `G 1/8` (`z = 8.00 mm`) y el piso de la cámara (`z = 15.00 mm`) sin acotar su diámetro. Se adopta `d_pasaje_g18 = 4.00 mm` (`supuesto`, consistente con 16a).
3. **Orientación angular de la corona trasera `Ø50.02 mm` (4x M3x0.5 ↧ 7.00):** En la vista posterior se observan a `45°, 135°, 225°, 315°` (coincidiendo con los 4 agujeros pasantes o roscados del `Adaptador del eje`, Plano 4).

## 7. Detalles pendientes de modelar
- Chaflanes `0.50 x 45°` indicados en la vista lateral y en el Detalle AF.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado (propuesta/aceptada/descartada) |
|---|---|---|---|---|---|
| 1 | Los 4 agujeros M3 de `d_cor_guia = 21.10 mm` no coinciden con los agujeros de la `Sufridera guía` (`Ø15.00 mm`, Plano 5b) y dejan solo `0.30 mm` de pared respecto del cajeado `Ø18.00 mm` | Redimensionar el alojamiento de la tórica `10 x 3 mm` a `Ø16.00 x 2.40 mm` (compresión axial del 20%) y llevar la `Sufridera guía` a `Øext = 27.00 mm` con corona `Ø21.10 mm` | Permite montar las sufrideras de guía y sella correctamente las barras `Ø12 h7` | Medio | propuesta |
| 2 | El cajeado de guía `Ø18.00 x 6.00 mm` es demasiado profundo (`6.00 mm`) para una tórica de sección `3.00 mm` (la tórica queda suelta sin comprimir) | Reducir la profundidad del alojamiento de la tórica a `2.40 mm` o suplementar con un anillo separador de `3.60 mm` | Garantiza la estanqueidad en el paso de las guías | Bajo | propuesta |
| 3 | Tabique central de PVC de solo `3.00 mm` de espesor (`z = 12.00..15.00 mm`) soporta la reacción del retén y del soporte del eje | Aumentar el espesor del tabique central a `4.50 mm` ajustando la profundidad del rebaje trasero a la altura real de `Sufridera int.` + `Tapa sufridera int` (`8.50 + 2.00 = 10.50 mm`) | Elimina el juego axial de `1.50 mm` de la sufridera y refuerza el tabique central | Bajo | propuesta |
| 4 | En el prototipo 3D (`Tapa_Interior_16b_3D`), al apretar `Tuerca_Guia_08_3D` (`e = 15.01 mm`) del lado `+Z`, sus vértices rozarían la cara superior de la tapa alrededor del rebaje `Ø13.59 × 1.744 mm` | Reemplazar las sufrideras superiores por **2× `Arandela_Guia_08_3D`** (`Ø13.59 × Ø7.20 × 4.00 mm`, `13.19 × 7.60 mm` con holgura FDM) que calzan en el rebaje `Ø13.59 mm` y sobresalen `2.256 mm` sobre la tapa | Protege la superficie impresa de `Tapa_Interior_16b_3D` durante el ajuste de las guías | Bajo | aceptada (implementada) |

