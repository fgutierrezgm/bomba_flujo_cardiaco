#!/usr/bin/env python3
"""
Importador y normalizador paramétrico de los archivos STEP de Inventor para la rama `impresion-3d`.
Convierte los 20 archivos `.stp` en piezas FreeCAD completas (`*_3D.FCStd`) con:
- Contenedor `App::Part`
- Hoja `Parametros` (Modo 1 = Impresión 3D, escala = 0.755)
- Hoja `Materiales` y apariencia visual
- Hoja `Reporte_Fisico` con volumen y masa real
- Conectores `LCS_Origen`, `LCS_Centro` y `LCS_Cara_Sup` alineados sobre el eje Z

También genera los componentes comerciales adaptados según la LISTA DE PIEZAS:
- `Rodamiento_SKF_609.FCStd` (SKF 609-2Z: Ø9 x Ø24 x 7 mm)
- `Reten_10x22x7.FCStd` (DIN 3760A 10x22x7 mm)
- `ORing_75x3_55.FCStd` (DIN 3771 75x3.55 mm)
- `ORing_69x3_55.FCStd` (DIN 3771 69x3.55 mm)
- `ORing_11_2x1_8.FCStd` (DIN 3771 11.2x1.8 mm)
- `Pasador_3x14.FCStd` (ISO 8752 Ø3x14 mm)
- `Pasador_3x10.FCStd` (ISO 8752 Ø3x10 mm)
- `Cilindro_09_3D.FCStd` (Camisa acrílica a escala: Ø83 x Ø76 x 188.75 mm)

Ejecución:
  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/importar_modelo_3d_steps.py
"""
import os
import shutil
import sys
import FreeCAD as App
import Part

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "pieza.py")))
RAIZ = AQUI
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import Pieza

DIR_ENTRADAS = os.path.join(os.path.dirname(AQUI), "entradas", "impresion_3d")
DIR_CATALOGO = os.path.join(RAIZ, "02_Catalogos_SKF_DIN_ISO")
DIR_ELEM_COM = os.path.join(AQUI, "Elementos_comericales")

