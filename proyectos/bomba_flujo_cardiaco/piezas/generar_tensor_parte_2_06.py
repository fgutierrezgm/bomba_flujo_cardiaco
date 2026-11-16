# Tensor Parte 2 (Impresión 3D a escala 75.5%) - Plano Nº 6
# Extraído y parametrizado desde entradas/impresion_3d/plano6_Tensor.stp
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_tensor_parte_2_06.py
import math
import os
import sys
import FreeCAD as App

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 1          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render
SALIDA = os.path.join(AQUI, "Tensor_Parte_2_06.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_cuerpo",    "Longitud total de la Parte 2",                "139.09 mm", "L", None, "plano"),
    ("l_rebaje",    "Longitud tramo extremo reducido (19 * 0.755)", "14.35 mm",  "L", None, "plano"),
    ("d_ext_mayor", "Diámetro exterior cuerpo grueso (24 * 0.755)", "18.12 mm",  "L", None, "plano"),
    ("d_ext_menor", "Diámetro exterior extremo rebajado (22*0.755)","16.61 mm",  "L", None, "plano"),
    ("c_ext",       "Chaflanes extremos (0.50 * 0.755)",           "0.38 mm",   "L", None, "plano"),
    ("p_cavidad",   "Profundidad cavidad triangular hembra",       "30.00 mm",  "L", None, "usuario"),
    ("r_espiga",    "Radio circunscrito cavidad hembra (R3,25)",   "3.25 mm",   "L", None, "usuario"),
    ("d_aguj",      "Diámetro agujero roscado a escala (M10*0.755)","6.32 mm",  "L", None, "plano"),
    ("p_aguj",      "Profundidad cilíndrica del agujero extremo",  "12.08 mm",  "L", None, "plano"),
    ("p_punta",     "Profundidad punta cónica de mecha (118°)",    "1.90 mm",   "L", None, "plano"),
]

pz = Pieza("Tensor_Parte_2_06")
pz.parametros(DIMS, modo=MODO_DISENO, escala="1.0", holgura_fdm="0.20 mm")
pz.materiales("PLA_Estructural")
p = pz.p

r_mayor = f"({p('d_ext_mayor')} / 2)"
r_menor = f"({p('d_ext_menor')} / 2)"

# --- 1. Tramo extremo rebajado (Z = 0 .. l_rebaje) con chaflán en Z = 0
ch_izq = pz.cono("Chaflan_Izq", f"{r_menor} - {p('c_ext')}", r_menor, p("c_ext"))
cil_menor = pz.cil(
    "Tramo_Menor",
    r_menor,
    f"{p('l_rebaje')} - {p('c_ext')}",
    z=p("c_ext"),
)

# --- 2. Tramo cuerpo grueso (Z = l_rebaje .. l_cuerpo) con chaflanes en ambos extremos
ch_esc = pz.cono(
    "Chaflan_Escalon",
    f"{r_mayor} - {p('c_ext')}",
    r_mayor,
    p("c_ext"),
    z=p("l_rebaje"),
)
cil_mayor = pz.cil(
    "Tramo_Mayor",
    r_mayor,
    f"{p('l_cuerpo')} - {p('l_rebaje')} - 2 * {p('c_ext')}",
    z=f"{p('l_rebaje')} + {p('c_ext')}",
)
ch_der = pz.cono(
    "Chaflan_Encastre",
    r_mayor,
    f"{r_mayor} - {p('c_ext')}",
    p("c_ext"),
    z=f"{p('l_cuerpo')} - {p('c_ext')}",
)
bruto = pz.fusion("Tensor_P2_Bruto", [ch_izq, cil_menor, ch_esc, cil_mayor, ch_der])

# --- 3. Cavidad triangular hembra en Z = (l_cuerpo - p_cavidad) .. l_cuerpo
# Holgura explícita de +0,25 mm en radio (0,125 mm/cara) entre R3,25 hembra y R3,00 macho
cav_bruta = pz.cil(
    "Cavidad_Cil_Bruta",
    f"{p('r_espiga')} + 2 mm",
    f"{p('p_cavidad')} + 1 mm",
    z=f"{p('l_cuerpo')} - {p('p_cavidad')}",
)
apotema_cav = f"({p('r_espiga')} * 0.5)"
cortes_tri = []
for idx_ang, ang in enumerate((0, 120, 240), start=1):
    caja_c = pz.caja(
        f"Corte_Cav_Tri_{idx_ang}",
        "20 mm",
        "20 mm",
        f"{p('p_cavidad')} + 3 mm",
    )
    ca = math.cos(math.radians(ang))
    sa = math.sin(math.radians(ang))
    caja_c.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), ang)
    caja_c.setExpression("Placement.Base.x", f"{-10.0 * ca:.6f} mm - {sa:.6f} * {apotema_cav}")
    caja_c.setExpression("Placement.Base.y", f"{-10.0 * sa:.6f} mm + {ca:.6f} * {apotema_cav}")
    caja_c.setExpression("Placement.Base.z", f"{p('l_cuerpo')} - {p('p_cavidad')} - 1 mm")
    cortes_tri.append(caja_c)

cavidad_tri = pz.corte("Cavidad_Triangular", cav_bruta, pz.fusion("Cortes_Cav_Tri", cortes_tri))

# --- 4. Agujero axial extremo en Z = 0
aguj_cil = pz.cil("Agujero_Cil", f"{p('d_aguj')} / 2", f"{p('p_aguj')} + 1 mm", z="-1 mm")
aguj_punta = pz.cono(
    "Agujero_Punta",
    f"{p('d_aguj')} / 2",
    "0.05 mm",
    p("p_punta"),
    z=p("p_aguj"),
)

vaciado = pz.fusion("Operaciones_Vaciado", [cavidad_tri, aguj_cil, aguj_punta])
solido = pz.corte("Tensor_Parte_2_Solido", bruto, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")                                         # Extremo izquierdo (Z = 0)
pz.lcs("LCS_Hombro_Rebaje", z=p("l_rebaje"))                 # Inicio cuerpo grueso (Z = 14.35)
pz.lcs("LCS_Encastre_Macho", z=p("l_cuerpo"))                # Cara de encastre con Parte 1 (Z = 139.09)

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
