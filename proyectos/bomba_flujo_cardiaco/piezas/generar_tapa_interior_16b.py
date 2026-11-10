# Tapa interior - Plano Nº 16b (bomba de simulación de flujo cardíaco)
# Sin interfaz:  /snap/bin/freecad.cmd generar_tapa_interior_16b.py
# Sigue la misma convención de ejes que generar_tapa_exterior_16a.py:
#   z = 0 en cara trasera, z = 25.50 en brida, z = 30.00 en tope del resalte Ø145.
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

MODO_DISENO = 2          # 1 = Impresión 3D | 2 = CNC / Planos | 3 = Render (valor inicial de B2)
SALIDA = os.path.join(AQUI, "Tapa_Interior_16b.FCStd")

# (alias, descripción, nominal, tipo, mecha, origen)
DIMS = [
    ("d_ext",          "Diámetro total brida",                        "160.00 mm", "L", None,       "plano"),
    ("h_base",         "Altura base exterior",                        "25.50 mm",  "L", None,       "plano"),
    ("d_enc",          "Resalte de encastre",                         "145.00 mm", "S", None,       "plano"),
    ("h_enc",          "Altura resalte (Z total 30 mm)",              "4.50 mm",   "L", None,       "plano"),
    ("d_cav1",         "Cavidad 1 (alojamiento tórica)",              "120.10 mm", "H", None,       "plano"),
    ("p_cav1",         "Prof. cavidad 1",                             "6.90 mm",   "L", None,       "plano"),
    ("d_cav2",         "Cavidad 2 (asiento tubo de vidrio)",          "110.50 mm", "H", None,       "plano"),
    ("p_cav2",         "Prof. cavidad 2",                             "8.10 mm",   "L", None,       "plano"),
    ("d_cav3",         "Diámetro interior borde rebaje central",      "40.00 mm",  "H", None,       "plano"),
    ("p_cav3",         "Espesor tabique central (Detalle AF)",        "3.00 mm",   "L", None,       "plano"),
    ("d_paso_central", "Agujero central pasante husillo",             "15.00 mm",  "H", None,       "plano"),
    ("d_reb1",         "Rebaje trasero 1 (tapa sufridera)",           "45.10 mm",  "H", None,       "plano"),
    ("p_reb1",         "Prof. rebaje trasero 1",                      "2.31 mm",   "L", None,       "plano"),
    ("d_reb2",         "Rebaje trasero 2 (sufridera int.)",           "41.00 mm",  "H", None,       "plano"),
    ("p_reb2",         "Prof. adicional rebaje trasero 2",            "9.69 mm",   "L", None,       "plano"),
    ("d_c75",          "Círculo de guías y puertos",                  "75.00 mm",  "L", None,       "plano"),
    ("d_guia_paso",    "Agujero pasante para espiga de guía (2x)",    "10.10 mm",  "H", None,       "plano"),
    ("d_caj_guia",     "Cajeado interno de guía (2x)",                "20.10 mm",  "H", None,       "plano"),
    ("p_caj_guia",     "Prof. cajeado interno de guía",               "6.00 mm",   "L", None,       "plano"),
    ("d_cor_guia",     "Círculo 4x M3 en fondo de cajeado de guía",   "15.00 mm",  "L", None,       "plano"),
    ("p_m3_guia",      "Prof. M3 en fondo de cajeado de guía",        "4.00 mm",   "L", None,       "plano"),
    ("ang_m12",        "Posición angular del puerto M12x1",           "45 deg",    "N", None,       "plano"),
    ("d_m12",          "Puerto M12x1 para sensor inductivo",          "12.00 mm",  "R", "11.00 mm", "norma"),
    ("d_g18",          "Puerto G 1/8 (2x)",                           "9.73 mm",   "R", "8.80 mm",  "norma"),
    ("p_g18",          "Prof. rosca G 1/8",                           "8.00 mm",   "L", None,       "plano"),
    ("d_pasaje_g18",   "Pasaje bajo puerto G 1/8 (no acotado)",       "4.00 mm",   "H", None,       "supuesto"),
    ("d_m3",           "Agujeros roscados M3x0.5",                    "3.00 mm",   "R", "2.50 mm",  "norma"),
    ("d_cor_ext",      "Corona exterior 6x M3",                       "152.50 mm", "L", None,       "plano"),
    ("p_m3_ext",       "Prof. M3 corona exterior",                    "6.00 mm",   "L", None,       "plano"),
    ("d_cor_med",      "Corona media 6x M3 (anillo tórica)",          "130.00 mm", "L", None,       "plano"),
    ("p_m3_med",       "Prof. M3 corona media",                       "4.00 mm",   "L", None,       "plano"),
    ("d_cor_tras",     "Corona trasera 4x M3 (adaptador eje)",        "50.02 mm",  "L", None,       "plano"),
    ("p_m3_tras",      "Prof. M3 corona trasera",                     "7.00 mm",   "L", None,       "plano"),
]

