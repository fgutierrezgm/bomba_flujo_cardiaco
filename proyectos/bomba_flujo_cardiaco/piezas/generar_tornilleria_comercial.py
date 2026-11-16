#!/usr/bin/env python3
"""Generador de tornillería comercial (Tornillos, Tuercas y Arandelas) y organización de Piezas_Comerciales."""
import math
import os
import shutil
import sys
import FreeCAD as App

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "_herramientas"))
from fc_helpers import Pieza

DIR_PIEZAS = os.path.dirname(os.path.abspath(__file__))
DIR_ELEM_OLD = os.path.join(DIR_PIEZAS, "Elementos_comericales")
DIR_COMERCIALES = os.path.join(DIR_PIEZAS, "Piezas_Comerciales")

SUBCARPETAS = [
    "Tornillos",
    "Tuercas",
    "Arandelas",
    "Retenes",
    "Rulemanes",
    "Orrings",
    "Pasadores",
]


def organizar_carpetas_existentes():
    """Crea la estructura Piezas_Comerciales/<Subcarpeta> y copia los comerciales existentes."""
    for sub in SUBCARPETAS:
        os.makedirs(os.path.join(DIR_COMERCIALES, sub), exist_ok=True)

    mapeo_copia = {
        "Retenes": ["Reten_10x22x7.FCStd", "Reten_14x30x7.FCStd"],
        "Rulemanes": ["Rodamiento_SKF_609.FCStd", "Rodamiento_SKF_6201.FCStd"],
        "Orrings": [
            "ORing_6_0x1_5.FCStd",
            "ORing_11_2x1_8.FCStd",
            "ORing_68x4_00.FCStd",
            "ORing_69x3_55.FCStd",
            "ORing_75x3_55.FCStd",
            "ORing_Embolo_97x3_5.FCStd",
        ],
        "Pasadores": [
            "Pasador_3x10.FCStd",
            "Pasador_3x14.FCStd",
            "Pasador_Cilindrico_4x18.FCStd",
        ],
    }

    for sub, archivos in mapeo_copia.items():
        for arch in archivos:
            origen = os.path.join(DIR_ELEM_OLD, arch)
            destino = os.path.join(DIR_COMERCIALES, sub, arch)
            if os.path.isfile(origen):
                shutil.copy2(origen, destino)


def _ocultar(*objs, pieza=None):
    for o in objs:
        if o is None:
            continue
        o.Visibility = False
        if App.GuiUp and hasattr(o, "ViewObject") and o.ViewObject:
            o.ViewObject.Visibility = False
        if pieza is not None and o not in pieza.auxiliares:
            pieza.auxiliares.append(o)


def _crear_prisma_hex(p, nombre, expr_s, expr_h, expr_z0):
    """Crea un prisma hexagonal regular de entrecaras expr_s y altura expr_h en z=expr_z0."""
    f = p.nuevo("Part::Prism", nombre)
    f.Polygon = 6
    f.setExpression("Circumradius", f"({expr_s}) / sqrt(3)")
    f.setExpression("Height", expr_h)
    f.setExpression(".Placement.Base.z", expr_z0)
    _ocultar(f, pieza=p)
    return f


def generar_arandela_comercial(nombre, d_ext, d_int, espesor, norma="DIN 125 A"):
    """Genera una arandela plana comercial en Piezas_Comerciales/Arandelas/.
    LCS_Origen en z=0 (cara inferior de apoyo), LCS_Cara_Sup en z=espesor.
    """
    ruta = os.path.join(DIR_COMERCIALES, "Arandelas", f"{nombre}.FCStd")
    p = Pieza(nombre)
    dims = [
        ("d_ext", f"Diámetro exterior ({norma})", f"{d_ext:.2f} mm", "L", "", "norma"),
        ("d_int", f"Diámetro interior ({norma})", f"{d_int:.2f} mm", "L", "", "norma"),
        ("espesor", f"Espesor ({norma})", f"{espesor:.2f} mm", "L", "", "norma"),
    ]
    p.parametros(dims, modo=1, holgura_fdm="0.00 mm")
    c_ext = p.cil("Cil_Ext", "<<Parametros>>.d_ext / 2", "<<Parametros>>.espesor")
    c_int = p.cil("Cil_Int", "<<Parametros>>.d_int / 2", "<<Parametros>>.espesor + 2 mm", z="-1 mm")
    sol = p.corte(f"{nombre}_Body", c_ext, c_int)
    p.lcs("LCS_Origen", z="0 mm")
    p.lcs("LCS_Cara_Sup", z="<<Parametros>>.espesor")
    p.cerrar(sol, ruta)


