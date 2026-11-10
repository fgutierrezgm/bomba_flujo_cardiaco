# FICHA DE DISEÑO - Transmisores 1 y 2 (Plano Nº 2: 02a y 02b)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 51, **Plano Nº 2 - Transmisores**, Escala 2:1):
  - **Pieza superior (`Transmisor_1_02a`):** vista longitudinal con líneas ocultas del alojamiento interior y vista lateral izquierda.
  - **Pieza inferior (`Transmisor_2_02b`):** vista longitudinal con 3 agujeros transversales pasantes y vista lateral izquierda.
- Especificación de proyecto: material acero inoxidable AISI 304 / 316L; `Transmisor_1_02a` acopla por su espiga izquierda al manchón/acople Oldham (Plano Nº 1) y recibe en su cavidad derecha el tramo izquierdo de `Transmisor_2_02b`, el cual atraviesa el rodamiento SKF 6201 (alojado en el Adaptador de rodamiento, Plano Nº 3) y el retén `14x30x7`, acoplando en su extremo derecho con el tornillo sin fin (Plano Nº 14).

## 2. Función y contexto
Conjunto de ejes de transmisión coaxiales que vinculan la salida del reductor/acople con el husillo de bolas (tornillo sin fin, Plano Nº 14) dentro del cabezal de accionamiento de la bomba:
- **`Transmisor_1_02a` (Plano Nº 2 arriba):** eje escalonado con espiga izquierda de `Ø8.00 mm` (`15.00 mm` de largo), tramo intermedio de `32.00 mm` (`z = 15.00` a `47.00 mm`) y cuerpo cilíndrico de `Ø20.00 mm` (`z = 47.00` a `127.00 mm`) con perforación interior derecha de `Ø12.00 mm` para alojar al `Transmisor_2_02b` y transmitir cupla mediante pasadores transversales.
- **`Transmisor_2_02b` (Plano Nº 2 abajo):** eje escalonado de `126.92 mm` de largo total con vástago izquierdo de `Ø12.00 mm` (`67.00 mm` de largo, con 2 agujeros transversales `Ø4.00 mm` en `z = 7.50` y `52.50 mm` que solidarizan con `Transmisor_1_02a` y asiento para el rodamiento rígido de bolas SKF 6201 de `Ø12x32x10 mm`), escalón intermedio de `Ø13.00 mm` (`z = 67.00` a `72.00 mm`), brida/collar central de `Ø15.00 mm` (`z = 72.00` a `93.00 mm` para tope axial), pista de `Ø14.00 mm` (`z = 93.00` a `112.00 mm` para labio del retén `14x30x7`) y espiga derecha de `Ø7.97 mm` (`z = 112.00` a `126.92 mm`, con agujero transversal `Ø4.00 mm` en `z = 119.50 mm` para pasador de acople con el tornillo sin fin del Plano Nº 14).

## 3. Datos generales
Material: Acero inoxidable AISI 304 / 316L (informe) | Proceso previsto: Torneado paralelo/CNC + taladrado transversal en fresadora con divisor/prisma en V | Cantidad: 1 de cada uno (`02a` y `02b`) | Tolerancias: no indicadas explícitamente como clase ISO en el plano (salvo cota directa `Ø7.97 mm` para ajuste con holgura en el alojamiento `Ø8.00 mm` del tornillo sin fin) | Acabado: mecanizado fino en pistas de rodamiento (`Ø12.00`) y retén (`Ø14.00`).

## 4. Cotas y elementos

