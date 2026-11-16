#!/usr/bin/env python3
"""Chequeo previo de STL para impresión FDM (sin laminar).

Valida:
1. Integridad topológica de malla, tamaño contra cama y paredes finas (trimesh).
2. Estabilidad estática (proyección del centro de masa sobre el polígono convexo
   de la cara de apoyo), voladizos reales y comparación contra orientaciones
   alternativas (invertida 180 deg / acostadas 90 deg).
3. Verificación del modo de diseño (Parametros.modo_diseno en el .FCStd fuente).
4. Frescura de la cadena script generador (.py) -> .FCStd -> .stl (y exportador).

Uso:
    python3 Experimental/preflight_stl.py pieza.stl
    python3 Experimental/preflight_stl.py proyectos/bomba_flujo_cardiaco/stl/*.stl --bed 220 220 250
    python3 Experimental/preflight_stl.py pieza.stl --fcstd pieza.FCStd --script generar_pieza.py --json

Código de salida: 0 = sin errores, 1 = hay ERROR (no apto), 2 = no se pudo leer.
Dependencias: trimesh, numpy, scipy, networkx, rtree
"""
import argparse
import glob
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from scipy.spatial import ConvexHull
import trimesh


MODOS_DISENO = {
    1: "Impresión 3D",
    2: "CNC y Planos",
    3: "Render",
}

ROTACIONES_ORT = {
    "actual_0": np.eye(3),
    "invertida_180_x": np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]]),
    "acostada_y_mas": np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]]),
    "acostada_y_menos": np.array([[0.0, 0.0, -1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]),
    "acostada_x_mas": np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]]),
    "acostada_x_menos": np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]]),
}


def cargar(path):
    """Carga un archivo STL binario o ASCII como malla única Trimesh."""
    m = trimesh.load(path, force="mesh", process=True)
    if not isinstance(m, trimesh.Trimesh):
        raise ValueError("El archivo no contiene una malla válida")
    return m


def _formatear_delta(segundos):
    s = int(round(abs(segundos)))
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m {s}s"


def _limpiar_stem_stl(stl_path):
    """Extrae el nombre base de pieza quitando prefijo Xn- y sufijo _ItemNN."""
    base = os.path.splitext(os.path.basename(stl_path))[0]
    base = re.sub(r"^X\d+-", "", base)
    base = re.sub(r"_Item\d+$", "", base)
    return base


def encontrar_fcstd(ruta_stl):
    """Intenta localizar el .FCStd origen a partir de la ruta del .stl."""
    stl_abs = os.path.abspath(ruta_stl)
    dir_stl = os.path.dirname(stl_abs)
    dir_proy = os.path.dirname(dir_stl)
    stem = _limpiar_stem_stl(stl_abs)
    base_raw = os.path.splitext(os.path.basename(stl_abs))[0]

    candidatos = []
    for nombre in dict.fromkeys([stem, base_raw]):
        candidatos.extend([
            os.path.join(dir_stl, f"{nombre}.FCStd"),
            os.path.join(dir_proy, "piezas", f"{nombre}.FCStd"),
            os.path.join(dir_proy, f"{nombre}.FCStd"),
            os.path.join(dir_stl, "..", f"{nombre}.FCStd"),
        ])
    for cand in candidatos:
        norm = os.path.normpath(cand)
        if os.path.isfile(norm):
            return norm
    return None


