"""Rodamiento rígido de bolas SKF 609 (9x24x7 mm, DIN 625-1 / ISO 15).

Modela la geometría comercial detallada del rodamiento SKF 609:
- Aro exterior (D = 24.00 mm, D1 = 20.40 mm) con chaflanes normativos, pista toroidal
  y ranuras laterales de fijación de placas (D2 = 21.20 mm).
- Aro interior (d = 9.00 mm, d1 = 12.60 mm) con chaflanes normativos y pista toroidal.
- 7 bolas de acero (Dw = 4.00 mm) sobre el diámetro primitivo Dpw = 16.50 mm.
- Jaula separadora anular centrada en las bolas.
"""
import math
import os
import shutil
import sys

RUTA_SCRIPT = os.path.abspath(globals().get("__file__", "generar_rodamiento_skf_609.py"))
DIR_PIEZAS = os.path.dirname(RUTA_SCRIPT)
DIR_PROYECTO = os.path.dirname(DIR_PIEZAS)
RAIZ_REPO = os.path.dirname(os.path.dirname(DIR_PROYECTO))
sys.path.insert(0, os.path.join(RAIZ_REPO, "_herramientas"))

import FreeCAD as App  # noqa: E402
from fc_helpers import Pieza  # noqa: E402

SALIDA = os.path.join(DIR_PIEZAS, "Elementos_comericales", "Rodamiento_SKF_609.FCStd")
SALIDA_CATALOGO = os.path.join(RAIZ_REPO, "02_Catalogos_SKF_DIN_ISO", "Rodamientos", "Rodamiento_SKF_609.FCStd")

# Mantenemos los alias originales (d_int, d_ext, ancho) y sumamos la geometría comercial SKF 609
DIMS = [
    ("d_int",       "Diámetro interior nominal d (SKF 609 / DIN 625-1)", "9.00 mm",  "H", "", "norma"),
    ("d_ext",       "Diámetro exterior nominal D (SKF 609 / DIN 625-1)", "24.00 mm", "S", "", "norma"),
    ("ancho",       "Ancho axial nominal B (SKF 609 / DIN 625-1)",       "7.00 mm",  "L", "", "norma"),
    ("d_hombro_int","Diámetro hombro del aro interior d1 (SKF 609)",     "12.60 mm", "L", "", "norma"),
    ("d_hombro_ext","Diámetro hombro del aro exterior D1 (SKF 609)",     "20.40 mm", "L", "", "norma"),
    ("d_rebaje_ext","Diámetro rebaje lateral de obturación D2",          "21.20 mm", "L", "", "norma"),
    ("p_rebaje",    "Profundidad axial rebaje lateral en aro exterior",  "0.75 mm",  "L", "", "norma"),
    ("d_paso_bolas","Diámetro primitivo del círculo de bolas Dpw",       "16.50 mm", "L", "", "norma"),
    ("d_bola",      "Diámetro de bola Dw (5/32 in)",                     "4.00 mm",  "L", "", "norma"),
    ("c_aro",       "Chaflán de montaje en aristas r1,2 (DIN 625-1)",    "0.35 mm",  "L", "", "norma"),
    ("e_jaula",     "Espesor axial de la jaula separadora",              "1.50 mm",  "L", "", "norma"),
]

MAT_ACERO_ROD = {
    "nombre": "Acero al Cromo SAE 52100 / 100Cr6 (SKF)",
    "densidad_num": "0.00000785",
    "densidad_desc": "7.85 g / cm^3 (kg / mm^3)",
    "color": (0.76, 0.78, 0.82),
    "transparencia": 0,
}

os.environ["FORZAR"] = "1"
pz = Pieza("Rodamiento_SKF_609", ruta_salida=SALIDA, ruta_script=RUTA_SCRIPT)
pz.parametros(DIMS, modo=1, escala="1.0", holgura_fdm="0.00 mm")
pz.materiales(MAT_ACERO_ROD, origen="norma")
p = pz.p

r_int = f"{p('d_int')} / 2"
r_ext = f"{p('d_ext')} / 2"
b = p("ancho")
r_d1 = f"{p('d_hombro_int')} / 2"
r_D1 = f"{p('d_hombro_ext')} / 2"
r_D2 = f"{p('d_rebaje_ext')} / 2"
p_reb = p("p_rebaje")
r_pw = f"{p('d_paso_bolas')} / 2"
r_bola = f"{p('d_bola')} / 2"
c = p("c_aro")
z_mid = f"{b} / 2"

# 1. Aro Exterior (entre D1 y D, con chaflanes exteriores y rebajes laterales D2)
ae_inf = pz.cono("AroExt_Ch_Inf", f"{r_ext} - {c}", r_ext, c, z="0 mm")
ae_cil = pz.cil("AroExt_Cil", r_ext, f"{b} - 2 * {c}", z=c)
ae_sup = pz.cono("AroExt_Ch_Sup", r_ext, f"{r_ext} - {c}", c, z=f"{b} - {c}")
ae_bruto = pz.fusion("AroExt_Bruto", [ae_inf, ae_cil, ae_sup])

