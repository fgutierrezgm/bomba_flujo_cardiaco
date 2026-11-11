# Émbolo de Delrin - Plano Nº 10 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_embolo_delrin_10.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Embolo_Delrin_10.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",       "Diámetro exterior del émbolo",                 "102.00 mm", "S", None,      "plano"),
    ("h_total",     "Espesor axial total del émbolo",               "20.00 mm",  "L", None,      "plano"),
    ("d_int",       "Agujero central para núcleo",                  "30.00 mm",  "H", None,      "plano"),
    ("c_ch",        "Chaflanes exteriores e interiores (1.00x45°)", "1.00 mm",   "L", None,      "plano"),
    ("a_ran",       "Ancho axial ranura para o-ring (Viton 97x3.5)","4.13 mm",   "L", None,      "plano"),
    ("p_ran",       "Profundidad radial ranura para o-ring",        "2.93 mm",   "L", None,      "plano"),
    ("z_ran",       "Posición axial ranura desde Z=0",              "8.00 mm",   "L", None,      "plano"),
    ("d_c75",       "Círculo de posición de guías y sensores M8",   "75.00 mm",  "L", None,      "plano"),
    ("d_aloj_guia", "Agujeros pasantes para bujes guía (2x)",       "14.00 mm",  "H", None,      "plano"),
    ("d_cor_m3",    "Corona de agujeros roscados M3 (4x cara Z=0)", "37.40 mm",  "L", None,      "plano"),
    ("d_m3",        "Rosca M3x0.5 (4x cara Z=0)",                   "3.00 mm",   "R", "2.50 mm", "plano"),
    ("p_m3",        "Profundidad roscas M3x0.5",                    "8.00 mm",   "L", None,      "plano"),
    ("d_m8",        "Rosca ciega M8x1.25 - 6H para topes FC (2x)",  "8.00 mm",   "R", "6.80 mm", "plano"),
    ("p_m8",        "Profundidad roscas ciegas M8x1.25 (sin fuga)", "8.00 mm",   "L", None,      "usuario"),
    ("ang_m8_1",    "Ángulo tope FC en cara Z=0 (hacia Tapa 16b)",  "45 deg",    "N", None,      "usuario"),
    ("ang_m8_2",    "Ángulo tope FC en cara Z=h_total (Tapa 16a)",  "315 deg",   "N", None,      "usuario"),
]

pz = Pieza("Embolo_Delrin_10")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Delrin")
p = pz.p

r_ext = f"({p('d_ext')} / 2)"
r_int = f"({p('d_int')} / 2)"

# --- Cuerpo exterior con chaflanes de 1.00 x 45° en ambas caras (sin usar índices de arista)
ch_ext_inf = pz.cono("Chaflan_Ext_Inf", f"{r_ext} - {p('c_ch')}", r_ext, p("c_ch"))
cil_cuerpo = pz.cil("Cil_Cuerpo", r_ext, f"{p('h_total')} - 2 * {p('c_ch')}", z=p("c_ch"))
ch_ext_sup = pz.cono("Chaflan_Ext_Sup", r_ext, f"{r_ext} - {p('c_ch')}", p("c_ch"),
                     z=f"{p('h_total')} - {p('c_ch')}")
cuerpo = pz.fusion("Cuerpo_Base", [ch_ext_inf, cil_cuerpo, ch_ext_sup])

# --- Herramientas de corte
cortes = []

# 1. Agujero central Ø30.00 con sus chaflanes interiores de 1.00 x 45° en ambas caras
cortes.append(pz.cil("Aguj_Central_30", r_int, f"{p('h_total')} + 2 mm", z="-1 mm"))
cortes.append(pz.cono("Chaflan_Int_Inf",
                      f"{r_int} + {p('c_ch')} + 1 mm", r_int,
                      f"{p('c_ch')} + 1 mm", z="-1 mm"))
cortes.append(pz.cono("Chaflan_Int_Sup",
                      r_int, f"{r_int} + {p('c_ch')} + 1 mm",
                      f"{p('c_ch')} + 1 mm", z=f"{p('h_total')} - {p('c_ch')}"))

# 2. Ranura perimetral para junta tórica (anillo entre r_ext - p_ran y r_ext + 1 mm en z = z_ran)
cil_ran_ext = pz.cil("Ranura_Ext", f"{r_ext} + 1 mm", p("a_ran"), z=p("z_ran"))
cil_ran_int = pz.cil("Ranura_Int", f"{r_ext} - {p('p_ran')}", f"{p('a_ran')} + 2 mm",
                     z=f"{p('z_ran')} - 1 mm")
anillo_ranura = pz.corte("Anillo_Ranura_ORing", cil_ran_ext, cil_ran_int)
pz.auxiliares.append(anillo_ranura)
cortes.append(anillo_ranura)

# 3. Dos agujeros pasantes Ø14.00 para bujes guía sobre d_c75 a 0° y 180°
for i, s in enumerate((-1, 1), 1):
    cortes.append(pz.cil(f"Aloj_Guia_{i}", f"{p('d_aloj_guia')} / 2", f"{p('h_total')} + 2 mm",
                         x=f"{s} * ({p('d_c75')} / 2)", z="-1 mm"))

# 4. Cuatro agujeros roscados M3x0.5 (prof. 8.00 mm) sobre Ø37.40 en cara Z=0 (hacia Centro_Embolo_1_11)
for i, ang in enumerate((0, 90, 180, 270), 1):
    x_m3 = f"({p('d_cor_m3')} / 2) * cos({ang} deg)"
    y_m3 = f"({p('d_cor_m3')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"M3_Inf_{i}", f"{p('d_m3')} / 2", f"{p('p_m3')} + 1 mm",
                         x=x_m3, y=y_m3, z="-1 mm"))

# 5. Dos agujeros roscados M8x1.25 - 6H sobre Ø75.00: uno en Z=0 (135°) y otro en Z=h_total (45°)
cortes.append(pz.cil("M8_Sensor_1", f"{p('d_m8')} / 2", f"{p('p_m8')} + 1 mm",
                     x=f"({p('d_c75')} / 2) * cos({p('ang_m8_1')})",
                     y=f"({p('d_c75')} / 2) * sin({p('ang_m8_1')})",
                     z="-1 mm"))
cortes.append(pz.cil("M8_Sensor_2", f"{p('d_m8')} / 2", f"{p('p_m8')} + 1 mm",
                     x=f"({p('d_c75')} / 2) * cos({p('ang_m8_2')})",
                     y=f"({p('d_c75')} / 2) * sin({p('ang_m8_2')})",
                     z=f"{p('h_total')} - {p('p_m8')}"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Embolo_Delrin_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Sup", z=p("h_total"))
pz.lcs("LCS_Ranura_ORing", z=p("z_ran"))
pz.lcs("LCS_Guia_1", x=f"-1 * ({p('d_c75')} / 2)")
pz.lcs("LCS_Guia_2", x=f"{p('d_c75')} / 2")
pz.lcs("LCS_Sensor_1",
       x=f"({p('d_c75')} / 2) * cos({p('ang_m8_1')})",
       y=f"({p('d_c75')} / 2) * sin({p('ang_m8_1')})")
pz.lcs("LCS_Sensor_2",
       x=f"({p('d_c75')} / 2) * cos({p('ang_m8_2')})",
       y=f"({p('d_c75')} / 2) * sin({p('ang_m8_2')})",
       z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
