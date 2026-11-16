#!/usr/bin/env python3
"""
Motor reutilizable de generación automática de planos técnicos bajo normas IRAM
para proyectos de FreeCAD (TechDraw).

Normas aplicadas:
- IRAM 4504: Formatos de láminas (A4, A3, A2) y márgenes (25 mm izq. archivo, 10 mm resto).
- IRAM 4502: Líneas de dibujo técnico (espesores y tipos A, B, E, F, G).
- IRAM 4503: Letras y números en dibujo tecnológico.
- IRAM 4513: Acotación de planos en fabricación metalmecánica.
- IRAM 4505: Escalas lineales normalizadas (2:1, 1:1, 1:2, 1:5).
- IRAM 4508: Rótulo, lista de materiales (BOM) y despiece.
- IRAM 4501-2: Método de proyección ISO-E (Primer Diedro) con símbolo normalizado.
"""
import base64
import math
import os
import re
import textwrap
import FreeCAD as App
import Part


def _formatear_decimales_coma(texto):
    """Convierte puntos decimales entre dígitos a coma sin dañar abreviaturas ni rangos."""
    return re.sub(r"(?<=\d)\.(?=\d)", ",", str(texto))


def _ancho_efectivo_chars(texto, pt_fuente, ancho_col_mm):
    """Estima cuántos renglones ocupa un texto con ajuste de palabra dentro de una celda HTML."""
    usable_mm = max(8.0, float(ancho_col_mm) - 2.6)
    char_mm = max(0.75, float(pt_fuente) * 0.175)
    cap = max(8, int(usable_mm / char_mm))
    lineas = 0
    for parrafo in str(texto).splitlines() or [""]:
        wrapped = textwrap.wrap(parrafo.strip(), width=cap, break_long_words=False, break_on_hyphens=False)
        lineas += max(1, len(wrapped))
    return max(1, lineas)


def estimar_altura_cuadro_html_mm(filas_resumen, notas_taller=None, ancho_mm=104.0, font_pt=5.3):
    """Estima la altura en mm de la tabla TechDraw::DrawRichAnno para posicionarla sobre el rótulo."""
    filas = filas_resumen or [("Sin datos", "-")]
    w_c1 = 0.42 * float(ancho_mm)
    w_c2 = 0.58 * float(ancho_mm)
    line_h = float(font_pt) * 0.49
    row_pad = 1.65

    # Encabezado principal + fila de columnas
    h = (2.0 * line_h + 2.0 * row_pad)
    for item in filas:
        c1 = _formatear_decimales_coma(item[0])
        c2 = _formatear_decimales_coma(item[1])
        n_lin = max(
            _ancho_efectivo_chars(c1, font_pt, w_c1),
            _ancho_efectivo_chars(c2, font_pt, w_c2),
        )
        h += n_lin * line_h + row_pad

    notas = [n for n in (notas_taller or []) if str(n).strip()]
    if notas:
        h += line_h + row_pad  # barra título NOTAS
        pt_nota = max(4.6, float(font_pt) - 0.5)
        line_hn = pt_nota * 0.49
        n_lin_tot = 0
        for nt in notas:
            n_lin_tot += _ancho_efectivo_chars("• " + _formatear_decimales_coma(nt), pt_nota, float(ancho_mm) - 1.5)
        h += n_lin_tot * line_hn + row_pad

    # Margen conservador para bordes Qt RichText
    return round(h * 1.08 + 2.5, 1)


def generar_html_cuadro_cotas_iram(
    filas_resumen,
    notas_taller=None,
    font_pt=5.3,
    titulo="CUADRO DE COTAS Y ESPECIFICACIONES",
):
    """Genera HTML compatible con QTextDocument (DrawRichAnno) con borde real, ajuste de palabra y cero truncado."""
    filas = filas_resumen or [("Sin datos", "-")]
    pt_nota = max(4.6, float(font_pt) - 0.5)
    partes = [
        (
            f'<table border="1" cellspacing="0" cellpadding="2" width="100%" '
            f'style="font-family:\'Liberation Sans\',Arial,sans-serif; font-size:{float(font_pt):.1f}pt; '
            f'border-color:#333333; color:#111827;">'
        ),
        (
            f'<tr bgcolor="#1e3a5f">'
            f'<th colspan="2" align="left" style="color:#ffffff; font-weight:bold; padding:2px 4px;">'
            f'{_escapar_xml(titulo)}</th></tr>'
        ),
        (
            f'<tr bgcolor="#dce6f1">'
            f'<th width="42%" align="left" style="color:#0f172a; font-weight:bold;">CARACTERÍSTICA</th>'
            f'<th width="58%" align="left" style="color:#0f172a; font-weight:bold;">VALOR / ESPECIFICACIÓN</th></tr>'
        ),
    ]
    for i, item in enumerate(filas):
        bg = "#ffffff" if i % 2 == 0 else "#f5f7fa"
        c1 = _escapar_xml(_formatear_decimales_coma(item[0]))
        c2 = _escapar_xml(_formatear_decimales_coma(item[1]))
        partes.append(
            f'<tr bgcolor="{bg}">'
            f'<td width="42%" valign="top">{c1}</td>'
            f'<td width="58%" valign="top"><b>{c2}</b></td>'
            f'</tr>'
        )

    notas = [_formatear_decimales_coma(str(n).strip()) for n in (notas_taller or []) if str(n).strip()]
    if notas:
        partes.append(
            f'<tr bgcolor="#dce6f1">'
            f'<td colspan="2" style="color:#0f172a; font-weight:bold;">NOTAS DE FABRICACIÓN / CONTROL</td></tr>'
        )
        notas_html = "<br/>".join("&#8226; " + _escapar_xml(n) for n in notas)
        partes.append(
            f'<tr bgcolor="#ffffff">'
            f'<td colspan="2" style="font-size:{pt_nota:.1f}pt; color:#1e293b;">{notas_html}</td></tr>'
        )

    partes.append("</table>")
    return "\n".join(partes)


def crear_cuadro_cotas_editable_iram(
    doc,
    page,
    nombre,
    filas_resumen,
    notas_taller=None,
    ancho_mm=104.0,
    x_centro=228.0,
    y_base_min=65.0,
    font_pt=5.3,
    titulo="CUADRO DE COTAS Y ESPECIFICACIONES",
):
    """Crea TechDraw::DrawRichAnno editable por doble clic con tabla HTML ajustada al ancho disponible."""
    html = generar_html_cuadro_cotas_iram(
        filas_resumen,
        notas_taller=notas_taller,
        font_pt=font_pt,
        titulo=titulo,
    )
    h_est = estimar_altura_cuadro_html_mm(
        filas_resumen,
        notas_taller=notas_taller,
        ancho_mm=ancho_mm,
        font_pt=font_pt,
    )
    y_top = float(y_base_min) + h_est

    ra = doc.addObject("TechDraw::DrawRichAnno", nombre)
    page.addView(ra)
    ra.AnnoText = html
    ra.MaxWidth = float(ancho_mm)
    ra.Scale = 1.0
    ra.ShowFrame = False
    # En TechDraw::DrawRichAnno, (X, Y) corresponde al vértice superior izquierdo de la caja de texto.
    ra.X = float(x_centro) - 0.5 * float(ancho_mm)
    ra.Y = float(y_top)
    return ra, float(y_top), float(h_est)


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


def obtener_ruta_fcpat():
    """Busca el archivo de tramas FCPat.pat o FCPAT.pat de TechDraw (tolerante a mayúsculas en Linux)."""
    import glob
    rutas_candidatas = [
        "/snap/freecad/current/usr/share/Mod/TechDraw/PAT/FCPAT.pat",
        "/snap/freecad/current/usr/share/Mod/TechDraw/PAT/FCPat.pat",
        "/usr/share/freecad/Mod/TechDraw/PAT/FCPAT.pat",
        "/usr/share/freecad/Mod/TechDraw/PAT/FCPat.pat",
    ]
    try:
        if hasattr(App, "getUserAppDataDir"):
            rutas_candidatas.append(os.path.join(App.getUserAppDataDir(), "Mod", "TechDraw", "PAT", "FCPat.pat"))
            rutas_candidatas.append(os.path.join(App.getUserAppDataDir(), "Mod", "TechDraw", "PAT", "FCPAT.pat"))
        if hasattr(App, "getResourceDir"):
            res_dir = App.getResourceDir()
            rutas_candidatas.extend([
                os.path.join(res_dir, "Mod", "TechDraw", "PAT", "FCPAT.pat"),
                os.path.join(res_dir, "Mod", "TechDraw", "PAT", "FCPat.pat"),
            ])
    except Exception:
        pass
    rutas_candidatas.extend(glob.glob("/snap/freecad/*/usr/share/Mod/TechDraw/PAT/FCPAT.pat"))
    rutas_candidatas.extend(glob.glob("/snap/freecad/*/usr/share/Mod/TechDraw/PAT/FCPat.pat"))
    for r in rutas_candidatas:
        if os.path.isfile(r):
            return r
    return ""