hueco_ae = pz.cil("Hueco_AroExt", r_D1, f"{b} + 2 mm", z="-1 mm")
reb_ae_inf = pz.cil("Rebaje_AroExt_Inf", r_D2, f"{p_reb} + 0.5 mm", z="-0.5 mm")
reb_ae_sup = pz.cil("Rebaje_AroExt_Sup", r_D2, f"{p_reb} + 0.5 mm", z=f"{b} - {p_reb}")
vaciado_ae = pz.fusion("Vaciado_AroExt", [hueco_ae, reb_ae_inf, reb_ae_sup])
aro_exterior = pz.corte("Aro_Exterior", ae_bruto, vaciado_ae)

# 2. Aro Interior (macizo hasta d1 con chaflanes exteriores; el agujero d se corta al final)
ai_inf = pz.cono("AroInt_Ch_Inf", f"{r_d1} - {c}", r_d1, c, z="0 mm")
ai_cil = pz.cil("AroInt_Cil", r_d1, f"{b} - 2 * {c}", z=c)
ai_sup = pz.cono("AroInt_Ch_Sup", r_d1, f"{r_d1} - {c}", c, z=f"{b} - {c}")
aro_interior = pz.fusion("Aro_Interior", [ai_inf, ai_cil, ai_sup])

# 3. Jaula separadora anular en el círculo primitivo (entre r_pw - 0.55 mm y r_pw + 0.55 mm)
j_ext = pz.cil(
    "Jaula_Ext",
    f"{r_pw} + 0.55 mm",
    p("e_jaula"),
    z=f"{z_mid} - {p('e_jaula')} / 2",
)
j_int = pz.cil(
    "Jaula_Int",
    f"{r_pw} - 0.55 mm",
    f"{p('e_jaula')} + 1 mm",
    z=f"{z_mid} - {p('e_jaula')} / 2 - 0.5 mm",
)
jaula = pz.corte("Jaula_Separadora", j_ext, j_int)

# 4. 7 Bolas esféricas (Part::Sphere) equiespaciadas en el diámetro primitivo Dpw
# Polos truncados a +-82° y costura rotada 90° tangencialmente para evitar singularidades UV en OCCT/Coin3D
N_BOLAS = 7
bolas = []
for i in range(N_BOLAS):
    ang_deg = 360.0 * i / N_BOLAS
    ang_rad = 2.0 * math.pi * i / N_BOLAS
    cos_a = f"{math.cos(ang_rad):.6f}"
    sin_a = f"{math.sin(ang_rad):.6f}"
    esf = pz.nuevo("Part::Sphere", f"Bola_{i + 1}")
    esf.setExpression("Radius", r_bola)
    esf.Angle1 = -82.0
    esf.Angle2 = 82.0
    esf.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), ang_deg + 90.0)
    esf.setExpression(".Placement.Base.x", f"{r_pw} * ({cos_a})")
    esf.setExpression(".Placement.Base.y", f"{r_pw} * ({sin_a})")
    esf.setExpression(".Placement.Base.z", z_mid)
    pz.auxiliares.append(esf)
    bolas.append(esf)

# 5. Unión de Aro Exterior + Aro Interior + Jaula + 7 Bolas (Refine=False evita singularidades en esferas)
conjunto_bruto = pz.fusion(
    "Conjunto_Rodamiento_Bruto",
    [aro_exterior, aro_interior, jaula] + bolas,
)
conjunto_bruto.Refine = False

# 6. Agujero central d = 9.00 mm con chaflanes de entrada a 45° en ambas caras del aro interior
aguj_central = pz.cil("Agujero_Eje", r_int, f"{b} + 2 mm", z="-1 mm")
ch_int_inf = pz.cono(
    "Chaflan_Int_Inf",
    f"{r_int} + {c} + 0.5 mm",
    r_int,
    f"{c} + 0.5 mm",
    z="-0.5 mm",
)
ch_int_sup = pz.cono(
    "Chaflan_Int_Sup",
    r_int,
    f"{r_int} + {c} + 0.5 mm",
    f"{c} + 0.5 mm",
    z=f"{b} - {c}",
)
herr_agujero = pz.fusion("Herramienta_Agujero_Eje", [aguj_central, ch_int_inf, ch_int_sup])

solido = pz.corte("Rodamiento_SKF_609_Solido", conjunto_bruto, herr_agujero)
solido.Refine = False

pz.lcs("LCS_Origen", z="0 mm")
pz.lcs("LCS_Cara_Sup", z=b)

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)

if os.path.isdir(os.path.dirname(SALIDA_CATALOGO)):
    shutil.copy2(SALIDA, SALIDA_CATALOGO)
    print("Actualizado catálogo:", SALIDA_CATALOGO)
