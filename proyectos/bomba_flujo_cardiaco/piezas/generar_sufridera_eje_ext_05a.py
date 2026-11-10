# Sufridera eje exterior - Plano Nº 5a (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_sufridera_eje_ext_05a.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Sufridera_Eje_Ext_05a.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_brida",     "Diámetro exterior de la brida",       "40.00 mm", "S", None, "plano"),
    ("h_brida",     "Espesor de la brida",                 "5.00 mm",  "L", None, "plano"),
    ("d_vast",      "Diámetro exterior del vástago",       "18.00 mm", "S", None, "plano"),
    ("h_vast",      "Longitud del vástago (total 13 mm)",  "8.00 mm",  "L", None, "plano"),
    ("d_int_brida", "Diámetro agujero lado brida",         "13.10 mm", "H", None, "plano"),
    ("d_int_vast",  "Diámetro agujero pasante vástago",    "12.20 mm", "H", None, "plano"),
    ("d_cor",       "Círculo de 4 agujeros en brida",      "29.00 mm", "L", None, "plano"),
    ("d_aguj",      "Diámetro agujeros pasantes (4x)",     "3.50 mm",  "H", None, "plano"),
    ("d_avell",     "Diámetro avellanado cónico 90°",      "5.00 mm",  "H", None, "plano"),
    ("p_avell",     "Profundidad avellanado 90°",          "0.75 mm",  "L", None, "calculado"),
]

pz = Pieza("Sufridera_Eje_Ext_05a")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Laton")
p = pz.p

# --- Cuerpo
c_brida = pz.cil("Cil_Brida", f"{p('d_brida')} / 2", p("h_brida"))
c_vast = pz.cil("Cil_Vastago", f"{p('d_vast')} / 2", f"{p('h_brida')} + {p('h_vast')}")
cuerpo = pz.fusion("Cuerpo_Principal", [c_brida, c_vast])

# --- Herramientas de corte
cortes = [
    pz.cil("Agujero_Vastago", f"{p('d_int_vast')} / 2",
           f"{p('h_brida')} + {p('h_vast')} + 2 mm", z="-1 mm"),
    pz.cil("Rebaje_Brida", f"{p('d_int_brida')} / 2", f"{p('h_brida')} + 1 mm", z="-1 mm"),
]
for i, ang in enumerate((0, 90, 180, 270), 1):
    x = f"({p('d_cor')} / 2) * cos({ang} deg)"
    y = f"({p('d_cor')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"Agujero_{i}", f"{p('d_aguj')} / 2", f"{p('h_brida')} + 2 mm",
                         x=x, y=y, z="-1 mm"))
    cortes.append(pz.cono(f"Avellanado_{i}", f"{p('d_avell')} / 2", f"{p('d_aguj')} / 2",
                          p("p_avell"), x=x, y=y))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Sufridera_Eje_Ext_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Escal_Brida", z=p("h_brida"))
pz.lcs("LCS_Tope_Vastago", z=f"{p('h_brida')} + {p('h_vast')}")

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
