# FICHA DE DISEÑO - Adaptador del eje (Plano Nº 4)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 53, **Plano Nº 4 - Adaptador del eje**, Escala 2:1):
  - Vista superior (planta con círculo de agujeros), vista frontal con líneas ocultas y **Sección K-K** (Escala 2:1, plano de corte quebrado que pasa por un agujero roscado a `45°` y un agujero pasante a `270°`).
- Especificación del proyecto: pieza fabricada en **Delrin (POM-C / Poliacetal)**.

## 2. Función y contexto
Anillo adaptador / espaciador aislante en Delrin (POM-C) que se interpone coaxialmente entre el Adaptador de rodamiento (Plano Nº 3) y el cuerpo/soporte del conjunto de transmisión. Su agujero central de `Ø40.10 mm` aloja con holgura (`0.10 mm` diametral) el cuerpo escalonado de `Ø40.00 mm` del Adaptador de rodamiento (Plano Nº 3). Posee una corona de `Ø50.00 mm` con dos patrones alternados cada `45°`:
- **4 agujeros pasantes de `Ø3.10 mm` (a `0°, 90°, 180°, 270°`)** con cajeado superior de `Ø4.50 x 5.00 mm` y pequeño rebaje inferior de `Ø4.50 x 0.70 mm` para paso de tornillos M3.
- **4 agujeros roscados ciegos `M3x0.5 - 6H` (a `45°, 135°, 225°, 315°`)** de `5.00 mm` de profundidad útil.

## 3. Datos generales
Material: Delrin / POM-C (Poliacetal, densidad $\approx 1.41\,\text{g/cm}^3$) | Proceso previsto: Torneado + taladrado y roscado en fresadora/CNC | Cantidad: 1 | Tolerancias: rosca `6H`, resto sin tolerancia explícita en plano | Acabado: mecanizado estándar.

## 4. Cotas y elementos
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior (`d_ext`) | `Ø57.00 mm` | plano | alta | Tipo `L` |
| Diámetro interior (`d_int`) | `Ø40.10 mm` | plano | alta | Tipo `H`; recibe el escalón `Ø40.00` del Plano Nº 3 |
| Altura total (`h_total`) | `16.50 mm` | plano | alta | Tipo `L`; en vista frontal |
| Círculo de agujeros (`d_cor`) | `Ø50.00 mm` | plano | alta | Tipo `L`; común a los 8 agujeros (ver sección 5) |
| Agujeros pasantes (4x a `0°, 90°, 180°, 270°`) (`d_paso`) | `Ø3.10 mm` | plano | alta | Tipo `H`; en Sección K-K |
| Diámetro cajeado agujeros pasantes (`d_caj`) | `Ø4.50 mm` | plano | alta | Tipo `H`; en vista superior |
| Profundidad cajeado superior (`p_caj`) | `5.00 mm` | supuesto | media | Dibujado en líneas ocultas en vista frontal a igual nivel (`5.00 mm`) que las roscas M3 |
| Profundidad rebaje inferior (`p_reb_inf`) | `0.70 mm` | plano | alta | Cota `.70` en Sección K-K |
| Roscas M3x0.5 - 6H (4x a `45°, 135°, 225°, 315°`) (`d_m3`) | `M3x0.5` (`Ø3.00`, mecha `Ø2.50`) | plano + norma | alta | Tipo `R` |
| Profundidad roscas M3 (`p_m3`) | `5.00 mm` | plano | alta | Acotado `M3x0.5 ↧ 5.00` en planta y `5.00` en Sección K-K |
| Chaflán interior inferior (`c_chaf`) | `0.50 x 45°` | plano | alta | Indicado `.50 X 45.0° CHAMFER` en Sección K-K y `.50` en vista frontal |

## 5. Verificación de coherencia
- **Espesor de pared radial de la corona:**
  - Radio interior: `40.10 / 2 = 20.05 mm`; radio exterior: `57.00 / 2 = 28.50 mm` → espesor radial del anillo = **`8.45 mm`**.
  - Los agujeros están centrados en el radio `50.00 / 2 = 25.00 mm`.
  - Para el cajeado `Ø4.50 mm` ($r = 2.25\,\text{mm}$): pared hacia el interior = `25.00 - 20.05 - 2.25 = 2.70 mm`; pared hacia el exterior = `28.50 - 25.00 - 2.25 = 1.25 mm`. Queda pared continua sin romper el cilindro interior ni el exterior.