### 4.1. Transmisor 1 (`Transmisor_1_02a` — Plano Nº 2 arriba)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Largo total (`l_total`) | `127.00 mm` | plano | alta | De extremo izquierdo (`z=0`) a cara derecha (`z=127.00`) |
| Largo espiga izquierda (`l_espiga`) | `15.00 mm` | plano | alta | Tramo `z = 0` a `15.00 mm` |
| Diámetro espiga izquierda (`d_espiga`) | `Ø8.00 mm` | plano | alta | Tipo `S`; entra en el acople (Plano Nº 1) |
| Posición axial segundo escalón (`z_med`) | `47.00 mm` | plano | alta | Tramo intermedio de `32.00 mm` de largo (`47.00 - 15.00`) |
| Diámetro tramo medio (`d_med`) | `Ø12.00 mm` | plano | media | Ver sección 5: en vista longitudinal hay cota `Ø10.00` sobre este tramo y `Ø12.00` en la vista lateral |
| Cota diámetro `Ø10.00` (`d_int_10`) | `Ø10.00 mm` | plano | media | Acotada a la izquierda sobre las líneas del tramo medio / fondo escalonado |
| Diámetro cuerpo derecho (`d_cuerpo`) | `Ø20.00 mm` | plano | alta | Tramo `z = 47.00` a `127.00 mm` (`80.00 mm` de largo) |
| Fondo alojamiento interior (`z_aloj`) | `59.00 mm` | calculado | alta | Fondo de la perforación `Ø12.00 mm` (profundidad `127.00 - 59.00 = 68.00 mm` para alojar los `67.00 mm` de `02b`) |
| Diámetro alojamiento interior (`d_aloj_int`) | `Ø12.00 mm` | plano | alta | Tipo `H`; recibe el vástago `Ø12.00` del `Transmisor_2_02b` |
| Agujero transversal pasador 1 (`z_pas1`) | `67.50 mm` | plano | alta | Cota `67.50` en el plano marca la línea de centro del 1º pasador (coincide con pasador `z=7.50` de `02b`) |
| Agujero transversal pasador 2 (`z_pas2`) | `112.50 mm` | plano | alta | Cota `112.50` en el plano marca la línea de centro del 2º pasador (`112.50 - 67.50 = 45.00 mm`, coincide con `z=52.50` de `02b`) |
| Diámetro agujeros pasadores (`d_pasador`) | `Ø4.00 mm` | plano | alta | Pasantes transversales de `Ø4.00 mm` en correspondencia directa con los de `02b` |
| Chaflanes (`c_chaf`) | `0.50 x 45°` | plano | alta | 5 indicaciones `.50 X 45.0°` en escalones exteriores y boca derecha |

### 4.2. Transmisor 2 (`Transmisor_2_02b` — Plano Nº 2 abajo)
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Largo total (`l_total`) | `126.92 mm` | plano | alta | De extremo izquierdo (`z=0`) a extremo derecho (`z=126.92`) |
| Fin tramo izquierdo (`z_1`) | `67.00 mm` | plano | alta | Tramo de `Ø12.00 mm` (acople en `02a` + asiento rodamiento 6201) |
| Diámetro tramo izquierdo (`d_izq`) | `Ø12.00 mm` | plano | alta | Tipo `S`; acotado dos veces en vista longitudinal |
| Fin escalón intermedio (`z_2`) | `72.00 mm` | plano | alta | Largo del escalón: `72.00 - 67.00 = 5.00 mm` |
| Diámetro escalón intermedio (`d_esc13`) | `Ø13.00 mm` | plano | alta | Tipo `S`; pasa con holgura por el agujero `Ø13.10` del Adaptador (Plano Nº 3) |
| Fin collar central (`z_3`) | `93.00 mm` | plano | alta | Largo del collar: `93.00 - 72.00 = 21.00 mm` |
| Diámetro collar central (`d_collar`) | `Ø15.00 mm` | plano | alta | Tipo `S`; acotado en vista lateral izquierda (`Ø15.00`) |
| Fin asiento de retén (`z_4`) | `112.00 mm` | plano | alta | Largo de pista de retén: `112.00 - 93.00 = 19.00 mm` |
| Diámetro asiento de retén (`d_reten`) | `Ø14.00 mm` | plano | alta | Tipo `S`; pista de sello para retén `14x30x7` |
| Diámetro espiga derecha (`d_espiga_der`) | `Ø7.97 mm` | plano | alta | Tipo `S`; largo `126.92 - 112.00 = 14.92 mm`, entra en alojamiento `Ø8.00` del Plano 14 |
| Agujero transversal 1 (`z_pas1`, `d_pasador`) | `7.50 mm`, `Ø4.00 mm` | plano | alta | Pasante transversal en tramo `Ø12.00` |
| Agujero transversal 2 (`z_pas2`, `d_pasador`) | `52.50 mm`, `Ø4.00 mm` | plano | alta | Pasante transversal en tramo `Ø12.00` (separación `45.00 mm` respecto de `z_pas1`) |
| Agujero transversal 3 (`z_pas3`, `d_pasador`) | `119.50 mm`, `Ø4.00 mm` | plano | alta | Pasante transversal en espiga `Ø7.97` (`7.50 mm` desde el hombro `z=112.00`) |
| Chaflanes (`c_chaf`) | `0.50 x 45°` | plano | alta | 4 indicaciones `.50 X 45.0°` en extremos y escalones |

