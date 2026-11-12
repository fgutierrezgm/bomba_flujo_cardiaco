#!/usr/bin/env python3
"""
Generador del Plano N° 16b (Tapa Interior Intermedia) bajo normas IRAM:
- IRAM 4501: Método ISO-E (Primer Diedro) con SECCIÓN A-A ARRIBA y vista circular DEBAJO.
- IRAM 4502: Ejes de simetría (tipo G) y círculos primitivos de centros (PCD).
- IRAM 4509: Rayado a 45° gobernado nativamente por TechDraw, sin desbordes.
- IRAM 4513: Acotación directa en vistas sin tabla de variables de código; coma decimal.
             Cotas visibles (Arbitrary = True), paso uniforme de 7.5 a 8 mm.
- IRAM 4515: Tolerancia geométrica de paralelismo [ // | 0,05 | A ] con símbolo Datum A exterior.
- IRAM 4517: Acabado superficial Ra 3,2 general y Ra 0,8 en asientos de sellos, sin pisar trazo.
- IRAM 4520: Representación normalizada de roscas M3, G 1/8 y M12x1.
- IRAM 4508: Rótulo reglamentario con símbolo gráfico ISO-E y textos sin solapamiento.
- Dos Vistas de Detalle ampliadas 2:1:
    * Detalle A (2:1): Escalón exterior, resalte Ø145 x 4,5, rosca M3 prof. 4 / mecha Ø2,5.
    * Detalle B (2:1): Zona central (Detalle AF), rebajes traseros Ø45,1 y Ø41 escalonados,
                       tabique central de 3 mm y pasaje central Ø15 H7.
"""
import os
import sys
import math
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


def generar_svg_notas_y_tolerancias_16b(ancho_mm=200.0, alto_mm=45.0):
    """Bloque inferior izquierdo de especificaciones técnicas según IRAM 4515 y 4517."""
    W = ancho_mm
    H = alto_mm
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{H - 1.0:.1f}" fill="#ffffff" stroke="#000000" stroke-width="0.45"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="6.5" fill="#eaeff5" stroke="#000000" stroke-width="0.45"/>',
        f'<text x="{W / 2:.1f}" y="4.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.7" font-weight="bold" text-anchor="middle">ESPECIFICACIONES TÉCNICAS Y TOLERANCIAS DE FABRICACIÓN (NORMAS IRAM)</text>',
        
        # Cuadro de tolerancia geométrica de paralelismo (IRAM 4515)
        '<g transform="translate(4.0, 9.5)">',
        '<rect x="0" y="0" width="30.0" height="6.5" fill="#ffffff" stroke="#000000" stroke-width="0.35"/>',
        '<line x1="8.0" y1="0" x2="8.0" y2="6.5" stroke="#000000" stroke-width="0.25"/>',
        '<line x1="22.0" y1="0" x2="22.0" y2="6.5" stroke="#000000" stroke-width="0.25"/>',
        '<text x="4.0" y="4.8" font-family="Liberation Sans, Arial, sans-serif" font-size="3.2" text-anchor="middle">//</text>',
        '<text x="15.0" y="4.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4" font-weight="bold" text-anchor="middle">0,05</text>',
        '<text x="26.0" y="4.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4" font-weight="bold" text-anchor="middle">A</text>',
        '</g>',
        '<text x="37.0" y="14.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">Paralelismo entre cara superior y cara base inferior A (IRAM 4515)</text>',
        
        # Símbolos de acabado superficial (IRAM 4517: texto elevado 2.5 mm sobre la pluma horizontal)
        '<g transform="translate(4.0, 18.5)">',
        '<path d="M 0 5 L 3 9 L 8 0" fill="none" stroke="#000000" stroke-width="0.35"/>',
        '<line x1="4.5" y1="0" x2="16.0" y2="0" stroke="#000000" stroke-width="0.35"/>',
        '<text x="7.0" y="-2.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">Ra 3,2</text>',
        '<text x="18.0" y="6.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">Rugosidad general de mecanizado (caras torneadas y fresadas)</text>',
        '</g>',

        '<g transform="translate(4.0, 28.5)">',
        '<path d="M 0 5 L 3 9 L 8 0" fill="none" stroke="#000000" stroke-width="0.35"/>',
        '<line x1="4.5" y1="0" x2="16.0" y2="0" stroke="#000000" stroke-width="0.35"/>',
        '<text x="7.0" y="-2.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">Ra 0,8</text>',
        '<text x="18.0" y="6.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">Asientos estáticos de junta tórica (Ø120,1 H8) y tubo de vidrio (Ø110,5 H7)</text>',
        '</g>',

        '<line x1="0.5" y1="36.0" x2="' + str(W - 0.5) + '" y2="36.0" stroke="#cccccc" stroke-width="0.25"/>',
        '<text x="4.0" y="40.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1">• Tolerancias dimensionales generales según ISO 2768-mK. Roscas métricas según ISO 68-1 / IRAM 5003.</text>',
        '<text x="4.0" y="43.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1">• Material: Acero Inoxidable AISI 304. Matar filos vivos 0,2 x 45°.</text>',
        '</svg>'
    ]
    return "\n".join(svg)


