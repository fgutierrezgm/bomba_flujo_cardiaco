# FICHA DE DISEÑO - Anillo tórica (Plano Nº 13)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, revisada contra legajo FCAI-UNCuyo

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 8, 20, 23, 25 y pág. 63 - Plano Nº 13 `Anillo tórica`, Escala 1:1, vista frontal, Sección AA-AA y Detalle AB Escala 4:1).

## 2. Función y contexto
Anillo prensa-tórica (brida de compresión axial) que se atornilla contra el escalón frontal (`z = 30.00 mm`, corona `Ø130.00 mm`) de la Tapa Exterior (Plano 16a) y de la Tapa Interior (Plano 16b). Su función es retener y comprimir axialmente la junta tórica estática de NBR70 (`110,49 x 5,33 mm`, según Sección 4.1 del informe) alojada en la cavidad `Ø120,10 x 6,90 mm` alrededor del tubo de vidrio borosilicato (`Øext 110,50 mm`, Plano 9), asegurando la estanqueidad de ambas cámaras sin someter el vidrio a contacto metal-vidrio.

## 3. Datos generales
Material: PVC rígido (mecanizado; PLA en prototipo FDM) | Proceso previsto: Torno + taladrado/fresado CNC | Cantidad: 2 unidades | Tolerancias: general sin indicar en plano | Acabado: mecanizado estándar

## 4. Cotas y elementos
| Elemento | Valor | Origen (plano/usuario/norma/calculado/supuesto) | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior (`d_ext`) | 140.00 mm | plano | alta | Encaja dentro del resalte `Ø145.00 mm` de las tapas 16a/16b |
| Diámetro interior (`d_int`) | 111.50 mm | plano | alta | Juego radial de 0.50 mm por lado respecto al tubo de vidrio `Ø110.50 mm` |
| Espesor total (`h_total`) | 5.00 mm | plano | alta | Acotado en Sección AA-AA |
| Círculo de agujeros (`d_cor`) | 130.00 mm | plano | alta | Coincide con la corona media `Ø130.00 mm` de las tapas 16a y 16b |
| Agujeros pasantes (`d_aguj`) | 3.10 mm | plano | alta | Para tornillos M3x0.5 de cabeza avellanada |
| Avellanado (`d_avell` x ángulo) | 3.50 mm x 90° | plano | alta | Detalle AB (prof. axial calculada `0.20 mm`) |
| Cantidad de agujeros (`n_aguj`) | 6 | plano | media | Tabla pág. 8 indica 6 agujeros; vista frontal dibuja 4 a 90° (ver incoherencias) |
| Chaflanes perimetrales | 0.50 x 45° | plano | alta | 2 llamadas en Sección AA-AA (borde exterior izq. y borde interior der.) |

## 5. Verificación de coherencia
- **Holgura con el cilindro de vidrio (Plano 9):** `d_int = 111.50 mm` frente a `d_ext_tubo = 110.50 mm` deja `1.00 mm` en diámetro (`0.50 mm` radial), evitando el contacto directo entre el anillo y el tubo de borosilicato.
- **Pared radial del anillo:** `(140.00 - 111.50) / 2 = 14.25 mm`. El círculo `Ø130.00 mm` queda a `5.00 mm` del borde exterior (`r = 70.00 mm`) y a `9.25 mm` del borde interior (`r = 55.75 mm`).
- **Incoherencia en el número de agujeros entre texto y vistas:** En la Tabla de la pág. 8 del informe se especifica explícitamente *"6 agujeros Ø3,10 mm avellanados a Ø3,50 mm x 90° sobre Ø130,00 mm"*, pero en la vista frontal del Plano 13 (pág. 63) y del Plano 16a (pág. 66) solo se dibujan 4 agujeros a 0°, 90°, 180° y 270°. Se modela el patrón de 6 agujeros cada 60° (`0°, 60°, 120°, 180°, 240°, 300°`) según la especificación tabular e instrucciones del grupo, dejando documentada la discrepancia con la Tapa 16a (4 agujeros).
- **Incoherencia dimensional del avellanado (`Ø3.50 mm`):** Para un tornillo comercial M3 avellanado (DIN 965 / ISO 7046), el diámetro de cabeza es `Ø5.5 a 6.0 mm` y el agujero pasante normal (serie fina/media ISO 273) es `Ø3.2 a 3.4 mm`. Con `d_aguj = 3.10 mm` y `d_avell = 3.50 mm`, el avellanado tiene apenas `(3.50 - 3.10) / 2 = 0.20 mm` de profundidad axial y la cabeza del tornillo M3 sobresaldrá `~1.25 mm` por encima de la cara del anillo.

## 6. Supuestos y dudas (máx. 5 dudas, priorizadas)
1. **Cantidad de agujeros en la corona `Ø130.00 mm`:** ¿Se unifican las tapas 16a, 16b y los anillos 13 en 6 agujeros a 60° o en 4 agujeros a 90°?
2. **Diámetro de avellanado (`Ø3.50 mm` vs. DIN 965 `Ø6.00 mm`):** ¿Se mantiene la cota de plano `Ø3.50 x 90°` (solo mata-canto) o se lleva a `Ø6.00 x 90°` para ocultar la cabeza del tornillo M3?
3. **Tolerancia del diámetro interior `Ø111.50 mm`:** ¿Se requiere tolerancia general ISO 2768-m para contener la tórica sin extrusión?

## 7. Detalles pendientes de modelar
- Los 2 chaflanes perimetrales de `0.50 x 45°` indicados en la Sección AA-AA (en borde exterior e interior). El avellanado de `Ø3.50 x 90°` de los 6 agujeros sí está modelado paramétricamente con conos.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado (propuesta/aceptada/descartada) |
|---|---|---|---|---|---|
| 1 | Avellanado de `Ø3.50 mm` insuficiente para alojar la cabeza de un tornillo M3 DIN 965 (`d_k ≈ 5.5–6.0 mm`), dejando la cabeza saliente | Ampliar el avellanado a `Ø6.20 mm x 90°` y el agujero pasante a `Ø3.40 mm` (ISO 273 medio) mediante parámetro `mej_avellanado_m3` | Montaje correcto al ras y sin tensiones en el PVC | Bajo | propuesta |
| 2 | Discrepancia entre 4 agujeros (Plano 16a / vista Plano 13) y 6 agujeros (tabla pág. 8 / Plano 16b) sobre `Ø130.00 mm` | Unificar en 6 agujeros a 60° en las tres piezas (13, 16a y 16b) para uniformizar la presión de apriete sobre la tórica `110.49 x 5.33 mm` | Estanqueidad uniforme y compatibilidad de montaje | Bajo | propuesta |
| 3 | La baja rigidez a flexión de un anillo de PVC de `5.00 mm` de espesor puede arquearse entre tornillos al comprimir una tórica NBR70 de sección `5.33 mm` | Aumentar el espesor del anillo a `8.00 mm` o fabricarlo en aluminio / acero inoxidable | Evita fugas por pérdida de compresión entre bulones | Medio | propuesta |
