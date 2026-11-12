#!/usr/bin/env python3
"""
Generador del Plano N° 16b (Tapa Interior Intermedia) bajo normas IRAM:
- IRAM 4501: Método ISO-E (Primer Diedro) con SECCIÓN A-A ARRIBA y vista circular DEBAJO.
- IRAM 4502: Ejes de simetría (tipo G) y círculos primitivos de centros (PCD).
- IRAM 4509: Rayado a 45° gobernado por PatHatch con ruta FCPat.pat válida en Linux.
- IRAM 4513: Acotación directa en vistas sin superposiciones; coma decimal.
- IRAM 4515: Tolerancia geométrica de paralelismo [ // | 0,05 | A ] con símbolo Datum A exterior.
- IRAM 4517: Acabado superficial Ra 3,2 general y Ra 0,8 en asientos de sellos visibles.
- IRAM 4520: Representación normalizada de roscas M3, G 1/8 y M12x1.
- IRAM 4508: Rótulo reglamentario con textos sin solapamiento ni recortes.
"""
import os
import sys
import glob
import math
import re
import FreeCAD as App
import Part

AQUI = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", "..")) if "proyectos" in AQUI else os.path.abspath(os.getcwd())
DIR_PLANOS = os.path.join(RAIZ, "proyectos", "bomba_flujo_cardiaco", "planos")
DIR_PROYECTO = os.path.join(RAIZ, "proyectos", "bomba_flujo_cardiaco")
DIR_PIEZAS = os.path.join(DIR_PROYECTO, "piezas")
DIR_HOJAS = os.path.join(DIR_PLANOS, "hojas")
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))

from planos_iram import (
    FORMATOS_IRAM,
    asegurar_plantillas_iram,
    estilizar_vista_iram,
)


