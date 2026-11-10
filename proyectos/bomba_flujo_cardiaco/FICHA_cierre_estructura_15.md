# FICHA DE DISEÑO - Cierre estructura (Plano Nº 15)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, revisada contra legajo FCAI-UNCuyo

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 9, 20, 23, 25, 26 y pág. 65 - Plano Nº 15 `Cierre estructura`, Escala 1:1, vista frontal y Sección AD-AD).

## 2. Función y contexto
Anillo estructural escalonado de aluminio (2 unidades en el banco) que vincula las placas cuadradas de la `Estructura interior` (Plano 7) con las tapas de PVC de la cámara (`Tapa exterior` 16a y `Tapa interior` 16b). Su escalón exterior de `Ø161.10 mm` encastra en el cajeado de `R80.25 / R84.63 mm` de las placas estructurales y su agujero interior pasante de `Ø131.00 mm` abraza el cuerpo de las tapas, fijándose mediante 4 tornillos pasantes de `Ø5.50 mm` (para bulones M5) sobre el círculo de `Ø169.26 mm` (`R84.63 mm`).

## 3. Datos generales
Material: Aluminio (mecanizado; PLA en prototipo FDM) | Proceso previsto: Torneado + taladrado en fresadora/ plato divisor | Cantidad: 2 unidades | Tolerancias: general sin indicar en plano | Acabado: mecanizado estándar

## 4. Cotas y elementos
| Elemento | Valor | Origen (plano/usuario/norma/calculado/supuesto) | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior brida (`d_ext`) | 176.00 mm | plano | alta | Brida de apoyo (`z = 0..10.00 mm`) |
| Espesor de brida (`h_brida`) | 10.00 mm | plano | alta | Sección AD-AD |
| Diámetro cuerpo escalonado (`d_cuerpo`) | 161.10 mm | plano | alta | Tramo `z = 10.00..28.50 mm` |
| Altura cuerpo escalonado (`h_cuerpo`) | 18.50 mm | plano | alta | Ancho total `10.00 + 18.50 = 28.50 mm` |
| Diámetro interior pasante (`d_int`) | 131.00 mm | plano | alta | Agujero central pasante |
| Círculo de agujeros (`d_cor`) | 169.26 mm | plano | alta | Coincide con `2 * R84.63 = 169.26 mm` del Plano 7 (`Estructura interior`) |
| Diámetro agujeros pasantes (`d_aguj`) | 5.50 mm | plano | alta | 4 agujeros a 0°, 90°, 180°, 270° para tornillos M5 (ISO 273 medio) |
| Chaflanes | 0.50 x 45° | plano | alta | 3 llamadas en Sección AD-AD |

## 5. Verificación de coherencia
- **Cadena axial:** `h_brida (10.00 mm) + h_cuerpo (18.50 mm) = 28.50 mm`, coincidiendo exactamente con la cota total de `28.50 mm` de la Sección AD-AD y la tabla de la pág. 9.
- **Correspondencia con `Estructura interior` (Plano 7, pág. 57):** El círculo de agujeros `Ø169.26 mm` tiene radio `84.63 mm`, idéntico al radio `R84.63 mm` donde se ubican las 4 roscas `M5x0.8` en el Plano 7.
- **Espesor crítico de pared en los 4 agujeros `Ø5.50 mm` sobre `Ø169.26 mm`:**
  - Hacia el borde exterior de la brida (`r_ext = 176.00 / 2 = 88.00 mm`): el borde externo del agujero llega a `84.63 + 5.50 / 2 = 87.38 mm`, dejando apenas **`0.62 mm` de pared remanente** hacia el exterior de la brida `Ø176.00 mm`.
  - Hacia el escalón del cuerpo (`r_cuerpo = 161.10 / 2 = 80.55 mm`): el borde interno del agujero está en `84.63 - 2.75 = 81.88 mm`, dejando solo `1.33 mm` respecto de la pared cilíndrica de `Ø161.10 mm` (lo que impide apoyar una cabeza hexagonal o cilíndrica M5 DIN 912 de `Ø8.5 mm` sin interferir con el cilindro `Ø161.10 mm` si entra desde el lado del escalón).
- **Interferencia entre `d_int = 131.00 mm` y las tapas (Planos 16a/16b):** Las tapas tienen diámetro exterior `Ø160.00 mm` y resalte `Ø145.00 mm`. Según el plano de conjunto (Figura 5.1, pág. 26), el `Cierre estructura` abraza o retiene la tapa contra la `Estructura interior` (`R72.55 = Ø145.10 mm` y `R80.25 = Ø160.50 mm`), por lo que el diámetro interior `Ø131.00 mm` actúa como tope frontal sobre la cara de `Ø160.00 mm` de las tapas.

## 6. Supuestos y dudas (máx. 5 dudas, priorizadas)
1. **Pared exterior de `0.62 mm` en los agujeros `Ø5.50 mm`:** ¿Se amplía el diámetro exterior de la brida `d_ext` de `176.00 mm` a `182.00 mm` (entrando dentro de la placa cuadrada de `183 x 183 mm` del Plano 7) para tener al menos `3.6 mm` de pared y alojar la cabeza de los bulones M5?
2. **Asiento de la cabeza del tornillo M5:** Al estar el agujero a `1.33 mm` del escalón `Ø161.10 mm`, una cabeza Allen M5 (`Ø8.5 mm`) choca contra el cuerpo `Ø161.10 mm` si se inserta desde el lado del escalón (`z = 10.00 mm`). ¿Los tornillos M5 entran desde la cara plana (`z = 0`) o se fresa un cajeado (`spotface` `Ø9.0 mm`) en el cuerpo `Ø161.10 mm`?
3. **Ubicación de los 3 chaflanes `0.50 x 45°`:** En la Sección AD-AD se señalan en el borde exterior derecho del cuerpo `Ø161.10 mm` y en las aristas del agujero `Ø131.00 mm`.

## 7. Detalles pendientes de modelar
- Los 3 chaflanes perimetrales de `0.50 x 45°` indicados en la Sección AD-AD.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado (propuesta/aceptada/descartada) |
|---|---|---|---|---|---|
| 1 | Pared remanente de solo `0.62 mm` entre los agujeros `Ø5.50 mm` (`d_cor = 169.26 mm`) y el borde exterior `Ø176.00 mm` (riesgo de rotura al taladrar o apretar) | Aumentar `d_ext` a `182.00 mm` (compatible con los `183.00 mm` de la `Estructura interior` Plano 7) mediante parámetro `mej_d_ext` | Evita que se rompa el borde de la brida de aluminio | Bajo | propuesta |
| 2 | Interferencia de la cabeza del tornillo M5 DIN 912 (`Ø8.5 mm`) con la pared del cuerpo `Ø161.10 mm` (distancia libre `1.33 mm` frente a `1.50 mm` necesarios) | Agregar 4 fresados de asiento (`spotface` `Ø9.0 mm`) sobre la pared del cuerpo `Ø161.10 mm` o avellanar desde la cara plana `z = 0` | Permite asentar rectas las cabezas de los 4 tornillos M5 | Bajo | propuesta |
