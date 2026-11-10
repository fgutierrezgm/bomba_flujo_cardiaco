# validar_fcstd.py
# Uso (sin interfaz):  FCSTD=ruta/pieza.FCStd freecadcmd _herramientas/validar_fcstd.py
# Salida: líneas INFO/AVISO/ERROR y una línea final "VALIDACION: OK" o "VALIDACION: FALLIDA".
import os
import sys
import FreeCAD as App


def ruta_a_validar():
    ruta = os.environ.get("FCSTD")
    if ruta:
        return ruta
    cands = [a for a in sys.argv if a.lower().endswith(".fcstd")]
    return cands[-1] if cands else None


def tiene_forma(o):
    return o.isDerivedFrom("Part::Feature") and not o.isDerivedFrom("Part::Datum")


def celdas_de(hoja):
    return hoja.getNonEmptyCells() if hasattr(hoja, "getNonEmptyCells") else hoja.getUsedCells()


def validar(ruta):
    errores, avisos = [], []
    try:
        doc = App.openDocument(ruta)
        doc.recompute()
    except Exception as e:
        return [f"No se pudo abrir/recalcular el documento: {e}"], avisos

    # 1. Objetos que fallaron al recalcular (incluye ciclos y expresiones rotas)
    for o in doc.Objects:
        if not o.isValid() or "Invalid" in o.State:
            errores.append(f"{o.Name} ({o.Label}): {o.getStatusString()}")

    # 2. Celdas de hoja con error (#NAME?, #CIRCULAR, etc.)
    hojas = [o for o in doc.Objects if o.TypeId == "Spreadsheet::Sheet"]
    for h in hojas:
        for c in celdas_de(h):
            try:
                h.get(c)
            except Exception as e:
                errores.append(f"Hoja {h.Label}, celda {c}: {e}")

    links = [o for o in doc.Objects if o.TypeId == "App::Link"]
    asm_nativo = next((o for o in doc.Objects if o.isDerivedFrom("Assembly::AssemblyObject")), None)
    pg = next((h for h in hojas if h.Label == "Parametros_Generales"), None)

    # --- MODO ENSAMBLAJE DE VÍNCULOS (App::Link o Assembly::AssemblyObject) ---
    if links:
        if asm_nativo is not None:
            try:
                res_s = asm_nativo.solve()
                if res_s != 0:
                    errores.append(f"El solver de Assembly::AssemblyObject devolvió código {res_s} (!= 0)")
            except Exception as e:
                errores.append(f"Error al ejecutar solve() en Assembly::AssemblyObject: {e}")
        else:
            if pg is None:
                errores.append("Falta la hoja 'Parametros_Generales' en el ensamblaje")
            else:
                if pg.getCellFromAlias("explosion") != "B2":
                    errores.append("El alias 'explosion' debe estar en la celda B2 de 'Parametros_Generales'")
                for c in celdas_de(pg):
                    if c.startswith("F"):
                        try:
                            if str(pg.get(c)).strip().lower() == "supuesto":
                                fila = c[1:]
                                avisos.append(f"Parámetro SUPUESTO sin confirmar: {pg.get('A' + fila)} (fila {fila})")
                        except Exception:
                            pass

            bom = next((h for h in hojas if h.Label == "Lista_de_Materiales"), None)
            if bom is None:
                errores.append("Falta la hoja 'Lista_de_Materiales' en el ensamblaje")

        links_validos = 0
        for lnk in links:
            if lnk.LinkedObject is None:
                errores.append(f"App::Link '{lnk.Name}' ({lnk.Label}) tiene LinkedObject = None")
            else:
                links_validos += 1
        tipo_ens = "Assembly::AssemblyObject" if asm_nativo is not None else "App::Link"
        print(f"INFO Ensamblaje {tipo_ens}: {links_validos}/{len(links)} instancias vinculadas válidas")
        return errores, avisos

    # --- MODO PIEZA INDIVIDUAL (Pieza) ---
    # 3. Reglas sobre la hoja Parametros
    param = next((h for h in hojas if h.Label in ("Parametros", "Parametros_Generales")), None)
    if param is None:
        errores.append("Falta la hoja 'Parametros' (o 'Parametros_Generales')")
    else:
        if param.getCellFromAlias("modo_diseno") != "B2":
            errores.append("El alias 'modo_diseno' debe estar en la celda B2 de 'Parametros'")
        if any(tiene_forma(o) for o in param.OutList):
            errores.append("'Parametros' lee propiedades de un sólido (riesgo de ciclo DAG): "
                           "mover ese cálculo a 'Reporte_Fisico'")
        for c in celdas_de(param):                     # columna F = ORIGEN
            if c.startswith("F"):
                try:
                    if str(param.get(c)).strip().lower() == "supuesto":
                        fila = c[1:]
                        avisos.append(f"Parámetro SUPUESTO sin confirmar: {param.get('A' + fila)} (fila {fila})")
                except Exception:
                    pass

    # 4. Sólido(s) final(es): objetos con forma que ningún otro objeto con forma consume
    finales = [o for o in doc.Objects
               if tiene_forma(o) and not o.Shape.isNull()
               and not any(tiene_forma(p) for p in o.InList)]
    buenos = []
    for o in finales:
        s = o.Shape
        if not s.Solids:
            avisos.append(f"{o.Name}: sin sólidos (¿boceto o superficie suelta?)")
        elif not s.isValid() or s.Volume <= 0:
            errores.append(f"{o.Name}: sólido inválido o de volumen <= 0")
        else:
            buenos.append(o)
            print(f"INFO {o.Name}: volumen = {s.Volume:.1f} mm3, sólidos = {len(s.Solids)}")
            if len(s.Solids) > 1:
                avisos.append(f"{o.Name}: la pieza quedó partida en {len(s.Solids)} sólidos")
    if not buenos:
        errores.append("No hay ningún sólido final válido")

    # 4b. Verificar que auxiliares (Part::Datum o sólidos intermedios consumidos) estén ocultos
    for o in doc.Objects:
        if o.isDerivedFrom("Part::Datum") and getattr(o, "Visibility", False):
            avisos.append(f"Objeto auxiliar Datum '{o.Name}' quedó con Visibility == True")
        elif tiene_forma(o) and o not in finales and getattr(o, "Visibility", False):
            avisos.append(f"Sólido intermedio '{o.Name}' quedó con Visibility == True")

    # 5. Conectores LCS y contención en App::Part
    if not [o for o in doc.Objects if o.TypeId == "PartDesign::CoordinateSystem"
            and o.Label.startswith("LCS_")]:
        errores.append("No hay conectores LCS_* en la pieza")
    for o in doc.Objects:
        if o.TypeId != "App::Part" and o.getParentGeoFeatureGroup() is None:
            avisos.append(f"{o.Name} está fuera de cualquier App::Part")
    return errores, avisos


ruta = ruta_a_validar()
if not ruta or not os.path.exists(ruta):
    print("Uso: FCSTD=archivo.FCStd freecadcmd validar_fcstd.py   (archivo no encontrado)")
    codigo = 2
else:
    errs, avs = validar(ruta)
    for a in avs:
        print("AVISO:", a)
    for e in errs:
        print("ERROR:", e)
    codigo = 1 if errs else 0
    print("VALIDACION: OK" if codigo == 0 else "VALIDACION: FALLIDA", "-", ruta)

sys.stdout.flush()
if not App.GuiUp:
    os._exit(codigo)   # freecadcmd no siempre propaga sys.exit(); así sí