def _encontrar_scripts_fcstd(ruta_fcstd, ruta_stl=None):
    """Localiza el script generador (.py) de un .FCStd y un posible exportador STL."""
    fc_abs = os.path.abspath(ruta_fcstd)
    dir_fc = os.path.dirname(fc_abs)
    stem = os.path.splitext(os.path.basename(fc_abs))[0]
    stl_name = os.path.basename(ruta_stl) if ruta_stl else None

    py_files = sorted(glob.glob(os.path.join(dir_fc, "*.py")))
    scripts_txt = {}
    for py_path in py_files:
        try:
            with open(py_path, encoding="utf-8", errors="ignore") as f:
                scripts_txt[py_path] = f.read()
        except OSError:
            continue

    # 1) Script dedicado exacto por nombre de archivo: generar_<stem>.py
    esperado_ded = os.path.join(dir_fc, f"generar_{stem.lower()}.py")
    gen_info = None
    for py_path in py_files:
        if os.path.normpath(py_path).lower() == esperado_ded.lower():
            gen_info = (py_path, "dedicado")
            break

    # 2) Script generar_*.py que instancie Pieza("<stem>"...) o guarde <stem>.FCStd
    if gen_info is None:
        pat_pieza = re.compile(rf"""Pieza\s*\(\s*["']{re.escape(stem)}["']|{re.escape(stem)}\.FCStd""")
        for py_path, txt in scripts_txt.items():
            bn = os.path.basename(py_path)
            if bn.startswith("generar_") and pat_pieza.search(txt):
                gen_info = (py_path, "dedicado")
                break

    # 3) Script por lotes (importar_*.py) cuyo catálogo incluya el stem entre comillas
    if gen_info is None:
        pat_lote = re.compile(rf"""["']{re.escape(stem)}(?:\.FCStd)?["']""")
        for py_path, txt in scripts_txt.items():
            bn = os.path.basename(py_path)
            if bn.startswith("importar_") and pat_lote.search(txt):
                gen_info = (py_path, "lote")
                break

    # Exportador STL en el mismo directorio de piezas
    exp_path = None
    for py_path, txt in scripts_txt.items():
        bn = os.path.basename(py_path)
        if "export" in bn.lower() and "stl" in bn.lower():
            if stl_name and stl_name in txt:
                exp_path = py_path
                break
            if f"{stem}.FCStd" in txt:
                exp_path = py_path
                break

    return gen_info, exp_path


def _leer_metadata_fcstd(ruta_fcstd):
    """Lee Parametros (modo_diseno, escala, holgura_fdm) y Manifiesto_Script desde el ZIP FCStd."""
    datos = {
        "fcstd": ruta_fcstd,
        "hoja": None,
        "modo_diseno": None,
        "escala": None,
        "holgura_fdm": None,
        "manifiesto_modo": None,
        "error_lectura": None,
    }
    try:
        with zipfile.ZipFile(ruta_fcstd, "r") as zf:
            if "Document.xml" not in zf.namelist():
                datos["error_lectura"] = "Falta Document.xml dentro del archivo FCStd"
                return datos
            root = ET.fromstring(zf.read("Document.xml").decode("utf-8", errors="replace"))
    except Exception as exc:
        datos["error_lectura"] = str(exc)
        return datos

    celdas_hojas = {}
    for od in root.findall(".//ObjectData/Object"):
        obj_name = od.attrib.get("name", "")
        for prop in od.findall("./Properties/Property"):
            pname = prop.attrib.get("name")
            if pname == "Manifiesto_Script":
                s_el = prop.find("./String")
                if s_el is not None and s_el.attrib.get("value"):
                    try:
                        man = json.loads(s_el.attrib["value"])
                        m_val = man.get("cabecera", {}).get("modo_diseno")
                        if m_val is not None:
                            datos["manifiesto_modo"] = int(float(str(m_val).strip()))
                    except Exception:
                        pass
            elif pname == "cells":
                mapa_alias = {}
                mapa_addr = {}
                for cell in prop.findall(".//Cell"):
                    addr = cell.attrib.get("address", "")
                    alias = cell.attrib.get("alias", "")
                    content = cell.attrib.get("content", "")
                    if addr:
                        mapa_addr[addr] = content
                    if alias:
                        mapa_alias[alias] = content
                celdas_hojas[obj_name] = (mapa_alias, mapa_addr)

    for hoja_cand in ("Parametros", "Parametros_Generales"):
        if hoja_cand in celdas_hojas:
            aliases, addrs = celdas_hojas[hoja_cand]
            datos["hoja"] = hoja_cand
            modo_raw = aliases.get("modo_diseno") or aliases.get("modo_diseno_global")
            if modo_raw is None and "modo" in str(addrs.get("A2", "")).lower():
                modo_raw = addrs.get("B2")
            if modo_raw is not None:
                try:
                    datos["modo_diseno"] = int(float(str(modo_raw).lstrip("'").strip()))
                except ValueError:
                    datos["modo_diseno"] = str(modo_raw)
            if "escala" in aliases:
                datos["escala"] = str(aliases["escala"]).lstrip("'").strip()
            if "holgura_fdm" in aliases:
                datos["holgura_fdm"] = str(aliases["holgura_fdm"]).lstrip("'").strip()
            break

    return datos


