# Cierre estructura - Plano Nº 15 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd generar_cierre_estructura_15.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Cierre_Estructura_15.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",    "Diámetro exterior de la brida",       "176.00 mm", "L", None, "plano"),
    ("h_brida",  "Espesor de la brida exterior",        "10.00 mm",  "L", None, "plano"),
    ("d_cuerpo", "Diámetro del cuerpo escalonado",      "161.10 mm", "S", None, "plano"),
    ("h_cuerpo", "Altura del cuerpo escalonado",        "18.50 mm",  "L", None, "plano"),
    ("d_int",    "Diámetro interior pasante",           "131.00 mm", "H", None, "plano"),
    ("d_cor",    "Círculo de agujeros pasantes (4x)",   "169.26 mm", "L", None, "plano"),
    ("d_aguj",   "Diámetro agujeros pasantes (4x M5)",  "5.50 mm",   "H", None, "plano"),
]

pz = Pieza("Cierre_Estructura_15")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Aluminio")
p = pz.p
Z_MENOS_1 = "-1 mm"

# --- Cuerpo escalonado
c_brida = pz.cil("Cil_Brida", f"{p('d_ext')} / 2", p("h_brida"))
c_cuerpo = pz.cil("Cil_Cuerpo", f"{p('d_cuerpo')} / 2", f"{p('h_brida')} + {p('h_cuerpo')}")
cuerpo = pz.fusion("Cuerpo_Principal", [c_brida, c_cuerpo])

# --- Herramientas de corte
cortes = [
    pz.cil("Agujero_Central", f"{p('d_int')} / 2",
           f"{p('h_brida')} + {p('h_cuerpo')} + 2 mm", z=Z_MENOS_1)
]
for i, ang in enumerate((0, 90, 180, 270), 1):
    cortes.append(pz.cil(f"Aguj_Brida_{i}", f"{p('d_aguj')} / 2", f"{p('h_brida')} + 2 mm",
                         x=f"({p('d_cor')} / 2) * cos({ang} deg)",
                         y=f"({p('d_cor')} / 2) * sin({ang} deg)",
                         z=Z_MENOS_1))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Cierre_Estructura_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Escalon", z=p("h_brida"))
pz.lcs("LCS_Tope_Sup", z=f"{p('h_brida')} + {p('h_cuerpo')}")

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