## 5. Verificación de coherencia
- **Coherencia axial y angular entre `Transmisor_1_02a` y `Transmisor_2_02b` (resolución de pasadores):**
  - En `Transmisor_2_02b`, los dos primeros agujeros transversales de `Ø4.00 mm` están en `z_pas1 = 7.50 mm` y `z_pas2 = 52.50 mm`, con una separación axial entre centros de exactamente **`52.50 - 7.50 = 45.00 mm`**.
  - En `Transmisor_1_02a`, las cotas axiales `67.50` y `112.50` están separadas entre sí exactamente **`112.50 - 67.50 = 45.00 mm`**. Estas dos cotas corresponden a las líneas de centro de los **dos agujeros pasantes transversales** en el cuerpo de `Ø20.00 mm`.
  - Cuando el `Transmisor_2_02b` penetra en el alojamiento `Ø12.00 mm` de `Transmisor_1_02a` hasta que su hombro de `Ø13.00 mm` (`z = 67.00 mm` de `02b`) hace tope contra la cara derecha (`z = 127.00 mm` de `02a`):
    - La posición axial del origen de `02b` respecto de `02a` es `z = 127.00 - 67.00 = 60.00 mm`.
    - Pasador 1: `60.00 + 7.50 = 67.50 mm` (coincide con cota `67.50` de `02a`, error `0.00 mm`).
    - Pasador 2: `60.00 + 52.50 = 112.50 mm` (coincide con cota `112.50` de `02a`, error `0.00 mm`).
    - El fondo del alojamiento en `02a` se fija en `z = 59.00 mm` (profundidad `127.00 - 59.00 = 68.00 mm`), garantizando `1.00 mm` de desahogo para que el extremo de `02b` no toque fondo antes del hombro.
  - En el ensamblaje, la distancia Z de `Transmisor_1_02a` se posiciona en `off_transm_1 = 166.42 mm` (coincidente con `off_transm_2 - 60.00 mm = 106.42 + 60.00 = 166.42 mm`), logrando alineación coaxial y angular perfecta entre ambos pasadores.
