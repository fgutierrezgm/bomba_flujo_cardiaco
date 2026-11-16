# Tornillo Sin Fin 3D (Escala 75.5%) - Rosca Trapezoidal 90° FDM (Opción A2: p = 3.00 mm)
# Ejecución: /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_tornillo_sin_fin_14_3d.py
import os
import sys
import FreeCAD as App
import Part

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 1
SALIDA = os.path.join(AQUI, "Tornillo_Sin_Fin_14_3D.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_total",      "Longitud total del sinfín 3D",             "192.15 mm", "L", None, "plano"),
    ("l_cuerpo",     "Longitud hasta fin tramo roscado (Opción 2)","179.00 mm", "L", None, "usuario"),
    ("l_esc_med",    "Longitud ref. escalón intermedio (Opción 2)","186.11 mm", "L", None, "plano"),
    ("d_ext",        "Ø mayor cresta rosca (imprime ~10.65 mm)", "10.50 mm",  "L", None, "usuario"),
    ("paso",         "Paso rosca trapezoidal 90° (Opción A2)",   "3.00 mm",   "N", None, "usuario"),
    ("h_diente",     "Profundidad radial filete 45° FDM",        "0.85 mm",   "N", None, "calculado"),
    ("b_cresta",     "Ancho plano cresta del diente",            "0.60 mm",   "N", None, "calculado"),
    ("z_rosca_ini",  "Inicio tramo roscado desde extremo acople","14.00 mm",  "L", None, "calculado"),
    ("z_rosca_fin",  "Fin tramo roscado antes de punta Opción 2","179.00 mm", "L", None, "calculado"),
    ("d_esc_med",    "Ø escalón transición (= raíz rosca Op. 2)", "8.80 mm",   "L", None, "usuario"),
    ("d_punta_sup",  "Ø espiga extremo libre (= raíz rosca Op. 2)","8.80 mm",  "L", None, "usuario"),
    ("d_aloj_eje",   "Ø taladro axial acople Transmisor B (+FDM)","6.49 mm",  "L", None, "usuario"),
    ("prof_aloj_eje","Profundidad taladro axial acople",         "11.32 mm",  "L", None, "plano"),
    ("z_pasador",    "Posición Z pasador transversal 3x10",      "5.68 mm",   "L", None, "plano"),
    ("d_pasador",    "Ø agujero pasador 3mm (+FDM anti-rajadura)","3.45 mm",  "L", None, "usuario"),
    ("mej_estabilizador_fdm", "0=pieza limpia ensamblaje | 1=con 3 costillas 90 mm", "0", "N", None, "usuario"),
]

MODO_ESTABILIZADOR = int(os.environ.get("CON_ESTABILIZADOR", "0"))
if MODO_ESTABILIZADOR:
    DIMS[-1] = ("mej_estabilizador_fdm", "0=pieza limpia ensamblaje | 1=con 3 costillas 90 mm", "1", "N", None, "usuario")
    SALIDA = os.path.join(AQUI, "Tornillo_Sin_Fin_14_3D_Impresion.FCStd")

MAT_PLA = {
    "nombre": "PLA+ / PETG (Impresión 3D)",
    "densidad_num": "0.00000124",
    "densidad_desc": "1.24 g / cm^3 (kg / mm^3)",
    "color": (0.18, 0.42, 0.72),
    "transparencia": 0,
}

pz = Pieza("Tornillo_Sin_Fin_14_3D_Impresion" if MODO_ESTABILIZADOR else "Tornillo_Sin_Fin_14_3D")
pz.parametros(DIMS, modo=MODO_DISENO, escala="1.0", holgura_fdm="0.45 mm")
pz.materiales(MAT_PLA, origen="usuario")


def _agregar_costillas_estabilizadoras(shape_sinfin, r_ext):
    """Agrega 3 costillas triangulares a 120° hasta Z=90 mm unidas por puentes rompibles cada 30 mm."""
    import math
    h_stab = 90.0
    sep = 0.40
    r_int_aleta = r_ext + sep
    r_base_out = 13.5
    r_top_out = 8.2
    espesor_aleta = 1.60

    # Zapata anular inferior para adherencia en cama (Z = 0..1.2 mm)
    anillo_base = Part.makeCylinder(r_base_out, 1.2, App.Vector(0.0, 0.0, 0.0))
    hueco_anillo = Part.makeCylinder(r_ext - 0.15, 1.4, App.Vector(0.0, 0.0, -0.1))
    piezas_stab = [anillo_base.cut(hueco_anillo)]

    for deg in (0.0, 120.0, 240.0):
        # Trapecio en XZ: desde r_int_aleta..r_base_out en Z=0 hasta r_int_aleta..r_top_out en Z=90
        pts = [
            App.Vector(r_int_aleta, -espesor_aleta / 2.0, 0.0),
            App.Vector(r_base_out,  -espesor_aleta / 2.0, 0.0),
            App.Vector(r_top_out,   -espesor_aleta / 2.0, h_stab),
            App.Vector(r_int_aleta, -espesor_aleta / 2.0, h_stab),
            App.Vector(r_int_aleta, -espesor_aleta / 2.0, 0.0),
        ]
        aleta = Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0.0, espesor_aleta, 0.0))

        # Puentes rompibles de 0.45 mm de alto cada 30 mm (Z = 30, 60, 90) y base Z=0..1.2
        aletas_con_puentes = aleta
        for zp in (0.4, 30.0, 60.0, 89.2):
            puente = Part.makeBox(
                r_int_aleta - (r_ext - 0.90) + 0.2,
                1.2,
                0.45,
                App.Vector(r_ext - 0.90, -0.6, zp),
            )
            aletas_con_puentes = aletas_con_puentes.fuse(puente)

        aletas_con_puentes.rotate(App.Vector(0.0, 0.0, 0.0), App.Vector(0.0, 0.0, 1.0), deg)
        piezas_stab.append(aletas_con_puentes)

    res = shape_sinfin
    for p_s in piezas_stab:
        res = res.fuse(p_s)
    return res


