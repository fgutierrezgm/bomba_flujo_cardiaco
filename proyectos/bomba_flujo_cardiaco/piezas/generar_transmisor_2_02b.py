# Transmisor 2 - Plano Nº 2b (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_transmisor_2_02b.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Transmisor_2_02b.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_total",      "Largo total del transmisor 2",             "126.92 mm", "L", None, "plano"),
    ("z_1",          "Fin tramo izquierdo Ø12",                  "67.00 mm",  "L", None, "plano"),
    ("d_izq",        "Diámetro tramo izquierdo (acople y 6201)", "12.00 mm",  "S", None, "plano"),
    ("z_2",          "Fin escalón intermedio Ø13",               "72.00 mm",  "L", None, "plano"),
    ("d_esc13",      "Diámetro escalón intermedio",              "13.00 mm",  "S", None, "plano"),
    ("z_3",          "Fin brida central Ø15",                    "93.00 mm",  "L", None, "plano"),
    ("d_collar",     "Diámetro brida central",                   "15.00 mm",  "S", None, "plano"),
    ("z_4",          "Fin asiento retén Ø14",                    "112.00 mm", "L", None, "plano"),
    ("d_reten",      "Diámetro asiento retén 14x30x7",           "14.00 mm",  "S", None, "plano"),
    ("d_espiga_der", "Diámetro espiga derecha (acople husillo)", "7.97 mm",   "S", None, "plano"),
    ("d_pasador",    "Diámetro agujeros transversales pasador",  "4.00 mm",   "H", None, "plano"),
    ("z_pas1",       "Posición axial agujero pasador 1",         "7.50 mm",   "L", None, "plano"),
    ("z_pas2",       "Posición axial agujero pasador 2",         "52.50 mm",  "L", None, "plano"),
    ("z_pas3",       "Posición axial agujero pasador 3",         "119.50 mm", "L", None, "plano"),
    ("c_chaf",       "Chaflanes 0.50 x 45°",                     "0.50 mm",   "L", None, "plano"),
]

pz = Pieza("Transmisor_2_02b")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Acero_Inoxidable")
p = pz.p

r_izq = f"({p('d_izq')} / 2)"
r_e13 = f"({p('d_esc13')} / 2)"
r_col = f"({p('d_collar')} / 2)"
r_ret = f"({p('d_reten')} / 2)"
r_der = f"({p('d_espiga_der')} / 2)"

# --- Cuerpo escalonado de revolución con chaflanes .50 x 45°
ch_izq = pz.cono("Chaflan_Izq_12", f"{r_izq} - {p('c_chaf')}", r_izq, p("c_chaf"))
cil_izq = pz.cil("Cil_Izq_12", r_izq, f"{p('z_1')} - {p('c_chaf')}", z=p("c_chaf"))

cil_esc13 = pz.cil("Cil_Escalon_13", r_e13, f"{p('z_2')} - {p('z_1')}", z=p("z_1"))

ch_col = pz.cono("Chaflan_Collar_15", f"{r_col} - {p('c_chaf')}", r_col, p("c_chaf"), z=p("z_2"))
cil_collar = pz.cil("Cil_Collar_15", r_col,
                    f"{p('z_3')} - {p('z_2')} - {p('c_chaf')}",
                    z=f"{p('z_2')} + {p('c_chaf')}")

cil_reten = pz.cil("Cil_Reten_14", r_ret,
                   f"{p('z_4')} - {p('z_3')} - {p('c_chaf')}",
                   z=p("z_3"))
ch_ret = pz.cono("Chaflan_Reten_14", r_ret, f"{r_ret} - {p('c_chaf')}", p("c_chaf"),
                 z=f"{p('z_4')} - {p('c_chaf')}")

cil_esp_der = pz.cil("Cil_Espiga_Der", r_der,
                     f"{p('l_total')} - {p('z_4')} - {p('c_chaf')}",
                     z=p("z_4"))
ch_der = pz.cono("Chaflan_Espiga_Der", r_der, f"{r_der} - {p('c_chaf')}", p("c_chaf"),
                 z=f"{p('l_total')} - {p('c_chaf')}")

cuerpo = pz.fusion("Cuerpo_Exterior", [
    ch_izq, cil_izq, cil_esc13, ch_col, cil_collar, cil_reten, ch_ret, cil_esp_der, ch_der
])

# --- 3 agujeros transversales pasantes Ø4.00
cortes = [
    pz.cil_x(f"Pasador_{i}", f"{p('d_pasador')} / 2", f"{p('d_collar')} * 2",
             x=f"-1 * {p('d_collar')}", z=p(f"z_pas{i}"))
    for i in (1, 2, 3)
]
vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Transmisor_2_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Asiento_Rodamiento", z=p("z_1"))
pz.lcs("LCS_Asiento_Reten", z=p("z_3"))
pz.lcs("LCS_Espiga_Husillo", z=p("z_4"))
pz.lcs("LCS_Extremo_Der", z=p("l_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
