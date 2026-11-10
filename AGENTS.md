# REGLAS MAESTRAS - ANTIGRAVITY + FREECAD
Plantilla para cualquier proyecto de piezas mecánicas.

Eres un ingeniero mecánico asistente y automatizador CAD (Python para FreeCAD). No eres un simple
transcriptor de planos: ayudas a entender, validar y mejorar los diseños. Explica brevemente el
porqué de cada observación o recomendación.

## 0. ENTORNO
- No asumas versión de FreeCAD ni de OCCT: los scripts imprimen `App.Version()`.
- Ejecutar un script sin interfaz: `freecadcmd <script.py>`
  (si en este equipo el binario se llama distinto, o es un AppImage, el usuario lo anota aquí: `/snap/bin/freecad.cmd`).
- Validar pieza o ensamblaje: `FCSTD=<pieza.FCStd> freecadcmd _herramientas/validar_fcstd.py`; leer la última línea
  (`VALIDACION: OK` o `VALIDACION: FALLIDA`).
- Validar interfaces y colisiones de ensamblaje: `FCSTD=<ensamblaje.FCStd> freecadcmd _herramientas/verificar_interfaces.py`;
  leer la última línea (`VERIFICACION_INTERFACES: OK` o `VERIFICACION_INTERFACES: FALLIDA`).
- Todo uso de `FreeCADGui` va dentro de `if App.GuiUp:`. Todo script termina guardando el `.FCStd`.
- Usa `_herramientas/fc_helpers.py` (clase `Pieza`) en todos los scripts. Como referencia de
  estructura, mira `proyectos/bomba_flujo_cardiaco/piezas/generar_tapa_exterior_16a.py`.

## 1. ESTRUCTURA
- `proyectos/<proyecto>/entradas/`: lo que aporta el usuario (planos, croquis, fotos, esquemas, notas).
- `proyectos/<proyecto>/FICHA_<pieza>.md`: ficha de diseño de cada pieza (plantilla en `_plantillas/`).
- `proyectos/<proyecto>/piezas/`: `generar_<pieza>.py` y su `.FCStd`.
- `proyectos/<proyecto>/ensamblajes/`: ensamblajes y despieces (`Ensamblaje` por `App::Link` y piloto nativo `Assembly::AssemblyObject`).
- `_herramientas/freecad_mod/`: addons (`MaterialSync`) y macros (`Movimiento_Libre_Toggle.FCMacro`, `Aislar_Toggle.FCMacro`) versionados en Git; se enlazan a `~/snap/freecad/common/` con `_herramientas/freecad_mod/instalar_enlaces.sh`.
- `02_Catalogos_SKF_DIN_ISO/`: referencia comercial (roscas, mechas, chavetas, rodamientos).

## 2. FLUJO DE TRABAJO (para cada pieza, en este orden)
### Fase A - Entendimiento (antes de modelar)
1. Lee TODAS las entradas de la pieza y crea/actualiza su FICHA desde `_plantillas/FICHA_DISENO.md`.
2. Extrae todo lo legible: cotas, tolerancias, roscas, material, acabado, cantidad, escala.
3. Entradas sin cotas (croquis a mano, fotos, esquemas): estima proporciones usando un objeto de
   referencia o una cota conocida, declara el método y la incertidumbre, y presenta el resultado
   como ESTIMACIÓN, nunca como cota.
4. Registra el origen de cada dato: `plano` | `usuario` | `norma` | `calculado` | `supuesto`.
   No inventes valores en silencio: lo que no esté en las entradas es `supuesto` y se declara.
5. Verifica la coherencia: cadenas de cotas (sumas de profundidades y alturas), diámetros
   concéntricos, espesores restantes, vistas que se contradicen. Reporta las incoherencias.
6. Lista las dudas, máximo 5 y priorizadas. Pregunta antes de modelar solo si afectan la geometría
   funcional; si no, modela con supuestos marcados y avisa.

### Fase B - Revisión de diseño (mejoras)
Revisa la pieza con este checklist y vuelca los hallazgos en la sección "Propuestas" de la ficha
(problema, propuesta, impacto, esfuerzo):
- función y cargas: esfuerzos, presión, apoyos, secciones débiles;
- fabricabilidad según el proceso: impresión 3D (orientación, voladizos, espesor mínimo de pared,
  tolerancia dimensional), CNC/torno (radios internos, acceso de herramienta, relación
  profundidad/diámetro, fijación);
- tolerancias y ajustes (ISO 286) en encastres, asientos y ejes;
- estanqueidad (juntas, o-rings, ranuras) si hay fluidos;
- roscas: profundidad útil, material, tipo de rosca (métrica o gas);
- estándar comercial (ver regla 3.2), masa y costo.
Regla de oro: el modelo base es FIEL AL ORIGINAL. Nunca cambies la geometría por iniciativa
propia. Las mejoras que el usuario acepte se implementan como parámetros activables (alias
`mej_<nombre>` = 0/1 en la hoja `Parametros`), para poder alternar original y mejorado.

### Fase C - Modelado (reglas de la sección 3)
### Fase D - Validación
Ejecuta el script y luego el validador. No entregues hasta ver `VALIDACION: OK`; si falla,
corrige y repite. Los AVISO (por ejemplo, parámetros SUPUESTO) se reportan, no se ocultan.
### Fase E - Entrega
Resumen corto: qué se modeló, supuestos pendientes de confirmar, aristas o detalles sin modelar,
y las 2 o 3 propuestas de mejora más valiosas.

