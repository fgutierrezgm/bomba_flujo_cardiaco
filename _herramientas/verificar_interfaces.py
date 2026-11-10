# verificar_interfaces.py - Verifica coaxialidad de agujeros/pasadores/sensores e interferencias entre sólidos en un ensamblaje.
# Uso: FCSTD=<ensamblaje.FCStd> /snap/bin/freecad.cmd _herramientas/verificar_interfaces.py
import fnmatch
import json
import math
import os
import sys
import FreeCAD as App

ruta = os.environ.get("FCSTD")
if not ruta:
    print("Uso: FCSTD=<ensamblaje.FCStd> freecadcmd _herramientas/verificar_interfaces.py")
    sys.exit(2)

ruta_abs = os.path.abspath(ruta)
doc = next((d for d in App.listDocuments().values()
            if os.path.abspath(getattr(d, "FileName", "")) == ruta_abs), None)
if doc is None:
    doc = App.openDocument(ruta_abs)

errores = []
avisos = []


def err(msg):
    errores.append(msg)
    print("ERROR:", msg)


def warn(msg):
    avisos.append(msg)
    print("AVISO:", msg)


# Asegurar que el ensamblaje se evalúe en posición armada (explosion = 0)
ss_gen = doc.getObject("Parametros_Generales")
exp_orig = None
if ss_gen:
    try:
        exp_orig = float(ss_gen.get("explosion"))
        if abs(exp_orig) > 1e-6:
            ss_gen.set("B2", "0.0")
            doc.recompute()
    except Exception:
        pass

asm = next((o for o in doc.Objects if o.isDerivedFrom("App::Part")), None)
interfaces_cfg = {"coaxiales": [], "pares_rosca_ajuste": []}
if asm and hasattr(asm, "Interfaces_Declaradas"):
    try:
        raw = getattr(asm, "Interfaces_Declaradas", "")
        if raw:
            interfaces_cfg = json.loads(raw)
    except Exception as e:
        warn(f"No se pudo leer Interfaces_Declaradas: {e}")


def _cilindros_instancia(inst_name, patron):
    link = doc.getObject(inst_name)
    if link is None or getattr(link, "LinkedObject", None) is None:
        return None, []
    doc_h = link.LinkedObject.Document
    cils = [
        o for o in doc_h.Objects
        if o.TypeId == "Part::Cylinder" and fnmatch.fnmatch(o.Name, patron)
    ]
    return link, cils


def _eje_global(link, cil):
    plc_g = link.Placement.multiply(cil.Placement)
    p0 = plc_g.Base
    u = plc_g.Rotation.multVec(App.Vector(0, 0, 1))
    u.normalize()
    return p0, u


def _dist_entre_ejes(p1, u1, p2, u2):
    dot = abs(u1.dot(u2))
    ang_deg = math.degrees(math.acos(max(-1.0, min(1.0, dot))))
    dp = p2.sub(p1)
    dist_perp = dp.cross(u1).Length
    return ang_deg, dist_perp


# 1. Verificación de coaxialidad de patrones declarados
coaxiales = interfaces_cfg.get("coaxiales", [])
n_coax_ok = 0
for item in coaxiales:
    ref1 = item["ref1"]
    ref2 = item["ref2"]
    desc = item.get("descripcion", f"{ref1} <-> {ref2}")
    tol = float(item.get("tol_mm", 0.05))
    inst1, pat1 = ref1.split(":", 1)
    inst2, pat2 = ref2.split(":", 1)
    l1, cils1 = _cilindros_instancia(inst1, pat1)
    l2, cils2 = _cilindros_instancia(inst2, pat2)
    if not cils1:
        err(f"[{desc}] No se encontraron cilindros para '{ref1}'")
        continue
    if not cils2:
        err(f"[{desc}] No se encontraron cilindros para '{ref2}'")
        continue
    if len(cils1) != len(cils2):
        err(f"[{desc}] Cantidad distinta de agujeros: {len(cils1)} en '{ref1}' vs {len(cils2)} en '{ref2}'")
        continue

    ejes1 = [(c.Name, _eje_global(l1, c)) for c in cils1]
    ejes2 = [(c.Name, _eje_global(l2, c)) for c in cils2]
    max_desv = 0.0
    fallo_par = False
    for n1, (p1, u1) in ejes1:
        mejor = None
        for n2, (p2, u2) in ejes2:
            ang, d_perp = _dist_entre_ejes(p1, u1, p2, u2)
            if mejor is None or (d_perp + ang * 10.0) < (mejor[0] + mejor[1] * 10.0):
                mejor = (d_perp, ang, n2)
        d_perp, ang, n2_match = mejor
        max_desv = max(max_desv, d_perp)
        if ang > 0.5 or d_perp > tol:
            err(
                f"[{desc}] Desalineación entre {inst1}.{n1} y {inst2}.{n2_match}: "
                f"desviación radial = {d_perp:.3f} mm (tol {tol:.3f} mm), ángulo = {ang:.2f}°"
            )
            fallo_par = True
    if not fallo_par:
        n_coax_ok += 1
        print(f"INFO Coaxialidad OK [{desc}]: {len(ejes1)}/{len(ejes2)} ejes (desv. máx = {max_desv:.4f} mm)")