def generar_tuerca_hex_comercial(nombre, s_hex, h_tuerca, d_int, norma="DIN 934"):
    """Genera una tuerca hexagonal comercial con chaflanes cónicos exteriores en ambas caras.
    LCS_Origen en z=0 (cara de apoyo inferior), LCS_Cara_Sup en z=h_tuerca.
    """
    ruta = os.path.join(DIR_COMERCIALES, "Tuercas", f"{nombre}.FCStd")
    p = Pieza(nombre)
    dims = [
        ("s_hex", f"Entrecaras hexágono ({norma})", f"{s_hex:.2f} mm", "L", "", "norma"),
        ("h_tuerca", f"Altura tuerca ({norma})", f"{h_tuerca:.2f} mm", "L", "", "norma"),
        ("d_int", f"Diámetro agujero roscado ({norma})", f"{d_int:.2f} mm", "L", "", "norma"),
    ]
    p.parametros(dims, modo=1, holgura_fdm="0.00 mm")
    hex_raw = _crear_prisma_hex(p, "Prisma_Hex", "<<Parametros>>.s_hex", "<<Parametros>>.h_tuerca", "0 mm")
    # Cono intersección para biselado comercial de aristas hexagonales (radios)
    cono_sup = p.cono("Cono_Bisel_Sup", "<<Parametros>>.s_hex * 0.72", "<<Parametros>>.s_hex * 0.47", "<<Parametros>>.h_tuerca", z="0 mm")
    cono_inf = p.cono("Cono_Bisel_Inf", "<<Parametros>>.s_hex * 0.47", "<<Parametros>>.s_hex * 0.72", "<<Parametros>>.h_tuerca", z="0 mm")
    # Intersectar hexágono con ambos conos
    inter1 = p.nuevo("Part::Common", "Hex_Bisel_1")
    inter1.Base = hex_raw
    inter1.Tool = cono_sup
    _ocultar(hex_raw, cono_sup, inter1, pieza=p)
    inter2 = p.nuevo("Part::Common", "Hex_Bisel_2")
    inter2.Base = inter1
    inter2.Tool = cono_inf
    _ocultar(cono_inf, inter2, pieza=p)
    aguj = p.cil("Agujero_Rosca", "<<Parametros>>.d_int / 2", "<<Parametros>>.h_tuerca + 2 mm", z="-1 mm")
    sol = p.corte(f"{nombre}_Body", inter2, aguj)
    p.lcs("LCS_Origen", z="0 mm")
    p.lcs("LCS_Cara_Sup", z="<<Parametros>>.h_tuerca")
    p.cerrar(sol, ruta)


def generar_tornillo_hex_comercial(nombre, s_hex, h_cab, d_vastago, l_vastago, norma="DIN 933"):
    """Genera un bulón de cabeza hexagonal comercial.
    Convención uniforme de montaje:
    - Cabeza hexagonal en z = [-h_cab, 0]
    - Cara de apoyo de la cabeza en z = 0 (LCS_Origen)
    - Vástago hacia +Z en z = [0, l_vastago]
    """
    ruta = os.path.join(DIR_COMERCIALES, "Tornillos", f"{nombre}.FCStd")
    p = Pieza(nombre)
    dims = [
        ("s_hex", f"Entrecaras cabeza ({norma})", f"{s_hex:.2f} mm", "L", "", "norma"),
        ("h_cab", f"Altura cabeza ({norma})", f"{h_cab:.2f} mm", "L", "", "norma"),
        ("d_vastago", f"Diámetro vástago ({norma})", f"{d_vastago:.2f} mm", "L", "", "norma"),
        ("l_vastago", f"Longitud vástago ({norma})", f"{l_vastago:.2f} mm", "L", "", "norma"),
    ]
    p.parametros(dims, modo=1, holgura_fdm="0.00 mm")
    hex_raw = _crear_prisma_hex(p, "Cabeza_Hex", "<<Parametros>>.s_hex", "<<Parametros>>.h_cab", "-<<Parametros>>.h_cab")
    cono_cab = p.cono("Cono_Bisel_Cab", "<<Parametros>>.s_hex * 0.47", "<<Parametros>>.s_hex * 0.72", "<<Parametros>>.h_cab", z="-<<Parametros>>.h_cab")
    cab_bisel = p.nuevo("Part::Common", "Cabeza_Biselada")
    cab_bisel.Base = hex_raw
    cab_bisel.Tool = cono_cab
    _ocultar(hex_raw, cono_cab, cab_bisel, pieza=p)

    vastago = p.cil("Vastago", "<<Parametros>>.d_vastago / 2", "<<Parametros>>.l_vastago - 0.5 mm", z="0 mm")
    punta = p.cono("Punta_Chaflan", "<<Parametros>>.d_vastago / 2", "<<Parametros>>.d_vastago * 0.35", "0.5 mm", z="<<Parametros>>.l_vastago - 0.5 mm")
    sol = p.fusion(f"{nombre}_Body", [cab_bisel, vastago, punta])
    p.lcs("LCS_Origen", z="0 mm")
    p.lcs("LCS_Punta", z="<<Parametros>>.l_vastago")
    p.cerrar(sol, ruta)


