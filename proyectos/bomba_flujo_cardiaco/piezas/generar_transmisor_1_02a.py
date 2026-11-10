# Transmisor 1 - Plano Nº 2a (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_transmisor_1_02a.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Transmisor_1_02a.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_total",    "Largo total del transmisor 1",             "127.00 mm", "L", None, "plano"),
    ("l_espiga",   "Largo espiga izquierda (acople Oldham)",   "15.00 mm",  "L", None, "plano"),
    ("d_espiga",   "Diámetro espiga izquierda",                "8.00 mm",   "S", None, "plano"),
    ("z_med",      "Posición axial fin tramo medio",           "47.00 mm",  "L", None, "plano"),
    ("d_med",      "Diámetro tramo medio",                     "12.00 mm",  "S", None, "plano"),
    ("d_cuerpo",   "Diámetro cuerpo derecho",                  "20.00 mm",  "S", None, "plano"),
    ("z_aloj",     "Fondo alojamiento interior (recibe Ø12)",  "59.00 mm",  "L", None, "calculado"),
    ("d_aloj_int", "Diámetro alojamiento interior (p/ 02b)",   "12.00 mm",  "H", None, "plano"),
    ("z_pas1",     "Posición axial pasador 1",                 "67.50 mm",  "L", None, "plano"),
    ("z_pas2",     "Posición axial pasador 2",                 "112.50 mm", "L", None, "plano"),
    ("d_pasador",  "Diámetro agujeros pasadores Ø4",           "4.00 mm",   "H", None, "plano"),
    ("c_chaf",     "Chaflanes 0.50 x 45°",                     "0.50 mm",   "L", None, "plano"),
]

pz = Pieza("Transmisor_1_02a")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Acero_Inoxidable")
p = pz.p

r_esp = f"({p('d_espiga')} / 2)"
r_med = f"({p('d_med')} / 2)"
r_cue = f"({p('d_cuerpo')} / 2)"
r_aloj = f"({p('d_aloj_int')} / 2)"

# --- Cuerpo exterior escalonado con chaflanes .50 x 45° (conos paramétricos, sin índices de arista)
ch_esp_izq = pz.cono("Chaflan_Espiga_Izq", f"{r_esp} - {p('c_chaf')}", r_esp, p("c_chaf"))
cil_espiga = pz.cil("Cil_Espiga_8", r_esp, f"{p('l_espiga')} - {p('c_chaf')}", z=p("c_chaf"))

ch_esc_med = pz.cono("Chaflan_Escalon_12", f"{r_med} - {p('c_chaf')}", r_med, p("c_chaf"),
                     z=p("l_espiga"))
cil_medio = pz.cil("Cil_Medio_12", r_med,
                   f"{p('z_med')} - {p('l_espiga')} - {p('c_chaf')}",
                   z=f"{p('l_espiga')} + {p('c_chaf')}")

ch_esc_cue = pz.cono("Chaflan_Escalon_20", f"{r_cue} - {p('c_chaf')}", r_cue, p("c_chaf"),
                     z=p("z_med"))
cil_cuerpo = pz.cil("Cil_Cuerpo_20", r_cue,
                    f"{p('l_total')} - {p('z_med')} - 2 * {p('c_chaf')}",
                    z=f"{p('z_med')} + {p('c_chaf')}")
ch_cue_der = pz.cono("Chaflan_Cuerpo_Der", r_cue, f"{r_cue} - {p('c_chaf')}", p("c_chaf"),
                     z=f"{p('l_total')} - {p('c_chaf')}")

cuerpo = pz.fusion("Cuerpo_Exterior", [
    ch_esp_izq, cil_espiga, ch_esc_med, cil_medio, ch_esc_cue, cil_cuerpo, ch_cue_der
])

# --- Vaciado interior y 2 agujeros transversales de pasador Ø4
cortes = [
    pz.cil("Alojamiento_Int_12", r_aloj, f"{p('l_total')} - {p('z_aloj')} + 1 mm", z=p("z_aloj")),
    pz.cono("Chaflan_Boca_Int", r_aloj, f"{r_aloj} + {p('c_chaf')}", p("c_chaf"),
            z=f"{p('l_total')} - {p('c_chaf')}"),
    pz.cil("Aux_Boca_Int", f"{r_aloj} + {p('c_chaf')}", "1 mm", z=p("l_total")),
    pz.cil_x("Agujero_Pasador_1", f"{p('d_pasador')} / 2", f"{p('d_cuerpo')} * 2",
             x=f"-1 * {p('d_cuerpo')}", z=p("z_pas1")),
    pz.cil_x("Agujero_Pasador_2", f"{p('d_pasador')} / 2", f"{p('d_cuerpo')} * 2",
             x=f"-1 * {p('d_cuerpo')}", z=p("z_pas2")),
]

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Transmisor_1_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Escalon_12", z=p("l_espiga"))
pz.lcs("LCS_Escalon_20", z=p("z_med"))
pz.lcs("LCS_Fondo_Aloj", z=p("z_aloj"))
pz.lcs("LCS_Pasador_1", z=p("z_pas1"))
pz.lcs("LCS_Pasador_2", z=p("z_pas2"))
pz.lcs("LCS_Extremo_Der", z=p("l_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
