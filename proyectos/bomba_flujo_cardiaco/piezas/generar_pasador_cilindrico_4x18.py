# Pasador cilíndrico / elástico Ø4 x 14 mm (ISO 8752 / DIN 1481, Acero Inox) - Componente comercial
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_pasador_cilindrico_4x18.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2
SALIDA = os.path.join(AQUI, "Pasador_Cilindrico_4x18.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_nom",   "Diámetro nominal del pasador (ISO 8752)",      "4.00 mm",  "S", None, "norma"),
    ("l_total", "Longitud total del pasador transversal",       "14.00 mm", "L", None, "norma"),
]

pz = Pieza("Pasador_Cilindrico_4x18")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Acero_Inoxidable", origen="norma")
p = pz.p

# Eje a lo largo de X centrado en X=0 para coincidir directamente con LCS_Pasador
solido = pz.cil_x("Pasador_4x18_Solido", f"{p('d_nom')} / 2", p("l_total"),
                  x=f"-0.5 * {p('l_total')}")

pz.lcs("LCS_Origen")

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
