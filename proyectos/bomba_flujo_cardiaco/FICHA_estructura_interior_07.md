# FICHA DE DISEÑO - Estructura interior (Plano Nº 7)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (página 57, correspondiente al **Plano Nº 7 - Estructura interior**, Escala 1:1, con vista frontal, `SECTION B-B` y `SECTION C-C`).
- Datos del proyecto: **2 placas cuadradas de aluminio** (`183.00 x 183.00 mm`) que sostienen las tapas/carcasas de las cámaras y se vinculan a los 4 tensores de esquina (`Tensor_06`).

## 2. Función y contexto
Placas estructurales portantes (2 unidades por bomba) de perfil cuadrado `183.00 x 183.00 mm` y espesor base `20.00 mm` (con un resalte frontal de `2.10 mm` hasta `22.10 mm` totales). En su abertura central escalonada (`R72.55 = Ø145.10 mm` pasante y rebaje `R80.25 = Ø160.50 mm` x `12.50 mm` de profundidad) alojan y centran las tapas exteriores (Planos 16a y 16b, que tienen encastre `Ø145.00` y brida `Ø160.00 mm`). Se vinculan a los 4 tensores de `Ø22.00 mm` en las esquinas.

## 3. Datos generales
Material: Aluminio | Proceso previsto: fresado CNC / pantógrafo + torneado o interpolación circular de alojamientos centrales | Cantidad: 2 | Tolerancias: no indicadas en plano (holguras funcionales dadas por cotas nominales: `Ø145.10` para encastre `Ø145.00` y `Ø160.50` para brida `Ø160.00`) | Acabado: mecanizado estándar.

## 4. Cotas y elementos
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Lado de la placa cuadrada (`lado`) | `183.00 mm` | plano | alta | Cuadrado de `183.00 x 183.00 mm` |
| Espesor base de la placa (`h_base`) | `20.00 mm` | plano | alta | En `SECTION B-B` (`z = 0..20.00 mm`) |
| Altura del resalte frontal (`h_res`) | `2.10 mm` | calculado | alta | De `22.10 mm` (`SECTION C-C`) - `20.00 mm` (`SECTION B-B`) |
| Radio exterior del resalte (`r_res_ext`) | `101.82 mm` | plano | alta | Recortado por los lados del cuadrado `183 x 183` |
| Radio interior del resalte (`r_res_int`) | `84.63 mm` | plano | alta | Define el escalón frontal del resalte |
| Radio agujero central pasante (`r_int`) | `72.55 mm` | plano | alta | `Ø145.10 mm` (encastre `Ø145.00` de Tapas 16a/16b) |
| Radio escalón/rebaje interior (`r_esc`) | `80.25 mm` | plano | alta | `Ø160.50 mm` (aloja brida `Ø160.00` de Tapas 16a/16b) |
| Profundidad escalón interior (`p_esc`) | `12.50 mm` | plano | alta | En `SECTION B-B` (medido desde `z = 0`) |
| Radio de posición 4 agujeros pasantes (`r_aguj`) | `76.27 mm` | plano | alta | `Ø152.54 mm` (coincide con corona `Ø152.50` de Tapas 16a/16b) |
| Diámetro 4 agujeros pasantes (`d_aguj`) | `3.50 mm` | plano | alta | A 0°, 90°, 180°, 270° (para tornillos M3 hacia las tapas) |
| Radio de posición 4 roscas M5 (`r_m5`) | `84.63 mm` | plano | alta | `Ø169.26 mm`, a 45°, 135°, 225°, 315° |
| Roscas axiales (`d_m5`) | `M5x0.8` | plano + norma | alta | Ø nominal `5.00 mm`, mecha `4.20 mm` |
| Posición X/Y centros de tensores (`pos_tensor`) | `69.00 mm` | supuesto | media | En `x = ±69.00`, `y = ±69.00` (`r = 97.58 mm`), no acotado en el plano |
| Diámetro alojamiento de tensores (`d_aloj_tensor`) | `22.00 mm` | supuesto | media | En `SECTION C-C` se ve el alojamiento para el tensor `Ø22.00` sin cota de Ø |
| Chaflanes | `.25x45°`, `.50x45°`, `1.00x45°` | plano | alta | En bordes exteriores, rebaje central y alojamientos de esquina |

