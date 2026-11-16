# FICHA DE DISEÑO - Tornillo sin fin (Plano Nº 14)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, revisada contra legajo FCAI-UNCuyo

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 5, 6, 9, 17, 20, 23, 25 y pág. 64 - Plano Nº 14 `Tornillo sin fin`, Escala 1:1, vista longitudinal y Detalle AC Escala 2:1).

## 2. Función y contexto
Husillo de potencia central (`M14x2 - 6g`, 1 sola entrada, avance `L_h = 2.00 mm/rev`) que atraviesa toda la cámara de bombeo y convierte la rotación del motor paso a paso NEMA 23 en el desplazamiento axial lineal del conjunto del émbolo (acoplado mediante la rosca interna `M14x2` del `Centro del émbolo parte 1`, Plano 11).
- En su extremo izquierdo (`z = 0..15.00 mm`) posee un alojamiento cilíndrico interno `Ø8.00 mm` con agujero transversal pasante `Ø4.00 mm` (en `z = 7.52 mm`) donde encastra y se fija con pasador la espiga `Ø7.97 mm` del `Transmisor 2` (Plano 2).
- En su extremo derecho (`z = 254.50..267.50 mm`) posee una espiga escalonada (`Ø13.0 mm` y `Ø12.0 mm`) que se aloja en el interior de la `Tapa exterior` (Plano 16a) y su sufridera (`Sufridera eje ext.`, Plano 5a).

## 3. Datos generales
Material: Acero inoxidable AISI 304 o AISI 316L | Proceso previsto: Torneado entre puntas + roscado al torno / laminado + taladrado transversal | Cantidad: 1 unidad | Tolerancias: `6g` en rosca `M14x2` | Acabado: mecanizado fino en flancos de rosca y espigas

## 4. Cotas y elementos
| Elemento | Valor | Origen (plano/usuario/norma/calculado/supuesto) | Confianza | Nota |
|---|---|---|---|---|
| Rosca principal (`d_m14`) | M14x2 - 6g (Ø14.00 mm) | plano | alta | 1 sola entrada (`z = 1`, `p = 2 mm`); nominal 14.00 mm |
| Largo roscado (`l_rosca`) | 254.50 mm | plano | alta | Tramo `z = 0` a `254.50 mm` |
| Largo total espiga derecha (`l_esp_der`) | 13.00 mm | plano | alta | Largo total total pieza = `254.50 + 13.00 = 267.50 mm` |
| Diámetro 1er escalón der. (`d_esp13`) | 13.00 mm | plano | alta | En el plano 2009 faltaba el símbolo `Ø`, corregido en tabla pág. 9 |
| Largo 1er escalón der. (`l_esp13`) | 5.00 mm | calculado | alta | Calculado de la cadena `13.00 - 8.00 = 5.00 mm` |
| Diámetro extremo der. (`d_esp12`) | 12.00 mm | plano | alta | Entra en `Sufridera eje ext.` (`Ø12.20 mm`, Plano 5a) |
| Largo extremo der. (`l_esp12`) | 8.00 mm | plano | alta | Coincide con los `8.00 mm` de prof. en `Sufridera eje ext.` (Plano 5a) |
| Diámetro alojamiento izq. (`d_aloj_izq`) | 8.00 mm | plano | alta | Detalle AC; recibe espiga `Ø7.97 mm` de `Transmisor 2` (Plano 2) |
| Profundidad alojamiento izq. (`p_aloj_izq`) | 15.00 mm | plano | alta | Detalle AC (`z = 0` a `15.00 mm`) |
| Agujero pasador transversal (`d_pasador`) | 4.00 mm | plano | alta | Detalle AC; pasante transversal |
| Posición axial del pasador (`z_pasador`) | 7.52 mm | plano | alta | Detalle AC (frente a `7.50 mm` en `Transmisor 2`, Plano 2) |

