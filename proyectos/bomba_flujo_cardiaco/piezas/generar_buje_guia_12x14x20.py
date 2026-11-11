# Buje guía autolubricado 12x14x20 mm (DIN 1850 / ISO 2795, Bronce sinterizado) - Componente comercial
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_buje_guia_12x14x20.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2
SALIDA = os.path.join(AQUI, "Buje_Guia_12x14x20.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_int",   "Diámetro interior nominal d (guía Ø12)",       "12.00 mm", "H", None, "norma"),
    ("d_ext",   "Diámetro exterior nominal D (alojamiento Ø14)","14.00 mm", "S", None, "norma"),
    ("l_total", "Longitud axial del buje L (espesor émbolo)",   "20.00 mm", "L", None, "norma"),
]

pz = Pieza("Buje_Guia_12x14x20")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Bronce", origen="norma")
p = pz.p

c_ext = pz.cil("Cil_Exterior_14", f"{p('d_ext')} / 2", p("l_total"))
c_int = pz.cil("Agujero_Interior_12", f"{p('d_int')} / 2", f"{p('l_total')} + 2 mm", z="-1 mm")
solido = pz.corte("Buje_Guia_Solido", c_ext, c_int)

pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Sup", z=p("l_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