def generar_tornillo_allen_comercial(
    nombre,
    d_cab,
    h_cab,
    s_allen,
    prof_allen,
    d_vastago,
    l_vastago,
    d_punta=None,
    l_cuello=None,
    norma="DIN 912",
):
    """Genera un tornillo Allen cilíndrico (DIN 912 / ISO 4762) con alojamiento hexagonal en la cabeza.
    Convención uniforme de montaje:
    - Cabeza cilíndrica en z = [-h_cab, 0] (alojamiento llave Allen en cara z = -h_cab)
    - Cara de apoyo bajo cabeza en z = 0 (LCS_Origen)
    - Vástago hacia +Z en z = [0, l_vastago]
    """
    ruta = os.path.join(DIR_COMERCIALES, "Tornillos", f"{nombre}.FCStd")
    p = Pieza(nombre)
    dims = [
        ("d_cab", f"Diámetro cabeza ({norma})", f"{d_cab:.2f} mm", "L", "", "norma"),
        ("h_cab", f"Altura cabeza ({norma})", f"{h_cab:.2f} mm", "L", "", "norma"),
        ("s_allen", f"Entrecaras llave Allen ({norma})", f"{s_allen:.2f} mm", "L", "", "norma"),
        ("prof_allen", f"Profundidad llave Allen ({norma})", f"{prof_allen:.2f} mm", "L", "", "norma"),
        ("d_vastago", f"Diámetro vástago ({norma})", f"{d_vastago:.2f} mm", "L", "", "norma"),
        ("l_vastago", f"Longitud vástago ({norma})", f"{l_vastago:.2f} mm", "L", "", "norma"),
    ]
    if d_punta is not None and l_cuello is not None:
        dims.extend([
            ("d_punta", f"Diámetro tramo roscado ({norma})", f"{d_punta:.2f} mm", "L", "", "norma"),
            ("l_cuello", f"Longitud cuello ({norma})", f"{l_cuello:.2f} mm", "L", "", "norma"),
        ])
    p.parametros(dims, modo=1, holgura_fdm="0.00 mm")

    cab_cil = p.cil("Cabeza_Cil", "<<Parametros>>.d_cab / 2", "<<Parametros>>.h_cab - 0.25 mm", z="-<<Parametros>>.h_cab + 0.25 mm")
    cab_chaf = p.cono("Cabeza_Chaflan", "(<<Parametros>>.d_cab - 0.5 mm) / 2", "<<Parametros>>.d_cab / 2", "0.25 mm", z="-<<Parametros>>.h_cab")
    partes = [cab_cil, cab_chaf]

    if d_punta is not None and l_cuello is not None:
        v_cuello = p.cil("Vastago_Cuello", "<<Parametros>>.d_vastago / 2", "<<Parametros>>.l_cuello", z="0 mm")
        v_rosca = p.cil("Vastago_Rosca", "<<Parametros>>.d_punta / 2", "<<Parametros>>.l_vastago - <<Parametros>>.l_cuello - 0.3 mm", z="<<Parametros>>.l_cuello")
        punta = p.cono("Punta_Chaflan", "<<Parametros>>.d_punta / 2", "<<Parametros>>.d_punta * 0.35", "0.3 mm", z="<<Parametros>>.l_vastago - 0.3 mm")
        partes.extend([v_cuello, v_rosca, punta])
    else:
        vastago = p.cil("Vastago", "<<Parametros>>.d_vastago / 2", "<<Parametros>>.l_vastago - 0.3 mm", z="0 mm")
        punta = p.cono("Punta_Chaflan", "<<Parametros>>.d_vastago / 2", "<<Parametros>>.d_vastago * 0.35", "0.3 mm", z="<<Parametros>>.l_vastago - 0.3 mm")
        partes.extend([vastago, punta])

    bruto = p.fusion("Cuerpo_Bruto", partes)
    hueco_allen = _crear_prisma_hex(p, "Hueco_Allen", "<<Parametros>>.s_allen", "<<Parametros>>.prof_allen + 0.5 mm", "-<<Parametros>>.h_cab - 0.5 mm")
    sol = p.corte(f"{nombre}_Body", bruto, hueco_allen)
    p.lcs("LCS_Origen", z="0 mm")
    p.lcs("LCS_Punta", z="<<Parametros>>.l_vastago")
    p.cerrar(sol, ruta)


