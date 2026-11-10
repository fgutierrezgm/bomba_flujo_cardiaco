# Sensor pistón - Plano Nº 5b (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_sensor_piston_05b.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Sensor_Piston_05b.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_m8",    "Rosca exterior M8x0.5 - 6g",             "8.00 mm",  "R", "8.00 mm", "plano"),
    ("paso_m8", "Paso rosca M8 (ver contradicción Pl.10)", "0.50 mm", "N", None,      "plano"),
    ("l_vast",  "Longitud del vástago roscado",           "8.00 mm",  "L", None,      "plano"),
    ("d_cab",   "Diámetro exterior de la cabeza",         "20.00 mm", "S", None,      "plano"),
    ("h_cab",   "Altura de la cabeza (total 15 mm)",      "7.00 mm",  "L", None,      "plano"),
    ("c_cab",   "Chaflán superior cabeza (0.50x45°)",     "0.50 mm",  "L", None,      "plano"),
]

pz = Pieza("Sensor_Piston_05b")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Acero_Inoxidable")
p = pz.p

r_cab = f"({p('d_cab')} / 2)"

# --- Cuerpo por tramos axiales (sin índices de arista)
c_vast = pz.cil("Vastago_M8", f"{p('d_m8')} / 2", p("l_vast"))
c_cab = pz.cil("Cabeza_Cil", r_cab, f"{p('h_cab')} - {p('c_cab')}", z=p("l_vast"))
ch_cab = pz.cono("Chaflan_Cabeza", r_cab, f"{r_cab} - {p('c_cab')}", p("c_cab"),
                 z=f"{p('l_vast')} + {p('h_cab')} - {p('c_cab')}")

solido = pz.fusion("Sensor_Piston_Solido", [c_vast, c_cab, ch_cab])

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Asiento_Embolo", z=p("l_vast"))
pz.lcs("LCS_Cara_Sensor", z=f"{p('l_vast')} + {p('h_cab')}")

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
