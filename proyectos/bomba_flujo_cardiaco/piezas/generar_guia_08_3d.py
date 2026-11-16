# Guía 3D (Escala 75.5%) - Plano Nº 8 (bomba de simulación de flujo cardíaco)
# Parametrizada para acoplar entre Tapa_Interior_16b_3D y Tapa_Exterior_16a_3D (alojamiento Face22).
# Ejecución: /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_guia_08_3d.py
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

MODO_DISENO = 1          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render
SALIDA = os.path.join(AQUI, "Guia_08_3D.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_total",   "Longitud total de la guía 3D",       "220.65 mm", "L", None, "calculado"),
    ("l_espiga",  "Longitud total espiga rebajada",     "22.65 mm",  "L", None, "plano"),
    ("l_rosca",   "Longitud roscada M10x1.5 a escala",  "9.82 mm",   "L", None, "plano"),
    ("d_cuerpo",  "Diámetro cuerpo guía (Ø12*0.755)",   "9.06 mm",   "S", None, "plano"),
    ("d_espiga",  "Diámetro espiga lisa (Ø10*0.755)",   "7.55 mm",   "S", None, "plano"),
    ("d_m10",     "Rosca exterior M10 a escala (con holgura FDM)", "7.55 mm", "S", "7.55 mm", "usuario"),
    ("paso_m10",  "Paso rosca triangular FDM",          "1.25 mm",   "N", None, "usuario"),
    ("prof_rosca","Profundidad radial filete triangular", "0.62 mm", "N", None, "calculado"),
    ("c_izq",     "Chaflán extremo roscado",            "0.76 mm",   "L", None, "plano"),
    ("c_escalon", "Chaflán escalón Ø7.55-Ø9.06",        "0.38 mm",   "L", None, "plano"),
    ("c_der",     "Chaflán extremo derecho",            "0.76 mm",   "L", None, "plano"),
]

pz = Pieza("Guia_08_3D")
# Calibrada según medición real: hueco tapa impreso = 7.00 mm, guía sin holgura = 7.70 mm (+0.15 mm)
# Con holgura_fdm = 0.42 mm (0.84 mm en Ø): Ø CAD = 6.71 mm -> impreso ~6.86 mm (~0.14 mm juego en Ø7.00)
pz.parametros(DIMS, modo=MODO_DISENO, escala="1.0", holgura_fdm="0.42 mm")
pz.materiales("AISI_304")
p = pz.p

r_m10 = f"({p('d_m10')} / 2)"
r_esp = f"({p('d_espiga')} / 2)"
r_cue = f"({p('d_cuerpo')} / 2)"


def _crear_tramo_roscado_triangular(pz_obj):
    """Genera el tramo roscado exterior macizo tallando vuelta por vuelta el valle triangular."""
    ss = pz_obj.hoja
    r_ext = float(ss.get("d_m10").Value) / 2.0
    paso = float(ss.get("paso_m10").Value)
    prof = float(ss.get("prof_rosca").Value)
    l_ros = float(ss.get("l_rosca").Value)
    c_in = float(ss.get("c_izq").Value)

    r_raiz = r_ext - prof
    r_afuera = r_ext + 0.30

    # Cilindro macizo con chaflán de entrada de 45° en la punta
    cono_in = Part.makeCone(max(0.5, r_ext - c_in), r_ext, c_in, App.Vector(0.0, 0.0, 0.0))
    cil_env = Part.makeCylinder(r_ext, l_ros - c_in, App.Vector(0.0, 0.0, c_in))
    cuerpo = cono_in.fuse(cil_env)

    # Una vuelta de valle triangular (Part::Helix + Part::Sweep en doc temporal para evitar distorsión OCCT)
    doc_tmp = App.newDocument("_tmp_rosca_guia")
    try:
        hel = doc_tmp.addObject("Part::Helix", "Helix")
        hel.Pitch = paso
        hel.Height = paso
        hel.Radius = r_afuera

        media_valle_ext = 0.42 * paso
        media_valle_int = 0.08
        pts = [
            App.Vector(r_raiz,   0.0, -media_valle_int),
            App.Vector(r_afuera, 0.0, -media_valle_ext),
            App.Vector(r_afuera, 0.0,  media_valle_ext),
            App.Vector(r_raiz,   0.0,  media_valle_int),
            App.Vector(r_raiz,   0.0, -media_valle_int),
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
        App.closeDocument("_tmp_rosca_guia")

    env_rosca = Part.makeCylinder(r_ext + 0.35, l_ros, App.Vector(0.0, 0.0, 0.0))
    n_vueltas = int(l_ros / paso) + 2
    vueltas = []
    for k in range(-1, n_vueltas):
        v = vuelta.copy()
        v.translate(App.Vector(0.0, 0.0, k * paso))
        v_clip = v.common(env_rosca)
        if v_clip.Volume > 1e-6:
            vueltas.append(v_clip)

    rosca_final = cuerpo.cut(vueltas).common(Part.makeCylinder(r_ext + 0.05, l_ros, App.Vector(0.0, 0.0, 0.0)))
    feat = pz_obj.nuevo("Part::Feature", "Tramo_Rosca_M10")
    feat.Shape = rosca_final
    feat.Visibility = False
    return feat


# --- Tramos axiales de revolución sin índices de arista + rosca triangular 3D
tramo_rosca = _crear_tramo_roscado_triangular(pz)
cil_espiga = pz.cil("Tramo_Espiga_10", r_esp, f"{p('l_espiga')} - {p('l_rosca')}", z=p("l_rosca"))
ch_esc = pz.cono("Chaflan_Escalon", f"{r_cue} - {p('c_escalon')}", r_cue, p("c_escalon"),
                 z=p("l_espiga"))
cil_cuerpo = pz.cil("Cuerpo_Guia_12", r_cue,
                    f"{p('l_total')} - {p('l_espiga')} - {p('c_escalon')} - {p('c_der')}",
                    z=f"{p('l_espiga')} + {p('c_escalon')}")
ch_der = pz.cono("Chaflan_Der", r_cue, f"{r_cue} - {p('c_der')}", p("c_der"),
                 z=f"{p('l_total')} - {p('c_der')}")

solido = pz.fusion("Guia_08_3D_Solido", [tramo_rosca, cil_espiga, ch_esc, cil_cuerpo, ch_der])

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Fin_Rosca_M10", z=p("l_rosca"))
pz.lcs("LCS_Hombro_Asiento", z=p("l_espiga"))
pz.lcs("LCS_Centro", z=f"{p('l_total')} / 2")
pz.lcs("LCS_Cara_Sup", z=p("l_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
print(f"Generado con éxito: {SALIDA}")
