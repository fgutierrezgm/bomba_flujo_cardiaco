#!/usr/bin/env python3
"""
Piloto de ensamblaje cinemático completo con el banco Assembly de FreeCAD 1.x (Solver Ondsel MbD).
Mecanismo completo de la Bomba de Flujo Cardíaco: 32 instancias vinculadas (App::Link).

Características clave:
- Usa `Assembly::AssemblyObject` nativo y juntas cinemáticas reales (`Fixed`, `Slider`, `GroundedJoint`)
  apuntando a los conectores `LCS_*` (`PartDesign::CoordinateSystem`) de cada pieza.
- El tren móvil del émbolo (`Embolo_Delrin_10`, `Centro_Embolo_1_11`, `Centro_Embolo_2_12` y
  los 2x `Sensor_Piston_05b`) se desplaza solidariamente sobre las guías con una junta `Slider`
  con límites de carrera configurados (-100 mm a 100 mm respecto a la posición central Z=115 mm).
- Modo incremental: si `Piloto_Embolo_Assembly.FCStd` ya existe y no se pasa `FORZAR=1`,
  preserva cualquier pieza o junta agregada/editada manualmente en la GUI.
- Hoja `Materiales_Generales` sincronizada automáticamente con colores y transparencias de inspección.
- Celda `modo_diseno_global` en `Parametros_Generales` que conmuta todas las piezas hijas entre
  1 (Impresión 3D), 2 (CNC/Planos) y 3 (Render/Nominal).

Ejecutar:
  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/ensamblajes/generar_piloto_embolo_assembly.py
"""
import json
import os
import sys
import FreeCAD as App

AQUI = os.path.dirname(
    os.path.abspath(
        globals().get(
            "__file__",
            "proyectos/bomba_flujo_cardiaco/ensamblajes/generar_piloto_embolo_assembly.py",
        )
    )
)
sys.path.insert(0, os.path.join(AQUI, "..", "..", "..", "_herramientas"))
from fc_helpers import MATERIALES_BASE

import JointObject
import UtilsAssembly

DIR_PROYECTO = os.path.abspath(os.path.join(AQUI, ".."))
DIR_PIEZAS = os.path.join(DIR_PROYECTO, "piezas")
RUTA_SALIDA = os.path.join(DIR_PROYECTO, "ensamblajes", "Piloto_Embolo_Assembly.FCStd")


def p(nombre_archivo):
    return os.path.join(DIR_PIEZAS, nombre_archivo)


def _obtener_part_hijo(ruta_fcstd):
    ruta_abs = os.path.abspath(ruta_fcstd)
    if not os.path.exists(ruta_abs):
        raise FileNotFoundError(f"No existe la pieza: {ruta_abs}")
    doc_hijo = next(
        (d for d in App.listDocuments().values() if os.path.abspath(getattr(d, "FileName", "")) == ruta_abs),
        None,
    )
    if doc_hijo is None:
        doc_hijo = App.openDocument(ruta_abs, True)
    part_hijo = next((o for o in doc_hijo.Objects if o.TypeId == "App::Part"), None)
    if part_hijo is None:
        raise RuntimeError(f"{ruta_abs} no contiene un contenedor App::Part")
    return doc_hijo, part_hijo


def _obtener_lcs_plc(part_hijo, nombre_lcs):
    if not nombre_lcs or nombre_lcs == "Origin":
        return App.Placement()
    for o in part_hijo.Group:
        if o.Name == nombre_lcs or o.Label == nombre_lcs:
            return o.Placement
    raise RuntimeError(f"Conector '{nombre_lcs}' no encontrado en '{part_hijo.Label}'")


def asegurar_link(doc, asm, ruta_fcstd, nombre_instancia, plc_inicial=None):
    """Obtiene o crea un App::Link dentro de Assembly::AssemblyObject."""
    existente = doc.getObject(nombre_instancia)
    _, part_hijo = _obtener_part_hijo(ruta_fcstd)
    if existente is not None:
        if getattr(existente, "LinkedObject", None) != part_hijo:
            existente.LinkedObject = part_hijo
        return existente, False

    lnk = asm.newObject("App::Link", nombre_instancia)
    lnk.Label = nombre_instancia
    lnk.LinkedObject = part_hijo
    if plc_inicial is not None:
        lnk.Placement = plc_inicial
    return lnk, True