pz = Pieza("Tapa_Interior_16b")
pz.parametros(DIMS, modo=MODO_DISENO)
pz.materiales("PVC_Rigido")
p = pz.p
Z_MENOS_1 = "-1 mm"

# --- Cuerpo exterior
c_base = pz.cil("Cil_Base", f"{p('d_ext')} / 2", p("h_base"))
c_enc = pz.cil("Cil_Encastre", f"{p('d_enc')} / 2", f"{p('h_base')} + {p('h_enc')}")
cuerpo = pz.fusion("Cuerpo_Principal", [c_base, c_enc])

z_tope = f"({p('h_base')} + {p('h_enc')})"
z_piso1 = f"({z_tope} - {p('p_cav1')})"
z_piso2 = f"({z_piso1} - {p('p_cav2')})"              # z = 15.00 mm (piso de cámara)
z_techo_reb = f"({z_piso2} - {p('p_cav3')})"          # z = 12.00 mm (techo del rebaje trasero)
ch_reb2 = f"(({p('d_reb2')} - {p('d_cav3')}) / 2)"    # 0.50 mm (chaflán .50x45° entre Ø41 y Ø40)

# --- Herramientas de corte
cortes = [
    # Cavidades desde cara interna (z_tope = 30.00 mm)
    pz.cil("Cavidad_1", f"{p('d_cav1')} / 2", f"{p('p_cav1')} + 1 mm", z=z_piso1),
    pz.cil("Cavidad_2", f"{p('d_cav2')} / 2", f"{p('p_cav2')} + 1 mm", z=z_piso2),
    # Agujero central pasante Ø15.00 mm a través del tabique central (z = 12.00..15.00 mm)
    pz.cil("Agujero_Central", f"{p('d_paso_central')} / 2", f"{z_tope} + 2 mm", z=Z_MENOS_1),
    # Rebajes traseros desde z = 0 (Detalle AF: 2.31 + 9.69 = 12.00 mm, dejando 3.00 mm de tabique)
    pz.cil("Rebaje_Trasero_1", f"{p('d_reb1')} / 2", f"{p('p_reb1')} + 1 mm", z=Z_MENOS_1),
    pz.cil("Rebaje_Trasero_2", f"{p('d_reb2')} / 2",
           f"{p('p_reb1')} + {p('p_reb2')} - {ch_reb2} + 1 mm", z=Z_MENOS_1),
    pz.cono("Chaflan_Rebaje_40",
            f"{p('d_reb2')} / 2 + 1 mm",
            f"{p('d_cav3')} / 2",
            f"{ch_reb2} + 1 mm",
            z=f"{z_techo_reb} - {ch_reb2} - 1 mm"),
]