def _cargar_escudo_base64(ruta_png):
    if not os.path.exists(ruta_png):
        return ""
    with open(ruta_png, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def generar_svg_plantilla_iram_fcai(formato, ruta_salida, ruta_escudo_png):
    """
    Genera una plantilla SVG para TechDraw siguiendo las normas IRAM 4504 / 4508
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

    # Coordenadas de referencia perimetral (grilla IRAM 4504)
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
    # Centrado dentro de la celda (rx + 26 .. rx + 52, ry + 30 .. ry + 41)
    sx = rx + 39.0
    sy = ry + 35.5
    simbolo_iso_e = f"""
    <g id="simbolo_iso_e" stroke="#000000" fill="none">
      <!-- Ejes de simetría (línea tipo G: trazo y punto fino) -->
      <line x1="{sx - 10.5:.2f}" y1="{sy:.2f}" x2="{sx + 8.5:.2f}" y2="{sy:.2f}" stroke-width="0.20" stroke-dasharray="3,0.8,0.5,0.8"/>
      <line x1="{sx + 4.0:.2f}" y1="{sy - 4.2:.2f}" x2="{sx + 4.0:.2f}" y2="{sy + 4.2:.2f}" stroke-width="0.20" stroke-dasharray="3,0.8,0.5,0.8"/>
      <!-- Trapecio (cono truncado vista frontal) -->
      <polygon points="{sx - 9.0:.2f},{sy - 2.8:.2f} {sx - 2.5:.2f},{sy - 1.4:.2f} {sx - 2.5:.2f},{sy + 1.4:.2f} {sx - 9.0:.2f},{sy + 2.8:.2f}" stroke-width="0.45"/>
      <!-- Dos círculos concéntricos a la derecha (vista lateral izquierda proyectada a la derecha) -->
      <circle cx="{sx + 4.0:.2f}" cy="{sy:.2f}" r="2.8" stroke-width="0.45"/>
      <circle cx="{sx + 4.0:.2f}" cy="{sy:.2f}" r="1.4" stroke-width="0.35"/>
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
  <!-- Borde exterior de corte de hoja (IRAM 4504) -->
  <rect x="0" y="0" width="{W:.1f}" height="{H:.1f}" fill="none" stroke="#000000" stroke-width="0.25"/>
  <!-- Marco exterior de referencia -->
  <rect x="{x0 - 5:.2f}" y="{y0 - 5:.2f}" width="{marco_w + 10:.2f}" height="{marco_h + 10:.2f}" fill="none" stroke="#000000" stroke-width="0.25"/>
  <!-- Recuadro principal de dibujo (IRAM 4504: margen izquierdo 25 mm, resto 10 mm, línea tipo A 0.7 mm) -->
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
    <!-- Columna escudo (0..26 mm) y divisoria Formato | Hoja en fila inferior (17.5 mm) -->
    <line x1="{rx + 26.0:.2f}" y1="{ry:.2f}" x2="{rx + 26.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.35"/>
    <line x1="{rx + 17.5:.2f}" y1="{ry + 41.0:.2f}" x2="{rx + 17.5:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.25"/>
    <!-- Separador Carrera / Cátedra en filas 2 y 3 -->
    <line x1="{rx + 85.0:.2f}" y1="{ry + 7.5:.2f}" x2="{rx + 85.0:.2f}" y2="{ry + 22.5:.2f}" stroke="#000000" stroke-width="0.35"/>
    <!-- Columnas inferiores (ry+30 .. ry+51) -->
    <line x1="{rx + 52.0:.2f}" y1="{ry + 30.0:.2f}" x2="{rx + 52.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.35"/>
    <line x1="{rx + 132.0:.2f}" y1="{ry + 30.0:.2f}" x2="{rx + 132.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.50"/>
    <line x1="{rx + 92.0:.2f}" y1="{ry + 41.0:.2f}" x2="{rx + 92.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.35"/>
    <!-- Subdivisión entre Tol. Gral. (92..114) y Masa (114..132) para evitar apilar 3 líneas -->
    <line x1="{rx + 114.0:.2f}" y1="{ry + 41.0:.2f}" x2="{rx + 114.0:.2f}" y2="{ry + rh:.2f}" stroke="#000000" stroke-width="0.25"/>

    <!-- Símbolo ISO-E -->
    {simbolo_iso_e}

    <!-- Etiquetas fijas del rótulo (IRAM 4508: separadas +2.4 mm debajo de cada línea horizontal) -->
    <g font-family="Liberation Sans, Arial, sans-serif" font-size="1.8" fill="#555555">
      <text x="{rx + 1.8:.2f}" y="{ry + 32.3:.2f}">Escala:</text>
      <text x="{rx + 1.5:.2f}" y="{ry + 43.2:.2f}">Formato:</text>
      <text x="{rx + 18.5:.2f}" y="{ry + 43.2:.2f}">Hoja:</text>
      <text x="{rx + 28.0:.2f}" y="{ry + 43.2:.2f}">Fecha:</text>
      <text x="{rx + 54.0:.2f}" y="{ry + 32.3:.2f}">Denominación / Título del Plano:</text>
      <text x="{rx + 54.0:.2f}" y="{ry + 43.2:.2f}">Material:</text>
      <text x="{rx + 93.5:.2f}" y="{ry + 43.2:.2f}">Tol. Gral.:</text>
      <text x="{rx + 115.5:.2f}" y="{ry + 43.2:.2f}">Masa:</text>
      <text x="{rx + 134.0:.2f}" y="{ry + 32.1:.2f}">Dibujó / Revisó:</text>
      <text x="{rx + 134.0:.2f}" y="{ry + 43.2:.2f}">Plano Nº:</text>
    </g>

    <!-- Textos editables (ubicados en la franja inferior de cada celda sin pisar bordes ni subtítulos) -->
    <g font-family="Liberation Sans, Arial, sans-serif" fill="#000000">
      <text freecad:editable="INSTITUCION" x="{rx + 100.5:.2f}" y="{ry + 5.2:.2f}" font-size="3.2" font-weight="bold" text-anchor="middle"><tspan>Facultad de Ciencias Aplicadas a la Industria - UNCUYO</tspan></text>
      <text freecad:editable="CARRERA" x="{rx + 55.5:.2f}" y="{ry + 12.6:.2f}" font-size="2.9" text-anchor="middle"><tspan>Ingeniería Mecánica</tspan></text>
      <text freecad:editable="CATEDRA" x="{rx + 130.0:.2f}" y="{ry + 12.6:.2f}" font-size="2.9" text-anchor="middle"><tspan>Máquinas Térmicas e Hidráulicas</tspan></text>
      <text freecad:editable="CURSO" x="{rx + 55.5:.2f}" y="{ry + 20.0:.2f}" font-size="2.7" text-anchor="middle"><tspan>4to Año - Segundo semestre</tspan></text>
      <text freecad:editable="PROFESOR" x="{rx + 130.0:.2f}" y="{ry + 20.0:.2f}" font-size="2.7" text-anchor="middle"><tspan>Profesor: Analía Bonino</tspan></text>
      <text freecad:editable="PROYECTO" x="{rx + 100.5:.2f}" y="{ry + 27.5:.2f}" font-size="3.0" font-weight="bold" text-anchor="middle"><tspan>Diseño y construcción de una bomba de simulación de flujo cardíaco</tspan></text>

      <!-- Escala -->
      <text freecad:editable="ESCALA" x="{rx + 13.0:.2f}" y="{ry + 39.0:.2f}" font-size="3.8" font-weight="bold" text-anchor="middle"><tspan>1:1</tspan></text>
      <!-- Formato y Hoja en subceldas propias (sin text-anchor="end") -->
      <text freecad:editable="FORMATO" x="{rx + 8.8:.2f}" y="{ry + 48.6:.2f}" font-size="2.3" font-weight="bold" text-anchor="middle"><tspan>IRAM {formato}</tspan></text>
      <text freecad:editable="HOJA" x="{rx + 21.8:.2f}" y="{ry + 48.6:.2f}" font-size="2.3" text-anchor="middle"><tspan>1/1</tspan></text>

      <!-- Fecha -->
      <text freecad:editable="FECHA" x="{rx + 39.0:.2f}" y="{ry + 48.6:.2f}" font-size="2.6" text-anchor="middle"><tspan>12/11/2026</tspan></text>

      <!-- Título de la pieza/conjunto -->
      <text freecad:editable="TITULO" x="{rx + 92.0:.2f}" y="{ry + 38.8:.2f}" font-size="3.6" font-weight="bold" text-anchor="middle"><tspan>Denominación de la Pieza</tspan></text>

      <!-- Material (font-size 2.35 para admitir nombres largos como "Acero Inox. AISI 304") -->
      <text freecad:editable="MATERIAL" x="{rx + 72.0:.2f}" y="{ry + 48.6:.2f}" font-size="2.35" font-weight="bold" text-anchor="middle"><tspan>AISI 304</tspan></text>
      <!-- Tolerancia General y Masa en subceldas contiguas -->
      <text freecad:editable="TOL_GRAL" x="{rx + 103.0:.2f}" y="{ry + 48.6:.2f}" font-size="2.15" text-anchor="middle"><tspan>ISO 2768-mK</tspan></text>
      <text freecad:editable="MASA" x="{rx + 123.0:.2f}" y="{ry + 48.6:.2f}" font-size="2.15" text-anchor="middle"><tspan>3185 g</tspan></text>

      <!-- Autor y Aprobado con margen izquierdo rx+134.0 (despegados de la línea vertical rx+132.0) -->
      <text freecad:editable="AUTOR" x="{rx + 134.0:.2f}" y="{ry + 35.8:.2f}" font-size="2.3"><tspan>Dib.: F. Gutiérrez</tspan></text>
      <text freecad:editable="APROBADO" x="{rx + 134.0:.2f}" y="{ry + 39.2:.2f}" font-size="2.2"><tspan>Apr.: Ing. A. Bonino</tspan></text>
      <text freecad:editable="NUM_PLANO" x="{rx + 153.5:.2f}" y="{ry + 48.8:.2f}" font-size="3.8" font-weight="bold" text-anchor="middle"><tspan>Plano Nº 1</tspan></text>
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

    if dim_max <= 16.5 and suma_vistas <= 28.0:
        return "A4", 5.0, "5:1"
    if dim_max <= 38.0 and suma_vistas <= 65.0:
        return "A4", 2.0, "2:1"
    if dim_max <= 55.0 and suma_vistas <= 95.0:
        return "A3", 2.0, "2:1"

    if dim_max <= 85.0 and suma_vistas <= 135.0:
        return "A4", 1.0, "1:1"

    if dim_max <= 145.0 and suma_vistas <= 225.0:
        return "A3", 1.0, "1:1"

    if dim_max <= 340.0:
        return "A3", 0.5, "1:2"

    return "A3", 0.2, "1:5"


def estilizar_vista_iram(vista, mostrar_ocultas=False, mostrar_centros=True):
    """Aplica espesores de línea IRAM 4502 (grupo fino 0,35 mm) y preferencias TechDraw."""
    try:
        p_dec = App.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Decorations")
        if p_dec.GetInt("LineGroup", -1) != 1:
            p_dec.SetInt("LineGroup", 1)  # *FC 0.35mm (visible=0.35, graphic=0.25, hidden=0.18)
            App.saveParameter()
    except Exception:
        pass
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
                vo.LineWidth = 0.35  # IRAM 4502 Tipo A (contornos visibles levemente más finos)
            if hasattr(vo, "HiddenWidth"):
                vo.HiddenWidth = 0.18  # IRAM 4502 Tipo E (aristas ocultas)
            if hasattr(vo, "IsoWidth"):
                vo.IsoWidth = 0.18
            if hasattr(vo, "ArcCenterMarks"):
                vo.ArcCenterMarks = mostrar_centros
            # Los ejes trazo-y-punto normados IRAM 4502 se generan vía
            # agregar_ejes_simetria_iram (CosmeticEdge lineNumber=4), evitando
            # duplicar líneas continuas sólidas de Horiz/VertCenterLine.
            if hasattr(vo, "HorizCenterLine"):
                vo.HorizCenterLine = False
            if hasattr(vo, "VertCenterLine"):
                vo.VertCenterLine = False
        except Exception:
            pass


def _hacer_linea_eje_cosmetica(vista, p1, p2, grosor=0.20, color=(0.0, 0.0, 0.0, 1.0)):
    """Crea una CosmeticEdge de eje (ISO 128-20 LongDashedDotted: lineNumber=4)."""
    tag = vista.makeCosmeticLine(p1, p2, 4, grosor, color)
    if tag:
        try:
            ce = vista.getCosmeticEdge(tag)
            if ce is not None:
                fmt = dict(ce.Format)
                fmt["style"] = 4
                fmt["lineNumber"] = 4
                fmt["weight"] = float(grosor)
                fmt["color"] = color
                ce.Format = fmt
        except Exception:
            pass
    return tag


def _limites_aristas_2d(edges):
    xmin, ymin, xmax, ymax = 1e9, 1e9, -1e9, -1e9
    for e in edges:
        bb = e.BoundBox
        xmin = min(xmin, bb.XMin)
        xmax = max(xmax, bb.XMax)
        ymin = min(ymin, bb.YMin)
        ymax = max(ymax, bb.YMax)
    return xmin, ymin, xmax, ymax


def agregar_ejes_simetria_iram(vista, es_revolucion=False, dx_ext=6.0, dy_ext=6.0):
    """
    Agrega ejes de simetría (IRAM 4502 Tipo G: trazo y punto fino, lineNumber=4)
    centrados en la vista según su BoundBox 2D.
    Toma en cuenta vista.Scale para pasar coordenadas en escala de modelo 3D.
    """
    try:
        edges = vista.getVisibleEdges()
        if not edges:
            return
        xmin, ymin, xmax, ymax = _limites_aristas_2d(edges)
        cx = 0.5 * (xmin + xmax)
        cy = 0.5 * (ymin + ymax)
        w = max(2.0, xmax - xmin)
        h = max(2.0, ymax - ymin)
        escala = float(getattr(vista, "Scale", 1.0) or 1.0)

        # Coordenadas modelo = coordenadas papel / escala
        cx_m = cx / escala
        cy_m = cy / escala
        hw_m = (0.5 * w + dx_ext) / escala
        hh_m = (0.5 * h + dy_ext) / escala

        # Eje horizontal (trazo y punto fino: ISO 128-20 lineNumber 4, grosor 0.20 mm)
        _hacer_linea_eje_cosmetica(
            vista,
            App.Vector(cx_m - hw_m, cy_m, 0.0),
            App.Vector(cx_m + hw_m, cy_m, 0.0),
            grosor=0.20,
            color=(0.0, 0.0, 0.0, 1.0),
        )
        # Eje vertical (trazo y punto fino: ISO 128-20 lineNumber 4, grosor 0.20 mm)
        _hacer_linea_eje_cosmetica(
            vista,
            App.Vector(cx_m, cy_m - hh_m, 0.0),
            App.Vector(cx_m, cy_m + hh_m, 0.0),
            grosor=0.20,
            color=(0.0, 0.0, 0.0, 1.0),
        )
    except Exception:
        pass


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
            bonus_sup = 2.0 if c.y >= cy_vista - 0.5 else -5.0
            score = e.Length - dist_centro * 3.0 + bonus_sup
            if actual is None or score > actual[1]:
                circulos_por_diam[clave] = (idx, score, r, c.x, c.y, d, dist_centro)

    if not circulos_por_diam:
        return []

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
    angulos_deg = [62.0, 118.0, 26.0, 154.0]
    cotas_creadas = []
    idx_conc = 0
    cajas_ocupadas = []

    _es_rect = any(
        abs(abs(v.X) - (cx_vista - xmin)) < 2.5
        and abs(abs(v.Y) - (cy_vista - ymin)) < 2.5
        for _e in (vista.getVisibleEdges() if hasattr(vista, "getVisibleEdges") else [])
        for v in _e.Vertexes
    )
    _xmax_r = 2.0 * cx_vista - xmin
    _ymax_r = 2.0 * cy_vista - ymin

    def _cabe_etiqueta(x_cand, y_cand):
        bw, bh = 18.0, 7.6
        if not (dx_min_s + 9.5 <= x_cand <= dx_max_s - 9.5):
            return False
        ly_min_lim = max(dy_min_s + 4.0, ymin + 2.5 if r_max_vista > 8.0 else cy_vista + 5.0)
        if not (ly_min_lim <= y_cand <= dy_max_s - 4.2):
            return False
        # Evitar cruzar el contorno sólido (incl. esquinas de placas cuadradas) o flechas A-A
        if _es_rect and (xmin - 8.5 <= x_cand <= _xmax_r + 8.5) and (ymin - 5.0 <= y_cand <= _ymax_r + 5.0):
            return False
        dist_v = math.hypot(x_cand - cx_vista, y_cand - cy_vista)
        if dist_v < r_max_vista + 5.0:
            return False
        if abs(y_cand - cy_vista) < 7.5 and abs(x_cand - cx_vista) > r_max_vista * 0.65:
            return False
        x0, y0, x1, y1 = x_cand - 0.5 * bw, y_cand - 0.5 * bh, x_cand + 0.5 * bw, y_cand + 0.5 * bh
        for ox0, oy0, ox1, oy1 in cajas_ocupadas:
            if x0 < ox1 + 1.5 and x1 + 1.5 > ox0 and y0 < oy1 + 1.2 and y1 + 1.2 > oy0:
                return False
        return True

    def _ubicar_etiqueta(ang_pref_deg, r_ini, xc_ref, yc_ref):
        cands_ang = [ang_pref_deg, ang_pref_deg + 16.0, ang_pref_deg - 16.0, ang_pref_deg + 30.0, ang_pref_deg - 30.0, 72.0, 108.0, 32.0, 148.0]
        for dr in (0.0, 7.0, 14.0, 21.0):
            r_tot = r_ini + dr
            for a_deg in cands_ang:
                if a_deg < 22.0 or a_deg > 158.0:
                    continue
                ang_r = math.radians(a_deg)
                xc = xc_ref + r_tot * math.cos(ang_r)
                yc = yc_ref + r_tot * math.sin(ang_r)
                if _cabe_etiqueta(xc, yc):
                    return xc, yc
        ang_r = math.radians(max(24.0, min(156.0, ang_pref_deg)))
        ly_min_lim = max(dy_min_s + 4.0, ymin + 2.5 if r_max_vista > 8.0 else cy_vista + 5.0)
        return (
            max(dx_min_s + 9.5, min(dx_max_s - 9.5, xc_ref + r_ini * math.cos(ang_r))),
            max(ly_min_lim, min(dy_max_s - 4.2, yc_ref + r_ini * math.sin(ang_r))),
        )

    for k, (edge_idx, _, r_papel, cx, cy, _, dist_centro) in enumerate(seleccionados):
        dim = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Diam_{k+1}")
        page.addView(dim)
        dim.Type = "Diameter"
        dim.MeasureType = "Projected"
        dim.FormatSpec = "⌀%.2w"
        dim.References2D = [(vista, f"Edge{edge_idx}")]

        if dist_centro <= 1.5:
            ang_deg = angulos_deg[idx_conc % len(angulos_deg)]
            nivel = idx_conc // 2
            dist_etiqueta = max(12.0, r_max_vista + 10.5 + nivel * 8.5)
            lx, ly = _ubicar_etiqueta(ang_deg, dist_etiqueta, cx, cy)
            idx_conc += 1
        else:
            ang_hole = math.degrees(math.atan2(max(2.0, cy - cy_vista), cx - cx_vista))
            ang_deg = max(24.0, min(68.0, ang_hole)) if cx >= cx_vista else max(112.0, min(156.0, ang_hole))
            dist_global = max(13.0, r_max_vista + 11.5)
            lx, ly = _ubicar_etiqueta(ang_deg, dist_global, cx_vista, cy_vista)

        dim.X = lx
        dim.Y = ly
        cajas_ocupadas.append((lx - 9.0, ly - 3.8, lx + 9.0, ly + 3.8))
        _estilizar_cota(dim)
        cotas_creadas.append(dim)

    return cotas_creadas


def _estilizar_cota(dim):
    vo = getattr(dim, "ViewObject", None)
    if vo:
        try:
            vo.Fontsize = 3.5
            vo.Color = (0.0, 0.0, 0.0)
        except Exception:
            pass


def _indices_extremos_vertices_2d(vista):
    """Devuelve los índices (i_minx, i_maxx, i_miny, i_maxy) y límites de `getVisibleVertexes()`."""
    try:
        vs = vista.getVisibleVertexes()
        edges = vista.getVisibleEdges()
    except Exception:
        vs = []
        edges = []
    if not vs:
        return None
    if edges:
        ex0, ey0, ex1, ey1 = _limites_aristas_2d(edges)
        validos = [
            i for i, v in enumerate(vs)
            if (ex0 - 0.5) <= v.x <= (ex1 + 0.5) and (ey0 - 0.5) <= v.y <= (ey1 + 0.5)
        ]
    else:
        validos = list(range(len(vs)))
    if not validos:
        validos = list(range(len(vs)))
    i_minx = min(validos, key=lambda i: (vs[i].x, abs(vs[i].y)))
    i_maxx = max(validos, key=lambda i: (vs[i].x, -abs(vs[i].y)))
    i_miny = min(validos, key=lambda i: (vs[i].y, abs(vs[i].x)))
    i_maxy = max(validos, key=lambda i: (vs[i].y, -abs(vs[i].x)))
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
    IRAM 4513 para evitar cualquier superposición con el `Caption` inferior de la vista.
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

    if h_papel >= 2.0:
        if i_miny is not None and i_maxy is not None and i_miny != i_maxy:
            dim_h = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Alt_1")
            page.addView(dim_h)
            dim_h.Type = "DistanceY"
            dim_h.MeasureType = "Projected"
            dim_h.FormatSpec = "%.2w"
            dim_h.References2D = [(vista, f"Vertex{i_miny}"), (vista, f"Vertex{i_maxy}")]
            dim_h.X = min(dx_max_s - 8.5, xmax + 12.0)
            h_seg = abs(vs[i_maxy].y - vs[i_miny].y)
            dim_h.Y = min(dy_max_s - 4.5, max(vs[i_miny].y, vs[i_maxy].y) + 5.5) if h_seg < 11.0 else cy_vista
            _estilizar_cota(dim_h)
            cotas.append(dim_h)
        elif aristas_vert:
            aristas_vert.sort(key=lambda x: x[1], reverse=True)
            idx_v, h_seg, _, yv0, yv1 = aristas_vert[0]
            dim_h = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Alt_1")
            page.addView(dim_h)
            dim_h.Type = "DistanceY"
            dim_h.MeasureType = "Projected"
            dim_h.FormatSpec = "%.2w"
            dim_h.References2D = [(vista, f"Edge{idx_v}")]
            dim_h.X = min(dx_max_s - 8.5, xmax + 12.0)
            dim_h.Y = min(dy_max_s - 4.5, max(yv0, yv1) + 5.5) if h_seg < 11.0 else 0.5 * (yv0 + yv1)
            _estilizar_cota(dim_h)
            cotas.append(dim_h)

        aristas_vert_ord = sorted(aristas_vert, key=lambda x: x[1], reverse=True)
        for idx_v2, lv2, xv2, y2a, y2b in aristas_vert_ord:
            if abs(lv2 - h_papel) > 2.5 and lv2 >= 4.0:
                dim_h2 = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Alt_2")
                page.addView(dim_h2)
                dim_h2.Type = "DistanceY"
                dim_h2.MeasureType = "Projected"
                dim_h2.FormatSpec = "%.2w"
                dim_h2.References2D = [(vista, f"Edge{idx_v2}")]
                dim_h2.X = max(dx_min_s + 8.5, xmin - 12.0)
                dim_h2.Y = min(dy_max_s - 4.5, max(y2a, y2b) + 5.5) if lv2 < 11.0 else 0.5 * (y2a + y2b)
                _estilizar_cota(dim_h2)
                cotas.append(dim_h2)
                break

    if w_papel >= 2.5:
        fmt_x = "⌀%.2w" if es_revolucion else "%.2w"

        par_interior = None
        if vs:
            cand_sup = [
                i for i, v in enumerate(vs)
                if abs(v.y - ymax) < max(3.0, 0.25 * h_papel) and abs(v.x - cx_vista) >= 2.5
            ]
            por_radio = {}
            for i in cand_sup:
                rad = round(abs(vs[i].x - cx_vista), 1)
                if rad * 2.0 < w_papel - 2.0 and rad * 2.0 >= 3.5:
                    por_radio.setdefault(rad, []).append(i)
            for rad in sorted(por_radio.keys(), reverse=True):
                idxs = por_radio[rad]
                izq = [i for i in idxs if vs[i].x < cx_vista]
                der = [i for i in idxs if vs[i].x > cx_vista]
                if izq and der:
                    par_interior = (izq[0], der[0])
                    break

        y_cota_total = ymax + 10.5
        if par_interior is not None and (ymax + 21.0) <= dy_max_s - 3.0:
            dim_w_int = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Ancho_Int")
            page.addView(dim_w_int)
            dim_w_int.Type = "DistanceX"
            dim_w_int.MeasureType = "Projected"
            dim_w_int.FormatSpec = fmt_x
            dim_w_int.References2D = [(vista, f"Vertex{par_interior[0]}"), (vista, f"Vertex{par_interior[1]}")]
            dim_w_int.X = cx_vista
            dim_w_int.Y = ymax + 10.5
            _estilizar_cota(dim_w_int)
            cotas.append(dim_w_int)
            y_cota_total = ymax + 20.5

        if i_minx is not None and i_maxx is not None and i_minx != i_maxx:
            dim_w = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Ancho_1")
            page.addView(dim_w)
            dim_w.Type = "DistanceX"
            dim_w.MeasureType = "Projected"
            dim_w.FormatSpec = fmt_x
            dim_w.References2D = [(vista, f"Vertex{i_minx}"), (vista, f"Vertex{i_maxx}")]
            dim_w.X = cx_vista
            dim_w.Y = min(dy_max_s - 3.5, y_cota_total)
            _estilizar_cota(dim_w)
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
            _estilizar_cota(dim_w)
            cotas.append(dim_w)

    return cotas


def _extraer_mm(val_str):
    import re as _re
    m = _re.search(r"[-+]?\d+(?:\.\d+)?", str(val_str or ""))
    return float(m.group(0)) if m else None


def acotar_detalles_y_roscas_corte_iram(
    doc,
    page,
    vista,
    prefijo_nombre,
    filas_param,
    cotas_existentes=None,
    formato="A3",
):
    """
    Complementa la vista de corte A-A según IRAM 4520 / ISO 6410-1:
    1. Dibuja líneas cosméticas de rosca (flancos al diámetro nominal exterior, línea de fin
       de rosca útil y eje trazo-punto) en los agujeros roscados visibles en el corte.
    2. Acota visualmente la profundidad de las roscas y profundidades internas evitando solapes.
    """
    try:
        edges = vista.getVisibleEdges()
    except Exception:
        return []
    if not edges or not filas_param:
        return []

    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    ext = _indices_extremos_vertices_2d(vista)
    if ext is not None:
        _, _, _, _, xmin, ymin, xmax, ymax, _ = ext
    else:
        xmin, ymin, xmax, ymax = _limites_aristas_2d(edges)
    cx_vista = 0.5 * (xmin + xmax)
    dx_min_s, dx_max_s, dy_min_s, dy_max_s = _limites_seguros_hoja(vista, formato=formato)

    vx = float(vista.X.Value)
    vy = float(vista.Y.Value)
    W_hoja, _ = FORMATOS_IRAM.get(formato, FORMATOS_IRAM["A3"])
    rx0_rel = (W_hoja - 10.0) - 175.0 - vx
    ry1_rel = 61.0 - vy

    TABLA_ROSCAS = [
        ("m3", 2.5, 3.0, "M3"),
        ("m4", 3.3, 4.0, "M4"),
        ("m5", 4.2, 5.0, "M5"),
        ("m6", 5.0, 6.0, "M6"),
        ("m8", 6.8, 8.0, "M8"),
        ("m10", 8.5, 10.0, "M10"),
        ("m12", 11.0, 12.0, "M12"),
        ("m14", 12.0, 14.0, "M14"),
        ("g18", 8.8, 9.73, "G1/8"),
    ]

    NO_ROSCA_TOKENS = ("aguj", "pas", "caj", "aloj", "avell", "corona", "despeje")
    NO_ROSCA_DESC = ("pasante", "cajeado", "alojamiento", "corona", "despeje")
    roscas_pieza = []
    profs_rosca = []
    profs_internas = []
    for alias, val_str, desc in filas_param:
        al_l = str(alias).lower()
        desc_l = str(desc).lower()
        val_mm = _extraer_mm(val_str)
        if val_mm is None or val_mm <= 0.2:
            continue
        es_solo_aguj_pasante = (
            (any(tok in al_l for tok in NO_ROSCA_TOKENS) or any(tok in desc_l for tok in NO_ROSCA_DESC))
            and "rosc" not in al_l
            and "rosc" not in desc_l
        )
        if al_l.startswith("d_") and not es_solo_aguj_pasante:
            for clave, d_def, d_nom, etiq in TABLA_ROSCAS:
                if clave in al_l or clave in desc_l or (clave == "g18" and "g 1/8" in desc_l):
                    roscas_pieza.append((clave, val_mm if abs(val_mm - d_def) < 1.2 else d_def, d_nom, etiq))
                    break
        if al_l.startswith(("p_m", "p_g18", "p_rosca", "l_rosca")) and not es_solo_aguj_pasante:
            tag = ""
            for clave, _, _, etiq in TABLA_ROSCAS:
                if clave in al_l or clave in desc_l:
                    tag = etiq
                    break
            profs_rosca.append((val_mm, tag))
        elif al_l.startswith(("p_cav", "p_reb", "p_caj", "p_aloj", "p_reten", "p_esc", "a_ran")):
            profs_internas.append((val_mm, alias))

    aristas_vert = []
    aristas_horiz = []
    for idx, e in enumerate(edges):
        bb = e.BoundBox
        curva = getattr(e, "Curve", None)
        if curva and curva.TypeId == "Part::GeomLine" and e.Length >= 1.2:
            dx = abs(bb.XMax - bb.XMin)
            dy = abs(bb.YMax - bb.YMin)
            if dx < 0.05 and dy >= 1.2:
                aristas_vert.append((idx, dy, 0.5 * (bb.XMin + bb.XMax), bb.YMin, bb.YMax))
            elif dy < 0.05 and dx >= 1.2:
                aristas_horiz.append((idx, dx, 0.5 * (bb.YMin + bb.YMax), bb.XMin, bb.XMax))

    pos_ocupadas = [(float(c.X.Value), float(c.Y.Value)) for c in (cotas_existentes or [])]
    alt_existentes = []
    for c in (cotas_existentes or []):
        if getattr(c, "Type", "") == "DistanceY":
            try:
                alt_existentes.append(float(c.NominalValue))
            except Exception:
                pass

    def _lugar_libre(x_pref, y_pref, lado_izq, label_len=8):
        alto_txt = max(16.0, label_len * 2.4)
        x_cand = x_pref
        if not lado_izq and x_cand >= rx0_rel - 4.0 and y_pref <= ry1_rel + 4.0:
            x_cand = max(dx_min_s + 9.0, xmin - 18.0)
            lado_izq = True
        x_cand = max(dx_min_s + 9.0, min(dx_max_s - 9.0, x_cand))
        y_base = max(ymin + 1.0, min(ymax - 0.5, y_pref))
        for dx_step in (0.0, -10.0 if lado_izq else 10.0, -20.0 if lado_izq else 20.0):
            xc = max(dx_min_s + 9.0, min(dx_max_s - 9.0, x_cand + dx_step))
            for delta in (0.0, 9.0, -9.0, 18.0, -18.0):
                yc = max(ymin + 0.8, min(dy_max_s - 4.0, y_base + delta))
                if not lado_izq and xc >= rx0_rel - 4.0 and yc <= ry1_rel + 4.0:
                    continue
                colision = False
                for ox, oy in pos_ocupadas:
                    if abs(xc - ox) < 9.5 and abs(yc - oy) < alto_txt:
                        colision = True
                        break
                if not colision:
                    return xc, yc
        return None

    cotas_nuevas = []
    prof_acotadas = set()

    usados = set()
    pares_rosca = []
    for i in range(len(aristas_vert)):
        if i in usados:
            continue
        idx_a, len_a, xa, ya0, ya1 = aristas_vert[i]
        for j in range(i + 1, len(aristas_vert)):
            if j in usados:
                continue
            idx_b, len_b, xb, yb0, yb1 = aristas_vert[j]
            if abs(ya0 - yb0) > 0.25 or abs(ya1 - yb1) > 0.25:
                continue
            sep_real = abs(xa - xb) / escala
            len_real = 0.5 * (len_a + len_b) / escala
            match_rosca = None
            for clave, d_mecha, d_nom, etiq in roscas_pieza:
                if abs(sep_real - d_mecha) <= 0.22:
                    if any(abs(len_real - pr) <= 0.35 and (not t or t == etiq) for pr, t in profs_rosca) or len_real >= 2.5:
                        match_rosca = (clave, d_mecha, d_nom, etiq, len_real)
                        break
            if match_rosca:
                usados.add(i)
                usados.add(j)
                pares_rosca.append((idx_a, idx_b, xa, xb, ya0, ya1, match_rosca))
                break

    h_corte_papel = ymax - ymin
    permitir_cotas_en_corte = h_corte_papel >= 26.0

    for idx_a, idx_b, xa, xb, y0, y1, (clave, d_mecha, d_nom, etiq, len_real) in pares_rosca:
        x_mid = 0.5 * (xa + xb)
        r_nom = 0.5 * d_nom * escala
        try:
            x_m0 = (x_mid - r_nom) / escala
            x_m1 = (x_mid + r_nom) / escala
            y_m0 = y0 / escala
            y_m1 = y1 / escala
            x_mid_m = x_mid / escala
            vista.makeCosmeticLine(
                App.Vector(x_m0, y_m0, 0),
                App.Vector(x_m0, y_m1, 0),
                1, 0.18, (0.0, 0.0, 0.0, 1.0),
            )
            vista.makeCosmeticLine(
                App.Vector(x_m1, y_m0, 0),
                App.Vector(x_m1, y_m1, 0),
                1, 0.18, (0.0, 0.0, 0.0, 1.0),
            )
            _hacer_linea_eje_cosmetica(
                vista,
                App.Vector(x_mid_m, y_m0 - 0.8 / escala, 0),
                App.Vector(x_mid_m, y_m1 + 0.8 / escala, 0),
                grosor=0.15,
                color=(0.25, 0.25, 0.25, 1.0),
            )
            for _, dx_h, yh, xh0, xh1 in aristas_horiz:
                if xh0 <= x_mid <= xh1 and dx_h <= (d_mecha * escala + 0.6):
                    if abs(yh - y0) < 0.2 or abs(yh - y1) < 0.2:
                        vista.makeCosmeticLine(
                            App.Vector(x_m0, yh / escala, 0),
                            App.Vector(x_m1, yh / escala, 0),
                            1, 0.18, (0.0, 0.0, 0.0, 1.0),
                        )
        except Exception:
            pass

        clave_prof = (etiq, round(len_real, 2))
        if permitir_cotas_en_corte and clave_prof not in prof_acotadas and len(cotas_nuevas) < 2:
            lado_izq = x_mid < cx_vista
            x_pref = (xmin - 16.5) if lado_izq else (xmax + 16.5)
            pos = _lugar_libre(x_pref, 0.5 * (y0 + y1), lado_izq, label_len=len(f"{etiq} prof. {len_real:.2f}"))
            if pos is not None:
                dim_r = doc.addObject(
                    "TechDraw::DrawViewDimension",
                    f"{prefijo_nombre}_Rosca_{len(cotas_nuevas) + 1}",
                )
                page.addView(dim_r)
                dim_r.Type = "DistanceY"
                dim_r.MeasureType = "Projected"
                dim_r.FormatSpec = f"{etiq} prof. %.2w"
                dim_r.References2D = [(vista, f"Edge{idx_a}")]
                dim_r.X, dim_r.Y = pos
                _estilizar_cota(dim_r)
                cotas_nuevas.append(dim_r)
                pos_ocupadas.append(pos)
                prof_acotadas.add(clave_prof)

    n_int = 0
    for val_mm, alias in profs_internas:
        if not permitir_cotas_en_corte or n_int >= 1:
            break
        if any(abs(val_mm - ae) <= 0.3 for ae in alt_existentes):
            continue
        if any(abs(val_mm - p[1]) <= 0.3 for p in prof_acotadas):
            continue
        cand = [
            (idx, len_p, x, y0, y1)
            for idx, len_p, x, y0, y1 in aristas_vert
            if abs((len_p / escala) - val_mm) <= 0.25
        ]
        if not cand:
            continue
        cand.sort(key=lambda item: item[2])
        idx_e, _, xe, y0, y1 = cand[0]
        lado_izq = xe < cx_vista
        x_pref = (xmin - 16.5) if lado_izq else (xmax + 16.5)
        pos = _lugar_libre(x_pref, 0.5 * (y0 + y1), lado_izq, label_len=6)
        if pos is not None:
            dim_i = doc.addObject(
                "TechDraw::DrawViewDimension",
                f"{prefijo_nombre}_Prof_{n_int + 1}",
            )
            page.addView(dim_i)
            dim_i.Type = "DistanceY"
            dim_i.MeasureType = "Projected"
            dim_i.FormatSpec = "%.2w"
            dim_i.References2D = [(vista, f"Edge{idx_e}")]
            dim_i.X, dim_i.Y = pos
            _estilizar_cota(dim_i)
            cotas_nuevas.append(dim_i)
            pos_ocupadas.append(pos)
            prof_acotadas.add((alias, round(val_mm, 2)))
            n_int += 1

    return cotas_nuevas


def _esperar_hlr_vista(doc, vista, timeout_s=20.0):
    """Espera a que una vista TechDraw complete su proyección HLR tanto en GUI como en CLI."""
    import time as _time
    t0 = _time.time()
    edges = []
    while _time.time() - t0 < float(timeout_s):
        try:
            edges = vista.getVisibleEdges()
        except Exception:
            edges = []
        if edges:
            return edges
        if App.GuiUp:
            try:
                import FreeCADGui as Gui
                Gui.updateGui()
            except Exception:
                pass
        else:
            doc.recompute()
        _time.sleep(0.15)
    return edges


def crear_vista_detalle_roscas_iram(
    doc,
    page,
    vista_corte,
    prefijo_nombre,
    filas_param,
    anchor_point,
    x_detalle,
    y_detalle,
    radio_corte=9.5,
    escala_detalle=2.0,
    ref_letra="A",
):
    """
    Crea una Vista de Detalle ampliada (`TechDraw::DrawViewDetail`, p.ej. Detalle A 2:1)
    a partir de `vista_corte`, dibuja líneas cosméticas de rosca IRAM 4520 en su interior
    y coloca cotas de profundidad de roscas y cavidades bien separadas (una por lado, sin solapes).
    """
    det = doc.addObject("TechDraw::DrawViewDetail", f"{prefijo_nombre}_Detalle_{ref_letra}")
    page.addView(det)
    det.BaseView = vista_corte
    det.AnchorPoint = anchor_point
    det.Radius = radio_corte
    det.ScaleType = "Custom"
    det.Scale = escala_detalle
    det.Reference = ref_letra
    det.X = x_detalle
    det.Y = y_detalle
    det.Caption = ""
    det.ShowHighlight = True
    det.ShowMatting = True
    estilizar_vista_iram(det, mostrar_ocultas=False, mostrar_centros=False)

    # Subtítulo de escala ubicado debajo del rótulo nativo "DETAIL X" sin solaparlo
    r_papel = radio_corte * escala_detalle
    try:
        ann = doc.addObject("TechDraw::DrawViewAnnotation", f"{prefijo_nombre}_Txt_Det_{ref_letra}")
        page.addView(ann)
        esc_lbl = f"{float(escala_detalle):g}".replace(".", ",")
        ann.Text = [f"Esc. {esc_lbl}:1"]
        ann.TextSize = 3.0
        ann.X = x_detalle
        ann.Y = y_detalle - r_papel - 10.5
    except Exception:
        pass

    doc.recompute()

    edges = _esperar_hlr_vista(doc, det, timeout_s=20.0)
    if not edges:
        return det, []

    r_papel = radio_corte * escala_detalle
    escala = float(getattr(det, "Scale", escala_detalle) or escala_detalle)

    TABLA_ROSCAS = [
        ("m3", 2.5, 3.0, "M3"),
        ("m4", 3.3, 4.0, "M4"),
        ("m5", 4.2, 5.0, "M5"),
        ("m6", 5.0, 6.0, "M6"),
        ("m8", 6.8, 8.0, "M8"),
        ("m10", 8.5, 10.0, "M10"),
        ("m12", 11.0, 12.0, "M12"),
        ("m14", 12.0, 14.0, "M14"),
        ("g18", 8.8, 9.73, "G1/8"),
    ]
    NO_ROSCA_TOKENS = ("aguj", "pas", "caj", "aloj", "avell", "corona", "despeje")
    NO_ROSCA_DESC = ("pasante", "cajeado", "alojamiento", "corona", "despeje")
    roscas_pieza = []
    profs_internas = []
    for alias, val_str, desc in (filas_param or []):
        al_l = str(alias).lower()
        desc_l = str(desc).lower()
        val_mm = _extraer_mm(val_str)
        if val_mm is None or val_mm <= 0.2:
            continue
        es_solo_aguj_pasante = (
            (any(tok in al_l for tok in NO_ROSCA_TOKENS) or any(tok in desc_l for tok in NO_ROSCA_DESC))
            and "rosc" not in al_l
            and "rosc" not in desc_l
        )
        if al_l.startswith("d_") and not es_solo_aguj_pasante:
            for clave, d_def, d_nom, etiq in TABLA_ROSCAS:
                if clave in al_l or clave in desc_l or (clave == "g18" and "g 1/8" in desc_l):
                    roscas_pieza.append((clave, val_mm if abs(val_mm - d_def) < 1.2 else d_def, d_nom, etiq))
                    break
        elif al_l.startswith(("p_cav", "p_reb", "p_caj", "p_aloj", "p_reten", "p_esc", "a_ran")):
            profs_internas.append(val_mm)

    aristas_vert = []
    aristas_horiz = []
    for idx, e in enumerate(edges):
        bb = e.BoundBox
        curva = getattr(e, "Curve", None)
        if curva and curva.TypeId == "Part::GeomLine" and e.Length >= 1.5:
            dx = abs(bb.XMax - bb.XMin)
            dy = abs(bb.YMax - bb.YMin)
            if dx < 0.05 and dy >= 1.5:
                aristas_vert.append((idx, dy, 0.5 * (bb.XMin + bb.XMax), bb.YMin, bb.YMax))
            elif dy < 0.05 and dx >= 1.5:
                aristas_horiz.append((idx, dx, 0.5 * (bb.YMin + bb.YMax), bb.XMin, bb.XMax))

    cotas_det = []
    rosca_izq = None
    rosca_der = None

    usados = set()
    for i in range(len(aristas_vert)):
        if i in usados:
            continue
        idx_a, len_a, xa, ya0, ya1 = aristas_vert[i]
        for j in range(i + 1, len(aristas_vert)):
            if j in usados:
                continue
            idx_b, len_b, xb, yb0, yb1 = aristas_vert[j]
            if abs(ya0 - yb0) > 0.3 or abs(ya1 - yb1) > 0.3:
                continue
            sep_real = abs(xa - xb) / escala
            len_real = 0.5 * (len_a + len_b) / escala
            for clave, d_mecha, d_nom, etiq in roscas_pieza:
                if abs(sep_real - d_mecha) <= 0.25 and len_real >= 2.0:
                    usados.add(i)
                    usados.add(j)
                    x_mid = 0.5 * (xa + xb)
                    r_nom = 0.5 * d_nom * escala
                    try:
                        det.makeCosmeticLine(
                            App.Vector(x_mid - r_nom, ya0, 0),
                            App.Vector(x_mid - r_nom, ya1, 0),
                            1, 0.20, (0.0, 0.0, 0.0, 1.0),
                        )
                        det.makeCosmeticLine(
                            App.Vector(x_mid + r_nom, ya0, 0),
                            App.Vector(x_mid + r_nom, ya1, 0),
                            1, 0.20, (0.0, 0.0, 0.0, 1.0),
                        )
                        _hacer_linea_eje_cosmetica(
                            det,
                            App.Vector(x_mid, ya0 - 1.2, 0),
                            App.Vector(x_mid, ya1 + 1.2, 0),
                            grosor=0.15,
                            color=(0.25, 0.25, 0.25, 1.0),
                        )
                    except Exception:
                        pass
                    item_r = (idx_a, idx_b, x_mid, ya0, ya1, etiq, len_real)
                    if x_mid >= 0 and rosca_der is None:
                        rosca_der = item_r
                    elif x_mid < 0 and rosca_izq is None:
                        rosca_izq = item_r
                    break
            if i in usados:
                break

    cota_rosca_principal = rosca_der or rosca_izq
    if cota_rosca_principal is not None:
        idx_a, idx_b, x_mid, y0, y1, etiq, len_real = cota_rosca_principal
        dim_r = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Det{ref_letra}_Rosca")
        page.addView(dim_r)
        dim_r.Type = "DistanceY"
        dim_r.MeasureType = "Projected"
        dim_r.FormatSpec = f"{etiq} prof. %.2w"
        dim_r.References2D = [(det, f"Edge{idx_a}")]
        dim_r.X = r_papel + 10.0
        dim_r.Y = max(-r_papel + 4.0, min(r_papel - 4.0, 0.5 * (y0 + y1)))
        cotas_det.append(dim_r)

        for idx_h, dx_h, yh, xh0, xh1 in aristas_horiz:
            if abs(xh0 - min(x_mid, xh0)) < 10.0 and abs((dx_h / escala) - 2.5) <= 1.0 and abs(yh - y1) < 0.3:
                dim_d = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Det{ref_letra}_Diam")
                page.addView(dim_d)
                dim_d.Type = "DistanceX"
                dim_d.MeasureType = "Projected"
                dim_d.FormatSpec = f"⌀%.2w ({etiq})"
                dim_d.References2D = [(det, f"Edge{idx_h}")]
                dim_d.X = 0.5 * (xh0 + xh1)
                dim_d.Y = r_papel + 7.5
                cotas_det.append(dim_d)
                break

    for val_mm in profs_internas:
        cand = [
            (idx, len_p, x, y0, y1)
            for idx, len_p, x, y0, y1 in aristas_vert
            if abs((len_p / escala) - val_mm) <= 0.25
        ]
        if cand:
            cand.sort(key=lambda item: item[2])
            idx_e, _, _, y0, y1 = cand[0]
            dim_c = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo_nombre}_Det{ref_letra}_Cav")
            page.addView(dim_c)
            dim_c.Type = "DistanceY"
            dim_c.MeasureType = "Projected"
            dim_c.FormatSpec = "%.2w"
            dim_c.References2D = [(det, f"Edge{idx_e}")]
            dim_c.X = -(r_papel + 10.0)
            dim_c.Y = max(-r_papel + 4.0, min(r_papel - 4.0, 0.5 * (y0 + y1)))
            cotas_det.append(dim_c)
            break

    return det, cotas_det


