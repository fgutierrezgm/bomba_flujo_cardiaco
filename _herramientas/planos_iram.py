#!/usr/bin/env python3
"""
Motor reutilizable de generación automática de planos técnicos bajo normas IRAM
para proyectos de FreeCAD (TechDraw).

Normas aplicadas:
- IRAM 4501: Formatos de láminas (A4, A3, A2) y márgenes (25 mm izq. archivo, 10 mm resto).
- IRAM 4502: Líneas de dibujo técnico (espesores y tipos A, B, E, F, G).
- IRAM 4503: Acotación de planos en fabricación metalmecánica.
- IRAM 4505: Escalas lineales normalizadas (2:1, 1:1, 1:2, 1:5).
- IRAM 4508: Rótulo, lista de materiales (BOM) y despiece.
- IRAM 4501-2: Método de proyección ISO-E (Primer Diedro) con símbolo normalizado.
"""
import base64
import math
import os
import textwrap
import FreeCAD as App
import Part


FORMATOS_IRAM = {
    "A4": (297.0, 210.0),
    "A3": (420.0, 297.0),
    "A2": (594.0, 420.0),
}

ESCALAS_IRAM = [
    (2.0, "2:1"),
    (1.0, "1:1"),
    (0.5, "1:2"),
    (0.2, "1:5"),
]


