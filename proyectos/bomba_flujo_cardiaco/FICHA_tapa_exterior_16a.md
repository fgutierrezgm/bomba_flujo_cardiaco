# FICHA DE DISEÑO - Tapa exterior (Plano Nº 16a)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/plano_16a.png`: vista frontal, lateral, posterior, Sección F-F y Detalle G. Escala 1:1.5.
- `entradas/informe_y_planos_bomba.pdf` (Secciones 1.2.4, 4.1 y 5.3; Plano Nº 0 en pág. 26 y Plano Nº 16a en pág. 66): confirma material, sellos y función de los alojamientos de Ø14.

## 2. Función y contexto
Tapa/brida del extremo libre (opuesto al motor) de la cámara de la bomba: recibe el tubo de vidrio borosilicato (`Ø110.50`) en su cavidad escalonada con junta tórica de NBR70 (`110.49 x 5.33 mm`) comprimida por el anillo prensa-tórica (Plano 13), encastra su resalte de `Ø145.00` en la placa de estructura interior (Plano 7), aloja en los 2 huecos de `Ø14.00` (sobre `Ø75.00`) los extremos o bujes (`Ø12 x Ø14`) de las dos barras guía (`Ø12 h7`, Plano 8), y posee 2 puertos `G 1/8` (entrada/salida hidráulica) y 1 puerto `M12x1` para el sensor inductivo de fin de carrera exterior (`LJ12A3`).

## 3. Datos generales
Material: PVC rígido mecanizado (informe Secc. 4.1) | Proceso: torneado y fresado/taladrado (prototipo impreso en PLA 40% gyroid) | Cantidad: 1 | Tolerancias: generales de mecanizado | Acabado: mecanizado estándar

## 4. Cotas y elementos
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Ø total / altura base / resalte | 160 / 25.50 / 4.50 | plano | alta | Z total 30 |
| Encastre | Ø145 | plano | alta | |
| Cavidades Ø (de fuera a dentro) | 120.10, 110.50, 40.10, 18.00 | plano | alta | |
| Profundidades de cavidad | 6.90, 7.10, 5.00, 8.00 | plano | alta | 6.90 y 7.10 asignadas por posición en la Sección F-F |
| Alojamientos | 2x Ø14, círculo Ø75 | plano | alta | sobre el eje X de la vista frontal |
| Profundidad alojamientos | 11 | supuesto | media | la cota 11.00 de la Sección F-F podría referirse a otra cosa |
| Puertos G 1/8 | 2x, a 90° y 270°, prof. 8.00 | plano + norma | alta | |
| Pasaje bajo G 1/8 | Ø4 | supuesto | baja | NO está acotado; estimado a ojo del dibujo, no medido |
| Puerto M12x1 | a 45°, círculo Ø75 | plano | alta | modelado pasante (el plano no indica profundidad) |
| M3x0.5 | 4x Ø152.50 (prof. 6), 4x Ø130 (prof. 4), 4x Ø29.10 (prof. 4) | plano | alta | posiciones a 0/90/180/270° |
| Chaflanes | .50 x 45° | plano | alta | 4 llamadas; aristas sin identificar |

## 5. Verificación de coherencia
- 25.50 + 4.50 = 30.
- 6.90 + 7.10 + 5.00 + 8.00 = 27.00, que coincide con la cota 27.00 de la Sección F-F; queda un fondo de 3.00 mm.
- 6.90 + 7.10 + 5.00 = 19.00, que coincide con la cota del Detalle G.
- El 8.00 de la vista lateral coincide con la profundidad del puerto G 1/8.

## 6. Supuestos y dudas
1. ¿Qué mide exactamente la cota 11.00 (profundidad de los Ø14 o espesor bajo la cavidad 3)?
2. ¿Diámetro real del pasaje bajo cada G 1/8?
3. ¿El M12x1 es pasante? ¿Qué profundidad útil de rosca?
4. ¿Sobre qué 4 aristas van los chaflanes .50 x 45°?
5. ¿Material y proceso (impresión 3D o mecanizado)?

## 7. Detalles pendientes de modelar
Chaflanes .50 x 45° (4). El resto del plano está modelado.

## 8. Propuestas de mejora (a confirmar, aún sin revisar con el usuario)
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | El plano no muestra ranura de o-ring ni junta | Definir cómo sella contra la carcasa; agregar ranura según el diámetro de sello | Estanqueidad | Medio | propuesta |
| 2 | El encastre Ø145 y el asiento no tienen tolerancia ni ajuste | Definir ajuste ISO 286 (por ejemplo H7/g6 si se mecaniza) | Montaje / fugas | Bajo | propuesta |
| 3 | Fondo de solo 3 mm bajo las cavidades de Ø40 y Ø18 | Verificar rigidez a la presión de trabajo y, si hace falta, aumentar el espesor | Resistencia | Medio | propuesta |