# Catálogo de los 20 archivos STEP exportados desde Inventor
# (archivo_stp, nombre_fcstd, material, eje_origen, descripcion)
CATALOGO_STEPS_3D = [
    ("x1 - plano1-tapa de motor.stp",        "Tapa_Motor_01_3D",          "PLA_Estructural", "Z", "Tapa soporte de motor (Plano 1)"),
    ("x1 - plano2 transmisor A.stp",         "Transmisor_A_02a_3D",       "AISI_304",        "X", "Eje transmisor A (Plano 2a)"),
    ("x1 - plano2 transmisor B.stp",         "Transmisor_B_02b_3D",       "AISI_304",        "X", "Eje transmisor B (Plano 2b)"),
    ("x1 - plano3-Adaptador de rodamiento.stp", "Adaptador_Rodamiento_03_3D", "PLA_Estructural", "Z", "Adaptador de rodamiento SKF 609 (Plano 3)"),
    ("x1 - plano4-adaptador del eje.stp",    "Adaptador_Eje_04_3D",       "PLA_Estructural", "Z", "Adaptador de eje (Plano 4)"),
    ("x1 - plano5-Sufridera eje ext.stp",    "Sufridera_Eje_Ext_05a_3D",  "PLA_Estructural", "Z", "Sufridera de eje exterior (Plano 5a)"),
    ("x1 - plano5-Sufridera int.stp",        "Sufridera_Int_05b_3D",      "PLA_Estructural", "Z", "Sufridera interior portarretén (Plano 5b)"),
    ("x1 - plano5-Tapa sufridera int5.stp",  "Tapa_Sufridera_Int_05a_3D", "PLA_Estructural", "Z", "Tapa de sufridera interior (Plano 5a)"),
    ("x4 - plano5-Sufridera guia.stp",       "Sufridera_Guia_05b_3D",     "PLA_Estructural", "Z", "Sufridera de barra guía (Plano 5b)"),
    ("x2 - plano5-Sensor pistón.stp",        "Sensor_Piston_05b_3D",      "AISI_430",        "Z", "Target ferromagnético de pistón (Plano 5b)"),
    ("x2 - plano7 Estructura interior.stp",  "Estructura_Interior_07_3D", "PLA_Estructural", "Z", "Anillo de estructura interior (Plano 7)"),
    ("x2 - plano8-guia.stp",                 "Guia_08_3D",                "AISI_304",        "X", "Barra guía rectificada (Plano 8)"),
    ("x1 - plano10-Delrin.stp",              "Embolo_Delrin_10_3D",       "Delrin",          "X", "Émbolo principal (Plano 10)"),
    ("x1 - plano11Centro émbolo 1.stp",      "Centro_Embolo_1_11_3D",     "PLA_Estructural", "Z", "Centro de émbolo 1 (Plano 11)"),
    ("x1 - plano12 Centro émbolo 2.stp",     "Centro_Embolo_2_12_3D",     "PLA_Estructural", "Z", "Centro de émbolo 2 (Plano 12)"),
    ("x2 - plano13-anillo torica.stp",       "Anillo_Torica_13_3D",       "PLA_Estructural", "X", "Anillo de junta tórica (Plano 13)"),
    ("x1 - plano14-Title.stp",               "Tornillo_Sin_Fin_14_3D",    "Acero_1045",      "X", "Tornillo sin fin / husillo (Plano 14)"),
    ("x2 - plano15-Cierre estructura.stp",   "Cierre_Estructura_15_3D",   "PLA_Estructural", "X", "Brida cierre de estructura (Plano 15)"),
    ("x1 - plano16a-Tapa exterior_MIR.stp",  "Tapa_Exterior_16a_3D",      "PLA_Estructural", "Z", "Tapa exterior frontal (Plano 16a)"),
    ("x1 - plano16b-Tapa interior.stp",      "Tapa_Interior_16b_3D",      "PLA_Estructural", "Z", "Tapa interior intermedia (Plano 16b)"),
]


def _normalizar_a_eje_z(shape, eje_origen):
    sh = shape.copy()
    if eje_origen == "X":
        # Rotar -90° en Y para llevar el eje X original al eje +Z
        sh.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), -90.0)
    bb = sh.BoundBox
    # Centrar en X, Y si corresponde y apoyar la base inferior en Z = 0
    cx = 0.5 * (bb.XMin + bb.XMax)
    cy = 0.5 * (bb.YMin + bb.YMax)
    sh.translate(App.Vector(-cx, -cy, -bb.ZMin))
    return sh