def _crear_sinfin(pz_obj):
    """Genera el husillo macizo con rosca trapezoidal 90° (45° FDM) y acoples originales."""
    ss = pz_obj.hoja
    l_tot = float(ss.get("l_total").Value)
    l_cue = float(ss.get("l_cuerpo").Value)
    l_med = float(ss.get("l_esc_med").Value)
    r_ext = float(ss.get("d_ext").Value) / 2.0
    paso = float(ss.get("paso").Value)
    h1 = float(ss.get("h_diente").Value)
    b_c = float(ss.get("b_cresta").Value)
    z_ini = float(ss.get("z_rosca_ini").Value)
    z_fin = float(ss.get("z_rosca_fin").Value)
    r_med = float(ss.get("d_esc_med").Value) / 2.0
    r_sup = float(ss.get("d_punta_sup").Value) / 2.0
    r_eje = float(ss.get("d_aloj_eje").Value) / 2.0
    p_eje = float(ss.get("prof_aloj_eje").Value)
    z_pas = float(ss.get("z_pasador").Value)
    r_pas = float(ss.get("d_pasador").Value) / 2.0

    r_raiz = r_ext - h1
    r_afuera = r_ext + 0.35
    dr = r_afuera - r_raiz

    # Flanco 45°: en r_ext el diente mide b_c -> ancho del valle en r_ext es (paso - b_c)
    # Con 45°, el valle se ensancha Δz = Δr por lado hacia afuera y se angosta hacia la raíz
    media_valle_ext = (paso - b_c) / 2.0
    media_valle_raiz = max(0.25, media_valle_ext - h1)
    media_valle_out = media_valle_ext + (r_afuera - r_ext)

    # 1. Cuerpo base macizo respetando extremos exactos del STEP original
    cil_cuerpo = Part.makeCylinder(r_ext, l_cue, App.Vector(0.0, 0.0, 0.0))
    cil_med = Part.makeCylinder(r_med, l_med - l_cue, App.Vector(0.0, 0.0, l_cue))
    cil_sup = Part.makeCylinder(r_sup, l_tot - l_med, App.Vector(0.0, 0.0, l_med))
    cuerpo = cil_cuerpo.fuse(cil_med).fuse(cil_sup)

    # 2. Una vuelta de valle trapezoidal a 45° (Part::Helix + Part::Sweep en doc temporal)
    doc_tmp = App.newDocument("_tmp_sinfin_90")
    try:
        hel = doc_tmp.addObject("Part::Helix", "Helix")
        hel.Pitch = paso
        hel.Height = paso
        hel.Radius = r_afuera

        pts = [
            App.Vector(r_raiz,   0.0, -media_valle_raiz),
            App.Vector(r_afuera, 0.0, -media_valle_out),
            App.Vector(r_afuera, 0.0,  media_valle_out),
            App.Vector(r_raiz,   0.0,  media_valle_raiz),
            App.Vector(r_raiz,   0.0, -media_valle_raiz),
        ]
        perf = doc_tmp.addObject("Part::Feature", "Perfil")
        perf.Shape = Part.makePolygon(pts)
        sw = doc_tmp.addObject("Part::Sweep", "Sweep")
        sw.Sections = [perf]
        sw.Spine = (hel, [])
        sw.Solid = True
        sw.Frenet = True
        doc_tmp.recompute()
        vuelta = sw.Shape.copy()
    finally:
        App.closeDocument("_tmp_sinfin_90")

    # Recortar las vueltas solo dentro de la zona roscada (z_ini .. z_fin)
    anillo_zona = Part.makeCylinder(r_afuera + 0.5, z_fin - z_ini, App.Vector(0.0, 0.0, z_ini))
    n_vueltas = int((z_fin - z_ini) / paso) + 3
    vueltas = []
    for k in range(-1, n_vueltas):
        v = vuelta.copy()
        v.translate(App.Vector(0.0, 0.0, z_ini + k * paso))
        vueltas.append(v.common(anillo_zona))

    cuerpo_roscado = cuerpo.cut(vueltas)

    # 3. Taladro axial de acople con Transmisor B + agujero pasador transversal (eje Y)
    tal_eje = Part.makeCylinder(r_eje, p_eje, App.Vector(0.0, 0.0, 0.0))
    tal_pas = Part.makeCylinder(
        r_pas,
        2.0 * r_ext + 2.0,
        App.Vector(0.0, -(r_ext + 1.0), z_pas),
        App.Vector(0.0, 1.0, 0.0),
    )
    final_shape = cuerpo_roscado.cut(tal_eje).cut(tal_pas)
    if float(ss.get("mej_estabilizador_fdm")) >= 0.5:
        final_shape = _agregar_costillas_estabilizadoras(final_shape, r_ext)

    feat_name = "Tornillo_Sin_Fin_14_3D_Impresion_Solido" if MODO_ESTABILIZADOR else "Tornillo_Sin_Fin_14_3D_Solido"
    feat = pz_obj.nuevo("Part::Feature", feat_name)
    feat.Shape = final_shape
    return feat


solido = _crear_sinfin(pz)

# --- Conectores LCS compatibles con el ensamblaje 3D
pz.lcs("LCS_Origen")
pz.lcs("LCS_Centro", z=f"{pz.p('l_total')} / 2")
pz.lcs("LCS_Cara_Sup", z=pz.p("l_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
print(f"Generado con éxito: {SALIDA}")
