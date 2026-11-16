# Guía de Impresión 3D y Configuración Espacial — Lote STL

**Proyecto:** Bomba de Flujo Cardíaco (`Piloto_Impresion_3D_Assembly.FCStd`)  
**Carpeta de salida:** `proyectos/bomba_flujo_cardiaco/stl/`  
**Script generador:** [`exportar_stl_3d.py`](../piezas/exportar_stl_3d.py)  
**Alcance del lote:** **24 archivos `.stl` binarios** que totalizan **38 piezas impresas**.

---

## 1. Convención Espacial y Alcance del Lote

- **Pre-orientación integrada en los `.stl`:** Todas las mallas se exportaron con la cara de apoyo óptima orientada hacia la cama (`RotX = 0°` o `RotX = 180°`), centradas en **XY = `(0, 0)`** y apoyadas exactamente en **`Z_mín = 0.00 mm`**. Salvo las alternativas horizontales comentadas para los ítems `#11` y `#12`, los archivos se cargan en el laminador **listos para cortar sin rotarlos**.
- **Calidad de malla validada (`STL_VALIDACION: OK`):** Triangulación binaria adaptativa (`0.02/0.10 mm` en 21 piezas, `0.03/0.15 mm` en `#14` y `0.04/0.20 mm` en `#21` y `#22`) para evitar auto-intersecciones en puentes y puntas cónicas. Todas pasan `isSolid = True`, `1` componente, sin bordes no múltiples ni auto-intersecciones, y error volumétrico respecto al sólido CAD `< 0.2%`.
- **Calibración FDM incorporada:**
  - Geometría general dimensionada con holgura FDM de `0.20 mm` en agujeros y encastres.
  - Rosca FDM calibrada integrada en `#11 Guia_08_3D` (`holgura_fdm = 0.42 mm`, paso `1.25 mm`) y `#31 Tuerca_Guia_08_3D` (`holgura_fdm = 0.50 mm`, paso `1.25 mm`).
- **Exclusiones (ítems comerciales):** No se incluyen `#02 Cilindro_09_3D` (tubo de vidrio comercial) ni bulonería, tuercas comerciales, arandelas metálicas, rodamientos, retenes, imán y O-Rings (`#24..#30` y `#33..#40`).
- **Tapas principales ya impresas:** Se incluyen `#01 X1-Tapa_Exterior_16a_3D_Item01.stl` y `#03 X1-Tapa_Interior_16b_3D_Item03.stl` para mantener el juego completo de archivos del ensamblaje, aunque ya cuentan con impresión física previa.

---

## 2. Tabla Maestra de Archivos y Parámetros de Impresión

> **Nomenclatura:** `Xn-Nombre_pieza_ItemNN.stl`, donde `Xn` indica la cantidad exacta de copias requeridas por `Lista_de_Materiales` de `Piloto_Impresion_3D_Assembly.FCStd`.  
> **Pesos teóricos:** Calculados a partir del volumen de malla (`100%` sólido en PLA `1.24 g/cm³`). En piezas configuradas al `40–50%` de relleno, el consumo real será menor.

