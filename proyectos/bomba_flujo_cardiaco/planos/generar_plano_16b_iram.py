#!/usr/bin/env python3
"""
Generador del Plano N° 16b (Tapa Interior Intermedia) bajo normas IRAM:
- IRAM 4501: Método ISO-E (Primer Diedro) con corte frontal A-A ARRIBA y vista circular DEBAJO.
- IRAM 4502: Ejes de simetría (tipo G) y círculos primitivos de centros (PCD).
- IRAM 4509: Rayado a 45° continuo en toda sección maciza y en detalles.
- IRAM 4513: Acotación directa en vistas sin tabla de variables de código; coma decimal.
- IRAM 4515: Tolerancia geométrica de paralelismo [ // | 0,05 | A ].
- IRAM 4517: Acabado superficial Ra 3,2 general y Ra 0,8 en asientos de sellos.
- IRAM 4520: Representación normalizada de roscas M3, G 1/8 y M12x1.
- IRAM 4508: Rótulo reglamentario con símbolo gráfico ISO-E.
- Dos Vistas de Detalle ampliadas 2:1:
    * Detalle A (2:1): Escalón exterior, resalte Ø145 x 4,5, cavidad 1 (Ø120,1 x 6,9) y roscas M3.
    * Detalle B (2:1): Zona central (Detalle AF), rebajes traseros Ø45,1 x 2,31 y Ø41 x 9,69,
                       tabique central de 3 mm y pasaje central Ø15 H7.
"""
import os
import sys
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
        
        # Símbolos de acabado superficial (IRAM 4517)
        '<g transform="translate(4.0, 18.5)">',
        '<path d="M 0 5 L 3 9 L 8 0" fill="none" stroke="#000000" stroke-width="0.35"/>',
        '<line x1="4.5" y1="0" x2="16.0" y2="0" stroke="#000000" stroke-width="0.35"/>',
        '<text x="6.0" y="-1.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">Ra 3,2</text>',
        '<text x="18.0" y="6.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">Rugosidad general de mecanizado (caras torneadas y fresadas)</text>',
        '</g>',

        '<g transform="translate(4.0, 28.5)">',
        '<path d="M 0 5 L 3 9 L 8 0" fill="none" stroke="#000000" stroke-width="0.35"/>',
        '<line x1="4.5" y1="0" x2="16.0" y2="0" stroke="#000000" stroke-width="0.35"/>',
        '<text x="6.0" y="-1.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">Ra 0,8</text>',
        '<text x="18.0" y="6.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2">Asientos estáticos de junta tórica (Ø120,1 H8) y tubo de vidrio (Ø110,5 H7)</text>',
        '</g>',

        '<line x1="0.5" y1="36.0" x2="' + str(W - 0.5) + '" y2="36.0" stroke="#cccccc" stroke-width="0.25"/>',
        '<text x="4.0" y="40.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1">• Tolerancias dimensionales generales según ISO 2768-mK. Roscas métricas según ISO 68-1 / IRAM 5003.</text>',
        '<text x="4.0" y="43.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.1">• Material: Acero Inoxidable AISI 304 / PVC Rígido. Matar filos vivos 0,2 x 45°.</text>',
        '</svg>'
    ]
    return "\n".join(svg)