def verificar_modo_diseno(ruta_fcstd, modo_esperado=1):
    """Verifica Parametros.modo_diseno == modo_esperado dentro de ruta_fcstd."""
    hallazgos = []
    meta = _leer_metadata_fcstd(ruta_fcstd)
    if meta["error_lectura"]:
        hallazgos.append(dict(
            nivel="ERROR",
            clave="fcstd_ilegible",
            mensaje=f"No se pudo leer metadata de {os.path.basename(ruta_fcstd)}: {meta['error_lectura']}",
        ))
        return hallazgos, meta

    modo_actual = meta["modo_diseno"]
    if meta["hoja"] is None or modo_actual is None:
        hallazgos.append(dict(
            nivel="WARNING",
            clave="sin_modo_diseno",
            mensaje=f"{os.path.basename(ruta_fcstd)} no declara alias 'modo_diseno' en Parametros.",
        ))
        return hallazgos, meta

    if modo_actual != modo_esperado:
        desc_act = MODOS_DISENO.get(modo_actual, "desconocido")
        desc_esp = MODOS_DISENO.get(modo_esperado, "desconocido")
        hallazgos.append(dict(
            nivel="ERROR",
            clave="modo_diseno_incorrecto",
            mensaje=(
                f"{os.path.basename(ruta_fcstd)} está en modo_diseno={modo_actual} ({desc_act}); "
                f"se esperaba modo_diseno={modo_esperado} ({desc_esp})."
            ),
            modo_actual=modo_actual,
            modo_esperado=modo_esperado,
        ))

    if meta["manifiesto_modo"] is not None and meta["manifiesto_modo"] != modo_actual:
        hallazgos.append(dict(
            nivel="WARNING",
            clave="manifiesto_desincronizado",
            mensaje=(
                f"{os.path.basename(ruta_fcstd)}: Manifiesto_Script indica modo {meta['manifiesto_modo']} "
                f"pero Parametros tiene modo {modo_actual} (regenerar desde script si cambió)."
            ),
        ))
    return hallazgos, meta


def verificar_frescura_scripts(ruta_stl, ruta_fcstd, ruta_script=None, strict=False):
    """Compara tiempos de modificación entre script generador, .FCStd, exportador y .stl."""
    hallazgos = []
    info = {
        "stl_mtime": None,
        "fcstd": ruta_fcstd,
        "fcstd_mtime": None,
        "script_generador": None,
        "script_tipo": None,
        "script_mtime": None,
        "exportador": None,
    }
    if not ruta_stl or not os.path.isfile(ruta_stl):
        return hallazgos, info

    stl_mt = os.path.getmtime(ruta_stl)
    info["stl_mtime"] = round(stl_mt, 1)
    tol = 2.0
    nivel_desact = "ERROR" if strict else "WARNING"

    if not ruta_fcstd or not os.path.isfile(ruta_fcstd):
        return hallazgos, info

    fc_mt = os.path.getmtime(ruta_fcstd)
    info["fcstd_mtime"] = round(fc_mt, 1)

    if fc_mt > stl_mt + tol:
        hallazgos.append(dict(
            nivel=nivel_desact,
            clave="stl_desactualizado",
            mensaje=(
                f"{os.path.basename(ruta_fcstd)} es {_formatear_delta(fc_mt - stl_mt)} más reciente "
                f"que el .stl: conviene re-exportar la malla."
            ),
        ))

    gen_info = (os.path.abspath(ruta_script), "manual") if ruta_script else None
    auto_gen, exp_path = _encontrar_scripts_fcstd(ruta_fcstd, ruta_stl)
    if gen_info is None:
        gen_info = auto_gen

    if exp_path and os.path.isfile(exp_path):
        info["exportador"] = os.path.basename(exp_path)
        exp_mt = os.path.getmtime(exp_path)
        if exp_mt > stl_mt + tol:
            hallazgos.append(dict(
                nivel=nivel_desact,
                clave="exportador_desactualizado",
                mensaje=(
                    f"El exportador {os.path.basename(exp_path)} es {_formatear_delta(exp_mt - stl_mt)} "
                    f"más reciente que el .stl."
                ),
            ))

    if gen_info is None:
        hallazgos.append(dict(
            nivel="INFO",
            clave="sin_script_generador",
            mensaje=f"No se identificó script generador en {os.path.dirname(ruta_fcstd)}.",
        ))
        return hallazgos, info

    script_path, script_tipo = gen_info
    info["script_generador"] = os.path.basename(script_path)
    info["script_tipo"] = script_tipo
    if os.path.isfile(script_path):
        sc_mt = os.path.getmtime(script_path)
        info["script_mtime"] = round(sc_mt, 1)
        if sc_mt > fc_mt + tol:
            delta_txt = _formatear_delta(sc_mt - fc_mt)
            if script_tipo == "lote":
                msg = (
                    f"Script por lotes {os.path.basename(script_path)} fue modificado {delta_txt} "
                    f"después que {os.path.basename(ruta_fcstd)} (verificar si el cambio afecta esta pieza)."
                )
            else:
                msg = (
                    f"Script {os.path.basename(script_path)} es {delta_txt} más reciente que "
                    f"{os.path.basename(ruta_fcstd)}: regenerar .FCStd antes de exportar."
                )
            hallazgos.append(dict(
                nivel=nivel_desact,
                clave="fcstd_desactualizado",
                mensaje=msg,
                script=os.path.basename(script_path),
                tipo=script_tipo,
            ))

    return hallazgos, info


