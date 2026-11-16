#!/usr/bin/env python3
"""
Generador de video de armado (1920x1080 @ 30 fps, H.264) de la Bomba de Flujo Cardíaco
Prototipo Impresión 3D (Escala 0,755 — 48 piezas de Piloto_Impresion_3D_Assembly.FCStd).

Estructura:
  - Intro: Vista general y explosión agrupada por subconjuntos.
  - Acto I (Subconjuntos en banco):
      1) Subconjunto Tapa Interior (#3) en corte longitudinal Y=0 temporal:
         #6 x4 + tornillería M2, #4/#25 (labio -Z)/#5 + M2, #15 + SKF 609 #24 (-Z),
         #17 a 45° + #15 a 22,5°/112,5°, #13 (-Z->+Z) + O-Ring #28 y presentación de #31.
      2) Subconjunto Émbolo Móvil (#7, #27, #8, #9, 2x #10 + tornillería M2,5).
      3) Subconjunto Base Exterior (#1, #16, #26, #18, #19, #20 + tornillería).
      4) Subconjunto Cabezal Motor (#19, #20, #12, 2x #29, #23 + bulonería).
      5) Subconjunto 4x Tensores Partidos (#21 + #22 encastre triangular 30 mm).
  - Acto II (Ensamblaje Final):
      Integración física paso a paso con Tornillo Sin Fin #14 + Pasador #30,
      inserción de 2x Guías #11 y apriete de 2x Tuercas #31, O-Ring #26 + Anillo #18,
      Cilindro Vidrio translúcido #2, Base Exterior, Cabezal Motor (#12+2x#29 -> #19/#20 -> #23)
      y 4x Tensores con tuercas M4.
  - Acto III (Funcionamiento):
      Cinemática sincronizada (tren rotativo girando acorde al paso 3,0 mm del sinfín
      y émbolo subiendo/bajando dentro de la camisa transparente) + órbita 360°.

Uso:
  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/ensamblajes/generar_video_ensamblaje_3d.py
  VIDEO_STORYBOARD_DIR=/ruta /snap/bin/freecad.cmd ...   (solo keyframes para revisión visual)
"""

import math
import os
import subprocess
import sys
import numpy as np

import FreeCAD as App
import Part
import vtk
from vtk.util import numpy_support
from PIL import Image, ImageDraw, ImageFont


DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_ASM = os.path.join(DIR_ACTUAL, "Piloto_Impresion_3D_Assembly.FCStd")
RUTA_MP4_DEFAULT = os.path.join(DIR_ACTUAL, "Video_Ensamblaje_Bomba_3D.mp4")

ANCHO = 1920
ALTO = 1080
FPS = int(os.environ.get("VIDEO_FPS", "30"))


# =============================================================================
# UTILIDADES MATEMÁTICAS Y CURVAS SUAVES
# =============================================================================
def smootherstep(t):
    u = max(0.0, min(1.0, float(t)))
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)


def smoothstep(t):
    u = max(0.0, min(1.0, float(t)))
    return u * u * (3.0 - 2.0 * u)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_vec(v1, v2, t):
    return (
        v1[0] + (v2[0] - v1[0]) * t,
        v1[1] + (v2[1] - v1[1]) * t,
        v1[2] + (v2[2] - v1[2]) * t,
    )


def cam_pos_orbita(focal, dist, az_deg, el_deg):
    az = math.radians(az_deg)
    el = math.radians(el_deg)
    c_el = math.cos(el)
    return (
        focal[0] + dist * c_el * math.sin(az),
        focal[1] - dist * c_el * math.cos(az),
        focal[2] + dist * math.sin(el),
    )


# =============================================================================
# PALETA DE MATERIALES Y CONVERSIÓN BREP -> VTK POLYDATA
# =============================================================================
def _propiedades_pieza(nombre):
    """Devuelve (rgb, opacity, specular, spec_power, diffuse, feature_edges)."""
    if nombre == "Cilindro_09_3D":
        return (0.68, 0.90, 0.88), 0.25, 0.85, 85.0, 0.65, False
    if nombre in ("Tapa_Interior_16b_3D", "Tapa_Exterior_16a_3D"):
        return (0.19, 0.44, 0.75), 1.0, 0.28, 38.0, 0.78, True
    if nombre in ("Estructura_Interior_1_07_3D", "Estructura_Interior_2_07_3D", "Tapa_Motor_01_3D"):
        return (0.28, 0.42, 0.58), 1.0, 0.25, 35.0, 0.78, True
    if nombre in ("Cierre_Estructura_1_15_3D", "Cierre_Estructura_2_15_3D"):
        return (0.15, 0.54, 0.62), 1.0, 0.28, 38.0, 0.78, True
    if nombre == "Adaptador_Eje_04_3D":
        return (0.82, 0.37, 0.18), 1.0, 0.30, 40.0, 0.78, True
    if nombre == "Adaptador_Rodamiento_03_3D":
        return (0.35, 0.39, 0.78), 1.0, 0.30, 40.0, 0.78, True
    if nombre in (
        "Sufridera_Int_05b_3D",
        "Sufridera_Eje_Ext_05a_3D",
        "Sufridera_Guia_1A_3D",
        "Sufridera_Guia_1B_3D",
        "Sufridera_Guia_2A_3D",
        "Sufridera_Guia_2B_3D",
        "Arandela_Guia_1_08_3D",
        "Arandela_Guia_2_08_3D",
    ):
        return (0.90, 0.59, 0.15), 1.0, 0.32, 42.0, 0.78, True
    if nombre == "Tapa_Sufridera_Int_05a_3D":
        return (0.95, 0.73, 0.26), 1.0, 0.32, 42.0, 0.78, True
    if nombre in ("Tuerca_Guia_1_08_3D", "Tuerca_Guia_2_08_3D", "Centro_Embolo_1_11_3D"):
        return (0.15, 0.62, 0.48), 1.0, 0.28, 38.0, 0.78, True
    if nombre == "Centro_Embolo_2_12_3D":
        return (0.24, 0.73, 0.56), 1.0, 0.28, 38.0, 0.78, True
    if nombre in ("Anillo_Torica_Int_13_3D", "Anillo_Torica_Ext_13_3D"):
        return (0.76, 0.47, 0.24), 1.0, 0.28, 38.0, 0.78, True
    if nombre == "Embolo_Delrin_10_3D":
        return (0.91, 0.90, 0.86), 1.0, 0.36, 48.0, 0.80, True
    if nombre in (
        "ORing_Camisa_Int", "ORing_Camisa_Ext", "ORing_Embolo_3D",
        "ORing_Eje_11_2x1_8", "ORing_Guia_1", "ORing_Guia_2", "Reten_10x22x7",
    ):
        return (0.10, 0.11, 0.13), 1.0, 0.45, 50.0, 0.72, False
    if nombre == "Tornillo_Sin_Fin_14_3D":
        return (0.26, 0.39, 0.64), 1.0, 0.35, 45.0, 0.78, True
    if nombre.endswith("_Parte_1"):
        return (0.24, 0.47, 0.72), 1.0, 0.30, 40.0, 0.78, True
    if nombre.endswith("_Parte_2"):
        return (0.16, 0.36, 0.52), 1.0, 0.30, 40.0, 0.78, True
    if nombre in ("Guia_1_08_3D", "Guia_2_08_3D", "Transmisor_A_02a_3D", "Transmisor_B_02b_3D",
                  "Sensor_Piston_1_3D", "Sensor_Piston_2_3D"):
        return (0.83, 0.85, 0.89), 1.0, 0.72, 90.0, 0.68, False
    if nombre in ("Rodamiento_SKF_609", "Pasador_3x14_1", "Pasador_3x14_2", "Pasador_3x10_3"):
        return (0.60, 0.63, 0.68), 1.0, 0.72, 85.0, 0.68, True
    return (0.45, 0.55, 0.68), 1.0, 0.30, 40.0, 0.78, True


def _shape_to_polydata(sh, defl=0.06):
    verts, tris = sh.tessellate(defl)
    if not verts or not tris:
        return None
    pts = vtk.vtkPoints()
    arr_pts = np.array([[v.x, v.y, v.z] for v in verts], dtype=np.float32)
    pts.SetData(numpy_support.numpy_to_vtk(arr_pts, deep=1))
    t_arr = np.array(tris, dtype=np.int64)
    c_np = np.hstack([np.full((len(t_arr), 1), 3, dtype=np.int64), t_arr]).ravel()
    cells = vtk.vtkCellArray()
    cells.SetCells(len(t_arr), numpy_support.numpy_to_vtkIdTypeArray(c_np, deep=1))
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetPolys(cells)

    norm = vtk.vtkPolyDataNormals()
    norm.SetInputData(pd)
    norm.ComputePointNormalsOn()
    norm.SplittingOn()
    norm.SetFeatureAngle(34.0)
    norm.ConsistencyOn()
    norm.Update()
    return norm.GetOutput()


def _crear_actor_pd(pd, rgb, opacity=1.0, spec=0.35, spec_pwr=45.0, diffuse=0.78, with_edges=True):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(pd)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    pr = actor.GetProperty()
    pr.SetColor(*rgb)
    pr.SetOpacity(opacity)
    pr.SetSpecular(spec)
    pr.SetSpecularPower(spec_pwr)
    pr.SetDiffuse(diffuse)
    pr.SetAmbient(0.19)

    edge_actor = None
    if with_edges:
        fe = vtk.vtkFeatureEdges()
        fe.SetInputData(pd)
        fe.FeatureEdgesOn()
        fe.BoundaryEdgesOff()
        fe.NonManifoldEdgesOff()
        fe.ManifoldEdgesOff()
        fe.SetFeatureAngle(33.0)
        fe.Update()
        if fe.GetOutput().GetNumberOfCells() > 0:
            em = vtk.vtkPolyDataMapper()
            em.SetInputData(fe.GetOutput())
            edge_actor = vtk.vtkActor()
            edge_actor.SetMapper(em)
            epr = edge_actor.GetProperty()
            epr.SetColor(0.10, 0.14, 0.20)
            epr.SetOpacity(0.28 * opacity)
            epr.SetLineWidth(1.0)
    return actor, edge_actor


def _set_xform(actor_pair, dxyz=(0.0, 0.0, 0.0), spin_z=0.0, pivot=(0.0, 0.0, 0.0)):
    tf = vtk.vtkTransform()
    tf.PostMultiply()
    if abs(spin_z) > 1e-4:
        tf.Translate(-pivot[0], -pivot[1], -pivot[2])
        tf.RotateZ(spin_z)
        tf.Translate(pivot[0], pivot[1], pivot[2])
    if abs(dxyz[0]) > 1e-5 or abs(dxyz[1]) > 1e-5 or abs(dxyz[2]) > 1e-5:
        tf.Translate(dxyz[0], dxyz[1], dxyz[2])
    for ac in actor_pair:
        if ac is not None:
            ac.SetUserTransform(tf)


def _set_vis(actor_pair, vis, opacity=None):
    for idx, ac in enumerate(actor_pair):
        if ac is not None:
            ac.SetVisibility(1 if vis else 0)
            if opacity is not None:
                ac.GetProperty().SetOpacity(opacity if idx == 0 else 0.28 * opacity)


# =============================================================================
# HUD GRÁFICO DE ALTA LEGIBILIDAD (PIL RGBA SOBRE RENDER VTK)
# =============================================================================
def _cargar_fuentes():
    def _try(rutas, sz):
        for r in rutas:
            if os.path.exists(r):
                return ImageFont.truetype(r, sz)
        return ImageFont.load_default()

    bold_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    reg_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    mono_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    return {
        "title": _try(bold_paths, 26),
        "act": _try(bold_paths, 19),
        "step_h": _try(bold_paths, 27),
        "sub": _try(bold_paths, 19),
        "body": _try(reg_paths, 20),
        "body_b": _try(bold_paths, 20),
        "chip": _try(bold_paths, 17),
        "small": _try(reg_paths, 16),
        "mono": _try(mono_paths, 17),
        "hero": _try(bold_paths, 44),
        "hero_sub": _try(reg_paths, 24),
    }


