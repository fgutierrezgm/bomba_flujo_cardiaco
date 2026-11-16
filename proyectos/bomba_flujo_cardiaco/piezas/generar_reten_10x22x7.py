"""Retén radial de eje 10x22x7 mm (DIN 3760 AS / ISO 6194, doble labio con resorte toroidal).

Modela la geometría comercial completa de un retén elastomerizado tipo AS / TC:
- Carcasa exterior Ø22.00 x 7.00 mm con chaflanes de entrada DIN 3760 (0.50 mm x 45°).
- Cara frontal cerrada (z=0) con ranura anular de moldeo y labio guardapolvo secundario.
- Cavidad posterior abierta profunda (z=2.0..7.0 mm) entre la pared armada exterior y el labio.
- Labio principal de sellado en perfil en V (Ø10.00 mm) con alivio inter-labios.
- Resorte helicoidal toroidal (garter spring) alojado en el asiento dorsal del labio.
"""
import os
import shutil
import sys

RUTA_SCRIPT = os.path.abspath(globals().get("__file__", "generar_reten_10x22x7.py"))
DIR_PIEZAS = os.path.dirname(RUTA_SCRIPT)
DIR_PROYECTO = os.path.dirname(DIR_PIEZAS)
RAIZ_REPO = os.path.dirname(os.path.dirname(DIR_PROYECTO))
sys.path.insert(0, os.path.join(RAIZ_REPO, "_herramientas"))

import FreeCAD as App  # noqa: E402
from fc_helpers import Pieza  # noqa: E402

SALIDA = os.path.join(DIR_PIEZAS, "Elementos_comericales", "Reten_10x22x7.FCStd")
SALIDA_CATALOGO = os.path.join(RAIZ_REPO, "02_Catalogos_SKF_DIN_ISO", "Retenes_DIN_3760", "Reten_10x22x7.FCStd")

# Mantenemos los alias originales (d_int, d_ext, ancho) y sumamos el detalle geométrico comercial
DIMS = [
    ("d_int",        "Diámetro nominal de eje d1 (DIN 3760 AS)",             "10.00 mm", "H", "", "norma"),
    ("d_ext",        "Diámetro exterior nominal d2 (DIN 3760 AS)",           "22.00 mm", "S", "", "norma"),
    ("ancho",        "Ancho axial nominal b (DIN 3760 AS)",                  "7.00 mm",  "L", "", "norma"),
    ("c_ext",        "Chaflán exterior de entrada DIN 3760",                 "0.50 mm",  "L", "", "norma"),
    ("d_cav_ext",    "Diámetro exterior de la cavidad del resorte",          "19.00 mm", "L", "", "norma"),
    ("d_cav_int",    "Diámetro exterior del dorso del labio principal",      "13.60 mm", "L", "", "norma"),
    ("p_cav",        "Profundidad axial de la cavidad interior",             "5.00 mm",  "L", "", "norma"),
    ("d_resorte",    "Diámetro medio del resorte toroidal (garter spring)",  "13.50 mm", "L", "", "norma"),
    ("d_alambre",    "Diámetro de sección del resorte toroidal",             "1.30 mm",  "L", "", "norma"),
    ("d_ran_ext",    "Diámetro exterior ranura frontal de moldeo",           "18.60 mm", "L", "", "norma"),
    ("d_ran_int",    "Diámetro interior ranura frontal de moldeo",           "14.80 mm", "L", "", "norma"),
    ("p_ran_frente", "Profundidad axial ranura frontal de moldeo",           "0.45 mm",  "L", "", "norma"),
]

MAT_RETEN = {
    "nombre": "Elastómero NBR / Viton (FKM)",
    "densidad_num": "0.00000125",
    "densidad_desc": "1.25 g / cm^3 (kg / mm^3)",
    "color": (0.16, 0.17, 0.19),
    "transparencia": 0,
}

os.environ["FORZAR"] = "1"
pz = Pieza("Reten_10x22x7", ruta_salida=SALIDA, ruta_script=RUTA_SCRIPT)
pz.parametros(DIMS, modo=1, escala="1.0", holgura_fdm="0.00 mm")
pz.materiales(MAT_RETEN, origen="norma")
p = pz.p

r_int = f"{p('d_int')} / 2"
r_ext = f"{p('d_ext')} / 2"
b = p("ancho")
c_e = p("c_ext")
r_cext = f"{p('d_cav_ext')} / 2"
r_cint = f"{p('d_cav_int')} / 2"
p_cav = p("p_cav")