def asegurar_grounded(jg, link_fijo, nombre="GroundedJoint"):
    """Asegura que exista un GroundedJoint para la pieza base."""
    for o in jg.Group:
        if hasattr(o, "ObjectToGround") and o.ObjectToGround == link_fijo:
            if App.GuiUp and getattr(o, "ViewObject", None) is not None:
                vp = getattr(o.ViewObject, "Proxy", None)
                if not isinstance(vp, JointObject.ViewProviderGroundedJoint) or not hasattr(vp, "app_obj"):
                    vp = JointObject.ViewProviderGroundedJoint(o.ViewObject)
                    vp.app_obj = o
                    vp.attach(o.ViewObject)
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
    asm,
    jg,
    nombre_junta,
    tipo_junta,
    link1,
    lcs1,
    link2,
    lcs2,
    offset1=None,
    offset2=None,
    plc_pre_alineacion=True,
    propiedades_extra=None,
):
    """
    Obtiene o crea una junta nativa del banco Assembly entre (link1, lcs1) y (link2, lcs2).
    Si la junta ya existe en el documento, la respeta sin sobrescribir ajustes manuales.
    """
    existente = doc.getObject(nombre_junta)
    if existente is not None:
        if App.GuiUp and getattr(existente, "ViewObject", None) is not None:
            vp = getattr(existente.ViewObject, "Proxy", None)
            if not isinstance(vp, JointObject.ViewProviderJoint) or not hasattr(vp, "app_obj"):
                vp = JointObject.ViewProviderJoint(existente.ViewObject)
                vp.app_obj = existente
                vp.attach(existente.ViewObject)
        return existente

    off1 = offset1 if offset1 is not None else App.Placement()
    off2 = offset2 if offset2 is not None else App.Placement()

    # Pre-posicionar link2 haciendo coincidir (link1 * lcs1 * off1) == (link2 * lcs2 * off2)
    # para que el solver nativo converja con la misma orientación de ejes Z (sin flip accidental).
    if plc_pre_alineacion:
        plc_lcs1 = _obtener_lcs_plc(link1.LinkedObject, lcs1)
        plc_lcs2 = _obtener_lcs_plc(link2.LinkedObject, lcs2)
        target_global = link1.Placement * plc_lcs1 * off1
        local_2 = plc_lcs2 * off2
        link2.Placement = target_global * local_2.inverse()

    j = jg.newObject("App::FeaturePython", nombre_junta)
    idx_tipo = JointObject.JointTypes.index(tipo_junta)
    JointObject.Joint(j, idx_tipo)

    if App.GuiUp and getattr(j, "ViewObject", None) is not None:
        vp = JointObject.ViewProviderJoint(j.ViewObject)
        vp.app_obj = j
        vp.attach(j.ViewObject)

    # Configurar conectores apuntando a los LCS (PartDesign::CoordinateSystem)
    j.Reference1 = [link1, [f"{lcs1}.", f"{lcs1}."]]
    j.Reference2 = [link2, [f"{lcs2}.", f"{lcs2}."]]
    j.Offset1 = off1
    j.Offset2 = off2

    if propiedades_extra:
        for k, v in propiedades_extra.items():
            if hasattr(j, k):
                setattr(j, k, v)

    j.Proxy.updateJCSPlacements(j)
    return j


def aplicar_apariencia_piloto(doc, asm):
    """Crea/actualiza la hoja Materiales_Generales y aplica colores y transparencias visuales a cada componente."""
    transp_insp_map = {"Cilindro_09": 75, "Tapa_Exterior_16a": 70}
    mg = doc.getObject("Materiales_Generales")
    if mg is None:
        mg = asm.newObject("Spreadsheet::Sheet", "Materiales_Generales")
        for celda, txt in (
            ("A1", "COMPONENTE"), ("B1", "MATERIAL"), ("C1", "DENSIDAD"),
            ("D1", "COLOR_R"), ("E1", "COLOR_G"), ("F1", "COLOR_B"),
            ("G1", "TRANSP_BASE"), ("H1", "TRANSP_INSP"), ("I1", "PERSONALIZADO")
        ):
            mg.set(celda, txt)

    links = [o for o in asm.Group if o.TypeId == "App::Link" and getattr(o, "LinkedObject", None)]
    for idx, o in enumerate(links, start=2):
        lo = o.LinkedObject
        doc_h = lo.Document
        hm = doc_h.getObject("Materiales")

        nombre_mat = "Estándar"
        dens_val = "0.00000785"
        r_c, g_c, b_c = 0.75, 0.75, 0.75
        tr_base = 0.0
        if hm:
            try:
                nombre_mat = str(hm.get("material_nombre"))
                dens_val = str(hm.get("densidad_mat"))
                r_c = float(hm.get("color_r"))
                g_c = float(hm.get("color_g"))
                b_c = float(hm.get("color_b"))
                tr_base = float(hm.get("transparencia_mat"))
            except Exception:
                pass

        tr_insp = float(transp_insp_map.get(o.Name, 0))

        personalizado = "0"
        try:
            if str(mg.get(f"I{idx}")) == "1":
                personalizado = "1"
                r_c = float(mg.get(f"D{idx}"))
                g_c = float(mg.get(f"E{idx}"))
                b_c = float(mg.get(f"F{idx}"))
                tr_base = float(mg.get(f"G{idx}"))
                tr_insp = float(mg.get(f"H{idx}"))
        except Exception:
            pass

        mg.set(f"A{idx}", o.Name)
        mg.set(f"B{idx}", nombre_mat)
        mg.set(f"C{idx}", f"={dens_val}")
        mg.set(f"D{idx}", f"{r_c:.3f}")
        mg.set(f"E{idx}", f"{g_c:.3f}")
        mg.set(f"F{idx}", f"{b_c:.3f}")
        mg.set(f"G{idx}", f"{tr_base:.1f}")
        mg.set(f"H{idx}", f"{tr_insp:.1f}")
        mg.set(f"I{idx}", personalizado)

        if App.GuiUp:
            tr_efectiva = tr_insp if tr_insp > 0 else tr_base
            vo = getattr(o, "ViewObject", None)
            if vo:
                vo.OverrideMaterial = True
                mat = App.Material()
                mat.DiffuseColor = (r_c, g_c, b_c)
                mat.Transparency = max(0.0, min(1.0, tr_efectiva / 100.0))
                if hasattr(vo, "ShapeAppearance"):
                    vo.ShapeAppearance = (mat,)
                elif hasattr(vo, "ShapeMaterial"):
                    vo.ShapeMaterial = mat