def construir_plano_tapa_interior_16b():
    print("Iniciando generación de Plano N° 16b (Tapa Interior Intermedia) IRAM...")
    
    # Asegurar plantillas IRAM
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
    masa_g = (shape_pieza.Volume * 1e-9) * 7850.0 * 1000.0  # AISI 304 (~518 g)
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
    # 1. VISTA SUPERIOR CIRCULAR (BASE DE LA PROYECCIÓN)
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
    estilizar_vista_iram(v_corte, mostrar_ocultas=False, mostrar_centros=True)

    # -------------------------------------------------------------------------
    # 3. DETALLE A (2:1): ESCALÓN EXTERIOR, RESALTE Ø145 x 4,5 Y ROSCAS M3 (CÍRCULO 1)
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
    # 6. BLOQUE DE ESPECIFICACIONES TÉCNICAS, RUGOSIDAD Y TOLERANCIA IRAM (INFERIOR IZQ.)
    # -------------------------------------------------------------------------
    sym_notas = doc_plano.addObject("TechDraw::DrawViewSymbol", "VP_03_Notas_Tecnicas")
    page.addView(sym_notas)
    sym_notas.Symbol = generar_svg_notas_y_tolerancias_16b(ancho_mm=200.0, alto_mm=45.0)
    sym_notas.X = 130.0
    sym_notas.Y = 36.0

    # Recomputar vistas para generar geometría 2D
    doc_plano.recompute()

    # -------------------------------------------------------------------------
    # 7. EJES DE SIMETRÍA Y LÍNEAS DE CENTRO (IRAM 4502)
    # -------------------------------------------------------------------------
    # En Vista Circular (v_planta):
    # Eje horizontal y vertical principales (trazo y punto fino)
    v_planta.makeCosmeticLine(App.Vector(-45.0, 0.0, 0.0), App.Vector(45.0, 0.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    v_planta.makeCosmeticLine(App.Vector(0.0, -45.0, 0.0), App.Vector(0.0, 45.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    # Eje a 45° del puerto M12x1
    v_planta.makeCosmeticLine(App.Vector(-26.0, -26.0, 0.0), App.Vector(26.0, 26.0, 0.0), 4, 0.18, (0.2, 0.2, 0.2, 1.0))
    
    # Círculos primitivos de centros (PCD en trazo y punto fino)
    # d_c75: R = 75 * 0.5 * 0.5 = 18.75 mm
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 18.75, 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    # d_cor_med: R = 130 * 0.5 * 0.5 = 32.50 mm
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 32.50, 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    # d_cor_ext: R = 152.5 * 0.5 * 0.5 = 38.125 mm
    v_planta.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), 38.125, 4, 0.18, (0.0, 0.0, 0.0, 1.0))

    # Cruces de centro en agujeros sobre v_planta
    for xg in (-18.75, 18.75):
        v_planta.makeCosmeticLine(App.Vector(xg - 3.5, 0.0, 0.0), App.Vector(xg + 3.5, 0.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
        v_planta.makeCosmeticLine(App.Vector(xg, -3.5, 0.0), App.Vector(xg, 3.5, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    for yg in (-18.75, 18.75):
        v_planta.makeCosmeticLine(App.Vector(-3.5, yg, 0.0), App.Vector(3.5, yg, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
        v_planta.makeCosmeticLine(App.Vector(0.0, yg - 3.5, 0.0), App.Vector(0.0, yg + 3.5, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))

    # En Corte A-A (v_corte):
    # Eje vertical central
    v_corte.makeCosmeticLine(App.Vector(0.0, -11.0, 0.0), App.Vector(0.0, 11.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))
    # Ejes verticales de guías
    v_corte.makeCosmeticLine(App.Vector(-18.75, -8.0, 0.0), App.Vector(-18.75, 8.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))
    v_corte.makeCosmeticLine(App.Vector(18.75, -8.0, 0.0), App.Vector(18.75, 8.0, 0.0), 4, 0.18, (0.0, 0.0, 0.0, 1.0))

    # En Detalle B (det_b):
    # Eje vertical central ampliado 2:1
    det_b.makeCosmeticLine(App.Vector(0.0, -18.0, 0.0), App.Vector(0.0, 18.0, 0.0), 4, 0.20, (0.0, 0.0, 0.0, 1.0))

    # -------------------------------------------------------------------------
    # 8. COTAS DEL CORTE LONGITUDINAL A-A (IRAM 4513)
    # -------------------------------------------------------------------------
    # Diámetros concéntricos escalonados ARRIBA del corte
    cotas_corte = [
        # (Nombre, Tipo, Ref1, Ref2, Formato, X, Y)
        ("Cota_03_Diam_Ext", "DistanceX", "Vertex0", "Vertex3", "⌀160", 0.0, -23.5),
        ("Cota_03_Diam_Enc", "DistanceX", "Vertex13", "Vertex49", "⌀145", 0.0, -17.5),
        ("Cota_03_Diam_Cav1", "DistanceX", "Vertex18", "Vertex44", "⌀120,1 H8", 0.0, -11.5),
        ("Cota_03_Diam_Cav2", "DistanceX", "Vertex20", "Vertex42", "⌀110,5 H7", 0.0, -5.5),
        # Altura total y base a la derecha
        ("Cota_03_Alt_Total", "DistanceY", "Vertex2", "Vertex49", "30", 52.0, 0.0),
        ("Cota_03_Alt_Base", "DistanceY", "Vertex2", "Vertex3", "25,5", 44.0, 1.1),
    ]
    for nom, tipo, r1, r2, fmt, dx, dy in cotas_corte:
        try:
            dim = doc_plano.addObject("TechDraw::DrawViewDimension", nom)
            page.addView(dim)
            dim.Type = tipo
            dim.MeasureType = "Projected"
            dim.FormatSpec = fmt
            dim.References2D = [(v_corte, r1), (v_corte, r2)]
            dim.X = dx
            dim.Y = dy
        except Exception as e:
            print(f"Aviso en cota {nom}: {e}")

    # -------------------------------------------------------------------------
    # 9. COTAS DE LA VISTA CIRCULAR INFERIOR (PCD, GUÍAS, PUERTOS)
    # -------------------------------------------------------------------------
    cotas_planta = [
        ("Cota_03_PCD_CorExt", "DistanceX", "Vertex11", "Vertex17", "6x M3 en ⌀152,5 prof. 6", 0.0, 43.5),
        ("Cota_03_PCD_CorMed", "DistanceX", "Vertex81", "Vertex78", "6x M3 en ⌀130 prof. 4", 0.0, 36.5),
        ("Cota_03_PCD_Guias", "DistanceX", "Vertex23", "Vertex26", "⌀75 (PCD)", 0.0, -23.5),
    ]
    for nom, tipo, r1, r2, fmt, dx, dy in cotas_planta:
        try:
            dim = doc_plano.addObject("TechDraw::DrawViewDimension", nom)
            page.addView(dim)
            dim.Type = tipo
            dim.MeasureType = "Projected"
            dim.FormatSpec = fmt
            dim.References2D = [(v_planta, r1), (v_planta, r2)]
            dim.X = dx
            dim.Y = dy
        except Exception as e:
            print(f"Aviso en {nom}: {e}")

    # Diámetros directos de agujeros en planta
    cotas_planta_circ = [
        ("Cota_03_Guia_Paso", "Diameter", "Edge8", "2x ⌀10,1 H7", 28.0, 8.0),
        ("Cota_03_Puerto_M12", "Diameter", "Edge9", "M12x1 (a 45°)", 25.0, -25.0),
        ("Cota_03_Puertos_G18", "Diameter", "Edge19", "2x G 1/8 prof. 8", -18.0, 28.0),
    ]
    for nom, tipo, ref, fmt, dx, dy in cotas_planta_circ:
        try:
            dim = doc_plano.addObject("TechDraw::DrawViewDimension", nom)
            page.addView(dim)
            dim.Type = tipo
            dim.MeasureType = "Projected"
            dim.FormatSpec = fmt
            dim.References2D = [(v_planta, ref)]
            dim.X = dx
            dim.Y = dy
        except Exception as e:
            print(f"Aviso en {nom}: {e}")

    # -------------------------------------------------------------------------
    # 10. COTAS DE DETALLE A (2:1): ESCALÓN EXTERIOR Y ROSCAS M3 (CÍRCULO 1)
    # -------------------------------------------------------------------------
    cotas_deta = [
        ("Cota_DetA_Alt_Enc", "DistanceY", "Edge24", "4,5", 14.5, -2.0),
        ("Cota_DetA_Prof_Cav1", "DistanceY", "Edge15", "6,9", -15.5, 9.0),
        ("Cota_DetA_Prof_M3", "DistanceY", "Edge26", "M3 prof. 4", 5.0, 6.0),
        ("Cota_DetA_Diam_M3", "DistanceX", "Edge22", "⌀2,5 (mecha)", -12.0, 13.5),
    ]
    for nom, tipo, ref, fmt, dx, dy in cotas_deta:
        try:
            dim = doc_plano.addObject("TechDraw::DrawViewDimension", nom)
            page.addView(dim)
            dim.Type = tipo
            dim.MeasureType = "Projected"
            dim.FormatSpec = fmt
            dim.References2D = [(det_a, ref)]
            dim.X = dx
            dim.Y = dy
        except Exception as e:
            print(f"Aviso en {nom}: {e}")

    # Rayado cosmético a 45° en Detalle A
    for yh in range(-8, 14, 3):
        det_a.makeCosmeticLine(App.Vector(-16.0, float(yh), 0.0), App.Vector(-6.0, float(yh + 10), 0.0), 1, 0.18, (0.0, 0.0, 0.0, 1.0))
        det_a.makeCosmeticLine(App.Vector(2.0, float(yh), 0.0), App.Vector(12.0, float(yh + 10), 0.0), 1, 0.18, (0.0, 0.0, 0.0, 1.0))

    # -------------------------------------------------------------------------
    # 11. COTAS DE DETALLE B (2:1): ZONA CENTRAL (CÍRCULO 2 / DETALLE AF)
    # -------------------------------------------------------------------------
    cotas_detb = [
        ("Cota_DetB_Esp_Tabique", "DistanceY", "Edge30", "3", 19.5, 10.0),
        ("Cota_DetB_Diam_Central", "DistanceX", "Edge27", "⌀15 H7", 0.0, 17.5),
        ("Cota_DetB_Diam_Reb2", "DistanceX", "Edge34", "⌀41", 0.0, -14.0),
    ]
    for nom, tipo, ref, fmt, dx, dy in cotas_detb:
        try:
            dim = doc_plano.addObject("TechDraw::DrawViewDimension", nom)
            page.addView(dim)
            dim.Type = tipo
            dim.MeasureType = "Projected"
            dim.FormatSpec = fmt
            dim.References2D = [(det_b, ref)]
            dim.X = dx
            dim.Y = dy
        except Exception as e:
            print(f"Aviso en {nom}: {e}")

    # Cota de profundidad de rebaje trasero 1 (2,31 mm) y diámetro rebaje 1 (Ø45,1)
    try:
        dim_reb1 = doc_plano.addObject("TechDraw::DrawViewDimension", "Cota_03_Prof_Reb1")
        page.addView(dim_reb1)
        dim_reb1.Type = "DistanceY"
        dim_reb1.MeasureType = "Projected"
        dim_reb1.FormatSpec = "2,31"
        dim_reb1.References2D = [(v_corte, "Vertex53"), (v_corte, "Vertex6")]
        dim_reb1.X = -18.0
        dim_reb1.Y = 7.0
    except Exception as e:
        print(f"Aviso en Cota_03_Prof_Reb1: {e}")

    # Rayado cosmético a 45° en Detalle B (tabique central macizo)
    for yh in range(7, 13, 2):
        det_b.makeCosmeticLine(App.Vector(-15.0, float(yh), 0.0), App.Vector(-11.0, float(yh + 4), 0.0), 1, 0.18, (0.0, 0.0, 0.0, 1.0))
        det_b.makeCosmeticLine(App.Vector(11.0, float(yh), 0.0), App.Vector(15.0, float(yh + 4), 0.0), 1, 0.18, (0.0, 0.0, 0.0, 1.0))

    # -------------------------------------------------------------------------
    # 12. CAMPOS DEL RÓTULO IRAM 4508
    # -------------------------------------------------------------------------
    campos_rotulo = {
        "TITULO": "Tapa Interior Intermedia",
        "NUM_PLANO": "Plano Nº 16b",
        "HOJA": "1/1",
        "FORMATO": "IRAM A3",
        "ESCALA": "1:2",
        "MATERIAL": "AISI 304 / PVC",
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
    
    # Si estamos en modo headless, cerramos; si estamos en GUI activa, dejamos la página en pantalla
    if not App.GuiUp:
        App.closeDocument(doc_plano.Name)
    else:
        import FreeCADGui as Gui
        Gui.ActiveDocument.ActiveView.fitAll()

    return salida_fcstd


construir_plano_tapa_interior_16b()
