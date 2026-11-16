# Tuerca Hexagonal Impresa 3D para Guía 3D (Escala 75.5%, rosca triangular FDM)
# Ejecución: /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_tuerca_guia_08_3d.py
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

MODO_DISENO = 1          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render
SALIDA = os.path.join(AQUI, "Tuerca_Guia_08_3D.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_rosca_base", "Ø mayor base rosca guía en CAD",     "6.71 mm",  "H", None, "calculado"),
    ("paso_rosca",   "Paso rosca triangular FDM",          "1.25 mm",  "N", None, "usuario"),
    ("prof_rosca",   "Profundidad radial filete triangular", "0.62 mm","N", None, "calculado"),
    ("s_hex",        "Distancia entre caras hexágono",     "13.00 mm", "L", None, "calculado"),
    ("h_tuerca",     "Altura total de la tuerca",          "6.00 mm",  "L", None, "calculado"),
    ("c_ext",        "Chaflán exterior caras hexágono",    "0.60 mm",  "L", None, "calculado"),
    ("c_int",        "Chaflán entrada rosca en ambas caras","0.60 mm", "L", None, "calculado"),
]

MAT_PLA = {
    "nombre": "PLA+ / PETG (Impresión 3D)",
    "densidad_num": "0.00000124",
    "densidad_desc": "1.24 g / cm^3 (kg / mm^3)",
    "color": (0.20, 0.45, 0.78),
    "transparencia": 0,
}

pz = Pieza("Tuerca_Guia_08_3D")
# Calibrada según medición real: contracción agujero = -0.55 mm en Ø, guía = +0.15 mm en Ø.
# Con holgura_fdm = 0.50 mm (+1.00 mm en Ø): Ø mayor CAD = 7.71 mm -> impreso ~7.16 mm (~0.30 mm juego sobre Ø6.86)
pz.parametros(DIMS, modo=MODO_DISENO, escala="1.0", holgura_fdm="0.50 mm")
pz.materiales(MAT_PLA, origen="usuario")
p = pz.p


def _crear_tuerca_roscada(pz_obj):
    """Genera el cuerpo hexagonal biselado con rosca interior triangular imprimible."""
    ss = pz_obj.hoja
    d_mayor = float(ss.get("d_rosca_base").Value)
    paso = float(ss.get("paso_rosca").Value)
    prof = float(ss.get("prof_rosca").Value)
    s_hex = float(ss.get("s_hex").Value)
    h_tot = float(ss.get("h_tuerca").Value)
    c_ext = float(ss.get("c_ext").Value)
    c_int = float(ss.get("c_int").Value)

    r_fondo = d_mayor / 2.0
    r_cresta = r_fondo - prof
    r_hex = (s_hex / 2.0) / math.cos(math.radians(30.0))

    # 1. Prisma hexagonal + bisel de revolución en ambas caras (sin índices de arista)
    pts_hex = [
        App.Vector(r_hex * math.cos(math.radians(60 * k)),
                   r_hex * math.sin(math.radians(60 * k)),
                   0.0)
        for k in range(7)
    ]
    cara_hex = Part.Face(Part.makePolygon(pts_hex))
    prisma = cara_hex.extrude(App.Vector(0.0, 0.0, h_tot))

    r_apotema = s_hex / 2.0
    r_env = r_hex + 0.5
    cono_inf = Part.makeCone(r_apotema, r_env, c_ext, App.Vector(0.0, 0.0, 0.0))
    cil_med = Part.makeCylinder(r_env, h_tot - 2.0 * c_ext, App.Vector(0.0, 0.0, c_ext))
    cono_sup = Part.makeCone(r_env, r_apotema, c_ext, App.Vector(0.0, 0.0, h_tot - c_ext))
    env_hex = cono_inf.fuse(cil_med).fuse(cono_sup)
    cuerpo = prisma.common(env_hex)

    # 2. Agujero pasante a diámetro menor + avellanados de entrada en ambas caras
    agujero = Part.makeCylinder(r_cresta, h_tot, App.Vector(0.0, 0.0, 0.0))
    av_inf = Part.makeCone(r_fondo + 0.15, r_cresta, c_int, App.Vector(0.0, 0.0, 0.0))
    av_sup = Part.makeCone(r_cresta, r_fondo + 0.15, c_int, App.Vector(0.0, 0.0, h_tot - c_int))
    vaciado_centro = agujero.fuse(av_inf).fuse(av_sup)
    cuerpo_perf = cuerpo.cut(vaciado_centro)

    # 3. Tallado de rosca interior vuelta por vuelta (Part::Helix + Part::Sweep en doc temporal)
    # Perfil coincidente con Guia_08_3D (mismo paso 1.25 mm y flanco ~52°):
    # - fondo en r_fondo (3.855 mm) con ancho 0.52 mm para alojar la cresta de la guía (0.49 mm)
    # - entrada en r_cresta (3.235 mm) con ancho 1.08 mm (cresta interior de tuerca 0.17 mm)
    r_solape = r_cresta - 0.12
    media_fondo = 0.26
    media_entrada = 0.54
    pend = (media_entrada - media_fondo) / (r_fondo - r_cresta)
    media_solape = media_entrada + pend * (r_cresta - r_solape)
    doc_tmp = App.newDocument("_tmp_rosca_tuerca")
    try:
        hel = doc_tmp.addObject("Part::Helix", "Helix")
        hel.Pitch = paso
        hel.Height = paso
        hel.Radius = r_fondo

        pts_rosca = [
            App.Vector(r_solape, 0.0, -media_solape),
            App.Vector(r_fondo,  0.0, -media_fondo),
            App.Vector(r_fondo,  0.0,  media_fondo),
            App.Vector(r_solape, 0.0,  media_solape),
            App.Vector(r_solape, 0.0, -media_solape),
        ]
        perf = doc_tmp.addObject("Part::Feature", "Perfil")
        perf.Shape = Part.makePolygon(pts_rosca)
        sw = doc_tmp.addObject("Part::Sweep", "Sweep")
        sw.Sections = [perf]
        sw.Spine = (hel, [])
        sw.Solid = True
        sw.Frenet = True
        doc_tmp.recompute()
        vuelta = sw.Shape.copy()
    finally:
        App.closeDocument("_tmp_rosca_tuerca")

    env_rosca = Part.makeCylinder(r_fondo + 0.35, h_tot, App.Vector(0.0, 0.0, 0.0))
    n_vueltas = int(h_tot / paso) + 2
    vueltas = []
    for k in range(-1, n_vueltas):
        v = vuelta.copy()
        v.translate(App.Vector(0.0, 0.0, k * paso))
        v_clip = v.common(env_rosca)
        if v_clip.Volume > 1e-6:
            vueltas.append(v_clip)

    tuerca_final = cuerpo_perf.cut(vueltas).common(
        Part.makeCylinder(r_hex + 0.5, h_tot, App.Vector(0.0, 0.0, 0.0))
    )
    feat = pz_obj.nuevo("Part::Feature", "Tuerca_Guia_08_3D_Solido")
    feat.Shape = tuerca_final
    return feat


solido = _crear_tuerca_roscada(pz)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Centro", z=f"{p('h_tuerca')} / 2")
pz.lcs("LCS_Cara_Sup", z=p("h_tuerca"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
print(f"Generado con éxito: {SALIDA}")