# =============================================================================
# PRIMITIVAS DETERMINÍSTICAS IRAM PARA PLANOS SIN AMBIGÜEDAD
# =============================================================================

def obtener_ruta_hatch_iram(estilo="45L"):
    """Devuelve ruta absoluta del patrón SVG normalizado IRAM 4502 (`45L`, `45R`, `simple`)."""
    mapa = {"45L": "hatch45L.svg", "45R": "hatch45R.svg", "simple": "simple.svg"}
    nombre = mapa.get(estilo, "hatch45L.svg")
    ruta = os.path.join(App.getResourceDir(), "Mod", "TechDraw", "Patterns", nombre)
    if os.path.exists(ruta):
        return ruta
    return os.path.join(App.getResourceDir(), "Mod", "TechDraw", "Patterns", "simple.svg")


def proyectar_a_2d_vista(pt3d, centro_ref_3d, direction, x_direction):
    """
    Proyecta un punto 3D al plano 2D matemático (X derecha, Y arriba, sin escalar)
    respecto de `centro_ref_3d`. Coincide con las coordenadas de `DrawViewDetail.AnchorPoint`
    y con `(x_vt, -y_vt) / Scale` de `getVisibleVertexes()`.
    """
    rel = App.Vector(pt3d) - App.Vector(centro_ref_3d)
    uz = App.Vector(direction).normalize()
    ux = App.Vector(x_direction)
    ux = (ux - uz * ux.dot(uz)).normalize()
    uy = uz.cross(ux).normalize()
    return float(rel.dot(ux)), float(rel.dot(uy))


