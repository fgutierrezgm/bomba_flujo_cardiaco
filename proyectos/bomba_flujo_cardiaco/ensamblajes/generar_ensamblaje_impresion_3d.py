#!/usr/bin/env python3
"""
Ensamblaje completo de la versión Impresión 3D (escala 75.5% + componentes comerciales adaptados).
Usa `Assembly::AssemblyObject` nativo (Solver Ondsel MbD) vinculando por `App::Link`:
- Las 20 piezas importadas desde STEP (`*_3D.FCStd`)
- Los 4 pares de tensores divididos (`Tensor_Parte_1_06.FCStd` + `Tensor_Parte_2_06.FCStd`)
- La camisa cilíndrica a escala (`Cilindro_09_3D.FCStd`)
- Todos los componentes comerciales de `piezas/Elementos_comericales/`
  (SKF 609-2Z, Retén 10x22x7, O-Rings DIN 3771 75x3.55 / 69x3.55 / 11.2x1.8, Pasadores 3x14 / 3x10).

Ejecutar:
  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/ensamblajes/generar_ensamblaje_impresion_3d.py
"""
import json
import os
import sys
import FreeCAD as App

AQUI = os.path.dirname(
    os.path.abspath(
        globals().get(
            "__file__",
            "proyectos/bomba_flujo_cardiaco/ensamblajes/generar_ensamblaje_impresion_3d.py",
        )
    )
)
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
from fc_helpers import MATERIALES_BASE

import JointObject
import UtilsAssembly

DIR_PROYECTO = os.path.abspath(os.path.join(AQUI, ".."))
DIR_PIEZAS = os.path.join(DIR_PROYECTO, "piezas")
DIR_COM = os.path.join(DIR_PIEZAS, "Elementos_comericales")
RUTA_SALIDA = os.path.join(DIR_PROYECTO, "ensamblajes", "Piloto_Impresion_3D_Assembly.FCStd")


def p(nombre):
    return os.path.join(DIR_PIEZAS, nombre)


def c(nombre):
    return os.path.join(DIR_COM, nombre)


def _abrir_part(ruta_fcstd):
    ruta_abs = os.path.abspath(ruta_fcstd)
    if not os.path.exists(ruta_abs):
        raise FileNotFoundError(f"No existe la pieza: {ruta_abs}")
    doc_h = next(
        (d for d in App.listDocuments().values() if os.path.abspath(getattr(d, "FileName", "")) == ruta_abs),
        None,
    )
    if doc_h is None:
        doc_h = App.openDocument(ruta_abs, True)
    part_h = next((o for o in doc_h.Objects if o.TypeId == "App::Part"), None)
    if part_h is None:
        raise RuntimeError(f"{ruta_abs} no tiene contenedor App::Part")
    return doc_h, part_h


def _lcs_plc(part_h, nombre_lcs):
    if not nombre_lcs or nombre_lcs == "Origin":
        return App.Placement()
    for o in part_h.Group:
        if o.Name == nombre_lcs or o.Label == nombre_lcs:
            return App.Placement(o.Placement)
    return App.Placement()


def asegurar_link(doc, asm, ruta_fcstd, nombre_inst):
    _, part_h = _abrir_part(ruta_fcstd)
    ex = doc.getObject(nombre_inst)
    if ex is not None and ex.TypeId == "App::Link":
        return ex
    lnk = asm.newObject("App::Link", nombre_inst)
    lnk.Label = nombre_inst
    lnk.LinkedObject = part_h
    return lnk


def asegurar_grounded(jg, link_fijo, nombre="Grounded_Base"):
    for o in jg.Group:
        if o.Name == nombre:
            return o
    g = jg.newObject("App::FeaturePython", nombre)
    JointObject.GroundedJoint(g, link_fijo)
    if App.GuiUp and getattr(g, "ViewObject", None) is not None:
        vp = JointObject.ViewProviderGroundedJoint(g.ViewObject)
        vp.app_obj = g
        vp.attach(g.ViewObject)
    return g