def _wrap_text(draw, text, font, max_w):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        cand = (cur + " " + w).strip() if cur else w
        if draw.textlength(cand, font=font) <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _dibujar_diagrama_desfase(draw, x0, y0, size):
    """Mini diagrama esquemático mostrando X=±28,31 (#31), #17 a 45° y #15 a 22,5°."""
    cx = x0 + size // 2
    cy = y0 + size // 2
    r_outer = int(size * 0.42)
    r_pcd = int(size * 0.25)

    draw.rounded_rectangle([x0, y0, x0 + size, y0 + size], radius=10, fill=(244, 247, 251, 245), outline=(195, 206, 220, 255), width=2)
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], outline=(50, 95, 165, 210), width=2)
    draw.ellipse([cx - r_pcd, cy - r_pcd, cx + r_pcd, cy + r_pcd], outline=(130, 145, 165, 180), width=1)
    # Ejes X/Y
    draw.line([cx - r_outer - 6, cy, cx + r_outer + 6, cy], fill=(160, 172, 188, 190), width=1)
    draw.line([cx, cy - r_outer - 6, cx, cy + r_outer + 6], fill=(160, 172, 188, 190), width=1)

    # Tornillos #17 -> #3 a 45° (naranja)
    for ang in (45, 135, 225, 315):
        px = cx + int(r_pcd * math.cos(math.radians(ang)))
        py = cy - int(r_pcd * math.sin(math.radians(ang)))
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(210, 92, 42, 255), outline=(255, 255, 255, 255), width=1)

    # Tornillos #15 -> #17 a 22,5°/112,5°/202,5°/292,5° (índigo)
    for ang in (22.5, 112.5, 202.5, 292.5):
        px = cx + int(r_pcd * math.cos(math.radians(ang)))
        py = cy - int(r_pcd * math.sin(math.radians(ang)))
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(80, 88, 195, 255), outline=(255, 255, 255, 255), width=1)

    # Guías / Tuercas #31 a X=±28,31 (verde)
    rx = int(r_outer * 0.66)
    for sgn in (-1, 1):
        gx = cx + sgn * rx
        draw.ellipse([gx - 6, cy - 6, gx + 6, cy + 6], fill=(35, 155, 118, 255), outline=(255, 255, 255, 255), width=1)


def componer_hud(img_np, fonts, info, progress, act_index):
    """Compone el overlay técnico profesional sobre un array RGB (H, W, 3) numpy."""
    base = Image.fromarray(img_np).convert("RGBA")
    ov = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ov)

    # 1. Barra superior fija
    draw.rectangle([0, 0, ANCHO, 74], fill=(18, 36, 62, 240))
    draw.rectangle([0, 74, ANCHO, 77], fill=(214, 110, 40, 255))
    draw.text((34, 14), "BOMBA DE FLUJO CARDÍACO — MODELO IMPRESIÓN 3D (ESC. 0,755)", font=fonts["title"], fill=(255, 255, 255, 255))
    draw.text((34, 46), "Guía visual de armado de subconjuntos y ensamblaje final · 45 ítems BOM (129 piezas) · Legajo IRAM", font=fonts["small"], fill=(190, 208, 232, 255))

    act_txt = info.get("act_badge", "ACTO")
    tw = draw.textlength(act_txt, font=fonts["act"])
    bx0 = ANCHO - int(tw) - 68
    draw.rounded_rectangle([bx0, 17, ANCHO - 30, 56], radius=18, fill=(214, 110, 40, 255))
    draw.text((bx0 + 19, 24), act_txt, font=fonts["act"], fill=(255, 255, 255, 255))

    # 2. Modo Portada / Hero o Tarjeta Lateral Izquierda
    if info.get("hero_center"):
        max_tw = max(
            draw.textlength(info["title"], font=fonts["hero"]),
            draw.textlength(info["desc"], font=fonts["hero_sub"]),
            draw.textlength(info.get("note", ""), font=fonts["body"]) if info.get("note") else 0,
        )
        cw, ch = max(980, int(max_tw) + 76), 170
        x0 = (ANCHO - cw) // 2
        y0 = ALTO - 235
        draw.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=16, fill=(18, 36, 62, 224), outline=(214, 110, 40, 255), width=3)
        draw.text((x0 + 36, y0 + 22), info["title"], font=fonts["hero"], fill=(255, 255, 255, 255))
        draw.text((x0 + 38, y0 + 82), info["desc"], font=fonts["hero_sub"], fill=(218, 228, 242, 255))
        if info.get("note"):
            draw.text((x0 + 38, y0 + 122), info["note"], font=fonts["body"], fill=(255, 198, 120, 255))
    else:
        px0, py0, pw = 32, 102, 532
        # Calcular altura dinámica exacta de tarjeta según líneas reales
        title_lines = _wrap_text(draw, info["title"], fonts["step_h"], pw - 48)
        desc_lines = _wrap_text(draw, info["desc"], fonts["body"], pw - 48)
        note_lines = _wrap_text(draw, info.get("note", ""), fonts["body_b"], pw - 64) if info.get("note") else []
        chips = info.get("chips", [])
        show_diag = info.get("show_pcd_diag", False)

        h_calc = (
            20 + 30 + len(title_lines) * 33 + 6 + 16
            + len(desc_lines) * 27
            + (8 + len(note_lines) * 25 + 20 + 10 if note_lines else 0)
            + (6 + len(chips) * 33 if chips else 0)
            + (154 if show_diag else 0)
            + 26
        )
        ph = min(ALTO - 178, max(300, h_calc))

        draw.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], radius=14, fill=(255, 255, 255, 234), outline=(186, 200, 218, 255), width=2)
        # Banda de acento lateral
        accent = info.get("accent", (29, 78, 137))
        draw.rounded_rectangle([px0, py0, px0 + 10, py0 + ph], radius=4, fill=(*accent, 255))

        cy = py0 + 20
        # Subtítulo / número de paso
        draw.text((px0 + 26, cy), info["step_label"], font=fonts["sub"], fill=(*accent, 255))
        cy += 30
        for tl in title_lines:
            draw.text((px0 + 26, cy), tl, font=fonts["step_h"], fill=(16, 28, 46, 255))
            cy += 33
        cy += 6
        draw.line([px0 + 26, cy, px0 + pw - 22, cy], fill=(214, 222, 232, 255), width=2)
        cy += 16

        for dl in desc_lines:
            draw.text((px0 + 26, cy), dl, font=fonts["body"], fill=(38, 52, 72, 255))
            cy += 27

        if note_lines:
            cy += 8
            nh = len(note_lines) * 25 + 20
            is_warn = info.get("warn", False)
            nfill = (254, 240, 236, 255) if is_warn else (238, 245, 253, 255)
            nedge = (196, 56, 42, 255) if is_warn else (46, 108, 180, 255)
            ntext = (152, 32, 24, 255) if is_warn else (24, 68, 124, 255)
            draw.rounded_rectangle([px0 + 24, cy, px0 + pw - 20, cy + nh], radius=8, fill=nfill, outline=nedge, width=2)
            ny = cy + 10
            for nl in note_lines:
                draw.text((px0 + 36, ny), nl, font=fonts["body_b"], fill=ntext)
                ny += 25
            cy += nh + 10

        if chips:
            cy += 6
            for item_id, label, col_rgb in chips:
                draw.rounded_rectangle([px0 + 26, cy, px0 + pw - 22, cy + 28], radius=6, fill=(242, 246, 250, 255), outline=(212, 220, 230, 255), width=1)
                draw.ellipse([px0 + 34, cy + 7, px0 + 48, cy + 21], fill=(int(col_rgb[0] * 255), int(col_rgb[1] * 255), int(col_rgb[2] * 255), 255), outline=(40, 50, 65, 200), width=1)
                txt_chip = f"[{item_id}]  {label}"
                draw.text((px0 + 58, cy + 4), txt_chip, font=fonts["chip"], fill=(24, 38, 58, 255))
                cy += 33

        if show_diag and (cy + 140 <= py0 + ph - 10):
            cy += 8
            _dibujar_diagrama_desfase(draw, px0 + 26, cy, 130)
            lx = px0 + 174
            draw.text((lx, cy + 10), "DESFASE DE BRIDAS:", font=fonts["chip"], fill=(20, 35, 58, 255))
            draw.text((lx, cy + 36), "• #17→#3: 4× a 45° (Ø37,8)", font=fonts["small"], fill=(195, 76, 28, 255))
            draw.text((lx, cy + 60), "• #15→#17: 4× a 22,5° (Ø37,0)", font=fonts["small"], fill=(68, 76, 178, 255))
            draw.text((lx, cy + 84), "• Guías #31: X=±28,31", font=fonts["small"], fill=(22, 132, 98, 255))
            draw.text((lx, cy + 108), "  en escotaduras Ø15,6.", font=fonts["small"], fill=(22, 132, 98, 255))

        # Sello inferior de tornillería si corresponde
        if info.get("bolt_badge"):
            bx, by = px0 + pw + 22, 96
            btw = int(draw.textlength(info["bolt_badge"], font=fonts["mono"])) + 36
            draw.rounded_rectangle([bx, by, bx + btw, by + 36], radius=18, fill=(28, 42, 62, 228), outline=(240, 172, 68, 255), width=2)
            draw.text((bx + 18, by + 8), info["bolt_badge"], font=fonts["mono"], fill=(255, 224, 150, 255))

    # 3. Barra de línea de tiempo inferior (barra continua + 8 pestañas equidistantes)
    by0 = ALTO - 58
    draw.rectangle([0, by0, ANCHO, ALTO], fill=(20, 34, 56, 240))
    etapas = [
        "INTRO",
        "1 · TAPA INT.",
        "2 · ÉMBOLO",
        "3 · BASE EXT.",
        "4 · CABEZAL",
        "5 · TENSORES",
        "ENS. FINAL",
        "PRUEBA 3D",
    ]
    bar_x0, bar_x1 = 34, ANCHO - 34
    bar_w = bar_x1 - bar_x0
    draw.rounded_rectangle([bar_x0, by0 + 7, bar_x1, by0 + 13], radius=3, fill=(58, 76, 102, 255))
    fill_x = bar_x0 + int(bar_w * max(0.0, min(1.0, progress)))
    draw.rounded_rectangle([bar_x0, by0 + 7, max(bar_x0 + 8, fill_x), by0 + 13], radius=3, fill=(214, 110, 40, 255))
    draw.ellipse([fill_x - 5, by0 + 5, fill_x + 5, by0 + 15], fill=(255, 224, 150, 255))

    n_et = len(etapas)
    gap = 8
    tab_w = (bar_w - (n_et - 1) * gap) / float(n_et)
    for i, et in enumerate(etapas):
        tx0 = int(round(bar_x0 + i * (tab_w + gap)))
        tx1 = int(round(tx0 + tab_w))
        ty0, ty1 = by0 + 20, by0 + 50
        active = i == act_index
        passed = i < act_index
        if active:
            tfill, tedge, tcol = (214, 110, 40, 255), (255, 210, 140, 255), (255, 255, 255, 255)
        elif passed:
            tfill, tedge, tcol = (38, 66, 104, 245), (96, 142, 198, 220), (222, 234, 248, 255)
        else:
            tfill, tedge, tcol = (26, 44, 70, 220), (66, 88, 118, 180), (144, 162, 186, 255)
        draw.rounded_rectangle([tx0, ty0, tx1, ty1], radius=7, fill=tfill, outline=tedge, width=1)
        tf = fonts["mono"] if active else fonts["small"]
        tw = draw.textlength(et, font=tf)
        draw.text((tx0 + (tx1 - tx0 - tw) / 2.0, ty0 + 6), et, font=tf, fill=tcol)

    out_rgba = Image.alpha_composite(base, ov)
    return np.asarray(out_rgba.convert("RGB"), dtype=np.uint8)


