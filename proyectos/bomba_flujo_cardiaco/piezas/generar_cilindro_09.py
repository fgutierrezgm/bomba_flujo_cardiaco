# Cilindro - Plano Nº 9 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_cilindro_09.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Cilindro_09.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",  "Diámetro exterior del cilindro", "110.50 mm", "S", None, "plano"),
    ("d_int",  "Diámetro interior del cilindro", "103.00 mm", "H", None, "plano"),
    ("l_tubo", "Longitud total del cilindro",    "250.00 mm", "L", None, "plano"),
]

pz = Pieza("Cilindro_09")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Vidrio_Borosilicato")
p = pz.p

# --- Geometría tubular (vidrio borosilicato)
c_ext = pz.cil("Cil_Exterior", f"{p('d_ext')} / 2", p("l_tubo"))
c_int = pz.cil("Vaciado_Interior", f"{p('d_int')} / 2", f"{p('l_tubo')} + 2 mm", z="-1 mm")
solido = pz.corte("Cilindro_Solido", c_ext, c_int)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Centro", z=f"{p('l_tubo')} / 2")
pz.lcs("LCS_Extremo_Sup", z=p("l_tubo"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
