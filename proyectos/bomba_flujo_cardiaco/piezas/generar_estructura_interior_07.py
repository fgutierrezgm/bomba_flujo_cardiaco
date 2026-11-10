# Estructura interior - Plano Nº 7 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_estructura_interior_07.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Estructura_Interior_07.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("lado",          "Lado de la placa cuadrada",             "183.00 mm", "L", None,      "plano"),
    ("h_base",        "Espesor base de la placa",              "20.00 mm",  "L", None,      "plano"),
    ("h_res",         "Altura del resalte central (Z=22.10)",  "2.10 mm",   "L", None,      "calculado"),
    ("r_res_ext",     "Radio exterior del resalte central",    "101.82 mm", "L", None,      "plano"),
    ("r_res_int",     "Radio interior del resalte central",    "84.63 mm",  "L", None,      "plano"),
    ("r_int",         "Radio agujero central pasante",         "72.55 mm",  "L", None,      "plano"),
    ("r_esc",         "Radio escalón circular interior",       "80.25 mm",  "L", None,      "plano"),
    ("p_esc",         "Profundidad escalón interior",          "12.50 mm",  "L", None,      "plano"),
    ("r_aguj",        "Radio corona 4 agujeros Ø3.50",         "76.27 mm",  "L", None,      "plano"),
    ("d_aguj",        "Diámetro 4 agujeros pasantes",          "3.50 mm",   "H", None,      "plano"),
    ("r_m5",          "Radio corona 4 roscas M5x0.8",          "84.63 mm",  "L", None,      "plano"),
    ("d_m5",          "Roscas M5x0.8 (4x a 45°)",              "5.00 mm",   "R", "4.20 mm", "norma"),
    ("pos_tensor",    "Coord. X/Y de los 4 tensores (no acot.)", "69.00 mm", "L", None,     "supuesto"),
    ("d_aloj_tensor", "Diámetro pasante esquina para tensor",  "22.00 mm",  "H", None,      "supuesto"),
]

pz = Pieza("Estructura_Interior_07")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Aluminio")
p = pz.p

h_tot = f"({p('h_base')} + {p('h_res')})"

# --- Cuerpo: placa cuadrada + resalte central recortado al cuadrado (intersección placa ∩ cilindro R101.82)
placa = pz.caja("Placa_Base", p("lado"), p("lado"), p("h_base"),
                x=f"-{p('lado')} / 2", y=f"-{p('lado')} / 2")
cil_res = pz.cil("Cil_Resalte_Bruto", p("r_res_ext"), h_tot)
cil_env = pz.cil("Cil_Envolvente", f"{p('r_res_ext')} + 10 mm", f"{h_tot} + 2 mm", z="-1 mm")
caja_env = pz.caja("Caja_Limite", p("lado"), p("lado"), f"{h_tot} + 4 mm",
                   x=f"-{p('lado')} / 2", y=f"-{p('lado')} / 2", z="-2 mm")
mascara_ext = pz.corte("Mascara_Exterior", cil_env, caja_env)
pz.auxiliares.append(mascara_ext)
resalte_rec = pz.corte("Resalte_Recortado", cil_res, mascara_ext)
pz.auxiliares.append(resalte_rec)
cuerpo = pz.fusion("Cuerpo_Principal", [placa, resalte_rec])

# --- Herramientas de corte
cortes = [
    pz.cil("Vaciado_Resalte_Int", p("r_res_int"), f"{p('h_res')} + 1 mm", z=p("h_base")),
    pz.cil("Agujero_Central", p("r_int"), f"{h_tot} + 2 mm", z="-1 mm"),
    pz.cil("Escalon_Interior", p("r_esc"), f"{p('p_esc')} + 1 mm", z="-1 mm"),
]

esquinas = ((1, 1), (-1, 1), (-1, -1), (1, -1))
for i, (sx, sy) in enumerate(esquinas, 1):
    cortes.append(pz.cil(f"Aloj_Tensor_{i}", f"{p('d_aloj_tensor')} / 2", f"{h_tot} + 2 mm",
                         x=f"{sx} * {p('pos_tensor')}",
                         y=f"{sy} * {p('pos_tensor')}",
                         z="-1 mm"))

for i, ang in enumerate((0, 90, 180, 270), 1):
    cortes.append(pz.cil(f"Agujero_3_5_{i}", f"{p('d_aguj')} / 2", f"{h_tot} + 2 mm",
                         x=f"{p('r_aguj')} * cos({ang} deg)",
                         y=f"{p('r_aguj')} * sin({ang} deg)",
                         z="-1 mm"))

for i, ang in enumerate((45, 135, 225, 315), 1):
    cortes.append(pz.cil(f"Rosca_M5_{i}", f"{p('d_m5')} / 2", f"{h_tot} + 2 mm",
                         x=f"{p('r_m5')} * cos({ang} deg)",
                         y=f"{p('r_m5')} * sin({ang} deg)",
                         z="-1 mm"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Estructura_Interior_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Asiento_Tapa", z=p("h_base"))
pz.lcs("LCS_Tope_Resalte", z=h_tot)
for i, (sx, sy) in enumerate(esquinas, 1):
    pz.lcs(f"LCS_Tensor_{i}", x=f"{sx} * {p('pos_tensor')}", y=f"{sy} * {p('pos_tensor')}")

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
