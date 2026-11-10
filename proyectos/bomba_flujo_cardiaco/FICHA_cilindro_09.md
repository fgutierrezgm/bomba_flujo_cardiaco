# FICHA DE DISEÑO - Cilindro (Plano Nº 9)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (pág. 59, Plano Nº 9 "Cilindro"): vista frontal y vista lateral longitudinal.
- Memoria descriptiva del informe (pág. 4/48): especifica que el cilindro es un tubo de vidrio borosilicato de `Øint 103.00 mm`, `Øext 110.50 mm` (espesor de pared `e = 3.75 mm`) y longitud `L_tubo = 250.00 mm`.

## 2. Función y contexto
Camisa cilíndrica transparente de la cámara de bombeo principal. Se aloja axialmente entre las cavidades de `Ø110.50 mm` de la Tapa Exterior (Plano 16a) y la Tapa Interior (Plano 16b), quedando comprimida por las varillas tensoras exteriores. En su interior (`Ø103.00 mm`) se desplaza alternativamente el émbolo de Delrin (`Ø102.00 mm`, Plano 10) con su junta tórica de Viton (`97 x 3.5 mm`), permitiendo visualizar el flujo y posibles burbujas durante los ensayos hemodinámicos.

## 3. Datos generales
Material: Vidrio borosilicato (densidad `2.23 g/cm³` = `0.00000223 kg/mm³`) | Proceso previsto: corte a medida y rectificado/pulido de frentes a partir de tubo comercial | Cantidad: 1 | Tolerancias: no indicadas en plano | Acabado: pulido óptico propio del tubo de vidrio.

## 4. Cotas y elementos
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Diámetro exterior (`d_ext`) | `Ø110.50 mm` | plano | alta | Encastra en la Cavidad 2 (`Ø110.50 mm`) de las tapas 16a y 16b |
| Diámetro interior (`d_int`) | `Ø103.00 mm` | plano | alta | Diámetro de carrera para el émbolo (`Ø102.00 mm` + o-ring) |
| Longitud total (`l_tubo`) | `250.00 mm` | plano | alta | Longitud axial entre fondos de asiento de las tapas |
| Espesor de pared | `3.75 mm` | calculado | alta | `(110.50 - 103.00) / 2 = 3.75 mm` |

## 5. Verificación de coherencia
- **Coherencia radial:** `(d_ext - d_int) / 2 = (110.50 - 103.00) / 2 = 3.75 mm` de espesor de pared uniforme.
- **Interfaz con tapas (Planos 16a / 16b):** La Cavidad 2 de las tapas mide exactamente `Ø110.50 mm` nominales, lo que supone un ajuste con juego nulo (`0.00 mm` nominal) frente al `Ø110.50 mm` exterior del tubo de vidrio. Dado que los tubos de vidrio borosilicato tienen tolerancia dimensional de extrusión/soplado ($\pm 1.0\text{ a }\pm 1.5\text{ mm}$) y son frágiles, el contacto directo vidrio-metal sin holgura ni junta elástica es crítico.
- **Interfaz con émbolo (Plano 10):** El émbolo tiene `Ø102.00 mm`, dejando una huelga diametral de `1.00 mm` (`0.50 mm` radial por lado) respecto de `Ø103.00 mm`, adecuada para que el contacto sea exclusivamente a través de la junta tórica y los bujes guía.
- **Observación de escala en rótulo:** El rótulo indica `Escala 2:1`, pero una pieza de `250 mm` a escala `2:1` mediría `500 mm` (no entra en hoja A4/A3); la representación gráfica real está reducida (~`1:1.5` o `1:2`).

## 6. Supuestos y dudas (priorizadas)
1. **Tubo comercial estándar vs medida del plano:** Los tubos estándar de borosilicato (Duran / Simax) suelen fabricarse en `Ø110 x 3.2 mm` (`Øint 103.6 mm`) o `Ø110 x 4.0 mm` (`Øint 102.0 mm`). ¿Las cotas `110.50 / 103.00 mm` fueron relevadas de un tubo real existente en el laboratorio?
2. **Sellado y apoyo axial en las tapas:** ¿Se interpone una junta plana de goma/silicona u o-ring en el fondo de la cavidad de `Ø110.50 mm` de las tapas 16a y 16b para evitar el contacto rígido vidrio-metal al apretar los tensores?
3. **Biselado de cantos:** Aunque el plano muestra aristas vivas en los extremos, el vidrio cortado requiere un bisel o matado de cantos (p. ej. `0.5 x 45°`) para evitar astilladuras en el montaje.

## 7. Detalles pendientes de modelar
Ninguno: la geometría del plano está íntegramente representada.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | Ajuste nominal `Ø110.50 / Ø110.50` entre tubo de vidrio y cavidad metálica de las tapas (riesgo de rotura por ovalización o dilatación térmica) | Ampliar la cavidad en tapas a `Ø112.0 mm` e incorporar asiento de elastómero (junta plana en el fondo + o-ring radial) para absorber tolerancias del vidrio y asegurar estanqueidad | Muy alto (integridad estructural y sellado) | Medio | propuesta |
| 2 | Fragilidad del vidrio borosilicato ante golpes o sobretensión de los tensores | Evaluar alternativa en tubo de **PMMA (acrílico colado)** o **policarbonato** torneado/pulido si la presión de trabajo es baja (fisiológica < 0.3 bar), o limitar el par de apriete con topes mecánicos | Alto (seguridad en laboratorio) | Bajo | propuesta |
| 3 | Cantos vivos en extremos del tubo de vidrio | Especificar en plano biselado perimetral interior/exterior de `0.5 x 45°` pulido al fuego o con piedra diamantada | Medio (evita fisuras de borde) | Bajo | propuesta |
