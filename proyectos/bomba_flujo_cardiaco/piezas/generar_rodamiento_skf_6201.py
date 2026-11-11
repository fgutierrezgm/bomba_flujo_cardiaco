# Rodamiento rígido de bolas SKF 6201 (12x32x10 mm, DIN 625-1) - Componente comercial
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_rodamiento_skf_6201.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2
SALIDA = os.path.join(AQUI, "Rodamiento_SKF_6201.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_int",   "Diámetro interior nominal d (DIN 625-1)",      "12.00 mm", "H", None, "norma"),
    ("d_ext",   "Diámetro exterior nominal D (DIN 625-1)",      "32.00 mm", "S", None, "norma"),
    ("b_ancho", "Ancho axial nominal B (DIN 625-1)",            "10.00 mm", "L", None, "norma"),
    ("d_pista_int", "Diámetro hombro aro interior d1",          "18.20 mm", "L", None, "norma"),
    ("d_pista_ext", "Diámetro hombro aro exterior D1",          "25.80 mm", "L", None, "norma"),
    ("p_canal", "Profundidad rebaje lateral de obturación",     "1.20 mm",  "L", None, "norma"),
]

pz = Pieza("Rodamiento_SKF_6201")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Acero_Inoxidable", origen="norma")
p = pz.p

# Cilindro exterior D=32 x B=10
c_base = pz.cil("Cil_Exterior_32", f"{p('d_ext')} / 2", p("b_ancho"))

# Agujero central d=12 y rebajes anulares laterales que representan aros interior/exterior
aguj_central = pz.cil("Agujero_Central_12", f"{p('d_int')} / 2", f"{p('b_ancho')} + 2 mm", z="-1 mm")
reb_inf_ext = pz.cil("Canal_Inf_Ext", f"{p('d_pista_ext')} / 2", f"{p('p_canal')} + 1 mm", z="-1 mm")
reb_inf_int = pz.cil("Canal_Inf_Int", f"{p('d_pista_int')} / 2", f"{p('p_canal')} + 2 mm", z="-2 mm")
canal_inf = pz.corte("Anillo_Canal_Inf", reb_inf_ext, reb_inf_int)

reb_sup_ext = pz.cil("Canal_Sup_Ext", f"{p('d_pista_ext')} / 2", f"{p('p_canal')} + 1 mm",
                     z=f"{p('b_ancho')} - {p('p_canal')}")
reb_sup_int = pz.cil("Canal_Sup_Int", f"{p('d_pista_int')} / 2", f"{p('p_canal')} + 2 mm",
                     z=f"{p('b_ancho')} - {p('p_canal')} - 0.5 mm")
canal_sup = pz.corte("Anillo_Canal_Sup", reb_sup_ext, reb_sup_int)

vaciado = pz.fusion("Operaciones_Vaciado", [aguj_central, canal_inf, canal_sup])
solido = pz.corte("Rodamiento_SKF_6201_Solido", c_base, vaciado)

pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Sup", z=p("b_ancho"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