## 5. Verificación de coherencia
- **Cadena longitudinal:** `l_rosca (254.50) + l_esp13 (5.00) + l_esp12 (8.00) = 267.50 mm` (con `5.00 + 8.00 = 13.00 mm` coincidente con la cota acumulada de `13.00 mm` en la espiga derecha).
- **Acoplamiento izquierdo con `Transmisor 2` (Plano 2, pág. 51):** El Transmisor 2 tiene una espiga de `Ø7.97 mm` y largo `15.00 mm` (`126.92 - 112.00 = 14.92 mm` o lado izq. `15.00 mm`) con agujero `Ø4.00 mm` a `7.50 mm` del extremo. El alojamiento del husillo mide `Ø8.00 x 15.00 mm` (juego diametral `0.03 mm`) con el pasador a `7.52 mm` del borde (`0.02 mm` de diferencia con los `7.50 mm` del Transmisor 2, lo que garantiza que el tope frontal apoye antes de cizallar el pasador).
- **Espesor de pared remanente en el alojamiento izquierdo (`z = 0..15.00 mm`):** El diámetro de fondo (núcleo) de una rosca externa `M14x2` (ISO 724 / DIN 13-1) es `d_3 = 14.00 - 1.22687 * 2 = 11.55 mm`. Con el agujero interno de `Ø8.00 mm`, el espesor radial de pared en el fondo de filete es de apenas `(11.55 - 8.00) / 2 = 1.77 mm`, debilitado además por el agujero transversal de `Ø4.00 mm`. No obstante, dado que el par máximo requerido es bajo (`0.35 N·m`, Sección 3.2.3), la tensión torsional es admisible en acero inoxidable.
- **Acoplamiento derecho con `Sufridera eje ext.` (Plano 5a, pág. 54):** La espiga derecha de `Ø12.00 x 8.00 mm` entra en el agujero de `Ø12.20 x 8.00 mm` de la sufridera exterior, mientras que el escalón de `Ø13.00 x 5.00 mm` queda dentro del tramo de `Ø13.10 x 5.00 mm` (`13.00 - 8.00 = 5.00 mm`) de dicha sufridera. Coherencia geométrica perfecta entre los Planos 5a y 14.

## 6. Supuestos y dudas (máx. 5 dudas, priorizadas)
1. **Tolerancias de ajuste en espiga derecha (`Ø12.0` y `Ø13.0`) y alojamiento izquierdo (`Ø8.00`):** ¿Se mecaniza el alojamiento a `Ø8.00 H7` y la espiga derecha con ajuste giratorio `f7/g6` sobre la sufridera?
2. **Desahogo de herramienta en el fondo del alojamiento `Ø8.00 x 15.00 mm`:** El Detalle AC muestra fondo plano; si se mecaniza con mecha estándar de `118°`, ¿se profundiza el cono de punta más allá de los `15.00 mm` útiles para que no interfiera con la espiga del Transmisor 2?
3. **Chaflanes de entrada:** El plano no acota chaflanes de entrada en la rosca `M14x2` ni en los escalones `Ø13.0` y `Ø12.0`.

## 7. Detalles pendientes de modelar
- Filete helicoidal físico de la rosca `M14x2` (según Regla 3.4 de `AGENTS.md`, en Modo 2 y Modo 3 se representa mediante su cilindro nominal de `Ø14.00 mm`).

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado (propuesta/aceptada/descartada) |
|---|---|---|---|---|---|
| 1 | Rosca métrica V `M14x2` a `60°` usada como tornillo de potencia tiene bajo rendimiento mecánico (`η ≈ 0.20–0.25`) y mayor desgaste por fricción | Reemplazar el par husillo/centro de émbolo por rosca trapecial `Tr14x2` (DIN 103, flanco a `30°`) manteniendo el mismo avance `L_h = 2 mm/rev` | Reduce el par de fricción y duplica la vida útil de la tuerca de latón/bronce | Medio | propuesta |
| 2 | El fondo plano del alojamiento `Ø8.00 x 15.00 mm` requiere escariado de fondo plano o dejar longitud adicional para el cono de la mecha | Profundizar el agujero cónico de mecha hasta `17.50 mm` (dejando `15.00 mm` cilíndricos útiles) o agregar un chaflán de `1.0 x 45°` en la espiga del Transmisor 2 | Evita interferencia axial al insertar el Transmisor 2 y alinear el pasador `Ø4.00 mm` | Bajo | propuesta |
| 3 | Falta de garganta de salida de rosca entre el tramo `M14x2` y el escalón `Ø13.00 mm` | Incorporar una garganta de salida de rosca según DIN 76 (`Ø11.2 mm x 3.0 mm`) en `z = 254.50 mm` | Permite terminar la rosca limpia al torno y asentar de frente contra la sufridera | Bajo | propuesta |
| 4 | En el prototipo impreso 3D (`Escala 0.755`, `Tornillo_Sin_Fin_14_3D.FCStd`), los escalones inferiores (`Ø9.82 / Ø9.06 mm`) superan el Ø interior efectivo de la rosca trapecial de `Centro_Embolo_1_11_3D` (`d_cresta = 9.70 mm`, `~9.15 mm` impreso) e impiden montar el émbolo por abajo tras unir `#14` con `#13` | Reducir la espiga inferior (`Z_local = 179.00..192.15 mm`) a diámetro uniforme **`Ø8.80 mm`** (= raíz de la rosca trapecial `p = 3.00 mm`, sin escalón `Ø10.50` / `Ø9.82`), conservando idéntico largo total `192.15 mm` y el extremo de acople superior `Ø10.50 mm` (`Z = 0..14.00 mm`) | Crítico (permite pasar `Centro_Embolo_1_11_3D` desde abajo sin tocar las tapas `16a`/`16b` ya impresas) | Bajo | aceptada (implementada en `generar_tornillo_sin_fin_14_3d.py`, Opción 2) |
