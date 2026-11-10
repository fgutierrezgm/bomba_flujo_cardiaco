# Centro del émbolo parte 1 - Plano Nº 11 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_centro_embolo_1_11.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Centro_Embolo_1_11.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_brida",      "Diámetro exterior de la brida base",       "45.00 mm", "S", None,       "plano"),
    ("h_brida",      "Espesor axial de la brida base",           "6.00 mm",  "L", None,       "plano"),
    ("d_vast",       "Diámetro del vástago central",             "30.00 mm", "S", None,       "plano"),
    ("h_total",      "Altura total de la pieza (Z=0..24.80)",    "24.80 mm", "L", None,       "plano"),
    ("d_m14",        "Rosca central pasante M14x2",              "14.00 mm", "R", "12.00 mm", "plano"),
    ("d_cor_brida",  "Corona de 4 agujeros en brida",            "37.50 mm", "L", None,       "plano"),
    ("d_aguj_brida", "Agujeros pasantes en brida (4x)",          "3.50 mm",  "H", None,       "plano"),
    ("c_avell",      "Avellanado 90° de agujeros en brida",      "0.50 mm",  "L", None,       "plano"),
    ("d_cor_sup",    "Corona de 3 roscas M3 en cara superior",   "21.00 mm", "L", None,       "plano"),
    ("d_m3",         "Roscas M3x0.5 en cara superior (3x)",      "3.00 mm",  "R", "2.50 mm",  "plano"),
    ("p_m3",         "Profundidad roscas M3x0.5 superiores",     "15.00 mm", "L", None,       "plano"),
    ("c_ch",         "Chaflanes generales (0.50 x 45°)",         "0.50 mm",  "L", None,       "plano"),
]

pz = Pieza("Centro_Embolo_1_11")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Laton")
p = pz.p

r_bri = f"({p('d_brida')} / 2)"
r_vas = f"({p('d_vast')} / 2)"
r_m14 = f"({p('d_m14')} / 2)"
r_agb = f"({p('d_aguj_brida')} / 2)"

# --- Cuerpo de revolución con chaflanes exteriores de 0.50 x 45°
ch_bri_inf = pz.cono("Chaflan_Brida_Inf", f"{r_bri} - {p('c_ch')}", r_bri, p("c_ch"))
cil_brida = pz.cil("Cil_Brida", r_bri, f"{p('h_brida')} - 2 * {p('c_ch')}", z=p("c_ch"))
ch_bri_sup = pz.cono("Chaflan_Brida_Sup", r_bri, f"{r_bri} - {p('c_ch')}", p("c_ch"),
                     z=f"{p('h_brida')} - {p('c_ch')}")
cil_vast = pz.cil("Cil_Vastago", r_vas, f"{p('h_total')} - {p('c_ch')}")
ch_vas_sup = pz.cono("Chaflan_Vastago_Sup", r_vas, f"{r_vas} - {p('c_ch')}", p("c_ch"),
                     z=f"{p('h_total')} - {p('c_ch')}")

cuerpo = pz.fusion("Cuerpo_Base", [ch_bri_inf, cil_brida, ch_bri_sup, cil_vast, ch_vas_sup])

# --- Herramientas de corte
cortes = []

# 1. Rosca central pasante M14x2 y su chaflán de entrada inferior (0.50 x 45°)
cortes.append(pz.cil("Rosca_Central_M14", r_m14, f"{p('h_total')} + 2 mm", z="-1 mm"))
cortes.append(pz.cono("Chaflan_M14_Inf",
                      f"{r_m14} + {p('c_ch')} + 1 mm", r_m14,
                      f"{p('c_ch')} + 1 mm", z="-1 mm"))

# 2. Cuatro agujeros pasantes Ø3.50 en la brida sobre Ø37.50 (a 0, 90, 180, 270°) con avellanado 90° (0.50 mm)
for i, ang in enumerate((0, 90, 180, 270), 1):
    x_b = f"({p('d_cor_brida')} / 2) * cos({ang} deg)"
    y_b = f"({p('d_cor_brida')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"Aguj_Brida_{i}", r_agb, f"{p('h_brida')} + 2 mm",
                         x=x_b, y=y_b, z="-1 mm"))
    cortes.append(pz.cono(f"Avell_Brida_{i}",
                          f"{r_agb} + {p('c_avell')} + 1 mm", r_agb,
                          f"{p('c_avell')} + 1 mm",
                          x=x_b, y=y_b, z="-1 mm"))

# 3. Tres roscas M3x0.5 (prof. 15.00 mm) desde Z=h_total sobre Ø21.00 a 120° (90, 210, 330°)
for i, ang in enumerate((90, 210, 330), 1):
    x_s = f"({p('d_cor_sup')} / 2) * cos({ang} deg)"
    y_s = f"({p('d_cor_sup')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"M3_Sup_{i}", f"{p('d_m3')} / 2", f"{p('p_m3')} + 1 mm",
                         x=x_s, y=y_s, z=f"{p('h_total')} - {p('p_m3')}"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Centro_Embolo_1_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Asiento_Brida", z=p("h_brida"))
pz.lcs("LCS_Tope_Vastago", z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