| Ítem | Archivo STL | Cant. | Dimensiones X×Y×Z (mm) | Orient. STL | Soportes | Adhesión / Brim | Altura de capa | Perímetros / Relleno | Vol. (mm³) | PLA 100% (u. / lote) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **01** | `X1-Tapa_Exterior_16a_3D_Item01.stl` | X1 | 120.80 × 120.78 × 22.65 | `0°` | No | Falda / Brim opcional | 0.20 mm | ≥5 perím. / ≥40% giroide | 182724.7 | 226.6 g / 226.6 g |
| **03** | `X1-Tapa_Interior_16b_3D_Item03.stl` | X1 | 120.80 × 120.78 × 22.65 | `180° X` | No *(1)* | Falda / Brim opcional | 0.20 mm | ≥5 perím. / ≥40% giroide | 172393.0 | 213.8 g / 213.8 g |
| **04** | `X1-Sufridera_Int_05b_3D_Item04.stl` | X1 | 33.98 × 33.97 × 7.12 | `0°` | No | Falda | 0.16 mm | ≥5 perím. / ≥50% | 3592.9 | 4.5 g / 4.5 g |
| **05** | `X1-Tapa_Sufridera_Int_05a_3D_Item05.stl` | X1 | 33.97 × 33.96 × 1.51 | `0°` | No | Falda | 0.12–0.16 mm | 100% sólido | 1160.5 | 1.4 g / 1.4 g |
| **06** | `X2-Sufridera_Guia_05b_3D_Item06.stl` | X2 | 15.10 × 15.10 × 2.27 | `0°` | No | Brim 5 mm (pieza chica) | 0.12–0.16 mm | 100% sólido | 230.7 | 0.3 g / 0.6 g |
| **07** | `X1-Embolo_Delrin_10_3D_Item07.stl` | X1 | 75.71 × 75.71 × 15.10 | `0°` | **Sí** *(ranura)* | Falda | 0.16–0.20 mm | ≥5 perím. / ≥40% | 55015.8 | 68.2 g / 68.2 g |
| **08** | `X1-Centro_Embolo_1_11_3D_Item08.stl` | X1 | 33.98 × 33.97 × 18.72 | `0°` | No | Falda | **0.12–0.16 mm** | ≥5 perím. / 50–100% | 7002.1 | 8.7 g / 8.7 g |
| **09** | `X1-Centro_Embolo_2_12_3D_Item09.stl` | X1 | 33.97 × 33.96 × 3.78 | `0°` | No | Falda | 0.16 mm | 100% sólido | 2953.9 | 3.7 g / 3.7 g |
| **10** | `X2-Sensor_Piston_05b_3D_Item10.stl` | X2 | 15.10 × 15.10 × 11.32 | `0°` | No | Brim 5 mm | 0.16 mm | ≥5 perím. / 100% | 1111.1 | 1.4 g / 2.8 g |
| **11** | `X2-Guia_08_3D_Item11.stl` | X2 | 8.22 × 8.22 × **220.65** | `180° X` | No *(o sí si 90°)* | **Brim ≥ 12 mm** | **0.12–0.16 mm** | ≥5 perím. / 100% | 11247.9 | 13.9 g / 27.9 g |
| **12** | `X1-Transmisor_A_02a_3D_Item12.stl` | X1 | 15.10 × 15.10 × 95.89 | `180° X` | No *(o sí si 90°)* | **Brim ≥ 8 mm** | 0.16 mm | ≥5 perím. / 100% | 8859.1 | 11.0 g / 11.0 g |
| **13** | `X1-Transmisor_B_02b_3D_Item13.stl` | X1 | 11.32 × 11.32 × 95.82 | `0°` | Opcional en Z=54.36 | **Brim ≥ 8 mm** | 0.16 mm | ≥5 perím. / 100% | 6550.8 | 8.1 g / 8.1 g |
| **14** | `X1-Tornillo_Sin_Fin_14_3D_Impresion_Item14.stl` | X1 | 27.00 × 27.00 × 192.15 | `0°` | **No** *(costillas)* | **Brim ≥ 10 mm** | **0.16 mm** | ≥5 perím. / 100% base, ≥50% resto | 16435.5 | 20.4 g / 20.4 g |
| **15** | `X1-Adaptador_Rodamiento_03_3D_Item15.stl` | X1 | 41.53 × 41.51 × 19.25 | `0°` | No | Falda | 0.16–0.20 mm | ≥5 perím. / 40–50% | 10118.3 | 12.5 g / 12.5 g |
| **16** | `X1-Sufridera_Eje_Ext_05a_3D_Item16.stl` | X1 | 30.20 × 30.19 × 9.81 | `0°` | No | Falda | 0.16 mm | 5 perím. / ≥50% | 2821.3 | 3.5 g / 3.5 g |
| **17** | `X1-Adaptador_Eje_04_3D_Item17.stl` | X1 | 42.52 × 43.02 × 12.46 | `0°` | No | Falda | 0.16 mm | ≥5 perím. / ≥50% | 8606.7 | 10.7 g / 10.7 g |
| **18** | `X2-Anillo_Torica_13_3D_Item18.stl` | X2 | 105.68 × 105.70 × 3.78 | `180° X` | No | Falda / Brim opcional | 0.16–0.20 mm | ≥5 perím. / 100% | 11999.5 | 14.9 g / 29.8 g |
| **19** | `X2-Estructura_Interior_07_3D_Item19.stl` | X2 | 138.16 × 138.16 × 15.10 | `0°` | No | Falda | 0.20 mm | ≥5 perím. / ≥40% giroide | 119879.2 | 148.7 g / 297.3 g |
| **20** | `X2-Cierre_Estructura_15_3D_Item20.stl` | X2 | 133.62 × 133.63 × 21.52 | `0°` | No | Falda | 0.20 mm | ≥5 perím. / ≥40% giroide | 83108.6 | 103.1 g / 206.1 g |
| **21** | `X4-Tensor_Parte_1_06_Item21.stl` | X4 | 16.60 × 16.60 × 181.81 | `180° X` | No | **Brim ≥ 10 mm** | 0.16–0.20 mm | ≥5 perím. / 50–100% | 32789.1 | 40.7 g / 162.6 g |
| **22** | `X4-Tensor_Parte_2_06_Item22.stl` | X4 | 18.11 × 18.11 × 139.09 | `0°` | No | **Brim ≥ 8–10 mm** | **0.16 mm** | ≥5 perím. / 50–100% | 34396.3 | 42.7 g / 170.6 g |
| **23** | `X1-Tapa_Motor_01_3D_Item23.stl` | X1 | 138.16 × 138.16 × 7.55 | `0°` | No | Falda | 0.20 mm | ≥5 perím. / ≥40% giroide | 131338.4 | 162.9 g / 162.9 g |
| **31** | `X2-Tuerca_Guia_08_3D_Item31.stl` | X2 | 15.01 × 13.00 × 6.00 | `0°` | No | Brim 5 mm | **0.12–0.16 mm** | 100% sólido | 621.7 | 0.8 g / 1.5 g |
| **32** | `X2-Arandela_Guia_08_3D_Item32.stl` | X2 | 13.19 × 13.19 × 4.00 | `0°` | No | Brim 5 mm | 0.16–0.20 mm | 100% sólido | 354.5 | 0.4 g / 0.9 g |