def obtener_ruta_fcpat():
    """Localiza FCPat.pat o FCPAT.pat en Linux respetando mayúsculas/minúsculas del sistema de archivos."""
    candidatos = [
        os.path.join(App.getResourceDir(), "Mod", "TechDraw", "PAT", "FCPat.pat"),
        os.path.join(App.getResourceDir(), "Mod", "TechDraw", "PAT", "FCPAT.pat"),
        os.path.join(App.getResourceDir(), "Mod", "TechDraw", "Patterns", "FCPat.pat"),
        "/snap/freecad/current/usr/share/Mod/TechDraw/PAT/FCPat.pat",
        "/snap/freecad/current/usr/share/Mod/TechDraw/PAT/FCPAT.pat",
        "/snap/freecad/current/usr/share/Mod/TechDraw/Patterns/FCPat.pat",
        "/snap/freecad/2926/usr/share/Mod/TechDraw/PAT/FCPat.pat",
        "/snap/freecad/2926/usr/share/Mod/TechDraw/PAT/FCPAT.pat",
        "/snap/freecad/2926/usr/share/Mod/TechDraw/Patterns/FCPat.pat",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    encontrados = glob.glob("/snap/freecad/*/**/FCPat.pat", recursive=True)
    if not encontrados:
        encontrados = glob.glob("/snap/freecad/*/**/FCPAT.pat", recursive=True)
    return encontrados[0] if encontrados else candidatos[0]


def parchar_svg_plantilla_a3(ruta_svg):
    """Corrige en disco la plantilla A3 tras asegurar_plantillas_iram() para evitar textos cortados."""
    if not os.path.exists(ruta_svg):
        return
    with open(ruta_svg, "r", encoding="utf-8") as f:
        contenido = f.read()
    # Asegurar que el nombre del autor no se corte por ancho ni tamaño de fuente
    contenido = contenido.replace("Dib F. Gutiérre", "Dib.: F. Gutiérrez")
    contenido = contenido.replace("Dib: F. Gutiérre", "Dib.: F. Gutiérrez")
    # Asegurar coordenada y tamaño de autor
    contenido = re.sub(r'freecad:editable="AUTOR"\s+x="[^"]+"\s+y="([^"]+)"\s+font-size="[^"]+"',
                       r'freecad:editable="AUTOR" x="367.00" y="\1" font-size="2.5"', contenido)
    with open(ruta_svg, "w", encoding="utf-8") as f:
        f.write(contenido)


def generar_svg_notas_y_tolerancias_16b(ancho_mm=200.0, alto_mm=45.0):
    """Bloque inferior izquierdo de especificaciones técnicas según IRAM 4515 y 4517."""
    W = ancho_mm
    H = alto_mm
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{H - 1.0:.1f}" fill="#ffffff" stroke="#000000" stroke-width="0.45"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="6.0" fill="#eaeff5" stroke="#000000" stroke-width="0.45"/>',
        f'<text x="{W / 2:.1f}" y="4.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.6" font-weight="bold" text-anchor="middle">ESPECIFICACIONES TÉCNICAS Y TOLERANCIAS DE FABRICACIÓN (NORMAS IRAM)</text>',
        
        # Cuadro de tolerancia geométrica de paralelismo (IRAM 4515)
        '<g transform="translate(4.0, 8.2)">',
        '<rect x="0" y="0" width="30.0" height="5.8" fill="#ffffff" stroke="#000000" stroke-width="0.35"/>',
        '<line x1="8.0" y1="0" x2="8.0" y2="5.8" stroke="#000000" stroke-width="0.25"/>',
        '<line x1="22.0" y1="0" x2="22.0" y2="5.8" stroke="#000000" stroke-width="0.25"/>',
        '<text x="4.0" y="4.2" font-family="Liberation Sans, Arial, sans-serif" font-size="3.0" text-anchor="middle">//</text>',
        '<text x="15.0" y="4.1" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold" text-anchor="middle">0,05</text>',
        '<text x="26.0" y="4.1" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold" text-anchor="middle">A</text>',
        '</g>',
        '<text x="37.0" y="12.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">Paralelismo entre cara superior y cara base inferior A (IRAM 4515)</text>',
        
        # Símbolo Ra 3,2 (ubicado en y=18.8 con texto en y=-0.8 sobre pluma sin tocar el cuadro superior)
        '<g transform="translate(4.0, 18.8)">',
        '<path d="M 0 4.5 L 2.8 8.0 L 7.2 0" fill="none" stroke="#000000" stroke-width="0.35"/>',
        '<line x1="7.2" y1="0" x2="17.5" y2="0" stroke="#000000" stroke-width="0.35"/>',
        '<text x="7.8" y="-0.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1" font-weight="bold">Ra 3,2</text>',
        '<text x="20.0" y="5.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">Rugosidad general de mecanizado (caras torneadas y fresadas)</text>',
        '</g>',

        # Símbolo Ra 0,8
        '<g transform="translate(4.0, 28.2)">',
        '<path d="M 0 4.5 L 2.8 8.0 L 7.2 0" fill="none" stroke="#000000" stroke-width="0.35"/>',
        '<line x1="7.2" y1="0" x2="17.5" y2="0" stroke="#000000" stroke-width="0.35"/>',
        '<text x="7.8" y="-0.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1" font-weight="bold">Ra 0,8</text>',
        '<text x="20.0" y="5.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">Asientos estáticos de junta tórica (⌀ 120,1 H8) y tubo de vidrio (⌀ 110,5 H7)</text>',
        '</g>',

        '<line x1="0.5" y1="36.5" x2="' + str(W - 0.5) + '" y2="36.5" stroke="#cccccc" stroke-width="0.25"/>',
        '<text x="4.0" y="40.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1">• Tolerancias dimensionales generales según ISO 2768-mK. Roscas métricas según ISO 68-1 / IRAM 5003.</text>',
        '<text x="4.0" y="43.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1">• Material: Acero Inoxidable AISI 304. Matar filos vivos 0,2 x 45°.</text>',
        '</svg>'
    ]
    return "\n".join(svg)


def generar_svg_datum_a():
    """Símbolo Datum A según IRAM 4515: apoyado sobre la línea auxiliar derecha de la base."""
    return """<svg xmlns="http://www.w3.org/2000/svg" width="10mm" height="10mm" viewBox="0 0 10 10">
      <polygon points="3.5,0.0 6.5,0.0 5.0,2.6" fill="#000000" stroke="#000000" stroke-width="0.30"/>
      <line x1="5.0" y1="2.6" x2="5.0" y2="4.2" stroke="#000000" stroke-width="0.35"/>
      <rect x="2.5" y="4.2" width="5.0" height="5.0" fill="#ffffff" stroke="#000000" stroke-width="0.45"/>
      <text x="5.0" y="7.9" font-family="Liberation Sans, Arial, sans-serif" font-size="3.4" font-weight="bold" text-anchor="middle">A</text>
    </svg>"""