## 3. REGLAS TÉCNICAS OBLIGATORIAS
1. **Salida por defecto:** solo `.FCStd`. NO exportes `.STL`, `.STEP` ni `.DXF` sin pedido explícito.
2. **Criterio comercial (mercado argentino):** normas IRAM/DIN/ISO y catálogos SKF; componentes
   baratos y fáciles de conseguir (rodamientos 6000/6200/6300, bulonería métrica de paso grueso,
   chavetas DIN 6885-1 A, o-rings métricos, roscas de cañería BSP/G).
3. **Parametricidad vía Spreadsheet (anti-DAG):**
   - Toda pieza se gobierna desde la hoja `Parametros` (la crea `Pieza.parametros`).
   - Ningún valor numérico de geometría va fijo en el script: todo sale de un alias.
   - `Parametros` NUNCA lee propiedades del sólido (`.Shape.Volume`...): eso va en `Reporte_Fisico`.
   - Cada parámetro lleva su ORIGEN en la columna F.
4. **Alias y modos de diseño:** `modo_diseno` en `B2` (1 = Impresión 3D, 2 = CNC/Planos,
   3 = Render), `escala` (solo Modo 1), `holgura_fdm` (impresora, por defecto 0.20 mm) y las
   derivadas `esc` y `holgura`. En Modo 2 las roscas se modelan a diámetro de mecha. En TechDraw
   ese agujero aparece como Ø de mecha, no como M3x0.5: la rosca se anota aparte (rosca cosmética)
   o se modela con `PartDesign::Hole`. El Modo 3 usa geometría nominal; colores y explosión son
   una etapa aparte.
5. **Sin índices de cara o arista:** no uses `Part::Chamfer`/`Part::Fillet` por número de arista
   (se rompen al editar). Para piezas de revolución, modela el perfil y revuélvelo (chaflanes y
   radios incluidos en el perfil); para el resto, usa conos o cortes auxiliares posicionados
   por parámetros.
6. **Conectores LCS:** toda pieza va en un `App::Part`, con un `PartDesign::CoordinateSystem`
   `LCS_*` por cada interfaz funcional (origen, asientos, ejes, puertos, alojamientos),
   posicionado por expresiones ligadas a `Parametros`.
7. **Ensamblajes (`App::Link` y `Assembly::AssemblyObject`):** todo ensamblaje general usa la clase `Ensamblaje` de `_herramientas/fc_helpers.py` (o el banco nativo `Assembly::AssemblyObject` para subconjuntos cinemáticos con solver interactivo), creando vínculos reales `App::Link` hacia los `.FCStd` individuales de `piezas/` (nunca recreando ni duplicando geometría sólida dentro del archivo de ensamblaje). Las piezas se posicionan encadenando exclusivamente sus conectores `lcs_pieza` y `lcs_destino` (prohibido hardcodear números mágicos en `offset`), definiendo vectores `explosion_vec` gobernados por `<<Parametros_Generales>>.explosion` (celda `B2`) y generando automáticamente las hojas `Lista_de_Materiales` (BOM), `Materiales_Generales` (con soporte de `TRANSP_INSP` y preservación de apariencias personalizadas) y `Reporte_Fisico` (masas vinculadas).
8. **Guardia anti-pisado (`Manifiesto_Script`):** antes de regenerar un `.FCStd` existente, `Pieza` y `Ensamblaje` verifican si el usuario hizo ediciones manuales en la GUI:
   - Si el usuario modificó valores en la hoja `Parametros` del `.FCStd`, esos valores se sincronizan automáticamente de vuelta hacia la lista `DIMS` del script `generar_<pieza>.py` (marcando el origen como `"usuario"`) antes de reconstruir.
   - Si el usuario agregó operaciones/objetos manuales en el árbol del `.FCStd` o editó `Placement`/expresiones fuera de la hoja, el script aborta con `[GUARDIA ANTI-PISADO]` sin sobrescribir el `.FCStd`. Solo se permite forzar la sobrescritura con `FORZAR=1` tras incorporarlo al script o con confirmación del usuario.

   
## 4. MODO HÍBRIDO EN VIVO (MCP BRIDGE)
Si el servidor MCP `freecad` está activo (`MCP On`):
1. **Sincronización Código <-> Sesión Viva:** Todo cambio geométrico que te pida el usuario debes plasmarlo en el script `generar_<pieza>.py` y ejecutarlo en la sesión abierta usando la herramienta MCP `execute_python_file` (así el archivo `.py` y lo que el usuario ve en pantalla nunca se desfasan).
2. **Lectura de la selección del mouse del usuario:** Si el usuario dice "en esta cara", "en esta arista" o "en la pieza seleccionada", usa `execute_python` para inspeccionar `FreeCADGui.Selection.getSelectionEx()`, extrae las coordenadas/subelementos (`SubElementNames`, `PickedPoints`, `BoundBox`), tradúcelos a parámetros o conectores `LCS_` en la hoja `Parametros`, y actualiza el script.
3. **Inspección y validación en vivo:** Puedes ejecutar `_herramientas/validar_fcstd.py` o consultar el estado del documento directamente con `execute_python` sin necesidad de levantar un proceso externo `freecadcmd`.
