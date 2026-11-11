# Retén radial de eje 14x30x7 mm (DIN 3760A / ISO 6194, NBR) - Componente comercial
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_reten_14x30x7.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2
SALIDA = os.path.join(AQUI, "Reten_14x30x7.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_eje",   "Diámetro nominal de eje d1 (DIN 3760)",        "14.00 mm", "H", None, "norma"),
    ("d_aloj",  "Diámetro exterior nominal d2 (DIN 3760)",      "30.00 mm", "S", None, "norma"),
    ("b_ancho", "Ancho nominal del retén b (DIN 3760)",         "7.00 mm",  "L", None, "norma"),
    ("d_cav",   "Diámetro exterior cavidad del labio",          "25.00 mm", "L", None, "norma"),
    ("d_labio", "Diámetro respaldo del labio",                  "17.50 mm", "L", None, "norma"),
    ("p_cav",   "Profundidad cavidad interior del resorte",     "4.50 mm",  "L", None, "norma"),
]

pz = Pieza("Reten_14x30x7")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Caucho_NBR", origen="norma")
p = pz.p

c_base = pz.cil("Cil_Exterior_30", f"{p('d_aloj')} / 2", p("b_ancho"))
aguj_eje = pz.cil("Agujero_Labio_14", f"{p('d_eje')} / 2", f"{p('b_ancho')} + 2 mm", z="-1 mm")

cav_ext = pz.cil("Cav_Ext", f"{p('d_cav')} / 2", f"{p('p_cav')} + 1 mm", z=f"{p('b_ancho')} - {p('p_cav')}")
cav_int = pz.cil("Cav_Int", f"{p('d_labio')} / 2", f"{p('p_cav')} + 2 mm", z=f"{p('b_ancho')} - {p('p_cav')} - 0.5 mm")
cavidad = pz.corte("Anillo_Cavidad", cav_ext, cav_int)

vaciado = pz.fusion("Operaciones_Vaciado", [aguj_eje, cavidad])
solido = pz.corte("Reten_14x30x7_Solido", c_base, vaciado)

pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Sup", z=p("b_ancho"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
