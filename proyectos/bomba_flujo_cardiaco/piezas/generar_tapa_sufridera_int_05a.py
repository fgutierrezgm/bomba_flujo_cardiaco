# Tapa sufridera interior - Plano Nº 5a (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_tapa_sufridera_int_05a.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Tapa_Sufridera_Int_05a.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",   "Diámetro exterior del disco",        "45.00 mm", "L", None, "plano"),
    ("h_total", "Espesor total de la tapa",           "2.00 mm",  "L", None, "plano"),
    ("d_int",   "Diámetro agujero central pasante",   "15.10 mm", "H", None, "plano"),
    ("d_cor",   "Círculo de 4 agujeros pasantes",     "37.50 mm", "L", None, "plano"),
    ("d_aguj",  "Diámetro agujeros pasantes (4x)",    "3.00 mm",  "H", None, "plano"),
    ("d_avell", "Diámetro avellanado cónico 90°",     "4.00 mm",  "H", None, "plano"),
    ("p_avell", "Profundidad avellanado 90°",         "0.50 mm",  "L", None, "calculado"),
]

pz = Pieza("Tapa_Sufridera_Int_05a")
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
    x = f"({p('d_cor')} / 2) * cos({ang} deg)"
    y = f"({p('d_cor')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"Agujero_{i}", f"{p('d_aguj')} / 2", f"{p('h_total')} + 2 mm",
                         x=x, y=y, z="-1 mm"))
    cortes.append(pz.cono(f"Avellanado_{i}", f"{p('d_aguj')} / 2", f"{p('d_avell')} / 2",
                          p("p_avell"), x=x, y=y, z=f"{p('h_total')} - {p('p_avell')}"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Tapa_Sufridera_Int_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Sup", z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
