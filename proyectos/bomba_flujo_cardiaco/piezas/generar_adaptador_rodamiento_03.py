# Adaptador de rodamiento - Plano Nº 3 (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/generar_adaptador_rodamiento_03.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Adaptador_Rodamiento_03.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("h_total",    "Altura total del adaptador",               "25.50 mm", "L", None, "plano"),
    ("d_brida",    "Diámetro exterior brida base",             "55.00 mm", "L", None, "plano"),
    ("h_brida",    "Altura brida base",                        "5.00 mm",  "L", None, "plano"),
    ("d_cuerpo1",  "Diámetro escalón intermedio",              "40.00 mm", "S", None, "plano"),
    ("z_ref_882",  "Cota referencia escalón Ø40",              "8.82 mm",  "L", None, "plano"),
    ("z_esc",      "Inicio cuerpo superior Ø37.50",            "11.68 mm", "L", None, "plano"),
    ("d_cuerpo2",  "Diámetro cuerpo superior",                 "37.50 mm", "S", None, "plano"),
    ("d_paso",     "Diámetro agujero central pasante (holgura collar)", "16.00 mm", "H", None, "usuario"),
    ("d_aloj_rod", "Diámetro alojamiento rodamiento SKF 6201", "32.00 mm", "H", None, "plano"),
    ("p_aloj_rod", "Profundidad alojamiento rodamiento 6201",  "10.50 mm", "L", None, "plano"),
    ("d_rebaje",   "Diámetro rebaje bajo rodamiento (holgura collar)",  "16.00 mm", "H", None, "usuario"),
    ("p_rebaje",   "Profundidad rebaje bajo rodamiento",       "5.00 mm",  "L", None, "plano"),
    ("d_cor",      "Círculo de agujeros de brida",             "49.00 mm", "L", None, "plano"),
    ("d_aguj",     "Diámetro agujeros pasantes de brida",      "3.10 mm",  "H", None, "plano"),
    ("d_avell",    "Diámetro avellanado agujeros brida",       "4.00 mm",  "H", None, "plano"),
    ("p_avell",    "Profundidad avellanado 90° en brida",      "0.45 mm",  "L", None, "plano"),
    ("c_chaf",     "Chaflanes 0.50 x 45°",                     "0.50 mm",  "L", None, "plano"),
    ("z_asiento_eje", "Cota axial asiento con Adaptador Eje",  "5.50 mm",  "L", None, "calculado"),
]

pz = Pieza("Adaptador_Rodamiento_03")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("Laton")
p = pz.p

r_bri = f"({p('d_brida')} / 2)"
r_c1 = f"({p('d_cuerpo1')} / 2)"
r_c2 = f"({p('d_cuerpo2')} / 2)"
r_aloj = f"({p('d_aloj_rod')} / 2)"
z_piso_rod = f"({p('h_total')} - {p('p_aloj_rod')})"

# --- Cuerpo exterior escalonado
cil_brida = pz.cil("Cil_Brida_55", r_bri, p("h_brida"))
cil_cuerpo1 = pz.cil("Cil_Escal_40", r_c1, f"{p('z_esc')} - {p('h_brida')}", z=p("h_brida"))
cil_cuerpo2 = pz.cil("Cil_Cuerpo_37_5", r_c2,
                     f"{p('h_total')} - {p('z_esc')} - {p('c_chaf')}",
                     z=p("z_esc"))
ch_sup_ext = pz.cono("Chaflan_Sup_Ext", r_c2, f"{r_c2} - {p('c_chaf')}", p("c_chaf"),
                     z=f"{p('h_total')} - {p('c_chaf')}")

cuerpo = pz.fusion("Cuerpo_Exterior", [cil_brida, cil_cuerpo1, cil_cuerpo2, ch_sup_ext])

# --- Vaciados interiores y corona de 4 agujeros con avellanado
cortes = [
    pz.cil("Agujero_Central_13_1", f"{p('d_paso')} / 2", f"{p('h_total')} + 2 mm", z="-1 mm"),
    pz.cil("Alojamiento_6201_32", r_aloj, f"{p('p_aloj_rod')} + 1 mm", z=z_piso_rod),
    pz.cono("Chaflan_Boca_6201", r_aloj, f"{r_aloj} + {p('c_chaf')}", p("c_chaf"),
            z=f"{p('h_total')} - {p('c_chaf')}"),
    pz.cil("Aux_Boca_6201", f"{r_aloj} + {p('c_chaf')}", "1 mm", z=p("h_total")),
    pz.cil("Rebaje_15", f"{p('d_rebaje')} / 2", f"{p('p_rebaje')} + 1 mm",
           z=f"{z_piso_rod} - {p('p_rebaje')}"),
]

for i, ang in enumerate((0, 90, 180, 270), 1):
    x_pos = f"({p('d_cor')} / 2) * cos({ang} deg)"
    y_pos = f"({p('d_cor')} / 2) * sin({ang} deg)"
    cortes.append(pz.cil(f"Aguj_Brida_{i}", f"{p('d_aguj')} / 2", f"{p('h_brida')} + 2 mm",
                         x=x_pos, y=y_pos, z="-1 mm"))
    cortes.append(pz.cono(f"Avell_Brida_{i}", f"{p('d_avell')} / 2", f"{p('d_aguj')} / 2",
                          p("p_avell"), x=x_pos, y=y_pos, z="0 mm"))
    cortes.append(pz.cil(f"Aux_Avell_{i}", f"{p('d_avell')} / 2", "1 mm",
                         x=x_pos, y=y_pos, z="-1 mm"))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Adaptador_Rodamiento_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Cara_Brida", z=p("h_brida"))
pz.lcs("LCS_Asiento_Adaptador_Eje", z=p("z_asiento_eje"))
pz.lcs("LCS_Asiento_Rodamiento_6201", z=z_piso_rod)
pz.lcs("LCS_Tope_Superior", z=p("h_total"))

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
