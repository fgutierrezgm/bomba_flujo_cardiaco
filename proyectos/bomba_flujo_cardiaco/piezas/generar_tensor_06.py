# Tensor - Plano Nº 6 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_tensor_06.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Tensor_06.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_total",    "Longitud total de la barra tensora",   "434.00 mm", "L", None,      "plano"),
    ("l_tramo1",   "Referencia intermedia (cota 223 mm)",  "223.00 mm", "L", None,      "plano"),
    ("d_ext",      "Diámetro exterior de la barra",        "22.00 mm",  "S", None,      "plano"),
    ("c_ext",      "Chaflanes extremos (0.50x45°)",        "0.50 mm",   "L", None,      "plano"),
    ("d_m10",      "Rosca interna M10x1.5 en extremos",    "10.00 mm",  "R", "8.50 mm", "norma"),
    ("p_rosca",    "Profundidad roscada M10x1.5",          "16.00 mm",  "L", None,      "plano"),
    ("p_aguj",     "Profundidad agujero extremo izq.",     "19.00 mm",  "L", None,      "plano"),
    ("p_aguj_der", "Profundidad agujero extremo der.",     "16.00 mm",  "L", None,      "plano"),
]

pz = Pieza("Tensor_06")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Aluminio")
p = pz.p

r_ext = f"({p('d_ext')} / 2)"

# --- Cuerpo con chaflanes en los extremos (sin índices de arista)
ch_izq = pz.cono("Chaflan_Izq", f"{r_ext} - {p('c_ext')}", r_ext, p("c_ext"))
cil_cuerpo = pz.cil("Cuerpo_Tensor", r_ext, f"{p('l_total')} - 2 * {p('c_ext')}", z=p("c_ext"))
ch_der = pz.cono("Chaflan_Der", r_ext, f"{r_ext} - {p('c_ext')}", p("c_ext"),
                 z=f"{p('l_total')} - {p('c_ext')}")
cuerpo = pz.fusion("Cuerpo_Bruto", [ch_izq, cil_cuerpo, ch_der])

# --- Roscas axiales en ambos extremos
cortes = [
    pz.cil("Rosca_M10_Izq", f"{p('d_m10')} / 2", f"{p('p_aguj')} + 1 mm", z="-1 mm"),
    pz.cil("Rosca_M10_Der", f"{p('d_m10')} / 2", f"{p('p_aguj_der')} + 1 mm",
           z=f"{p('l_total')} - {p('p_aguj_der')}"),
]
vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Tensor_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Centro_223", z=p("l_tramo1"))
pz.lcs("LCS_Extremo_Der", z=p("l_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
