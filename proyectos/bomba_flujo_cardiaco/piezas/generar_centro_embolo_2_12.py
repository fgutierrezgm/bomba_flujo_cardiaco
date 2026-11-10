# Centro del émbolo parte 2 - Plano Nº 12 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_centro_embolo_2_12.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Centro_Embolo_2_12.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",   "Diámetro exterior de la brida",             "45.00 mm", "S", None, "plano"),
    ("h_total", "Espesor axial total",                       "5.00 mm",  "L", None, "plano"),
    ("d_int",   "Agujero central pasante",                   "15.00 mm", "H", None, "plano"),
    ("d_cor",   "Corona de 3 agujeros a 120°",               "21.00 mm", "L", None, "plano"),
    ("d_aguj",  "Agujeros pasantes para M3 (3x)",            "3.50 mm",  "H", None, "plano"),
    ("d_caj",   "Diámetro de avellanado/cajeado (3x)",       "5.00 mm",  "H", None, "plano"),
    ("p_caj",   "Profundidad de avellanado desde Z=h_total", "0.75 mm",  "L", None, "plano"),
    ("c_ch",    "Chaflanes en cara Z=0 (0.50 x 45°)",        "0.50 mm",  "L", None, "plano"),
]

pz = Pieza("Centro_Embolo_2_12")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Laton")
p = pz.p

r_ext = f"({p('d_ext')} / 2)"
r_int = f"({p('d_int')} / 2)"

# --- Cuerpo exterior con chaflán de 0.50 x 45° en Z=0
ch_ext_inf = pz.cono("Chaflan_Ext_Inf", f"{r_ext} - {p('c_ch')}", r_ext, p("c_ch"))
cil_cuerpo = pz.cil("Cil_Cuerpo", r_ext, f"{p('h_total')} - {p('c_ch')}", z=p("c_ch"))
cuerpo = pz.fusion("Cuerpo_Base", [ch_ext_inf, cil_cuerpo])

# --- Herramientas de corte
cortes = []

# 1. Agujero central Ø15.00 y su chaflán interior de 0.50 x 45° en Z=0
cortes.append(pz.cil("Aguj_Central_15", r_int, f"{p('h_total')} + 2 mm", z="-1 mm"))
cortes.append(pz.cono("Chaflan_Int_Inf",
                      f"{r_int} + {p('c_ch')} + 1 mm", r_int,
                      f"{p('c_ch')} + 1 mm", z="-1 mm"))

# 2. Tres agujeros pasantes Ø3.50 sobre Ø21.00 a 120° (90, 210, 330°) con avellanado Ø5.00 x 0.75 en Z=h_total
for i, ang in enumerate((90, 210, 330), 1):
    x_a = f"({p('d_cor')} / 2) * cos({ang} deg)"
    y_a = f"({p('d_cor')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"Aguj_M3_{i}", f"{p('d_aguj')} / 2", f"{p('h_total')} + 2 mm",
                         x=x_a, y=y_a, z="-1 mm"))
    cortes.append(pz.cono(f"Avell_M3_{i}",
                          f"{p('d_aguj')} / 2", f"{p('d_caj')} / 2", p("p_caj"),
                          x=x_a, y=y_a, z=f"{p('h_total')} - {p('p_caj')}"))
    cortes.append(pz.cil(f"Salida_Avell_M3_{i}", f"{p('d_caj')} / 2", "1 mm",
                         x=x_a, y=y_a, z=p("h_total")))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Centro_Embolo_2_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Exterior", z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
