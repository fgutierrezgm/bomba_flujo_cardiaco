# Sufridera guía - Plano Nº 5b (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_sufridera_guia_05b.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Sufridera_Guia_05b.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",   "Diámetro exterior del disco",        "20.00 mm", "S", None, "plano"),
    ("h_total", "Espesor total de la sufridera",      "3.00 mm",  "L", None, "plano"),
    ("d_int",   "Diámetro agujero central pasante",   "10.10 mm", "H", None, "plano"),
    ("d_cor",   "Círculo de 4 agujeros pasantes",     "15.00 mm", "L", None, "plano"),
    ("d_aguj",  "Diámetro agujeros pasantes (4x)",    "3.10 mm",  "H", None, "plano"),
]

pz = Pieza("Sufridera_Guia_05b")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Laton")
p = pz.p

# --- Cuerpo
cuerpo = pz.cil("Disco_Base", f"{p('d_ext')} / 2", p("h_total"))

# --- Herramientas de corte
cortes = [
    pz.cil("Agujero_Central", f"{p('d_int')} / 2", f"{p('h_total')} + 2 mm", z="-1 mm"),
]
for i, ang in enumerate((0, 90, 180, 270), 1):
    cortes.append(pz.cil(f"Agujero_{i}", f"{p('d_aguj')} / 2", f"{p('h_total')} + 2 mm",
                         x=f"({p('d_cor')} / 2) * cos({ang} deg)",
                         y=f"({p('d_cor')} / 2) * sin({ang} deg)",
                         z="-1 mm"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Sufridera_Guia_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Sup", z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