def asegurar_hoja_parametros_generales(doc, asm):
    """Crea o recupera la hoja Parametros_Generales con explosion y modo_diseno_global."""
    pg = doc.getObject("Parametros_Generales")
    if pg is None:
        pg = asm.newObject("Spreadsheet::Sheet", "Parametros_Generales")
        pg.set("A1", "PARÁMETRO"); pg.set("B1", "VALOR"); pg.set("C1", "DESCRIPCIÓN")
        pg.set("A2", "Factor de explosión"); pg.set("B2", "0.0")
        pg.setAlias("B2", "explosion")
        pg.set("C2", "0.0 = Ensamblado | 1.0 = Vista Explotada")

        pg.set("A3", "Modo de diseño global"); pg.set("B3", "3")
        pg.setAlias("B3", "modo_diseno_global")
        pg.set("C3", "1 = Impresión 3D | 2 = CNC/Planos | 3 = Render (sincroniza todas las piezas vinculadas)")
        doc.recompute()
    return pg


def sincronizar_modo_diseno_piezas_piloto(doc, pg):
    try:
        val_raw = pg.get("modo_diseno_global")
        if val_raw is None:
            return
        modo_global = int(float(str(val_raw).strip()))
    except Exception:
        return

    docs_hijos = set()
    for o in getattr(doc, "Objects", []):
        if o.TypeId == "App::Link" and getattr(o, "LinkedObject", None):
            lo = o.LinkedObject
            dh = getattr(lo, "Document", None)
            if dh and dh != doc:
                docs_hijos.add(dh)

    for dh in docs_hijos:
        sp = dh.getObject("Parametros")
        if sp and hasattr(sp, "getAlias") and sp.getAlias("B2") == "modo_diseno":
            try:
                cur = int(float(str(sp.get("B2")).strip()))
            except Exception:
                cur = None
            if cur != modo_global:
                sp.set("B2", str(modo_global))
                dh.recompute()
    doc.recompute()