# 1. Carcasa exterior cilíndrica con chaflanes de entrada a 45° en ambos extremos
ext_inf = pz.cono("Carcasa_Ch_Inf", f"{r_ext} - {c_e}", r_ext, c_e, z="0 mm")
ext_cil = pz.cil("Carcasa_Cil", r_ext, f"{b} - 2 * {c_e}", z=c_e)
ext_sup = pz.cono("Carcasa_Ch_Sup", r_ext, f"{r_ext} - {c_e}", c_e, z=f"{b} - {c_e}")
carcasa = pz.fusion("Carcasa_Exterior", [ext_inf, ext_cil, ext_sup])

# 2. Cavidad anular posterior profunda (z = b - p_cav .. b) + rebaje de corona del labio
cav_ext = pz.cono(
    "Cav_Cono_Ext",
    f"{r_cext} - 0.35 mm",
    r_cext,
    f"{p_cav} + 0.5 mm",
    z=f"{b} - {p_cav}",
)
cav_int = pz.cono(
    "Cav_Cono_Int",
    f"{r_cint} - 0.30 mm",
    f"{r_cint} + 0.15 mm",
    f"{p_cav} + 1.0 mm",
    z=f"{b} - {p_cav} - 0.2 mm",
)
anillo_cav = pz.corte("Anillo_Cavidad_Principal", cav_ext, cav_int)
reb_corona = pz.cil("Rebaje_Corona_Labio", f"{r_cint} + 0.30 mm", "1.0 mm", z=f"{b} - 0.45 mm")

# 3. Perfil interior de doble labio (labio principal en V a Ø10.00 mm + alivio + labio guardapolvo)
aguj_eje = pz.cil("Agujero_Eje", r_int, f"{b} + 2 mm", z="-1 mm")
cono_labio_sup = pz.cono("Cono_Labio_Principal", r_int, f"{r_cint} - 0.45 mm", "2.10 mm", z=f"{b} - 2.55 mm")
alivio_inf = pz.cono("Alivio_Entre_Labios_Inf", f"{r_int} + 0.15 mm", f"{r_int} + 0.70 mm", "1.10 mm", z="0.90 mm")
alivio_cil = pz.cil("Alivio_Entre_Labios_Cil", f"{r_int} + 0.70 mm", "1.45 mm", z="2.00 mm")
alivio_sup = pz.cono("Alivio_Entre_Labios_Sup", f"{r_int} + 0.70 mm", r_int, "0.85 mm", z="3.45 mm")
ch_guardapolvo = pz.cono("Cono_Guardapolvo_Inf", f"{r_int} + 0.55 mm", f"{r_int} + 0.15 mm", "0.90 mm", z="-0.01 mm")

# 4. Ranura frontal anular de moldeo en la cara cerrada (z = 0)
ran_f_ext = pz.cil("Ranura_Frente_Ext", f"{p('d_ran_ext')} / 2", f"{p('p_ran_frente')} + 0.2 mm", z="-0.2 mm")
ran_f_int = pz.cil("Ranura_Frente_Int", f"{p('d_ran_int')} / 2", f"{p('p_ran_frente')} + 0.6 mm", z="-0.4 mm")
anillo_frente = pz.corte("Anillo_Ranura_Frontal", ran_f_ext, ran_f_int)

# 5. Cuerpo elastomérico vaciado + resorte helicoidal toroidal (garter spring)
vaciado_elast = pz.fusion(
    "Herramienta_Vaciado_Elastomero",
    [anillo_cav, reb_corona, cono_labio_sup, alivio_inf, alivio_cil, alivio_sup, ch_guardapolvo, anillo_frente],
)
cuerpo_elast = pz.corte("Cuerpo_Elastomero", carcasa, vaciado_elast)

toro = pz.nuevo("Part::Torus", "Resorte_Toroidal")
toro.setExpression("Radius1", f"{p('d_resorte')} / 2")
toro.setExpression("Radius2", f"{p('d_alambre')} / 2")
toro.setExpression(".Placement.Base.z", f"{b} - 2.15 mm")
pz.auxiliares.append(toro)

cuerpo_con_resorte = pz.fusion("Cuerpo_Con_Resorte", [cuerpo_elast, toro])

# Sólido final como Part::Cut (preserva el TypeId estándar para vínculos y expresiones)
solido = pz.corte("Reten_10x22x7_Solido", cuerpo_con_resorte, aguj_eje)

pz.lcs("LCS_Origen", z="0 mm")
pz.lcs("LCS_Cara_Sup", z=b)

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)

if os.path.isdir(os.path.dirname(SALIDA_CATALOGO)):
    shutil.copy2(SALIDA, SALIDA_CATALOGO)
    print("Actualizado catálogo:", SALIDA_CATALOGO)