# =============================================================================
# CONSTRUCTOR PRINCIPAL DE ESCENA, PIEZAS Y TORNILLERÍA
# =============================================================================
def construir_escena():
    doc = App.openDocument(RUTA_ASM)
    asm = next(o for o in doc.Objects if o.TypeId == "Assembly::AssemblyObject")

    # Renderer offscreen VTK con Depth Peeling para vidrio transparente
    rw = vtk.vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetSize(ANCHO, ALTO)
    rw.SetAlphaBitPlanes(1)
    rw.SetMultiSamples(0)

    ren = vtk.vtkRenderer()
    ren.SetUseDepthPeeling(1)
    ren.SetMaximumNumberOfPeels(8)
    ren.SetOcclusionRatio(0.02)
    ren.SetBackground(0.95, 0.96, 0.985)
    ren.SetBackground2(0.84, 0.88, 0.94)
    ren.GradientBackgroundOn()
    rw.AddRenderer(ren)

    for pos, intensity, col in (
        ((320.0, -360.0, 280.0), 0.95, (1.0, 0.99, 0.97)),
        ((-320.0, -190.0, 120.0), 0.48, (0.86, 0.92, 1.0)),
        ((40.0, 320.0, 180.0), 0.42, (1.0, 1.0, 1.0)),
        ((0.0, -180.0, -340.0), 0.25, (0.92, 0.95, 1.0)),
    ):
        lt = vtk.vtkLight()
        lt.SetPosition(*pos)
        lt.SetFocalPoint(0.0, 0.0, -40.0)
        lt.SetIntensity(intensity)
        lt.SetColor(*col)
        ren.AddLight(lt)

    actores = {}
    colores_base = {}
    opacidades_base = {}
    corte_mitades = {}  # nombre -> {"back": actor_pair (Y>=0), "front": actor_pair (Y<0)}

    box_y_pos = Part.makeBox(420.0, 210.0, 420.0, App.Vector(-210.0, 0.0, -210.0))
    box_y_neg = Part.makeBox(420.0, 210.0, 420.0, App.Vector(-210.0, -210.0, -210.0))
    piezas_con_corte = {
        "Tapa_Interior_16b_3D",
        "Adaptador_Rodamiento_03_3D",
        "Adaptador_Eje_04_3D",
        "Sufridera_Int_05b_3D",
        "Tapa_Sufridera_Int_05a_3D",
        "Reten_10x22x7",
        "Rodamiento_SKF_609",
    }

    def _shape_link(lnk):
        if hasattr(lnk, "Shape") and not lnk.Shape.isNull() and lnk.Shape.Solids:
            sh = lnk.Shape.copy()
            sh.Placement = lnk.Placement
            return sh
        lo = lnk.LinkedObject
        sols_p = [
            g for g in getattr(lo, "Group", [])
            if g.isDerivedFrom("Part::Feature")
            and not g.isDerivedFrom("Part::Datum")
            and not g.Shape.isNull()
            and g.Shape.Solids
        ]
        finales = [o for o in sols_p if not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
        elegido = finales[-1] if finales else max(sols_p, key=lambda o: o.Shape.Volume)
        sh = elegido.Shape.copy()
        sh.Placement = lnk.Placement
        return sh

    print("Teselando las instancias BRep de Piloto_Impresion_3D_Assembly.FCStd...")
    _prefijos_tornilleria_asm = (
        "Tornillo_Hex_",
        "Tornillo_Allen_",
        "Tornillo_M",
        "Tornillo_Avell_",
        "Esparrago_",
        "Tuerca_Hex_",
        "Arandela_M",
    )
    bolt_links = []
    for lnk in asm.Group:
        if lnk.TypeId != "App::Link" or not lnk.LinkedObject:
            continue
        nm = lnk.Name
        if nm.startswith(_prefijos_tornilleria_asm):
            bolt_links.append(lnk)
            continue
        sh = _shape_link(lnk)
        rgb, op, spec, pwr, diff, edges = _propiedades_pieza(nm)
        colores_base[nm] = rgb
        opacidades_base[nm] = op
        defl = 0.04 if sh.BoundBox.DiagonalLength < 80.0 else 0.065

        pd_full = _shape_to_polydata(sh, defl=defl)
        ap_full = _crear_actor_pd(pd_full, rgb, op, spec, pwr, diff, with_edges=edges)
        for ac in ap_full:
            if ac is not None:
                ren.AddActor(ac)
        _set_vis(ap_full, False)
        actores[nm] = ap_full

        if nm in piezas_con_corte:
            pd_b = _shape_to_polydata(sh.common(box_y_pos), defl=defl)
            pd_f = _shape_to_polydata(sh.common(box_y_neg), defl=defl)
            ap_b = _crear_actor_pd(pd_b, rgb, 1.0, spec, pwr, diff, with_edges=True)
            ap_f = _crear_actor_pd(pd_f, rgb, 1.0, spec, pwr, diff, with_edges=True)
            for ac in (*ap_b, *ap_f):
                if ac is not None:
                    ren.AddActor(ac)
            _set_vis(ap_b, False)
            _set_vis(ap_f, False)
            corte_mitades[nm] = {"back": ap_b, "front": ap_f}

    # --- Tornillería, arandelas y tuercas reales desde Piloto_Impresion_3D_Assembly.FCStd ---
    steel_bolt = (0.38, 0.42, 0.48)
    washer_nut_steel = (0.64, 0.68, 0.74)
    _reglas_grupos_tornilleria = (
        ("Tornillo_M2x5_SufGuia", "suf_guia_inf"),
        ("Tornillo_M2x14_AdEje_", "ad_eje_45"),
        ("Tornillo_M2x8_AdRod_", "ad_rod_0"),
        ("Tornillo_M2_5x8_CE1_", "ce1_embolo"),
        ("Tornillo_M2_5x8_CE2_", "ce2_centro"),
        ("Tornillo_M2_5x6_SufExt_", "suf_ext"),
        ("Tornillo_Avell_M2x6_AnilloExt_", "anillo_ext"),
        ("Tornillo_Avell_M2x6_AnilloInt_", "anillo_int"),
        ("Arandela_M4_Cierre_Inf_", "cierre_inf_ar"),
        ("Tornillo_Allen_M4x35_Inf_", "cierre_inf_tor"),
        ("Arandela_M4_Cierre_Sup_", "cierre_sup_ar"),
        ("Tornillo_Allen_M4x35_Sup_", "cierre_sup_tor"),
        ("Tornillo_Allen_M4x12_Motor_", "motor_tor"),
        ("Arandela_M4_Motor_", "motor_ar"),
        ("Tuerca_Hex_M4_Motor_", "motor_tuerca"),
        ("Arandela_M8_Sup_", "tensor_sup_ar"),
        ("Tornillo_Hex_M8x16_Sup_", "tensor_sup_tor"),
        ("Arandela_M8_Inf_", "tensor_inf_ar"),
        ("Tornillo_Hex_M8x16_Inf_", "tensor_inf_tor"),
    )
    bolt_groups = {gname: [] for _, gname in _reglas_grupos_tornilleria}
    pd_bolt_cache = {}
    for lnk in sorted(bolt_links, key=lambda o: o.Name):
        nm = lnk.Name
        gname = next((gn for pref, gn in _reglas_grupos_tornilleria if nm.startswith(pref)), None)
        if gname is None:
            raise ValueError(f"Elemento de fijación sin grupo asignado en el ensamblaje: {nm}")
        sh = _shape_link(lnk)
        bb = sh.BoundBox
        cx, cy, cz = bb.Center.x, bb.Center.y, bb.Center.z
        base = lnk.Placement.Base
        rot_q = tuple(round(float(v), 5) for v in lnk.Placement.Rotation.Q)
        off_loc = (round(cx - base.x, 4), round(cy - base.y, 4), round(cz - base.z, 4))
        cache_key = (lnk.LinkedObject.Name, rot_q, off_loc)
        pd_hw = pd_bolt_cache.get(cache_key)
        if pd_hw is None:
            sh_local = sh.copy()
            sh_local.translate(App.Vector(-cx, -cy, -cz))
            pd_hw = _shape_to_polydata(sh_local, defl=0.03)
            pd_bolt_cache[cache_key] = pd_hw
        es_arand_tuerca = nm.startswith(("Arandela_", "Tuerca_"))
        col = washer_nut_steel if es_arand_tuerca else steel_bolt
        spec = 0.78 if es_arand_tuerca else 0.72
        pwr = 90.0 if es_arand_tuerca else 85.0
        diff = 0.70 if es_arand_tuerca else 0.68
        ap = _crear_actor_pd(pd_hw, col, 1.0, spec, pwr, diff, with_edges=True)
        for ac in ap:
            if ac is not None:
                ren.AddActor(ac)
        _set_vis(ap, False)
        _set_xform(ap, dxyz=(cx, cy, cz))
        bolt_groups[gname].append((ap, (cx, cy, cz)))

    n_hw = sum(len(v) for v in bolt_groups.values())
    print(f"Escena lista: {len(actores)} piezas + {n_hw} elementos de fijación reales en {len(bolt_groups)} grupos.")
    return doc, rw, ren, actores, corte_mitades, bolt_groups, colores_base, opacidades_base


# =============================================================================
# MOTOR DE GUION Y ANIMACIÓN
# =============================================================================
def _build_timeline():
    """Define todos los planos/beats secuenciales con su duración en segundos."""
    beats = []

    def add(key, act_idx, act_badge, step_label, title, desc, dur, cam_from, cam_to,
            wc=(-0.27, 0.02), hero=False, note="", warn=False, chips=None, bolt_badge="", pcd=False, accent=(29, 78, 137)):
        beats.append({
            "key": key,
            "act_idx": act_idx,
            "act_badge": act_badge,
            "step_label": step_label,
            "title": title,
            "desc": desc,
            "dur": float(dur),
            "n_frames": max(2, int(round(dur * FPS))),
            "cam_from": cam_from,  # (focal, dist, az, el)
            "cam_to": cam_to,
            "wc": wc,
            "hero_center": hero,
            "note": note,
            "warn": warn,
            "chips": chips or [],
            "bolt_badge": bolt_badge,
            "show_pcd_diag": pcd,
            "accent": accent,
        })

    # --- INTRO (5.5 s) ---
    add("intro_hold", 0, "PRESENTACIÓN", "MODELO COMPLETO",
        "Bomba de Flujo Cardíaco (129 Instancias)",
        "Secuencia de pre-armado en 5 subconjuntos de banco e integración con tornillería real del ensamblaje.",
        2.5, ((0, 0, -50), 960, 28, 20), ((0, 0, -50), 960, 52, 20), wc=(0.0, -0.15), hero=True,
        note="Prototipo Impresión 3D (Esc. 0,755) — Vidrio transparente para vista interna")
    add("intro_explode", 0, "PRESENTACIÓN", "ARQUITECTURA MODULAR",
        "División en 5 Subconjuntos",
        "1) Tapa Interior (#3) · 2) Émbolo · 3) Base Exterior · 4) Cabezal Motor · 5) Tensores.",
        3.0, ((0, 0, -50), 960, 52, 20), ((0, 0, -28), 1340, 62, 22), wc=(0.0, -0.15), hero=True)

    # --- ACTO I: SUBCONJUNTO 1 (TAPA INTERIOR #3) — 20.6 s ---
    add("s1_cut_open", 1, "ACTO I · SUBCONJUNTO 1", "SUBCONJUNTO 1 — PASO 1/6",
        "Tapa Interior (#3) en Corte Y=0",
        "Activamos corte longitudinal temporal en #3 para visualizar los bolsillos internos de guías y sellos.",
        2.4, ((0, 0, 14), 270, 14, 18), ((0, 0, 14), 235, 10, 20),
        chips=[("3", "Tapa Interior Intermedia (PLA+)", (0.19, 0.44, 0.75))],
        note="Bolsillo central inferior Ø34,05 mm (escalón Ø30,20 arriba) + bolsillos Ø15,50 mm.")

    add("s1_guia_suf", 1, "ACTO I · SUBCONJUNTO 1", "SUBCONJUNTO 1 — PASO 2/6",
        "O-Rings, Sufrideras (#6), Arandelas y Tuercas (#31)",
        "Alojar 2× O-Ring 6,0×1,5 y 2× #6 (inf.) desde -Z con 8× M2×5; arriba (+Z) asentar Arandelas y Tuercas #31.",
        3.8, ((0, 0, 14), 235, 10, 20), ((0, 0, 18), 245, 18, 22),
        chips=[("6", "2× O-Ring 6×1,5 + #6 (-Z) + Arand.", (0.90, 0.59, 0.15)),
               ("31", "2× Tuerca Guía (ajuste horario +Z)", (0.15, 0.62, 0.48))],
        bolt_badge="8× TORN. ALLEN M2×5 (4 por sufridera inf. · X=±28,31)",
        note="Los 2 pequeños O-Rings 6,0×1,5 sellan cada barra guía entre el bolsillo de #3 y #6.", warn=True, accent=(180, 95, 24))

    add("s1_sello_reten", 1, "ACTO I · SUBCONJUNTO 1", "SUBCONJUNTO 1 — PASO 3/6",
        "Sello Central (#4, #25, #5) desde -Z",
        "Desde ABAJO (-Z) insertar en corte Sufridera Int. #4, Retén 10×22×7 #25 y cerrar con Tapa #5.",
        3.8, ((0, 0, 14), 245, 18, 22), ((0, 0, -12), 255, 8, -12),
        chips=[("4", "Sufridera Interior (desde -Z)", (0.90, 0.59, 0.15)),
               ("25", "Retén 10×22×7 (labio hacia -Z)", (0.10, 0.11, 0.13)),
               ("5", "Tapa Sufridera Int. (cierre -Z)", (0.95, 0.73, 0.26))],
        note="CRÍTICO: #4/#25/#5 entran desde -Z respetando el corte para ver su asiento.", warn=True, accent=(188, 48, 38))

    add("s1_ad_eje_17", 1, "ACTO I · SUBCONJUNTO 1", "SUBCONJUNTO 1 — PASO 4/6",
        "Adaptador del Eje (#17) y 4× Allen M2×14",
        "Asentar #17 derecho (+Z arriba) sobre #3 y fijar desde arriba con 4× Tornillos Allen M2×14 a 45°.",
        3.6, ((0, 0, 24), 235, 14, 26), ((0, 0, 28), 245, 20, 24),
        chips=[("17", "Adaptador Eje (+Z arriba, cajeado Ø4,1)", (0.82, 0.37, 0.18))],
        bolt_badge="4× TORN. ALLEN M2×14 a 45° · PCD Ø37,76 mm (cabeza embutida)",
        note="Las cabezas Allen M2×14 quedan embutidas 1 mm bajo la cara sup. de #17 sin tocar a #15.",
        pcd=True, accent=(185, 76, 30))

    add("s1_rodam_15", 1, "ACTO I · SUBCONJUNTO 1", "SUBCONJUNTO 1 — PASO 5/6",
        "Adaptador (#15) y Rulemán SKF 609 (#24)",
        "Prensar el rodamiento SKF 609 (#24) desde ABAJO (-Z) en #15, bajar sobre #17 y fijar con 4× M2×8 a 22,5°.",
        3.4, ((0, 0, 30), 250, 18, 22), ((0, 0, 30), 260, 16, 26),
        chips=[("15", "Adaptador Rodamiento (4× M2×8)", (0.35, 0.39, 0.78)),
               ("24", "Rodamiento SKF 609-2Z (en corte)", (0.60, 0.63, 0.68))],
        bolt_badge="4× TORN. ALLEN M2×8 a 22,5° · PCD Ø37,00 mm (en ciegos de #17)",
        note="NO forzar #24 por arriba: #15 tiene agujero sup. Ø15,60 de tope axial.", warn=True)

    add("s1_eje_oring", 1, "ACTO I · SUBCONJUNTO 1", "SUBCONJUNTO 1 — PASO 6/6",
        "Eje Transmisor B (#13), O-Ring #28 y Cierre",
        "Pasar #13 desde -Z hacia +Z, calzar O-Ring #28 (11,2×1,8) arriba del SKF 609 y cerrar sólido.",
        3.8, ((0, 0, 24), 265, 16, 26), ((0, 0, 22), 285, 65, 22),
        chips=[("13", "Eje Transmisor B (Inox.)", (0.83, 0.85, 0.89)),
               ("28", "O-Ring 11,2×1,8 (cuello Ø9,82)", (0.10, 0.11, 0.13))],
        note="O-Ring #28 apoya en el cuello arriba de #24. Queda listo Subconjunto 1 sin guías.")

    # --- ACTO I: SUBCONJUNTO 2 (ÉMBOLO MÓVIL) — 7.2 s ---
    add("s2_embolo_base", 2, "ACTO I · SUBCONJUNTO 2", "SUBCONJUNTO 2 — PASO 1/2",
        "Émbolo Delrin (#7) y O-Ring (#27)",
        "Calzar O-Ring dinámico 69×3,55 (#27) en la ranura periférica del Émbolo #7 (Delrin POM-C).",
        3.2, ((0, 0, -68), 220, 22, 24), ((0, 0, -68), 220, 48, 22),
        chips=[("7", "Émbolo Principal (Delrin POM-C)", (0.91, 0.90, 0.86)),
               ("27", "O-Ring 69×3,55 mm", (0.10, 0.11, 0.13))],
        accent=(22, 132, 98))

    add("s2_embolo_comp", 2, "ACTO I · SUBCONJUNTO 2", "SUBCONJUNTO 2 — PASO 2/2",
        "Centros (#8, #9) y 2× Sensores (#10)",
        "Fijar Centro #8 (-Z, 4× M2,5) y #9 (+Z, 3× M2,5); insertar 2× Sensor AISI 430 (#10) coaxiales a +45°.",
        4.0, ((0, 0, -70), 275, 18, -14), ((0, 0, -70), 255, 58, 22),
        chips=[("8", "Centro de Émbolo 1 (-Z)", (0.15, 0.62, 0.48)),
               ("9", "Centro de Émbolo 2 (+Z)", (0.24, 0.73, 0.56)),
               ("10", "2× Sensor Magnético (AISI 430)", (0.83, 0.85, 0.89))],
        bolt_badge="4× M2,5 (-Z, #8) + 3× M2,5 (+Z, #9) + 2× Sensor (+45°)",
        note="Sensores #10 enfrentados en taladro pasante +45°; guías #11 pasan por agujeros Ø8,3.", accent=(22, 132, 98))

    # --- ACTO I: SUBCONJUNTO 3 (BASE EXTERIOR) — 6.8 s ---
    add("s3_base_caps", 3, "ACTO I · SUBCONJUNTO 3", "SUBCONJUNTO 3 — PASO 1/2",
        "Tapa Exterior (#1), Sufridera (#16) y Sellos",
        "Desde ARRIBA (+Z) fijar Sufridera Ext. #16 (4× M2,5×6), asentar O-Ring #26 y Anillo Tórico #18 (4× Avell. M2×6).",
        3.5, ((0, 0, -172), 365, 24, 24), ((0, 0, -172), 375, 48, 22),
        chips=[("1", "Tapa Exterior 16a", (0.19, 0.44, 0.75)),
               ("16", "Sufridera Eje Ext. (+Z)", (0.90, 0.59, 0.15)),
               ("26", "O-Ring 75×3,55 mm (+Z)", (0.10, 0.11, 0.13)),
               ("18", "Anillo Prensa Tórica (+Z)", (0.76, 0.47, 0.24))],
        bolt_badge="4× ALLEN M2,5×6 (#16, +Z) + 4× AVELL. M2×6 (#18, +Z)")

    add("s3_base_est", 3, "ACTO I · SUBCONJUNTO 3", "SUBCONJUNTO 3 — PASO 2/2",
        "Estructura Inf. (#19) y Cierre (#20)",
        "Acoplar Estructura Int. 2 (#19) y Cierre 2 (#20) en cara inferior (-Z) de #1 con 4× M4×35 + Arandelas.",
        3.3, ((0, 0, -206), 445, 42, -14), ((0, 0, -202), 445, 95, 18),
        chips=[("19", "Estructura Interior 2", (0.28, 0.42, 0.58)),
               ("20", "Cierre Estructura 2", (0.15, 0.54, 0.62))],
        bolt_badge="4× TORN. ALLEN M4×35 + 4× ARANDELA M4 (#20+#19 → #1)")

    # --- ACTO I: SUBCONJUNTO 4 (CABEZAL MOTOR Y EJE SUP.) — 6.4 s ---
    add("s4_cabezal_cage", 4, "ACTO I · SUBCONJUNTO 4", "SUBCONJUNTO 4 — PASO 1/2",
        "Jaula Superior (#19 + #20) y Tapa Motor (#23)",
        "Unir Estructura Sup. (#19) y Cierre (#20) con 4× M4×35 + Arandelas M4; fijar Brida Motor #23 (4× M4×12 + Tuercas).",
        3.6, ((0, 0, 74), 435, 25, 22), ((0, 0, 74), 435, 65, 24),
        chips=[("19", "Estructura Interior 1 (Sup.)", (0.28, 0.42, 0.58)),
               ("20", "Cierre Estructura 1 (Sup.)", (0.15, 0.54, 0.62)),
               ("23", "Tapa Motor Superior", (0.28, 0.42, 0.58))],
        bolt_badge="4× M4×35 + ARAND. (#20+#19) · 4× M4×12 + ARAND. + TUERCA (#23)")

    add("s4_trans_a", 4, "ACTO I · SUBCONJUNTO 4", "SUBCONJUNTO 4 — PASO 2/2",
        "Eje Transmisor A (#12) y Pasadores (#29)",
        "Presentar Transmisor A (#12) con los 2× Pasadores Ø3×14 (#29) listos para bloqueo sobre #13.",
        3.2, ((0, 0, 72), 340, 65, 24), ((0, 0, 72), 345, 120, 20),
        chips=[("12", "Eje Transmisor A Motor", (0.83, 0.85, 0.89)),
               ("29", "2× Pasador Elástico Ø3×14", (0.60, 0.63, 0.68))],
        note="Los pasadores #29 se clavan radialmente tras calzar #12 sobre el vástago de #13.")

    # --- ACTO I: SUBCONJUNTO 5 (4× TENSORES PARTIDOS) — 4.8 s ---
    add("s5_tensores", 5, "ACTO I · SUBCONJUNTO 5", "SUBCONJUNTO 5 — PASO ÚNICO",
        "4× Tensores Partidos (#21 + #22)",
        "Ensamblar axialmente las espigas triangulares de 30 mm entre Tensor Parte 1 (#21) y Parte 2 (#22).",
        4.8, ((0, 0, -55), 860, 28, 18), ((0, 0, -55), 900, 62, 22),
        chips=[("21", "4× Tensor Sup. Parte 1 (espiga 30 mm)", (0.24, 0.47, 0.72)),
               ("22", "4× Tensor Inf. Parte 2 (cavidad 30 mm)", (0.16, 0.36, 0.52))],
        note="Empalme autocentrante por encastre triangular antes del tensado final.")

    # --- ACTO II: ENSAMBLAJE FINAL DE LA BOMBA — 28.8 s ---
    add("f1_sub1_base", 6, "ACTO II · ENSAMBLAJE FINAL", "ENSAMBLAJE FINAL — PASO 1/7",
        "Partida: Subconjunto 1 (Tapa Interior #3)",
        "Colocamos en posición el Subconjunto 1 armado en banco (con #13 montado y sin guías).",
        2.5, ((0, 0, 12), 300, 35, 20), ((0, 0, -55), 620, 35, 18),
        chips=[("S1", "Subconjunto Tapa Interior (#3..#31)", (0.19, 0.44, 0.75))],
        accent=(180, 75, 25))

    add("f2_embolo_husillo", 6, "ACTO II · ENSAMBLAJE FINAL", "ENSAMBLAJE FINAL — PASO 2/7",
        "Sinfín (#14), Émbolo (-Z) y Acople (#30)",
        "Presentar Sinfín #14, subir Émbolo S2 desde -Z sin girar mientras #14 gira para enroscarlo, y acoplar #14 en #13 con #30.",
        6.8, ((0, 0, -118), 700, 38, 18), ((0, 0, -72), 575, 22, 14),
        chips=[("14", "Tornillo Sin Fin (GIRA para enroscar S2)", (0.26, 0.39, 0.64)),
               ("S2", "Sub. Émbolo sube desde -Z (SIN GIRAR)", (0.15, 0.62, 0.48)),
               ("30", "Pasador Elástico Ø3×10 (fija #14 a #13)", (0.60, 0.63, 0.68))],
        note="Antes de fijar #14 en #13: S2 entra por espiga Ø8,80 (-Z) y sube sin girar mientras #14 gira para enroscarlo.", warn=True, accent=(180, 75, 25))

    add("f3_guias_tuercas", 6, "ACTO II · ENSAMBLAJE FINAL", "ENSAMBLAJE FINAL — PASO 3/7",
        "Inserción de Guías (#11) y Apriete (#31)",
        "Pasar las 2× Guías #11 desde -Z por Émbolo y #6 x4 hasta su tope; roscar y ajustar Tuercas #31.",
        4.2, ((0, 0, -65), 650, 18, 12), ((0, 0, -65), 680, 40, 22),
        chips=[("11", "2× Eje Guía Ø8,22 (tope en #6 inf.)", (0.83, 0.85, 0.89)),
               ("31", "2× Tuerca Guía (roscadas en +Z)", (0.15, 0.62, 0.48))],
        note="Sentido de #11: extremo roscado p=1,25 hacia +Z (#31); extremo liso hacia -Z.", warn=True, accent=(180, 75, 25))

    add("f4_camisa_vidrio", 6, "ACTO II · ENSAMBLAJE FINAL", "ENSAMBLAJE FINAL — PASO 4/7",
        "O-Ring (#26), Anillo (#18) y Camisa (#2)",
        "Asentar O-Ring 75×3,55 #26 y Anillo Tórico #18 en -Z de #3 (4× Avell. M2×6) y deslizar Cilindro #2.",
        4.0, ((0, 0, -82), 815, 40, 22), ((0, 0, -82), 815, 32, 16),
        chips=[("26", "O-Ring 75×3,55 (#3 lado -Z)", (0.10, 0.11, 0.13)),
               ("18", "Anillo Prensa Tórica (4× Avell. M2×6)", (0.76, 0.47, 0.24)),
               ("2", "Cilindro Camisa Vidrio (translúcido)", (0.68, 0.90, 0.88))],
        bolt_badge="4× TORN. AVELL. M2×6 (#18 → cara -Z de #3)", accent=(180, 75, 25))

    add("f5_base_exterior", 6, "ACTO II · ENSAMBLAJE FINAL", "ENSAMBLAJE FINAL — PASO 5/7",
        "Cierre Inferior con Subconjunto 3",
        "Subir Subconjunto Base Exterior (#1+#16+#26+#18+#19+#20) encastrando #2 en #26 y #14 en #16.",
        3.8, ((0, 0, -90), 820, 32, 16), ((0, 0, -82), 840, 45, 18),
        chips=[("S3", "Subconjunto Base Exterior (#1..#20)", (0.19, 0.44, 0.75))],
        note="Comprobar entrada suave de la espiga inferior de #14 dentro de Sufridera #16.", accent=(180, 75, 25))

    add("f6_cabezal_motor", 6, "ACTO II · ENSAMBLAJE FINAL", "ENSAMBLAJE FINAL — PASO 6/7",
        "Acoplamiento Cabezal Motor (Sub. 4)",
        "Calzar #12 sobre #13 con 2× Pasadores #29; bajar jaula #19+#20 (4× M4×35 + Arand.) y Tapa #23.",
        4.6, ((0, 0, -32), 840, 45, 22), ((0, 0, -50), 890, 36, 20),
        chips=[("12", "Transmisor A + 2× Pasadores #29", (0.83, 0.85, 0.89)),
               ("19", "Jaula #19+#20 (4× M4×35 + Arand. → #3)", (0.28, 0.42, 0.58)),
               ("23", "Tapa Motor Sup. + 4× M4×12 + Tuercas", (0.28, 0.42, 0.58))],
        bolt_badge="4× M4×35 + ARAND. (#20+#19→#3) · 4× M4×12 + ARAND. + TUERCA (#23)", accent=(180, 75, 25))

    add("f7_tensores_cierre", 6, "ACTO II · ENSAMBLAJE FINAL", "ENSAMBLAJE FINAL — PASO 7/7",
        "4× Tensores (#21+#22) y Apriete Final",
        "Insertar los 4× subconjuntos tensores por las esquinas y apretar bulones Hex M8×16 + Arandelas M8 arriba y abajo.",
        4.4, ((0, 0, -50), 870, 36, 20), ((0, 0, -50), 890, 65, 22),
        chips=[("S5", "4× Tensores (#21+#22) ensamblados", (0.24, 0.47, 0.72))],
        bolt_badge="4× HEX. M8×16 + ARAND. M8 (+Z) · 4× HEX. M8×16 + ARAND. M8 (-Z)",
        note="Bomba completa armada — verificar giro libre del eje antes de energizar motor.", accent=(26, 130, 88))

    # --- ACTO III: FUNCIONAMIENTO CINEMÁTICO + ÓRBITA FINAL — 11.0 s ---
    add("run_pump", 7, "ACTO III · FUNCIONAMIENTO", "PRUEBA CINEMÁTICA EN VIVO",
        "Bombeo: Giro Rotativo ↔ Carrera Lineal",
        "El motor gira #12→#13→#14 (paso 3,0 mm); el émbolo #7 desliza por #11 desplazando fluido en #2.",
        8.0, ((0, 0, -50), 880, 65, 22), ((0, 0, -50), 880, 245, 20),
        chips=[("14", "Husillo girando (p = 3,0 mm/vuelta)", (0.26, 0.39, 0.64)),
               ("7", "Émbolo en carrera axial sobre #11", (0.91, 0.90, 0.86)),
               ("10", "Sensores coaxiales detectando tope a +45°", (0.83, 0.85, 0.89))],
        note="Movimiento sincronizado dentro del cilindro transparente.", accent=(20, 124, 152))

    add("outro", 7, "CIERRE DEL LEGAJO", "CONJUNTO VERIFICADO",
        "Ensamblaje Completo — 45 Ítems BOM / 129 Piezas",
        "Consultar Plano Nº 0b-3D, Plano Nº 0c-3D (BOM) y Plano Nº 0d-3D (Tapa Interior).",
        3.0, ((0, 0, -50), 880, 245, 20), ((0, 0, -50), 960, 295, 20),
        wc=(0.0, -0.15), hero=True, note="0 colisiones geométricas · Modelo listo para impresión 3D y montaje")

    return beats


# =============================================================================
# EVALUACIÓN DE ESTADO POR FRAME
# =============================================================================
def _aplicar_estado_frame(beat, lt, actores, corte_mitades, bolt_groups, opacidades_base):
    """Configura visibilidad, medio corte, opacidades y transformaciones de los 48 sólidos + tornillos."""
    k = beat["key"]
    s = smootherstep(lt)
    s_fast = smootherstep(min(1.0, lt / 0.65))
    s_mid = smootherstep(max(0.0, (lt - 0.15) / 0.65))
    s_late = smootherstep(max(0.0, (lt - 0.45) / 0.50))

    plane_y_pos = vtk.vtkPlane()
    plane_y_pos.SetOrigin(0.0, 0.0, 0.0)
    plane_y_pos.SetNormal(0.0, 1.0, 0.0)

    # Por defecto todo oculto y en posición de reposo
    for nm, ap in actores.items():
        _set_vis(ap, False, opacidades_base[nm])
        _set_xform(ap)
    for cm in corte_mitades.values():
        _set_vis(cm["back"], False, 1.0)
        _set_vis(cm["front"], False, 1.0)
        _set_xform(cm["back"])
        _set_xform(cm["front"])
    for bname, blst in bolt_groups.items():
        for ap, pos in blst:
            _set_vis(ap, False, 1.0)
            _set_xform(ap, dxyz=pos)
            for ac in ap:
                if ac is not None:
                    ac.GetMapper().RemoveAllClippingPlanes()

    def show_full(names, dxyz=(0, 0, 0), spin_z=0.0, pivot=(0, 0, 0), op=None):
        if isinstance(names, str):
            names = (names,)
        for nm in names:
            o = opacidades_base[nm] if op is None else op
            _set_vis(actores[nm], True, o)
            _set_xform(actores[nm], dxyz=dxyz, spin_z=spin_z, pivot=pivot)

    def show_cut_back(names, dxyz=(0, 0, 0), spin_z=0.0, pivot=(0, 0, 0), op=1.0):
        if isinstance(names, str):
            names = (names,)
        for nm in names:
            _set_vis(actores[nm], False)
            _set_vis(corte_mitades[nm]["back"], True, op)
            _set_vis(corte_mitades[nm]["front"], False)
            _set_xform(corte_mitades[nm]["back"], dxyz=dxyz, spin_z=spin_z, pivot=pivot)

    def show_cut_closing(nm, front_op, dxyz=(0, 0, 0)):
        if front_op >= 0.99:
            show_full(nm, dxyz=dxyz, op=1.0)
        else:
            _set_vis(actores[nm], False)
            _set_vis(corte_mitades[nm]["back"], True, 1.0)
            _set_vis(corte_mitades[nm]["front"], front_op > 0.02, front_op)
            _set_xform(corte_mitades[nm]["back"], dxyz=dxyz)
            _set_xform(corte_mitades[nm]["front"], dxyz=dxyz)

    def anim_bolts(gname, dz_start, prog, spin_turns=2.0, cut_y=False):
        for ap, (cx, cy, cz) in bolt_groups[gname]:
            if prog <= 0.01:
                continue
            if cut_y and cy < -0.1:
                continue
            u = smootherstep(min(1.0, prog))
            dz = lerp(dz_start, 0.0, u)
            sp = ((-360.0 if dz_start > 0 else 360.0) * spin_turns * u) if abs(spin_turns) > 1e-4 else 0.0
            _set_vis(ap, True, min(1.0, prog * 3.0))
            _set_xform(ap, dxyz=(cx, cy, cz + dz), spin_z=sp, pivot=(0.0, 0.0, 0.0))

    def show_bolts(gname, cut_y=False, front_op=0.0):
        for ap, (cx, cy, cz) in bolt_groups[gname]:
            if cut_y and front_op < 0.98:
                if cy < -0.1:
                    if front_op > 0.02:
                        _set_vis(ap, True, front_op)
                        _set_xform(ap, dxyz=(cx, cy, cz))
                    continue
                _set_vis(ap, True, 1.0)
                _set_xform(ap, dxyz=(cx, cy, cz))
            else:
                _set_vis(ap, True, 1.0)
                _set_xform(ap, dxyz=(cx, cy, cz))

    def show_bolts_offset(gname, dxyz=(0.0, 0.0, 0.0), spin_z=0.0, op=1.0):
        ox, oy, oz = dxyz
        ang = math.radians(spin_z) if abs(spin_z) > 1e-4 else 0.0
        ca, sa = math.cos(ang), math.sin(ang)
        for ap, (cx, cy, cz) in bolt_groups[gname]:
            _set_vis(ap, True, op)
            if ang != 0.0:
                rx = cx * ca - cy * sa
                ry = cx * sa + cy * ca
                _set_xform(ap, dxyz=(rx + ox, ry + oy, cz + oz), spin_z=spin_z, pivot=(0.0, 0.0, 0.0))
            else:
                _set_xform(ap, dxyz=(cx + ox, cy + oy, cz + oz))

    def show_bolts_translate(gnames, dxyz=(0.0, 0.0, 0.0)):
        if isinstance(gnames, str):
            gnames = (gnames,)
        ox, oy, oz = dxyz
        for gname in gnames:
            for ap, (cx, cy, cz) in bolt_groups[gname]:
                _set_vis(ap, True, 1.0)
                _set_xform(ap, dxyz=(cx + ox, cy + oy, cz + oz))

    # Agrupaciones lógicas
    sub1_cut_parts = (
        "Tapa_Interior_16b_3D", "Sufridera_Int_05b_3D", "Tapa_Sufridera_Int_05a_3D",
        "Reten_10x22x7", "Adaptador_Eje_04_3D", "Adaptador_Rodamiento_03_3D",
        "Rodamiento_SKF_609",
    )
    sub1_full_parts = (
        "Tapa_Interior_16b_3D", "Arandela_Guia_1_08_3D", "ORing_Guia_1", "Sufridera_Guia_1B_3D",
        "Arandela_Guia_2_08_3D", "ORing_Guia_2", "Sufridera_Guia_2B_3D", "Sufridera_Int_05b_3D",
        "Reten_10x22x7", "Tapa_Sufridera_Int_05a_3D", "Adaptador_Eje_04_3D",
        "Adaptador_Rodamiento_03_3D", "Rodamiento_SKF_609", "Transmisor_B_02b_3D",
        "ORing_Eje_11_2x1_8", "Tuerca_Guia_1_08_3D", "Tuerca_Guia_2_08_3D",
    )
    sub2_parts = (
        "Embolo_Delrin_10_3D", "ORing_Embolo_3D",
        "Centro_Embolo_1_11_3D", "Centro_Embolo_2_12_3D",
        "Sensor_Piston_1_3D", "Sensor_Piston_2_3D",
    )
    sub3_parts = (
        "Tapa_Exterior_16a_3D", "Sufridera_Eje_Ext_05a_3D",
        "ORing_Camisa_Ext", "Anillo_Torica_Ext_13_3D",
        "Estructura_Interior_2_07_3D", "Cierre_Estructura_2_15_3D",
    )
    sub4_cage = ("Estructura_Interior_1_07_3D", "Cierre_Estructura_1_15_3D")
    sub4_shaft = ("Transmisor_A_02a_3D", "Pasador_3x14_1", "Pasador_3x14_2")
    tensores_all = (
        "Tensor_1_Parte_1", "Tensor_2_Parte_1", "Tensor_3_Parte_1", "Tensor_4_Parte_1",
        "Tensor_1_Parte_2", "Tensor_2_Parte_2", "Tensor_3_Parte_2", "Tensor_4_Parte_2",
    )

    # =========================================================================
    # INTRO
    # =========================================================================
    if k == "intro_hold":
        show_full(actores.keys())
        for bg in bolt_groups:
            show_bolts(bg)
        return
    if k == "intro_explode":
        show_full(sub1_full_parts, dxyz=(0, 0, lerp(0, 35, s)))
        show_bolts_translate(("suf_guia_inf", "ad_eje_45", "ad_rod_0"), dxyz=(0, 0, lerp(0, 35, s)))
        show_full(sub2_parts, dxyz=(0, 0, lerp(0, -10, s)))
        show_bolts_translate(("ce1_embolo", "ce2_centro"), dxyz=(0, 0, lerp(0, -10, s)))
        show_full(("Tornillo_Sin_Fin_14_3D", "Pasador_3x10_3", "Guia_1_08_3D", "Guia_2_08_3D"), dxyz=(0, 0, lerp(0, -6, s)))
        show_full(("ORing_Camisa_Int", "Anillo_Torica_Int_13_3D"), dxyz=(0, 0, lerp(0, 14, s)))
        show_bolts_translate("anillo_int", dxyz=(0, 0, lerp(0, 14, s)))
        show_full("Cilindro_09_3D", dxyz=(0, 0, lerp(0, -22, s)))
        show_full(sub3_parts, dxyz=(0, 0, lerp(0, -56, s)))
        show_bolts_translate(("suf_ext", "anillo_ext", "cierre_inf_ar", "cierre_inf_tor"), dxyz=(0, 0, lerp(0, -56, s)))
        show_full((*sub4_cage, *sub4_shaft), dxyz=(0, 0, lerp(0, 68, s)))
        show_bolts_translate(("cierre_sup_ar", "cierre_sup_tor"), dxyz=(0, 0, lerp(0, 68, s)))
        show_full("Tapa_Motor_01_3D", dxyz=(0, 0, lerp(0, 98, s)))
        show_bolts_translate(("motor_tor", "motor_ar", "motor_tuerca"), dxyz=(0, 0, lerp(0, 98, s)))
        for idx_t, (xt, yt) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1)), 1):
            dx_t, dy_t = lerp(0, 32 * xt, s), lerp(0, 32 * yt, s)
            dz_p1, dz_p2 = lerp(0, 28, s), lerp(0, -38, s)
            show_full(f"Tensor_{idx_t}_Parte_1", dxyz=(dx_t, dy_t, dz_p1))
            show_full(f"Tensor_{idx_t}_Parte_2", dxyz=(dx_t, dy_t, dz_p2))
            for bg_sup in ("tensor_sup_ar", "tensor_sup_tor"):
                ap_s, (cx, cy, cz) = bolt_groups[bg_sup][idx_t - 1]
                _set_vis(ap_s, True, 1.0)
                _set_xform(ap_s, dxyz=(cx + dx_t, cy + dy_t, cz + dz_p1))
            for bg_inf in ("tensor_inf_ar", "tensor_inf_tor"):
                ap_i, (cx, cy, cz) = bolt_groups[bg_inf][idx_t - 1]
                _set_vis(ap_i, True, 1.0)
                _set_xform(ap_i, dxyz=(cx + dx_t, cy + dy_t, cz + dz_p2))
        return

    # =========================================================================
    # ACTO I — SUBCONJUNTO 1 (TAPA INTERIOR #3 CON CORTE Y>=0)
    # =========================================================================
    if k == "s1_cut_open":
        show_cut_closing("Tapa_Interior_16b_3D", 1.0 - s_fast)
        return

    if k == "s1_guia_suf":
        show_cut_back("Tapa_Interior_16b_3D")
        u_or = smootherstep(min(1.0, lt / 0.36))
        u_suf = smootherstep(max(0.0, min(1.0, (lt - 0.12) / 0.40)))
        u_ar = smootherstep(min(1.0, lt / 0.45))
        show_full(("ORing_Guia_1", "ORing_Guia_2"), dxyz=(0, 0, lerp(-32.0, 0.0, u_or)))
        show_full(("Arandela_Guia_1_08_3D", "Arandela_Guia_2_08_3D"), dxyz=(0, 0, lerp(42.0, 0.0, u_ar)))
        show_full(("Sufridera_Guia_1B_3D", "Sufridera_Guia_2B_3D"), dxyz=(0, 0, lerp(-52.0, 0.0, u_suf)))
        anim_bolts("suf_guia_inf", -26.0, max(0.0, (lt - 0.38) / 0.42))
        # Presentar tuercas #31 arriba girando en sentido horario (-Z spin)
        if lt > 0.55:
            u31 = smootherstep((lt - 0.55) / 0.40)
            dz31 = lerp(38.0, 0.0, u31)
            for idx_g, xg in ((1, -28.31), (2, 28.31)):
                show_full(f"Tuerca_Guia_{idx_g}_08_3D", dxyz=(0, 0, dz31), spin_z=-360.0 * u31, pivot=(xg, 0.0, 27.6))
        return

    if k == "s1_sello_reten":
        show_cut_back("Tapa_Interior_16b_3D")
        show_full(("Arandela_Guia_1_08_3D", "ORing_Guia_1", "Sufridera_Guia_1B_3D",
                   "Arandela_Guia_2_08_3D", "ORing_Guia_2", "Sufridera_Guia_2B_3D",
                   "Tuerca_Guia_1_08_3D", "Tuerca_Guia_2_08_3D"))
        show_bolts("suf_guia_inf")
        u_suf = smootherstep(min(1.0, lt / 0.38))
        u_ret = smootherstep(max(0.0, min(1.0, (lt - 0.22) / 0.38)))
        u_tap = smootherstep(max(0.0, min(1.0, (lt - 0.45) / 0.35)))
        show_cut_back("Sufridera_Int_05b_3D", dxyz=(0, 0, lerp(-56.0, 0.0, u_suf)))
        show_cut_back("Reten_10x22x7", dxyz=(0, 0, lerp(-72.0, 0.0, u_ret)))
        show_cut_back("Tapa_Sufridera_Int_05a_3D", dxyz=(0, 0, lerp(-84.0, 0.0, u_tap)))
        return

    if k == "s1_ad_eje_17":
        show_cut_back(("Tapa_Interior_16b_3D", "Sufridera_Int_05b_3D", "Reten_10x22x7", "Tapa_Sufridera_Int_05a_3D"))
        show_full(("Arandela_Guia_1_08_3D", "ORing_Guia_1", "Sufridera_Guia_1B_3D",
                   "Arandela_Guia_2_08_3D", "ORing_Guia_2", "Sufridera_Guia_2B_3D",
                   "Tuerca_Guia_1_08_3D", "Tuerca_Guia_2_08_3D"))
        show_bolts("suf_guia_inf")

        # 1) Primero (lt=0..0.46) Adaptador_Eje_04_3D (#17) derecho (+Z arriba) baja recto sobre Tapa_Interior #3.
        # 2) Luego (lt=0.44..0.96) los 4× Tornillos Allen M2x14 descienden desde arriba (+Z) hacia los cajeados Ø4.10
        #    a 45°; #17 se muestra brevemente translúcido (rayos X) durante el apriete para ver el vástago entrar en #3.
        u_17 = smootherstep(min(1.0, lt / 0.46))
        if lt < 0.40:
            op_17 = 1.0
        elif lt < 0.52:
            op_17 = lerp(1.0, 0.58, (lt - 0.40) / 0.12)
        elif lt < 0.88:
            op_17 = 0.58
        else:
            op_17 = lerp(0.58, 1.0, (lt - 0.88) / 0.12)
        show_cut_back("Adaptador_Eje_04_3D", dxyz=(0, 0, lerp(44.0, 0.0, u_17)), op=op_17)
        anim_bolts("ad_eje_45", 26.0, max(0.0, (lt - 0.44) / 0.50), cut_y=True)
        return

    if k == "s1_rodam_15":
        show_cut_back(("Tapa_Interior_16b_3D", "Sufridera_Int_05b_3D", "Reten_10x22x7",
                       "Tapa_Sufridera_Int_05a_3D", "Adaptador_Eje_04_3D"))
        show_full(("Arandela_Guia_1_08_3D", "ORing_Guia_1", "Sufridera_Guia_1B_3D",
                   "Arandela_Guia_2_08_3D", "ORing_Guia_2", "Sufridera_Guia_2B_3D",
                   "Tuerca_Guia_1_08_3D", "Tuerca_Guia_2_08_3D"))
        show_bolts("suf_guia_inf")
        show_bolts("ad_eje_45", cut_y=True)

        # 1) Prensar SKF 609 #24 (en corte) desde abajo en Adaptador #15 (en corte) arriba (Z+44)
        # 2) Bajar #15 + #24 sobre #17 y fijar con tornillos Allen M2x8 a 22,5°/112,5° en los ciegos de #17
        u_skf = smootherstep(min(1.0, lt / 0.40))
        u_15 = smootherstep(max(0.0, min(1.0, (lt - 0.38) / 0.36)))
        dz15 = lerp(44.0, 0.0, u_15)
        dz_skf = lerp(16.0, 44.0, u_skf) if lt < 0.38 else dz15
        show_cut_back("Adaptador_Rodamiento_03_3D", dxyz=(0, 0, dz15))
        show_cut_back("Rodamiento_SKF_609", dxyz=(0, 0, dz_skf))
        anim_bolts("ad_rod_0", 26.0, max(0.0, (lt - 0.70) / 0.26), cut_y=True)
        return

    if k == "s1_eje_oring":
        show_full(("Arandela_Guia_1_08_3D", "ORing_Guia_1", "Sufridera_Guia_1B_3D",
                   "Arandela_Guia_2_08_3D", "ORing_Guia_2", "Sufridera_Guia_2B_3D",
                   "Tuerca_Guia_1_08_3D", "Tuerca_Guia_2_08_3D"))
        u_eje = smootherstep(min(1.0, lt / 0.45))
        u_or = smootherstep(max(0.0, min(1.0, (lt - 0.30) / 0.32)))
        u_close = smootherstep(max(0.0, min(1.0, (lt - 0.62) / 0.30)))
        show_bolts("suf_guia_inf")
        show_bolts("ad_eje_45", cut_y=True, front_op=u_close)
        show_bolts("ad_rod_0", cut_y=True, front_op=u_close)
        for pcut in sub1_cut_parts:
            show_cut_closing(pcut, u_close)
        show_full("Transmisor_B_02b_3D", dxyz=(0, 0, lerp(-88.0, 0.0, u_eje)))
        show_full("ORing_Eje_11_2x1_8", dxyz=(0, 0, lerp(58.0, 0.0, u_or)))
        return

    # =========================================================================
    # ACTO I — SUBCONJUNTO 2 (ÉMBOLO MÓVIL)
    # =========================================================================
    if k == "s2_embolo_base":
        show_full("Embolo_Delrin_10_3D")
        show_full("ORing_Embolo_3D", dxyz=(0, 0, lerp(44.0, 0.0, s_mid)))
        return

    if k == "s2_embolo_comp":
        show_full(("Embolo_Delrin_10_3D", "ORing_Embolo_3D"))
        u_ce = smootherstep(min(1.0, lt / 0.45))
        u_sp = smootherstep(max(0.0, min(1.0, (lt - 0.40) / 0.45)))
        show_full("Centro_Embolo_1_11_3D", dxyz=(0, 0, lerp(-38.0, 0.0, u_ce)))
        show_full("Centro_Embolo_2_12_3D", dxyz=(0, 0, lerp(38.0, 0.0, u_ce)))
        anim_bolts("ce1_embolo", -26.0, max(0.0, (lt - 0.30) / 0.32))
        anim_bolts("ce2_centro", 28.0, max(0.0, (lt - 0.34) / 0.32))
        show_full("Sensor_Piston_1_3D", dxyz=(0, 0, lerp(34.0, 0.0, u_sp)))
        show_full("Sensor_Piston_2_3D", dxyz=(0, 0, lerp(-34.0, 0.0, u_sp)))
        return

    # =========================================================================
    # ACTO I — SUBCONJUNTO 3 (BASE EXTERIOR)
    # =========================================================================
    if k == "s3_base_caps":
        show_full("Tapa_Exterior_16a_3D")
        u16 = smootherstep(min(1.0, lt / 0.45))
        u_top = smootherstep(max(0.0, min(1.0, (lt - 0.32) / 0.50)))
        show_full("Sufridera_Eje_Ext_05a_3D", dxyz=(0, 0, lerp(42.0, 0.0, u16)))
        anim_bolts("suf_ext", 24.0, max(0.0, (lt - 0.30) / 0.30))
        show_full("ORing_Camisa_Ext", dxyz=(0, 0, lerp(44.0, 0.0, u_top)))
        show_full("Anillo_Torica_Ext_13_3D", dxyz=(0, 0, lerp(64.0, 0.0, u_top)))
        anim_bolts("anillo_ext", 26.0, max(0.0, (lt - 0.65) / 0.30))
        return

    if k == "s3_base_est":
        show_full(("Tapa_Exterior_16a_3D", "Sufridera_Eje_Ext_05a_3D", "ORing_Camisa_Ext", "Anillo_Torica_Ext_13_3D"))
        show_bolts("suf_ext"); show_bolts("anillo_ext")
        u_e2 = smootherstep(min(1.0, lt / 0.40))
        u_c2 = smootherstep(max(0.0, min(1.0, (lt - 0.30) / 0.35)))
        show_full("Estructura_Interior_2_07_3D", dxyz=(0, 0, lerp(-40.0, 0.0, u_e2)))
        show_full("Cierre_Estructura_2_15_3D", dxyz=(0, 0, lerp(-56.0, 0.0, u_c2)))
        anim_bolts("cierre_inf_ar", -26.0, max(0.0, (lt - 0.56) / 0.16), spin_turns=0.0)
        anim_bolts("cierre_inf_tor", -36.0, max(0.0, (lt - 0.68) / 0.30), spin_turns=2.5)
        return

    # =========================================================================
    # ACTO I — SUBCONJUNTO 4 (CABEZAL MOTOR)
    # =========================================================================
    if k == "s4_cabezal_cage":
        show_full("Estructura_Interior_1_07_3D")
        u_c1 = smootherstep(min(1.0, lt / 0.36))
        u_tm = smootherstep(max(0.0, min(1.0, (lt - 0.46) / 0.28)))
        show_full("Cierre_Estructura_1_15_3D", dxyz=(0, 0, lerp(42.0, 0.0, u_c1)))
        anim_bolts("cierre_sup_ar", 24.0, max(0.0, (lt - 0.26) / 0.14), spin_turns=0.0)
        anim_bolts("cierre_sup_tor", 36.0, max(0.0, (lt - 0.36) / 0.24), spin_turns=2.5)
        show_full("Tapa_Motor_01_3D", dxyz=(0, 0, lerp(44.0, 0.0, u_tm)))
        anim_bolts("motor_tor", 24.0, max(0.0, (lt - 0.64) / 0.18), spin_turns=2.0)
        anim_bolts("motor_ar", -16.0, max(0.0, (lt - 0.72) / 0.12), spin_turns=0.0)
        anim_bolts("motor_tuerca", -24.0, max(0.0, (lt - 0.80) / 0.18), spin_turns=2.0)
        return

    if k == "s4_trans_a":
        show_full((*sub4_cage, "Tapa_Motor_01_3D"), op=0.22)
        show_full("Transmisor_A_02a_3D", dxyz=(0, 0, lerp(40.0, 0.0, s_fast)))
        u_p = smootherstep(max(0.0, min(1.0, (lt - 0.35) / 0.50)))
        show_full("Pasador_3x14_1", dxyz=(0, lerp(-32.0, 0.0, u_p), 0))
        show_full("Pasador_3x14_2", dxyz=(0, lerp(32.0, 0.0, u_p), 0))
        return

    # =========================================================================
    # ACTO I — SUBCONJUNTO 5 (4× TENSORES PARTIDOS)
    # =========================================================================
    if k == "s5_tensores":
        u_t = smootherstep(min(1.0, lt / 0.72))
        dz_sep = lerp(38.0, 0.0, u_t)
        for idx_t in range(1, 5):
            show_full(f"Tensor_{idx_t}_Parte_2")
            show_full(f"Tensor_{idx_t}_Parte_1", dxyz=(0, 0, dz_sep))
        return

    # =========================================================================
    # ACTO II — ENSAMBLAJE FINAL
    # =========================================================================
    def _show_sub1_complete():
        show_full(sub1_full_parts)
        for bg in ("suf_guia_inf", "ad_eje_45", "ad_rod_0"):
            show_bolts(bg)

    if k == "f1_sub1_base":
        _show_sub1_complete()
        return

    if k == "f2_embolo_husillo":
        _show_sub1_complete()
        # 1) Primero aparece el Tornillo sin fin #14 en posición previa (dz = -36 mm, antes de colocarlo en su lugar sobre #13);
        # 2) Aparece por debajo (-Z) el subensamblaje del émbolo (S2 + tornillos reales CE1/CE2) y calza en la espiga Ø8.80;
        # 3) A medida que el subensamblaje del émbolo sube SIN GIRAR (spin_emb = 0), es el sinfín #14 el que GIRA
        #    (spin_hus) para enroscar el subensamblaje del émbolo hasta que quede en su lugar sobre el sinfín;
        # 4) Finalmente el conjunto (#14 + S2) sube hasta acoplar #14 en #13 y se bloquea con el Pasador Ø3x10 #30.
        u_hus_in = smootherstep(min(1.0, lt / 0.14))
        u_slide = smootherstep(max(0.0, min(1.0, (lt - 0.14) / 0.18)))
        u_screw = smoothstep(max(0.0, min(1.0, (lt - 0.32) / 0.42)))
        u_place = smootherstep(max(0.0, min(1.0, (lt - 0.74) / 0.14)))
        u_p30 = smootherstep(max(0.0, min(1.0, (lt - 0.86) / 0.12)))

        if lt < 0.14:
            dz_hus = lerp(-64.0, -36.0, u_hus_in)
            spin_hus = 0.0
        elif lt < 0.74:
            dz_hus = -36.0
            spin_hus = lerp(0.0, -1440.0, u_screw)
        else:
            dz_hus = lerp(-36.0, 0.0, u_place)
            spin_hus = 0.0

        show_full("Tornillo_Sin_Fin_14_3D", dxyz=(0, 0, dz_hus), spin_z=spin_hus, pivot=(0.0, 0.0, 0.0))
        if lt > 0.86:
            show_full("Pasador_3x10_3", dxyz=(0, lerp(-36.0, 0.0, u_p30), 0))

        if lt >= 0.12:
            if lt < 0.32:
                dz_emb = lerp(-176.0, -144.5, u_slide)
            elif lt < 0.74:
                dz_emb = lerp(-144.5, -36.0, u_screw)
            else:
                dz_emb = lerp(-36.0, 0.0, u_place)
            op_emb = min(1.0, max(0.0, (lt - 0.12) / 0.08))
            show_full(sub2_parts, dxyz=(0, 0, dz_emb), spin_z=0.0, op=None if op_emb >= 0.99 else op_emb)
            show_bolts_offset("ce1_embolo", dxyz=(0, 0, dz_emb), spin_z=0.0, op=op_emb)
            show_bolts_offset("ce2_centro", dxyz=(0, 0, dz_emb), spin_z=0.0, op=op_emb)
        return

    if k == "f3_guias_tuercas":
        # Sub1 sin Tuerca_Guia todavía girada hasta que suban #11
        show_full([p for p in sub1_full_parts if not p.startswith("Tuerca_Guia")])
        for bg in ("suf_guia_inf", "ad_eje_45", "ad_rod_0"):
            show_bolts(bg)
        show_full((*sub2_parts, "Tornillo_Sin_Fin_14_3D", "Pasador_3x10_3"))
        show_bolts("ce1_embolo"); show_bolts("ce2_centro")

        u_g = smootherstep(min(1.0, lt / 0.58))
        show_full(("Guia_1_08_3D", "Guia_2_08_3D"), dxyz=(0, 0, lerp(-145.0, 0.0, u_g)))
        u_n = smootherstep(max(0.0, min(1.0, (lt - 0.52) / 0.42)))
        for idx_g, xg in ((1, -28.31), (2, 28.31)):
            show_full(f"Tuerca_Guia_{idx_g}_08_3D", dxyz=(0, 0, lerp(28.0, 0.0, u_n)),
                      spin_z=-720.0 * u_n, pivot=(xg, 0.0, 27.6))
        return

    if k == "f4_camisa_vidrio":
        _show_sub1_complete()
        for bg in ("ce1_embolo", "ce2_centro"):
            show_bolts(bg)
        show_full((*sub2_parts, "Tornillo_Sin_Fin_14_3D", "Pasador_3x10_3", "Guia_1_08_3D", "Guia_2_08_3D"))
        u_or = smootherstep(min(1.0, lt / 0.35))
        u_an = smootherstep(max(0.0, min(1.0, (lt - 0.14) / 0.34)))
        u_cil = smootherstep(max(0.0, min(1.0, (lt - 0.50) / 0.46)))
        show_full("ORing_Camisa_Int", dxyz=(0, 0, lerp(-65.0, 0.0, u_or)))
        show_full("Anillo_Torica_Int_13_3D", dxyz=(0, 0, lerp(-75.0, 0.0, u_an)))
        anim_bolts("anillo_int", -28.0, max(0.0, (lt - 0.48) / 0.24))
        show_full("Cilindro_09_3D", dxyz=(0, 0, lerp(-115.0, 0.0, u_cil)))
        return

    if k == "f5_base_exterior":
        _show_sub1_complete()
        show_bolts("ce1_embolo"); show_bolts("ce2_centro"); show_bolts("anillo_int")
        show_full((*sub2_parts, "Tornillo_Sin_Fin_14_3D", "Pasador_3x10_3", "Guia_1_08_3D", "Guia_2_08_3D",
                   "ORing_Camisa_Int", "Anillo_Torica_Int_13_3D", "Cilindro_09_3D"))
        dz_b = lerp(-125.0, 0.0, s_fast)
        show_full(sub3_parts, dxyz=(0, 0, dz_b))
        show_bolts_translate(("suf_ext", "anillo_ext", "cierre_inf_ar", "cierre_inf_tor"), dxyz=(0, 0, dz_b))
        return

    if k == "f6_cabezal_motor":
        _show_sub1_complete()
        for bg in ("ce1_embolo", "ce2_centro", "anillo_int", "suf_ext", "anillo_ext", "cierre_inf_ar", "cierre_inf_tor"):
            show_bolts(bg)
        show_full((*sub2_parts, "Tornillo_Sin_Fin_14_3D", "Pasador_3x10_3", "Guia_1_08_3D", "Guia_2_08_3D",
                   "ORing_Camisa_Int", "Anillo_Torica_Int_13_3D", "Cilindro_09_3D", *sub3_parts))

        u_ta = smootherstep(min(1.0, lt / 0.26))
        u_p29 = smootherstep(max(0.0, min(1.0, (lt - 0.22) / 0.20)))
        u_jaula = smootherstep(max(0.0, min(1.0, (lt - 0.38) / 0.26)))
        u_tm = smootherstep(max(0.0, min(1.0, (lt - 0.66) / 0.18)))

        show_full("Transmisor_A_02a_3D", dxyz=(0, 0, lerp(95.0, 0.0, u_ta)))
        if lt > 0.20:
            show_full("Pasador_3x14_1", dxyz=(0, lerp(-32.0, 0.0, u_p29), 0))
            show_full("Pasador_3x14_2", dxyz=(0, lerp(32.0, 0.0, u_p29), 0))
        if lt > 0.38:
            dz_j = lerp(72.0, 0.0, u_jaula)
            show_full(sub4_cage, dxyz=(0, 0, dz_j))
            anim_bolts("cierre_sup_ar", 24.0, max(0.0, (lt - 0.60) / 0.12), spin_turns=0.0)
            anim_bolts("cierre_sup_tor", 34.0, max(0.0, (lt - 0.66) / 0.18), spin_turns=2.5)
        if lt > 0.64:
            show_full("Tapa_Motor_01_3D", dxyz=(0, 0, lerp(58.0, 0.0, u_tm)))
            anim_bolts("motor_tor", 22.0, max(0.0, (lt - 0.80) / 0.14), spin_turns=2.0)
            anim_bolts("motor_ar", -16.0, max(0.0, (lt - 0.84) / 0.10), spin_turns=0.0)
            anim_bolts("motor_tuerca", -24.0, max(0.0, (lt - 0.88) / 0.12), spin_turns=2.0)
        return

    if k == "f7_tensores_cierre":
        show_full([nm for nm in actores.keys() if nm not in tensores_all])
        for bg in (
            "suf_guia_inf", "ad_eje_45", "ad_rod_0",
            "ce1_embolo", "ce2_centro", "anillo_int",
            "suf_ext", "anillo_ext", "cierre_inf_ar", "cierre_inf_tor",
            "cierre_sup_ar", "cierre_sup_tor", "motor_tor", "motor_ar", "motor_tuerca",
        ):
            show_bolts(bg)

        u_ten = smootherstep(min(1.0, lt / 0.56))
        for idx_t, (xt, yt) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1)), 1):
            dx = lerp(42.0 * xt, 0.0, u_ten)
            dy = lerp(42.0 * yt, 0.0, u_ten)
            dz = lerp(35.0, 0.0, u_ten)
            show_full((f"Tensor_{idx_t}_Parte_1", f"Tensor_{idx_t}_Parte_2"), dxyz=(dx, dy, dz))
        anim_bolts("tensor_sup_ar", 26.0, max(0.0, (lt - 0.52) / 0.16), spin_turns=0.0)
        anim_bolts("tensor_sup_tor", 38.0, max(0.0, (lt - 0.62) / 0.34), spin_turns=3.0)
        anim_bolts("tensor_inf_ar", -26.0, max(0.0, (lt - 0.52) / 0.16), spin_turns=0.0)
        anim_bolts("tensor_inf_tor", -38.0, max(0.0, (lt - 0.62) / 0.34), spin_turns=3.0)
        return

    # =========================================================================
    # ACTO III — CINEMÁTICA SINCRONIZADA + ÓRBITA DE CIERRE
    # =========================================================================
    if k == "run_pump":
        rot_parts = (
            "Transmisor_A_02a_3D", "Transmisor_B_02b_3D", "ORing_Eje_11_2x1_8",
            "Pasador_3x14_1", "Pasador_3x14_2", "Pasador_3x10_3", "Tornillo_Sin_Fin_14_3D",
        )
        static_parts = [nm for nm in actores.keys() if nm not in rot_parts and nm not in sub2_parts]
        show_full(static_parts)
        for bg in bolt_groups:
            if bg not in ("ce1_embolo", "ce2_centro"):
                show_bolts(bg)

        # 2 ciclos completos suaves (carrera lineal ±16.5 mm -> giro proporcional al paso 3.0 mm)
        dz_emb = -16.5 * math.sin(2.0 * math.pi * 2.0 * lt)
        # Relación paso sin fin p=3.0 mm (ajustado suave para evitar aliasing estroboscópico)
        spin_deg = -(dz_emb / 3.0) * 360.0
        show_full(sub2_parts, dxyz=(0, 0, dz_emb))
        show_bolts_offset("ce1_embolo", dxyz=(0, 0, dz_emb))
        show_bolts_offset("ce2_centro", dxyz=(0, 0, dz_emb))
        show_full(rot_parts, spin_z=spin_deg, pivot=(0.0, 0.0, 0.0))
        return

    if k == "outro":
        show_full(actores.keys())
        for bg in bolt_groups:
            show_bolts(bg)
        return