def generar_tornillo_avellanado_comercial(nombre, d_cab, h_cono, s_allen, prof_allen, d_vastago, l_total, norma="DIN 7991"):
    """Genera un tornillo avellanado plano con hexágono interior (DIN 7991 / ISO 10642).
    - Cara plana exterior de la cabeza en z = 0 (LCS_Origen)
    - Cono avellanado en z = [0, h_cono]
    - Vástago en z = [h_cono, l_total] hacia +Z
    """
    ruta = os.path.join(DIR_COMERCIALES, "Tornillos", f"{nombre}.FCStd")
    p = Pieza(nombre)
    dims = [
        ("d_cab", f"Diámetro cabeza ({norma})", f"{d_cab:.2f} mm", "L", "", "norma"),
        ("h_cono", f"Altura cono cabeza ({norma})", f"{h_cono:.2f} mm", "L", "", "norma"),
        ("s_allen", f"Entrecaras llave Allen ({norma})", f"{s_allen:.2f} mm", "L", "", "norma"),
        ("prof_allen", f"Profundidad llave Allen ({norma})", f"{prof_allen:.2f} mm", "L", "", "norma"),
        ("d_vastago", f"Diámetro vástago ({norma})", f"{d_vastago:.2f} mm", "L", "", "norma"),
        ("l_total", f"Longitud total ({norma})", f"{l_total:.2f} mm", "L", "", "norma"),
    ]
    p.parametros(dims, modo=1, holgura_fdm="0.00 mm")
    cono_cab = p.cono("Cono_Cabeza", "<<Parametros>>.d_cab / 2", "<<Parametros>>.d_vastago / 2", "<<Parametros>>.h_cono", z="0 mm")
    vastago = p.cil("Vastago", "<<Parametros>>.d_vastago / 2", "<<Parametros>>.l_total - <<Parametros>>.h_cono - 0.25 mm", z="<<Parametros>>.h_cono")
    punta = p.cono("Punta_Chaflan", "<<Parametros>>.d_vastago / 2", "<<Parametros>>.d_vastago * 0.35", "0.25 mm", z="<<Parametros>>.l_total - 0.25 mm")
    bruto = p.fusion("Cuerpo_Bruto", [cono_cab, vastago, punta])
    hueco_allen = _crear_prisma_hex(p, "Hueco_Allen", "<<Parametros>>.s_allen", "<<Parametros>>.prof_allen + 0.4 mm", "-0.4 mm")
    sol = p.corte(f"{nombre}_Body", bruto, hueco_allen)
    p.lcs("LCS_Origen", z="0 mm")
    p.lcs("LCS_Punta", z="<<Parametros>>.l_total")
    p.cerrar(sol, ruta)