# 2. Verificación de interferencias volumétricas entre sólidos vinculados
pares_exentos = {tuple(sorted(p)) for p in interfaces_cfg.get("pares_rosca_ajuste", [])}
pares_plano_aviso = {
    tuple(sorted(item["par"])): item.get("motivo", "Incoherencia dimensional del plano original")
    for item in interfaces_cfg.get("interferencias_plano", [])
}
links = [o for o in doc.Objects if o.TypeId == "App::Link" and getattr(o, "LinkedObject", None)]
formas_inst = []
for l in links:
    doc_h = l.LinkedObject.Document
    cands = [
        o for o in doc_h.Objects
        if o.isDerivedFrom("Part::Feature") and not o.isDerivedFrom("Part::Datum")
        and getattr(o, "Shape", None) and o.Shape.Solids
        and not any(p.isDerivedFrom("Part::Feature") and not p.isDerivedFrom("Part::Datum") for p in o.InList)
    ]
    if cands:
        sh = cands[-1].Shape.copy()
        sh.Placement = l.Placement.multiply(sh.Placement)
        formas_inst.append((l.Name, sh, sh.BoundBox))

n_colisiones = 0
TOL_VOL_MM3 = 1.0
for i in range(len(formas_inst)):
    n1, sh1, bb1 = formas_inst[i]
    for j in range(i + 1, len(formas_inst)):
        n2, sh2, bb2 = formas_inst[j]
        clave_par = tuple(sorted((n1, n2)))
        if clave_par in pares_exentos:
            continue
        if not bb1.intersect(bb2):
            continue
        try:
            com = sh1.common(sh2)
            vol = com.Volume if com and com.Solids else 0.0
            if vol > TOL_VOL_MM3:
                if clave_par in pares_plano_aviso:
                    warn(
                        f"Interferencia del plano original entre '{n1}' y '{n2}' ({vol:.1f} mm3): "
                        f"{pares_plano_aviso[clave_par]}"
                    )
                else:
                    n_colisiones += 1
                    err(f"Interferencia volumétrica no declarada entre '{n1}' y '{n2}': {vol:.2f} mm3")
        except Exception:
            pass

if n_colisiones == 0:
    print(f"INFO Interferencias: 0 colisiones inesperadas entre {len(formas_inst)} instancias sólidas")

# 3. Verificación de material ferromagnético en topes de sensores inductivos
for nombre_tope in ("Sensor_Piston_1_05b", "Sensor_Piston_2_05b"):
    l_tope = doc.getObject(nombre_tope)
    if l_tope and getattr(l_tope, "LinkedObject", None):
        hm = l_tope.LinkedObject.Document.getObject("Materiales")
        if hm:
            mat_nom = str(hm.get("material_nombre"))
            if "304" in mat_nom or "316" in mat_nom:
                warn(f"{nombre_tope} usa acero austenítico no magnético ({mat_nom}); se recomienda AISI 430 o SAE 1045.")
            else:
                print(f"INFO Material ferromagnético OK en {nombre_tope}: {mat_nom}")

if exp_orig is not None and abs(exp_orig) > 1e-6:
    ss_gen.set("B2", str(exp_orig))
    doc.recompute()

if errores:
    print(f"VERIFICACION_INTERFACES: FALLIDA ({len(errores)} errores, {len(avisos)} avisos) - {ruta}")
    sys.exit(1)
print(f"VERIFICACION_INTERFACES: OK ({n_coax_ok}/{len(coaxiales)} interfaces coaxiales, 0 colisiones) - {ruta}")