def _adaptar_pieza_3d_impresa(pz, nombre, sh_norm, bb):
    """
    Adapta paramétricamente las piezas impresas en 3D (PLA_Estructural) a los
    componentes comerciales elegidos (SKF 609-2Z, Retén 10x22x7, guías, husillo)
    compensando holguras FDM y cotas heredadas de escala 0.755.
    """
    p = pz.p
    if nombre == "Sufridera_Int_05b_3D":
        # Desplazar el sólido STEP +0.70 mm en Z y fusionar anillo base para alojar Retén 10x22x7 (ancho 7.00 mm)
        sh_shift = sh_norm.copy()
        sh_shift.translate(App.Vector(0, 0, 0.70))
        base_step = pz.nuevo("Part::Feature", f"{nombre}_BaseSTEP")
        base_step.Shape = sh_shift
        anillo = pz.cil("Anillo_Base_Reten", f"{p('d_ext_brida')} / 2", "0.90 mm", z="0 mm")
        fus = pz.fusion("Fusion_Base_Sufridera", [base_step, anillo])
        corte_ret = pz.cil("Corte_Aloj_Reten_22", f"{p('d_aloj_reten')} / 2", "10 mm", z="-1 mm")
        sol = pz.corte(f"{nombre}_Solido", fus, corte_ret)
        base_step.Visibility = False
        anillo.Visibility = False
        fus.Visibility = False
        corte_ret.Visibility = False
        return sol, bb.ZLength + 0.70

    base_step = pz.nuevo("Part::Feature", f"{nombre}_BaseSTEP")
    base_step.Shape = sh_norm
    cortes = []

    if nombre == "Tapa_Sufridera_Int_05a_3D":
        cortes.append(pz.cil("Corte_Paso_Eje", f"{p('d_paso_eje')} / 2", "5 mm", z="-1 mm"))
    elif nombre == "Adaptador_Rodamiento_03_3D":
        cortes.append(pz.cil("Corte_Paso_Transmisor", f"{p('d_paso_transm')} / 2", "24 mm", z="-1 mm"))
        cortes.append(pz.cil("Corte_Aloj_SKF_609", f"{p('d_aloj_609')} / 2", "10 mm", z=p("z_piso_609")))
    elif nombre == "Adaptador_Eje_04_3D":
        cortes.append(pz.cil("Corte_Despeje_Guia_1", f"{p('d_despeje_sufr')} / 2", "16 mm",
                             x=f"-1 * {p('x_guia')}", z="-1 mm"))
        cortes.append(pz.cil("Corte_Despeje_Guia_2", f"{p('d_despeje_sufr')} / 2", "16 mm",
                             x=p("x_guia"), z="-1 mm"))
    elif nombre == "Sufridera_Guia_05b_3D":
        cortes.append(pz.cil("Corte_Paso_Guia", f"{p('d_paso_guia')} / 2", "6 mm", z="-1 mm"))
    elif nombre == "Tapa_Interior_16b_3D":
        cortes.append(pz.cil("Corte_Bolsillo_Sufr_1", f"{p('d_aloj_sufr_guia')} / 2", p("p_sufr_guia"),
                             x=f"-1 * {p('x_guia')}", z=p("z_ini_sufr")))
        cortes.append(pz.cil("Corte_Bolsillo_Sufr_2", f"{p('d_aloj_sufr_guia')} / 2", p("p_sufr_guia"),
                             x=p("x_guia"), z=p("z_ini_sufr")))
    elif nombre == "Tapa_Exterior_16a_3D":
        cortes.append(pz.cil("Corte_Bolsillo_Brida_Ext", f"{p('d_aloj_brida_ext')} / 2", "6 mm",
                             z=p("z_hombro_ext")))
        cortes.append(pz.cil("Corte_Bolsillo_Nariz_Ext", f"{p('d_aloj_nariz_ext')} / 2", "12 mm",
                             z=p("z_fondo_ext")))
    elif nombre == "Sufridera_Eje_Ext_05a_3D":
        cortes.append(pz.cil("Corte_Paso_Punta_Husillo", f"{p('d_eje_punta')} / 2", "13 mm", z="-1 mm"))
        cortes.append(pz.cil("Corte_Paso_Escalon_Husillo", f"{p('d_eje_esc')} / 2", "4.85 mm", z="-1 mm"))

    if not cortes:
        base_step.Label = f"{nombre}_Solido"
        return base_step, bb.ZLength

    vaciado = cortes[0] if len(cortes) == 1 else pz.fusion("Operaciones_Adaptacion_3D", cortes)
    sol = pz.corte(f"{nombre}_Solido", base_step, vaciado)
    base_step.Visibility = False
    vaciado.Visibility = False
    return sol, bb.ZLength