- **Totales del lote completo (24 archivos, 38 piezas):** `1335.42 cm³` (`1655.9 g` al 100% sólido PLA `1.24 g/cm³`).
- **Totales excluyendo `#01` y `#03` ya impresas (22 archivos, 36 piezas):** `980.30 cm³` (`1215.6 g` al 100% sólido PLA `1.24 g/cm³`).
- *(1)* En `#03 Tapa_Interior_16b_3D`, al estar invertida `180°`, las 2 cavidades poco profundas de arandela (`Ø13.59 × 1.74 mm`) y los 4 avellanados M2 quedan cerrando hacia arriba cerca de la cama y puentean limpio sin necesidad de soportes.

---

## 3. Piezas Pre-orientadas en el `.stl` (`RotX = 180°`)

Cinco piezas estaban diseñadas en el sistema de referencia del ensamblaje con su cara más ancha hacia `+Z` o con escalones/espigas que generarían voladizos si se imprimieran en `0°`. Se rotaron `180°` en X y se apoyaron en `Z = 0` directamente dentro del `.stl`:

1. **`#03 X1-Tapa_Interior_16b_3D_Item03.stl`:** Pone sobre la cama la cara plana de `10119.2 mm²`, eliminando ~7200 mm² de cavidades colgantes hacia abajo y dejando todos los pasos principales mirando hacia `+Z`.
2. **`#11 X2-Guia_08_3D_Item11.stl`:** Pone sobre la cama el extremo ancho `Ø8.22 mm` (`35.3 mm²`), elimina el escalón colgante de `Z = 22.65 mm` y deja la rosca FDM `p = 1.25 mm` arriba (`Z = 210.8..220.65 mm`) libre de soportes y de "pie de elefante".
3. **`#12 X1-Transmisor_A_02a_3D_Item12.stl`:** Apoya su cabeza plana `Ø15.10 mm` (`86.0 mm²`) sobre `Z = 0`; los escalones `Ø15.10 → Ø7.55 → Ø6.04 mm` se estrechan progresivamente hacia arriba con `0` voladizos.
4. **`#18 X2-Anillo_Torica_13_3D_Item18.stl`:** Apoya la cara plana completa (`3066.9 mm²`) en `Z = 0`, dejando los 4 avellanados abiertos hacia `+Z`.
5. **`#21 X4-Tensor_Parte_1_06_Item21.stl`:** Apoya el extremo plano `Ø16.61 mm` (`165.9 mm²`) en `Z = 0` y dirige la espiga triangular machihembrada (`R3.00 × 30 mm`) hacia arriba (`Z = 151.81..181.81 mm`), evitando cualquier soporte sobre caras de encastre.

---

## 4. Configuraciones Espaciales Críticas y Notas de Ingeniería

### 4.1 Piezas muy altas o esbeltas (cuidado de estabilidad y altura Z)

- **`#11 Guia_08_3D` (CRÍTICA — `220.65 mm` de altura, esbeltez `27:1`):**
  - **Altura de impresora:** Verifique que su impresora disponga de **recorrido útil `Z ≥ 225 mm`** antes de lanzar el trabajo.
  - **Estabilidad vertical:** Imprimir con **Brim ≥ 12 mm**, **Z-hop activo** (para que la boquilla no golpee la varilla al desplazarse), relleno **100%** (`≥ 5` perímetros), capa **`0.12–0.16 mm`** para resolver la rosca superior (`p = 1.25 mm`) y **velocidad reducida en el tercio superior (`≤ 30 mm/s`)**.
  - **Alternativa si `Z < 225 mm` o si vibra demasiado:** Acostar la pieza `90°` en diagonal sobre la cama y colocar soportes mínimos solo bajo el tramo fino superior (`Ø6.71 mm`). La rosca quedará ligeramente ovalada en la cara inferior y requerirá un repaso suave antes de probar la tuerca `#31`.