def asegurar_junta(
    doc,
    jg,
    nombre,
    tipo,
    lnk1,
    lcs1,
    lnk2,
    lcs2,
    off1=None,
    off2=None,
    extras=None,
):
    ex = doc.getObject(nombre)
    if ex is not None:
        return ex

    o1 = off1 if off1 is not None else App.Placement()
    o2 = off2 if off2 is not None else App.Placement()

    p1 = _lcs_plc(lnk1.LinkedObject, lcs1)
    p2 = _lcs_plc(lnk2.LinkedObject, lcs2)
    lnk2.Placement = (lnk1.Placement * p1 * o1) * (p2 * o2).inverse()

    j = jg.newObject("App::FeaturePython", nombre)
    idx_tipo = JointObject.JointTypes.index(tipo)
    JointObject.Joint(j, idx_tipo)
    if App.GuiUp and getattr(j, "ViewObject", None) is not None:
        vp = JointObject.ViewProviderJoint(j.ViewObject)
        vp.app_obj = j
        vp.attach(j.ViewObject)

    j.Reference1 = [lnk1, [f"{lcs1}.", f"{lcs1}."]]
    j.Reference2 = [lnk2, [f"{lcs2}.", f"{lcs2}."]]
    j.Offset1 = o1
    j.Offset2 = o2
    if extras:
        for k, v in extras.items():
            if hasattr(j, k):
                setattr(j, k, v)
    return j


def _prop_str(obj, prop, default=""):
    try:
        return str(obj.getContents(prop)) if hasattr(obj, "getContents") else default
    except Exception:
        return default


def _leer_material_pieza(dh):
    """Extrae material, densidad, color RGB y transparencia desde la hoja `Materiales` de una pieza."""
    hm = dh.getObject("Materiales")
    mat_nombre = ""
    dens = 0.0
    rgb = (0.72, 0.74, 0.76)
    tr = 0
    if hm is not None:
        for alias, cell in (("material", "B2"),):
            try:
                mat_nombre = str(hm.get(alias))
                break
            except Exception:
                pass
        if not mat_nombre:
            try:
                mat_nombre = str(hm.get("B2"))
            except Exception:
                mat_nombre = ""
        for alias in ("densidad", "B3"):
            try:
                dens = float(hm.get(alias))
                break
            except Exception:
                pass
        try:
            r, g, b = float(hm.get("color_r")), float(hm.get("color_g")), float(hm.get("color_b"))
            if r > 1 or g > 1 or b > 1:
                r, g, b = r / 255.0, g / 255.0, b / 255.0
            rgb = (r, g, b)
        except Exception:
            pass
        for alias in ("transparencia_mat", "B7"):
            try:
                tr = int(float(hm.get(alias)))
                break
            except Exception:
                pass
    if not mat_nombre or dens <= 0:
        for k, meta in MATERIALES_BASE.items():
            if k.lower() in dh.Name.lower():
                mat_nombre = meta["nombre"]
                dens = meta["densidad"]
                rgb = meta["color"]
                tr = meta.get("transparencia", 0)
                break
    return mat_nombre, dens, rgb, tr


def _solido_principal_part(part_h):
    for o in part_h.Group:
        if getattr(o, "Visibility", False) and hasattr(o, "Shape") and not o.Shape.isNull():
            return o
    for o in part_h.Group:
        if hasattr(o, "Shape") and not o.Shape.isNull():
            return o
    return None