def _distancias_vistas_coincidentes(vista, p_math_2d):
    """Devuelve lista ordenada `(dist_unscaled, idx, pt_vt)` contra `vista.getVisibleVertexes()`."""
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    tx = float(p_math_2d[0]) * escala
    ty = -float(p_math_2d[1]) * escala  # getVisibleVertexes usa Y invertida respecto de View/Page Y+
    cands = []
    for idx, vt in enumerate(vista.getVisibleVertexes()):
        d = math.hypot(vt.x - tx, vt.y - ty) / max(escala, 1e-6)
        cands.append((d, idx, vt))
    cands.sort(key=lambda t: t[0])
    return cands


def buscar_arista_circulo_exacto(
    vista,
    d_objetivo,
    cx_math=0.0,
    cy_math=0.0,
    tol_d=0.15,
    tol_c=0.25,
    min_arc_deg=45.0,
):
    """
    Busca determinísticamente en `vista.getVisibleEdges()` la arista circular/arco que mejor
    coincida con diámetro `d_objetivo` y centro `(cx_math, cy_math)` (coords sin escalar).
    Retorna `(idx, edge, span_deg)` o `None`.
    """
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    r_obj = 0.5 * float(d_objetivo)
    mejor = None
    mejor_score = 1e9
    for idx, e in enumerate(vista.getVisibleEdges()):
        curva = getattr(e, "Curve", None)
        if not curva or curva.TypeId != "Part::GeomCircle":
            continue
        loc = getattr(curva, "Location", None) or getattr(curva, "Center", None)
        if loc is None:
            continue
        r_real = float(curva.Radius) / escala
        d_real = 2.0 * r_real
        if abs(d_real - float(d_objetivo)) > tol_d:
            continue
        cx_real = float(loc.x) / escala
        cy_real = -float(loc.y) / escala
        dc = math.hypot(cx_real - cx_math, cy_real - cy_math)
        if dc > tol_c:
            continue
        span_deg = math.degrees(e.Length / max(float(curva.Radius), 1e-6))
        if span_deg < min_arc_deg:
            continue
        score = abs(d_real - float(d_objetivo)) * 4.0 + dc - min(span_deg, 360.0) * 1e-3
        if score < mejor_score:
            mejor_score = score
            mejor = (idx, e, span_deg)
    return mejor