ADAPTACIONES_DIMS = {
    "Sufridera_Int_05b_3D": [
        ("d_ext_brida", "Diámetro exterior sufridera int", "33.98 mm", "N", None, "plano"),
        ("d_aloj_reten", "Diámetro alojamiento retén 10x22x7", "22.00 mm", "H", None, "norma"),
        ("h_ext_reten", "Sobre-espesor axial p/ retén 7 mm", "0.70 mm", "N", None, "calculado"),
    ],
    "Tapa_Sufridera_Int_05a_3D": [
        ("d_paso_eje", "Diámetro paso eje transmisor B (holgura FDM)", "11.40 mm", "H", None, "usuario"),
    ],
    "Adaptador_Rodamiento_03_3D": [
        ("d_paso_transm", "Diámetro paso transmisor A Ø15.10 + holgura", "15.20 mm", "H", None, "calculado"),
        ("d_aloj_609", "Diámetro alojamiento rodamiento SKF 609 (Ø24)", "24.00 mm", "H", None, "norma"),
        ("z_piso_609", "Cota asiento axial rodamiento SKF 609", "11.65 mm", "N", None, "calculado"),
    ],
    "Adaptador_Eje_04_3D": [
        ("x_guia", "Semidistancia entre barras guía", "28.31 mm", "N", None, "plano"),
        ("d_despeje_sufr", "Diámetro despeje brida sufridera guía", "15.20 mm", "H", None, "calculado"),
    ],
    "Sufridera_Guia_05b_3D": [
        ("d_paso_guia", "Diámetro paso barra guía Ø7.55 + holgura", "7.55 mm", "H", None, "usuario"),
    ],
    "Tapa_Interior_16b_3D": [
        ("x_guia", "Semidistancia entre barras guía", "28.31 mm", "N", None, "plano"),
        ("d_aloj_sufr_guia", "Diámetro bolsillo sufridera guía", "15.10 mm", "H", None, "usuario"),
        ("z_ini_sufr", "Inicio axial bolsillo sufridera guía", "11.20 mm", "N", None, "calculado"),
        ("p_sufr_guia", "Profundidad bolsillo sufridera guía", "2.50 mm", "N", None, "calculado"),
    ],
    "Tapa_Exterior_16a_3D": [
        ("d_aloj_brida_ext", "Diámetro bolsillo brida sufridera ext", "30.20 mm", "H", None, "usuario"),
        ("d_aloj_nariz_ext", "Diámetro bolsillo nariz sufridera ext", "13.60 mm", "H", None, "usuario"),
        ("z_hombro_ext", "Cota hombro brida sufridera ext", "7.85 mm", "N", None, "calculado"),
        ("z_fondo_ext", "Cota fondo bolsillo punta husillo ext", "1.40 mm", "N", None, "calculado"),
    ],
    "Sufridera_Eje_Ext_05a_3D": [
        ("d_eje_punta", "Diámetro paso punta husillo Ø9.06 + holgura", "9.06 mm", "H", None, "usuario"),
        ("d_eje_esc", "Diámetro paso escalón husillo Ø9.82 + holgura", "9.82 mm", "H", None, "usuario"),
    ],
}


def importar_steps():
    print("FreeCAD", ".".join(App.Version()[:3]))
    for archivo_stp, nombre, mat, eje, desc in CATALOGO_STEPS_3D:
        ruta_stp = os.path.join(DIR_ENTRADAS, archivo_stp)
        ruta_fcstd = os.path.join(AQUI, f"{nombre}.FCStd")
        if not os.path.exists(ruta_stp):
            raise FileNotFoundError(f"No se encontró el STEP: {ruta_stp}")

        sh_raw = Part.read(ruta_stp)
        sol_stp = sh_raw.Solids[0]
        sh_norm = _normalizar_a_eje_z(sol_stp, eje)
        bb = sh_norm.BoundBox

        dims = [
            ("dx_env", "Ancho envolvente X (modelo STEP 3D)", f"{bb.XLength:.2f} mm", "N", None, "plano"),
            ("dy_env", "Ancho envolvente Y (modelo STEP 3D)", f"{bb.YLength:.2f} mm", "N", None, "plano"),
            ("dz_env", "Altura / longitud Z (modelo STEP 3D)", f"{bb.ZLength:.2f} mm", "N", None, "plano"),
        ]
        dims.extend(ADAPTACIONES_DIMS.get(nombre, []))

        # Nota: FORZAR=1 implícito al crear/reimportar desde STEP (escala=1.0 porque STEP ya viene a 0.755)
        pz = Pieza(nombre, ruta_salida=None)
        pz.parametros(dims, modo=1, escala="1.0", holgura_fdm="0.20 mm")
        pz.materiales(mat)

        sol_feat, z_sup = _adaptar_pieza_3d_impresa(pz, nombre, sh_norm, bb)

        pz.lcs("LCS_Origen")
        pz.lcs("LCS_Centro", z=f"{z_sup * 0.5:.3f} mm")
        pz.lcs("LCS_Cara_Sup", z=f"{z_sup:.3f} mm")
        pz.reporte_fisico(sol_feat)
        pz.cerrar(sol_feat, ruta_fcstd)
        bb_fin = sol_feat.Shape.BoundBox
        print(f"Importado STEP -> {nombre}.FCStd ({bb_fin.XLength:.1f}x{bb_fin.YLength:.1f}x{bb_fin.ZLength:.1f} mm, Vol={sol_feat.Shape.Volume:.1f} mm3)")


