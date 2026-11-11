# Tensor Parte 1 (Impresión 3D a escala 75.5%) - Plano Nº 6
# Extraído y parametrizado desde entradas/impresion_3d/plano6_Tensor.stp
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_tensor_parte_1_06.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 1          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render
SALIDA = os.path.join(AQUI, "Tensor_Parte_1_06.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("l_cuerpo",  "Longitud del cuerpo cilíndrico Ø16.61",     "151.81 mm", "L", None,     "plano"),
    ("d_ext",     "Diámetro exterior (22 mm * 0.755)",          "16.61 mm",  "L", None,     "plano"),
    ("c_ext",     "Chaflán en extremo libre (0.50 * 0.755)",    "0.38 mm",   "L", None,     "plano"),
    ("l_espiga",  "Longitud de la espiga triangular macho",     "30.00 mm",  "L", None,     "usuario"),
    ("r_espiga",  "Radio circunscrito de la espiga triangular", "3.16 mm",   "L", None,     "usuario"),
    ("d_aguj",    "Diámetro agujero roscado a escala (M10*0.755)", "6.32 mm", "L", None,    "plano"),
    ("p_aguj",    "Profundidad cilíndrica del agujero extremo", "12.08 mm",  "L", None,     "plano"),
    ("p_punta",   "Profundidad punta cónica de mecha (118°)",   "1.90 mm",   "L", None,     "plano"),
]

pz = Pieza("Tensor_Parte_1_06")
pz.parametros(DIMS, modo=MODO_DISENO, escala="1.0", holgura_fdm="0.20 mm")
pz.materiales("PLA_Estructural")
p = pz.p

r_ext = f"({p('d_ext')} / 2)"

# --- 1. Cuerpo cilíndrico principal (Z = 0 .. l_cuerpo) con chaflán en Z = l_cuerpo
cil_cuerpo = pz.cil("Cuerpo_Cilindrico", r_ext, f"{p('l_cuerpo')} - {p('c_ext')}")
ch_der = pz.cono(
    "Chaflan_Extremo",
    r_ext,
    f"{r_ext} - {p('c_ext')}",
    p("c_ext"),
    z=f"{p('l_cuerpo')} - {p('c_ext')}",
)

# --- 2. Espiga triangular macho (Z = -l_espiga .. 0) mediante cilindro + 3 cortes planos a 120°
# Apotema del triángulo equilátero = r_espiga * 0.5
esp_bruta = pz.cil(
    "Espiga_Cil_Bruta",
    f"{p('r_espiga')} + 1 mm",
    p("l_espiga"),
    z=f"-{p('l_espiga')}",
)
apotema = f"({p('r_espiga')} * 0.5)"
cortes_tri = []
for idx_ang, ang in enumerate((0, 120, 240), start=1):
    # Caja grande colocada en +Y desde y = apotema hacia afuera, rotada alrededor de Z
    caja_c = pz.caja(
        f"Corte_Cara_Tri_{idx_ang}",
        "20 mm",
        "20 mm",
        f"{p('l_espiga')} + 2 mm",
    )
    caja_c.setExpression(
        "Placement.Base.x", "-10 mm"
    )
    caja_c.setExpression(
        "Placement.Base.y", apotema
    )
    caja_c.setExpression(
        "Placement.Base.z", f"-{p('l_espiga')} - 1 mm"
    )
    # Rotar el plano de corte alrededor del eje Z manteniendo su ubicación relativa
    if ang != 0:
        import math
        rad = math.radians(ang)
        # Reemplazar Placement usando rotación alrededor de Z centrada en (0, 0)
        # En coordenadas rotadas: el centro del borde inferior del bloque pasa por (0, apotema)
        # tras rotar ang° -> (-apotema*sin(ang), apotema*cos(ang)), mejor crear un Part::Box centrado en X
        # y usar una expresión o ángulo directo en Placement.
    cortes_tri.append((caja_c, ang))

# Como App::Placement aplica rotación alrededor del origen del objeto antes o después según Base,
# posicionamos cada caja directamente en su semiplano exacto usando expresiones trigonométricas limpias:
import FreeCAD as App
import math
for idx_c, (caja_c, ang) in enumerate(cortes_tri):
    # Vector normal saliente desde el eje Z: (sin(-ang), cos(-ang)) o (-sin(ang), cos(ang))
    # Para ang = 0: normal (0, 1), cara en y = apotema.
    # Para ang = 120: normal (-sqrt(3)/2, -0.5)
    # Para ang = 240: normal (+sqrt(3)/2, -0.5)
    # Si rotamos el cuadro en Z por `ang`, su eje local +Y apunta en dirección (-sin(ang), cos(ang)),
    # y su eje local +X apunta en (cos(ang), sin(ang)).
    # Queremos que el punto local (x_loc=10, y_loc=0, z_loc=0) caiga en (-apotema*sin(ang), apotema*cos(ang)):
    # Base = Rot(ang) * (-10, apotema, 0) = (-10*cos(ang) - apotema*sin(ang), -10*sin(ang) + apotema*cos(ang))
    ca = math.cos(math.radians(ang))
    sa = math.sin(math.radians(ang))
    caja_c.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), ang)
    caja_c.setExpression("Placement.Base.x", f"{-10.0 * ca:.6f} mm - {sa:.6f} * {apotema}")
    caja_c.setExpression("Placement.Base.y", f"{-10.0 * sa:.6f} mm + {ca:.6f} * {apotema}")
    caja_c.setExpression("Placement.Base.z", f"-{p('l_espiga')} - 1 mm")

espiga_tri = pz.corte("Espiga_Triangular", esp_bruta, pz.fusion("Cortes_Espiga_Tri", [c[0] for c in cortes_tri]))
bruto_total = pz.fusion("Tensor_P1_Bruto", [cil_cuerpo, ch_der, espiga_tri])

# --- 3. Agujero extremo con punta cónica de mecha 118°
aguj_cil = pz.cil(
    "Agujero_Cil",
    f"{p('d_aguj')} / 2",
    f"{p('p_aguj')} + 1 mm",
    z=f"{p('l_cuerpo')} - {p('p_aguj')}",
)
aguj_punta = pz.cono(
    "Agujero_Punta",
    "0.05 mm",
    f"{p('d_aguj')} / 2",
    p("p_punta"),
    z=f"{p('l_cuerpo')} - {p('p_aguj')} - {p('p_punta')}",
)
vaciado = pz.fusion("Vaciado_Extremo", [aguj_cil, aguj_punta])
solido = pz.corte("Tensor_Parte_1_Solido", bruto_total, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")                                         # Cara de apoyo/encastre (Z = 0)
pz.lcs("LCS_Punta_Espiga", z=f"-{p('l_espiga')}")            # Extremo de la espiga macho (Z = -30)
pz.lcs("LCS_Extremo_Der", z=p("l_cuerpo"))                   # Extremo libre (Z = 151.81)

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