def _aplicar_tolerancia_y_formato_dim(dim, fmt, tol_sym=None, tol_pos=None, tol_neg=None):
    """Aplica `FormatSpec` y tolerancias nativas de TechDraw cuando corresponde."""
    dim.FormatSpec = fmt
    if tol_sym is not None:
        dim.EqualTolerance = True
        dim.OverTolerance = float(tol_sym)
    elif tol_pos is not None or tol_neg is not None:
        dim.EqualTolerance = False
        dim.OverTolerance = float(tol_pos or 0.0)
        dim.UnderTolerance = float(tol_neg or 0.0)


def acotar_diametro_exacto_iram(
    doc,
    page,
    vista,
    prefijo,
    d_objetivo,
    cx_math=0.0,
    cy_math=0.0,
    ang_deg=45.0,
    r_offset=10.0,
    cantidad=1,
    fmt="%.2w",
    tol_sym=None,
    tol_pos=None,
    tol_neg=None,
    prefijo_txt="",
    sufijo="",
    tol_d=0.16,
    tol_c=0.25,
    solo_si_circulo_completo=False,
    forzar_diametro_cosmetico=False,
    min_arc_deg=None,
):
    """
    Crea una cota de diámetro exacta buscando `d_objetivo` en `(cx_math, cy_math)`.
    Si el círculo es completo (>=300°) o arco >=120°, usa `Type='Diameter'`; si no existe
    arista circular completa (p.ej. contorno seccionado o DBC), usa vértices opuestos
    con `Distance` horizontal o diagonal sobre `(cx_math ± R)` cuando `forzar_diametro_cosmetico=True`.
    """
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    arc_min = float(min_arc_deg) if min_arc_deg is not None else (300.0 if solo_si_circulo_completo else 45.0)
    enc = buscar_arista_circulo_exacto(
        vista, d_objetivo, cx_math=cx_math, cy_math=cy_math, tol_d=tol_d, tol_c=tol_c,
        min_arc_deg=arc_min,
    )
    ang_rad = math.radians(ang_deg)
    r_papel = 0.5 * float(d_objetivo) * escala
    x_pos = cx_math * escala + (r_papel + r_offset) * math.cos(ang_rad)
    y_pos = cy_math * escala + (r_papel + r_offset) * math.sin(ang_rad)

    pref_cant = f"{int(cantidad)}× " if int(cantidad) > 1 else ""
    base_fmt = fmt if "⌀" in fmt or "Ø" in fmt or "M" in fmt or "R" in fmt else f"⌀{fmt}"
    fmt_final = f"{prefijo_txt}{pref_cant}{base_fmt}{sufijo}"

    if enc is not None:
        idx_e, _, _ = enc
        dim = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo}_D_{int(round(d_objetivo * 100))}")
        page.addView(dim)
        dim.Type = "Diameter"
        dim.MeasureType = "Projected"
        _aplicar_tolerancia_y_formato_dim(dim, fmt_final, tol_sym=tol_sym, tol_pos=tol_pos, tol_neg=tol_neg)
        dim.References2D = [(vista, f"Edge{idx_e}")]
        dim.X = x_pos
        dim.Y = y_pos
        _estilizar_cota(dim)
        return dim

    if forzar_diametro_cosmetico:
        r_m = 0.5 * float(d_objetivo)
        p1 = (cx_math + r_m * math.cos(ang_rad), cy_math + r_m * math.sin(ang_rad))
        p2 = (cx_math - r_m * math.cos(ang_rad), cy_math - r_m * math.sin(ang_rad))
        c1 = _distancias_vistas_coincidentes(vista, p1)
        c2 = _distancias_vistas_coincidentes(vista, p2)
        necesita_recomp = False
        if not c1 or c1[0][0] > 0.08:
            vista.makeCosmeticVertex(App.Vector(p1[0], p1[1], 0.0))
            necesita_recomp = True
        if not c2 or c2[0][0] > 0.08:
            vista.makeCosmeticVertex(App.Vector(p2[0], p2[1], 0.0))
            necesita_recomp = True
        if necesita_recomp:
            doc.recompute()
        i1 = _distancias_vistas_coincidentes(vista, p1)[0][1]
        i2 = _distancias_vistas_coincidentes(vista, p2)[0][1]
        dim = doc.addObject("TechDraw::DrawViewDimension", f"{prefijo}_DC_{int(round(d_objetivo * 100))}")
        page.addView(dim)
        dim.Type = "Distance"
        dim.MeasureType = "Projected"
        _aplicar_tolerancia_y_formato_dim(dim, fmt_final, tol_sym=tol_sym, tol_pos=tol_pos, tol_neg=tol_neg)
        dim.References2D = [(vista, f"Vertex{i1}"), (vista, f"Vertex{i2}")]
        dim.X = x_pos
        dim.Y = y_pos
        _estilizar_cota(dim)
        return dim
    return None


