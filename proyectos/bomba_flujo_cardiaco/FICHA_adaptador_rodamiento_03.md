# FICHA DE DISEÑO - Adaptador de rodamiento (Plano Nº 3)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 52, **Plano Nº 3 - Adaptador de rodamiento**, Escala 2:1):
  - Vista frontal (lado brida), vista lateral derecha, vista posterior (lado alojamiento de rodamiento) y **Sección J-J** (Escala 2:1).
- Catálogo SKF / norma DIN 625: rodamiento rígido de bolas **SKF 6201** (`d = 12 mm`, `D = 32 mm`, `B = 10 mm`).

## 2. Función y contexto
Portarrodamiento bridado que aloja el rodamiento rígido de bolas **SKF 6201 (`12x32x10 mm`)** encargado de soportar radial y axialmente al `Transmisor_2_02b` (Plano Nº 2b). Su escalón exterior de `Ø40.00 mm` encastra dentro del diámetro interior `Ø40.10 mm` del Adaptador del eje (Plano Nº 4), y su brida de `Ø55.00 mm` se fija mediante 4 tornillos pasantes M3 sobre una corona de `Ø49.00 mm`.

## 3. Datos generales
Material: Latón / Acero inoxidable (según especificación del subconjunto de transmisión) | Proceso previsto: Torneado paralelo/CNC + taladrado en fresadora/centro de mecanizado | Cantidad: 1 | Tolerancias: no indicadas en plano | Acabado: no indicado en plano (requiere $R_a \le 1.6\,\mu\text{m}$ en asiento de rodamiento `Ø32.00`).

## 4. Cotas y elementos
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Altura total (`h_total`) | `25.50 mm` | plano | alta | En vista lateral y Sección J-J |
| Diámetro exterior brida (`d_brida`) | `Ø55.00 mm` | plano | alta | Tipo `L` |
| Espesor de brida (`h_brida`) | `5.00 mm` | plano | alta | Cota `5` en vista lateral |
| Diámetro escalón intermedio (`d_cuerpo1`) | `Ø40.00 mm` | plano | alta | Tipo `S`; encastra en `Ø40.10` del Adaptador del eje (Plano Nº 4) |
| Cota axial fin de escalón Ø40 (`z_ref_882`) | `8.82 mm` | plano | alta | Desde `z = 0` (`3.82 mm` sobre la brida) |
| Cota axial inicio cuerpo Ø37.50 (`z_esc`) | `11.68 mm` | plano | alta | Entre `8.82` y `11.68 mm` el plano dibuja una garganta cuyo Ø de fondo no está acotado |
| Diámetro cuerpo superior (`d_cuerpo2`) | `Ø37.50 mm` | plano | alta | Tipo `S`; tramo desde `z = 11.68` hasta `25.50 mm` |
| Agujero central pasante (`d_paso`) | `Ø16.00 mm` (`Ø13.10 mm` en plano original) | usuario | alta | Ampliado a `Ø16.00 mm` para dar holgura radial ($0.50\,\text{mm}$) al collar de `Ø15.00 mm` del `Transmisor_2_02b` |
| Diámetro alojamiento rodamiento (`d_aloj_rod`) | `Ø32.00 mm` | plano | alta | Tipo `H`; para aro exterior de rodamiento SKF 6201 (`D = 32 mm`) |
| Profundidad alojamiento rodamiento (`p_aloj_rod`) | `10.50 mm` | plano | alta | Para ancho `B = 10 mm` del 6201 (ver nota de coherencia en sección 5) |
| Diámetro rebaje bajo rodamiento (`d_rebaje`) | `Ø16.00 mm` (`Ø15.00 mm` en plano original) | usuario | alta | Ampliado a `Ø16.00 mm` para unificar el paso libre y evitar fricción parásita con collar Ø15 |
| Profundidad rebaje bajo rodamiento (`p_rebaje`) | `5.00 mm` | plano | alta | En Sección J-J |
| Círculo de agujeros de brida (`d_cor`) | `Ø49.00 mm` | plano | alta | 4 agujeros a `0°, 90°, 180°, 270°` (ver discrepancia con Plano Nº 4 en sección 5) |
| Diámetro agujeros de brida (`d_aguj`) | `Ø3.10 mm` | plano | alta | Tipo `H`; paso para tornillos M3 |
| Avellanado agujeros de brida (`d_avell`, `p_avell`) | `Ø4.00 mm`, `0.45 mm` a `90°` | plano | alta | En cara inferior de la brida (`(4.00 - 3.10)/2 = 0.45 mm` a `45°` por lado) |
| Chaflanes (`c_chaf`) | `0.50 x 45°` | plano | alta | 4 indicaciones `.50 X 45.0°` (3 exteriores y 1 en boca del alojamiento `Ø32.00`) |

