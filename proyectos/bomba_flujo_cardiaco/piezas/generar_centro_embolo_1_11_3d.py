# Centro de Émbolo 1 3D (Escala 75.5%) - Tuerca roscada trapezoidal 90° FDM (p = 3.00 mm)
# Ejecución: /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_centro_embolo_1_11_3d.py
import math
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
SALIDA = os.path.join(AQUI, "Centro_Embolo_1_11_3D.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("h_total",      "Altura total cuerpo + brida",                          "18.72 mm", "L", None, "plano"),
    ("h_brida",      "Espesor de la brida de asiento",                       "3.78 mm",  "L", None, "plano"),
    ("d_brida",      "Diámetro exterior de brida",                           "33.98 mm", "L", None, "plano"),
    ("d_cuello",     "Diámetro cuello FDM libre p/ émbolo Ø22,65 impreso",   "21.75 mm", "L", None, "usuario"),
    ("c_borde",      "Chaflán exterior en aristas de brida y cuello",        "0.38 mm",  "L", None, "plano"),
    ("d_corona_m3",  "Diámetro corona 4 tornillos brida",                    "28.32 mm", "L", None, "plano"),
    ("d_aguj_m3",    "Diámetro 4 aguj. pasantes brida (comp. FDM M2,5)",     "3.24 mm",  "L", None, "usuario"),
    ("d_avell_m3",   "Diámetro cajeado inf. cabeza M2,5 (comp. FDM)",        "5.43 mm",  "L", None, "usuario"),
    ("p_avell_m3",   "Profundidad cajeado inferior brida",                   "0.94 mm",  "L", None, "plano"),
    ("d_corona_m25", "Diámetro corona 3 agujeros ciegos sup. 120°",          "15.86 mm", "L", None, "plano"),
    ("d_aguj_m25",   "Diámetro 3 aguj. ciegos M2,5 sup. (comp. FDM)",        "2.20 mm",  "L", None, "usuario"),
    ("p_aguj_m25",   "Profundidad 3 agujeros ciegos sup. M2,5",              "6.00 mm",  "L", None, "usuario"),
    ("d_rosca_base", "Ø mayor base sinfín en CAD (10.50 + 2x0.45 = 11.40)",  "10.50 mm", "H", None, "usuario"),
    ("paso",         "Paso rosca trapezoidal 90° (Opción A2)",               "3.00 mm",  "N", None, "usuario"),
    ("h_diente",     "Profundidad radial filete 45° FDM",                    "0.85 mm",  "N", None, "calculado"),
    ("b_fondo",      "Ancho plano fondo surco (mayor a 0.60 mm)",            "0.90 mm",  "N", None, "calculado"),
    ("c_entrada",    "Chaflán entrada rosca 45° en ambas caras",             "1.20 mm",  "L", None, "calculado"),
]

MAT_PLA = {
    "nombre": "PLA+ / PETG (Impresión 3D)",
    "densidad_num": "0.00000124",
    "densidad_desc": "1.24 g / cm^3 (kg / mm^3)",
    "color": (0.20, 0.55, 0.45),
    "transparencia": 0,
}

pz = Pieza("Centro_Embolo_1_11_3D")
# Calibrada con desvío real medido: exterior +0.15 mm Ø, agujero -0.55 mm Ø.
# Con holgura_fdm = 0.45 mm (+0.90 mm en Ø): Ø fondo CAD = 11.40 mm -> impreso ~10.85 mm (~0.20 mm juego sobre Ø10.65)
pz.parametros(DIMS, modo=MODO_DISENO, escala="1.0", holgura_fdm="0.45 mm")
pz.materiales(MAT_PLA, origen="usuario")


