# Junta tórica (O-Ring) de émbolo 97 x 3.50 mm (Viton / NBR, ISO 3601) - Componente comercial
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_oring_embolo_97x3_5.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2
SALIDA = os.path.join(AQUI, "ORing_Embolo_97x3_5.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_int",   "Diámetro interior nominal d1 (ISO 3601)",      "97.00 mm", "L", None, "norma"),
    ("d_sec",   "Diámetro de sección transversal d2",           "3.50 mm",  "L", None, "norma"),
]

pz = Pieza("ORing_Embolo_97x3_5")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Caucho_NBR", origen="norma")
p = pz.p

toro = pz.nuevo("Part::Torus", "ORing_97x3_5_Solido")
toro.setExpression("Radius1", f"({p('d_int')} + {p('d_sec')}) / 2")
toro.setExpression("Radius2", f"{p('d_sec')} / 2")
toro.setExpression(".Placement.Base.z", f"{p('d_sec')} / 2")

pz.lcs("LCS_Origen")
pz.lcs("LCS_Centro_Toro", z=f"{p('d_sec')} / 2")

pz.reporte_fisico(toro)
pz.cerrar(toro, SALIDA)
