# FICHA DE DISEÑO - Guía (Plano Nº 8)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/plano_08_guia.png`: vista longitudinal general (Escala 1:1), Detalle V del extremo roscado y escalón (Escala 3:1), Detalle W del extremo liso (Escala 2:1) y rótulo.
- Indicaciones del usuario: son **2 unidades** por bomba y van fijas en los agujeros correspondientes de las tapas.

## 2. Función y contexto
Columnas/barras guía cilíndricas (2x) que vinculan las tapas de la bomba y sirven de guía lineal de precisión (`Ø12.00 h7`, rugosidad `N5`) para el elemento móvil intermedio, manteniendo la coaxialidad entre componentes. Un extremo tiene una espiga rebajada a `Ø10.00` (largo `30.00 mm`) con punta roscada `M10x1.5 - 6g` (`13.00 mm`) para fijación axial contra una tapa, y el cuerpo principal de `Ø12.00 h7` (`260.00 mm`) se extiende hasta acoplar en la tapa opuesta.

## 3. Datos generales
Material: no indicado en plano (supuesto: acero inoxidable AISI 304/316 o acero SAE 1045 cromado duro para guía lineal) | Proceso previsto: torno paralelo/CNC + rectificado sin centros (por `h7` y `N5`) | Cantidad: 2 | Tolerancias: `Ø12.00 h7` (`0 / -0.018 mm`), rosca `6g`, GD&T `0.003` respecto de `A` | Acabado: `N5` ($R_a = 0.4\,\mu\text{m}$) en cilindros de `Ø10` y `Ø12`.

## 4. Cotas y elementos
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Longitud total (`l_total`) | `290.00 mm` | plano | alta | De extremo a extremo |
| Longitud espiga rebajada (`l_espiga`) | `30.00 mm` | plano | alta | Incluye el tramo roscado y el tramo liso de Ø10 |
| Diámetro espiga lisa (`d_espiga`) | `Ø10.00 mm` | plano | alta | Acabado `N5`; largo liso resultante `17.00 mm` |
| Rosca extremo izquierdo (`d_rosca`, paso) | `M10x1.5 - 6g` | plano + norma | alta | Paso grueso estándar ISO; Ø mayor nominal `10.00 mm`, Ø núcleo `8.16 mm` |
| Longitud roscada (`l_rosca`) | `13.00 mm` | plano | alta | En Detalle V |
| Chaflán extremo roscado (`c_izq`) | `1.00 x 45°` | plano | alta | En Detalle V |
| Diámetro cuerpo guía (`d_cuerpo`) | `Ø12.00 h7` | plano | alta | Acabado `N5`; largo resultante `260.00 mm` |
| Chaflán escalón Ø10 → Ø12 (`c_escalon`) | `0.50 x 45°` | plano | alta | En Detalle V |
| Chaflán extremo derecho (`c_der`) | `1.00 x 45°` | plano | alta | En Detalle W |
| Cantidad por equipo | `2` | usuario | alta | Fijas en los 2 alojamientos sobre círculo Ø75 de las tapas |

## 5. Verificación de coherencia
- **Cadena longitudinal:** `l_rosca (13.00) + tramo liso Ø10 (17.00) = l_espiga (30.00 mm)`; `l_espiga (30.00) + l_cuerpo (260.00) = l_total (290.00 mm)`. Todas las cotas axiales cierran sin sobre-restricción.
- **Incoherencia / duda de interfaz con Tapa exterior (Plano Nº 16a):**
  1. En el **Plano 16a (Tapa exterior)**, los dos alojamientos a `0°` y `180°` sobre el círculo de `Ø75.00 mm` están acotados en el círculo exterior como **`Ø14.00`** (con un segundo círculo interior concéntrico sin acotar en la vista frontal y profundidad `11.00 mm` en la Sección F-F), mientras que la **Guía (Plano 8)** tiene cuerpo de **`Ø12.00 h7`** y espiga de **`Ø10.00 / M10x1.5`**.
  2. La longitud de la espiga (`30.00 mm`) coincide exactamente con el espesor total de la Tapa exterior (`25.50 + 4.50 = 30.00 mm`), o bien atraviesa la pared de `16.00 mm` bajo la Cavidad 2 dejando `14.00 mm` (la parte roscada `M10x1.5` de `13.00 mm`) del lado exterior para tuerca y arandela.