def _cargar_escudo_base64(ruta_png):
    if not os.path.exists(ruta_png):
        return ""
    with open(ruta_png, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def generar_svg_plantilla_iram_fcai(formato, ruta_salida, ruta_escudo_png):
    """
    Genera una plantilla SVG para TechDraw siguiendo las normas IRAM 4501 / 4508
    y replicando el rótulo institucional de la FCAI - UNCUYO con escudo a color
    y atributos freecad:editable sincronizables con la hoja Datos_Rotulo.
    """
    W, H = FORMATOS_IRAM[formato]
    m_izq = 25.0
    m_otros = 10.0
    x0, y0 = m_izq, m_otros
    x1, y1 = W - m_otros, H - m_otros
    marco_w = x1 - x0
    marco_h = y1 - y0

    # Dimensiones del rótulo IRAM 4508 / FCAI-UNCUYO (175 x 51 mm en esquina inferior derecha)
    rw = 175.0
    rh = 51.0
    rx = x1 - rw
    ry = y1 - rh

    escudo_uri = _cargar_escudo_base64(ruta_escudo_png)
    etiqueta_escudo = ""
    if escudo_uri:
        etiqueta_escudo = (
            f'<image x="{rx + 2.5:.2f}" y="{ry + 2.5:.2f}" width="21.0" height="25.0" '
            f'preserveAspectRatio="xMidYMid meet" href="{escudo_uri}" />'
        )

    # Coordenadas de referencia perimetral (grilla IRAM)
    cols_grilla = 6 if formato == "A4" else (8 if formato == "A3" else 12)
    filas_grilla = 4 if formato == "A4" else (6 if formato == "A3" else 8)
    letras = "ABCDEFGHJKLM"
    svg_grilla = []
    paso_x = marco_w / cols_grilla
    for i in range(cols_grilla):
        cx = x0 + (i + 0.5) * paso_x
        if i > 0:
            gx = x0 + i * paso_x
            svg_grilla.append(
                f'<line x1="{gx:.2f}" y1="{y0 - 5:.2f}" x2="{gx:.2f}" y2="{y0:.2f}" stroke="#000" stroke-width="0.25"/>'
            )
            svg_grilla.append(
                f'<line x1="{gx:.2f}" y1="{y1:.2f}" x2="{gx:.2f}" y2="{y1 + 5:.2f}" stroke="#000" stroke-width="0.25"/>'
            )
        svg_grilla.append(
            f'<text x="{cx:.2f}" y="{y0 - 1.5:.2f}" font-family="Liberation Sans, Arial, sans-serif" '
            f'font-size="2.8" text-anchor="middle">{i + 1}</text>'
        )
        svg_grilla.append(
            f'<text x="{cx:.2f}" y="{y1 + 3.8:.2f}" font-family="Liberation Sans, Arial, sans-serif" '
            f'font-size="2.8" text-anchor="middle">{i + 1}</text>'
        )

    paso_y = marco_h / filas_grilla
    for j in range(filas_grilla):
        cy = y0 + (j + 0.5) * paso_y
        if j > 0:
            gy = y0 + j * paso_y
            svg_grilla.append(
                f'<line x1="{x0 - 5:.2f}" y1="{gy:.2f}" x2="{x0:.2f}" y2="{gy:.2f}" stroke="#000" stroke-width="0.25"/>'
            )
            svg_grilla.append(
                f'<line x1="{x1:.2f}" y1="{gy:.2f}" x2="{x1 + 5:.2f}" y2="{gy:.2f}" stroke="#000" stroke-width="0.25"/>'
            )
        svg_grilla.append(
            f'<text x="{x0 - 2.5:.2f}" y="{cy + 1.0:.2f}" font-family="Liberation Sans, Arial, sans-serif" '
            f'font-size="2.8" text-anchor="middle">{letras[j]}</text>'
        )
        svg_grilla.append(
            f'<text x="{x1 + 2.5:.2f}" y="{cy + 1.0:.2f}" font-family="Liberation Sans, Arial, sans-serif" '
            f'font-size="2.8" text-anchor="middle">{letras[j]}</text>'
        )

    # Símbolo ISO-E (Método E de proyección del primer diedro - IRAM 4501-2)
    # Ubicado en la celda de símbolo dentro del rótulo: (rx + 26 .. rx + 52, ry + 30 .. ry + 41)
    sx = rx + 39.0
    sy = ry + 35.5
    simbolo_iso_e = f"""
    <g id="simbolo_iso_e" stroke="#000000" fill="none">
      <!-- Ejes de simetría (línea tipo F: trazo y punto fino) -->
      <line x1="{sx - 11.5:.2f}" y1="{sy:.2f}" x2="{sx + 10.5:.2f}" y2="{sy:.2f}" stroke-width="0.20" stroke-dasharray="3,0.8,0.5,0.8"/>
      <line x1="{sx + 5.5:.2f}" y1="{sy - 4.5:.2f}" x2="{sx + 5.5:.2f}" y2="{sy + 4.5:.2f}" stroke-width="0.20" stroke-dasharray="3,0.8,0.5,0.8"/>
      <!-- Trapecio (cono truncado vista frontal) -->
      <polygon points="{sx - 10.0:.2f},{sy - 3.2:.2f} {sx - 1.5:.2f},{sy - 1.8:.2f} {sx - 1.5:.2f},{sy + 1.8:.2f} {sx - 10.0:.2f},{sy + 3.2:.2f}" stroke-width="0.45"/>
      <!-- Círculos concéntricos a la derecha (vista lateral izquierda proyectada a la derecha en ISO-E) -->
      <circle cx="{sx + 5.5:.2f}" cy="{sy:.2f}" r="3.2" stroke-width="0.45"/>
      <circle cx="{sx + 5.5:.2f}" cy="{sy:.2f}" r="1.8" stroke-width="0.35"/>
      <text x="{sx:.2f}" y="{sy + 4.9:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.0" text-anchor="middle" stroke="none" fill="#000">ISO-E (IRAM)</text>
    </g>
    """

    svg = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns="http://www.w3.org/2000/svg"
   xmlns:freecad="http://www.freecadweb.org/wiki/index.php?title=Svg_Namespace"
   width="{W:.1f}mm"
   height="{H:.1f}mm"
   viewBox="0 0 {W:.1f} {H:.1f}"
   version="1.1">
  <!-- Borde exterior de corte de hoja (IRAM 4501) -->
  <rect x="0" y="0" width="{W:.1f}" height="{H:.1f}" fill="none" stroke="#000000" stroke-width="0.25"/>
  <!-- Marco exterior de referencia -->
  <rect x="{x0 - 5:.2f}" y="{y0 - 5:.2f}" width="{marco_w + 10:.2f}" height="{marco_h + 10:.2f}" fill="none" stroke="#000000" stroke-width="0.25"/>
  <!-- Recuadro principal de dibujo (IRAM 4501: margen izquierdo 25 mm, resto 10 mm, línea tipo A 0.7 mm) -->
  <rect x="{x0:.2f}" y="{y0:.2f}" width="{marco_w:.2f}" height="{marco_h:.2f}" fill="none" stroke="#000000" stroke-width="0.70"/>
  <!-- Grilla de coordenadas de referencia -->
  {"".join(svg_grilla)}

  <!-- RÓTULO IRAM 4508 / FCAI - UNCUYO (175 x 51 mm) -->
  <g id="rotulo_iram_fcai">
    <rect x="{rx:.2f}" y="{ry:.2f}" width="{rw:.2f}" height="{rh:.2f}" fill="#ffffff" stroke="#000000" stroke-width="0.70"/>
    {etiqueta_escudo}

    <!-- Líneas horizontales internas del rótulo -->
    <line x1="{rx + 26.0:.2f}" y1="{ry + 7.5:.2f}" x2="{rx + rw:.2f}" y2="{ry + 7.5:.2f}" stroke="#000000" stroke-width="0.35"/>
    <line x1="{rx + 26.0:.2f}" y1="{ry + 15.0:.2f}" x2="{rx + rw:.2f}" y2="{ry + 15.0:.2f}" stroke="#000000" stroke-width="0.35"/>
    <line x1="{rx + 26.0:.2f}" y1="{ry + 22.5:.2f}" x2="{rx + rw:.2f}" y2="{ry + 22.5:.2f}" stroke="#000000" stroke-width="0.35"/>
    <line x1="{rx:.2f}" y1="{ry + 30.0:.2f}" x2="{rx + rw:.2f}" y2="{ry + 30.0:.2f}" stroke="#000000" stroke-width="0.50"/>
    <line x1="{rx:.2f}" y1="{ry + 41.0:.2f}" x2="{rx + rw:.2f}" y2="{ry + 41.0:.2f}" stroke="#000000" stroke-width="0.35"/>

    <!-- Líneas verticales internas del rótulo -->
    <!-- Columna escudo (0..26 mm) -->
    <line x1="{rx + 26.0:.2f}" y1="{ry:.2f}" x2="{rx + 26.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.35"/>
    <!-- Separador Carrera / Cátedra en fila 2 -->
    <line x1="{rx + 85.0:.2f}" y1="{ry + 7.5:.2f}" x2="{rx + 85.0:.2f}" y2="{ry + 22.5:.2f}" stroke="#000000" stroke-width="0.35"/>
    <!-- Columnas inferiores (ry+30 .. ry+51) -->
    <line x1="{rx + 52.0:.2f}" y1="{ry + 30.0:.2f}" x2="{rx + 52.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.35"/>
    <line x1="{rx + 132.0:.2f}" y1="{ry + 30.0:.2f}" x2="{rx + 132.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.50"/>
    <line x1="{rx + 92.0:.2f}" y1="{ry + 41.0:.2f}" x2="{rx + 92.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.35"/>

    <!-- Símbolo ISO-E -->
    {simbolo_iso_e}

    <!-- Etiquetas fijas del rótulo -->
    <g font-family="Liberation Sans, Arial, sans-serif" font-size="2.1" fill="#333333">
      <text x="{rx + 1.5:.2f}" y="{ry + 32.8:.2f}">Escala:</text>
      <text x="{rx + 1.5:.2f}" y="{ry + 43.8:.2f}">Formato / Hoja:</text>
      <text x="{rx + 27.5:.2f}" y="{ry + 43.8:.2f}">Fecha:</text>
      <text x="{rx + 53.5:.2f}" y="{ry + 32.8:.2f}">Denominación / Título del Plano:</text>
      <text x="{rx + 53.5:.2f}" y="{ry + 43.8:.2f}">Material:</text>
      <text x="{rx + 93.5:.2f}" y="{ry + 43.8:.2f}">Tol. Gral. / Masa:</text>
      <text x="{rx + 133.5:.2f}" y="{ry + 32.8:.2f}">Dibujó / Revisó:</text>
      <text x="{rx + 133.5:.2f}" y="{ry + 43.8:.2f}">Plano Nº:</text>
    </g>

    <!-- Textos editables (sincronizados con hoja Datos_Rotulo) -->
    <g font-family="Liberation Sans, Arial, sans-serif" fill="#000000">
      <text freecad:editable="INSTITUCION" x="{rx + 100.5:.2f}" y="{ry + 5.2:.2f}" font-size="3.3" font-weight="bold" text-anchor="middle"><tspan>Facultad de Ciencias Aplicadas a la Industria - UNCUYO</tspan></text>
      <text freecad:editable="CARRERA" x="{rx + 55.5:.2f}" y="{ry + 12.6:.2f}" font-size="3.0" text-anchor="middle"><tspan>Ingeniería Mecánica</tspan></text>
      <text freecad:editable="CATEDRA" x="{rx + 130.0:.2f}" y="{ry + 12.6:.2f}" font-size="3.0" text-anchor="middle"><tspan>Máquinas Térmicas e Hidráulicas</tspan></text>
      <text freecad:editable="CURSO" x="{rx + 55.5:.2f}" y="{ry + 20.0:.2f}" font-size="2.8" text-anchor="middle"><tspan>4to Año - Segundo semestre</tspan></text>
      <text freecad:editable="PROFESOR" x="{rx + 130.0:.2f}" y="{ry + 20.0:.2f}" font-size="2.8" text-anchor="middle"><tspan>Profesor: Analía Bonino</tspan></text>
      <text freecad:editable="PROYECTO" x="{rx + 100.5:.2f}" y="{ry + 27.5:.2f}" font-size="3.1" font-weight="bold" text-anchor="middle"><tspan>Diseño y construcción de una bomba de simulación de flujo cardíaco</tspan></text>

      <!-- Escala -->
      <text freecad:editable="ESCALA" x="{rx + 13.0:.2f}" y="{ry + 38.8:.2f}" font-size="4.0" font-weight="bold" text-anchor="middle"><tspan>1:1</tspan></text>
      <!-- Formato y Hoja -->
      <text freecad:editable="FORMATO" x="{rx + 2.0:.2f}" y="{ry + 49.0:.2f}" font-size="2.7" font-weight="bold"><tspan>IRAM {formato}</tspan></text>
      <text freecad:editable="HOJA" x="{rx + 24.5:.2f}" y="{ry + 49.0:.2f}" font-size="2.6" text-anchor="end"><tspan>1/24</tspan></text>

      <!-- Fecha -->
      <text freecad:editable="FECHA" x="{rx + 39.0:.2f}" y="{ry + 49.0:.2f}" font-size="2.8" text-anchor="middle"><tspan>10/11/2026</tspan></text>

      <!-- Título de la pieza/conjunto -->
      <text freecad:editable="TITULO" x="{rx + 92.0:.2f}" y="{ry + 38.6:.2f}" font-size="3.8" font-weight="bold" text-anchor="middle"><tspan>Denominación de la Pieza</tspan></text>

      <!-- Material y Masa/Tolerancia -->
      <text freecad:editable="MATERIAL" x="{rx + 72.0:.2f}" y="{ry + 49.0:.2f}" font-size="2.7" text-anchor="middle"><tspan>AISI 304</tspan></text>
      <text freecad:editable="TOL_GRAL" x="{rx + 93.5:.2f}" y="{ry + 47.2:.2f}" font-size="2.3"><tspan>ISO 2768-mK</tspan></text>
      <text freecad:editable="MASA" x="{rx + 93.5:.2f}" y="{ry + 50.0:.2f}" font-size="2.3"><tspan>Masa: - g</tspan></text>

      <!-- Autor, Aprobado y Número de Plano -->
      <text freecad:editable="AUTOR" x="{rx + 133.5:.2f}" y="{ry + 36.6:.2f}" font-size="2.5"><tspan>Dib.: F. Gutiérrez</tspan></text>
      <text freecad:editable="APROBADO" x="{rx + 133.5:.2f}" y="{ry + 39.8:.2f}" font-size="2.5"><tspan>Apr.: Ing. A. Bonino</tspan></text>
      <text freecad:editable="NUM_PLANO" x="{rx + 153.5:.2f}" y="{ry + 49.2:.2f}" font-size="4.2" font-weight="bold" text-anchor="middle"><tspan>Plano Nº 1</tspan></text>
    </g>
  </g>
</svg>
"""
    os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(svg)
    return ruta_salida


def asegurar_plantillas_iram(dir_plantillas):
    """Genera las plantillas SVG IRAM A4, A3 y A2 con el escudo de la FCAI-UNCUYO."""
    ruta_escudo = os.path.join(dir_plantillas, "escudo_uncuyo.png")
    rutas = {}
    for fmt in ("A4", "A3", "A2"):
        ruta_svg = os.path.join(dir_plantillas, f"rotulo_iram_fcai_{fmt}.svg")
        generar_svg_plantilla_iram_fcai(fmt, ruta_svg, ruta_escudo)
        rutas[fmt] = ruta_svg
    return rutas


def seleccionar_formato_y_escala(bb, es_conjunto=False):
    """
    Selecciona automáticamente el formato de hoja IRAM (A4, A3 o A2) y la escala
    normalizada IRAM 4505 (2:1, 1:1, 1:2, 1:5) según el BoundBox de la pieza o conjunto.
    """
    dx = max(1.0, bb.XLength)
    dy = max(1.0, bb.YLength)
    dz = max(1.0, bb.ZLength)
    dim_max = max(dx, dy, dz)
    suma_vistas = dx + dz

    if es_conjunto:
        return "A2", 0.5, "1:2"

    # Para piezas pequeñas (< 48 mm) usamos escala de ampliación 2:1 en A3 o A4
    if dim_max <= 38.0 and suma_vistas <= 65.0:
        return "A4", 2.0, "2:1"
    if dim_max <= 55.0 and suma_vistas <= 95.0:
        return "A3", 2.0, "2:1"

    # Escala natural 1:1 en A4 si entra cómodamente con la tabla paramétrica
    if dim_max <= 85.0 and suma_vistas <= 135.0:
        return "A4", 1.0, "1:1"

    # Escala natural 1:1 en A3 para piezas medianas
    if dim_max <= 145.0 and suma_vistas <= 225.0:
        return "A3", 1.0, "1:1"

    # Escala de reducción 1:2 en A3 para piezas grandes (tapas Ø200, tensores 288 mm, ejes)
    if dim_max <= 340.0:
        return "A3", 0.5, "1:2"

    return "A3", 0.2, "1:5"


def estilizar_vista_iram(vista, mostrar_ocultas=False, mostrar_centros=True):
    """Aplica espesores de línea IRAM 4502 si ViewObject está disponible."""
    try:
        vista.HardHidden = mostrar_ocultas
        vista.SmoothVisible = True
        vista.SeamVisible = False
    except Exception:
        pass
    vo = getattr(vista, "ViewObject", None)
    if vo:
        try:
            if hasattr(vo, "LineWidth"):
                vo.LineWidth = 0.50  # IRAM 4502 Tipo A (contornos visibles)
            if hasattr(vo, "HiddenWidth"):
                vo.HiddenWidth = 0.25  # IRAM 4502 Tipo E (aristas ocultas)
            if hasattr(vo, "IsoWidth"):
                vo.IsoWidth = 0.25
            if hasattr(vo, "ArcCenterMarks"):
                vo.ArcCenterMarks = mostrar_centros
            if hasattr(vo, "HorizCenterLine"):
                vo.HorizCenterLine = mostrar_centros
            if hasattr(vo, "VertCenterLine"):
                vo.VertCenterLine = mostrar_centros
        except Exception:
            pass


def _limites_aristas_2d(edges):
    xmin, ymin, xmax, ymax = 1e9, 1e9, -1e9, -1e9
    for e in edges:
        bb = e.BoundBox
        xmin = min(xmin, bb.XMin)
        xmax = max(xmax, bb.XMax)
        ymin = min(ymin, bb.YMin)
        ymax = max(ymax, bb.YMax)
    return xmin, ymin, xmax, ymax


def _limites_seguros_hoja(vista, formato="A3"):
    """Devuelve (dx_min, dx_max, dy_min, dy_max) relativos a la vista dentro del área útil IRAM."""
    W, H = FORMATOS_IRAM.get(formato, (420.0, 297.0))
    vx = float(vista.X.Value) if hasattr(vista.X, "Value") else float(vista.X)
    vy = float(vista.Y.Value) if hasattr(vista.Y, "Value") else float(vista.Y)
    return (30.0 - vx, (W - 14.0) - vx, 16.0 - vy, (H - 14.0) - vy)


def acotar_vista_circular_iram(doc, page, vista, prefijo_nombre, max_diametros=4, formato="A3"):
    """
    Detecta los círculos concéntricos proyectados en una vista superior/frontal (Direction=(0,0,1))
    y crea cotas de diámetro reales (`TechDraw::DrawViewDimension`) dispuestas en el semicírculo
    superior para nunca superponerse con el título (`Caption`) inferior de la vista ni salirse
    de los márgenes IRAM.
    """
    try:
        edges = vista.getVisibleEdges()
    except Exception:
        return []
    if not edges:
        return []

    xmin, ymin, xmax, ymax = _limites_aristas_2d(edges)
    cx_vista = 0.5 * (xmin + xmax)
    cy_vista = 0.5 * (ymin + ymax)
    r_max_vista = max(1.0, 0.5 * max(xmax - xmin, ymax - ymin))

    # Agrupar aristas circulares completas o arcos grandes por su diámetro redondeado a 0.1 mm
    circulos_por_diam = {}
    for idx, e in enumerate(edges):
        curva = getattr(e, "Curve", None)
        if curva and curva.TypeId == "Part::GeomCircle":
            r = float(curva.Radius)
            d = round(2.0 * r, 2)
            if d < 1.8:
                continue
            c = curva.Center
            dist_centro = math.hypot(c.x - cx_vista, c.y - cy_vista)
            clave = round(d, 1)
            actual = circulos_por_diam.get(clave)
            # Preferir círculos concéntricos y en el semicírculo superior si son excéntricos
            bonus_sup = 2.0 if c.y >= cy_vista - 0.5 else -5.0
            score = e.Length - dist_centro * 3.0 + bonus_sup
            if actual is None or score > actual[1]:
                circulos_por_diam[clave] = (idx, score, r, c.x, c.y, d, dist_centro)

    if not circulos_por_diam:
        return []

    # Priorizar círculos concéntricos ordenados de mayor a menor diámetro, y luego a lo sumo 1 agujero excéntrico
    concentricos = [it for it in circulos_por_diam.values() if it[6] <= 1.5]
    excentricos = [it for it in circulos_por_diam.values() if it[6] > 1.5 and it[4] >= cy_vista - 0.5]
    concentricos.sort(key=lambda x: x[2], reverse=True)
    excentricos.sort(key=lambda x: (x[2], x[4]), reverse=True)

    seleccionados = []
    for item in concentricos:
        if len(seleccionados) >= max_diametros:
            break
        if all(abs(item[2] - prev[2]) >= 2.2 for prev in seleccionados):
            seleccionados.append(item)

    if len(seleccionados) < max_diametros and excentricos:
        for item in excentricos:
            if all(abs(item[2] - prev[2]) >= 2.0 for prev in seleccionados):
                seleccionados.append(item)
                break

    dx_min_s, dx_max_s, dy_min_s, dy_max_s = _limites_seguros_hoja(vista, formato=formato)
    # Solo ángulos en cuadrantes superiores (sin(ang) > 0) para mantener libre la zona inferior del Caption
    angulos_deg = [34.0, 146.0, 14.0, 166.0]
    cotas_creadas = []
    idx_conc = 0

    for k, (edge_idx, _, r_papel, cx, cy, _, dist_centro) in enumerate(seleccionados):
        dim = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Diam_{k+1}")
        page.addView(dim)
        dim.Type = "Diameter"
        dim.MeasureType = "Projected"
        dim.FormatSpec = "⌀%.2w"
        dim.References2D = [(vista, f"Edge{edge_idx}")]

        if dist_centro <= 1.5:
            ang = math.radians(angulos_deg[idx_conc % len(angulos_deg)])
            nivel = idx_conc // 2
            dist_etiqueta = max(10.0, r_max_vista + 8.5 + nivel * 7.0)
            lx = cx + dist_etiqueta * math.cos(ang)
            ly = cy + dist_etiqueta * math.sin(ang)
            idx_conc += 1
        else:
            # Para agujeros excéntricos (brida/tornillos), usar líder corto local hacia arriba-afuera
            ang_exc = math.radians(42.0 if cx >= cx_vista else 138.0)
            dist_local = max(7.0, r_papel + 6.5)
            lx = cx + dist_local * math.cos(ang_exc)
            ly = cy + dist_local * math.sin(ang_exc)

        # Garantizar que nunca invada el título inferior ni los márgenes de la hoja
        ly_min_caption = ymin + 2.0 if r_max_vista > 8.0 else cy_vista + 4.0
        dim.X = max(dx_min_s + 8.0, min(dx_max_s - 8.0, lx))
        dim.Y = max(max(dy_min_s + 4.0, ly_min_caption), min(dy_max_s - 4.0, ly))
        cotas_creadas.append(dim)

    return cotas_creadas


def _indices_extremos_vertices_2d(vista):
    """Devuelve los índices (i_minx, i_maxx, i_miny, i_maxy) y límites de `getVisibleVertexes()`."""
    try:
        vs = vista.getVisibleVertexes()
    except Exception:
        vs = []
    if not vs:
        return None
    i_minx = min(range(len(vs)), key=lambda i: (vs[i].x, abs(vs[i].y)))
    i_maxx = max(range(len(vs)), key=lambda i: (vs[i].x, -abs(vs[i].y)))
    i_miny = min(range(len(vs)), key=lambda i: (vs[i].y, abs(vs[i].x)))
    i_maxy = max(range(len(vs)), key=lambda i: (vs[i].y, -abs(vs[i].x)))
    xmin = vs[i_minx].x
    xmax = vs[i_maxx].x
    ymin = vs[i_miny].y
    ymax = vs[i_maxy].y
    return i_minx, i_maxx, i_miny, i_maxy, xmin, ymin, xmax, ymax, vs


def acotar_vista_perfil_o_corte_iram(
    doc,
    page,
    vista,
    prefijo_nombre,
    es_revolucion=False,
    formato="A3",
):
    """
    Crea cotas lineales claras (`DistanceY` para longitud total y escalones relevantes a izq/der,
    `DistanceX` para ancho/diámetro total e interior escalonados ARRIBA de la vista) siguiendo
    IRAM 4503 para evitar cualquier superposición con el `Caption` inferior de la vista.
    """
    try:
        edges = vista.getVisibleEdges()
    except Exception:
        return []
    if not edges:
        return []

    ext = _indices_extremos_vertices_2d(vista)
    if ext is not None:
        i_minx, i_maxx, i_miny, i_maxy, xmin, ymin, xmax, ymax, vs = ext
    else:
        xmin, ymin, xmax, ymax = _limites_aristas_2d(edges)
        i_minx = i_maxx = i_miny = i_maxy = None
        vs = []

    w_papel = xmax - xmin
    h_papel = ymax - ymin
    cx_vista = 0.5 * (xmin + xmax)
    cy_vista = 0.5 * (ymin + ymax)
    dx_min_s, dx_max_s, dy_min_s, dy_max_s = _limites_seguros_hoja(vista, formato=formato)

    aristas_vert = []
    aristas_horiz = []
    for idx, e in enumerate(edges):
        bb = e.BoundBox
        curva = getattr(e, "Curve", None)
        if curva and curva.TypeId == "Part::GeomLine" and e.Length >= 2.0:
            dx = abs(bb.XMax - bb.XMin)
            dy = abs(bb.YMax - bb.YMin)
            if dx < 0.05 and dy >= 2.0:
                aristas_vert.append((idx, dy, 0.5 * (bb.XMin + bb.XMax), bb.YMin, bb.YMax))
            elif dy < 0.05 and dx >= 3.0:
                aristas_horiz.append((idx, dx, 0.5 * (bb.YMin + bb.YMax), bb.XMin, bb.XMax))

    cotas = []

    # 1. COTAS VERTICALES (Alturas / Longitudes) -> a la DERECHA e IZQUIERDA (nunca abajo)
    if h_papel >= 2.0:
        # Altura / longitud total a la derecha
        if i_miny is not None and i_maxy is not None and i_miny != i_maxy:
            dim_h = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Alt_1")
            page.addView(dim_h)
            dim_h.Type = "DistanceY"
            dim_h.MeasureType = "Projected"
            dim_h.FormatSpec = "%.2w"
            dim_h.References2D = [(vista, f"Vertex{i_miny}"), (vista, f"Vertex{i_maxy}")]
            dim_h.X = min(dx_max_s - 6.0, xmax + 9.5)
            dim_h.Y = cy_vista
            cotas.append(dim_h)
        elif aristas_vert:
            aristas_vert.sort(key=lambda x: x[1], reverse=True)
            idx_v, _, _, yv0, yv1 = aristas_vert[0]
            dim_h = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Alt_1")
            page.addView(dim_h)
            dim_h.Type = "DistanceY"
            dim_h.MeasureType = "Projected"
            dim_h.FormatSpec = "%.2w"
            dim_h.References2D = [(vista, f"Edge{idx_v}")]
            dim_h.X = min(dx_max_s - 6.0, xmax + 9.5)
            dim_h.Y = 0.5 * (yv0 + yv1)
            cotas.append(dim_h)

        # Segundo escalón vertical distintivo (distinto de la altura total) a la izquierda
        aristas_vert_ord = sorted(aristas_vert, key=lambda x: x[1], reverse=True)
        for idx_v2, lv2, xv2, y2a, y2b in aristas_vert_ord:
            if abs(lv2 - h_papel) > 2.5 and lv2 >= 4.0:
                dim_h2 = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Alt_2")
                page.addView(dim_h2)
                dim_h2.Type = "DistanceY"
                dim_h2.MeasureType = "Projected"
                dim_h2.FormatSpec = "%.2w"
                dim_h2.References2D = [(vista, f"Edge{idx_v2}")]
                dim_h2.X = max(dx_min_s + 6.0, xmin - 9.5)
                dim_h2.Y = 0.5 * (y2a + y2b)
                cotas.append(dim_h2)
                break

    # 2. COTAS HORIZONTALES (Anchos / Diámetros exteriores) -> SIEMPRE ARRIBA (Y > ymax) para no tapar Caption
    if w_papel >= 2.5:
        fmt_x = "⌀%.2w" if es_revolucion else "%.2w"

        # Buscar un diámetro/ancho interior centrado o escalón secundario relevante para anidar dentro del total
        par_interior = None
        if vs:
            # Buscar pares de vértices simétricos respecto a cx_vista cerca de ymax (boca/escalón superior)
            cand_sup = [
                i for i, v in enumerate(vs)
                if abs(v.y - ymax) < max(3.0, 0.25 * h_papel) and abs(v.x - cx_vista) >= 2.5
            ]
            # Agrupar por |x - cx_vista| para hallar simétricos distintos del ancho total
            por_radio = {}
            for i in cand_sup:
                rad = round(abs(vs[i].x - cx_vista), 1)
                if rad * 2.0 < w_papel - 5.0 and rad * 2.0 >= 5.5:
                    por_radio.setdefault(rad, []).append(i)
            for rad in sorted(por_radio.keys(), reverse=True):
                idxs = por_radio[rad]
                izq = [i for i in idxs if vs[i].x < cx_vista]
                der = [i for i in idxs if vs[i].x > cx_vista]
                if izq and der:
                    par_interior = (izq[0], der[0])
                    break

        y_cota_total = ymax + 8.5
        if par_interior is not None and (ymax + 15.5) <= dy_max_s - 3.0:
            dim_w_int = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Ancho_Int")
            page.addView(dim_w_int)
            dim_w_int.Type = "DistanceX"
            dim_w_int.MeasureType = "Projected"
            dim_w_int.FormatSpec = fmt_x
            dim_w_int.References2D = [(vista, f"Vertex{par_interior[0]}"), (vista, f"Vertex{par_interior[1]}")]
            dim_w_int.X = cx_vista
            dim_w_int.Y = ymax + 7.5
            cotas.append(dim_w_int)
            y_cota_total = ymax + 14.5

        if i_minx is not None and i_maxx is not None and i_minx != i_maxx:
            dim_w = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Ancho_1")
            page.addView(dim_w)
            dim_w.Type = "DistanceX"
            dim_w.MeasureType = "Projected"
            dim_w.FormatSpec = fmt_x
            dim_w.References2D = [(vista, f"Vertex{i_minx}"), (vista, f"Vertex{i_maxx}")]
            dim_w.X = cx_vista
            dim_w.Y = min(dy_max_s - 3.5, y_cota_total)
            cotas.append(dim_w)
        elif aristas_horiz:
            aristas_horiz.sort(key=lambda x: x[1], reverse=True)
            idx_hz, _, _, xh0, xh1 = aristas_horiz[0]
            dim_w = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Ancho_1")
            page.addView(dim_w)
            dim_w.Type = "DistanceX"
            dim_w.MeasureType = "Projected"
            dim_w.FormatSpec = fmt_x
            dim_w.References2D = [(vista, f"Edge{idx_hz}")]
            dim_w.X = 0.5 * (xh0 + xh1)
            dim_w.Y = min(dy_max_s - 3.5, y_cota_total)
            cotas.append(dim_w)

    return cotas


def _escapar_xml(texto):
    return (
        str(texto)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _truncar_texto(txt, max_ancho_mm, font_size):
    """Recorta texto estimando ancho en mm para evitar desbordes entre columnas SVG."""
    s = str(txt or "").strip()
    max_chars = max(4, int(max_ancho_mm / max(0.5, font_size * 0.58)))
    if len(s) <= max_chars:
        return s
    return s[: max(1, max_chars - 2)] + ".."


def generar_svg_bloque_cotas_pieza(filas_parametros, notas_taller, ancho_mm=98.0):
    """
    Genera un bloque SVG vectorial limpio con todas las cotas nominales, roscas,
    tolerancias y notas de fabricación extraídas de la hoja `Parametros` de la pieza.
    """
    alto_fila = 4.2
    n_filas = min(len(filas_parametros), 22)
    alto_tabla = 8.0 + n_filas * alto_fila
    W = ancho_mm

    # Envolver notas técnicas al ancho útil de la caja
    max_chars_nota = max(32, int((W - 6.0) / (2.15 * 0.58)))
    lineas_notas = []
    for nota in notas_taller or []:
        envueltas = textwrap.wrap(str(nota).strip(), width=max_chars_nota - 2) or [""]
        for k, seg in enumerate(envueltas):
            prefijo = "• " if k == 0 else "  "
            lineas_notas.append(prefijo + seg)

    alto_notas = (6.0 + len(lineas_notas) * 3.6) if lineas_notas else 0.0
    H = alto_tabla + alto_notas + 2.0

    # Columnas: [0.5..26.0] Símbolo | [26.0..46.5] Valor | [46.5..W-0.5] Descripción
    x_div1 = 26.0
    x_div2 = 46.5
    x_val_end = 45.0
    x_desc = 48.0
    w_desc = max(20.0, W - x_desc - 1.5)

    lineas = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{alto_tabla - 0.5:.1f}" fill="#ffffff" stroke="#000000" stroke-width="0.45"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="6.5" fill="#eaeff5" stroke="#000000" stroke-width="0.45"/>',
        f'<text x="{W / 2:.1f}" y="4.8" font-family="Liberation Sans, Arial, sans-serif" font-size="{2.9 if W >= 130 else 2.4:.1f}" font-weight="bold" text-anchor="middle">CUADRO DE COTAS FUNCIONALES, ROSCAS Y TOLERANCIAS (IRAM 4503)</text>',
        f'<line x1="{x_div1:.1f}" y1="7.0" x2="{x_div1:.1f}" y2="{alto_tabla:.1f}" stroke="#000000" stroke-width="0.25"/>',
        f'<line x1="{x_div2:.1f}" y1="7.0" x2="{x_div2:.1f}" y2="{alto_tabla:.1f}" stroke="#000000" stroke-width="0.25"/>',
    ]

    for idx, (simbolo, valor_unid, descripcion) in enumerate(filas_parametros[:n_filas]):
        y_top = 7.0 + idx * alto_fila
        y_txt = y_top + 3.0
        if idx > 0:
            lineas.append(
                f'<line x1="0.5" y1="{y_top:.2f}" x2="{W - 0.5:.1f}" y2="{y_top:.2f}" stroke="#cccccc" stroke-width="0.20"/>'
            )
        simb_corta = _truncar_texto(simbolo, x_div1 - 3.0, 2.25)
        val_corta = _truncar_texto(valor_unid, x_div2 - x_div1 - 2.5, 2.35)
        desc_corta = _truncar_texto(descripcion, w_desc, 2.15)
        lineas.append(
            f'<text x="2.0" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.25" font-weight="bold">{_escapar_xml(simb_corta)}</text>'
        )
        lineas.append(
            f'<text x="{x_val_end:.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" text-anchor="end">{_escapar_xml(val_corta)}</text>'
        )
        lineas.append(
            f'<text x="{x_desc:.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.15">{_escapar_xml(desc_corta)}</text>'
        )

    if lineas_notas:
        y_n0 = alto_tabla + 1.5
        lineas.append(
            f'<rect x="0.5" y="{y_n0:.2f}" width="{W - 1.0:.1f}" height="{alto_notas - 1.0:.2f}" fill="#fcfcfc" stroke="#000000" stroke-width="0.35"/>'
        )
        lineas.append(
            f'<text x="2.0" y="{y_n0 + 3.6:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4" font-weight="bold">NOTAS TÉCNICAS Y TOLERANCIAS:</text>'
        )
        for j, nota_ln in enumerate(lineas_notas):
            yn = y_n0 + 7.2 + j * 3.6
            lineas.append(
                f'<text x="2.5" y="{yn:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.15">{_escapar_xml(nota_ln)}</text>'
            )

    lineas.append("</svg>")
    return "\n".join(lineas)


def generar_svg_tabla_bom_iram(items_bom, resumen_buloneria, ancho_mm=385.0):
    """
    Genera el símbolo SVG vectorial de la Lista de Materiales (BOM) según IRAM 4508,
    coincidiendo exactamente con la numeración 1..27 de los globos de la vista explotada,
    e incluyendo fila destacada de Peso Total del Ensamblaje.
    """
    alto_fila = 5.4
    n_items = len(items_bom)
    alto_cabecera = 12.0
    alto_fila_total = 6.8
    alto_tabla = alto_cabecera + n_items * alto_fila + alto_fila_total
    alto_bul = 10.0 + len(resumen_buloneria) * 4.5 if resumen_buloneria else 0.0
    H = alto_tabla + alto_bul + 4.0
    W = ancho_mm

    # Columnas:
    # [0..16] N° Ítem | [16..34] Cant. | [34..115] Denominación / Pieza | [115..160] Plano / Ref. | [160..235] Material | [235..345] Norma / Código Comercial / Detalles | [345..384] Masa Unit. (g)
    cols_x = [16.0, 34.0, 115.0, 160.0, 235.0, 345.0]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{alto_tabla - 0.5:.1f}" fill="#ffffff" stroke="#000000" stroke-width="0.60"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{alto_cabecera:.1f}" fill="#dce6f1" stroke="#000000" stroke-width="0.60"/>',
        f'<text x="{W / 2:.1f}" y="5.0" font-family="Liberation Sans, Arial, sans-serif" font-size="3.6" font-weight="bold" text-anchor="middle">LISTA DE MATERIALES Y DESPIECE GENERAL (IRAM 4508)</text>',
        f'<line x1="0.5" y1="6.8" x2="{W - 0.5:.1f}" y2="6.8" stroke="#000000" stroke-width="0.40"/>',
    ]

    for cx in cols_x:
        svg.append(
            f'<line x1="{cx:.1f}" y1="6.8" x2="{cx:.1f}" y2="{alto_tabla - alto_fila_total:.1f}" stroke="#000000" stroke-width="0.35"/>'
        )

    encabezados = [
        (8.0, "ÍTEM"),
        (25.0, "CANT."),
        (74.5, "DENOMINACIÓN DE LA PIEZA"),
        (137.5, "PLANO N°"),
        (197.5, "MATERIAL ESPECIFICADO"),
        (290.0, "NORMA / CÓDIGO COMERCIAL / OBSERVACIONES"),
        (364.5, "MASA UN. (g)"),
    ]
    for cx, titulo in encabezados:
        svg.append(
            f'<text x="{cx:.1f}" y="10.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.6" font-weight="bold" text-anchor="middle">{_escapar_xml(titulo)}</text>'
        )

    cant_total_piezas = 0
    masa_total_piezas_g = 0.0

    for idx, it in enumerate(items_bom):
        y_top = alto_cabecera + idx * alto_fila
        y_txt = y_top + 3.8
        cant_total_piezas += it["cantidad"]
        masa_sub = it["masa_g"] * it["cantidad"]
        masa_total_piezas_g += masa_sub

        es_comercial = it.get("es_comercial", False)
        bg = "#f7fbff" if es_comercial else ("#ffffff" if idx % 2 == 0 else "#f9f9f9")
        svg.append(
            f'<rect x="0.8" y="{y_top:.2f}" width="{W - 1.6:.1f}" height="{alto_fila:.2f}" fill="{bg}" stroke="none"/>'
        )
        svg.append(
            f'<line x1="0.5" y1="{y_top:.2f}" x2="{W - 0.5:.1f}" y2="{y_top:.2f}" stroke="#000000" stroke-width="0.25"/>'
        )
        for cx in cols_x:
            svg.append(
                f'<line x1="{cx:.1f}" y1="{y_top:.2f}" x2="{cx:.1f}" y2="{y_top + alto_fila:.2f}" stroke="#000000" stroke-width="0.25"/>'
            )

        svg.append(
            f'<text x="8.0" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.8" font-weight="bold" text-anchor="middle">{it["item"]}</text>'
        )
        svg.append(
            f'<text x="25.0" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.8" font-weight="bold" text-anchor="middle">{it["cantidad"]}</text>'
        )
        svg.append(
            f'<text x="36.5" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.6">{_escapar_xml(_truncar_texto(it["denominacion"], 76.5, 2.6))}</text>'
        )
        svg.append(
            f'<text x="137.5" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.5" text-anchor="middle">{_escapar_xml(_truncar_texto(it["plano_ref"], 42.0, 2.5))}</text>'
        )
        svg.append(
            f'<text x="162.5" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.5">{_escapar_xml(_truncar_texto(it["material"], 70.5, 2.5))}</text>'
        )
        svg.append(
            f'<text x="237.5" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.45">{_escapar_xml(_truncar_texto(it["detalles"], 105.5, 2.45))}</text>'
        )
        svg.append(
            f'<text x="381.5" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.6" text-anchor="end">{it["masa_g"]:.1f}</text>'
        )

    # --- FILA DESTACADA DE PESO TOTAL DEL ENSAMBLAJE ---
    y_tot = alto_cabecera + n_items * alto_fila
    masa_total_kg = masa_total_piezas_g / 1000.0
    svg.append(
        f'<rect x="0.8" y="{y_tot:.2f}" width="{W - 1.6:.1f}" height="{alto_fila_total:.2f}" fill="#e3ecf6" stroke="none"/>'
    )
    svg.append(
        f'<line x1="0.5" y1="{y_tot:.2f}" x2="{W - 0.5:.1f}" y2="{y_tot:.2f}" stroke="#000000" stroke-width="0.55"/>'
    )
    svg.append(
        f'<line x1="16.0" y1="{y_tot:.2f}" x2="16.0" y2="{y_tot + alto_fila_total:.2f}" stroke="#000000" stroke-width="0.35"/>'
    )
    svg.append(
        f'<line x1="34.0" y1="{y_tot:.2f}" x2="34.0" y2="{y_tot + alto_fila_total:.2f}" stroke="#000000" stroke-width="0.35"/>'
    )
    svg.append(
        f'<line x1="345.0" y1="{y_tot:.2f}" x2="345.0" y2="{y_tot + alto_fila_total:.2f}" stroke="#000000" stroke-width="0.35"/>'
    )
    svg.append(
        f'<text x="25.0" y="{y_tot + 4.6:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="3.0" font-weight="bold" text-anchor="middle">{cant_total_piezas}</text>'
    )
    svg.append(
        f'<text x="38.0" y="{y_tot + 4.6:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="3.1" font-weight="bold">PESO TOTAL ESTIMADO DEL CONJUNTO MECÁNICO (BOMBA ARMADA COMPLETA)</text>'
    )
    svg.append(
        f'<text x="381.5" y="{y_tot + 4.6:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="3.2" font-weight="bold" text-anchor="end">{masa_total_kg:.2f} kg ({masa_total_piezas_g:.0f} g)</text>'
    )

    if resumen_buloneria:
        yb0 = alto_tabla + 3.0
        svg.append(
            f'<rect x="0.5" y="{yb0:.2f}" width="265.0" height="{alto_bul - 1.5:.2f}" fill="#fffdf7" stroke="#000000" stroke-width="0.45"/>'
        )
        svg.append(
            f'<text x="3.0" y="{yb0 + 4.5:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.7" font-weight="bold">ELEMENTOS DE FIJACIÓN ESTÁNDAR (BULONERÍA IRAM / DIN / ISO - NO NUMERADOS EN EXPLOTADA):</text>'
        )
        for j, b_txt in enumerate(resumen_buloneria):
            yb = yb0 + 9.0 + j * 4.4
            svg.append(
                f'<text x="4.5" y="{yb:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">• {_escapar_xml(b_txt)}</text>'
            )

    svg.append("</svg>")
    return "\n".join(svg)