- **Cajeado `Ø4.50 mm` vs cabeza de tornillo M3 estándar:**
  - Un tornillo cilíndrico con hexágono interior **DIN 912 / ISO 4762 M3** tiene diámetro de cabeza **`d_k = 5.50 mm`** (requiere cajeado estándar de `Ø6.00 mm` según DIN 974-1). En un cajeado de **`Ø4.50 mm`** **no entra la cabeza de ningún tornillo M3 estándar** (salvo que se tornee la cabeza del tornillo a `Ø4.3 mm` o que el cajeado sea en realidad para alojar una espiga/buje tubular).
- **Discrepancia de círculo de agujeros con el Adaptador de rodamiento (Plano Nº 3):**
  - En el Plano Nº 4 la corona es de `Ø50.00 mm`, mientras que en el Plano Nº 3 es de `Ø49.00 mm` (ver Ficha del Plano Nº 3).
- **Roscas M3 en vista frontal vs Sección K-K:**
  - En la vista frontal las líneas ocultas de los agujeros ciegos roscados bajan `5.00 mm` desde la cara superior, mientras que en la Sección K-K el agujero roscado aparece en la cara derecha (`5.00 mm`) y el rebaje de `0.70 mm` también en la cara derecha. Modelar los agujeros roscados `M3x0.5` de `5.00 mm` de profundidad en ambas caras (superior e inferior, a `45°, 135°, 225°, 315°`) deja un tabique central macizo de `16.50 - 2 * 5.00 = 6.50 mm` y permite vincular desde ambos lados.

## 6. Supuestos y dudas (máx. 5, priorizadas)
1. **Diámetro de cajeado `Ø4.50 mm` para tornillo M3:** ¿Se rebaja la cabeza de los tornillos M3 en torno o ese cajeado de `Ø4.50 mm` cumple otra función? (Si se amplía a `Ø6.00 mm` en corona de `Ø50.00 mm`, la pared exterior en `Ø57.00 mm` quedaría de solo `0.50 mm`).
2. **Corona `Ø50.00 mm` (Plano 4) vs `Ø49.00 mm` (Plano 3):** Confirmar cuál de las dos cotas rige para todo el subconjunto.
3. **Roscas `M3x0.5` en una o ambas caras:** En la vista superior se acota dos veces `M3x0.5 ↧ 5.00` sobre agujeros opuestos de la corona; confirmar si lleva 4 roscas en una sola cara o 4 en cada cara (8 roscas en total).

## 7. Detalles pendientes de modelar
Ninguno: el anillo, el chaflán interior inferior de `0.50 x 45°`, los 4 agujeros pasantes con su cajeado de `5.00 mm` y rebaje de `0.70 mm`, y las roscas `M3x0.5` en ambas caras están completamente modelados de forma paramétrica.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Roscas `M3x0.5` de solo `5.00 mm` de profundidad directamente sobre Delrin (POM-C) tienen baja resistencia al arrancamiento y se barren con facilidad | Aumentar la profundidad roscada a `8.00–10.00 mm` ($2.5\text{–}3\times d$ para polímeros) o colocar insertos roscados tipo Helicoil / autorroscantes Ensat M3 | Alto (durabilidad ante arme y desarme) | Bajo | propuesta |
| 2 | El cajeado de `Ø4.50 mm` no admite cabezas de tornillos Allen M3 estándar (`Ø5.50 mm`) y el exterior `Ø57.00 mm` deja poca pared si se agranda el cajeado | Si el entorno lo permite, unificar la corona en `Ø49.00 mm` (igual al Plano Nº 3) y llevar el diámetro exterior de `Ø57.00` a `Ø59.00 mm` para admitir cajeados estándar de `Ø6.00 mm` para DIN 912 M3 | Alto (permite usar bulonería comercial sin retrabajar cabezas) | Medio | propuesta |