- **Observación de dibujo técnico (GD&T en Detalle V):** el cuadro de control indica posición y concentricidad `.003 | A`, pero en el plano no está dibujado el triángulo indicador de la referencia/datum `A` (se infiere que el datum `A` es el eje de la espiga `Ø10.00` o del cuerpo `Ø12.00 h7`).

## 6. Supuestos y dudas (priorizadas)
1. **Interfaz Guía ↔ Tapa 16a (crítica para el ensamblaje):** ¿En la Tapa exterior (16a) entra el extremo de **espiga `Ø10 / M10x1.5`** (apoyando el hombro de `Ø12` en la tapa y fijando con tuerca desde afuera) o entra el extremo liso de **`Ø12.00 h7`** en los alojamientos de la cara interna? *(En el ensamblaje inicial se deja parametrizado en `Parametros_Generales` con asiento en el alojamiento de la tapa, seleccionable por modo).*
2. **Cota `Ø14.00` en Tapa 16a vs `Ø12.00 h7` / `Ø10.00` en Guía 8:** ¿El círculo interior sin acotar de los dos agujeros laterales en el Plano 16a es de `Ø10.00` / `Ø12.00` y el `Ø14.00` es un rebaje para tuerca/buje, o hay una diferencia de diámetro entre planos?
3. **Material de la guía:** ¿Se fabricará a partir de barra comercial rectificada y cromada de `Ø12 h7` (estándar de guías lineales) o acero inoxidable torneado?

## 7. Detalles pendientes de modelar
Ninguno de geometría maciza: se modelan todos los tramos (`M10x1.5`, espiga `Ø10`, cuerpo `Ø12`) y los 3 chaflanes (`1.00 x 45°`, `0.50 x 45°` y `1.00 x 45°`) de forma 100% paramétrica mediante conos y cilindros sin usar índices de arista. La rosca exterior `M10x1.5` se representa por su cilindro nominal en Modo 1/3 y diámetro de núcleo/efectivo en Modo 2 según convención de `fc_helpers.py`.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Tornear y rectificar `260 mm` de largo a `Ø12 h7` y `N5` es costoso y propenso a flexión en torno | Partir de **barra comercial rectificada/cromada estándar Ø12 h7** (stock local para rodamientos lineales LM12UU) y mecanizar únicamente los `30 mm` de la espiga `Ø10 / M10x1.5` en un extremo | Muy alto (reduce costo y garantiza `h7` y `N5` reales) | Bajo | propuesta |
| 2 | Falta de garganta de salida de rosca (DIN 76) y de rectificado (DIN 509) en los cambios de sección | Agregar garganta de salida de rosca en `Z = 13 mm` y radio/entalla de alivio en el hombro `Z = 30 mm` para que el hombro apoye plano contra la tapa sin interferir con el radio de punta de herramienta | Medio (mejor asiento axial y menor concentración de tensiones) | Bajo | propuesta |
| 3 | Sin medio de retención de giro al apretar la tuerca `M10x1.5` | Incorporar hexágono interior Allen (p. ej. 5 mm en el extremo) o dos planos paralelos para llave en el extremo derecho de la guía | Medio (facilita el montaje y desmontaje sin dañar la superficie `N5`) | Bajo | propuesta |
| 4 | Tolerancia geométrica `.003 mm` (3 µm) excesivamente exigente para el método de fijación por rosca | Relajar a `0.015 - 0.020 mm` (típico de torneado entre puntas / boquilla de precisión) y asegurar que el centrado lo dé el tramo liso `Ø10.00` con ajuste `H7/js6` o `H7/h6` | Medio (viabilidad de fabricación) | Nulo (plano) | propuesta |
