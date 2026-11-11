# FICHA DE DISEÑO - Émbolo de Delrin (Plano Nº 10)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 60, Plano Nº 10 "Delrin"): vista frontal izquierda, vista lateral, vista frontal derecha y corte `SECTION Y-Y` (Escala 1:1).
- Memoria descriptiva del informe: disco de Delrin (POM-C) que aloja la junta tórica perimetral de Viton (`97 x 3.5 mm`), 2 bujes guía (`Ø12 x Ø14 x 20 mm`), el núcleo central de latón (Planos 11 y 12) y los 2 vástagos sensores/topes `M8` (Plano 5b).

## 2. Función y contexto
Cuerpo principal del pistón/émbolo que desplaza el fluido dentro del cilindro de borosilicato (`Ø103.00 mm`, Plano 9). Se guía linealmente sobre las 2 barras guía de `Ø12.00 h7` (Plano 8) mediante bujes insertados en los 2 agujeros pasantes de `Ø14.00 mm` sobre el círculo de `Ø75.00 mm`. En su agujero central de `Ø30.00 mm` recibe el vástago del Centro del Émbolo Parte 1 (Plano 11), que queda aprisionado axialmente junto con la Parte 2 (Plano 12) y fijado mediante tornillos `M3x0.5`. Además, posee dos agujeros roscados `M8x1.25 - 6H` sobre el círculo de `Ø75.00 mm` (uno en cada cara, desfasados `90°` entre sí: a `135°` en una cara y a `45°` en la opuesta) para roscar los vástagos de accionamiento de sensores de fin de carrera (Plano 5b).

## 3. Datos generales
Material: Delrin / Poliacetal POM-C (densidad `1.41 g/cm³` = `0.00000141 kg/mm³`) | Proceso previsto: torneado CNC/convencional + fresado/taladrado con plato divisor o centro de mecanizado | Cantidad: 1 | Tolerancias: rosca `M8x1.25 - 6H`; resto sin tolerancia específica en plano | Acabado: mecanizado liso de baja fricción propio del POM.

## 4. Cotas y elementos
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior (`d_ext`) | `Ø102.00 mm` | plano | alta | Huelga diametral de `1.00 mm` dentro del cilindro `Ø103.00 mm` |
| Espesor total (`h_total`) | `20.00 mm` | plano | alta | Ancho axial del disco |
| Agujero central (`d_int`) | `Ø30.00 mm` | plano | alta | Aloja el vástago `Ø30.00 mm` del Centro del Émbolo Parte 1 (Plano 11) |
| Chaflanes ext. e int. (`c_ch`) | `1.00 x 45°` | plano | alta | En las 4 aristas circulares (2 exteriores en `Ø102` y 2 interiores en `Ø30`) |
| Ancho axial ranura o-ring (`a_ran`) | `4.13 mm` | plano | alta | Para junta tórica de Viton `97 x 3.5 mm` (`d_2 = 3.53 mm`) |
| Profundidad radial ranura (`p_ran`) | `2.93 mm` | plano | alta | Diámetro de fondo de ranura resultante: `102.00 - 2*2.93 = 96.14 mm` |
| Posición axial ranura (`z_ran`) | `8.00 mm` | plano | alta | Desde la cara `Z = 0` hasta el inicio de la ranura |
| Círculo de posición (`d_c75`) | `Ø75.00 mm` | plano | alta | Común para los 2 alojamientos de guía (`Ø14`) y los 2 agujeros `M8x1.25` |
| Agujeros para bujes guía (`d_aloj_guia`) | `2x Ø14.00 mm` pasantes | plano | alta | A `0°` y `180°` sobre `Ø75.00 mm` |
| Corona de roscas M3 (`d_cor_m3`) | `Ø37.40 mm` | plano | alta | 4x a `0°, 90°, 180°, 270°` en cara `Z = 0` (hacia `Centro_Embolo_1_11`) |
| Roscas de fijación central (`d_m3`, `p_m3`) | `M3x0.5`, prof. `8.00 mm` | usuario + plano | alta | Mecha `Ø2.50 mm`; 4 en cara `Z = 0`. Se eliminaron las 4 de cara `Z = 20.00 mm` porque `Centro_Embolo_2_12` atornilla sobre el vástago de `Centro_Embolo_1_11` |
| Roscas para sensor (`d_m8`) | `2x M8x1.25 - 6H` | usuario + norma | alta | Mecha `Ø6.80 mm`; sobre `Ø75.00 mm`, ciegos: uno en `Z = 0` a `45°` (enfrentando `Puerto_M12x1` de `Tapa_Interior_16b`) y otro en `Z = 20` a `315°` / `-45°` (enfrentando `Puerto_M12x1` de `Tapa_Exterior_16a`) |
| Profundidad roscas M8 (`p_m8`) | `8.00 mm` (ciegos) | usuario | alta | Agujeros ciegos (`8.00 mm` por cara en espesor de `20.00 mm`, pared maciza intermedia de `4.00 mm`) para evitar cualquier fuga interna de fluido a través de las roscas de los topes |