def _guardar_comercial(pz, sol, categoria, nombre):
    os.makedirs(os.path.join(DIR_CATALOGO, categoria), exist_ok=True)
    os.makedirs(DIR_ELEM_COM, exist_ok=True)
    ruta_cat = os.path.join(DIR_CATALOGO, categoria, f"{nombre}.FCStd")
    ruta_loc = os.path.join(DIR_ELEM_COM, f"{nombre}.FCStd")
    pz.cerrar(sol, ruta_cat)
    shutil.copy2(ruta_cat, ruta_loc)


def generar_comerciales_y_cilindro():
    # 1. Cilindro Acrílico 3D (Ø83 x Ø76 x 188.75 mm) adaptado a Tapa_Exterior/Interior
    pz = Pieza("Cilindro_09_3D")
    pz.parametros([
        ("d_ext",   "Diámetro exterior camisa acrílica (escala)", "83.00 mm",  "L", None, "calculado"),
        ("d_int",   "Diámetro interior camisa acrílica (escala)", "76.00 mm",  "L", None, "calculado"),
        ("l_total", "Longitud de la camisa (250 mm * 0.755)",     "188.75 mm", "L", None, "plano"),
    ], modo=1, escala="1.0", holgura_fdm="0.20 mm")
    pz.materiales("Acrilico_PMMA")
    p = pz.p
    ext = pz.cil("Cil_Ext", f"{p('d_ext')} / 2", p("l_total"))
    inte = pz.cil("Cil_Int", f"{p('d_int')} / 2", f"{p('l_total')} + 2 mm", z="-1 mm")
    sol = pz.corte("Cilindro_09_3D_Solido", ext, inte)
    pz.lcs("LCS_Origen")
    pz.lcs("LCS_Extremo_Sup", z=p("l_total"))
    pz.reporte_fisico(sol)
    pz.cerrar(sol, os.path.join(AQUI, "Cilindro_09_3D.FCStd"))

    # 2. Rodamiento SKF 609-2Z (Ø9 x Ø24 x 7 mm)
    pz = Pieza("Rodamiento_SKF_609")
    pz.parametros([
        ("d_int", "Diámetro interior d (SKF 609-2Z)", "9.00 mm",  "L", None, "norma"),
        ("d_ext", "Diámetro exterior D (SKF 609-2Z)", "24.00 mm", "L", None, "norma"),
        ("ancho", "Ancho B (SKF 609-2Z)",             "7.00 mm",  "L", None, "norma"),
    ], modo=3)
    pz.materiales("Acero_1045")
    p = pz.p
    c1 = pz.cil("Aro_Ext", f"{p('d_ext')} / 2", p("ancho"))
    c2 = pz.cil("Eje_Int", f"{p('d_int')} / 2", f"{p('ancho')} + 2 mm", z="-1 mm")
    sol = pz.corte("Rodamiento_SKF_609_Solido", c1, c2)
    pz.lcs("LCS_Origen")
    pz.lcs("LCS_Cara_Sup", z=p("ancho"))
    pz.reporte_fisico(sol)
    _guardar_comercial(pz, sol, "Rodamientos", "Rodamiento_SKF_609")

    # 3. Retén DIN 3760 A 10x22x7 mm
    pz = Pieza("Reten_10x22x7")
    pz.parametros([
        ("d_int", "Diámetro de eje (DIN 3760A)",      "10.00 mm", "L", None, "norma"),
        ("d_ext", "Diámetro alojamiento (DIN 3760A)", "22.00 mm", "L", None, "norma"),
        ("ancho", "Espesor axial",                    "7.00 mm",  "L", None, "norma"),
    ], modo=3)
    pz.materiales("Caucho_NBR")
    p = pz.p
    c1 = pz.cil("Reten_Ext", f"{p('d_ext')} / 2", p("ancho"))
    c2 = pz.cil("Reten_Int", f"{p('d_int')} / 2", f"{p('ancho')} + 2 mm", z="-1 mm")
    sol = pz.corte("Reten_10x22x7_Solido", c1, c2)
    pz.lcs("LCS_Origen")
    pz.lcs("LCS_Cara_Sup", z=p("ancho"))
    pz.reporte_fisico(sol)
    _guardar_comercial(pz, sol, "Retenes_DIN_3760", "Reten_10x22x7")

    # 4. O-Rings DIN 3771 (75x3.55, 69x3.55, 11.2x1.8)
    for nom, d_i, s_c in [
        ("ORing_75x3_55",   75.0, 3.55),
        ("ORing_69x3_55",   69.0, 3.55),
        ("ORing_11_2x1_8",  11.2, 1.80),
    ]:
        pz = Pieza(nom)
        pz.parametros([
            ("d_int", "Diámetro interior DIN 3771", f"{d_i:.2f} mm", "L", None, "norma"),
            ("s_cuerda", "Diámetro de cuerda s",    f"{s_c:.2f} mm", "L", None, "norma"),
        ], modo=3)
        pz.materiales("Caucho_NBR")
        toro = pz.nuevo("Part::Torus", f"{nom}_Solido")
        toro.setExpression("Radius1", f"({pz.p('d_int')} + {pz.p('s_cuerda')}) / 2")
        toro.setExpression("Radius2", f"{pz.p('s_cuerda')} / 2")
        pz.lcs("LCS_Origen")
        pz.reporte_fisico(toro)
        _guardar_comercial(pz, toro, "ORings_DIN_3771_ISO_3601", nom)

    # 5. Pasadores elásticos ISO 8752 (3x14 y 3x10)
    for nom, l_p in [("Pasador_3x14", 14.0), ("Pasador_3x10", 10.0)]:
        pz = Pieza(nom)
        pz.parametros([
            ("d_ext", "Diámetro nominal ISO 8752", "3.00 mm",      "L", None, "norma"),
            ("d_int", "Diámetro interior hueco",   "1.80 mm",      "L", None, "norma"),
            ("l_tot", "Longitud nominal",          f"{l_p:.2f} mm","L", None, "norma"),
        ], modo=3)
        pz.materiales("Acero_1045")
        p = pz.p
        c1 = pz.cil("Pas_Ext", f"{p('d_ext')} / 2", p("l_tot"), z=f"-{p('l_tot')} / 2")
        c2 = pz.cil("Pas_Int", f"{p('d_int')} / 2", f"{p('l_tot')} + 2 mm", z=f"-{p('l_tot')} / 2 - 1 mm")
        sol = pz.corte(f"{nom}_Solido", c1, c2)
        pz.lcs("LCS_Origen")
        pz.reporte_fisico(sol)
        _guardar_comercial(pz, sol, "Pasadores_ISO_8752", nom)


if __name__ in ("__main__", "importar_modelo_3d_steps"):
    os.environ["FORZAR"] = "1"
    importar_steps()
    generar_comerciales_y_cilindro()