def acotar_distancia_coords_iram(
    doc,
    page,
    vista,
    prefijo,
    p1_2d,
    p2_2d,
    tipo="DistanceX",
    offset_x=0.0,
    offset_y=0.0,
    x_abs_vista=None,
    y_abs_vista=None,
    fmt="%.2w",
    prefijo_txt="",
    sufijo_txt="",
    tol_sym=None,
    tol_pos=None,
    tol_neg=None,
    tol_busqueda=0.05,
    permitir_cosmetico=True,
):
    """
    Crea una cota lineal (`DistanceX`, `DistanceY` o `Distance`) entre dos puntos exactos
    `p1_2d`, `p2_2d` en coordenadas matemáticas 2D (sin escalar) de `vista`.
    """
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)

    def _resolver_idx(pt):
        cands = _distancias_vistas_coincidentes(vista, pt)
        if cands and cands[0][0] <= tol_busqueda:
            return cands[0][1], False
        if not permitir_cosmetico:
            return (cands[0][1] if cands else None), False
        vista.makeCosmeticVertex(App.Vector(float(pt[0]), float(pt[1]), 0.0))
        return None, True

    i1, add1 = _resolver_idx(p1_2d)
    i2, add2 = _resolver_idx(p2_2d)
    if add1 or add2:
        doc.recompute()
        if i1 is None:
            i1 = _distancias_vistas_coincidentes(vista, p1_2d)[0][1]
        if i2 is None:
            i2 = _distancias_vistas_coincidentes(vista, p2_2d)[0][1]
    if i1 is None or i2 is None or i1 == i2:
        return None

    dim = doc.addObject("TechDraw::DrawViewDimension", prefijo)
    page.addView(dim)
    dim.Type = tipo
    dim.MeasureType = "Projected"
    fmt_final = f"{prefijo_txt}{fmt}{sufijo_txt}"
    _aplicar_tolerancia_y_formato_dim(dim, fmt_final, tol_sym=tol_sym, tol_pos=tol_pos, tol_neg=tol_neg)
    dim.References2D = [(vista, f"Vertex{i1}"), (vista, f"Vertex{i2}")]
    xm = 0.5 * (float(p1_2d[0]) + float(p2_2d[0])) * escala
    ym = 0.5 * (float(p1_2d[1]) + float(p2_2d[1])) * escala
    dim.X = x_abs_vista if x_abs_vista is not None else (xm + offset_x)
    dim.Y = y_abs_vista if y_abs_vista is not None else (ym + offset_y)
    _estilizar_cota(dim)
    return dim


def acotar_angulo_centrado_iram(
    doc,
    page,
    vista,
    prefijo,
    ang1_deg,
    ang2_deg,
    r_rayo_in=2.0,
    r_rayo_out=12.0,
    r_cota_papel=18.0,
    cx_math=0.0,
    cy_math=0.0,
    fmt="%.0w",
):
    """
    Traza dos rayos finos de centro en `ang1_deg` y `ang2_deg` respecto de `(cx_math, cy_math)`
    y acota el ángulo entre ambos mediante `DrawViewDimension(Type='Angle')`.
    """
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    a1 = math.radians(float(ang1_deg))
    a2 = math.radians(float(ang2_deg))
    cx = float(cx_math)
    cy = float(cy_math)
    n_prev = len(vista.getVisibleEdges())
    for ang_r in (a1, a2):
        p1 = App.Vector(cx + float(r_rayo_in) * math.cos(ang_r), cy + float(r_rayo_in) * math.sin(ang_r), 0.0)
        p2 = App.Vector(cx + float(r_rayo_out) * math.cos(ang_r), cy + float(r_rayo_out) * math.sin(ang_r), 0.0)
        _hacer_linea_eje_cosmetica(vista, p1, p2, grosor=0.14)
    doc.recompute()
    ee = vista.getVisibleEdges()
    if len(ee) < n_prev + 2:
        return None
    dim = doc.addObject("TechDraw::DrawViewDimension", prefijo)
    page.addView(dim)
    dim.Type = "Angle"
    dim.MeasureType = "Projected"
    dim.FormatSpec = fmt
    dim.References2D = [(vista, f"Edge{len(ee) - 2}"), (vista, f"Edge{len(ee) - 1}")]
    diff = ((float(ang2_deg) - float(ang1_deg) + 180.0) % 360.0) - 180.0
    ang_mid = math.radians(float(ang1_deg) + 0.5 * diff)
    dim.X = cx * escala + float(r_cota_papel) * math.cos(ang_mid)
    dim.Y = cy * escala + float(r_cota_papel) * math.sin(ang_mid)
    _estilizar_cota(dim)
    return dim


def agregar_circulo_centros_iram(
    vista,
    d_dbc,
    n_aguj=4,
    ang_ini_deg=0.0,
    cx_math=0.0,
    cy_math=0.0,
    incluir_cruz=True,
    radio_ext_cruz=3.5,
):
    """
    Traza en `vista` el círculo de paso (DBC) en línea trazo y punto fina (`style=4`,
    IRAM 4502) junto con marcas radiales de centros sobre cada agujero.
    """
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    sc = max(escala, 1e-6)
    r_p = 0.5 * float(d_dbc)
    cx_p = float(cx_math)
    cy_p = float(cy_math)
    try:
        vista.makeCosmeticCircle(App.Vector(cx_p, cy_p, 0.0), r_p, 4, 0.16, (0.0, 0.0, 0.0, 1.0))
    except Exception:
        pass
    if n_aguj and n_aguj > 0:
        tick_m = 2.4 / sc
        r_in = max(0.3 / sc, r_p - tick_m)
        r_out = r_p + tick_m
        for k in range(int(n_aguj)):
            ang = math.radians(float(ang_ini_deg) + k * (360.0 / float(n_aguj)))
            p1 = App.Vector(cx_p + r_in * math.cos(ang), cy_p + r_in * math.sin(ang), 0.0)
            p2 = App.Vector(cx_p + r_out * math.cos(ang), cy_p + r_out * math.sin(ang), 0.0)
            _hacer_linea_eje_cosmetica(vista, p1, p2, grosor=0.14)
    if incluir_cruz:
        r_ext = r_p + float(radio_ext_cruz) / sc
        _hacer_linea_eje_cosmetica(
            vista, App.Vector(cx_p - r_ext, cy_p, 0.0), App.Vector(cx_p + r_ext, cy_p, 0.0), grosor=0.16
        )
        _hacer_linea_eje_cosmetica(
            vista, App.Vector(cx_p, cy_p - r_ext, 0.0), App.Vector(cx_p, cy_p + r_ext, 0.0), grosor=0.16
        )


def agregar_llamada_lider_iram(
    doc,
    page,
    vista,
    prefijo,
    pt_ancla_2d,
    offset_papel,
    texto,
    simbolo="None",
    flecha="Filled arrow",
    text_size=2.5,
):
    """
    Coloca una llamada normativa con flecha (`BubbleShape='None'` o `'Rectangle'` para GD&T)
    anclada al punto 2D sin escalar `pt_ancla_2d` dentro de `vista`.
    """
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    bal = doc.addObject("TechDraw::DrawViewBalloon", prefijo)
    page.addView(bal)
    bal.SourceView = vista
    bal.OriginX = float(pt_ancla_2d[0])
    bal.OriginY = float(pt_ancla_2d[1])
    bal.X = float(pt_ancla_2d[0]) + (float(offset_papel[0]) / max(escala, 1e-6))
    bal.Y = float(pt_ancla_2d[1]) + (float(offset_papel[1]) / max(escala, 1e-6))
    bal.Text = texto
    bal.BubbleShape = simbolo
    bal.EndType = flecha
    bal.KinkLength = 3.0
    bal.ShapeScale = 0.85
    vo = getattr(bal, "ViewObject", None)
    if vo:
        try:
            vo.Fontsize = text_size
            vo.LineWidth = 0.22
        except Exception:
            pass
    return bal


def crear_rosca_cosmetica_vista_iram(
    vista,
    x_ini,
    x_fin,
    y_centro,
    d_mayor,
    d_menor,
    tipo="externa",
    draw_axis=True,
):
    """
    Traza convención IRAM 4520 de rosca sobre vista longitudinal horizontal:
    línea fina continua (`style=1`, 0.18 mm) en fondo (externa) o cresta nominal (interna)
    y límite de fin de rosca.
    """
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    sc = max(escala, 1e-6)
    x0 = float(x_ini)
    x1 = float(x_fin)
    yc = float(y_centro)
    r_line = 0.5 * (float(d_menor) if tipo == "externa" else float(d_mayor))
    try:
        vista.makeCosmeticLine(App.Vector(x0, yc + r_line, 0.0), App.Vector(x1, yc + r_line, 0.0), 1, 0.18, (0.0, 0.0, 0.0, 1.0))
        vista.makeCosmeticLine(App.Vector(x0, yc - r_line, 0.0), App.Vector(x1, yc - r_line, 0.0), 1, 0.18, (0.0, 0.0, 0.0, 1.0))
        r_lim = 0.5 * float(d_mayor)
        vista.makeCosmeticLine(App.Vector(x1, yc - r_lim, 0.0), App.Vector(x1, yc + r_lim, 0.0), 1, 0.30, (0.0, 0.0, 0.0, 1.0))
    except Exception:
        pass
    if draw_axis:
        ext = 3.0 / sc
        _hacer_linea_eje_cosmetica(
            vista, App.Vector(min(x0, x1) - ext, yc, 0.0), App.Vector(max(x0, x1) + ext, yc, 0.0), grosor=0.18
        )