## 5. Verificación de coherencia
1. **Acoplamiento con Tapas Exteriores (Planos 16a y 16b):**
   - El agujero central `2 x 72.55 = Ø145.10 mm` recibe con `0.10 mm` de juego diametral al resalte `Ø145.00 mm` de las Tapas 16a/16b.
   - El rebaje `2 x 80.25 = Ø160.50 mm` recibe con `0.50 mm` de juego diametral a la brida exterior `Ø160.00 mm` de las Tapas 16a/16b.
   - Los 4 agujeros `Ø3.50 mm` sobre `2 x 76.27 = Ø152.54 mm` a 0°/90°/180°/270° coinciden con la corona exterior de 4 roscas `M3x0.5` sobre `Ø152.50 mm` de las Tapas 16a/16b (`0.02 mm` de diferencia radial).
2. **Omisión de cotas en los 4 alojamientos de esquina para los tensores (hallazgo crítico):**
   - El Plano Nº 7 dibuja los 4 alojamientos en las esquinas y muestra el corte de uno de ellos en `SECTION C-C`, pero **omite acotar la distancia entre centros (X, Y) y los diámetros** de dichos alojamientos.
   - En la vista frontal, el círculo `R101.82` (`Ø203.64 mm`) pasa por el contorno de los alojamientos de esquina. Con centros en `x = ±69.00 mm, y = ±69.00 mm` (distancia entre centros `138.00 mm`), el radio al centro del tensor es $\sqrt{69^2 + 69^2} = 97.58\,\text{mm}$. Ambos parámetros (`pos_tensor = 69.00 mm` y `d_aloj_tensor = 22.00 mm`) se declaran explícitamente con origen `supuesto` en la hoja `Parametros`.
3. **Cota angular `35.0°` y `45.0°` en vista frontal:**
   - Las 4 roscas `M5x0.8` están simétricamente dispuestas a `45°` de los ejes principales (45°, 135°, 225°, 315°). En el primer cuadrante aparece una segunda cota angular `35.0°` apuntando a una línea auxiliar sin agujero asociado (remanente de construcción del croquis original).

## 6. Supuestos y dudas (máx. 5 dudas, priorizadas)
1. **Posición de los 4 tensores (`pos_tensor`):** ¿Cuál es la distancia exacta entre centros de los 4 agujeros de esquina (estimada en `138.00 mm`, es decir `±69.00 mm` respecto del centro)?
2. **Geometría de los alojamientos de esquina (`SECTION C-C`):** ¿Las dos placas `Estructura_Interior_07` deslizan sobre el diámetro exterior de los tensores (`Ø22.00 mm` pasante) o tienen un alojamiento ciego de `Ø22.00 mm` con agujero pasante de `Ø10.50 mm` para bulón `M10x1.5` en los extremos del tensor?
3. **Profundidad de las 4 roscas `M5x0.8`:** El plano no indica si son pasantes o ciegas (se modelan pasantes en el espesor de la placa).

## 7. Detalles pendientes de modelar
Chaflanes menores `.25 x 45°`, `.50 x 45°` y `1.00 x 45°` indicados en las vistas de sección.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Faltan en el Plano Nº 7 las cotas de posición (X/Y) y diámetro de los 4 alojamientos de los tensores | Acotar explícitamente en el plano la distancia entre centros (p. ej. `138.00 ± 0.10 mm`) y el detalle del alojamiento (`Ø22.10` / `Ø10.50`) | Crítico (sin estas cotas no se puede fabricar la pieza ni garantizar alineación con otras placas) | Bajo | propuesta |
| 2 | La fijación de la Tapa Exterior (`Ø160 mm`, sometida a la presión pulsante de la cámara) a la Estructura Interior se hace solo con 4 tornillos `M3x0.5` sobre `Ø152.50 mm` | Subir los 4 tornillos de fijación de tapa de `M3` a **`M5` o `M6`** (hay espesor de sobra tanto en la placa como en la brida de la tapa) | Alto (seguridad estructural frente a fatiga y presión hidráulica) | Bajo | propuesta |
| 3 | El resalte frontal de `2.10 mm` obliga a desbastar `2.10 mm` en casi toda la superficie de una placa de `22.10 mm` (o partir de placa de `25 mm`) | Partir de **placa comercial laminada de aluminio de `20.00 mm` (`3/4"`)** sin el resalte de `2.10 mm`, compensando los `2.10 mm` en el separador o en la profundidad del rebaje | Alto (ahorro de material y ~40% del tiempo de fresado) | Medio | propuesta |