def buscar_aristas_rebajes_det_b(vista_det_b):
    """Encuentra en Detalle B dos aristas horizontales distintas para ⌀41 y ⌀45,1."""
    edge_41 = "Edge31"
    edge_45 = "Edge33"
    try:
        edges = vista_det_b.getVisibleEdges()
        for idx, e in enumerate(edges):
            if abs(e.BoundBox.YLength) < 0.2:
                ancho = e.BoundBox.XLength
                if 28.0 <= ancho <= 32.0:
                    edge_41 = f"Edge{idx}"
                elif 36.0 <= ancho <= 42.0:
                    edge_45 = f"Edge{idx}"
    except Exception:
        pass
    return edge_41, edge_45


def construir_plano_tapa_interior_16b():
    print("Iniciando generación de Plano N° 16b (Tapa Interior Intermedia) IRAM...")
    
    rutas_plantillas = asegurar_plantillas_iram(os.path.join(RAIZ, "_plantillas"))
    parchar_svg_plantilla_a3(rutas_plantillas["A3"])
    
    ruta_pieza = os.path.join(DIR_PIEZAS, "Tapa_Interior_16b.FCStd")
    doc_pieza = App.openDocument(ruta_pieza)
    sp = doc_pieza.getObject("Parametros")
    if sp:
        sp.set("B2", "2")
        doc_pieza.recompute()
    sol_obj = doc_pieza.getObject("Tapa_Interior_Solido")
    shape_pieza = sol_obj.Shape.copy()
    masa_g = (shape_pieza.Volume * 1e-9) * 7850.0 * 1000.0
    App.closeDocument(doc_pieza.Name)

    try:
        doc_existente = App.getDocument("Plano_03_Tapa_Interior_16b")
        if doc_existente:
            App.closeDocument(doc_existente.Name)
    except Exception:
        pass

    doc_plano = App.newDocument("Plano_03_Tapa_Interior_16b")
    
    obj_p = doc_plano.addObject("Part::Feature", "Pieza_03_Solido")
    obj_p.Shape = shape_pieza
    if getattr(obj_p, "ViewObject", None):
        obj_p.ViewObject.Visibility = False

    page = doc_plano.addObject("TechDraw::DrawPage", "Plano_03_Tapa_Interior_16b")
    tpl = doc_plano.addObject("TechDraw::DrawSVGTemplate", "Template_Plano_03_Tapa_Interior_16b")
    tpl.Template = rutas_plantillas["A3"]
    page.Template = tpl

    # -------------------------------------------------------------------------
    # 1. VISTA SUPERIOR CIRCULAR (ISO-E: ABAJO, elevada a Y=114.0 para despejar cuadro de notas)
    # -------------------------------------------------------------------------
    v_planta = doc_plano.addObject("TechDraw::DrawViewPart", "VP_03_Planta")
    page.addView(v_planta)
    v_planta.Source = [obj_p]
    v_planta.Direction = App.Vector(0.0, 0.0, 1.0)
    v_planta.XDirection = App.Vector(1.0, 0.0, 0.0)
    v_planta.ScaleType = "Custom"
    v_planta.Scale = 0.5
    v_planta.X = 130.0
    v_planta.Y = 114.0
    estilizar_vista_iram(v_planta, mostrar_ocultas=False, mostrar_centros=True)

    # -------------------------------------------------------------------------
    # 2. SECCIÓN A-A (ISO-E: ARRIBA DE PLANTA, en Y=220.0)
    # -------------------------------------------------------------------------
    pat_file = obtener_ruta_fcpat()
    v_corte = doc_plano.addObject("TechDraw::DrawViewSection", "VP_03_Corte_AA")
    page.addView(v_corte)
    v_corte.Source = [obj_p]
    v_corte.BaseView = v_planta
    v_corte.SectionOrigin = App.Vector(0.0, 0.0, 15.0)
    v_corte.SectionNormal = App.Vector(0.0, -1.0, 0.0)
    v_corte.Direction = App.Vector(0.0, -1.0, 0.0)
    v_corte.XDirection = App.Vector(1.0, 0.0, 0.0)
    v_corte.SectionDirection = "Up"
    v_corte.SectionSymbol = "A"
    v_corte.SectionLineStretch = 6.0
    v_corte.ScaleType = "Custom"
    v_corte.Scale = 0.5
    v_corte.X = 130.0
    v_corte.Y = 220.0
    v_corte.Caption = ""
    v_corte.FuseBeforeCut = True
    v_corte.CutSurfaceDisplay = "PatHatch"
    v_corte.FileGeomPattern = pat_file
    v_corte.NameGeomPattern = "Diagonal4"
    v_corte.HatchScale = 2.0
    estilizar_vista_iram(v_corte, mostrar_ocultas=False, mostrar_centros=True)

    def agregar_texto(nombre, lineas, x, y, tam=3.5):
        ann = doc_plano.addObject("TechDraw::DrawViewAnnotation", nombre)
        page.addView(ann)
        ann.Text = lineas
        ann.TextSize = tam
        ann.X = x
        ann.Y = y
        return ann

    # Título arriba del corte y letras A y B por encima de la pieza sin tocar contornos ni cotas
    agregar_texto("Txt_Titulo_Corte", ["SECCIÓN A - A"], 130.0, 238.0, 4.0)
    agregar_texto("Txt_Ref_DetA", ["A"], 166.0, 230.0, 3.5)
    agregar_texto("Txt_Ref_DetB", ["B"], 140.0, 231.0, 3.5)

    # -------------------------------------------------------------------------
    # 3. DETALLE A (2:1): ESCALÓN EXTERIOR Y ROSCA M3 (Radio en hoja = 18.0 mm)
    # -------------------------------------------------------------------------
    det_a = doc_plano.addObject("TechDraw::DrawViewDetail", "VP_03_Detalle_A")
    page.addView(det_a)
    det_a.BaseView = v_corte
    det_a.AnchorPoint = App.Vector(36.0, -5.0, 0.0)
    det_a.Radius = 9.0
    det_a.ScaleType = "Custom"
    det_a.Scale = 2.0
    det_a.X = 258.0
    det_a.Y = 142.0
    det_a.Reference = "A"
    det_a.Caption = ""
    det_a.ShowHighlight = False
    det_a.ShowMatting = True
    estilizar_vista_iram(det_a, mostrar_ocultas=False, mostrar_centros=False)
    agregar_texto("Txt_Titulo_DetA", ["DETALLE A (2:1)"], 258.0, 94.0, 3.5)

    # -------------------------------------------------------------------------
    # 4. DETALLE B (2:1): ZONA CENTRAL Y REBAJES TRASEROS (Radio en hoja = 21.0 mm)
    # -------------------------------------------------------------------------
    det_b = doc_plano.addObject("TechDraw::DrawViewDetail", "VP_03_Detalle_B")
    page.addView(det_b)
    det_b.BaseView = v_corte
    det_b.AnchorPoint = App.Vector(0.0, 3.5, 0.0)
    det_b.Radius = 10.5
    det_b.ScaleType = "Custom"
    det_b.Scale = 2.0
    det_b.X = 352.0
    det_b.Y = 142.0
    det_b.Reference = "B"
    det_b.Caption = ""
    det_b.ShowHighlight = False
    det_b.ShowMatting = True
    estilizar_vista_iram(det_b, mostrar_ocultas=False, mostrar_centros=False)
    agregar_texto("Txt_Titulo_DetB", ["DETALLE B (2:1)"], 352.0, 94.0, 3.5)

    # -------------------------------------------------------------------------
    # 5. PERSPECTIVA ISOMÉTRICA 3D
    # -------------------------------------------------------------------------
    v_iso = doc_plano.addObject("TechDraw::DrawViewPart", "VP_03_Iso")
    page.addView(v_iso)
    v_iso.Source = [obj_p]
    v_iso.Direction = App.Vector(1.0, -1.0, 1.0)
    v_iso.XDirection = App.Vector(1.0, 1.0, 0.0)
    v_iso.ScaleType = "Custom"
    v_iso.Scale = 0.33
    v_iso.X = 315.0
    v_iso.Y = 232.0
    estilizar_vista_iram(v_iso, mostrar_ocultas=False, mostrar_centros=False)

    # -------------------------------------------------------------------------
    # 6. ESPECIFICACIONES TÉCNICAS Y SÍMBOLO DATUM A EXTERIOR
    # -------------------------------------------------------------------------
    sym_notas = doc_plano.addObject("TechDraw::DrawViewSymbol", "VP_03_Notas_Tecnicas")
    page.addView(sym_notas)
    sym_notas.Symbol = generar_svg_notas_y_tolerancias_16b(ancho_mm=200.0, alto_mm=45.0)
    sym_notas.X = 130.0
    sym_notas.Y = 36.0

    # Símbolo Datum A colocado a la derecha de la cota '30' (X=216.0), sin pisar ninguna línea
    sym_datum = doc_plano.addObject("TechDraw::DrawViewSymbol", "VP_03_Datum_A")
    page.addView(sym_datum)
    sym_datum.Symbol = generar_svg_datum_a()
    sym_datum.X = 216.0
    sym_datum.Y = 207.5

    doc_plano.recompute()

    # -------------------------------------------------------------------------
    # 7. EJES DE SIMETRÍA, LÍNEAS DE CENTRO Y CÍRCULOS DE DETALLE
    # -------------------------------------------------------------------------
    v_planta.makeCosmeticLine(App.Vector(-45.0, 0.0, 0.0), App.Vector(45.0, 0.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticLine(App.Vector(0.0, -45.0, 0.0), App.Vector(0.0, 45.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticLine(App.Vector(-26.0, -26.0, 0.0), App.Vector(26.0, 26.0, 0.0), 4, 0.18, (0.2, 0.2, 0.2, 1.0))
    
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 18.75, 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 32.50, 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 38.125, 4, 0.18, (0.0, 0.0, 0.0, 1.0))

    for xg in (-18.75, 18.75):
        v_planta.makeCosmeticLine(App.Vector(xg - 3.5, 0.0, 0.0), App.Vector(xg + 3.5, 0.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
        v_planta.makeCosmeticLine(App.Vector(xg, -3.5, 0.0), App.Vector(xg, 3.5, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    for yg in (-18.75, 18.75):
        v_planta.makeCosmeticLine(App.Vector(-3.5, yg, 0.0), App.Vector(3.5, yg, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
        v_planta.makeCosmeticLine(App.Vector(0.0, yg - 3.5, 0.0), App.Vector(0.0, yg + 3.5, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))

    # Arco de cota angular de 45° en v_planta
    v_planta.makeCosmeticCircleArc(App.Vector(0.0, 0.0, 0.0), 24.0, 0.0, 45.0, 1, 0.18, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticLine(App.Vector(24.0, 0.0, 0.0), App.Vector(25.5, 1.2, 0.0), 1, 0.25, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticLine(App.Vector(24.0 * math.cos(math.radians(45)), 24.0 * math.sin(math.radians(45)), 0.0),
                              App.Vector(22.5 * math.cos(math.radians(43)), 22.5 * math.sin(math.radians(43)), 0.0), 1, 0.25, (0.0, 0.0, 0.0, 1.0))

    # Ejes en Corte A-A y línea auxiliar extendida hasta X_local=92.0 para apoyar Datum A en X_hoja=216.0
    v_corte.makeCosmeticLine(App.Vector(0.0, -11.0, 0.0), App.Vector(0.0, 11.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    v_corte.makeCosmeticLine(App.Vector(-18.75, -8.0, 0.0), App.Vector(-18.75, 8.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    v_corte.makeCosmeticLine(App.Vector(18.75, -8.0, 0.0), App.Vector(18.75, 8.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    v_corte.makeCosmeticLine(App.Vector(40.0, -7.5, 0.0), App.Vector(92.0, -7.5, 0.0), 1, 0.20, (0.0, 0.0, 0.0, 1.0))

    # Círculos de detalle finos en v_corte y aros de recorte en det_a y det_b
    v_corte.makeCosmeticCircle(App.Vector(36.0, -5.0, 0.0), 9.0, 1, 0.18, (0.0, 0.0, 0.0, 1.0))
    v_corte.makeCosmeticCircle(App.Vector(0.0, 3.5, 0.0), 10.5, 1, 0.18, (0.0, 0.0, 0.0, 1.0))
    det_a.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 18.0, 1, 0.22, (0.0, 0.0, 0.0, 1.0))
    det_b.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 21.0, 1, 0.22, (0.0, 0.0, 0.0, 1.0))
    det_b.makeCosmeticLine(App.Vector(0.0, -10.0, 0.0), App.Vector(0.0, 10.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))

    def agregar_cota(nombre, tipo, refs, fmt, x, y):
        try:
            dim = doc_plano.addObject("TechDraw::DrawViewDimension", nombre)
            page.addView(dim)
            dim.Type = tipo
            dim.MeasureType = "Projected"
            dim.References2D = refs
            dim.Arbitrary = True
            dim.TheoreticalExact = False
            dim.FormatSpec = fmt
            dim.X = x
            dim.Y = y
            vo = getattr(dim, "ViewObject", None)
            if vo:
                try:
                    vo.Fontsize = 3.5
                    vo.Color = (0.0, 0.0, 0.0)
                except Exception:
                    pass
            return dim
        except Exception as e:
            print(f"Aviso en cota {nombre}: {e}")
            return None

    # -------------------------------------------------------------------------
    # 8. COTAS DEL CORTE LONGITUDINAL A-A
    # -------------------------------------------------------------------------
    agregar_cota("Cota_03_Diam_Cav2", "DistanceX", [(v_corte, "Vertex20"), (v_corte, "Vertex42")], "⌀110,5 H7", 0.0, -15.5)
    agregar_cota("Cota_03_Diam_Cav1", "DistanceX", [(v_corte, "Vertex18"), (v_corte, "Vertex44")], "⌀120,1 H8", 0.0, -23.0)
    agregar_cota("Cota_03_Diam_Enc",  "DistanceX", [(v_corte, "Vertex13"), (v_corte, "Vertex49")], "⌀145",      0.0, -30.5)
    agregar_cota("Cota_03_Diam_Ext",  "DistanceX", [(v_corte, "Vertex0"),  (v_corte, "Vertex3")],  "⌀160",      0.0, -38.0)

    agregar_cota("Cota_03_Alt_Enc",   "DistanceY", [(v_corte, "Vertex13"), (v_corte, "Vertex0")],  "4,5", -48.0, -6.37)
    agregar_cota("Cota_03_Prof_Cav1", "DistanceY", [(v_corte, "Vertex18"), (v_corte, "Vertex19")], "6,9", -56.0, -5.77)
    agregar_cota("Cota_03_Prof_Cav2", "DistanceY", [(v_corte, "Vertex20"), (v_corte, "Vertex21")], "8,1", -64.0, -2.02)

    # Desplazadas +6 mm a la derecha (X = 54 a 78) para despejar el borde de la pieza
    agregar_cota("Cota_03_Prof_Reb1", "DistanceY", [(v_corte, "Vertex53"), (v_corte, "Vertex6")],  "2,31", 54.0, 6.92)
    agregar_cota("Cota_03_Prof_Reb2", "DistanceY", [(v_corte, "Vertex6"),  (v_corte, "Vertex59")], "12,0", 62.0, 4.50)
    agregar_cota("Cota_03_Alt_Base",  "DistanceY", [(v_corte, "Vertex2"),  (v_corte, "Vertex3")],  "25,5", 70.0, 1.12)
    agregar_cota("Cota_03_Alt_Total", "DistanceY", [(v_corte, "Vertex2"),  (v_corte, "Vertex49")], "30",   78.0, 0.0)

    # -------------------------------------------------------------------------
    # 9. COTAS DE LA VISTA CIRCULAR INFERIOR (Radio exterior = 40.0 mm)
    # -------------------------------------------------------------------------
    agregar_cota("Cota_03_PCD_CorMed", "DistanceX", [(v_planta, "Vertex81"), (v_planta, "Vertex78")], "6x M3 en ⌀130 prof. 4",   0.0,  47.0)
    agregar_cota("Cota_03_PCD_CorExt", "DistanceX", [(v_planta, "Vertex11"), (v_planta, "Vertex17")], "6x M3 en ⌀152,5 prof. 6", 0.0,  55.0)
    agregar_cota("Cota_03_PCD_Guias",  "DistanceX", [(v_planta, "Vertex23"), (v_planta, "Vertex26")], "⌀75",                     0.0, -45.0)

    # Edge7 está a la derecha (X=+18.75): sacamos la directriz hacia abajo a la derecha (X=+52, Y=-18)
    agregar_cota("Cota_03_Guia_Paso",   "Diameter", [(v_planta, "Edge7")],  "2x ⌀10,1 H7",      52.0, -18.0)
    # Edge23 hacia abajo a la izquierda sin cruzar las cotas horizontales superiores
    agregar_cota("Cota_03_Puertos_G18", "Diameter", [(v_planta, "Edge23")], "2x G 1/8 prof. 8", -52.0, -26.0)
    agregar_cota("Cota_03_Puerto_M12",  "Diameter", [(v_planta, "Edge9")],  "M12x1 (a 45°)",     48.0,  32.0)
    # Etiqueta angular fuera del cajeado derecho
    agregar_texto("Txt_Ang_45", ["45°"], 158.0, 126.0, 3.5)

    # -------------------------------------------------------------------------
    # 10. COTAS DE DETALLE A (2:1) - Radio círculo = 18.0 mm
    # -------------------------------------------------------------------------
    agregar_cota("Cota_DetA_Alt_Enc",  "DistanceY", [(det_a, "Edge24")], "4,5",  23.0,  0.0)
    agregar_cota("Cota_DetA_Prof_M3",  "DistanceY", [(det_a, "Edge26")], "4",   -22.0, -4.0)
    agregar_texto("Txt_DetA_Rosca_M3", ["M3 prof. 4 (mecha ⌀2,5)"], 258.0, 165.0, 3.2)

    # -------------------------------------------------------------------------
    # 11. COTAS DE DETALLE B (2:1) - Radio círculo = 21.0 mm
    # -------------------------------------------------------------------------
    edge_41, edge_45 = buscar_aristas_rebajes_det_b(det_b)
    agregar_cota("Cota_DetB_Esp_Tabique",  "DistanceY", [(det_b, "Edge30")], "3",     -25.0,   6.0)
    agregar_cota("Cota_DetB_Diam_Central", "DistanceX", [(det_b, "Edge27")], "⌀15 H7",  0.0,  15.0)
    agregar_cota("Cota_DetB_Diam_Reb2",    "DistanceX", [(det_b, edge_41)],  "⌀41",     0.0, -23.0)
    agregar_cota("Cota_DetB_Diam_Reb1",    "DistanceX", [(det_b, edge_45)],  "⌀45,1",   0.0, -30.5)

    # -------------------------------------------------------------------------
    # 12. CAMPOS DEL RÓTULO IRAM 4508
    # -------------------------------------------------------------------------
    campos_rotulo = {
        "TITULO": "Tapa Interior Intermedia",
        "NUM_PLANO": "Plano Nº 16b",
        "HOJA": "1/1",
        "FORMATO": "IRAM A3",
        "ESCALA": "1:2",
        "MATERIAL": "Acero Inox. AISI 304",
        "MASA": f"{masa_g:.0f} g",
        "TOL_GRAL": "ISO 2768-mK",
        "AUTOR": "Dib.: F. Gutiérrez",
        "APROBADO": "Apr.: Ing. A. Bonino",
        "FECHA": "12/11/2026",
    }
    for k, v in campos_rotulo.items():
        try:
            tpl.setEditFieldContent(k, v)
        except Exception:
            pass

    doc_plano.recompute()
    
    os.makedirs(DIR_HOJAS, exist_ok=True)
    salida_fcstd = os.path.join(DIR_HOJAS, "Plano_03_Tapa_Interior_16b.FCStd")
    doc_plano.saveAs(salida_fcstd)
    print(f"Plano 16b guardado exitosamente: {salida_fcstd}")
    
    if App.GuiUp:
        try:
            import FreeCADGui as Gui
            Gui.ActiveDocument.ActiveView.fitAll()
        except Exception:
            pass
    else:
        App.closeDocument(doc_plano.Name)

    return salida_fcstd


if __name__ == "__main__":
    construir_plano_tapa_interior_16b()
else:
    construir_plano_tapa_interior_16b()
