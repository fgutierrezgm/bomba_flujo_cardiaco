# Guía 3D (Escala 75.5%) - Plano Nº 8 (bomba de simulación de flujo cardíaco)
# Parametrizada para acoplar entre Tapa_Interior_16b_3D y Tapa_Exterior_16a_3D (alojamiento Face22).
# Ejecución: /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_guia_08_3d.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 1          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render
SALIDA = os.path.join(AQUI, "Guia_08_3D.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_total",   "Longitud total de la guía 3D",       "220.65 mm", "L", None, "calculado"),
    ("l_espiga",  "Longitud total espiga rebajada",     "22.65 mm",  "L", None, "plano"),
    ("l_rosca",   "Longitud roscada M10x1.5 a escala",  "9.82 mm",   "L", None, "plano"),
    ("d_cuerpo",  "Diámetro cuerpo guía (Ø12*0.755)",   "9.06 mm",   "S", None, "plano"),
    ("d_espiga",  "Diámetro espiga lisa (Ø10*0.755)",   "7.55 mm",   "S", None, "plano"),
    ("d_m10",     "Rosca exterior M10 a escala",        "7.55 mm",   "R", "7.55 mm", "plano"),
    ("paso_m10",  "Paso rosca a escala",                "1.13 mm",   "N", None, "plano"),
    ("c_izq",     "Chaflán extremo roscado",            "0.76 mm",   "L", None, "plano"),
    ("c_escalon", "Chaflán escalón Ø7.55-Ø9.06",        "0.38 mm",   "L", None, "plano"),
    ("c_der",     "Chaflán extremo derecho",            "0.76 mm",   "L", None, "plano"),
]

pz = Pieza("Guia_08_3D")
pz.parametros(DIMS, modo=MODO_DISENO, escala="1.0", holgura_fdm="0.20 mm")
pz.materiales("AISI_304")
p = pz.p

r_m10 = f"({p('d_m10')} / 2)"
r_esp = f"({p('d_espiga')} / 2)"
r_cue = f"({p('d_cuerpo')} / 2)"

# --- Tramos axiales de revolución sin índices de arista
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

solido = pz.fusion("Guia_08_3D_Solido", [ch_izq, cil_rosca, cil_espiga, ch_esc, cil_cuerpo, ch_der])

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Fin_Rosca_M10", z=p("l_rosca"))
pz.lcs("LCS_Hombro_Asiento", z=p("l_espiga"))
pz.lcs("LCS_Centro", z=f"{p('l_total')} / 2")
pz.lcs("LCS_Cara_Sup", z=p("l_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
print(f"Generado con éxito: {SALIDA}")
