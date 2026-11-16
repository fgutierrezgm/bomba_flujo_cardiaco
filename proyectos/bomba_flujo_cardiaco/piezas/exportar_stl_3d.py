#!/usr/bin/env python3
"""
Exportador reproducible de mallas .STL binarias pre-orientadas para impresión 3D FDM
del prototipo Bomba de Flujo Cardíaco (escala 0,755).

- Lee las 24 piezas fabricadas (19 PLA+/PETG + Guía 08 FDM + 4 maquetas de piezas torneadas)
- Verifica cantidades 1:1 contra Lista_de_Materiales de Piloto_Impresion_3D_Assembly.FCStd
- Pre-orienta piezas invertidas (180 deg en X) apoyando la cara óptima en Z=0 y centrando XY en (0,0)
- Valida cada .stl exportado (malla sólida cerrada, 0 aristas no-manifold, componente único, desvío vol < 2%)

Ejecución:
  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/piezas/exportar_stl_3d.py
"""
import os
import sys

import FreeCAD as App
import Mesh
import MeshPart

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "exportar_stl_3d.py")))
DIR_PROYECTO = os.path.dirname(AQUI)
DIR_ASM = os.path.join(DIR_PROYECTO, "ensamblajes", "Piloto_Impresion_3D_Assembly.FCStd")
DIR_STL = os.path.join(DIR_PROYECTO, "stl")

PERFILES_MALLA = [
    (0.02, 0.10),
    (0.03, 0.15),
    (0.04, 0.20),
    (0.05, 0.25),
]

# (item, copias, archivo_fcstd, archivo_stl, rot_x_deg, clave_bom_opcional)
PIEZAS_STL = [
    (1,  1, "Tapa_Exterior_16a_3D.FCStd",             "X1-Tapa_Exterior_16a_3D_Item01.stl",             0,   None),
    (3,  1, "Tapa_Interior_16b_3D.FCStd",             "X1-Tapa_Interior_16b_3D_Item03.stl",           180,   None),
    (4,  1, "Sufridera_Int_05b_3D.FCStd",             "X1-Sufridera_Int_05b_3D_Item04.stl",             0,   None),
    (5,  1, "Tapa_Sufridera_Int_05a_3D.FCStd",        "X1-Tapa_Sufridera_Int_05a_3D_Item05.stl",        0,   None),
    (6,  2, "Sufridera_Guia_05b_3D.FCStd",            "X2-Sufridera_Guia_05b_3D_Item06.stl",            0,   None),
    (7,  1, "Embolo_Delrin_10_3D.FCStd",              "X1-Embolo_Delrin_10_3D_Item07.stl",              0,   None),
    (8,  1, "Centro_Embolo_1_11_3D.FCStd",            "X1-Centro_Embolo_1_11_3D_Item08.stl",            0,   None),
    (9,  1, "Centro_Embolo_2_12_3D.FCStd",            "X1-Centro_Embolo_2_12_3D_Item09.stl",            0,   None),
    (10, 2, "Sensor_Piston_05b_3D.FCStd",             "X2-Sensor_Piston_05b_3D_Item10.stl",             0,   None),
    (11, 2, "Guia_08_3D.FCStd",                       "X2-Guia_08_3D_Item11.stl",                    180,   None),
    (12, 1, "Transmisor_A_02a_3D.FCStd",              "X1-Transmisor_A_02a_3D_Item12.stl",           180,   None),
    (13, 1, "Transmisor_B_02b_3D.FCStd",              "X1-Transmisor_B_02b_3D_Item13.stl",             0,   None),
    (14, 1, "Tornillo_Sin_Fin_14_3D_Impresion.FCStd", "X1-Tornillo_Sin_Fin_14_3D_Impresion_Item14.stl", 0,   "Tornillo_Sin_Fin_14_3D.FCStd"),
    (15, 1, "Adaptador_Rodamiento_03_3D.FCStd",       "X1-Adaptador_Rodamiento_03_3D_Item15.stl",       0,   None),
    (16, 1, "Sufridera_Eje_Ext_05a_3D.FCStd",         "X1-Sufridera_Eje_Ext_05a_3D_Item16.stl",         0,   None),
    (17, 1, "Adaptador_Eje_04_3D.FCStd",              "X1-Adaptador_Eje_04_3D_Item17.stl",              0,   None),
    (18, 2, "Anillo_Torica_13_3D.FCStd",              "X2-Anillo_Torica_13_3D_Item18.stl",            180,   None),
    (19, 2, "Estructura_Interior_07_3D.FCStd",        "X2-Estructura_Interior_07_3D_Item19.stl",        0,   None),
    (20, 2, "Cierre_Estructura_15_3D.FCStd",          "X2-Cierre_Estructura_15_3D_Item20.stl",          0,   None),
    (21, 4, "Tensor_Parte_1_06.FCStd",                "X4-Tensor_Parte_1_06_Item21.stl",              180,   None),
    (22, 4, "Tensor_Parte_2_06.FCStd",                "X4-Tensor_Parte_2_06_Item22.stl",                0,   None),
    (23, 1, "Tapa_Motor_01_3D.FCStd",                 "X1-Tapa_Motor_01_3D_Item23.stl",                 0,   None),
    (31, 2, "Tuerca_Guia_08_3D.FCStd",                "X2-Tuerca_Guia_08_3D_Item31.stl",                0,   None),
    (32, 2, "Arandela_Guia_08_3D.FCStd",              "X2-Arandela_Guia_08_3D_Item32.stl",              0,   None),
]