def _crear_centro_embolo_roscado(pz_obj):
    """Genera Centro_Embolo_1_11_3D macizo con rosca pasante 90° FDM en toda la longitud."""
    ss = pz_obj.hoja
    h_tot = float(ss.get("h_total").Value)
    h_bri = float(ss.get("h_brida").Value)
    r_bri = float(ss.get("d_brida").Value) / 2.0
    r_cue = float(ss.get("d_cuello").Value) / 2.0
    c_ext = float(ss.get("c_borde").Value)
    r_cor = float(ss.get("d_corona_m3").Value) / 2.0
    r_m3 = float(ss.get("d_aguj_m3").Value) / 2.0
    r_ave = float(ss.get("d_avell_m3").Value) / 2.0
    p_ave = float(ss.get("p_avell_m3").Value)
    r_cor_m25 = float(ss.get("d_corona_m25").Value) / 2.0
    r_m25 = float(ss.get("d_aguj_m25").Value) / 2.0
    p_m25 = float(ss.get("p_aguj_m25").Value)

    r_fondo = float(ss.get("d_rosca_base").Value) / 2.0
    paso = float(ss.get("paso").Value)
    h1 = float(ss.get("h_diente").Value)
    b_f = float(ss.get("b_fondo").Value)
    c_in = float(ss.get("c_entrada").Value)
    r_cresta = r_fondo - h1

    # 1. Cuerpo exterior con chaflanes de revolución
    ch_inf = Part.makeCone(r_bri - c_ext, r_bri, c_ext, App.Vector(0.0, 0.0, 0.0))
    cil_bri = Part.makeCylinder(r_bri, h_bri - 2.0 * c_ext, App.Vector(0.0, 0.0, c_ext))
    ch_bri_sup = Part.makeCone(r_bri, r_bri - c_ext, c_ext, App.Vector(0.0, 0.0, h_bri - c_ext))
    cil_cue = Part.makeCylinder(r_cue, h_tot - h_bri - c_ext, App.Vector(0.0, 0.0, h_bri))
    ch_cue_sup = Part.makeCone(r_cue, r_cue - c_ext, c_ext, App.Vector(0.0, 0.0, h_tot - c_ext))
    cuerpo = ch_inf.fuse(cil_bri).fuse(ch_bri_sup).fuse(cil_cue).fuse(ch_cue_sup)

    # 2. Agujero pasante a diámetro menor + chaflanes de entrada 45° en ambas caras
    agujero = Part.makeCylinder(r_cresta, h_tot, App.Vector(0.0, 0.0, 0.0))
    av_inf = Part.makeCone(r_fondo + 0.25, r_cresta, c_in, App.Vector(0.0, 0.0, 0.0))
    av_sup = Part.makeCone(r_cresta, r_fondo + 0.25, c_in, App.Vector(0.0, 0.0, h_tot - c_in))
    cuerpo_perf = cuerpo.cut(agujero.fuse(av_inf).fuse(av_sup))

    # 3. 4 agujeros de fijación en la brida con avellanado inferior
    for hx, hy in ((r_cor, 0.0), (-r_cor, 0.0), (0.0, r_cor), (0.0, -r_cor)):
        pas = Part.makeCylinder(r_m3, h_bri + 0.2, App.Vector(hx, hy, -0.1))
        ave = Part.makeCylinder(r_ave, p_ave + 0.1, App.Vector(hx, hy, -0.1))
        cuerpo_perf = cuerpo_perf.cut(pas).cut(ave)

    # 3b. 3 agujeros ciegos M2,5 a 120° en la cara frontal del cuello (90°, 210°, 330° coincidiendo con CE2)
    for ang_deg in (90.0, 210.0, 330.0):
        hx = r_cor_m25 * math.cos(math.radians(ang_deg))
        hy = r_cor_m25 * math.sin(math.radians(ang_deg))
        cuerpo_perf = cuerpo_perf.cut(
            Part.makeCylinder(r_m25, p_m25 + 0.1, App.Vector(hx, hy, h_tot - p_m25))
        )

    # 4. Rosca interior trapezoidal 90° (45° FDM) pasante en toda la longitud
    r_solape = r_cresta - 0.15
    media_fondo = b_f / 2.0
    media_entrada = media_fondo + h1
    media_solape = media_entrada + (r_cresta - r_solape)

    doc_tmp = App.newDocument("_tmp_centro1_90")
    try:
        hel = doc_tmp.addObject("Part::Helix", "Helix")
        hel.Pitch = paso
        hel.Height = paso
        hel.Radius = r_fondo

        pts = [
            App.Vector(r_solape, 0.0, -media_solape),
            App.Vector(r_fondo,  0.0, -media_fondo),
            App.Vector(r_fondo,  0.0,  media_fondo),
            App.Vector(r_solape, 0.0,  media_solape),
            App.Vector(r_solape, 0.0, -media_solape),
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
        App.closeDocument("_tmp_centro1_90")

    env_rosca = Part.makeCylinder(r_fondo + 0.5, h_tot, App.Vector(0.0, 0.0, 0.0))
    n_vueltas = int(h_tot / paso) + 2
    vueltas = []
    for k in range(-1, n_vueltas):
        v = vuelta.copy()
        v.translate(App.Vector(0.0, 0.0, k * paso))
        v_clip = v.common(env_rosca)
        if v_clip.Volume > 1e-6:
            vueltas.append(v_clip)

    final_shape = cuerpo_perf.cut(vueltas).removeSplitter()
    feat = pz_obj.nuevo("Part::Feature", "Centro_Embolo_1_11_3D_Solido")
    feat.Shape = final_shape
    return feat


solido = _crear_centro_embolo_roscado(pz)

# --- Conectores LCS compatibles con el ensamblaje 3D
pz.lcs("LCS_Origen")
pz.lcs("LCS_Centro", z=f"{pz.p('h_total')} / 2")
pz.lcs("LCS_Cara_Sup", z=pz.p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
print(f"Generado con éxito: {SALIDA}")