def crear_circulo_rosca_34_iram(vista, d_exterior_o_fondo, cx_math=0.0, cy_math=0.0):
    """
    Dibuja el arco fino abierto de 3/4 de circunferencia (270°) según IRAM 4520
    en vistas frontales de piezas roscadas (`8-3D`, `8b-3D`).
    """
    r_p = 0.5 * float(d_exterior_o_fondo)
    try:
        vista.makeCosmeticCircleArc(
            App.Vector(float(cx_math), float(cy_math), 0.0),
            r_p,
            90.0,
            360.0,
            1,
            0.18,
            (0.0, 0.0, 0.0, 1.0),
        )
    except Exception:
        pass


def crear_solido_corte_parcial_z(shape_pieza, z_a, z_b, eje_xy_ancho=50.0, amp_wavy=0.45):
    """
    Recorta un sub-sólido en el rango `Z=[z_a, z_b]` mediante una superficie ondulada
    en los límites interiores para representar un corte parcial (`corte parcial` IRAM 4502)
    exclusivamente en zonas con agujeros ciegos/transversales sobre ejes macizos.
    """
    bb = shape_pieza.BoundBox
    n_seg = 12
    z_ini = max(bb.ZMin - 0.5, float(z_a))
    z_fin = min(bb.ZMax + 0.5, float(z_b))
    corte_izq = z_a > (bb.ZMin + 0.2)
    corte_der = z_b < (bb.ZMax - 0.2)

    pts_xz = []
    # Pared inferior / derecha en X=[-W, +W]
    for k in range(n_seg + 1):
        xk = -eje_xy_ancho + (2.0 * eje_xy_ancho) * (k / float(n_seg))
        dz = amp_wavy * math.sin(k * math.pi * 0.65) if corte_der else 0.0
        pts_xz.append(App.Vector(xk, -eje_xy_ancho, z_fin + dz))
    for k in range(n_seg, -1, -1):
        xk = -eje_xy_ancho + (2.0 * eje_xy_ancho) * (k / float(n_seg))
        dz = amp_wavy * math.sin(k * math.pi * 0.65) if corte_izq else 0.0
        pts_xz.append(App.Vector(xk, -eje_xy_ancho, z_ini + dz))
    pts_xz.append(pts_xz[0])
    try:
        w = Part.makePolygon(pts_xz)
        f = Part.Face(w)
        prisma = f.extrude(App.Vector(0.0, 2.0 * eje_xy_ancho, 0.0))
        return shape_pieza.common(prisma)
    except Exception:
        caja = Part.makeBox(2.0 * eje_xy_ancho, 2.0 * eje_xy_ancho, z_fin - z_ini, App.Vector(-eje_xy_ancho, -eje_xy_ancho, z_ini))
        return shape_pieza.common(caja)


def agregar_marcas_plano_corte_iram(
    vista,
    puntos_2d_papel_sin_esc,
    letra="A",
    vec_flecha_2d=(1.0, 0.0),
    largo_brazo=5.5,
):
    """
    Dibuja traza escalonada o recta de plano de corte IRAM 4502 (`style=4` trazo/punto
    con extremos gruesos, flechas hacia `vec_flecha_2d` y marca en `vista`).
    `puntos_2d_papel_sin_esc` es lista de puntos `(x, y)` en coords modelo de `vista`.
    """
    escala = float(getattr(vista, "Scale", 1.0) or 1.0)
    sc = max(escala, 1e-6)
    pts = [App.Vector(float(px), float(py), 0.0) for px, py in puntos_2d_papel_sin_esc]
    if len(pts) < 2:
        return
    for i in range(len(pts) - 1):
        try:
            vista.makeCosmeticLine(pts[i], pts[i + 1], 4, 0.22, (0.0, 0.0, 0.0, 1.0))
        except Exception:
            pass
    # Extremos gruesos (trazo terminal 3.8 mm en papel, grosor 0.55 mm) + flechas en dirección de observación
    fn = math.hypot(vec_flecha_2d[0], vec_flecha_2d[1]) or 1.0
    fx, fy = vec_flecha_2d[0] / fn, vec_flecha_2d[1] / fn
    nx, ny = -fy, fx
    l_ext = 3.8 / sc
    l_punta = 2.4 / sc
    l_brazo = float(largo_brazo) / sc
    l_wing = 2.4 / sc
    w_wing = 0.9 / sc
    for idx_end, p_end in ((0, pts[0]), (-1, pts[-1])):
        p_otro = pts[1] if idx_end == 0 else pts[-2]
        vx = p_end.x - p_otro.x
        vy = p_end.y - p_otro.y
        vn = math.hypot(vx, vy) or 1.0
        ux, uy = vx / vn, vy / vn
        try:
            vista.makeCosmeticLine(
                p_end, App.Vector(p_end.x + ux * l_ext, p_end.y + uy * l_ext, 0.0),
                1, 0.55, (0.0, 0.0, 0.0, 1.0)
            )
            p_punta = App.Vector(p_end.x + ux * l_punta, p_end.y + uy * l_punta, 0.0)
            p_cola = App.Vector(p_punta.x - fx * l_brazo, p_punta.y - fy * l_brazo, 0.0)
            vista.makeCosmeticLine(p_cola, p_punta, 1, 0.30, (0.0, 0.0, 0.0, 1.0))
            vista.makeCosmeticLine(
                p_punta, App.Vector(p_punta.x - fx * l_wing + nx * w_wing, p_punta.y - fy * l_wing + ny * w_wing, 0.0),
                1, 0.30, (0.0, 0.0, 0.0, 1.0)
            )
            vista.makeCosmeticLine(
                p_punta, App.Vector(p_punta.x - fx * l_wing - nx * w_wing, p_punta.y - fy * l_wing - ny * w_wing, 0.0),
                1, 0.30, (0.0, 0.0, 0.0, 1.0)
            )
        except Exception:
            pass


def crear_vista_detalle_especifico_iram(
    doc,
    page,
    vista_base,
    prefijo_nombre,
    anchor_point,
    x_detalle,
    y_detalle,
    radio_corte=8.0,
    escala_detalle=3.0,
    ref_letra="B",
    cotas_relativas=None,
    rosca_cosmetica=None,
    notas_lider=None,
):
    """
    Crea `TechDraw::DrawViewDetail` limpio y determinístico (sin inclinaciones accidentales,
    con círculo resaltado + letra en `vista_base`, borde normalizado y cotas/roscas IRAM 4520).
    """
    det = doc.addObject("TechDraw::DrawViewDetail", f"{prefijo_nombre}_Detalle_{ref_letra}")
    page.addView(det)
    det.BaseView = vista_base
    det.AnchorPoint = App.Vector(anchor_point)
    det.Radius = float(radio_corte)
    det.ScaleType = "Custom"
    det.Scale = float(escala_detalle)
    det.Reference = ref_letra
    det.X = float(x_detalle)
    det.Y = float(y_detalle)
    det.Caption = ""
    det.ShowHighlight = True
    det.ShowMatting = True
    estilizar_vista_iram(det, mostrar_ocultas=False, mostrar_centros=False)

    r_papel = float(radio_corte) * float(escala_detalle)
    try:
        ann = doc.addObject("TechDraw::DrawViewAnnotation", f"{prefijo_nombre}_Txt_Det_{ref_letra}")
        page.addView(ann)
        esc_lbl = f"{float(escala_detalle):g}".replace(".", ",")
        ann.Text = [f"Esc. {esc_lbl}:1"]
        ann.TextSize = 2.8
        ann.X = float(x_detalle)
        ann.Y = max(14.0, float(y_detalle) - r_papel - 9.5)
    except Exception:
        pass

    doc.recompute()
    _esperar_hlr_vista(doc, det, timeout_s=20.0)

    # Trazado cosmético opcional de rosca IRAM 4520 (coords locales respecto de anchor_point)
    if rosca_cosmetica:
        for rc in rosca_cosmetica:
            crear_rosca_cosmetica_vista_iram(
                det,
                rc["x_ini"],
                rc["x_fin"],
                rc.get("y_c", 0.0),
                rc["d_mayor"],
                rc["d_menor"],
                tipo=rc.get("tipo", "externa"),
                draw_axis=rc.get("axis", True),
            )

    cotas = []
    for idx_c, sc in enumerate(cotas_relativas or []):
        dim = acotar_distancia_coords_iram(
            doc,
            page,
            det,
            f"{prefijo_nombre}_D{ref_letra}_{idx_c}",
            sc["p1"],
            sc["p2"],
            tipo=sc.get("tipo", "DistanceX"),
            offset_x=sc.get("ox", 0.0),
            offset_y=sc.get("oy", 0.0),
            x_abs_vista=sc.get("ax"),
            y_abs_vista=sc.get("ay"),
            fmt=sc.get("fmt", "%.2w"),
            prefijo_txt=sc.get("pref", ""),
            sufijo_txt=sc.get("suf", ""),
            tol_sym=sc.get("tol_sym"),
            tol_pos=sc.get("tol_pos"),
            tol_neg=sc.get("tol_neg"),
            tol_busqueda=sc.get("tol_busqueda", 0.05),
            permitir_cosmetico=sc.get("cosmetico", True),
        )
        if dim:
            cotas.append(dim)

    for idx_l, nl in enumerate(notas_lider or []):
        agregar_llamada_lider_iram(
            doc,
            page,
            det,
            f"{prefijo_nombre}_L{ref_letra}_{idx_l}",
            nl["pt"],
            nl["off"],
            nl["texto"],
            simbolo=nl.get("simbolo", "None"),
            text_size=nl.get("size", 2.4),
        )

    return det, cotas