def _metricas_hull_apoyo(verts_xy, com_xy):
    """Calcula área de polígono convexo 2D de apoyo y distancia firmada desde el CoM."""
    if len(verts_xy) < 3:
        return 0.0, None
    pts_u = np.unique(np.round(verts_xy, 4), axis=0)
    if len(pts_u) < 3:
        return 0.0, None
    try:
        hull = ConvexHull(pts_u)
    except Exception:
        return 0.0, None
    # En 2D de SciPy, hull.volume es el área; equations (nx, ny, d) <= 0 en el interior
    area_hull = float(hull.volume)
    margen = float(-np.max(hull.equations[:, :-1] @ com_xy + hull.equations[:, -1]))
    return area_hull, margen


def _evaluar_orientacion(verts, faces, normals, centers, areas, com, rot_mat,
                        umbral_vol, ignorar_chaflan_z):
    """Evalúa métricas geométricas de cama, estabilidad CoM y voladizos para una matriz 3x3."""
    rt = rot_mat.T
    v_rot = verts @ rt
    n_rot = normals @ rt
    c_rot = centers @ rt
    com_rot = com @ rt

    b_min = v_rot.min(axis=0)
    b_max = v_rot.max(axis=0)
    ext = b_max - b_min
    z_min = float(b_min[2])

    nz = n_rot[:, 2]
    zc = c_rot[:, 2]
    en_cama = (zc < z_min + 0.05) & (nz < -0.99)
    area_base = float(areas[en_cama].sum())

    if np.any(en_cama):
        base_v_idx = np.unique(faces[en_cama].ravel())
        area_hull, margen_vuelco = _metricas_hull_apoyo(v_rot[base_v_idx, :2], com_rot[:2])
    else:
        area_hull, margen_vuelco = 0.0, None

    z_com = float(com_rot[2] - z_min)
    if margen_vuelco is not None and z_com > 1e-4:
        ang_vuelco = math.degrees(math.atan2(margen_vuelco, z_com))
    elif margen_vuelco is not None:
        ang_vuelco = 90.0 if margen_vuelco >= 0 else -90.0
    else:
        ang_vuelco = None

    # Distingue chaflanes auto-portantes de borde de cama (~45 deg) vs voladizos reales
    candidato_vol = (nz < umbral_vol) & ~en_cama
    chaflan_base = candidato_vol & (zc <= z_min + ignorar_chaflan_z) & (nz >= -0.78)
    vol_real = candidato_vol & ~chaflan_base
    techo_plano = vol_real & (nz < -0.95) & (zc > z_min + 0.30)

    a_chaflan = float(areas[chaflan_base].sum())
    a_vol = float(areas[vol_real].sum())
    a_techo = float(areas[techo_plano].sum())
    z_primero = float(zc[vol_real].min() - z_min) if np.any(vol_real) else None

    base_xy = max(min(float(ext[0]), float(ext[1])), 1e-6)
    esbeltez = float(ext[2]) / base_xy

    return dict(
        z_min=z_min,
        ext=ext,
        area_base=area_base,
        area_hull=area_hull,
        margen_vuelco=margen_vuelco,
        z_com=z_com,
        ang_vuelco=ang_vuelco,
        esbeltez=esbeltez,
        area_chaflan_base=a_chaflan,
        area_voladizo=a_vol,
        area_techo_plano=a_techo,
        z_primer_voladizo=z_primero,
    )


