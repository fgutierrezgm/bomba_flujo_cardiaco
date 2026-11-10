# Guía - Plano Nº 8 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_guia_08.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Guia_08.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_total",   "Longitud total de la guía",          "290.00 mm", "L", None,       "plano"),
    ("l_espiga",  "Longitud total espiga rebajada",     "30.00 mm",  "L", None,       "plano"),
    ("l_rosca",   "Longitud roscada M10x1.5",           "13.00 mm",  "L", None,       "plano"),
    ("d_cuerpo",  "Diámetro cuerpo guía (Ø12 h7)",      "12.00 mm",  "S", None,       "plano"),
    ("d_espiga",  "Diámetro espiga lisa",               "10.00 mm",  "S", None,       "plano"),
    ("d_m10",     "Rosca exterior M10x1.5 - 6g",        "10.00 mm",  "R", "10.00 mm", "plano"),
    ("paso_m10",  "Paso rosca M10x1.5",                 "1.50 mm",   "N", None,       "plano"),
    ("c_izq",     "Chaflán extremo roscado (1.00x45°)", "1.00 mm",   "L", None,       "plano"),
    ("c_escalon", "Chaflán escalón Ø10-Ø12 (0.50x45°)", "0.50 mm",   "L", None,       "plano"),
    ("c_der",     "Chaflán extremo derecho (1.00x45°)", "1.00 mm",   "L", None,       "plano"),
]

pz = Pieza("Guia_08")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Acero_Inoxidable")
p = pz.p

r_m10 = f"({p('d_m10')} / 2)"
r_esp = f"({p('d_espiga')} / 2)"
r_cue = f"({p('d_cuerpo')} / 2)"

# --- Tramos axiales de revolución (sin usar Part::Chamfer por índice de arista)
ch_izq = pz.cono("Chaflan_Izq", f"{r_m10} - {p('c_izq')}", r_m10, p("c_izq"))
cil_rosca = pz.cil("Tramo_Rosca_M10", r_m10, f"{p('l_rosca')} - {p('c_izq')}", z=p("c_izq"))
cil_espiga = pz.cil("Tramo_Espiga_10", r_esp, f"{p('l_espiga')} - {p('l_rosca')}", z=p("l_rosca"))
ch_esc = pz.cono("Chaflan_Escalon", f"{r_cue} - {p('c_escalon')}", r_cue, p("c_escalon"),
                 z=p("l_espiga"))
cil_cuerpo = pz.cil("Cuerpo_Guia_12", r_cue,
                    f"{p('l_total')} - {p('l_espiga')} - {p('c_escalon')} - {p('c_der')}",
                    z=f"{p('l_espiga')} + {p('c_escalon')}")
ch_der = pz.cono("Chaflan_Der", r_cue, f"{r_cue} - {p('c_der')}", p("c_der"),
                 z=f"{p('l_total')} - {p('c_der')}")

solido = pz.fusion("Guia_Solido", [ch_izq, cil_rosca, cil_espiga, ch_esc, cil_cuerpo, ch_der])

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Fin_Rosca_M10", z=p("l_rosca"))
pz.lcs("LCS_Hombro_Asiento", z=p("l_espiga"))
pz.lcs("LCS_Extremo_Guia", z=p("l_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
