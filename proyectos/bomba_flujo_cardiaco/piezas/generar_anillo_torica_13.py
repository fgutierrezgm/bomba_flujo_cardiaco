# Anillo tórica - Plano Nº 13 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd generar_anillo_torica_13.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Anillo_Torica_13.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",   "Diámetro exterior del anillo",        "140.00 mm", "L", None, "plano"),
    ("d_int",   "Diámetro interior pasante",           "111.50 mm", "H", None, "plano"),
    ("h_total", "Espesor axial del anillo",            "5.00 mm",   "L", None, "plano"),
    ("d_cor",   "Círculo de centro de los 6 agujeros", "130.00 mm", "L", None, "plano"),
    ("d_aguj",  "Diámetro agujeros pasantes (6x)",     "3.10 mm",   "H", None, "plano"),
    ("d_avell", "Diámetro avellanado a 90° (6x)",      "3.50 mm",   "H", None, "plano"),
]

pz = Pieza("Anillo_Torica_13")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("PVC_Rigido")
p = pz.p
Z_MENOS_1 = "-1 mm"

# --- Cuerpo base
cuerpo = pz.cil("Cil_Exterior", f"{p('d_ext')} / 2", p("h_total"))

# --- Herramientas de corte
cortes = [
    pz.cil("Agujero_Interior", f"{p('d_int')} / 2", f"{p('h_total')} + 2 mm", z=Z_MENOS_1)
]

h_avell = f"(({p('d_avell')} - {p('d_aguj')}) / 2)"
for i, ang in enumerate((0, 60, 120, 180, 240, 300), 1):
    x = f"({p('d_cor')} / 2) * cos({ang} deg)"
    y = f"({p('d_cor')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"Aguj_Pasante_{i}", f"{p('d_aguj')} / 2", f"{p('h_total')} + 2 mm",
                         x=x, y=y, z=Z_MENOS_1))
    # Cono a 90° (semiángulo 45°: r2 - r1 = altura) en la cara superior z = h_total
    cortes.append(pz.cono(f"Avellanado_{i}",
                          f"{p('d_aguj')} / 2",
                          f"{p('d_avell')} / 2 + 1 mm",
                          f"{h_avell} + 1 mm",
                          x=x, y=y, z=f"{p('h_total')} - {h_avell}"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Anillo_Torica_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Sup", z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