def generar_video(ruta_mp4=RUTA_MP4_DEFAULT, storyboard_dir=None):
    os.makedirs(os.path.dirname(ruta_mp4), exist_ok=True)
    if storyboard_dir:
        os.makedirs(storyboard_dir, exist_ok=True)

    fonts = _cargar_fuentes()
    doc, rw, ren, actores, corte_mitades, bolt_groups, _, opacidades_base = construir_escena()
    beats = _build_timeline()
    total_frames = sum(b["n_frames"] for b in beats)
    total_sec = sum(b["dur"] for b in beats)
    print(f"Guion: {len(beats)} planos, {total_frames} frames @ {FPS} fps ({total_sec:.1f} s).")

    cam = ren.GetActiveCamera()
    cam.SetViewAngle(32.0)

    wif = vtk.vtkWindowToImageFilter()
    wif.SetInput(rw)
    wif.SetInputBufferTypeToRGB()

    import shutil

    raw_pipe = os.environ.get("VIDEO_RAW_PIPE", "").strip() or None
    proc = None
    raw_fh = None
    if not storyboard_dir:
        if raw_pipe:
            raw_fh = open(raw_pipe, "wb", buffering=0)
        else:
            ffmpeg_bin = shutil.which("ffmpeg")
            if not ffmpeg_bin:
                raise RuntimeError(
                    "No se encontró 'ffmpeg' en PATH (sandbox Snap). "
                    "Use VIDEO_RAW_PIPE apuntando a un FIFO conectado a /usr/bin/ffmpeg en el host."
                )
            cmd = [
                ffmpeg_bin, "-y",
                "-f", "rawvideo", "-vcodec", "rawvideo",
                "-s", f"{ANCHO}x{ALTO}", "-pix_fmt", "rgb24",
                "-r", str(FPS), "-i", "-",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                ruta_mp4,
            ]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            raw_fh = proc.stdin

    f_global = 0
    only_keys = [x.strip() for x in os.environ.get("VIDEO_ONLY_KEYS", "").split(",") if x.strip()]
    for b_idx, beat in enumerate(beats):
        n_f = beat["n_frames"]
        if storyboard_dir and only_keys and beat["key"] not in only_keys:
            f_global += n_f
            continue
        sample_fis = (
            {int(r * (n_f - 1)) for r in (0.12, 0.32, 0.52, 0.72, 0.92)}
            if (storyboard_dir and only_keys)
            else {0, int(0.48 * n_f), n_f - 1}
        )
        for fi in range(n_f):
            lt = fi / float(max(1, n_f - 1))
            if storyboard_dir and fi not in sample_fis:
                f_global += 1
                continue

            _aplicar_estado_frame(beat, lt, actores, corte_mitades, bolt_groups, opacidades_base)

            sc = smootherstep(lt)
            f0, d0, az0, el0 = beat["cam_from"]
            f1, d1, az1, el1 = beat["cam_to"]
            foc = lerp_vec(f0, f1, sc)
            dist = lerp(d0, d1, sc)
            az = lerp(az0, az1, sc)
            el = lerp(el0, el1, sc)
            cpos = cam_pos_orbita(foc, dist, az, el)

            cam.SetFocalPoint(*foc)
            cam.SetPosition(*cpos)
            cam.SetViewUp(0.0, 0.0, 1.0)
            cam.SetWindowCenter(*beat["wc"])
            ren.ResetCameraClippingRange()
            rw.Render()

            wif.Modified()
            wif.Update()
            vimg = wif.GetOutput()
            arr = numpy_support.vtk_to_numpy(vimg.GetPointData().GetScalars())
            # VTK da origen abajo-izquierda; voltear eje vertical para PIL
            rgb_np = np.flipud(arr.reshape(ALTO, ANCHO, 3))

            prog = f_global / float(max(1, total_frames - 1))
            frame_rgb = componer_hud(rgb_np, fonts, beat, prog, beat["act_idx"])

            if storyboard_dir:
                out_png = os.path.join(storyboard_dir, f"sb_{b_idx:02d}_{beat['key']}_f{fi:03d}.png")
                Image.fromarray(frame_rgb).save(out_png)
            else:
                raw_fh.write(frame_rgb.tobytes())

            f_global += 1

        if not storyboard_dir:
            print(f"  [{b_idx + 1:02d}/{len(beats)}] {beat['key']} ({n_f} frames) -> {f_global}/{total_frames}")
            sys.stdout.flush()

    if proc is not None:
        raw_fh.close()
        stderr = proc.stderr.read().decode("utf-8", errors="ignore")
        rc = proc.wait()
        if rc != 0:
            raise RuntimeError(f"ffmpeg falló rc={rc}: {stderr[-600:]}")
        sz = os.path.getsize(ruta_mp4) if os.path.exists(ruta_mp4) else 0
        print(f"VIDEO_OK: {ruta_mp4} ({sz / (1024 * 1024):.2f} MB)")
    elif raw_fh is not None:
        raw_fh.close()
        print(f"STREAM_OK: {f_global} frames escritos en {raw_pipe}")
    else:
        print(f"STORYBOARD_OK: {storyboard_dir}")

    App.closeDocument(doc.Name)


if __name__ in ("__main__", "generar_video_ensamblaje_3d", "__console__") and not getattr(sys, "_gf_video_ran", False):
    sys._gf_video_ran = True
    sb_dir = os.environ.get("VIDEO_STORYBOARD_DIR", "").strip() or None
    out_mp4 = os.environ.get("VIDEO_OUT_MP4", "").strip() or RUTA_MP4_DEFAULT
    generar_video(ruta_mp4=out_mp4, storyboard_dir=sb_dir)