## 5. Verificación de coherencia
- **Incoherencia crítica entre planos (Plano Nº 3 vs Plano Nº 4 — círculo de agujeros `Ø49.00` vs `Ø50.00`):**
  - El escalón exterior `Ø40.00 mm` del Adaptador de rodamiento (Plano Nº 3) encastra en el agujero interior `Ø40.10 mm` del Adaptador del eje (Plano Nº 4).
  - Sin embargo, los 4 agujeros pasantes de `Ø3.10 mm` en el **Plano Nº 3** están acotados sobre un círculo de **`Ø49.00 mm`**, mientras que los 4 agujeros pasantes de `Ø3.10 mm` (y las 4 roscas `M3x0.5`) en el **Plano Nº 4** están acotados sobre un círculo de **`Ø50.00 mm`**.
  - Esto produce una desalineación radial de `0.50 mm` en cada agujero (`(50.00 - 49.00)/2 = 0.50 mm`), impidiendo que pasen los tornillos M3 (`Ø3.00 mm` en agujeros de `Ø3.10 mm`, que solo admiten `0.05 mm` de error radial).
- **Acotación en Sección J-J (`10.50` y `5.00` respecto de `25.50`):**
  - En la Sección J-J, las líneas de referencia de `5.00`, `10.50` y `25.50` arrancan visualmente desde la cara inferior (`z = 0`). Si se leyeran como coordenadas acumuladas desde `z = 0`, el alojamiento de `Ø32.00 mm` tendría `25.50 - 10.50 = 15.00 mm` de profundidad y el rebaje de `Ø15.00 mm` tendría `10.50 - 5.00 = 5.50 mm`.
  - No obstante, el rodamiento estándar **SKF 6201** mide `12 x 32 x 10 mm` (`B = 10.00 mm`), por lo que funcionalmente `p_aloj_rod = 10.50 mm` es la profundidad del alojamiento del rodamiento medida desde la cara superior (`z = 25.50 mm`), y `p_rebaje = 5.00 mm` es la profundidad del rebaje de `Ø15.00 mm` bajo dicho asiento, quedando `25.50 - 10.50 - 5.00 = 10.00 mm` de longitud para el agujero central de `Ø13.10 mm`. Así se ha modelado paramétricamente.
- **Garganta exterior sin diámetro acotado entre `z = 8.82 mm` y `z = 11.68 mm`:**
  - En la vista lateral se acotan las alturas axiales `5`, `8.82`, `11.68` y `25.50`, mostrando una garganta/entalla entre `8.82` y `11.68 mm` cuyo diámetro de fondo no figura en ninguna vista. En el modelo base se extiende el escalón `d_cuerpo1 = 40.00 mm` hasta `z_esc = 11.68 mm` (guardando `z_ref_882 = 8.82 mm` en `Parametros`).
- **Coherencia del avellanado:** `(d_avell - d_aguj) / 2 = (4.00 - 3.10) / 2 = 0.45 mm`, que coincide exactamente con la profundidad `.45` y el ángulo `90.0°` acotados en la Sección J-J.

## 6. Supuestos y dudas (máx. 5, priorizadas)
1. **Círculo de agujeros `Ø49.00 mm` (Plano 3) vs `Ø50.00 mm` (Plano 4):** ¿Cuál de los dos diámetros de corona es el correcto en el conjunto real (`49.00 mm` o `50.00 mm`, según la pieza donde roscan los tornillos M3)?
2. **Sentido de la cota `10.50 mm` en la Sección J-J:** Confirmar que `10.50 mm` es la profundidad del alojamiento del rodamiento 6201 desde la cara superior (para alojar el ancho `B = 10 mm` del 6201) y no la distancia desde la base.
3. **Diámetro y función de la garganta exterior entre `z = 8.82` y `11.68 mm`:** ¿Es una ranura para O-ring de sello radial contra el agujero `Ø40.10` del Adaptador del eje (Plano 4) o un alivio de mecanizado? ¿Qué diámetro de fondo lleva?

## 7. Detalles pendientes de modelar
Garganta exterior entre `8.82` y `11.68 mm` (sin diámetro acotado en el plano original; el escalón `Ø40.00` se modela continuo de `5.00` a `11.68 mm`). Los chaflanes de `0.50 x 45°` y los avellanados cónicos de `0.45 x 45°` están íntegramente modelados con conos paramétricos.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Desalineación entre la corona de `Ø49.00 mm` (Plano 3) y `Ø50.00 mm` (Plano 4) impide el montaje de los 4 tornillos M3 | Unificar el diámetro de corona en ambos planos (`Ø50.00 mm` o `Ø49.00 mm`) y ampliar los agujeros pasantes a `Ø3.40 mm` (serie media ISO 273 para M3) | Crítico (sin esto las piezas no ensamblan) | Bajo | propuesta |
| 2 | El alojamiento `Ø32.00 mm` para el rodamiento SKF 6201 no tiene tolerancia dimensional especificada | Especificar ajuste **Ø32 H7** (`+0.025 / 0 mm`) o **J7** según carga en el plano de taller y radio máximo de fondo $r_{\text{máx}} \le 0.6\,\text{mm}$ (radio del 6201: $r = 0.6\,\text{mm}$) | Alto (evita giro del aro exterior o bloqueo del rodamiento) | Bajo | propuesta |
| 3 | El rebaje de `Ø15.00 mm` y agujero de paso `Ø13.10 mm` colisionaban con el collar de `Ø15.00 mm` del `Transmisor_2_02b` | Ampliar el diámetro del rebaje y paso interior a `Ø16.00 mm` (holgura radial $0.50\,\text{mm}$ para rotación sin fricción) | Crítico / Alto | Bajo | implementado |