def analizar(m, bed=None, nozzle=0.4, min_perimetros=2, angulo_soporte=45.0,
             muestras=4000, seed=0, ruta_stl=None, ruta_fcstd=None, ruta_script=None,
             modo_esperado=1, sin_fcstd=False, ignorar_chaflan_z=0.6,
             evaluar_alternativas=True, strict_frescura=False):
    hallazgos = []

    def add(nivel, clave, msg, **datos):
        hallazgos.append(dict(nivel=nivel, clave=clave, mensaje=msg, **datos))

    # --- 1. Integridad topológica de malla ------------------------------------
    if not m.is_watertight:
        add("ERROR", "no_estanca", "La malla no es estanca (tiene huecos o aristas abiertas).")
    if not m.is_winding_consistent:
        add("ERROR", "normales", "Orientación de triángulos inconsistente.")
    if m.is_watertight and m.volume < 0:
        add("ERROR", "volumen_negativo", "Volumen negativo: normales invertidas.")
    areas = m.area_faces
    degeneradas = int((areas < 1e-9).sum())
    if degeneradas:
        add("WARNING", "degeneradas", "%d triángulos degenerados (área ~0)." % degeneradas)
    cuerpos = m.split(only_watertight=False)
    if len(cuerpos) > 1:
        add("INFO", "cuerpos", "El archivo tiene %d cuerpos separados." % len(cuerpos))

    # --- 2. Estabilidad estática y voladizos en la cara de apoyo --------------
    umbral = -math.sin(math.radians(angulo_soporte))
    com = m.center_mass if m.is_watertight else m.centroid
    verts = np.asarray(m.vertices)
    faces = np.asarray(m.faces)
    normals = np.asarray(m.face_normals)
    centers = np.asarray(m.triangles_center)

    act = _evaluar_orientacion(
        verts, faces, normals, centers, areas, com, ROTACIONES_ORT["actual_0"],
        umbral, ignorar_chaflan_z,
    )
    ext = act["ext"]

    if bed is not None:
        if any(e > b for e, b in zip(ext, bed)):
            add("ERROR", "no_entra",
                "Mide %.1f x %.1f x %.1f mm y no entra en la cama %s." % (*ext, tuple(bed)))

    if abs(act["z_min"]) > 0.05:
        add("WARNING", "z_no_cero",
            "Z_mín = %.2f mm (el STL no está apoyado exactamente en Z = 0)." % act["z_min"])

    area_total = float(areas.sum()) or 1.0
    a_vol = act["area_voladizo"]
    pct = 100.0 * a_vol / area_total
    if a_vol > 2.0:
        extra_techo = ""
        if act["area_techo_plano"] > 2.0:
            extra_techo = " (incluye %.1f mm2 de techos planos a 90°)" % act["area_techo_plano"]
        z_msg = ""
        if act["z_primer_voladizo"] is not None:
            z_msg = " desde Z=%.1f mm" % act["z_primer_voladizo"]
        add("WARNING", "voladizos",
            "%.1f mm2 (%.1f %% de la superficie) con voladizo > %.0f°%s%s: puede requerir soportes."
            % (a_vol, pct, angulo_soporte, z_msg, extra_techo),
            area_mm2=round(a_vol, 2),
            area_techo_plano_mm2=round(act["area_techo_plano"], 2))

    area_cama = act["area_base"]
    margen_vuelco = act["margen_vuelco"]
    ang_vuelco = act["ang_vuelco"]
    if area_cama < 1.0:
        add("WARNING", "sin_base", "Casi no hay superficie plana apoyada en la cama (%.1f mm2)." % area_cama)
    elif margen_vuelco is not None and margen_vuelco <= 0.0:
        add("ERROR", "vuelco_inminente",
            "Inestable sin soportes: el centro de masa cae %.2f mm fuera de la huella de apoyo (hull %.1f mm2)."
            % (-margen_vuelco, act["area_hull"]))
    elif area_cama < 50.0 or (ang_vuelco is not None and ang_vuelco < 12.0):
        ang_txt = ("%.1f°" % ang_vuelco) if ang_vuelco is not None else "n/d"
        add("WARNING", "base_chica",
            "Base de apoyo reducida (contacto %.1f mm2, hull %.1f mm2, ángulo de vuelco %s): usar brim."
            % (area_cama, act["area_hull"], ang_txt))

    if act["esbeltez"] > 4.0:
        add("WARNING", "esbelta",
            "Pieza esbelta (alto/base = %.1f, Z=%.1f mm): riesgo de vibración o despegue; considerar brim/Z-hop."
            % (act["esbeltez"], float(ext[2])))

    # Comparación automática con orientación invertida (180° X) y acostadas (90°)
    mejor_invertida = None
    mejor_acostada = None
    if evaluar_alternativas:
        inv = _evaluar_orientacion(
            verts, faces, normals, centers, areas, com, ROTACIONES_ORT["invertida_180_x"],
            umbral, ignorar_chaflan_z,
        )
        inv_estable = (inv["margen_vuelco"] is None or inv["margen_vuelco"] > 0.0) and inv["area_base"] >= 1.0
        baja_vol = (act["area_voladizo"] - inv["area_voladizo"]) > max(15.0, 0.30 * act["area_voladizo"])
        elimina_techo90 = (
            (act["area_techo_plano"] - inv["area_techo_plano"]) > 10.0
            and inv["area_base"] >= act["area_base"]
            and inv["area_voladizo"] <= act["area_voladizo"] + 5.0
        )
        mejora_base = (act["area_base"] < 80.0 and inv["area_base"] >= max(2.0 * act["area_base"], 40.0)
                       and inv["area_voladizo"] <= act["area_voladizo"] + 15.0)
        if inv_estable and (baja_vol or elimina_techo90 or mejora_base):
            mejor_invertida = inv
            add("WARNING", "orientacion_invertida_mejor",
                "Invertir 180° en X mejora la cara de apoyo: voladizos %.1f -> %.1f mm2, base %.1f -> %.1f mm2."
                % (act["area_voladizo"], inv["area_voladizo"], act["area_base"], inv["area_base"]),
                voladizo_actual_mm2=round(act["area_voladizo"], 2),
                voladizo_invertida_mm2=round(inv["area_voladizo"], 2),
                base_actual_mm2=round(act["area_base"], 2),
                base_invertida_mm2=round(inv["area_base"], 2))

        necesita_alt_horizontal = (
            act["esbeltez"] > 8.0
            or (ang_vuelco is not None and ang_vuelco < 10.0)
            or (bed is not None and ext[2] > bed[2])
        )
        if necesita_alt_horizontal:
            for nombre_rot in ("acostada_y_mas", "acostada_y_menos", "acostada_x_mas", "acostada_x_menos"):
                cand = _evaluar_orientacion(
                    verts, faces, normals, centers, areas, com, ROTACIONES_ORT[nombre_rot],
                    umbral, ignorar_chaflan_z,
                )
                entra_bed = bed is None or all(ce <= be for ce, be in zip(cand["ext"], bed))
                c_estable = (cand["margen_vuelco"] is None or cand["margen_vuelco"] > 0.0) and cand["esbeltez"] < act["esbeltez"] * 0.5
                if entra_bed and c_estable:
                    if mejor_acostada is None or cand["area_voladizo"] < mejor_acostada[1]["area_voladizo"]:
                        mejor_acostada = (nombre_rot, cand)
            if mejor_acostada is not None:
                r_nom, c_alt = mejor_acostada
                add("INFO", "orientacion_horizontal_alternativa",
                    "Alternativa horizontal (%s): altura baja de %.1f a %.1f mm (esbeltez %.1f -> %.2f; voladizos %.1f mm2)."
                    % (r_nom, float(ext[2]), float(c_alt["ext"][2]), act["esbeltez"], c_alt["esbeltez"], c_alt["area_voladizo"]))

    # --- 3. Paredes finas (trazado de rayos hacia paredes opuestas) -----------
    minimo = nozzle * min_perimetros
    espesor_min_medido = None
    try:
        rng = np.random.default_rng(seed)
        n = min(muestras, len(m.faces))
        total_area = float(areas.sum())
        if total_area > 0.0:
            idx = rng.choice(len(m.faces), size=n, replace=True, p=areas / total_area)
        else:
            idx = rng.choice(len(m.faces), size=n, replace=False)
        nrm = normals[idx]
        orig = centers[idx] - nrm * 1e-3
        loc, ray_idx, tri_hit = m.ray.intersects_location(orig, -nrm, multiple_hits=False)
        if len(ray_idx):
            dist = np.linalg.norm(loc - orig[ray_idx], axis=1)
            # Filtrar impactos en paredes realmente opuestas (evita falsos positivos en crestas de roscas)
            dots = np.einsum("ij,ij->i", nrm[ray_idx], normals[tri_hit])
            opuestas = dots < -0.60
            dist_op = dist[opuestas]
            if len(dist_op):
                espesor_min_medido = round(float(dist_op.min()), 3)
                finas = dist_op < minimo
                frac = float(finas.mean())
                if frac > 0.02:
                    add("WARNING", "paredes_finas",
                        "%.1f %% de las muestras tienen espesor < %.2f mm (%d perímetros x boquilla %.2f). "
                        "Mínimo medido: %.2f mm." % (100 * frac, minimo, min_perimetros, nozzle, float(dist_op.min())),
                        espesor_min_mm=espesor_min_medido)
    except Exception as e:
        add("INFO", "paredes_omitido", "No se pudo medir espesor de paredes (%s)." % e)

    # --- 4. Verificación del modo de diseño y frescura respecto a scripts ------
    meta_cad = None
    info_frescura = None
    if not sin_fcstd:
        fc_resuelto = os.path.abspath(ruta_fcstd) if ruta_fcstd else (encontrar_fcstd(ruta_stl) if ruta_stl else None)
        if fc_resuelto is not None:
            h_modo, meta_cad = verificar_modo_diseno(fc_resuelto, modo_esperado=modo_esperado)
            hallazgos.extend(h_modo)
            h_fresc, info_frescura = verificar_frescura_scripts(
                ruta_stl, fc_resuelto, ruta_script=ruta_script, strict=strict_frescura
            )
            hallazgos.extend(h_fresc)
        elif ruta_stl is not None:
            add("INFO", "sin_fcstd", "No se halló .FCStd asociado (modo_diseno y frescura omitidos).")

    resumen = dict(
        estanca=bool(m.is_watertight),
        triangulos=int(len(m.faces)),
        dimensiones_mm=[round(float(x), 2) for x in ext],
        volumen_mm3=round(float(m.volume), 1) if m.is_watertight else None,
        area_voladizo_mm2=round(a_vol, 2),
        area_techo_plano_mm2=round(act["area_techo_plano"], 2),
        area_chaflan_base_mm2=round(act["area_chaflan_base"], 2),
        area_base_mm2=round(area_cama, 2),
        area_hull_base_mm2=round(act["area_hull"], 2),
        margen_vuelco_mm=round(margen_vuelco, 2) if margen_vuelco is not None else None,
        angulo_vuelco_deg=round(ang_vuelco, 1) if ang_vuelco is not None else None,
        esbeltez=round(act["esbeltez"], 2),
        espesor_min_mm=espesor_min_medido,
        cad=meta_cad,
        frescura=info_frescura,
    )
    return dict(resumen=resumen, hallazgos=hallazgos)