def generar_svg_datum_a():
    """Símbolo Datum A según IRAM 4515: apoyado desde afuera sobre línea auxiliar."""
    return """<svg xmlns="http://www.w3.org/2000/svg" width="16mm" height="20mm" viewBox="0 0 16 20">
      <!-- Línea auxiliar de referencia horizontal -->
      <line x1="0" y1="4.0" x2="16" y2="4.0" stroke="#000000" stroke-width="0.25"/>
      <!-- Triángulo equilátero relleno negro apoyado en la línea -->
      <polygon points="8.0,4.0 6.25,1.0 9.75,1.0" fill="#000000" stroke="#000000" stroke-width="0.30"/>
      <!-- Tallo vertical hacia el recuadro -->
      <line x1="8.0" y1="4.0" x2="8.0" y2="10.0" stroke="#000000" stroke-width="0.35"/>
      <!-- Recuadro 5x5 mm con letra A -->
      <rect x="5.5" y="10.0" width="5.0" height="5.0" fill="#ffffff" stroke="#000000" stroke-width="0.45"/>
      <text x="8.0" y="13.9" font-family="Liberation Sans, Arial, sans-serif" font-size="3.5" font-weight="bold" text-anchor="middle">A</text>
    </svg>"""


def construir_plano_tapa_interior_16b():
    print("Iniciando generación de Plano N° 16b (Tapa Interior Intermedia) IRAM...")
    
    # Asegurar plantillas IRAM con rótulo y símbolo ISO-E corregidos
    rutas_plantillas = asegurar_plantillas_iram(os.path.join(RAIZ, "_plantillas"))
    
    # Abrir modelo 3D de la pieza
    ruta_pieza = os.path.join(DIR_PIEZAS, "Tapa_Interior_16b.FCStd")
    doc_pieza = App.openDocument(ruta_pieza)
    sp = doc_pieza.getObject("Parametros")
    if sp:
        sp.set("B2", "2")  # Modo 2 = CNC y Planos
        doc_pieza.recompute()
    sol_obj = doc_pieza.getObject("Tapa_Interior_Solido")
    shape_pieza = sol_obj.Shape.copy()
    masa_g = (shape_pieza.Volume * 1e-9) * 7850.0 * 1000.0  # AISI 304 (~3180 g)
    App.closeDocument(doc_pieza.Name)

    # Si el documento ya está abierto en la GUI de FreeCAD, cerrarlo primero
    try:
        doc_existente = App.getDocument("Plano_03_Tapa_Interior_16b")
        if doc_existente:
            App.closeDocument(doc_existente.Name)
    except Exception:
        pass

    # Crear documento de dibujo
    doc_plano = App.newDocument("Plano_03_Tapa_Interior_16b")
    
    # Objeto sólido fuente
    obj_p = doc_plano.addObject("Part::Feature", "Pieza_03_Solido")
    obj_p.Shape = shape_pieza
    if getattr(obj_p, "ViewObject", None):
        obj_p.ViewObject.Visibility = False

    # Página A3
    page = doc_plano.addObject("TechDraw::DrawPage", "Plano_03_Tapa_Interior_16b")
    tpl = doc_plano.addObject("TechDraw::DrawSVGTemplate", "Template_Plano_03_Tapa_Interior_16b")
    tpl.Template = rutas_plantillas["A3"]
    page.Template = tpl

    # -------------------------------------------------------------------------
    # 1. VISTA SUPERIOR CIRCULAR (BASE DE LA PROYECCIÓN ISO-E: ABAJO)
    # -------------------------------------------------------------------------
    v_planta = doc_plano.addObject("TechDraw::DrawViewPart", "VP_03_Planta")
    page.addView(v_planta)
    v_planta.Source = [obj_p]
    v_planta.Direction = App.Vector(0.0, 0.0, 1.0)
    v_planta.XDirection = App.Vector(1.0, 0.0, 0.0)
    v_planta.ScaleType = "Custom"
    v_planta.Scale = 0.5  # Escala 1:2
    v_planta.X = 130.0
    v_planta.Y = 108.0
    estilizar_vista_iram(v_planta, mostrar_ocultas=False, mostrar_centros=True)

    # -------------------------------------------------------------------------
    # 2. VISTA ANTERIOR FRONTAL EN CORTE (IRAM 4501 ISO-E: ARRIBA DE LA PLANTA)
    # -------------------------------------------------------------------------
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
    v_corte.Scale = 0.5  # Escala 1:2
    v_corte.X = 130.0
    v_corte.Y = 212.0
    v_corte.Caption = "SECCIÓN A - A"
    v_corte.CaptionSnap = "Top"  # Título arriba de la vista para despejar las cotas diametrales inferiores
    v_corte.FuseBeforeCut = True
    v_corte.CutSurfaceDisplay = "SvgHatch"
    v_corte.FileHatchPattern = "/snap/freecad/2926/usr/share/Mod/TechDraw/Patterns/hatch45R.svg"
    v_corte.HatchScale = 1.0
    estilizar_vista_iram(v_corte, mostrar_ocultas=False, mostrar_centros=True)

    # -------------------------------------------------------------------------
    # 3. DETALLE A (2:1): ESCALÓN EXTERIOR Y ROSCA M3 (CÍRCULO 1)
    # -------------------------------------------------------------------------
    det_a = doc_plano.addObject("TechDraw::DrawViewDetail", "VP_03_Detalle_A")
    page.addView(det_a)
    det_a.BaseView = v_corte
    det_a.AnchorPoint = App.Vector(36.0, -5.0, 0.0)
    det_a.Radius = 9.0
    det_a.ScaleType = "Custom"
    det_a.Scale = 2.0  # Escala 2:1
    det_a.X = 256.0
    det_a.Y = 135.0
    det_a.Reference = "A"
    det_a.Caption = "DETALLE A (2:1)"
    det_a.ShowHighlight = False  # Suprimir el resaltado automático para evitar letras toscas invasivas
    det_a.ShowMatting = False
    estilizar_vista_iram(det_a, mostrar_ocultas=False, mostrar_centros=False)

    # -------------------------------------------------------------------------
    # 4. DETALLE B (2:1): ZONA CENTRAL - REBAJES TRASEROS Y TABIQUE (CÍRCULO 2 / DETALLE AF)
    # -------------------------------------------------------------------------
    det_b = doc_plano.addObject("TechDraw::DrawViewDetail", "VP_03_Detalle_B")
    page.addView(det_b)
    det_b.BaseView = v_corte
    det_b.AnchorPoint = App.Vector(0.0, 3.5, 0.0)
    det_b.Radius = 10.5
    det_b.ScaleType = "Custom"
    det_b.Scale = 2.0  # Escala 2:1
    det_b.X = 352.0
    det_b.Y = 135.0
    det_b.Reference = "B"
    det_b.Caption = "DETALLE B (2:1)"
    det_b.ShowHighlight = False  # Suprimir resaltado automático
    det_b.ShowMatting = False
    estilizar_vista_iram(det_b, mostrar_ocultas=False, mostrar_centros=False)

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
    v_iso.Y = 228.0
    estilizar_vista_iram(v_iso, mostrar_ocultas=False, mostrar_centros=False)

    # -------------------------------------------------------------------------
    # 6. ESPECIFICACIONES TÉCNICAS Y SÍMBOLO DATUM A EXTERIOR
    # -------------------------------------------------------------------------
    sym_notas = doc_plano.addObject("TechDraw::DrawViewSymbol", "VP_03_Notas_Tecnicas")
    page.addView(sym_notas)
    sym_notas.Symbol = generar_svg_notas_y_tolerancias_16b(ancho_mm=200.0, alto_mm=45.0)
    sym_notas.X = 130.0
    sym_notas.Y = 36.0

    # Símbolo Datum A (IRAM 4515): ubicado 6 mm fuera del contorno derecho, sobre la línea auxiliar de base
    sym_datum = doc_plano.addObject("TechDraw::DrawViewSymbol", "VP_03_Datum_A")
    page.addView(sym_datum)
    sym_datum.Symbol = generar_svg_datum_a()
    sym_datum.X = 176.0
    sym_datum.Y = 204.5

    # Recomputar vistas para generar geometría 2D
    doc_plano.recompute()

    # -------------------------------------------------------------------------
    # 7. EJES DE SIMETRÍA, LÍNEAS DE CENTRO Y CÍRCULOS DE DETALLE FINOS
    # -------------------------------------------------------------------------
    # En Vista Circular (v_planta):
    # Ejes principales ortogonales (tipo G: trazo y punto fino)
    v_planta.makeCosmeticLine(App.Vector(-45.0, 0.0, 0.0), App.Vector(45.0, 0.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticLine(App.Vector(0.0, -45.0, 0.0), App.Vector(0.0, 45.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    # Eje a 45° del puerto M12x1
    v_planta.makeCosmeticLine(App.Vector(-26.0, -26.0, 0.0), App.Vector(26.0, 26.0, 0.0), 4, 0.18, (0.2, 0.2, 0.2, 1.0))
    
    # Círculos primitivos de centros (PCD en trazo y punto fino)
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 18.75, 4, 0.18, (0.0, 0.0, 0.0, 1.0))  # Ø75
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 32.50, 4, 0.18, (0.0, 0.0, 0.0, 1.0))  # Ø130
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 38.125, 4, 0.18, (0.0, 0.0, 0.0, 1.0)) # Ø152.5

    # Cruces de centro en agujeros sobre v_planta
    for xg in (-18.75, 18.75):
        v_planta.makeCosmeticLine(App.Vector(xg - 3.5, 0.0, 0.0), App.Vector(xg + 3.5, 0.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
        v_planta.makeCosmeticLine(App.Vector(xg, -3.5, 0.0), App.Vector(xg, 3.5, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    for yg in (-18.75, 18.75):
        v_planta.makeCosmeticLine(App.Vector(-3.5, yg, 0.0), App.Vector(3.5, yg, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
        v_planta.makeCosmeticLine(App.Vector(0.0, yg - 3.5, 0.0), App.Vector(0.0, yg + 3.5, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))

    # Arco de cota angular de 45° en v_planta (primer cuadrante)
    v_planta.makeCosmeticCircleArc(App.Vector(0.0, 0.0, 0.0), 24.0, 0.0, 45.0, 1, 0.18, (0.0, 0.0, 0.0, 1.0))
    # Flecha sobre arco
    v_planta.makeCosmeticLine(App.Vector(24.0, 0.0, 0.0), App.Vector(25.5, 1.2, 0.0), 1, 0.25, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticLine(App.Vector(24.0 * math.cos(math.radians(45)), 24.0 * math.sin(math.radians(45)), 0.0),
                              App.Vector(22.5 * math.cos(math.radians(43)), 22.5 * math.sin(math.radians(43)), 0.0), 1, 0.25, (0.0, 0.0, 0.0, 1.0))

    # En Corte A-A (v_corte):
    v_corte.makeCosmeticLine(App.Vector(0.0, -11.0, 0.0), App.Vector(0.0, 11.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    v_corte.makeCosmeticLine(App.Vector(-18.75, -8.0, 0.0), App.Vector(-18.75, 8.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    v_corte.makeCosmeticLine(App.Vector(18.75, -8.0, 0.0), App.Vector(18.75, 8.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    
    # Línea auxiliar horizontal para Datum A extendida a la derecha de la base
    v_corte.makeCosmeticLine(App.Vector(40.0, 7.5, 0.0), App.Vector(52.0, 7.5, 0.0), 1, 0.20, (0.0, 0.0, 0.0, 1.0))

    # Círculos de detalle finos con identificación en ángulo a 45° hacia afuera (IRAM 4502)
    # Círculo A (en resalte derecho):
    v_corte.makeCosmeticCircle(App.Vector(36.0, -5.0, 0.0), 9.0, 1, 0.18, (0.0, 0.0, 0.0, 1.0))
    # Círculo B (en tabique central):
    v_corte.makeCosmeticCircle(App.Vector(0.0, 3.5, 0.0), 10.5, 1, 0.18, (0.0, 0.0, 0.0, 1.0))

    # En Detalle B (det_b):
    # Eje vertical central acotado al radio del detalle
    det_b.makeCosmeticLine(App.Vector(0.0, -10.0, 0.0), App.Vector(0.0, 10.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))

    # Función auxiliar para configurar y activar cotas visibles (IRAM 4513)
    def agregar_cota(nombre, tipo, refs, fmt, x, y):
        try:
            dim = doc_plano.addObject("TechDraw::DrawViewDimension", nombre)
            page.addView(dim)
            dim.Type = tipo
            dim.MeasureType = "Projected"
            dim.References2D = refs
            dim.Arbitrary = True       # OBLIGATORIO: activa el renderizado visible de la cadena FormatSpec
            dim.TheoreticalExact = False
            dim.FormatSpec = fmt
            dim.X = x
            dim.Y = y
            vo = getattr(dim, "ViewObject", None)
            if vo:
                try:
                    vo.Fontsize = 3.5  # Altura normativa IRAM 4503
                    vo.Color = (0.0, 0.0, 0.0)
                except Exception:
                    pass
            return dim
        except Exception as e:
            print(f"Aviso en cota {nombre}: {e}")
            return None

    # -------------------------------------------------------------------------
    # 8. COTAS DEL CORTE LONGITUDINAL A-A (IRAM 4513)
    # -------------------------------------------------------------------------
    # A. Diámetros concéntricos escalonados DEBAJO del corte (paso constante de 7.5 mm)
    # La cara inferior está en y = -7.5. La primera cota empieza a 8.0 mm por debajo (y = -15.5)
    agregar_cota("Cota_03_Diam_Cav2", "DistanceX", [(v_corte, "Vertex20"), (v_corte, "Vertex42")], "⌀110,5 H7", 0.0, -15.5)
    agregar_cota("Cota_03_Diam_Cav1", "DistanceX", [(v_corte, "Vertex18"), (v_corte, "Vertex44")], "⌀120,1 H8", 0.0, -23.0)
    agregar_cota("Cota_03_Diam_Enc", "DistanceX", [(v_corte, "Vertex13"), (v_corte, "Vertex49")], "⌀145", 0.0, -30.5)
    agregar_cota("Cota_03_Diam_Ext", "DistanceX", [(v_corte, "Vertex0"), (v_corte, "Vertex3")], "⌀160", 0.0, -38.0)

    # B. Profundidades de cavidades superiores y resalte a la IZQUIERDA (paso constante de 8 mm)
    # x = -40 es el contorno izquierdo
    agregar_cota("Cota_03_Alt_Enc", "DistanceY", [(v_corte, "Vertex13"), (v_corte, "Vertex0")], "4,5", -48.0, -6.37)
    agregar_cota("Cota_03_Prof_Cav1", "DistanceY", [(v_corte, "Vertex18"), (v_corte, "Vertex19")], "6,9", -56.0, -5.77)
    agregar_cota("Cota_03_Prof_Cav2", "DistanceY", [(v_corte, "Vertex20"), (v_corte, "Vertex21")], "8,1", -64.0, -2.02)

    # C. Alturas y profundidades de rebajes traseros a la DERECHA (paso constante de 8 mm)
    # x = +40 es el contorno derecho
    agregar_cota("Cota_03_Prof_Reb1", "DistanceY", [(v_corte, "Vertex53"), (v_corte, "Vertex6")], "2,31", 48.0, 6.92)
    agregar_cota("Cota_03_Prof_Reb2", "DistanceY", [(v_corte, "Vertex6"), (v_corte, "Vertex59")], "12,0", 56.0, 4.50)
    agregar_cota("Cota_03_Alt_Base", "DistanceY", [(v_corte, "Vertex2"), (v_corte, "Vertex3")], "25,5", 64.0, 1.12)
    agregar_cota("Cota_03_Alt_Total", "DistanceY", [(v_corte, "Vertex2"), (v_corte, "Vertex49")], "30", 72.0, 0.0)

    # -------------------------------------------------------------------------
    # 9. COTAS DE LA VISTA CIRCULAR INFERIOR (PCD, GUÍAS, PUERTOS)
    # -------------------------------------------------------------------------
    # Cotas horizontales de PCD elevadas fuera del contorno exterior (R_ext = 40 mm)
    agregar_cota("Cota_03_PCD_CorMed", "DistanceX", [(v_planta, "Vertex81"), (v_planta, "Vertex78")], "6x M3 en ⌀130 prof. 4", 0.0, 48.0)
    agregar_cota("Cota_03_PCD_CorExt", "DistanceX", [(v_planta, "Vertex11"), (v_planta, "Vertex17")], "6x M3 en ⌀152,5 prof. 6", 0.0, 56.0)
    agregar_cota("Cota_03_PCD_Guias", "DistanceX", [(v_planta, "Vertex23"), (v_planta, "Vertex26")], "⌀75", 0.0, -24.0)

    # Agujero de guía en cuadrante izquierdo (180°), directriz hacia abajo a la izquierda (225°)
    agregar_cota("Cota_03_Guia_Paso", "Diameter", [(v_planta, "Edge7")], "2x ⌀10,1 H7", -30.0, -12.0)

    # Puertos de fluido G 1/8 en agujero inferior (270°), directriz hacia abajo a la izquierda (240°)
    agregar_cota("Cota_03_Puertos_G18", "Diameter", [(v_planta, "Edge23")], "2x G 1/8 prof. 8", -20.0, -30.0)

    # Cuadrante superior derecho exclusivo para puerto M12 y arco angular de 45°
    agregar_cota("Cota_03_Puerto_M12", "Diameter", [(v_planta, "Edge9")], "M12x1 a 45°", 26.0, -26.0)
    agregar_cota("Cota_03_Ang_M12", "DistanceX", [(v_planta, "Vertex15"), (v_planta, "Vertex17")], "45°", 22.0, 10.0)

    # -------------------------------------------------------------------------
    # 10. COTAS DE DETALLE A (2:1): ESCALÓN EXTERIOR Y ROSCA M3 (CÍRCULO 1)
    # -------------------------------------------------------------------------
    # Altura resalte exterior fuera del círculo a la derecha
    agregar_cota("Cota_DetA_Alt_Enc", "DistanceY", [(det_a, "Edge24")], "4,5", 14.0, 0.0)
    # Rosca M3 fuera del círculo a la izquierda
    agregar_cota("Cota_DetA_Rosca_M3", "DistanceY", [(det_a, "Edge26")], "M3 prof. 4 / mecha ⌀2,5", -14.0, -14.0)

    # -------------------------------------------------------------------------
    # 11. COTAS DE DETALLE B (2:1): ZONA CENTRAL (CÍRCULO 2 / DETALLE AF)
    # -------------------------------------------------------------------------
    # Espesor tabique central
    agregar_cota("Cota_DetB_Esp_Tabique", "DistanceY", [(det_b, "Edge30")], "3", 18.0, 10.0)
    # Agujero pasante central sacado arriba fuera del hueco
    agregar_cota("Cota_DetB_Diam_Central", "DistanceX", [(det_b, "Edge27")], "⌀15 H7", 0.0, 20.0)
    # Rebajes traseros escalonados abajo (⌀41 primero, ⌀45,1 a 7.5 mm por debajo)
    agregar_cota("Cota_DetB_Diam_Reb2", "DistanceX", [(det_b, "Edge34")], "⌀41", 0.0, -16.0)
    agregar_cota("Cota_DetB_Diam_Reb1", "DistanceX", [(det_b, "Edge34")], "⌀45,1", 0.0, -23.5)

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
    
    # Guardar en hojas/Plano_03_Tapa_Interior_16b.FCStd
    os.makedirs(DIR_HOJAS, exist_ok=True)
    salida_fcstd = os.path.join(DIR_HOJAS, "Plano_03_Tapa_Interior_16b.FCStd")
    doc_plano.saveAs(salida_fcstd)
    print(f"Plano 16b guardado exitosamente: {salida_fcstd}")
    
    # En entorno con interfaz gráfica, ajustar zoom
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