- **`#14 Tornillo_Sin_Fin_14_3D_Impresion` (`192.15 mm`):**
  - Se exportó desde `Tornillo_Sin_Fin_14_3D_Impresion.FCStd`, variante preparada específicamente para FDM con zapata anular inferior (`r = 13.5 mm`, `539.5 mm²`) y **3 costillas estabilizadoras verticales** (`Z = 0..90 mm`) unidas por puentes fusibles en `Z = 0.4, 30, 60 y 89.2 mm`.
  - **No active soportes** en el laminador (el soporte ya forma parte de la malla). Use capa **`0.16 mm`**, **Brim ≥ 10 mm**, `≥ 5` perímetros, **100% de relleno en la base (`Z = 0..15 mm`)** y `≥ 50%` en el resto, con velocidad moderada en altura.
  - Al finalizar, rompa suavemente las 3 costillas por los puentes fusibles con pinza alicate y lime cualquier resto mínimo fuera del filete helicoidal.
- **`#21 Tensor_Parte_1_06` (`181.81 mm`) y `#22 Tensor_Parte_2_06` (`139.09 mm`):**
  - Par bipartido unido por espiga/cavidad triangular de `30 mm` (`R3.00` en `#21`, `R3.25` en `#22`) atravesado luego por tirante `M6`.
  - `#21` se apoya plano en `Z = 0` con la espiga apuntando hacia arriba (`0` soportes). `#22` se apoya en `Z = 0` (`165.9 mm²`) con la cavidad triangular abierta hacia arriba (`0` soportes internos); el escalón externo de `0.755 mm` en `Z = 14.35 mm` incorpora chaflán `0.38 mm`, imprimible sin soportes en capa `0.16 mm`.
  - Obligatorio **Brim ≥ 8–10 mm**, `≥ 5` perímetros y `50–100%` de relleno por trabajar bajo compresión axial del tensor.

### 4.2 Soportes puntuales y roscas FDM

- **`#07 Embolo_Delrin_10_3D` (Única pieza con soporte obligatorio en modo vertical):**
  - La ranura periférica de O-Ring entre `Z = 4.95` y `Z = 10.15 mm` presenta un vuelo radial de `3.06 mm` (`698.2 mm²` de techo).
  - Configure el laminador en **"Soportes: Solo tocando la cama / Touching Buildplate"** de modo que apoyen únicamente la ranura exterior, sin rellenar agujeros internos. Use `≥ 40%` relleno y `5` perímetros. Limpie con cuidado cualquier resto de interfaz en el canal del O-Ring.
- **`#08 Centro_Embolo_1_11_3D` y `#31 Tuerca_Guia_08_3D` (Roscas FDM):**
  - `#08` tiene rosca trapezoidal vertical a `90°` (`flanco 45°`, paso `3.00 mm`) que imprime sin soportes desde su brida base (`664.7 mm²`), y `#31` tiene rosca interna triangular FDM paso `1.25 mm`. Ambas requieren **capa fina `0.12–0.16 mm`** (`≥ 5` perímetros y `50–100%` relleno en `#08`; `100%` sólido en `#31`).
- **`#12 Transmisor_A_02a_3D` (`95.89 mm`) y `#13 Transmisor_B_02b_3D` (`95.82 mm`):**
  - Verticales con **Brim ≥ 8 mm**, **100% relleno / ≥ 5 perímetros** y capa `0.16 mm`. Los agujeros transversales `Ø3.02 mm` de `#12` puentean sin soporte. En `#13`, los escalones pequeños `0.38 / 0.75 mm` a `Z = 50.6` y `54.4 mm` requieren buena ventilación de capa (o soporte tipo árbol opcional bajo `Z = 54.36 mm`).
  - *Alternativa de resistencia para `#12`:* Si este prototipo va a transmitir par/empuje real en plástico, puede tumbarse `90°` con soportes mínimos para orientar los filamentos longitudinalmente y evitar delaminación por flexión.

### 4.3 Piezas delgadas, sufrideras, tapas y subconjunto de acoplamiento