def _imprimir_humano(ruta_stl, r):
    s = r["resumen"]
    cad = s.get("cad") or {}
    fresc = s.get("frescura") or {}
    modo_str = f"modo={cad['modo_diseno']}" if cad.get("modo_diseno") is not None else "modo=n/d"
    script_str = fresc.get("script_generador") or "n/d"
    ang_str = f"{s['angulo_vuelco_deg']}°" if s.get("angulo_vuelco_deg") is not None else "n/d"
    print(f"== {ruta_stl} ==")
    print(
        f"Estanca: {s['estanca']} | {s['triangulos']} triángulos | {s['dimensiones_mm']} mm | "
        f"vol {s['volumen_mm3']} mm3"
    )
    print(
        f"Apoyo: {s['area_base_mm2']} mm2 (hull {s['area_hull_base_mm2']} mm2, "
        f"θ_vuelco={ang_str}, esbeltez={s['esbeltez']}) | {modo_str} | script={script_str}"
    )
    for h in r["hallazgos"]:
        print(f"[{h['nivel']}] {h['mensaje']}")
    if not r["hallazgos"]:
        print("Sin hallazgos.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stl", nargs="+", help="Uno o varios archivos .stl")
    ap.add_argument("--bed", nargs=3, type=float, metavar=("X", "Y", "Z"))
    ap.add_argument("--nozzle", type=float, default=0.4)
    ap.add_argument("--min-perimetros", type=int, default=2)
    ap.add_argument("--angulo-soporte", type=float, default=45.0)
    ap.add_argument("--ignorar-chaflan-z", type=float, default=0.6)
    ap.add_argument("--fcstd", help="Ruta explícita al .FCStd fuente (para 1 STL)")
    ap.add_argument("--script", help="Ruta explícita al script generador .py (para 1 STL)")
    ap.add_argument("--modo-esperado", type=int, default=1, help="modo_diseno esperado en Parametros (defecto: 1)")
    ap.add_argument("--sin-fcstd", action="store_true", help="Omitir verificación de .FCStd y frescura")
    ap.add_argument("--no-rotaciones", action="store_true", help="No evaluar orientaciones alternativas")
    ap.add_argument("--strict-frescura", action="store_true", help="Escalar desactualización script/.FCStd a ERROR")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if len(a.stl) > 1 and (a.fcstd or a.script):
        print("ERROR: --fcstd y --script solo aplican cuando se pasa un único STL.", file=sys.stderr)
        return 2

    resultados = []
    hubo_error = False
    for ruta_stl in a.stl:
        try:
            m = cargar(ruta_stl)
        except Exception as e:
            print("No se pudo leer %s: %s" % (ruta_stl, e), file=sys.stderr)
            return 2

        r = analizar(
            m,
            bed=a.bed,
            nozzle=a.nozzle,
            min_perimetros=a.min_perimetros,
            angulo_soporte=a.angulo_soporte,
            ruta_stl=ruta_stl,
            ruta_fcstd=a.fcstd,
            ruta_script=a.script,
            modo_esperado=a.modo_esperado,
            sin_fcstd=a.sin_fcstd,
            ignorar_chaflan_z=a.ignorar_chaflan_z,
            evaluar_alternativas=not a.no_rotaciones,
            strict_frescura=a.strict_frescura,
        )
        resultados.append((ruta_stl, r))
        if any(h["nivel"] == "ERROR" for h in r["hallazgos"]):
            hubo_error = True

    if a.json:
        if len(resultados) == 1:
            print(json.dumps(resultados[0][1], indent=2, ensure_ascii=False))
        else:
            payload = {
                "archivos": [{"archivo": p, **r} for p, r in resultados],
                "total_archivos": len(resultados),
                "con_error": sum(1 for _, r in resultados if any(h["nivel"] == "ERROR" for h in r["hallazgos"])),
                "con_warning": sum(1 for _, r in resultados if any(h["nivel"] == "WARNING" for h in r["hallazgos"])),
            }
            print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for i, (ruta_stl, r) in enumerate(resultados):
            if i:
                print()
            _imprimir_humano(ruta_stl, r)

    return 1 if hubo_error else 0


if __name__ == "__main__":
    sys.exit(main())
