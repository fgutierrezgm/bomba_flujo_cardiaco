# Sufridera interior / portarretén - Plano Nº 5b (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_sufridera_int_05b.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Sufridera_Int_05b.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",     "Diámetro exterior del cuerpo",          "45.00 mm", "S", None,      "plano"),
    ("h_total",   "Altura total del cuerpo",               "8.50 mm",  "L", None,      "plano"),
    ("d_int",     "Diámetro agujero central pasante",      "15.10 mm", "H", None,      "plano"),
    ("d_reten",   "Diámetro alojamiento retén 14x30x7",    "30.00 mm", "H", None,      "plano"),
    ("p_reten",   "Profundidad alojamiento retén",         "7.00 mm",  "L", None,      "plano"),
    ("d_m3",      "Roscas M3x0.5",                         "3.00 mm",  "R", "2.50 mm", "norma"),
    ("p_m3",      "Profundidad roscas M3x0.5",             "5.00 mm",  "L", None,      "plano"),
    ("d_cor_ext", "Corona superior 4x M3 (tapa)",          "37.50 mm", "L", None,      "plano"),
    ("d_cor_int", "Corona inferior 4x M3 (fijación)",      "22.50 mm", "L", None,      "plano"),
]

pz = Pieza("Sufridera_Int_05b")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Laton")
p = pz.p

# --- Cuerpo
cuerpo = pz.cil("Cil_Cuerpo", f"{p('d_ext')} / 2", p("h_total"))

# --- Herramientas de corte
cortes = [
    pz.cil("Agujero_Central", f"{p('d_int')} / 2", f"{p('h_total')} + 2 mm", z="-1 mm"),
    pz.cil("Alojamiento_Reten", f"{p('d_reten')} / 2", f"{p('p_reten')} + 1 mm",
           z=f"{p('h_total')} - {p('p_reten')}"),
]
for i, ang in enumerate((0, 90, 180, 270), 1):
    cortes.append(pz.cil(f"M3_Sup_{i}", f"{p('d_m3')} / 2", f"{p('p_m3')} + 1 mm",
                         x=f"({p('d_cor_ext')} / 2) * cos({ang} deg)",
                         y=f"({p('d_cor_ext')} / 2) * sin({ang} deg)",
                         z=f"{p('h_total')} - {p('p_m3')}"))
    cortes.append(pz.cil(f"M3_Inf_{i}", f"{p('d_m3')} / 2", f"{p('p_m3')} + 1 mm",
                         x=f"({p('d_cor_int')} / 2) * cos({ang} deg)",
                         y=f"({p('d_cor_int')} / 2) * sin({ang} deg)",
                         z="-1 mm"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Sufridera_Int_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Asiento_Reten", z=f"{p('h_total')} - {p('p_reten')}")
pz.lcs("LCS_Cara_Tapa", z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