- **Piezas delgadas al 100% sólido:** `#05 Tapa_Sufridera_Int_05a_3D` (`1.51 mm`), `#06 Sufridera_Guia_05b_3D` (`2.27 mm`), `#09 Centro_Embolo_2_12_3D` (`3.78 mm`), `#18 Anillo_Torica_13_3D` (`3.78 mm`) y `#32 Arandela_Guia_08_3D` (`4.00 mm`) deben ir al **100% de relleno** para trabajar a compresión sin aplastarse.
  - *Nota sobre `#06 Sufridera_Guia_05b_3D`:* Aunque antiguos archivos STEP la nombraban `x4`, en el diseño actualizado del ensamblaje se utilizan **2 unidades (`X2`)** en el lado `-Z` junto con 2 O-Rings `#40`; en el lado `+Z` trabajan las `2× #32 Arandela_Guia_08_3D`.
- **Acoplamiento eje-motor (`#15`, `#16`, `#17`):**
  - Todas imprimen sin soportes (`#15` puentea limpio su canal interno de O-Ring de `0.95 mm`; `#16` se escalona hacia arriba; `#17` tiene sus 4 alojamientos `M2×14` a `45°` y sus 4 pilotos ciegos `Ø1.85` a `22.5°` abiertos hacia `+Z`).
  - *Recordatorio de armado:* `#15 Adaptador_Rodamiento_03_3D` se fija desfasado `+22.5°` respecto a `#17 Adaptador_Eje_04_3D`.
- **Anillos y tapas principales (`#01`, `#03`, `#04`, `#19`, `#20`, `#23`):**
  - Sin soportes, `≥ 5` perímetros y `≥ 40%` de relleno giroidal (`≥ 50%` en `#04` por alojar el retén `10×22×7` en `Ø22.40 mm`).

---

## 5. Piezas Mockup 3D vs. Materiales Definitivos en la Bomba Real

Los siguientes `.stl` se incluyen para armar y validar geométricamente el prototipo completo impreso, pero en la bomba funcional definitiva deben mecanizarse en su material de diseño:

| Ítem | Pieza | Rol del STL | Material definitivo de ingeniería |
| :---: | :--- | :--- | :--- |
| **07** | `Embolo_Delrin_10_3D` | Mockup dimensional 3D | **Delrin / POM-C mecanizado CNC** (baja fricción contra cilindro de vidrio) |
| **10** | `Sensor_Piston_05b_3D` (×2) | Mockup dimensional 3D | **Acero inoxidable ferrítico magnético AISI 430** (disparo del sensor inductivo) |
| **11** | `Guia_08_3D` (×2) | Versión funcional FDM (rosca calibrada `0.42 mm`) | Alternativa metálica en **AISI 304/316L** |
| **12** | `Transmisor_A_02a_3D` | Mockup dimensional 3D | **Acero inoxidable AISI 304/316L** |
| **13** | `Transmisor_B_02b_3D` | Mockup dimensional 3D | **AISI 304/316L** con acabado de torno `Ø9.00 k5` / `Ø10.00 h9` |

---

## 6. Lotes Recomendados por Cama y Post-procesado

1. **Lote A — Estructurales y tapas (`0.20 mm`, 5 perím., ≥40% giroide):** `#19 (×2)`, `#20 (×2)`, `#23 (×1)`, `#18 (×2 al 100%)` *(y opcional `#01`, `#03` si desea reimprimirlas)*.
2. **Lote B — Mecánica media de precisión (`0.16 mm`, 5 perím.):** `#04`, `#05`, `#06 (×2)`, `#08`, `#09`, `#10 (×2)`, `#15`, `#16`, `#17`, `#31 (×2)`, `#32 (×2)`; más `#07` en tanda propia o con soportes bloqueados en el centro y activos solo tocando la cama bajo su ranura periférica.
3. **Lote C — Columnas altas y esbeltas (imprimir individualmente o en pares bien espaciados, con Brim ancho y velocidad conservadora):** `#14` (`192.15 mm`), `#11 (×2)` (`220.65 mm`), `#12`, `#13`, `#21 (×4)`, `#22 (×4)`.

### Checklist de post-procesado antes del armado
- Retirar completamente el *brim* en bases de rosca y caras de apoyo (`#11`, `#12`, `#13`, `#14`, `#21`, `#22`, `#31`, `#32`).
- Separar con cuidado las 3 costillas estabilizadoras del `#14 Tornillo_Sin_Fin_14_3D_Impresion`.
- Limpiar rebabas en la ranura periférica del `#07 Embolo` antes de montar el O-Ring.
- Verificar antes de apretar en máquina el roscado manual de `#11 + #31` (`Guia + Tuerca_Guia`) y el encastre triangular `#21 + #22` (`Tensor 1 + 2`).
