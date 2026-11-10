# Sensor inductivo comercial LJ12A3-4-Z/BX (M12x1, Sn = 4 mm) - Componente comercial
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_sensor_inductivo_lj12a3.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2
SALIDA = os.path.join(AQUI, "Sensor_Inductivo_LJ12A3.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_m12",     "Diámetro exterior rosca M12x1",              "12.00 mm", "R", "12.00 mm", "norma"),
    ("l_cuerpo",  "Longitud cuerpo cilíndrico M12x1",           "50.00 mm", "L", None,       "norma"),
    ("d_punta",   "Diámetro cabezal plástico sensor (no ras.)", "10.40 mm", "S", None,       "norma"),
    ("l_punta",   "Longitud cabezal sensor",                    "4.00 mm",  "L", None,       "norma"),
    ("d_brida",   "Diámetro collarín/tuerca de asiento",        "17.00 mm", "L", None,       "norma"),
    ("h_brida",   "Espesor collarín de asiento en tapa",        "4.00 mm",  "L", None,       "norma"),
    ("p_ins",     "Profundidad de inserción dentro del puerto", "14.00 mm", "L", None,       "usuario"),
    ("sn",        "Distancia nominal de detección Sn",          "4.00 mm",  "L", None,       "norma"),
]

pz = Pieza("Sensor_Inductivo_LJ12A3")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Laton", origen="norma")
p = pz.p

# --- Geometría: cuerpo M12 (z = -l_cuerpo + p_ins .. p_ins), tuerca en z = -h_brida .. 0, punta en z = p_ins .. p_ins + l_punta
z_ini = f"({p('p_ins')} - {p('l_cuerpo')})"
c_cuerpo = pz.cil("Cuerpo_M12", f"{p('d_m12')} / 2", p("l_cuerpo"), z=z_ini)
c_tuerca = pz.cil("Tuerca_Tope", f"{p('d_brida')} / 2", p("h_brida"), z=f"-1 * {p('h_brida')}")
c_punta = pz.cil("Cabeza_Sensora", f"{p('d_punta')} / 2", p("l_punta"), z=p("p_ins"))

solido = pz.fusion("Sensor_Inductivo_Solido", [c_cuerpo, c_tuerca, c_punta])

# --- Conectores LCS
pz.lcs("LCS_Origen")                                         # Asiento de la tuerca contra el puerto M12x1 (z = 0)
pz.lcs("LCS_Frente_Sensor", z=f"{p('p_ins')} + {p('l_punta')}")  # Cara frontal activa de detección

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