def generar_svg_resumen_tecnico_iram(
    filas_resumen,
    notas_taller,
    ancho_mm=98.0,
    titulo="ESPECIFICACIONES TÉCNICAS Y TOLERANCIAS",
):
    """
    Genera el símbolo SVG de resumen de fabricación sin nombres de variables de código:
    dos columnas limpias ('CARACTERÍSTICA' | 'MEDIDA / ESPEC.') con coma decimal IRAM y
    bloque inferior de notas técnicas ajustado automáticamente al ancho del panel.
    """
    alto_fila = 4.6
    alto_cab = 11.2
    lineas_notas = []
    for n in (notas_taller or []):
        envueltas = textwrap.wrap(str(n), width=56)
        for j, seg in enumerate(envueltas):
            lineas_notas.append(("• " + seg) if j == 0 else ("  " + seg))

    n_filas = max(1, len(filas_resumen or []))
    alto_tabla = alto_cab + n_filas * alto_fila
    alto_notas = 7.0 + max(1, len(lineas_notas)) * 3.8 + 2.5
    H = alto_tabla + alto_notas + 3.0
    W = float(ancho_mm)
    x_col = W * 0.61

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{alto_tabla - 0.5:.1f}" fill="#ffffff" stroke="#000000" stroke-width="0.45"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{alto_cab:.1f}" fill="#1d3557" stroke="#000000" stroke-width="0.45"/>',
        f'<text x="{W / 2:.1f}" y="4.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.65" font-weight="bold" fill="#ffffff" text-anchor="middle">{_escapar_xml(titulo)}</text>',
        f'<rect x="0.5" y="6.6" width="{W - 1.0:.1f}" height="4.6" fill="#dce6f1" stroke="#000000" stroke-width="0.35"/>',
        f'<line x1="{x_col:.1f}" y1="6.6" x2="{x_col:.1f}" y2="{alto_tabla:.1f}" stroke="#000000" stroke-width="0.35"/>',
        f'<text x="3.0" y="9.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.25" font-weight="bold">CARACTERÍSTICA FUNCIONAL</text>',
        f'<text x="{W - 2.5:.1f}" y="9.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.25" font-weight="bold" text-anchor="end">MEDIDA / ESPECIF.</text>',
    ]

    for i, item in enumerate(filas_resumen or [("Sin datos", "-")]):
        concepto, valor = item[0], item[1]
        val_fmt = _formatear_decimales_coma(valor)
        yt = alto_cab + i * alto_fila
        y_tx = yt + 3.25
        bg = "#ffffff" if i % 2 == 0 else "#f7f9fc"
        svg.append(f'<rect x="0.8" y="{yt:.2f}" width="{W - 1.6:.1f}" height="{alto_fila:.2f}" fill="{bg}" stroke="none"/>')
        svg.append(f'<line x1="0.5" y1="{yt:.2f}" x2="{W - 0.5:.1f}" y2="{yt:.2f}" stroke="#cbd5e1" stroke-width="0.25"/>')
        svg.append(f'<line x1="{x_col:.1f}" y1="{yt:.2f}" x2="{x_col:.1f}" y2="{yt + alto_fila:.2f}" stroke="#cbd5e1" stroke-width="0.25"/>')
        svg.append(
            f'<text x="2.5" y="{y_tx:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">{_escapar_xml(_truncar_texto(_formatear_decimales_coma(concepto), x_col - 4.0, 2.2))}</text>'
        )
        svg.append(
            f'<text x="{W - 2.3:.1f}" y="{y_tx:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.25" font-weight="bold" text-anchor="end">{_escapar_xml(_truncar_texto(val_fmt, W - x_col - 3.5, 2.25))}</text>'
        )

    yn0 = alto_tabla + 2.5
    svg.append(f'<rect x="0.5" y="{yn0:.2f}" width="{W - 1.0:.1f}" height="{alto_notas:.2f}" fill="#fffdf7" stroke="#000000" stroke-width="0.45"/>')
    svg.append(f'<rect x="0.5" y="{yn0:.2f}" width="{W - 1.0:.1f}" height="5.2" fill="#eef3f8" stroke="#000000" stroke-width="0.35"/>')
    svg.append(f'<text x="2.8" y="{yn0 + 3.6:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold" fill="#1d3557">NOTAS DE TALLER Y TOLERANCIAS</text>')
    for j, ln in enumerate(lineas_notas):
        yl = yn0 + 8.6 + j * 3.8
        svg.append(
            f'<text x="2.6" y="{yl:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1">{_escapar_xml(_truncar_texto(ln, W - 4.8, 2.1))}</text>'
        )
    svg.append("</svg>")
    return "\n".join(svg)


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
    Envuelve descripciones largas en 2 líneas para evitar recortes ("..").
    """
    W = ancho_mm
    x_div1 = round(min(34.0, max(25.0, W * 0.24)), 1)
    x_div2 = round(x_div1 + max(23.5, W * 0.18), 1)
    x_val_end = x_div2 - 1.6
    x_desc = x_div2 + 1.8
    w_desc = max(24.0, W - x_desc - 2.0)

    max_chars_desc = max(18, int(w_desc / (2.10 * 0.56)))
    filas_prep = []
    y_cursor = 7.0
    for simbolo, valor_unid, descripcion in (filas_parametros or [])[:22]:
        simb_txt = _truncar_texto(simbolo, x_div1 - 2.5, 2.15)
        val_raw = str(valor_unid).replace(".", ",")
        val_lines = textwrap.wrap(val_raw, width=max(10, int((x_div2 - x_div1 - 2.5) / (2.2 * 0.56)))) or [val_raw]
        desc_lines = textwrap.wrap(str(descripcion or "").strip(), width=max_chars_desc) or ["-"]
        if len(desc_lines) > 2:
            desc_lines = [desc_lines[0], _truncar_texto(" ".join(desc_lines[1:]), w_desc, 2.05)]
        n_sub = max(len(desc_lines[:2]), min(2, len(val_lines)))
        dy = 4.2 if n_sub <= 1 else 6.8
        filas_prep.append((y_cursor, dy, simb_txt, val_lines[:2], desc_lines[:2]))
        y_cursor += dy

    alto_tabla = max(12.0, y_cursor + 0.6)

    max_chars_nota = max(32, int((W - 6.0) / (2.15 * 0.56)))
    lineas_notas = []
    for nota in notas_taller or []:
        envueltas = textwrap.wrap(str(nota).strip(), width=max_chars_nota - 2) or [""]
        for k, seg in enumerate(envueltas):
            prefijo = "• " if k == 0 else "  "
            lineas_notas.append(prefijo + seg)

    alto_notas = (6.0 + len(lineas_notas) * 3.6) if lineas_notas else 0.0
    H = alto_tabla + alto_notas + 2.0

    lineas = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{alto_tabla - 0.5:.1f}" fill="#ffffff" stroke="#000000" stroke-width="0.45"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="6.5" fill="#eaeff5" stroke="#000000" stroke-width="0.45"/>',
        f'<text x="{W / 2:.1f}" y="4.8" font-family="Liberation Sans, Arial, sans-serif" font-size="{2.9 if W >= 130 else 2.4:.1f}" font-weight="bold" text-anchor="middle">CUADRO DE COTAS FUNCIONALES, ROSCAS Y TOLERANCIAS (IRAM 4513)</text>',
        f'<line x1="{x_div1:.1f}" y1="7.0" x2="{x_div1:.1f}" y2="{alto_tabla:.1f}" stroke="#000000" stroke-width="0.25"/>',
        f'<line x1="{x_div2:.1f}" y1="7.0" x2="{x_div2:.1f}" y2="{alto_tabla:.1f}" stroke="#000000" stroke-width="0.25"/>',
    ]

    for idx, (y_top, dy, simb_txt, val_lines, desc_lines) in enumerate(filas_prep):
        y_txt = y_top + 2.95
        if idx > 0:
            lineas.append(
                f'<line x1="0.5" y1="{y_top:.2f}" x2="{W - 0.5:.1f}" y2="{y_top:.2f}" stroke="#cccccc" stroke-width="0.20"/>'
            )
        lineas.append(
            f'<text x="1.8" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.15" font-weight="bold">{_escapar_xml(simb_txt)}</text>'
        )
        for kv, vl in enumerate(val_lines):
            lineas.append(
                f'<text x="{x_val_end:.1f}" y="{y_txt + kv * 2.8:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.20" text-anchor="end">{_escapar_xml(vl)}</text>'
            )
        for kd, dl in enumerate(desc_lines):
            lineas.append(
                f'<text x="{x_desc:.1f}" y="{y_txt + kd * 2.8:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.10">{_escapar_xml(dl)}</text>'
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
    coincidiendo exactamente con la numeración 1..N de los globos de la vista explotada,
    e incluyendo fila destacada de Peso Total del Ensamblaje.
    """
    alto_fila = 4.6
    n_items = len(items_bom)
    alto_cabecera = 12.0
    alto_fila_total = 6.4
    alto_tabla = alto_cabecera + n_items * alto_fila + alto_fila_total
    alto_bul = 9.0 + len(resumen_buloneria) * 4.2 if resumen_buloneria else 0.0
    H = alto_tabla + alto_bul + 3.5
    W = ancho_mm

    k = W / 382.0
    cols_x = [13.0 * k, 27.0 * k, 96.0 * k, 134.0 * k, 198.0 * k, W - 40.0]
    x_masa_der = W - 3.5

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
        (0.5 * cols_x[0], "ÍTEM"),
        (0.5 * (cols_x[0] + cols_x[1]), "CANT."),
        (0.5 * (cols_x[1] + cols_x[2]), "DENOMINACIÓN DE LA PIEZA"),
        (0.5 * (cols_x[2] + cols_x[3]), "PLANO N°"),
        (0.5 * (cols_x[3] + cols_x[4]), "MATERIAL ESPECIFICADO"),
        (0.5 * (cols_x[4] + cols_x[5]), "NORMA / CÓDIGO COMERCIAL / OBSERVACIONES"),
        (0.5 * (cols_x[5] + W - 1.0), "MASA UN. (g)"),
    ]
    for cx, titulo in encabezados:
        svg.append(
            f'<text x="{cx:.1f}" y="10.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.55" font-weight="bold" text-anchor="middle">{_escapar_xml(titulo)}</text>'
        )

    cant_total_piezas = 0
    masa_total_piezas_g = 0.0

    for idx, it in enumerate(items_bom):
        y_top = alto_cabecera + idx * alto_fila
        y_txt = y_top + 3.25
        cant_total_piezas += it["cantidad"]
        masa_sub = it["masa_g"] * it["cantidad"]
        masa_total_piezas_g += masa_sub

        es_comercial = it.get("es_comercial", False)
        es_buloneria = int(it.get("item", 0)) >= 32
        if es_buloneria:
            bg = "#fffaf0"
        elif es_comercial:
            bg = "#f3f8fe"
        else:
            bg = "#ffffff" if idx % 2 == 0 else "#f9f9f9"
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
            f'<text x="{0.5 * cols_x[0]:.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.65" font-weight="bold" text-anchor="middle">{it["item"]}</text>'
        )
        svg.append(
            f'<text x="{0.5 * (cols_x[0] + cols_x[1]):.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.65" font-weight="bold" text-anchor="middle">{it["cantidad"]}</text>'
        )
        svg.append(
            f'<text x="{cols_x[1] + 2.0:.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">{_escapar_xml(_truncar_texto(it["denominacion"], cols_x[2] - cols_x[1] - 4.0, 2.4))}</text>'
        )
        svg.append(
            f'<text x="{0.5 * (cols_x[2] + cols_x[3]):.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" text-anchor="middle">{_escapar_xml(_truncar_texto(it["plano_ref"], cols_x[3] - cols_x[2] - 3.0, 2.35))}</text>'
        )
        svg.append(
            f'<text x="{cols_x[3] + 2.0:.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">{_escapar_xml(_truncar_texto(it["material"], cols_x[4] - cols_x[3] - 4.0, 2.35))}</text>'
        )
        svg.append(
            f'<text x="{cols_x[4] + 2.0:.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">{_escapar_xml(_truncar_texto(it["detalles"], cols_x[5] - cols_x[4] - 4.0, 2.3))}</text>'
        )
        masa_str = f"{it['masa_g']:.1f}".replace(".", ",")
        svg.append(
            f'<text x="{x_masa_der:.1f}" y="{y_txt:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.5" text-anchor="end">{masa_str}</text>'
        )

    y_tot = alto_cabecera + n_items * alto_fila
    masa_total_kg = f"{masa_total_piezas_g / 1000.0:.2f}".replace(".", ",")
    svg.append(
        f'<rect x="0.8" y="{y_tot:.2f}" width="{W - 1.6:.1f}" height="{alto_fila_total:.2f}" fill="#e3ecf6" stroke="none"/>'
    )
    svg.append(
        f'<line x1="0.5" y1="{y_tot:.2f}" x2="{W - 0.5:.1f}" y2="{y_tot:.2f}" stroke="#000000" stroke-width="0.55"/>'
    )
    svg.append(
        f'<line x1="{cols_x[0]:.1f}" y1="{y_tot:.2f}" x2="{cols_x[0]:.1f}" y2="{y_tot + alto_fila_total:.2f}" stroke="#000000" stroke-width="0.35"/>'
    )
    svg.append(
        f'<line x1="{cols_x[1]:.1f}" y1="{y_tot:.2f}" x2="{cols_x[1]:.1f}" y2="{y_tot + alto_fila_total:.2f}" stroke="#000000" stroke-width="0.35"/>'
    )
    svg.append(
        f'<line x1="{cols_x[5]:.1f}" y1="{y_tot:.2f}" x2="{cols_x[5]:.1f}" y2="{y_tot + alto_fila_total:.2f}" stroke="#000000" stroke-width="0.35"/>'
    )
    svg.append(
        f'<text x="{0.5 * (cols_x[0] + cols_x[1]):.1f}" y="{y_tot + 4.6:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="3.0" font-weight="bold" text-anchor="middle">{cant_total_piezas}</text>'
    )
    svg.append(
        f'<text x="{cols_x[1] + 4.0:.1f}" y="{y_tot + 4.6:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="3.1" font-weight="bold">PESO TOTAL ESTIMADO DEL CONJUNTO MECÁNICO (BOMBA ARMADA COMPLETA)</text>'
    )
    svg.append(
        f'<text x="{x_masa_der:.1f}" y="{y_tot + 4.6:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.9" font-weight="bold" text-anchor="end">{masa_total_kg} kg ({masa_total_piezas_g:.0f} g)</text>'
    )

    if resumen_buloneria:
        yb0 = alto_tabla + 3.0
        svg.append(
            f'<rect x="0.5" y="{yb0:.2f}" width="265.0" height="{alto_bul - 1.5:.2f}" fill="#fffdf7" stroke="#000000" stroke-width="0.45"/>'
        )
        svg.append(
            f'<text x="3.0" y="{yb0 + 4.5:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.7" font-weight="bold">NOTAS TÉCNICAS DE BULONERÍA ESTÁNDAR (ÍTEMS #32..#38) Y APRIETE IRAM/DIN/ISO:</text>'
        )
        for j, b_txt in enumerate(resumen_buloneria):
            yb = yb0 + 9.0 + j * 4.4
            svg.append(
                f'<text x="4.5" y="{yb:.2f}" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">• {_escapar_xml(b_txt)}</text>'
            )

    svg.append("</svg>")
    return "\n".join(svg)