def main():
    print(f"FreeCAD {'.'.join(App.Version()[:3])} — Generando Piezas_Comerciales...")
    organizar_carpetas_existentes()

    # 1. Arandelas comerciales (DIN 125 A)
    generar_arandela_comercial("Arandela_Plana_M8", d_ext=16.00, d_int=8.40, espesor=1.60)
    generar_arandela_comercial("Arandela_Plana_M4", d_ext=9.00, d_int=4.30, espesor=0.80)

    # 2. Tuercas comerciales (DIN 934)
    generar_tuerca_hex_comercial("Tuerca_Hex_M4", s_hex=7.00, h_tuerca=3.20, d_int=4.00)
    generar_tuerca_hex_comercial("Tuerca_Hex_M6", s_hex=10.00, h_tuerca=4.50, d_int=5.00)
    generar_tuerca_hex_comercial("Tuerca_Hex_M2", s_hex=4.00, h_tuerca=1.60, d_int=1.65)

    # 3. Tornillos comerciales
    # M8x16 Hex (para los 8 extremos de los 4 Tensores, entra en agujero Ø6.32 mm de los tensores)
    generar_tornillo_hex_comercial("Tornillo_Hex_M8x16", s_hex=13.00, h_cab=5.30, d_vastago=6.10, l_vastago=14.00)

    # M6x22 Allen (para fijación de Sensor_Piston_1 y 2 a través de las Tuercas M6)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M6x22", d_cab=10.00, h_cab=4.50, s_allen=5.00, prof_allen=3.00, d_vastago=4.90, l_vastago=24.50
    )

    # M4x35 Allen (para Cierre_Estructura_1 y 2 -> Estructura_Interior_1 y 2; cuello Ø3.95 en pasante Ø4.15 y rosca Ø3.00 en Ø3.12)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M4x35",
        d_cab=7.00,
        h_cab=4.00,
        s_allen=3.00,
        prof_allen=2.20,
        d_vastago=3.95,
        l_vastago=35.00,
        d_punta=3.00,
        l_cuello=21.00,
    )

    # M4x12 Allen (para brida motor en Tapa_Motor_01_3D)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M4x12", d_cab=7.00, h_cab=4.00, s_allen=3.00, prof_allen=2.20, d_vastago=3.95, l_vastago=12.00
    )

    # M2.5x8 Allen (para Centro_Embolo_1 -> Embolo_Delrin y Centro_Embolo_2 -> Centro_Embolo_1)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M2_5x8", d_cab=4.50, h_cab=2.50, s_allen=2.00, prof_allen=1.40, d_vastago=1.78, l_vastago=8.00
    )

    # Espárrago/Prisionero Allen M2.5x8 (conservado en catálogo)
    generar_tornillo_allen_comercial(
        "Esparrago_Allen_M2_5x8", d_cab=2.45, h_cab=1.50, s_allen=1.27, prof_allen=1.00, d_vastago=1.78, l_vastago=6.50
    )

    # M2x14 Allen (para Adaptador_Eje_04_3D -> Tapa_Interior_16b_3D a 45° desde cajeado superior)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M2x14", d_cab=3.80, h_cab=2.00, s_allen=1.50, prof_allen=1.10, d_vastago=1.75, l_vastago=14.00
    )

    # M2.5x6 Allen (para Sufridera_Eje_Ext_05a -> Tapa_Exterior_16a)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M2_5x6", d_cab=4.50, h_cab=2.20, s_allen=2.00, prof_allen=1.30, d_vastago=1.78, l_vastago=6.00
    )

    # M2x8 Allen (para Adaptador_Rodamiento_03_3D -> Adaptador_Eje_04_3D a 22.5°/112.5°/202.5°/292.5°)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M2x8", d_cab=3.80, h_cab=2.00, s_allen=1.50, prof_allen=1.10, d_vastago=1.75, l_vastago=8.00
    )

    # M2x16 Allen (conservado en catálogo)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M2x16", d_cab=3.80, h_cab=2.00, s_allen=1.50, prof_allen=1.10, d_vastago=1.60, l_vastago=16.00
    )

    # M2x5 Allen cabeza Ø3.00 mm (para Sufridera_Guia_1B y 2B -> Tapa_Interior_16b, libre del eje Guia_08 Ø8.22 mm)
    generar_tornillo_allen_comercial(
        "Tornillo_Allen_M2x5", d_cab=3.00, h_cab=1.80, s_allen=1.50, prof_allen=1.00, d_vastago=1.75, l_vastago=5.00
    )

    # M2x6 Avellanado (para Anillo_Torica_Int_13 y Ext_13 -> Tapas 16b y 16a)
    generar_tornillo_avellanado_comercial(
        "Tornillo_Avellanado_M2x6", d_cab=3.80, h_cono=1.10, s_allen=1.27, prof_allen=0.90, d_vastago=1.75, l_total=6.00
    )

    print("OK: Piezas_Comerciales generadas y organizadas.")


main()



