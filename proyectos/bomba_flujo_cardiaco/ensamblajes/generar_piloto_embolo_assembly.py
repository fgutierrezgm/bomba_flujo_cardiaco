#!/usr/bin/env python3
"""
Piloto de ensamblaje nativo con el banco Assembly de FreeCAD 1.x (Solver Ondsel).
Subconjunto funcional: Tren del Émbolo, Guías, Camisa, Tapas y Sensores Inductivos.

Características clave:
- Usa `Assembly::AssemblyObject` nativo y juntas reales (`Fixed`, `Slider`, `GroundedJoint`)
  apuntando a los conectores `LCS_*` (`PartDesign::CoordinateSystem`) de cada pieza.
- El émbolo (`Embolo_Delrin_10`) tiene una junta `Slider` (`Joint_Corredera_Embolo`) con
  límites de carrera (`LengthMin = 15 mm`, `LengthMax = 215 mm`), por lo que se puede
  arrastrar con el mouse a lo largo de las guías directamente en la vista 3D de FreeCAD.
- Modo incremental: si `Piloto_Embolo_Assembly.FCStd` ya existe y no se pasa `FORZAR=1`,
  preserva cualquier pieza o junta agregada/editada manualmente en la GUI.

Ejecutar:
  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/ensamblajes/generar_piloto_embolo_assembly.py
"""
import os
import sys
import FreeCAD as App

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "_herramientas"))
from fc_helpers import MATERIALES_BASE

import JointObject
import UtilsAssembly

DIR_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_PIEZAS = os.path.join(DIR_PROYECTO, "piezas")
RUTA_SALIDA = os.path.join(DIR_PROYECTO, "ensamblajes", "Piloto_Embolo_Assembly.FCStd")


def p(nombre_archivo):
    return os.path.join(DIR_PIEZAS, nombre_archivo)


def _obtener_part_hijo(ruta_fcstd):
    ruta_abs = os.path.abspath(ruta_fcstd)
    if not os.path.exists(ruta_abs):
        raise FileNotFoundError(f"No existe la pieza: {ruta_abs}")
    doc_hijo = next(
        (d for d in App.listDocuments().values() if os.path.abspath(d.FileName) == ruta_abs),
        None,
    )
    if doc_hijo is None:
        doc_hijo = App.openDocument(ruta_abs)
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
    # FreeCAD Assembly espera 2 entradas en la lista de subnombres (elemento y vértice)
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
    """Aplica colores de materiales y transparencia de inspección a camisa y tapa exterior."""
    if not App.GuiUp:
        return
    transp_insp = {"Cilindro_09": 70, "Tapa_Exterior_16a": 70}
    for o in asm.Group:
        if o.TypeId != "App::Link" or getattr(o, "LinkedObject", None) is None:
            continue
        part_hijo = o.LinkedObject
        mat_id = getattr(part_hijo, "Material_ID", "")
        info = MATERIALES_BASE.get(mat_id)
        if not info or getattr(o, "ViewObject", None) is None:
            continue
        try:
            o.ViewObject.OverrideMaterial = True
            mat = o.ViewObject.ShapeMaterial
            mat.DiffuseColor = info["color"]
            t_inst = transp_insp.get(o.Name, int(round(info["transparencia"])))
            mat.Transparency = max(0.0, min(1.0, t_inst / 100.0))
            o.ViewObject.ShapeMaterial = mat
        except Exception:
            pass


