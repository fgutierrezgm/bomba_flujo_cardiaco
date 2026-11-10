# Tapa exterior - Plano Nº 16a (bomba de simulación de flujo cardíaco)
# Sin interfaz:  freecadcmd generar_tapa_exterior_16a.py
# Referencia de estructura para nuevas piezas: ficha -> parámetros -> geometría -> LCS -> reporte -> cerrar.
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Tapa_Exterior_16a.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)  -  ver fc_helpers.py para los tipos
DIMS = [
    ("d_ext",        "Diámetro total brida",              "160.00 mm", "L", None,       "plano"),
    ("h_base",       "Altura base exterior",              "25.50 mm",  "L", None,       "plano"),
    ("d_enc",        "Resalte de encastre",               "145.00 mm", "S", None,       "plano"),
    ("h_enc",        "Altura resalte (Z total 30 mm)",    "4.50 mm",   "L", None,       "plano"),
    ("d_cav1",       "Cavidad 1",                         "120.10 mm", "H", None,       "plano"),
    ("p_cav1",       "Prof. cavidad 1",                   "6.90 mm",   "L", None,       "plano"),
    ("d_cav2",       "Cavidad 2",                         "110.50 mm", "H", None,       "plano"),
    ("p_cav2",       "Prof. cavidad 2",                   "7.10 mm",   "L", None,       "plano"),
    ("d_cav3",       "Cavidad 3 (Detalle G)",             "40.10 mm",  "H", None,       "plano"),
    ("p_cav3",       "Prof. cavidad 3",                   "5.00 mm",   "L", None,       "plano"),
    ("d_cav4",       "Cavidad 4 (fondo)",                 "18.00 mm",  "H", None,       "plano"),
    ("p_cav4",       "Prof. cavidad 4",                   "8.00 mm",   "L", None,       "plano"),
    ("d_c75",        "Círculo de alojamientos y puertos", "75.00 mm",  "L", None,       "plano"),
    ("ang_m12",      "Posición angular del puerto M12x1", "45 deg",    "N", None,       "plano"),
    ("d_aloj14",     "2 alojamientos laterales",          "14.00 mm",  "H", None,       "plano"),
    ("p_aloj14",     "Prof. alojamientos (cota 11.00 ambigua)", "11.00 mm", "L", None,  "supuesto"),
    ("d_pasaje_g18", "Pasaje bajo puerto G1/8 (NO acotado)", "4.00 mm", "H", None,      "supuesto"),
    ("d_m12",        "Puerto M12x1",                      "12.00 mm",  "R", "11.00 mm", "norma"),
    ("d_g18",        "Puerto G 1/8",                      "9.73 mm",   "R", "8.80 mm",  "norma"),
    ("p_g18",        "Prof. rosca G 1/8",                 "8.00 mm",   "L", None,       "plano"),
    ("d_m3",         "Agujeros M3x0.5",                   "3.00 mm",   "R", "2.50 mm",  "norma"),
    ("d_cor_ext",    "Corona exterior 4x M3",             "152.50 mm", "L", None,       "plano"),
    ("p_m3_ext",     "Prof. M3 corona ext.",              "6.00 mm",   "L", None,       "plano"),
    ("d_cor_med",    "Corona media 4x M3",                "130.00 mm", "L", None,       "plano"),
    ("p_m3_med",     "Prof. M3 corona media",             "4.00 mm",   "L", None,       "plano"),
    ("d_cor_int",    "Corona interior 4x M3",             "29.10 mm",  "L", None,       "plano"),
    ("p_m3_int",     "Prof. M3 corona int.",              "4.00 mm",   "L", None,       "plano"),
]

pz = Pieza("Tapa_Exterior_16a")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("PVC_Rigido")
p = pz.p
Z_MENOS_1 = "-1 mm"      # las herramientas de corte arrancan 1 mm bajo la cara trasera

# --- Cuerpo
c_base = pz.cil("Cil_Base", f"{p('d_ext')} / 2", p("h_base"))
c_enc = pz.cil("Cil_Encastre", f"{p('d_enc')} / 2", f"{p('h_base')} + {p('h_enc')}")
cuerpo = pz.fusion("Cuerpo_Principal", [c_base, c_enc])

z_tope = f"({p('h_base')} + {p('h_enc')})"
z_piso = [z_tope]                                    # z_piso[n] = fondo de la cavidad n
for n in range(1, 5):
    z_piso.append(f"({z_piso[-1]} - {p(f'p_cav{n}')})")

# --- Herramientas de corte
cortes = []
for n in range(1, 5):
    cortes.append(pz.cil(f"Cavidad_{n}", f"{p(f'd_cav{n}')} / 2", f"{p(f'p_cav{n}')} + 1 mm",
                         z=z_piso[n]))
for i, s in enumerate((-1, 1), 1):                   # alojamientos Ø14 a 0° y 180°
    cortes.append(pz.cil(f"Alojamiento_14_{i}", f"{p('d_aloj14')} / 2", f"{p('p_aloj14')} + 1 mm",
                         x=f"{s} * {p('d_c75')} / 2", z=f"{z_piso[2]} - {p('p_aloj14')}"))
for i, s in enumerate((1, -1), 1):                   # puertos G 1/8 a 90° y 270°
    y = f"{s} * {p('d_c75')} / 2"
    cortes.append(pz.cil(f"Puerto_G1_8_{i}", f"{p('d_g18')} / 2", f"{p('p_g18')} + 1 mm",
                         y=y, z=Z_MENOS_1))
    cortes.append(pz.cil(f"Pasaje_G1_8_{i}", f"{p('d_pasaje_g18')} / 2", p("h_base"),
                         y=y, z=Z_MENOS_1))
cortes.append(pz.cil("Puerto_M12x1", f"{p('d_m12')} / 2", p("h_base"),
                     x=f"({p('d_c75')} / 2) * cos({p('ang_m12')})",
                     y=f"({p('d_c75')} / 2) * sin({p('ang_m12')})", z=Z_MENOS_1))
for suf, d_cor, p_m3, z_cara in (("Ext", "d_cor_ext", "p_m3_ext", p("h_base")),
                                 ("Med", "d_cor_med", "p_m3_med", z_tope),
                                 ("Int", "d_cor_int", "p_m3_int", z_piso[3])):
    for i, ang in enumerate((0, 90, 180, 270), 1):
        cortes.append(pz.cil(f"M3_{suf}_{i}", f"{p('d_m3')} / 2", f"{p(p_m3)} + 1 mm",
                             x=f"({p(d_cor)} / 2) * cos({ang} deg)",
                             y=f"({p(d_cor)} / 2) * sin({ang} deg)",
                             z=f"{z_cara} - {p(p_m3)}"))
vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Tapa_Exterior_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Asiento_Carcasa_145mm", z=p("h_base"))
pz.lcs("LCS_Racor_G1_8_Sup", y=f"{p('d_c75')} / 2")
pz.lcs("LCS_Racor_G1_8_Inf", y=f"-1 * {p('d_c75')} / 2")
pz.lcs("LCS_Puerto_M12x1", x=f"({p('d_c75')} / 2) * cos({p('ang_m12')})",
       y=f"({p('d_c75')} / 2) * sin({p('ang_m12')})")
pz.lcs("LCS_Aloj_14_1", x=f"-1 * {p('d_c75')} / 2", z=z_piso[2])
pz.lcs("LCS_Aloj_14_2", x=f"{p('d_c75')} / 2", z=z_piso[2])

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