# 2 alojamientos para guías a 0° y 180° sobre d_c75
for i, s in enumerate((-1, 1), 1):
    x_guia = f"{s} * {p('d_c75')} / 2"
    cortes.append(pz.cil(f"Paso_Guia_{i}", f"{p('d_guia_paso')} / 2", f"{z_tope} + 2 mm",
                         x=x_guia, z=Z_MENOS_1))
    cortes.append(pz.cil(f"Cajeado_Guia_{i}", f"{p('d_caj_guia')} / 2", f"{p('p_caj_guia')} + 1 mm",
                         x=x_guia, z=f"{z_piso2} - {p('p_caj_guia')}"))
    for j, ang in enumerate((0, 90, 180, 270), 1):
        cortes.append(pz.cil(f"M3_Guia_{i}_{j}", f"{p('d_m3')} / 2", f"{p('p_m3_guia')} + 1 mm",
                             x=f"{x_guia} + ({p('d_cor_guia')} / 2) * cos({ang} deg)",
                             y=f"({p('d_cor_guia')} / 2) * sin({ang} deg)",
                             z=f"{z_piso2} - {p('p_caj_guia')} - {p('p_m3_guia')}"))

# 2 puertos G 1/8 a 90° y 270° sobre d_c75 desde cara trasera z = 0
for i, s in enumerate((1, -1), 1):
    y_puerto = f"{s} * {p('d_c75')} / 2"
    cortes.append(pz.cil(f"Puerto_G1_8_{i}", f"{p('d_g18')} / 2", f"{p('p_g18')} + 1 mm",
                         y=y_puerto, z=Z_MENOS_1))
    cortes.append(pz.cil(f"Pasaje_G1_8_{i}", f"{p('d_pasaje_g18')} / 2", p("h_base"),
                         y=y_puerto, z=Z_MENOS_1))

# 1 puerto M12x1 a 45° sobre d_c75 pasante hasta cámara
cortes.append(pz.cil("Puerto_M12x1", f"{p('d_m12')} / 2", p("h_base"),
                     x=f"({p('d_c75')} / 2) * cos({p('ang_m12')})",
                     y=f"({p('d_c75')} / 2) * sin({p('ang_m12')})",
                     z=Z_MENOS_1))

# Coronas de 6x M3x0.5 en cara de brida (d_cor_ext) y en tope (d_cor_med)
for suf, d_cor, p_m3, z_cara in (("Ext", "d_cor_ext", "p_m3_ext", p("h_base")),
                                 ("Med", "d_cor_med", "p_m3_med", z_tope)):
    for i, ang in enumerate((0, 60, 120, 180, 240, 300), 1):
        cortes.append(pz.cil(f"M3_{suf}_{i}", f"{p('d_m3')} / 2", f"{p(p_m3)} + 1 mm",
                             x=f"({p(d_cor)} / 2) * cos({ang} deg)",
                             y=f"({p(d_cor)} / 2) * sin({ang} deg)",
                             z=f"{z_cara} - {p(p_m3)}"))

# Corona trasera de 4x M3x0.5 sobre d_cor_tras = 50.02 mm desde z = 0
for i, ang in enumerate((45, 135, 225, 315), 1):
    cortes.append(pz.cil(f"M3_Tras_{i}", f"{p('d_m3')} / 2", f"{p('p_m3_tras')} + 1 mm",
                         x=f"({p('d_cor_tras')} / 2) * cos({ang} deg)",
                         y=f"({p('d_cor_tras')} / 2) * sin({ang} deg)",
                         z=Z_MENOS_1))

vaciado = pz.fusion("Operaciones_Vaciado", cortes)
solido = pz.corte("Tapa_Interior_Solido", cuerpo, vaciado)

# --- Conectores LCS
pz.lcs("LCS_Origen")
pz.lcs("LCS_Asiento_Carcasa_145mm", z=p("h_base"))
pz.lcs("LCS_Piso_Tubo_110_5", z=z_piso2)
pz.lcs("LCS_Guia_1", x=f"-1 * {p('d_c75')} / 2", z=z_piso2)
pz.lcs("LCS_Guia_2", x=f"{p('d_c75')} / 2", z=z_piso2)
pz.lcs("LCS_Puerto_M12x1",
       x=f"({p('d_c75')} / 2) * cos({p('ang_m12')})",
       y=f"({p('d_c75')} / 2) * sin({p('ang_m12')})")
pz.lcs("LCS_Racor_G1_8_Sup", y=f"{p('d_c75')} / 2")
pz.lcs("LCS_Racor_G1_8_Inf", y=f"-1 * {p('d_c75')} / 2")

pz.reporte_fisico(solido)
pz.cerrar(solido, SALIDA)