def generar_hojas_materiales_y_bom(doc, asm, transp_insp_map=None):
    """Crea/actualiza `Materiales_Generales`, `Lista_de_Materiales` y `Reporte_Fisico`."""
    transp_insp_map = transp_insp_map or {}
    links = [o for o in asm.Group if o.TypeId == "App::Link" and o.LinkedObject]

    # Preservar filas marcadas como PERSONALIZADO=1 en Materiales_Generales existente
    mg_old = doc.getObject("Materiales_Generales")
    preservados = {}
    if mg_old is not None:
        r = 2
        while True:
            try:
                comp = str(mg_old.get(f"A{r}")).strip()
            except Exception:
                break
            if not comp:
                break
            try:
                pers = int(float(mg_old.get(f"I{r}")))
            except Exception:
                pers = 0
            if pers == 1:
                preservados[comp] = (
                    str(mg_old.get(f"B{r}")),
                    float(mg_old.get(f"C{r}")),
                    float(mg_old.get(f"D{r}")),
                    float(mg_old.get(f"E{r}")),
                    float(mg_old.get(f"F{r}")),
                    int(float(mg_old.get(f"G{r}"))),
                    int(float(mg_old.get(f"H{r}"))),
                    1,
                )
            r += 1
        doc.removeObject("Materiales_Generales")

    mg = doc.addObject("Spreadsheet::Sheet", "Materiales_Generales")
    headers_mg = [
        "COMPONENTE", "MATERIAL", "DENSIDAD",
        "COLOR_R", "COLOR_G", "COLOR_B",
        "TRANSP_BASE", "TRANSP_INSP", "PERSONALIZADO",
    ]
    for idx_c, txt in enumerate(headers_mg):
        col = chr(ord("A") + idx_c)
        mg.set(f"{col}1", txt)

    bom_conteo = {}
    for idx, lnk in enumerate(links, start=2):
        dh = lnk.LinkedObject.Document
        mat_nombre, dens, rgb, tr_base = _leer_material_pieza(dh)
        tr_insp = transp_insp_map.get(lnk.Name, tr_base)

        if lnk.Name in preservados:
            mat_nombre, dens, rr, gg, bb, tr_base, tr_insp, pers = preservados[lnk.Name]
            rgb = (rr, gg, bb)
        else:
            pers = 0

        mg.set(f"A{idx}", lnk.Name)
        mg.set(f"B{idx}", mat_nombre)
        mg.set(f"C{idx}", f"{dens:.8g}")
        mg.set(f"D{idx}", f"{rgb[0]:.3f}")
        mg.set(f"E{idx}", f"{rgb[1]:.3f}")
        mg.set(f"F{idx}", f"{rgb[2]:.3f}")
        mg.set(f"G{idx}", str(int(tr_base)))
        mg.set(f"H{idx}", str(int(tr_insp)))
        mg.set(f"I{idx}", str(pers))

        archivo = os.path.basename(getattr(dh, "FileName", "") or f"{dh.Name}.FCStd")
        clave_bom = (archivo, dh.Name, mat_nombre)
        bom_conteo[clave_bom] = bom_conteo.get(clave_bom, 0) + 1

        if App.GuiUp and hasattr(lnk, "ViewObject") and lnk.ViewObject:
            try:
                tr_ef = max(tr_base, tr_insp) / 100.0
                mat = App.Material()
                mat.DiffuseColor = rgb
                mat.Transparency = tr_ef
                lnk.ViewObject.OverrideMaterial = True
                lnk.ViewObject.ShapeAppearance = (mat,)
            except Exception:
                pass

    # Lista_de_Materiales (BOM)
    if doc.getObject("Lista_de_Materiales"):
        doc.removeObject("Lista_de_Materiales")
    bom = doc.addObject("Spreadsheet::Sheet", "Lista_de_Materiales")
    for col, txt in (("A", "ARCHIVO"), ("B", "PIEZA"), ("C", "CANTIDAD"), ("D", "MATERIAL")):
        bom.set(f"{col}1", txt)
    for idx, ((archivo, pieza, mat_n), cant) in enumerate(sorted(bom_conteo.items()), start=2):
        bom.set(f"A{idx}", archivo)
        bom.set(f"B{idx}", pieza)
        bom.set(f"C{idx}", str(cant))
        bom.set(f"D{idx}", mat_n)

    # Reporte_Fisico (masas individuales vinculadas + masa total)
    if doc.getObject("Reporte_Fisico"):
        doc.removeObject("Reporte_Fisico")
    rf = doc.addObject("Spreadsheet::Sheet", "Reporte_Fisico")
    for col, txt in (
        ("A", "COMPONENTE"),
        ("B", "MATERIAL"),
        ("C", "VOLUMEN (mm^3)"),
        ("D", "DENSIDAD (kg/mm^3)"),
        ("E", "MASA (kg)"),
    ):
        rf.set(f"{col}1", txt)

    for idx, lnk in enumerate(links, start=2):
        dh = lnk.LinkedObject.Document
        sol = _solido_principal_part(lnk.LinkedObject)
        rf.set(f"A{idx}", lnk.Name)
        rf.set(f"B{idx}", f"=<<Materiales_Generales>>.B{idx}")
        if sol is not None:
            rf.set(f"C{idx}", f"={dh.Name}#{sol.Name}.Shape.Volume")
        else:
            rf.set(f"C{idx}", "0")
        rf.set(f"D{idx}", f"=<<Materiales_Generales>>.C{idx}")
        rf.set(f"E{idx}", f"=C{idx} * D{idx} * 1 kg")

    fila_tot = len(links) + 2
    rf.set(f"A{fila_tot}", "MASA TOTAL ENSAMBLAJE")
    rf.set(f"E{fila_tot}", f"=sum(E2:E{fila_tot - 1})")
    rf.setAlias(f"E{fila_tot}", "masa_total_ensamblaje")
    return mg, bom, rf