def _leer_cantidades_bom(ruta_asm):
    """Lee cantidades desde la hoja Lista_de_Materiales del ensamblaje 3D."""
    doc_asm = App.openDocument(ruta_asm)
    try:
        sp = doc_asm.getObject("Lista_de_Materiales")
        if sp is None:
            raise RuntimeError(f"No se encontró Lista_de_Materiales en {ruta_asm}")
        cantidades = {}
        for r in range(2, 80):
            try:
                arch = str(sp.get(f"A{r}")).strip()
                qty = int(float(str(sp.get(f"C{r}")).strip()))
                if arch:
                    cantidades[arch] = qty
            except Exception:
                continue
        return cantidades
    finally:
        App.closeDocument(doc_asm.Name)


def _extraer_solido_principal(doc):
    """Extrae una copia del sólido principal del documento FCStd."""
    part_obj = next((o for o in doc.Objects if o.TypeId == "App::Part"), None)
    sh = None
    if part_obj and hasattr(part_obj, "Shape") and not part_obj.Shape.isNull() and part_obj.Shape.Solids:
        sh = part_obj.Shape.copy()
    else:
        cands = [
            o for o in doc.Objects
            if o.isDerivedFrom("Part::Feature")
            and not o.isDerivedFrom("Part::Datum")
            and not o.Shape.isNull()
            and o.Shape.Solids
        ]
        if not cands:
            raise RuntimeError(f"Sin sólido válido en {doc.FileName}")
        finales = [o for o in cands if not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
        elegido = finales[-1] if finales else max(cands, key=lambda o: o.Shape.Volume)
        sh = elegido.Shape.copy()
    if len(sh.Solids) != 1:
        raise RuntimeError(f"{doc.FileName} tiene {len(sh.Solids)} sólidos (esperado 1)")
    return sh


def exportar_todos():
    print("FreeCAD", ".".join(App.Version()[:3]))
    os.makedirs(DIR_STL, exist_ok=True)
    bom_cant = _leer_cantidades_bom(DIR_ASM)

    errores = []
    total_copias = 0
    for item, qty, src_fn, stl_fn, rot_x, clave_bom in PIEZAS_STL:
        bom_key = clave_bom or src_fn
        if bom_key not in bom_cant:
            raise RuntimeError(f"Falta {bom_key} en Lista_de_Materiales")
        if bom_cant[bom_key] != qty:
            raise RuntimeError(
                f"Discrepancia de cantidad en {bom_key}: BOM={bom_cant[bom_key]} vs script={qty}"
            )

        ruta_fcstd = os.path.join(AQUI, src_fn)
        ruta_stl = os.path.join(DIR_STL, stl_fn)
        doc = App.openDocument(ruta_fcstd)
        try:
            sh = _extraer_solido_principal(doc)
        finally:
            App.closeDocument(doc.Name)

        if rot_x:
            sh.rotate(App.Vector(0.0, 0.0, 0.0), App.Vector(1.0, 0.0, 0.0), float(rot_x))

        vol_cad = sh.Volume
        check = None
        perfil_usado = None
        ultimo_diag = ""
        for ld, ad in PERFILES_MALLA:
            mesh = MeshPart.meshFromShape(
                Shape=sh,
                LinearDeflection=ld,
                AngularDeflection=ad,
                Relative=False,
            )
            mbb = mesh.BoundBox
            cx = 0.5 * (mbb.XMin + mbb.XMax)
            cy = 0.5 * (mbb.YMin + mbb.YMax)
            mesh.translate(-cx, -cy, -mbb.ZMin)
            mesh.write(ruta_stl)

            # Validación posterior sobre el .stl guardado en disco
            cand = Mesh.Mesh(ruta_stl)
            cbb = cand.BoundBox
            vol_stl = cand.Volume
            diff_pct = 100.0 * abs(vol_stl - vol_cad) / max(vol_cad, 1e-6)
            ok = (
                cand.isSolid()
                and not cand.hasNonManifolds()
                and not cand.hasSelfIntersections()
                and cand.countComponents() == 1
                and abs(cbb.ZMin) < 0.01
                and diff_pct < 2.0
            )
            ultimo_diag = (
                f"solid={cand.isSolid()}, nonManifold={cand.hasNonManifolds()}, "
                f"selfInt={cand.hasSelfIntersections()}, comps={cand.countComponents()}, "
                f"ZMin={cbb.ZMin:.3f}, diff={diff_pct:.2f}%"
            )
            if ok:
                check = cand
                perfil_usado = (ld, ad, diff_pct)
                break

        if check is None:
            errores.append(f"{stl_fn}: {ultimo_diag}")
            print(f"ITEM={item:02d} | {stl_fn:<47s} | ERROR: {ultimo_diag}")
            continue

        cbb = check.BoundBox
        vol_stl = check.Volume
        ld_u, ad_u, diff_pct = perfil_usado
        kb = os.path.getsize(ruta_stl) / 1024.0
        total_copias += qty
        print(
            f"ITEM={item:02d} | {stl_fn:<47s} | X{qty} | RotX={rot_x:3d} | "
            f"def={ld_u:.2f}/{ad_u:.2f} | BB={cbb.XLength:6.2f}x{cbb.YLength:6.2f}x{cbb.ZLength:6.2f} | "
            f"Z=[{cbb.ZMin:5.2f},{cbb.ZMax:6.2f}] | Vol={vol_stl:9.1f}mm3 ({diff_pct:.2f}%) | "
            f"Tris={check.CountFacets:6d} | {kb:7.1f}KB | OK=True"
        )

    if errores:
        print("STL_VALIDACION: FALLIDA")
        for err in errores:
            print("  ERROR:", err)
        sys.exit(1)
    print(f"STL_VALIDACION: OK ({len(PIEZAS_STL)} archivos STL, {total_copias} piezas totales)")


if __name__ in ("__main__", "exportar_stl_3d"):
    exportar_todos()
