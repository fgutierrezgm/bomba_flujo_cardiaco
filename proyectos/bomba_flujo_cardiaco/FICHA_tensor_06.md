# FICHA DE DISEÑO - Tensor (Plano Nº 6)
Proyecto: bomba de simulación de flujo cardíaco | Estado: borrador, sin revisar con el usuario

## 1. Entradas utilizadas
- `entradas/informe_y_planos_bomba.pdf` (página 56, correspondiente al **Plano Nº 6 - Tensor**, Escala 1:1.5, con vista longitudinal general y `DETAIL A` en Escala 1:1).
- Datos del proyecto: **4 barras tensoras de aluminio** (`Ø22.00 x 434.00 mm`) ubicadas en las 4 esquinas de las placas de estructura (`Estructura_Interior_07`).

## 2. Función y contexto
Columnas/barras estructurales cilíndricas (4 unidades por bomba) de `Ø22.00 mm` y `434.00 mm` de longitud total que vinculan y mantienen la separación axial entre las placas estructurales del equipo. Poseen roscas internas axiales **`M10x1.5`** en ambos extremos para fijación mediante bulones M10 desde las placas extremas.

## 3. Datos generales
Material: Aluminio (según memoria descriptiva del proyecto) | Proceso previsto: torno paralelo (frentado, perforado, roscado interior y chaflanado a partir de barra redonda comercial de `Ø22 mm` o `7/8"`) | Cantidad: 4 | Tolerancias: no indicadas en plano (ISO 2768-m) | Acabado: torneado estándar.

## 4. Cotas y elementos
| Elemento | Valor | Origen | Confianza | Nota |
|---|---|---|---|---|
| Longitud total (`l_total`) | `434.00 mm` | plano | alta | De extremo a extremo |
| Posición escalón/línea intermedia (`l_tramo1`) | `223.00 mm` | plano | alta | Ambos tramos acotados a `Ø22.00 mm`; sirve de referencia axial |
| Diámetro exterior (`d_ext`) | `22.00 mm` | plano | alta | Acotado en ambos extremos |
| Rosca interna en ambos extremos (`d_m10`) | `M10x1.5` | plano + norma | alta | Ø nominal `10.00 mm`, mecha `8.50 mm` |
| Profundidad roscada (`p_rosca`) | `16.00 mm` | plano | alta | En ambos extremos (`DETAIL A` y extremo derecho) |
| Profundidad agujero previo izquierdo (`p_aguj_izq`) | `19.00 mm` | plano | alta | En vista general izquierda (`z = 0..19 mm`) |
| Profundidad agujero extremo derecho (`p_aguj_der`) | `16.00 mm` | plano | alta | En vista general derecha (`z = 418..434 mm`) |
| Chaflanes exteriores e interiores (`c_ext`) | `0.50 x 45°` | plano | alta | En ambos extremos y en la boca de las roscas |

## 5. Verificación de coherencia
- **Línea divisoria a `223.00 mm` con chaflán `.50 x 45°` sin cambio de diámetro:**
  En la vista general del Plano Nº 6 aparece una línea transversal a `223.00 mm` del extremo izquierdo con la indicación `.50 X 45.0°`, pero el diámetro a izquierda y derecha es idéntico (`Ø22.00 mm`). Esto sugiere que en el modelo CAD original del alumno la barra se construyó uniendo dos extrusiones (`223 mm + 211 mm = 434 mm`) o marcando la posición intermedia de una placa estructural. En el modelo se conserva el conector `LCS_Centro_223` en `z = 223.00 mm` como referencia de ensamblaje.
- **Profundidad de perforación vs profundidad de rosca:**
  En el extremo izquierdo el agujero previo tiene `19.00 mm` y la rosca `16.00 mm` (`DETAIL A`), dejando `3.00 mm` de alivio para la punta de mecha y salida del macho. En el extremo derecho solo se acota `16.00 mm` tanto para el agujero como para la rosca.

## 6. Supuestos y dudas (máx. 5 dudas, priorizadas)
1. **Línea a `223.00 mm`:** ¿Es solo una referencia axial de posición de la `Estructura_Interior_07` o lleva una ranura/marca circunferencial física de `0.50 x 45°` para posicionar las placas durante el armado?
2. **Agujero previo derecho:** ¿Se perfora también a `19.00 mm` (o `20.00 mm`) de profundidad previa en el extremo derecho para permitir los `16.00 mm` de rosca útil `M10x1.5` con macho cónico/semicónico?

## 7. Detalles pendientes de modelar
Chaflanes internos de entrada de rosca (`0.50 x 45°`) y eventual marca a `223.00 mm`. Los chaflanes exteriores de ambos extremos (`0.50 x 45°`) y los agujeros axiales en ambos extremos están 100% modelados con primitivas paramétricas.

## 8. Propuestas de mejora
| # | Problema | Propuesta | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| 1 | En el extremo derecho el agujero ciego y la rosca `M10x1.5` tienen la misma profundidad (`16.00 mm`), imposible de lograr sin tocar fondo con el macho | Estandarizar en ambos extremos una perforación previa de mechas Ø8.50 mm a **`20.00 mm` de profundidad** para lograr `16.00 mm` de rosca útil con macho estándar | Alto (evita rotura de machos en aluminio) | Bajo | propuesta |
| 2 | La barra redonda lisa de `Ø22.00 mm` gira al apretar los bulones M10 de los extremos | Fresar dos planos paralelos para llave (`SW 19 mm`) cerca de los extremos de la barra | Medio (facilita el ajuste y desarme de la estructura) | Bajo | propuesta |
| 3 | En aluminio, `16.00 mm` de rosca `M10x1.5` equivale a `1.6 x D` (justo en el límite para tracción repetida) | Si se requiere desarme frecuente, llevar la rosca útil a `20.00 mm` (`2 x D`) con perforación previa de `25.00 mm` | Medio (mayor vida útil de la rosca en aluminio) | Bajo | propuesta |