## 5. Verificación de coherencia
- **Cadena axial de la ranura de o-ring:** La ranura arranca a `8.00 mm` de una cara y mide `4.13 mm` de ancho, quedando a `20.00 - 8.00 - 4.13 = 7.87 mm` de la otra cara (casi centrada en el espesor de `20.00 mm`).
- **Verificación de compresión del o-ring (`97 x 3.5 mm` dentro de `Ø103.00 mm`):**
  - Diámetro de fondo de ranura: `d_fondo = 102.00 - 2 * 2.93 = 96.14 mm`.
  - Espacio radial entre el fondo de ranura y la pared interior del cilindro (`Ø103.00 mm`): `(103.00 - 96.14) / 2 = 3.43 mm`.
  - Si la sección del o-ring es `3.50 mm` (o `3.53 mm` estándar AS568 / ISO 3601), el aplastamiento radial es de solo `3.50 - 3.43 = 0.07 mm` (`2%`) a `0.10 mm` (`2.8%`), muy bajo para sellado dinámico hidráulico estándar (que suele requerir `8% - 12%`), aunque reduce drásticamente la fricción contra el tubo de vidrio.
- **Discrepancia entre planos en la corona de tornillos M3 (`Ø37.40` vs `Ø37.50`):**
  - En este **Plano Nº 10**, la corona de los 4 agujeros `M3x0.5` está acotada a **`Ø37.40 mm`**, mientras que en el **Plano Nº 11 (Centro del émbolo parte 1)** los 4 agujeros pasantes `Ø3.50 mm` están acotados sobre **`Ø37.50 mm`**. La diferencia radial de `0.05 mm` es absorbida por la holgura del agujero pasante `Ø3.50 mm` para tornillo `M3` (`0.25 mm` radial), pero conviene unificar ambas cotas en `Ø37.50 mm`.
- **Roscas M3 en ambas caras:** Cada rosca `M3x0.5` tiene `8.00 mm` de profundidad desde su cara respectiva (`8.00 + 8.00 = 16.00 mm < 20.00 mm`), dejando `4.00 mm` de material macizo entre agujeros opuestos.

## 6. Supuestos y dudas (priorizadas)
1. **Profundidad de los agujeros `M8x1.25 - 6H` (`p_m8 = 8.00 mm`):** No tiene cota propia en el plano; se adoptó `8.00 mm` por coincidencia visual en la vista lateral con la profundidad de los agujeros `M3x0.5 x 8.00` y con el largo roscado del vástago sensor (Plano 5b).
2. **Unificación del círculo de agujeros `M3` (`Ø37.40` vs `Ø37.50`):** ¿Se debe corregir a `Ø37.50 mm` para coincidir exactamente con el Plano 11?
3. **Ajuste de alojamientos `Ø14.00 mm` y central `Ø30.00 mm`:** No se indican tolerancias ISO en el plano para el clavado de los bujes `Ø12xØ14x20` ni para el calce del núcleo `Ø30.00 mm`.

## 7. Detalles pendientes de modelar
Ninguno: se modelan todos los chaflanes exteriores e interiores (`1.00 x 45°`), la ranura perimetral del o-ring, los 2 alojamientos de `Ø14.00 mm`, las 8 roscas `M3x0.5` (4 por cara) y las 2 roscas `M8x1.25` desfasadas en caras opuestas.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Discrepancia entre el círculo `Ø37.40 mm` (Plano 10) y `Ø37.50 mm` (Plano 11) | Unificar ambos planos a `Ø37.50 mm` para evitar interferencia de montaje en los tornillos M3 | Medio (montaje limpio) | Nulo | propuesta |
| 2 | Roscas `M3x0.5` directamente sobre Delrin (POM) con solo `8 mm` de profundidad | Si se desmonta con frecuencia, utilizar insertos roscados de latón o hacer pasantes los 4 agujeros `Ø3.4 mm` con tuerca/arandela del lado opuesto | Medio (durabilidad de rosca en plástico) | Bajo | propuesta |
| 3 | Falta de tolerancias en alojamientos de bujes `Ø14.00` y núcleo `Ø30.00` | Especificar `Ø14.00 H7` (para bujes sinterizados/poliméricos clavados) y `Ø30.00 H8/f7` con sellador o junta frontal en la brida del núcleo para evitar fugas por el centro del émbolo | Alto (paralelismo de guías y estanqueidad central) | Bajo | propuesta |