def main():
    print("FreeCAD", ".".join(App.Version()[:3]))
    nombre_doc = "Piloto_Impresion_3D_Assembly"
    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    if nombre_doc in App.listDocuments():
        App.closeDocument(nombre_doc)
    doc = App.newDocument(nombre_doc)
    doc.saveAs(RUTA_SALIDA)

    asm = doc.addObject("Assembly::AssemblyObject", nombre_doc)
    asm.Label = nombre_doc

    pg = asm.newObject("Spreadsheet::Sheet", "Parametros_Generales")
    pg.set("A1", "PARÁMETRO"); pg.set("B1", "VALOR"); pg.set("C1", "DESCRIPCIÓN")
    pg.set("A2", "Factor de explosión"); pg.set("B2", "0.0")
    pg.setAlias("B2", "explosion")
    pg.set("C2", "0.0 = Ensamblado | 1.0 = Vista Explotada")
    pg.set("A3", "Modo de diseño global"); pg.set("B3", "1")
    pg.setAlias("B3", "modo_diseno_global")
    pg.set("C3", "1 = Impresión 3D (escala 0.755 + holguras FDM)")

    jg = UtilsAssembly.getJointGroup(asm)

    # =========================================================================
    # 1. BASE FIJA: Tapa Interior 16b_3D
    # =========================================================================
    lnk_tapa_int = asegurar_link(doc, asm, p("Tapa_Interior_16b_3D.FCStd"), "Tapa_Interior_16b_3D")
    asegurar_grounded(jg, lnk_tapa_int, "Grounded_Tapa_Interior_3D")

    # =========================================================================
    # 2. CÁMARA ACRÍLICA, O-RINGS 75x3.55 Y TAPA EXTERIOR 16a_3D
    # =========================================================================
    rot_flip_x = App.Rotation(App.Vector(1, 0, 0), 180)

    lnk_cil = asegurar_link(doc, asm, p("Cilindro_09_3D.FCStd"), "Cilindro_09_3D")
    asegurar_junta(
        doc, jg, "Joint_Cilindro_3D", "Fixed",
        lnk_tapa_int, "LCS_Origen",
        lnk_cil, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 8.12), rot_flip_x),
    )

    lnk_tapa_ext = asegurar_link(doc, asm, p("Tapa_Exterior_16a_3D.FCStd"), "Tapa_Exterior_16a_3D")
    asegurar_junta(
        doc, jg, "Joint_Tapa_Exterior_3D", "Fixed",
        lnk_cil, "LCS_Extremo_Sup",
        lnk_tapa_ext, "LCS_Cara_Sup",
        off1=App.Placement(App.Vector(0, 0, -7.36), rot_flip_x),
    )

    lnk_oring_int = asegurar_link(doc, asm, c("ORing_75x3_55.FCStd"), "ORing_Camisa_Int")
    lnk_oring_ext = asegurar_link(doc, asm, c("ORing_75x3_55.FCStd"), "ORing_Camisa_Ext")
    asegurar_junta(
        doc, jg, "Joint_ORing_Camisa_Int", "Fixed",
        lnk_tapa_int, "LCS_Origen", lnk_oring_int, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 2.60), App.Rotation()),
    )
    asegurar_junta(
        doc, jg, "Joint_ORing_Camisa_Ext", "Fixed",
        lnk_tapa_ext, "LCS_Cara_Sup", lnk_oring_ext, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, -2.60), App.Rotation()),
    )

    # Anillos de junta tórica (Plano 13) y Estructura Interior (Plano 7) + Cierre (Plano 15)
    lnk_anillo_1 = asegurar_link(doc, asm, p("Anillo_Torica_13_3D.FCStd"), "Anillo_Torica_Int_13_3D")
    lnk_anillo_2 = asegurar_link(doc, asm, p("Anillo_Torica_13_3D.FCStd"), "Anillo_Torica_Ext_13_3D")
    asegurar_junta(
        doc, jg, "Joint_Anillo_Int", "Fixed",
        lnk_tapa_int, "LCS_Origen", lnk_anillo_1, "LCS_Cara_Sup",
        off1=App.Placement(App.Vector(0, 0, -0.02), App.Rotation()),
    )
    asegurar_junta(
        doc, jg, "Joint_Anillo_Ext", "Fixed",
        lnk_tapa_ext, "LCS_Cara_Sup", lnk_anillo_2, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 0.02), App.Rotation()),
    )

    lnk_est_1 = asegurar_link(doc, asm, p("Estructura_Interior_07_3D.FCStd"), "Estructura_Interior_1_07_3D")
    lnk_est_2 = asegurar_link(doc, asm, p("Estructura_Interior_07_3D.FCStd"), "Estructura_Interior_2_07_3D")
    asegurar_junta(
        doc, jg, "Joint_Estructura_1", "Fixed",
        lnk_tapa_int, "LCS_Cara_Sup", lnk_est_1, "LCS_Cara_Sup",
        off1=App.Placement(App.Vector(0, 0, -5.66), rot_flip_x),
    )
    asegurar_junta(
        doc, jg, "Joint_Estructura_2", "Fixed",
        lnk_tapa_ext, "LCS_Origen", lnk_est_2, "LCS_Cara_Sup",
        off1=App.Placement(App.Vector(0, 0, 5.66), App.Rotation()),
    )

    lnk_cierre_1 = asegurar_link(doc, asm, p("Cierre_Estructura_15_3D.FCStd"), "Cierre_Estructura_1_15_3D")
    lnk_cierre_2 = asegurar_link(doc, asm, p("Cierre_Estructura_15_3D.FCStd"), "Cierre_Estructura_2_15_3D")
    asegurar_junta(
        doc, jg, "Joint_Cierre_1", "Fixed",
        lnk_est_1, "LCS_Origen", lnk_cierre_1, "LCS_Cara_Sup",
        off1=App.Placement(App.Vector(0, 0, -0.02), App.Rotation()),
    )
    asegurar_junta(
        doc, jg, "Joint_Cierre_2", "Fixed",
        lnk_est_2, "LCS_Origen", lnk_cierre_2, "LCS_Cara_Sup",
        off1=App.Placement(App.Vector(0, 0, -0.02), App.Rotation()),
    )

    # =========================================================================
    # 3. GUÍAS, SUFRIDERAS DE GUÍA Y TREN MÓVIL DEL ÉMBOLO (Slider)
    # =========================================================================
    for idx_g, xg in ((1, -28.31), (2, 28.31)):
        lnk_g = asegurar_link(doc, asm, p("Guia_08_3D.FCStd"), f"Guia_{idx_g}_08_3D")
        asegurar_junta(
            doc, jg, f"Joint_Guia_{idx_g}_3D", "Fixed",
            lnk_tapa_int, "LCS_Cara_Sup", lnk_g, "LCS_Origen",
            off1=App.Placement(App.Vector(xg, 0, 11.33), rot_flip_x),
        )
        # 2 sufrideras por barra guía (4 en total según x4 - plano5-Sufridera guia.stp)
        lnk_sg_a = asegurar_link(doc, asm, p("Sufridera_Guia_05b_3D.FCStd"), f"Sufridera_Guia_{idx_g}A_3D")
        lnk_sg_b = asegurar_link(doc, asm, p("Sufridera_Guia_05b_3D.FCStd"), f"Sufridera_Guia_{idx_g}B_3D")
        asegurar_junta(
            doc, jg, f"Joint_Suf_Guia_{idx_g}A", "Fixed",
            lnk_tapa_int, "LCS_Cara_Sup", lnk_sg_a, "LCS_Origen",
            off1=App.Placement(App.Vector(xg, 0, 0.02), App.Rotation()),
        )
        asegurar_junta(
            doc, jg, f"Joint_Suf_Guia_{idx_g}B", "Fixed",
            lnk_tapa_int, "LCS_Origen", lnk_sg_b, "LCS_Origen",
            off1=App.Placement(App.Vector(xg, 0, 11.33), App.Rotation()),
        )

    lnk_embolo = asegurar_link(doc, asm, p("Embolo_Delrin_10_3D.FCStd"), "Embolo_Delrin_10_3D")
    asegurar_junta(
        doc, jg, "Joint_Slider_Embolo_3D", "Slider",
        lnk_tapa_int, "LCS_Origen", lnk_embolo, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, -80.0), App.Rotation()),
        extras={"EnableLengthMin": True, "EnableLengthMax": True, "LengthMin": -50.0, "LengthMax": 50.0},
    )

    lnk_oring_emb = asegurar_link(doc, asm, c("ORing_69x3_55.FCStd"), "ORing_Embolo_3D")
    asegurar_junta(
        doc, jg, "Joint_ORing_Embolo_3D", "Fixed",
        lnk_embolo, "LCS_Centro", lnk_oring_emb, "LCS_Origen",
    )

    lnk_ce1 = asegurar_link(doc, asm, p("Centro_Embolo_1_11_3D.FCStd"), "Centro_Embolo_1_11_3D")
    lnk_ce2 = asegurar_link(doc, asm, p("Centro_Embolo_2_12_3D.FCStd"), "Centro_Embolo_2_12_3D")
    asegurar_junta(doc, jg, "Joint_CE1_3D", "Fixed", lnk_embolo, "LCS_Cara_Sup", lnk_ce1, "LCS_Origen")
    asegurar_junta(doc, jg, "Joint_CE2_3D", "Fixed", lnk_embolo, "LCS_Origen", lnk_ce2, "LCS_Cara_Sup")

    lnk_sp1 = asegurar_link(doc, asm, p("Sensor_Piston_05b_3D.FCStd"), "Sensor_Piston_1_3D")
    lnk_sp2 = asegurar_link(doc, asm, p("Sensor_Piston_05b_3D.FCStd"), "Sensor_Piston_2_3D")
    asegurar_junta(
        doc, jg, "Joint_SP1_3D", "Fixed",
        lnk_embolo, "LCS_Cara_Sup", lnk_sp1, "LCS_Origen",
        off1=App.Placement(App.Vector(20.02, 20.02, 0), App.Rotation()),
    )
    asegurar_junta(
        doc, jg, "Joint_SP2_3D", "Fixed",
        lnk_embolo, "LCS_Origen", lnk_sp2, "LCS_Cara_Sup",
        off1=App.Placement(App.Vector(-20.02, 20.02, 0), App.Rotation()),
    )

    # =========================================================================
    # 4. TRANSMISIÓN, RETÉN 10x22x7, RODAMIENTO SKF 609-2Z Y PASADORES
    # =========================================================================
    # Sufridera interior + Retén 10x22x7 alojados dentro del bolsillo Ø34.05 de Tapa_Interior (Z=11.70..19.25)
    lnk_suf_int = asegurar_link(doc, asm, p("Sufridera_Int_05b_3D.FCStd"), "Sufridera_Int_05b_3D")
    asegurar_junta(
        doc, jg, "Joint_Sufridera_Int_3D", "Fixed",
        lnk_tapa_int, "LCS_Origen", lnk_suf_int, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 12.12), App.Rotation()),
    )

    lnk_reten = asegurar_link(doc, asm, c("Reten_10x22x7.FCStd"), "Reten_10x22x7")
    asegurar_junta(
        doc, jg, "Joint_Reten_3D", "Fixed",
        lnk_suf_int, "LCS_Origen", lnk_reten, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 0.02), App.Rotation()),
    )

    lnk_tapa_suf = asegurar_link(doc, asm, p("Tapa_Sufridera_Int_05a_3D.FCStd"), "Tapa_Sufridera_Int_05a_3D")
    asegurar_junta(
        doc, jg, "Joint_Tapa_Suf_3D", "Fixed",
        lnk_tapa_int, "LCS_Origen", lnk_tapa_suf, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 10.60), App.Rotation()),
    )

    # Adaptador del eje (Z=22.67..35.13) + Adaptador de rodamiento anidado en -Z (Z=19.65..38.90)
    lnk_ad_eje = asegurar_link(doc, asm, p("Adaptador_Eje_04_3D.FCStd"), "Adaptador_Eje_04_3D")
    asegurar_junta(
        doc, jg, "Joint_Ad_Eje_3D", "Fixed",
        lnk_tapa_int, "LCS_Cara_Sup", lnk_ad_eje, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 12.48), rot_flip_x),
    )

    lnk_ad_rod = asegurar_link(doc, asm, p("Adaptador_Rodamiento_03_3D.FCStd"), "Adaptador_Rodamiento_03_3D")
    asegurar_junta(
        doc, jg, "Joint_Ad_Rod_3D", "Fixed",
        lnk_ad_eje, "LCS_Origen", lnk_ad_rod, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, -3.79), App.Rotation()),
    )

    lnk_skf609 = asegurar_link(doc, asm, c("Rodamiento_SKF_609.FCStd"), "Rodamiento_SKF_609")
    asegurar_junta(
        doc, jg, "Joint_SKF_609", "Fixed",
        lnk_ad_rod, "LCS_Origen", lnk_skf609, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 11.67), App.Rotation()),
    )

    # Sufridera eje exterior montada en la Tapa Exterior (Z=-194.04..-184.22)
    lnk_suf_ext = asegurar_link(doc, asm, p("Sufridera_Eje_Ext_05a_3D.FCStd"), "Sufridera_Eje_Ext_05a_3D")
    asegurar_junta(
        doc, jg, "Joint_Suf_Ext_3D", "Fixed",
        lnk_tapa_ext, "LCS_Origen", lnk_suf_ext, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 11.70), rot_flip_x),
    )

    # Cadena rotativa coaxial: Husillo (-194.03..-1.88) -> Transmisor B (-13.13..82.70) -> Transmisor A (32.14..128.02)
    lnk_hus = asegurar_link(doc, asm, p("Tornillo_Sin_Fin_14_3D.FCStd"), "Tornillo_Sin_Fin_14_3D")
    asegurar_junta(
        doc, jg, "Joint_Husillo_3D", "Fixed",
        lnk_tapa_int, "LCS_Origen", lnk_hus, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, -1.88), rot_flip_x),
    )

    lnk_tb = asegurar_link(doc, asm, p("Transmisor_B_02b_3D.FCStd"), "Transmisor_B_02b_3D")
    asegurar_junta(
        doc, jg, "Joint_Transmisor_B", "Fixed",
        lnk_hus, "LCS_Origen", lnk_tb, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, -84.58), App.Rotation()),
    )

    lnk_ta = asegurar_link(doc, asm, p("Transmisor_A_02a_3D.FCStd"), "Transmisor_A_02a_3D")
    asegurar_junta(
        doc, jg, "Joint_Transmisor_A", "Fixed",
        lnk_tb, "LCS_Origen", lnk_ta, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, -45.32), App.Rotation()),
    )

    lnk_oring_eje = asegurar_link(doc, asm, c("ORing_11_2x1_8.FCStd"), "ORing_Eje_11_2x1_8")
    asegurar_junta(
        doc, jg, "Joint_ORing_Eje", "Fixed",
        lnk_tb, "LCS_Origen", lnk_oring_eje, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 54.50), App.Rotation()),
    )

    rot_pas = App.Rotation(App.Vector(1, 0, 0), 90)
    lnk_p1 = asegurar_link(doc, asm, c("Pasador_3x14.FCStd"), "Pasador_3x14_1")
    lnk_p2 = asegurar_link(doc, asm, c("Pasador_3x14.FCStd"), "Pasador_3x14_2")
    lnk_p3 = asegurar_link(doc, asm, c("Pasador_3x10.FCStd"), "Pasador_3x10_3")
    asegurar_junta(doc, jg, "Joint_Pas_1", "Fixed", lnk_ta, "LCS_Origen", lnk_p1, "LCS_Origen", off1=App.Placement(App.Vector(0, 0, 50.96), rot_pas))
    asegurar_junta(doc, jg, "Joint_Pas_2", "Fixed", lnk_ta, "LCS_Origen", lnk_p2, "LCS_Origen", off1=App.Placement(App.Vector(0, 0, 84.94), rot_pas))
    asegurar_junta(doc, jg, "Joint_Pas_3", "Fixed", lnk_tb, "LCS_Origen", lnk_p3, "LCS_Origen", off1=App.Placement(App.Vector(0, 0, 90.22), rot_pas))

    # =========================================================================
    # 5. 4x TENSORES DIVIDIDOS (Parte 1 + Parte 2) + TAPA MOTOR 01
    # =========================================================================
    coords_tens = [(1, 54.36, 54.36), (2, -54.36, 54.36), (3, -54.36, -54.36), (4, 54.36, -54.36)]
    for idx_t, xt, yt in coords_tens:
        lnk_tp2 = asegurar_link(doc, asm, p("Tensor_Parte_2_06.FCStd"), f"Tensor_{idx_t}_Parte_2")
        lnk_tp1 = asegurar_link(doc, asm, p("Tensor_Parte_1_06.FCStd"), f"Tensor_{idx_t}_Parte_1")
        asegurar_junta(
            doc, jg, f"Joint_Tensor_P2_{idx_t}", "Fixed",
            lnk_est_2, "LCS_Cara_Sup", lnk_tp2, "LCS_Origen",
            off1=App.Placement(App.Vector(xt, yt, -14.35), App.Rotation()),
        )
        # Empalme por espiga triangular: Parte 1 LCS_Origen acopla contra Parte 2 LCS_Encastre_Macho
        asegurar_junta(
            doc, jg, f"Joint_Tensor_Empalme_{idx_t}", "Fixed",
            lnk_tp2, "LCS_Encastre_Macho", lnk_tp1, "LCS_Origen",
        )

    lnk_tapa_mot = asegurar_link(doc, asm, p("Tapa_Motor_01_3D.FCStd"), "Tapa_Motor_01_3D")
    asegurar_junta(
        doc, jg, "Joint_Tapa_Motor", "Fixed",
        lnk_tapa_ext, "LCS_Origen", lnk_tapa_mot, "LCS_Origen",
        off1=App.Placement(App.Vector(0, 0, 276.55), App.Rotation()),
    )

    for o in jg.Group:
        o.Visibility = False

    # Declarar pares de ajuste / sellos / roscas esperados para verificar_interfaces.py
    pares_esperados = [
        ["Embolo_Delrin_10_3D", "ORing_Embolo_3D"],
        ["Cilindro_09_3D", "ORing_Embolo_3D"],
        ["Tapa_Interior_16b_3D", "ORing_Camisa_Int"],
        ["Tapa_Exterior_16a_3D", "ORing_Camisa_Ext"],
        ["Cilindro_09_3D", "ORing_Camisa_Int"],
        ["Cilindro_09_3D", "ORing_Camisa_Ext"],
        ["Transmisor_A_02a_3D", "Pasador_3x14_1"],
        ["Transmisor_B_02b_3D", "Pasador_3x14_1"],
        ["Transmisor_A_02a_3D", "Pasador_3x14_2"],
        ["Transmisor_B_02b_3D", "Pasador_3x14_2"],
        ["Transmisor_B_02b_3D", "Pasador_3x10_3"],
        ["Tornillo_Sin_Fin_14_3D", "Pasador_3x10_3"],
        ["Transmisor_B_02b_3D", "ORing_Eje_11_2x1_8"],
        ["Centro_Embolo_1_11_3D", "Tornillo_Sin_Fin_14_3D"],
    ]
    for it_num in range(1, 5):
        pares_esperados.append([f"Tensor_{it_num}_Parte_1", f"Tensor_{it_num}_Parte_2"])

    interferencias_plano = [
        {
            "par": ["Rodamiento_SKF_609", "Transmisor_B_02b_3D"],
            "motivo": "Cuello acero AISI 304 Ø11.32 mm del STEP original vs piste int. SKF 609 Ø9.00 mm (requiere torneado del eje metálico a Ø9.00 k5)",
        },
        {
            "par": ["Reten_10x22x7", "Transmisor_B_02b_3D"],
            "motivo": "Cuello acero AISI 304 Ø11.32 mm del STEP original vs labio Retén 10x22x7 Ø10.00 mm (requiere torneado del eje metálico a Ø10.00 h9)",
        },
    ]

    if not hasattr(asm, "Interfaces_Declaradas"):
        asm.addProperty("App::PropertyString", "Interfaces_Declaradas", "Ingenieria", "Pares de ajuste y sellos")
    asm.Interfaces_Declaradas = json.dumps(
        {
            "pares_rosca_ajuste": pares_esperados,
            "interferencias_plano": interferencias_plano,
        },
        ensure_ascii=False,
    )

    doc.recompute()
    res = asm.solve()
    print(f"Solver Assembly (0 = OK): {res}")
    transp_insp_map = {
        "Cilindro_09_3D": 75,
        "Tapa_Exterior_16a_3D": 65,
    }
    generar_hojas_materiales_y_bom(doc, asm, transp_insp_map=transp_insp_map)
    doc.recompute()
    doc.saveAs(RUTA_SALIDA)
    print("Guardado ensamblaje 3D:", RUTA_SALIDA)


if __name__ in ("__main__", "generar_ensamblaje_impresion_3d"):
    main()
