# Tornillo sin fin - Plano Nº 14 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd generar_tornillo_sin_fin_14.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Tornillo_Sin_Fin_14.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_m14",      "Diámetro nominal rosca M14x2 - 6g",   "14.00 mm",  "R", "14.00 mm", "plano"),
    ("l_rosca",    "Largo del tramo roscado M14x2",       "254.50 mm", "L", None,       "plano"),
    ("l_esp_der",  "Largo total espiga derecha",          "13.00 mm",  "L", None,       "plano"),
    ("d_esp13",    "Diámetro primer escalón derecho",     "13.00 mm",  "S", None,       "plano"),
    ("l_esp13",    "Largo primer escalón (13.00 - 8.00)", "5.00 mm",   "L", None,       "calculado"),
    ("d_esp12",    "Diámetro extremo derecho",            "12.00 mm",  "S", None,       "plano"),
    ("l_esp12",    "Largo extremo derecho Ø12",           "8.00 mm",   "L", None,       "plano"),
    ("d_aloj_izq", "Diámetro alojamiento interno izq.",   "8.00 mm",   "H", None,       "plano"),
    ("p_aloj_izq", "Profundidad alojamiento interno izq.","15.00 mm",  "L", None,       "plano"),
    ("d_pasador",  "Diámetro agujero transversal pasador","4.00 mm",   "H", None,       "plano"),
    ("z_pasador",  "Posición axial agujero pasador",      "7.52 mm",   "L", None,       "plano"),
]

pz = Pieza("Tornillo_Sin_Fin_14")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Acero_Inoxidable")
p = pz.p
Z_MENOS_1 = "-1 mm"

# --- Cuerpo escalonado (cilindros solapados desde z=0 para unión booleana limpia)
c_rosca = pz.cil("Cil_Rosca_M14", f"{p('d_m14')} / 2", p("l_rosca"))
c_esp13 = pz.cil("Cil_Espiga_13", f"{p('d_esp13')} / 2", f"{p('l_rosca')} + {p('l_esp13')}")
c_esp12 = pz.cil("Cil_Espiga_12", f"{p('d_esp12')} / 2",
                 f"{p('l_rosca')} + {p('l_esp13')} + {p('l_esp12')}")
cuerpo = pz.fusion("Cuerpo_Husillo", [c_rosca, c_esp13, c_esp12])

# --- Herramientas de corte (Detalle AC en extremo izquierdo)
aloj_izq = pz.cil("Alojamiento_Izq", f"{p('d_aloj_izq')} / 2", f"{p('p_aloj_izq')} + 1 mm",
                  z=Z_MENOS_1)
pasador = pz.cil_x("Agujero_Pasador", f"{p('d_pasador')} / 2", f"2 * {p('d_m14')}",
                   x=f"-1 * {p('d_m14')}", z=p("z_pasador"))
vaciado = pz.fusion("Operaciones_Vaciado", [aloj_izq, pasador])
solido = pz.corte("Tornillo_Sin_Fin_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Pasador", z=p("z_pasador"))
pz.lcs("LCS_Fondo_Aloj_Izq", z=p("p_aloj_izq"))
pz.lcs("LCS_Fin_Rosca", z=p("l_rosca"))
pz.lcs("LCS_Extremo_Der", z=f"{p('l_rosca')} + {p('l_esp_der')}")

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