- **Ambigüedad `Ø10.00` vs `Ø12.00` en `Transmisor_1_02a`:** en la vista longitudinal superior se acota `Ø10.00` sobre el tramo intermedio (`z = 15..47`), mientras que en la vista lateral izquierda se acota `Ø12.00` apuntando al círculo de líneas ocultas (el alojamiento interior `d_aloj_int = 12.00 mm` para recibir el eje de `Ø12.00 mm` del `Transmisor_2_02b`). En la tabla de parámetros se incluyen ambos alias (`d_med = 12.00 mm` y `d_int_10 = 10.00 mm`).
- **Coherencia de `Transmisor_2_02b` con el Adaptador de rodamiento (Plano Nº 3) y el Tornillo sin fin (Plano Nº 14):**
  - El escalón de `Ø13.00 mm` (`5.00 mm` de largo) pasa con `0.10 mm` de holgura diametral por el agujero pasante `Ø13.10 mm` (`5.00 mm` de espesor) del Adaptador de rodamiento (Plano Nº 3).
  - El collar de `Ø15.00 mm` tiene el mismo diámetro nominal que el rebaje interior `Ø15.00 mm` bajo el rodamiento del Plano Nº 3 (¡atención: sin holgura si entra en dicho rebaje!).
  - La espiga derecha `Ø7.97 mm` (largo `14.92 mm`, pasador `Ø4.00` a `7.50 mm` del hombro) coincide con el alojamiento `Ø8.00 mm` (profundidad `15.00 mm`, pasador a `7.50 mm`) del Tornillo sin fin (Plano Nº 14), dejando `0.08 mm` de holgura axial (`15.00 - 14.92`) para asegurar el tope en el hombro.

## 6. Supuestos y dudas (máx. 5, priorizadas)
1. **Diámetro del tramo intermedio (`z = 15..47 mm`) en `Transmisor_1_02a`:** ¿El diámetro exterior de ese tramo es `Ø10.00 mm` (según cota vertical izquierda) o `Ø12.00 mm`?
2. **Interferencia entre el collar `Ø15.00 mm` de `Transmisor_2_02b` y el rebaje `Ø15.00 mm` del Adaptador de rodamiento (Plano Nº 3):** ¿El collar trabaja fuera del adaptador o penetra en el rebaje de `Ø15.00 mm` (en cuyo caso rozaría nominalmente)?

## 7. Detalles pendientes de modelar
Ninguno: se modelan todos los cilindros escalonados, los chaflanes de `0.50 x 45°` mediante conos paramétricos (`Pieza.cono`, sin depender de índices de arista), el alojamiento interior y los agujeros transversales (`Pieza.cil_x`).

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Falta de tolerancias ISO 286 en el asiento del rodamiento 6201 (`Ø12.00`), pista de retén (`Ø14.00`) y enchufe telescópico (`Ø12.00`) | Especificar `Ø12.00 k5` o `js6` en el asiento del rodamiento 6201, `Ø14.00 h8` (acabado $R_a \le 0.4\,\mu\text{m}$, sin marcas de hélice de torno) en la pista del retén `14x30x7`, y `H7/g6` en el acople entre Transmisor 1 y 2 | Alto (evita juego radial, fugas en el retén y fretting en el rodamiento) | Bajo | propuesta |
| 2 | Los chaflanes de entrada a `45°` en la pista de `Ø14.00` pueden cortar el labio elastomérico del retén `14x30x7` durante el montaje | Reemplazar el chaflán de `0.50 x 45°` en `z = 112.00 mm` por un chaflán de entrada suave a `15°–20°` con bordes redondeados según DIN 3760 / catálogo SKF | Alto (vida útil y estanqueidad del retén) | Bajo | propuesta |
| 3 | Agujeros transversales de `Ø4.00 mm` en espiga de `Ø7.97 mm` reducen la sección resistente en más del 50% en la zona de mayor concentración de tensiones | Usar pasador elástico espiralado (DIN 7343) de `Ø3.00 mm` o chaveta/prisionero con plano si el par transmitido es moderado | Medio (resistencia a fatiga torsional) | Bajo | propuesta |
| 4 | Igualdad nominal (`Ø15.00 mm`) entre el collar de `Transmisor_2_02b` y el rebaje del Adaptador de rodamiento (Plano Nº 3) | Reducir el diámetro del collar de `Transmisor_2_02b` a `Ø14.50 mm` o ampliar el rebaje del Plano Nº 3 a `Ø16.00 mm` para garantizar holgura radial sin rozamiento | Alto (evita engrane/roce en rotación) | Bajo | propuesta |
