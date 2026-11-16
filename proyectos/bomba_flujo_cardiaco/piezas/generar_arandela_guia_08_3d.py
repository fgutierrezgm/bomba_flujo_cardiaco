"""Arandela impresa 3D de asiento para Tuerca_Guia_08_3D sobre Tapa_Interior_16b_3D.

Se aloja en el rebaje cilíndrico Ø13.59 mm (profundidad 1.744 mm, Z = 20.906..22.650 mm)
de la Tapa_Interior_16b_3D y sobresale 2.256 mm por encima de la cara superior de la tapa
para que las aristas del hexágono de Tuerca_Guia_08_3D (entre vértices Ø15.01 mm) apoyen
sin tocar ni dañar el material de la tapa al ajustar.
"""
import os
import sys

RUTA_SCRIPT = os.path.abspath(__file__)
DIR_PROYECTO = os.path.dirname(os.path.dirname(RUTA_SCRIPT))
RAIZ_REPO = os.path.dirname(os.path.dirname(DIR_PROYECTO))
sys.path.insert(0, os.path.join(RAIZ_REPO, "_herramientas"))

from fc_helpers import Pieza  # noqa: E402

SALIDA = os.path.join(DIR_PROYECTO, "piezas", "Arandela_Guia_08_3D.FCStd")

# Modo 1: Impresión 3D FDM (PLA+/PETG, holgura radial 0.20 mm)
DIMS = [
    ("d_ext",   "Diámetro exterior nominal (alojamiento Ø13.59 mm en Tapa_Interior_16b_3D)", "13.59 mm", "S", "", "calculado"),
    ("d_int",   "Diámetro interior nominal (paso holgado para Guia_08_3D Ø6.71..6.86 mm)",   "7.20 mm",  "H", "", "calculado"),
    ("h_total", "Espesor axial total (1.744 mm dentro del hueco + 2.256 mm saliente)",       "4.00 mm",  "L", "", "calculado"),
    ("c_borde", "Chaflán 45 deg en aristas exteriores e interiores",                         "0.40 mm",  "L", "", "calculado"),
]

MAT_ARANDELA_3D = {
    "nombre": "PLA+/PETG Estructural (Impresión 3D)",
    "densidad_num": "0.00000124",
    "densidad_desc": "1.24 g / cm^3",
    "color": (0.92, 0.65, 0.18),
    "transparencia": 0,
}

pz = Pieza("Arandela_Guia_08_3D", ruta_salida=SALIDA, ruta_script=RUTA_SCRIPT)
pz.parametros(DIMS, modo=1, escala="1.0", holgura_fdm="0.20 mm")
pz.materiales(MAT_ARANDELA_3D, origen="calculado")
p = pz.p

r_ext = f"{p('d_ext')} / 2"
r_int = f"{p('d_int')} / 2"
h_tot = p("h_total")
c = p("c_borde")

# Cuerpo exterior: chaflán inferior + tramo cilíndrico central + chaflán superior
ext_inf = pz.cono(
    "Ext_Chaflan_Inf",
    radio1 := f"{r_ext} - {c}",
    r_ext,
    c,
    z="0 mm",
)
ext_cen = pz.cil(
    "Ext_Cilindro",
    r_ext,
    f"{h_tot} - 2 * {c}",
    z=c,
)
ext_sup = pz.cono(
    "Ext_Chaflan_Sup",
    r_ext,
    radio1,
    c,
    z=f"{h_tot} - {c}",
)
cuerpo_ext = pz.fusion("Cuerpo_Exterior", [ext_inf, ext_cen, ext_sup])

# Herramienta de corte interior: agujero pasante + chaflanes a 45 deg sin caras coplanares
agujero = pz.cil("Agujero_Paso", r_int, f"{h_tot} + 2 mm", z="-1 mm")
ch_int_inf = pz.cono(
    "Chaflan_Int_Inf",
    f"{r_int} + {c} + 0.5 mm",
    r_int,
    f"{c} + 0.5 mm",
    z="-0.5 mm",
)
ch_int_sup = pz.cono(
    "Chaflan_Int_Sup",
    r_int,
    f"{r_int} + {c} + 0.5 mm",
    f"{c} + 0.5 mm",
    z=f"{h_tot} - {c}",
)
tool_int = pz.fusion("Tool_Agujero_Chaflanes", [agujero, ch_int_inf, ch_int_sup])

solido = pz.corte("Arandela_Guia_08_3D_Solido", cuerpo_ext, tool_int)

# Conectores funcionales: apoyo en fondo del rebaje (z=0) y asiento de tuerca (z=h_total)
pz.lcs("LCS_Origen", z="0 mm")
pz.lcs("LCS_Cara_Sup", z=h_tot)

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
