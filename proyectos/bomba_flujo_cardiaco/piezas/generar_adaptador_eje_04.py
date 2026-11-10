# Adaptador del eje - Plano Nº 4 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_adaptador_eje_04.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Adaptador_Eje_04.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",     "Diámetro exterior del adaptador",          "57.00 mm", "L", None,      "plano"),
    ("d_int",     "Diámetro interior pasante",                "40.10 mm", "H", None,      "plano"),
    ("h_total",   "Altura total del adaptador",               "16.50 mm", "L", None,      "plano"),
    ("d_cor",     "Círculo de agujeros y roscas",             "50.00 mm", "L", None,      "plano"),
    ("d_paso",    "Diámetro 4 agujeros pasantes (0/90/180/270)", "3.10 mm", "H", None,    "plano"),
    ("d_caj",     "Diámetro cajeado agujeros pasantes",       "4.50 mm",  "H", None,      "plano"),
    ("p_caj",     "Profundidad cajeado superior",             "5.00 mm",  "L", None,      "supuesto"),
    ("p_reb_inf", "Profundidad rebaje inferior (.70)",        "0.70 mm",  "L", None,      "plano"),
    ("d_m3",      "Roscas M3x0.5 - 6H (45/135/225/315)",      "3.00 mm",  "R", "2.50 mm", "plano"),
    ("p_m3",      "Profundidad roscas M3x0.5",                "5.00 mm",  "L", None,      "plano"),
    ("c_chaf",    "Chaflán interior inferior 0.50 x 45°",     "0.50 mm",  "L", None,      "plano"),
]

pz = Pieza("Adaptador_Eje_04")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Delrin")
p = pz.p

r_int = f"({p('d_int')} / 2)"

# --- Cilindro base exterior
cuerpo = pz.cil("Cil_Exterior_57", f"{p('d_ext')} / 2", p("h_total"))

# --- Vaciados: agujero central + chaflán interior + 4 pasantes con cajeados + 4x2 roscas M3
cortes = [
    pz.cil("Agujero_Central_40_1", r_int, f"{p('h_total')} + 2 mm", z="-1 mm"),
    pz.cono("Chaflan_Int_Inf", f"{r_int} + {p('c_chaf')}", r_int, p("c_chaf"), z="0 mm"),
    pz.cil("Aux_Chaflan_Int_Inf", f"{r_int} + {p('c_chaf')}", "1 mm", z="-1 mm"),
]

for i, ang in enumerate((0, 90, 180, 270), 1):
    x_pos = f"({p('d_cor')} / 2) * cos({ang} deg)"
    y_pos = f"({p('d_cor')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"Paso_3_1_{i}", f"{p('d_paso')} / 2", f"{p('h_total')} + 2 mm",
                         x=x_pos, y=y_pos, z="-1 mm"))
    cortes.append(pz.cil(f"Cajeado_Sup_{i}", f"{p('d_caj')} / 2", f"{p('p_caj')} + 1 mm",
                         x=x_pos, y=y_pos, z=f"{p('h_total')} - {p('p_caj')}"))
    cortes.append(pz.cil(f"Rebaje_Inf_{i}", f"{p('d_caj')} / 2", f"{p('p_reb_inf')} + 1 mm",
                         x=x_pos, y=y_pos, z="-1 mm"))

for i, ang in enumerate((45, 135, 225, 315), 1):
    x_pos = f"({p('d_cor')} / 2) * cos({ang} deg)"
    y_pos = f"({p('d_cor')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"M3_Sup_{i}", f"{p('d_m3')} / 2", f"{p('p_m3')} + 1 mm",
                         x=x_pos, y=y_pos, z=f"{p('h_total')} - {p('p_m3')}"))
    cortes.append(pz.cil(f"M3_Inf_{i}", f"{p('d_m3')} / 2", f"{p('p_m3')} + 1 mm",
                         x=x_pos, y=y_pos, z="-1 mm"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Adaptador_Eje_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Superior", z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