def main():
    print("FreeCAD", ".".join(App.Version()[:3]))
    nombre_doc = "Piloto_Embolo_Assembly"
    forzar = os.environ.get("FORZAR", "0") == "1"

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)

    # Modo incremental: si existe y no se fuerza, abrir y actualizar sin perder juntas manuales
    if os.path.exists(RUTA_SALIDA) and not forzar:
        doc = next(
            (d for d in App.listDocuments().values() if os.path.abspath(getattr(d, "FileName", "")) == RUTA_SALIDA),
            None,
        )
        if doc is None:
            doc = App.openDocument(RUTA_SALIDA)
        print(f"ACTUALIZACIÓN INCREMENTAL: preservando juntas manuales en {RUTA_SALIDA}")
    else:
        if nombre_doc in App.listDocuments():
            App.closeDocument(nombre_doc)
        doc = App.newDocument(nombre_doc)
        doc.saveAs(RUTA_SALIDA)

    asm = doc.getObject(nombre_doc)
    if asm is None:
        asm = doc.addObject("Assembly::AssemblyObject", nombre_doc)
        asm.Label = nombre_doc

    pg = asegurar_hoja_parametros_generales(doc, asm)
    jg = UtilsAssembly.getJointGroup(asm)

    # =========================================================================
    # 1. BASE: Tapa Interior (Grounded al origen del ensamblaje)
    # =========================================================================
    lnk_tapa_int, _ = asegurar_link(doc, asm, p("Tapa_Interior_16b.FCStd"), "Tapa_Interior_16b")
    asegurar_grounded(jg, lnk_tapa_int, "Grounded_Tapa_Interior")

    # =========================================================================
    # 2. BARRAS GUÍA Y SUFRIDERAS (2x Guia_08 + 2x Sufridera_Guia_05b)
    # =========================================================================
    lnk_guia_1, _ = asegurar_link(doc, asm, p("Guia_08.FCStd"), "Guia_1_08")
    lnk_guia_2, _ = asegurar_link(doc, asm, p("Guia_08.FCStd"), "Guia_2_08")
    asegurar_junta(doc, asm, jg, "Joint_Guia_1", "Fixed", lnk_tapa_int, "LCS_Guia_1", lnk_guia_1, "LCS_Hombro_Asiento")
    asegurar_junta(doc, asm, jg, "Joint_Guia_2", "Fixed", lnk_tapa_int, "LCS_Guia_2", lnk_guia_2, "LCS_Hombro_Asiento")

    lnk_sufr_guia_1, _ = asegurar_link(doc, asm, p("Sufridera_Guia_05b.FCStd"), "Sufridera_Guia_1_05b")
    lnk_sufr_guia_2, _ = asegurar_link(doc, asm, p("Sufridera_Guia_05b.FCStd"), "Sufridera_Guia_2_05b")
    asegurar_junta(doc, asm, jg, "Joint_Sufridera_Guia_1", "Fixed", lnk_tapa_int, "LCS_Guia_1", lnk_sufr_guia_1, "LCS_Cara_Sup")
    asegurar_junta(doc, asm, jg, "Joint_Sufridera_Guia_2", "Fixed", lnk_tapa_int, "LCS_Guia_2", lnk_sufr_guia_2, "LCS_Cara_Sup")

    # =========================================================================
    # 3. TREN MÓVIL DEL ÉMBOLO (Slider + 4 piezas solidarias Fixed)
    # =========================================================================
    lnk_embolo, _ = asegurar_link(doc, asm, p("Embolo_Delrin_10.FCStd"), "Embolo_Delrin_10")
    asegurar_junta(
        doc, asm, jg, "Joint_Corredera_Embolo", "Slider",
        lnk_guia_1, "LCS_Hombro_Asiento",
        lnk_embolo, "LCS_Guia_1",
        offset1=App.Placement(App.Vector(0, 0, 115), App.Rotation()),
        propiedades_extra={
            "EnableLengthMin": True,
            "EnableLengthMax": True,
            "LengthMin": -100.0,
            "LengthMax": 100.0,
        },
    )

    # 3.1 Centro Émbolo 1 y 2 (Plano 11 y 12) unidos rígidamente al émbolo
    lnk_ce1, _ = asegurar_link(doc, asm, p("Centro_Embolo_1_11.FCStd"), "Centro_Embolo_1_11")
    lnk_ce2, _ = asegurar_link(doc, asm, p("Centro_Embolo_2_12.FCStd"), "Centro_Embolo_2_12")
    asegurar_junta(doc, asm, jg, "Joint_Centro_Embolo_1", "Fixed", lnk_embolo, "LCS_Origen", lnk_ce1, "LCS_Asiento_Brida")
    asegurar_junta(doc, asm, jg, "Joint_Centro_Embolo_2", "Fixed", lnk_embolo, "LCS_Cara_Sup", lnk_ce2, "LCS_Origen")

    # 3.2 Targets ferromagnéticos AISI 430 en ambas caras del émbolo
    lnk_target_1, _ = asegurar_link(doc, asm, p("Sensor_Piston_05b.FCStd"), "Sensor_Piston_1_05b")
    lnk_target_2, _ = asegurar_link(doc, asm, p("Sensor_Piston_05b.FCStd"), "Sensor_Piston_2_05b")
    asegurar_junta(
        doc, asm, jg, "Joint_Target_Int", "Fixed",
        lnk_embolo, "LCS_Sensor_1",
        lnk_target_1, "LCS_Asiento_Embolo",
        offset2=App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 180)),
    )
    asegurar_junta(
        doc, asm, jg, "Joint_Target_Ext", "Fixed",
        lnk_embolo, "LCS_Sensor_2",
        lnk_target_2, "LCS_Asiento_Embolo",
    )

    # =========================================================================
    # 4. CAMISA Y TAPA EXTERIOR
    # =========================================================================
    lnk_cilindro, _ = asegurar_link(doc, asm, p("Cilindro_09.FCStd"), "Cilindro_09")
    lnk_tapa_ext, _ = asegurar_link(doc, asm, p("Tapa_Exterior_16a.FCStd"), "Tapa_Exterior_16a")
    asegurar_junta(doc, asm, jg, "Joint_Cilindro", "Fixed", lnk_tapa_int, "LCS_Piso_Tubo_110_5", lnk_cilindro, "LCS_Origen")
    asegurar_junta(
        doc, asm, jg, "Joint_Tapa_Exterior", "Fixed",
        lnk_cilindro, "LCS_Extremo_Sup",
        lnk_tapa_ext, "LCS_Piso_Tubo_110_5",
        offset2=App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 180)),
    )

    # =========================================================================
    # 5. SENSORES INDUCTIVOS COMERCIALES LJ12A3 EN LAS TAPAS
    # =========================================================================
    lnk_sens_int, _ = asegurar_link(doc, asm, p("Sensor_Inductivo_LJ12A3.FCStd"), "Sensor_Inductivo_Int")
    lnk_sens_ext, _ = asegurar_link(doc, asm, p("Sensor_Inductivo_LJ12A3.FCStd"), "Sensor_Inductivo_Ext")
    asegurar_junta(doc, asm, jg, "Joint_Sensor_Inductivo_Int", "Fixed", lnk_tapa_int, "LCS_Puerto_M12x1", lnk_sens_int, "LCS_Origen")
    asegurar_junta(doc, asm, jg, "Joint_Sensor_Inductivo_Ext", "Fixed", lnk_tapa_ext, "LCS_Puerto_M12x1", lnk_sens_ext, "LCS_Origen")

    # =========================================================================
    # 6. HUSILLO Y TREN DE TRANSMISIÓN (Planos 14, 5a, 5b, 4, 3, 2b, 2a)
    # =========================================================================
    lnk_husillo, _ = asegurar_link(doc, asm, p("Tornillo_Sin_Fin_14.FCStd"), "Tornillo_Sin_Fin_14")
    asegurar_junta(
        doc, asm, jg, "Joint_Husillo", "Fixed",
        lnk_tapa_int, "LCS_Acople_Husillo",
        lnk_husillo, "LCS_Origen",
        offset2=App.Placement(App.Vector(0, 0, -5.0), App.Rotation()),
    )

    lnk_sufr_ext, _ = asegurar_link(doc, asm, p("Sufridera_Eje_Ext_05a.FCStd"), "Sufridera_Eje_Ext_05a")
    asegurar_junta(
        doc, asm, jg, "Joint_Sufridera_Eje_Ext", "Fixed",
        lnk_tapa_ext, "LCS_Asiento_Sufridera_Ext",
        lnk_sufr_ext, "LCS_Origen",
        offset2=App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 180)),
    )

    lnk_sufr_int, _ = asegurar_link(doc, asm, p("Sufridera_Int_05b.FCStd"), "Sufridera_Int_05b")
    asegurar_junta(doc, asm, jg, "Joint_Sufridera_Int", "Fixed", lnk_tapa_int, "LCS_Asiento_Sufridera_Int", lnk_sufr_int, "LCS_Origen")

    lnk_tapa_sufr_int, _ = asegurar_link(doc, asm, p("Tapa_Sufridera_Int_05a.FCStd"), "Tapa_Sufridera_Int_05a")
    asegurar_junta(doc, asm, jg, "Joint_Tapa_Sufridera_Int", "Fixed", lnk_tapa_int, "LCS_Origen", lnk_tapa_sufr_int, "LCS_Origen")

    lnk_adap_eje, _ = asegurar_link(doc, asm, p("Adaptador_Eje_04.FCStd"), "Adaptador_Eje_04")
    asegurar_junta(doc, asm, jg, "Joint_Adaptador_Eje", "Fixed", lnk_tapa_int, "LCS_Origen", lnk_adap_eje, "LCS_Cara_Superior")

    lnk_adap_rod, _ = asegurar_link(doc, asm, p("Adaptador_Rodamiento_03.FCStd"), "Adaptador_Rodamiento_03")
    asegurar_junta(
        doc, asm, jg, "Joint_Adaptador_Rodamiento", "Fixed",
        lnk_adap_eje, "LCS_Origen",
        lnk_adap_rod, "LCS_Tope_Superior",
        offset2=App.Placement(App.Vector(0, 0, -16.0), App.Rotation()),
    )

    lnk_transm_2, _ = asegurar_link(doc, asm, p("Transmisor_2_02b.FCStd"), "Transmisor_2_02b")
    asegurar_junta(doc, asm, jg, "Joint_Transmisor_2", "Fixed", lnk_husillo, "LCS_Pasador", lnk_transm_2, "LCS_Pasador_3")

    lnk_transm_1, _ = asegurar_link(doc, asm, p("Transmisor_1_02a.FCStd"), "Transmisor_1_02a")
    asegurar_junta(doc, asm, jg, "Joint_Transmisor_1", "Fixed", lnk_transm_2, "LCS_Asiento_Rodamiento", lnk_transm_1, "LCS_Extremo_Der")

    # =========================================================================
    # 7. ANILLOS TÓRICOS, ESTRUCTURA EXTERIOR Y TENSORES
    # =========================================================================
    lnk_anillo_int, _ = asegurar_link(doc, asm, p("Anillo_Torica_13.FCStd"), "Anillo_Torica_Int_13")
    lnk_anillo_ext, _ = asegurar_link(doc, asm, p("Anillo_Torica_13.FCStd"), "Anillo_Torica_Ext_13")
    asegurar_junta(doc, asm, jg, "Joint_Anillo_Torica_Int", "Fixed", lnk_tapa_int, "LCS_Tope_Resalte", lnk_anillo_int, "LCS_Origen")
    asegurar_junta(doc, asm, jg, "Joint_Anillo_Torica_Ext", "Fixed", lnk_tapa_ext, "LCS_Tope_Resalte", lnk_anillo_ext, "LCS_Origen")

    lnk_estruct_1, _ = asegurar_link(doc, asm, p("Estructura_Interior_07.FCStd"), "Estructura_Interior_1_07")
    lnk_estruct_2, _ = asegurar_link(doc, asm, p("Estructura_Interior_07.FCStd"), "Estructura_Interior_2_07")
    asegurar_junta(doc, asm, jg, "Joint_Estructura_1", "Fixed", lnk_tapa_int, "LCS_Asiento_Carcasa_145mm", lnk_estruct_1, "LCS_Origen")
    asegurar_junta(doc, asm, jg, "Joint_Estructura_2", "Fixed", lnk_tapa_ext, "LCS_Asiento_Carcasa_145mm", lnk_estruct_2, "LCS_Origen")

    lnk_cierre_1, _ = asegurar_link(doc, asm, p("Cierre_Estructura_15.FCStd"), "Cierre_Estructura_1_15")
    lnk_cierre_2, _ = asegurar_link(doc, asm, p("Cierre_Estructura_15.FCStd"), "Cierre_Estructura_2_15")
    asegurar_junta(
        doc, asm, jg, "Joint_Cierre_1", "Fixed",
        lnk_estruct_1, "LCS_Tope_Resalte",
        lnk_cierre_1, "LCS_Origen",
        offset2=App.Placement(App.Vector(0, 0, 0), App.Rotation(45, 0, 0)),
    )
    asegurar_junta(
        doc, asm, jg, "Joint_Cierre_2", "Fixed",
        lnk_estruct_2, "LCS_Tope_Resalte",
        lnk_cierre_2, "LCS_Origen",
        offset2=App.Placement(App.Vector(0, 0, 0), App.Rotation(45, 0, 0)),
    )

    for idx in range(1, 5):
        lnk_tensor, _ = asegurar_link(doc, asm, p("Tensor_06.FCStd"), f"Tensor_{idx}_06")
        asegurar_junta(
            doc, asm, jg, f"Joint_Tensor_{idx}", "Fixed",
            lnk_estruct_1, f"LCS_Tensor_{idx}",
            lnk_tensor, "LCS_Asiento_Estructura_1",
        )

    # =========================================================================
    # 8. ELEMENTOS COMERCIALES NORMALIZADOS (Bujes, O-Ring, Rodamiento, Retén, Pasadores)
    # =========================================================================
    lnk_buje_1, _ = asegurar_link(doc, asm, p("Buje_Guia_12x14x20.FCStd"), "Buje_Guia_1")
    lnk_buje_2, _ = asegurar_link(doc, asm, p("Buje_Guia_12x14x20.FCStd"), "Buje_Guia_2")
    asegurar_junta(doc, asm, jg, "Joint_Buje_Guia_1", "Fixed", lnk_embolo, "LCS_Guia_1", lnk_buje_1, "LCS_Origen")
    asegurar_junta(doc, asm, jg, "Joint_Buje_Guia_2", "Fixed", lnk_embolo, "LCS_Guia_2", lnk_buje_2, "LCS_Origen")

    lnk_oring_emb, _ = asegurar_link(doc, asm, p("ORing_Embolo_97x3_5.FCStd"), "ORing_Embolo")
    asegurar_junta(doc, asm, jg, "Joint_ORing_Embolo", "Fixed", lnk_embolo, "LCS_Ranura_ORing", lnk_oring_emb, "LCS_Origen")

    lnk_rod_6201, _ = asegurar_link(doc, asm, p("Rodamiento_SKF_6201.FCStd"), "Rodamiento_SKF_6201")
    asegurar_junta(doc, asm, jg, "Joint_Rodamiento_6201", "Fixed", lnk_adap_rod, "LCS_Asiento_Rodamiento_6201", lnk_rod_6201, "LCS_Origen")

    lnk_reten, _ = asegurar_link(doc, asm, p("Reten_14x30x7.FCStd"), "Reten_14x30x7")
    asegurar_junta(doc, asm, jg, "Joint_Reten_14x30x7", "Fixed", lnk_sufr_int, "LCS_Asiento_Reten", lnk_reten, "LCS_Origen")

    for idx_pas in (1, 2, 3):
        lnk_pas, _ = asegurar_link(doc, asm, p("Pasador_Cilindrico_4x18.FCStd"), f"Pasador_Transm_{idx_pas}")
        asegurar_junta(
            doc, asm, jg, f"Joint_Pasador_Transm_{idx_pas}", "Fixed",
            lnk_transm_2, f"LCS_Pasador_{idx_pas}",
            lnk_pas, "LCS_Origen",
        )

    # Ocultar los iconos de juntas en 3D para una vista limpia (el usuario puede activarlos en el árbol)
    for o in jg.Group:
        o.Visibility = False

    # Declarar interfaces coaxiales y pares de rosca para _herramientas/verificar_interfaces.py
    interfaces_piloto = {
        "coaxiales": [
            {
                "ref1": "Tapa_Interior_16b:M3_Guia_1_*",
                "ref2": "Sufridera_Guia_1_05b:Agujero_[1-4]",
                "descripcion": "4x M3 Sufridera Guía 1 <-> Tapa Interior",
            },
            {
                "ref1": "Tapa_Interior_16b:M3_Guia_2_*",
                "ref2": "Sufridera_Guia_2_05b:Agujero_[1-4]",
                "descripcion": "4x M3 Sufridera Guía 2 <-> Tapa Interior",
            },
            {
                "ref1": "Tapa_Interior_16b:Puerto_M12x1",
                "ref2": "Embolo_Delrin_10:M8_Sensor_1",
                "descripcion": "Sensor inductivo Tapa Interior (+45°) <-> Target 1 Émbolo (Z=0)",
            },
            {
                "ref1": "Tapa_Exterior_16a:Puerto_M12x1",
                "ref2": "Embolo_Delrin_10:M8_Sensor_2",
                "descripcion": "Sensor inductivo Tapa Exterior (-45°) <-> Target 2 Émbolo (Z=20)",
            },
            {
                "ref1": "Embolo_Delrin_10:M3_Inf_*",
                "ref2": "Centro_Embolo_1_11:Aguj_Brida_*",
                "descripcion": "4x M3 Centro Émbolo 1 <-> Émbolo Delrin",
                "tol_mm": 0.06,
            },
            {
                "ref1": "Centro_Embolo_1_11:M3_Sup_*",
                "ref2": "Centro_Embolo_2_12:Aguj_M3_*",
                "descripcion": "3x M3 Centro Émbolo 1 <-> Centro Émbolo 2",
            },
            {
                "ref1": "Transmisor_1_02a:Agujero_Pasador_1",
                "ref2": "Transmisor_2_02b:Pasador_1",
                "descripcion": "Pasador transversal 1 Transmisor 1 <-> Transmisor 2",
            },
            {
                "ref1": "Transmisor_1_02a:Agujero_Pasador_2",
                "ref2": "Transmisor_2_02b:Pasador_2",
                "descripcion": "Pasador transversal 2 Transmisor 1 <-> Transmisor 2",
            },
            {
                "ref1": "Transmisor_2_02b:Pasador_3",
                "ref2": "Tornillo_Sin_Fin_14:Agujero_Pasador",
                "descripcion": "Pasador transversal 3 Transmisor 2 <-> Tornillo Sin Fin",
            },
            {
                "ref1": "Estructura_Interior_1_07:Rosca_M5_*",
                "ref2": "Cierre_Estructura_1_15:Aguj_Brida_*",
                "descripcion": "4x M5 Estructura Interior 1 <-> Cierre 1",
            },
            {
                "ref1": "Estructura_Interior_2_07:Rosca_M5_*",
                "ref2": "Cierre_Estructura_2_15:Aguj_Brida_*",
                "descripcion": "4x M5 Estructura Interior 2 <-> Cierre 2",
            },
            {
                "ref1": "Tapa_Interior_16b:Puerto_M12x1",
                "ref2": "Sensor_Inductivo_Int:Cuerpo_M12",
                "descripcion": "Puerto M12x1 Tapa Interior <-> Sensor Inductivo Interior",
            },
            {
                "ref1": "Tapa_Exterior_16a:Puerto_M12x1",
                "ref2": "Sensor_Inductivo_Ext:Cuerpo_M12",
                "descripcion": "Puerto M12x1 Tapa Exterior <-> Sensor Inductivo Exterior",
            },
        ],
        "pares_rosca_ajuste": [
            ["Embolo_Delrin_10", "Sensor_Piston_1_05b"],
            ["Embolo_Delrin_10", "Sensor_Piston_2_05b"],
            ["Embolo_Delrin_10", "Buje_Guia_1"],
            ["Embolo_Delrin_10", "Buje_Guia_2"],
            ["Guia_1_08", "Buje_Guia_1"],
            ["Guia_2_08", "Buje_Guia_2"],
            ["Embolo_Delrin_10", "ORing_Embolo"],
            ["Cilindro_09", "ORing_Embolo"],
            ["Adaptador_Rodamiento_03", "Rodamiento_SKF_6201"],
            ["Transmisor_2_02b", "Rodamiento_SKF_6201"],
            ["Tapa_Sufridera_Int_05a", "Rodamiento_SKF_6201"],
            ["Sufridera_Int_05b", "Reten_14x30x7"],
            ["Transmisor_2_02b", "Reten_14x30x7"],
            ["Tapa_Interior_16b", "Reten_14x30x7"],
            ["Transmisor_1_02a", "Pasador_Transm_1"],
            ["Transmisor_1_02a", "Pasador_Transm_2"],
            ["Transmisor_2_02b", "Pasador_Transm_1"],
            ["Transmisor_2_02b", "Pasador_Transm_2"],
            ["Transmisor_2_02b", "Pasador_Transm_3"],
            ["Tornillo_Sin_Fin_14", "Pasador_Transm_3"],
            ["Centro_Embolo_1_11", "Tornillo_Sin_Fin_14"],
            ["Centro_Embolo_2_12", "Tornillo_Sin_Fin_14"],
            ["Tornillo_Sin_Fin_14", "Transmisor_2_02b"],
            ["Tapa_Interior_16b", "Sensor_Inductivo_Int"],
            ["Tapa_Exterior_16a", "Sensor_Inductivo_Ext"],
        ],
        "interferencias_plano": [
            {
                "par": ["Tapa_Interior_16b", "Sufridera_Int_05b"],
                "motivo": "FICHA 16b Secc. 5: rebaje d_reb2=41.00 mm en Plano 16b vs d_ext=45.00 mm en Plano 5b",
            },
            {
                "par": ["Adaptador_Rodamiento_03", "Transmisor_2_02b"],
                "motivo": "FICHA 03/02b: agujero d_paso=13.10 mm en Plano 3 vs collar d_collar=15.00 mm en Plano 2b",
            },
            {
                "par": ["Adaptador_Rodamiento_03", "Transmisor_1_02a"],
                "motivo": "FICHA 03/02a: solape axial del manguito Ø20 mm de Plano 2a con la base de Plano 3",
            },
            {
                "par": ["Cierre_Estructura_1_15", "Tensor_1_06"],
                "motivo": "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)",
            },
            {
                "par": ["Cierre_Estructura_1_15", "Tensor_2_06"],
                "motivo": "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)",
            },
            {
                "par": ["Cierre_Estructura_1_15", "Tensor_3_06"],
                "motivo": "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)",
            },
            {
                "par": ["Cierre_Estructura_1_15", "Tensor_4_06"],
                "motivo": "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)",
            },
            {
                "par": ["Cierre_Estructura_2_15", "Tensor_1_06"],
                "motivo": "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)",
            },
            {
                "par": ["Cierre_Estructura_2_15", "Tensor_2_06"],
                "motivo": "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)",
            },
            {
                "par": ["Cierre_Estructura_2_15", "Tensor_3_06"],
                "motivo": "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)",
            },
            {
                "par": ["Cierre_Estructura_2_15", "Tensor_4_06"],
                "motivo": "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)",
            },
        ],
    }
    if not hasattr(asm, "Interfaces_Declaradas"):
        asm.addProperty(
            "App::PropertyString",
            "Interfaces_Declaradas",
            "Ingenieria",
            "Interfaces coaxiales y pares de rosca esperados",
        )
    asm.Interfaces_Declaradas = json.dumps(interfaces_piloto, ensure_ascii=False)

    doc.recompute()
    res_solver = asm.solve()
    print(f"Estado del solver Assembly (0 = resuelto): {res_solver}")

    aplicar_apariencia_piloto(doc, asm)
    sincronizar_modo_diseno_piezas_piloto(doc, pg)
    doc.recompute()
    doc.saveAs(RUTA_SALIDA)
    print("Guardado exitosamente:", RUTA_SALIDA)


if __name__ in ("__main__", "generar_piloto_embolo_assembly"):
    main()