def main():
    print("FreeCAD", ".".join(App.Version()[:3]))
    nombre_doc = "Piloto_Embolo_Assembly"
    forzar = os.environ.get("FORZAR", "0") == "1"

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)

    # Modo incremental: si existe y no se fuerza, abrir y actualizar sin perder juntas manuales
    if os.path.exists(RUTA_SALIDA) and not forzar:
        doc = next(
            (d for d in App.listDocuments().values() if os.path.abspath(d.FileName) == RUTA_SALIDA),
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

    jg = UtilsAssembly.getJointGroup(asm)

    # 1. Insertar/recuperar componentes (App::Link)
    lnk_tapa_int, _ = asegurar_link(doc, asm, p("Tapa_Interior_16b.FCStd"), "Tapa_Interior_16b")
    lnk_guia_1, _ = asegurar_link(doc, asm, p("Guia_08.FCStd"), "Guia_1_08")
    lnk_guia_2, _ = asegurar_link(doc, asm, p("Guia_08.FCStd"), "Guia_2_08")
    lnk_embolo, _ = asegurar_link(doc, asm, p("Embolo_Delrin_10.FCStd"), "Embolo_Delrin_10")
    lnk_target_1, _ = asegurar_link(doc, asm, p("Sensor_Piston_05b.FCStd"), "Sensor_Piston_1_05b")
    lnk_target_2, _ = asegurar_link(doc, asm, p("Sensor_Piston_05b.FCStd"), "Sensor_Piston_2_05b")
    lnk_cilindro, _ = asegurar_link(doc, asm, p("Cilindro_09.FCStd"), "Cilindro_09")
    lnk_tapa_ext, _ = asegurar_link(doc, asm, p("Tapa_Exterior_16a.FCStd"), "Tapa_Exterior_16a")
    lnk_sens_int, _ = asegurar_link(
        doc, asm, p("Sensor_Inductivo_LJ12A3.FCStd"), "Sensor_Inductivo_Int"
    )
    lnk_sens_ext, _ = asegurar_link(
        doc, asm, p("Sensor_Inductivo_LJ12A3.FCStd"), "Sensor_Inductivo_Ext"
    )

    # 2. Pieza base fija al piso (GroundedJoint)
    asegurar_grounded(jg, lnk_tapa_int, "Grounded_Tapa_Interior")

    # 3. Guías del pistón (Fixed)
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Guia_1",
        "Fixed",
        lnk_tapa_int,
        "LCS_Guia_1",
        lnk_guia_1,
        "LCS_Hombro_Asiento",
    )
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Guia_2",
        "Fixed",
        lnk_tapa_int,
        "LCS_Guia_2",
        lnk_guia_2,
        "LCS_Hombro_Asiento",
    )

    # 4. Émbolo de Delrin con junta corredera (Slider) sobre Guia_1_08
    # Posición inicial a mitad de carrera (Z = 115 mm sobre el hombro de la guía)
    # y límites de carrera entre las dos tapas (15 mm a 215 mm).
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Corredera_Embolo",
        "Slider",
        lnk_guia_1,
        "LCS_Hombro_Asiento",
        lnk_embolo,
        "LCS_Guia_1",
        offset1=App.Placement(App.Vector(0, 0, 115), App.Rotation()),
        propiedades_extra={
            "EnableLengthMin": True,
            "EnableLengthMax": True,
            "LengthMin": 15.0,
            "LengthMax": 215.0,
        },
    )

    # 5. Targets ferromagnéticos AISI 430 en ambas caras del émbolo (Fixed)
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Target_Int",
        "Fixed",
        lnk_embolo,
        "LCS_Sensor_1",
        lnk_target_1,
        "LCS_Asiento_Embolo",
        offset2=App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 180)),
    )
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Target_Ext",
        "Fixed",
        lnk_embolo,
        "LCS_Sensor_2",
        lnk_target_2,
        "LCS_Asiento_Embolo",
    )

    # 6. Camisa acrílica y Tapa Exterior (Fixed)
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Cilindro",
        "Fixed",
        lnk_tapa_int,
        "LCS_Piso_Tubo_110_5",
        lnk_cilindro,
        "LCS_Origen",
    )
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Tapa_Exterior",
        "Fixed",
        lnk_cilindro,
        "LCS_Extremo_Sup",
        lnk_tapa_ext,
        "LCS_Piso_Tubo_110_5",
        offset2=App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 180)),
    )

    # 7. Sensores inductivos M12x1 en las tapas (Fixed)
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Sensor_Inductivo_Int",
        "Fixed",
        lnk_tapa_int,
        "LCS_Puerto_M12x1",
        lnk_sens_int,
        "LCS_Origen",
    )
    asegurar_junta(
        doc,
        asm,
        jg,
        "Joint_Sensor_Inductivo_Ext",
        "Fixed",
        lnk_tapa_ext,
        "LCS_Puerto_M12x1",
        lnk_sens_ext,
        "LCS_Origen",
    )

    # Ocultar los iconos de juntas en 3D para una vista limpia (el usuario puede activarlos en el árbol)
    for o in jg.Group:
        o.Visibility = False

    # Declarar interfaces coaxiales y pares de rosca M8 / M12x1 para _herramientas/verificar_interfaces.py
    import json
    interfaces_piloto = {
        "coaxiales": [
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
            ["Tapa_Interior_16b", "Sensor_Inductivo_Int"],
            ["Tapa_Exterior_16a", "Sensor_Inductivo_Ext"],
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
    doc.recompute()
    doc.saveAs(RUTA_SALIDA)
    print("Guardado:", RUTA_SALIDA)


main()
