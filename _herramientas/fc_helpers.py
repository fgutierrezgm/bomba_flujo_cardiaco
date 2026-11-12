# fc_helpers.py - utilidades comunes para generar piezas paramétricas en FreeCAD.
# Cada script de pieza hace:  from fc_helpers import Pieza
import FreeCAD as App

ORIGENES = ("plano", "usuario", "norma", "calculado", "supuesto")

# Biblioteca base de materiales físicos y apariencias visuales
MATERIALES_BASE = {
    "Acero_Inoxidable": {
        "nombre": "Acero Inoxidable AISI 304/316L",
        "densidad_num": "0.00000790",
        "densidad_desc": "7.90 g / cm^3 (kg / mm^3)",
        "color": (0.75, 0.76, 0.78),
        "transparencia": 0,
    },
    "Acero_Inox_430": {
        "nombre": "Acero Inoxidable Ferrítico AISI 430 (Ferromagnético)",
        "densidad_num": "0.00000770",
        "densidad_desc": "7.70 g / cm^3 (kg / mm^3)",
        "color": (0.70, 0.72, 0.75),
        "transparencia": 0,
    },
    "Delrin": {
        "nombre": "Delrin POM-C",
        "densidad_num": "0.00000141",
        "densidad_desc": "1.41 g / cm^3 (kg / mm^3)",
        "color": (0.15, 0.15, 0.15),
        "transparencia": 0,
    },
    "Vidrio_Borosilicato": {
        "nombre": "Vidrio Borosilicato",
        "densidad_num": "0.00000223",
        "densidad_desc": "2.23 g / cm^3 (kg / mm^3)",
        "color": (0.85, 0.95, 1.00),
        "transparencia": 75,
    },
    "Vidrio_Sodocalcico": {
        "nombre": "Vidrio Sodocálcico",
        "densidad_num": "0.00000250",
        "densidad_desc": "2.50 g / cm^3 (kg / mm^3)",
        "color": (0.80, 0.90, 0.88),
        "transparencia": 80,
    },
    "Laton": {
        "nombre": "Latón",
        "densidad_num": "0.00000850",
        "densidad_desc": "8.50 g / cm^3 (kg / mm^3)",
        "color": (0.85, 0.65, 0.20),
        "transparencia": 0,
    },
    "Aluminio": {
        "nombre": "Aluminio 6061",
        "densidad_num": "0.00000270",
        "densidad_desc": "2.70 g / cm^3 (kg / mm^3)",
        "color": (0.82, 0.82, 0.84),
        "transparencia": 0,
    },
    "PVC_Rigido": {
        "nombre": "PVC Rígido",
        "densidad_num": "0.00000140",
        "densidad_desc": "1.40 g / cm^3 (kg / mm^3)",
        "color": (0.35, 0.40, 0.45),
        "transparencia": 0,
    },
    "Caucho_NBR": {
        "nombre": "Elastómero NBR / Viton (FKM)",
        "densidad_num": "0.00000125",
        "densidad_desc": "1.25 g / cm^3 (kg / mm^3)",
        "color": (0.12, 0.12, 0.14),
        "transparencia": 0,
    },
    "Bronce": {
        "nombre": "Bronce Sinterizado SAE 841 / DIN 1850",
        "densidad_num": "0.00000680",
        "densidad_desc": "6.80 g / cm^3 (kg / mm^3)",
        "color": (0.76, 0.52, 0.22),
        "transparencia": 0,
    },
    "PLA_Estructural": {
        "nombre": "PLA+ / PETG Estructural (Impresión 3D)",
        "densidad_num": "0.00000124",
        "densidad_desc": "1.24 g / cm^3 (kg / mm^3)",
        "color": (0.20, 0.48, 0.75),
        "transparencia": 0,
    },
    "Acrilico_PMMA": {
        "nombre": "Acrílico Transparente PMMA",
        "densidad_num": "0.00000119",
        "densidad_desc": "1.19 g / cm^3 (kg / mm^3)",
        "color": (0.78, 0.92, 0.98),
        "transparencia": 75,
    },
    "Acero_1045": {
        "nombre": "Acero SAE 1045",
        "densidad_num": "0.00000785",
        "densidad_desc": "7.85 g / cm^3 (kg / mm^3)",
        "color": (0.50, 0.52, 0.56),
        "transparencia": 0,
    },
    "AISI_304": {
        "nombre": "Acero Inoxidable AISI 304/316L",
        "densidad_num": "0.00000790",
        "densidad_desc": "7.90 g / cm^3 (kg / mm^3)",
        "color": (0.76, 0.78, 0.80),
        "transparencia": 0,
    },
    "AISI_430": {
        "nombre": "Acero Inoxidable Ferrítico AISI 430 (Ferromagnético)",
        "densidad_num": "0.00000770",
        "densidad_desc": "7.70 g / cm^3 (kg / mm^3)",
        "color": (0.65, 0.68, 0.72),
        "transparencia": 0,
    },
}

# tipo de parámetro -> fórmula de la columna B (valor efectivo). D = nominal, E = mecha
#   L lineal (escala) | H hueco, diámetro (+holgura) | S saliente, diámetro (-holgura)
#   R rosca (nominal; mecha en Modo 2; sin escala ni holgura) | N sin transformar (ángulos, conteos)
FORMULA = {
    "L": "=D{r} * esc",
    "H": "=D{r} * esc + holgura * 2",
    "S": "=D{r} * esc - holgura * 2",
    "R": "=modo_diseno == 2 ? E{r} : D{r}",
    "N": "=D{r}",
}


def _q_val(val_str):
    """Extrae el valor numérico flotante de una cantidad FreeCAD (p. ej. '15.00 mm' -> 15.0)."""
    if val_str is None:
        return None
    s = str(val_str).strip().lstrip("=")
    if not s:
        return None
    try:
        return float(App.Units.Quantity(s).Value)
    except Exception:
        try:
            return float(s)
        except Exception:
            return s


def _q_diff(a, b, tol=1e-4):
    """Devuelve True si dos cantidades difieren numéricamente más que tol."""
    va, vb = _q_val(a), _q_val(b)
    if isinstance(va, float) and isinstance(vb, float):
        return abs(va - vb) > tol
    return str(a).strip() != str(b).strip()


def _formatear_cantidad(val_prev, plantilla_nominal):
    """Formatea un valor leído de Spreadsheet conservando la unidad del nominal original."""
    s_prev = str(val_prev).strip().lstrip("=")
    v_num = _q_val(s_prev)
    if not isinstance(v_num, float):
        return s_prev
    s_nom = str(plantilla_nominal).strip()
    if "deg" in s_nom:
        return f"{v_num:g} deg"
    if "mm" in s_nom:
        return f"{v_num:.2f} mm"
    return f"{v_num:g}"


class Pieza:
    def __init__(self, nombre, ruta_salida=None, ruta_script=None):
        import os
        import sys
        print("FreeCAD", ".".join(App.Version()[:3]))
        self.nombre = nombre

        # Descubrir automáticamente SALIDA y __file__ del script llamador si no se pasan
        caller_globals = {}
        try:
            caller_globals = sys._getframe(1).f_globals
        except Exception:
            pass
        self.ruta_salida = ruta_salida or caller_globals.get("SALIDA")
        self.ruta_script = ruta_script or caller_globals.get("__file__")
        if self.ruta_salida:
            self.ruta_salida = os.path.abspath(self.ruta_salida)
        if self.ruta_script and os.path.exists(str(self.ruta_script)):
            self.ruta_script = os.path.abspath(self.ruta_script)
        else:
            self.ruta_script = None

        # Limpiar snapshots en memoria de macros (Movimiento Libre / Aislar) para no inyectar expresiones viejas
        for prefijo_macro in ("_mov_libre_", "_aislado_"):
            attr_m = f"{prefijo_macro}{nombre}"
            if hasattr(App, attr_m):
                delattr(App, attr_m)

        # Guardia anti-pisado: inspeccionar documento previo (en memoria o en disco) ANTES de cerrarlo
        self._estado_prev = self._capturar_estado_previo()
        self._verificar_operaciones_manuales_arbol()

        if nombre in App.listDocuments():
            self.doc = App.getDocument(nombre)
            self.part = self.doc.getObject(nombre)
            if self.part is None:
                self.part = self.doc.addObject("App::Part", nombre)
            # Limpiar objetos internos previos sin destruir self.doc ni self.part (evita punteros colgantes en App::Link)
            for o in list(self.doc.Objects):
                if o == self.part or o.TypeId in ("App::Origin", "App::Plane", "App::Line"):
                    continue
                try:
                    self.doc.removeObject(o.Name)
                except Exception:
                    pass
        else:
            self.doc = App.newDocument(nombre)
            self.part = self.doc.addObject("App::Part", nombre)
        self.hoja = None
        self.hoja_mat = None
        self.filas_actuales = []
        self.cabecera_actual = {}
        self.auxiliares = []      # herramientas y fusiones intermedias (se ocultan en la GUI)

    def _capturar_estado_previo(self):
        """Lee parámetros y objetos del documento existente (en GUI o en disco) antes de regenerar."""
        import json
        import os
        estado = {"manifiesto": None, "parametros": {}, "cabecera": {}, "objetos": {}}
        doc_prev = None
        cerrar_temp = False

        if self.nombre in App.listDocuments():
            doc_prev = App.getDocument(self.nombre)
        elif self.ruta_salida and os.path.exists(self.ruta_salida):
            try:
                doc_prev = App.openDocument(self.ruta_salida, True)
                cerrar_temp = True
            except Exception:
                doc_prev = None

        if doc_prev is None:
            return estado

        try:
            part_prev = doc_prev.getObject(self.nombre)
            if part_prev and hasattr(part_prev, "Manifiesto_Script"):
                raw_m = getattr(part_prev, "Manifiesto_Script", "")
                if raw_m:
                    estado["manifiesto"] = json.loads(raw_m)

            ss = doc_prev.getObject("Parametros")
            if ss:
                for clave, celda in (("modo_diseno", "B2"), ("escala", "B3"), ("holgura_fdm", "B4")):
                    try:
                        estado["cabecera"][clave] = str(ss.get(celda))
                    except Exception:
                        pass
                r = 7
                while True:
                    try:
                        alias = ss.get(f"A{r}")
                    except Exception:
                        break
                    if not alias:
                        break
                    alias_s = str(alias).strip()
                    try:
                        nom_val = str(ss.get(f"D{r}"))
                    except Exception:
                        nom_val = ""
                    try:
                        mecha_val = str(ss.get(f"E{r}"))
                    except Exception:
                        mecha_val = None
                    try:
                        orig_val = str(ss.get(f"F{r}")).strip()
                    except Exception:
                        orig_val = "plano"
                    estado["parametros"][alias_s] = {
                        "nominal": nom_val,
                        "mecha": mecha_val,
                        "origen": orig_val,
                        "fila": r,
                    }
                    r += 1

            for o in doc_prev.Objects:
                if o.TypeId in ("App::Origin", "App::Plane", "App::Line"):
                    continue
                plc = None
                if hasattr(o, "Placement"):
                    b = o.Placement.Base
                    rot = o.Placement.Rotation.Q
                    plc = [round(b.x, 4), round(b.y, 4), round(b.z, 4),
                           round(rot[0], 4), round(rot[1], 4), round(rot[2], 4), round(rot[3], 4)]
                exprs = {}
                if hasattr(o, "ExpressionEngine"):
                    exprs = {k: v for k, v in o.ExpressionEngine}
                estado["objetos"][o.Name] = {
                    "TypeId": o.TypeId,
                    "Label": o.Label,
                    "Placement": plc,
                    "Expresiones": exprs,
                }
        except Exception:
            pass
        finally:
            if cerrar_temp and doc_prev:
                try:
                    App.closeDocument(doc_prev.Name)
                except Exception:
                    pass
        return estado

    def _verificar_operaciones_manuales_arbol(self):
        """Si hay objetos nuevos o expresiones/posiciones editadas a mano en el árbol, detiene la regeneración."""
        import os
        if os.environ.get("FORZAR") == "1":
            return
        manif = self._estado_prev.get("manifiesto")
        if not manif:
            return
        objs_manif = manif.get("objetos", {})
        objs_prev = self._estado_prev.get("objetos", {})

        # ¿Cambió algún parámetro en la hoja Parametros respecto del manifiesto?
        params_manif = manif.get("parametros", {})
        params_prev = self._estado_prev.get("parametros", {})
        hubo_cambio_param = any(
            alias in params_manif and _q_diff(info["nominal"], params_manif[alias].get("nominal"))
            for alias, info in params_prev.items()
        )

        nuevos = [
            f"{nombre_obj} ({info['TypeId']}, Label='{info['Label']}')"
            for nombre_obj, info in objs_prev.items()
            if nombre_obj not in objs_manif
        ]
        modificados = []
        for nombre_obj, info in objs_prev.items():
            if nombre_obj not in objs_manif:
                continue
            m_info = objs_manif[nombre_obj]
            if info["Expresiones"] != m_info.get("Expresiones", {}):
                modificados.append(
                    f"{nombre_obj}: expresiones cambiaron de {m_info.get('Expresiones')} a {info['Expresiones']}"
                )
            elif not hubo_cambio_param and info["Placement"] != m_info.get("Placement"):
                modificados.append(
                    f"{nombre_obj}: Placement cambió manualmente de {m_info.get('Placement')} a {info['Placement']}"
                )

        if nuevos or modificados:
            lineas = [
                f"[GUARDIA ANTI-PISADO] Se abortó la regeneración de '{self.nombre}' para no perder cambios manuales en el árbol:"
            ]
            if nuevos:
                lineas.append("  - Objetos agregados manualmente: " + ", ".join(nuevos))
            if modificados:
                for m in modificados:
                    lineas.append("  - " + m)
            lineas.append("  -> Pasa estos cambios al script .py antes de regenerar, o ejecuta con FORZAR=1.")
            raise RuntimeError("\n".join(lineas))

    def _sincronizar_parametros_con_script(self, filas):
        """Si el usuario editó valores en la hoja Parametros del .FCStd, actualiza filas y el archivo .py."""
        import os
        import re
        if os.environ.get("FORZAR") == "1":
            return list(filas)
        params_prev = self._estado_prev.get("parametros", {})
        if not params_prev:
            return list(filas)
        manif = self._estado_prev.get("manifiesto")
        params_manif = manif.get("parametros", {}) if manif else {}

        filas_nuevas = []
        cambios_script = []
        for item in filas:
            alias, desc, nominal, tipo, mecha, origen = item
            if alias in params_prev:
                p_prev = params_prev[alias]
                editado_en_fcstd = False
                if alias in params_manif:
                    if _q_diff(p_prev["nominal"], params_manif[alias].get("nominal")):
                        editado_en_fcstd = True
                    elif mecha and p_prev.get("mecha") and _q_diff(p_prev["mecha"], params_manif[alias].get("mecha")):
                        editado_en_fcstd = True
                elif p_prev.get("origen") == "usuario" and _q_diff(p_prev["nominal"], nominal):
                    editado_en_fcstd = True

                if editado_en_fcstd and _q_diff(p_prev["nominal"], nominal):
                    nuevo_nom = _formatear_cantidad(p_prev["nominal"], nominal)
                    nueva_mecha = (
                        _formatear_cantidad(p_prev["mecha"], mecha)
                        if (mecha and p_prev.get("mecha"))
                        else mecha
                    )
                    cambios_script.append((alias, nominal, nuevo_nom, origen))
                    filas_nuevas.append((alias, desc, nuevo_nom, tipo, nueva_mecha, "usuario"))
                    continue
            filas_nuevas.append(item)

        if cambios_script and self.ruta_script and os.path.exists(self.ruta_script):
            try:
                with open(self.ruta_script, "r", encoding="utf-8") as f:
                    texto = f.read()
                for alias, nom_viejo, nom_nuevo, orig_viejo in cambios_script:
                    patron = rf'(\(\s*"{re.escape(alias)}"\s*,\s*"[^"]*"\s*,\s*"){re.escape(nom_viejo)}(".*?)"{re.escape(orig_viejo)}"(\s*\)\s*,?)'
                    reemplazo = (
                        rf'\g<1>{nom_nuevo}\g<2>"usuario"\g<3>  # sync desde .FCStd (antes: {nom_viejo})'
                    )
                    texto_nuevo, n_sub = re.subn(patron, reemplazo, texto, count=1)
                    if n_sub > 0:
                        texto = texto_nuevo
                    print(
                        f"[GUARDIA ANTI-PISADO] Sincronizado '{alias}' desde .FCStd -> {os.path.basename(self.ruta_script)}: "
                        f"{nom_viejo} -> {nom_nuevo} (origen: usuario)"
                    )
                with open(self.ruta_script, "w", encoding="utf-8") as f:
                    f.write(texto)
            except Exception as e:
                print(f"[GUARDIA ANTI-PISADO] Aviso al escribir {self.ruta_script}: {e}")

        return filas_nuevas

    def _guardar_manifiesto(self):
        """Guarda en el App::Part el manifiesto JSON de parámetros y objetos generados por el script."""
        import json
        manifiesto = {
            "cabecera": self.cabecera_actual,
            "parametros": {
                alias: {"nominal": nominal, "mecha": mecha, "origen": origen}
                for (alias, _desc, nominal, _tipo, mecha, origen) in self.filas_actuales
            },
            "objetos": {},
        }
        for o in self.doc.Objects:
            if o.TypeId in ("App::Origin", "App::Plane", "App::Line"):
                continue
            plc = None
            if hasattr(o, "Placement"):
                b = o.Placement.Base
                rot = o.Placement.Rotation.Q
                plc = [round(b.x, 4), round(b.y, 4), round(b.z, 4),
                       round(rot[0], 4), round(rot[1], 4), round(rot[2], 4), round(rot[3], 4)]
            exprs = {}
            if hasattr(o, "ExpressionEngine"):
                exprs = {k: v for k, v in o.ExpressionEngine}
            manifiesto["objetos"][o.Name] = {
                "TypeId": o.TypeId,
                "Label": o.Label,
                "Placement": plc,
                "Expresiones": exprs,
            }
        if not hasattr(self.part, "Manifiesto_Script"):
            self.part.addProperty(
                "App::PropertyString", "Manifiesto_Script", "_Control_IA",
                "Manifiesto JSON para la guardia anti-pisado", 4
            )
        self.part.Manifiesto_Script = json.dumps(manifiesto, ensure_ascii=False)

    # -- utilidades de expresiones -------------------------------------------
    def p(self, alias):
        """Referencia a un alias de la hoja Parametros, para usar dentro de expresiones."""
        return f"<<Parametros>>.{alias}"

    def nuevo(self, tipo, nombre):
        """Crea el objeto DENTRO del App::Part (evita 'Links go out of the allowed scope')."""
        return self.part.newObject(tipo, nombre)

    # -- hoja de parámetros ---------------------------------------------------
    def parametros(self, filas, modo=2, escala="1.0", holgura_fdm="0.20 mm"):
        """filas: (alias, descripción, nominal, tipo, mecha|None, origen)."""
        filas_sync = self._sincronizar_parametros_con_script(filas)
        self.filas_actuales = list(filas_sync)
        self.cabecera_actual = {
            "modo_diseno": str(modo),
            "escala": str(escala),
            "holgura_fdm": str(holgura_fdm),
        }
        ss = self.hoja = self.nuevo("Spreadsheet::Sheet", "Parametros")
        for celda, txt in (("A1", "PARÁMETRO"), ("B1", "VALOR EFECTIVO"), ("C1", "DESCRIPCIÓN"),
                           ("D1", "NOMINAL"), ("E1", "MECHA (solo Modo 2)"), ("F1", "ORIGEN")):
            ss.set(celda, txt)
        # Cabecera de control (el orden importa: cada alias debe existir antes de usarse)
        ss.set("A2", "Modo de diseño"); ss.set("B2", str(modo)); ss.setAlias("B2", "modo_diseno")
        ss.set("C2", "1 = Impresión 3D | 2 = CNC y Planos | 3 = Render")
        ss.set("A3", "Escala"); ss.set("B3", escala); ss.setAlias("B3", "escala")
        ss.set("C3", "Factor de escala (solo se aplica en Modo 1)")
        ss.set("A4", "Holgura FDM"); ss.set("B4", holgura_fdm); ss.setAlias("B4", "holgura_fdm")
        ss.set("C4", "Holgura configurada de la impresora")
        ss.set("A5", "Escala efectiva"); ss.set("B5", "=modo_diseno == 1 ? escala : 1")
        ss.setAlias("B5", "esc")
        ss.set("A6", "Holgura efectiva"); ss.set("B6", "=modo_diseno == 1 ? holgura_fdm : 0 mm")
        ss.setAlias("B6", "holgura"); ss.set("C6", "0 fuera del Modo 1")
        for r, (alias, desc, nominal, tipo, mecha, origen) in enumerate(filas_sync, start=7):
            if origen not in ORIGENES:
                raise ValueError(f"{alias}: origen '{origen}' inválido, usar {ORIGENES}")
            ss.set(f"A{r}", alias)
            ss.set(f"C{r}", desc)
            ss.set(f"D{r}", nominal)
            if mecha:
                ss.set(f"E{r}", mecha)
            ss.set(f"F{r}", origen)
            ss.set(f"B{r}", FORMULA[tipo].format(r=r))
            ss.setAlias(f"B{r}", alias)
            if origen == "supuesto":              # resaltar lo que NO sale del plano/usuario
                try:
                    ss.setBackground(f"A{r}:F{r}", (1.0, 0.85, 0.4, 1.0))
                except Exception:
                    pass
        self.doc.recompute()                      # alias vivos ANTES de vincular el 3D
        return ss

    def materiales(self, clave_o_dict, origen="norma"):
        """Crea y configura la hoja 'Materiales' con propiedades físicas y de apariencia."""
        if isinstance(clave_o_dict, str):
            info = MATERIALES_BASE.get(clave_o_dict, {
                "nombre": clave_o_dict,
                "densidad_num": "0.00000785",
                "densidad_desc": "7.85 g / cm^3",
                "color": (0.75, 0.75, 0.75),
                "transparencia": 0,
            })
        else:
            info = clave_o_dict

        ss = self.hoja_mat = self.nuevo("Spreadsheet::Sheet", "Materiales")
        for celda, txt in (("A1", "PROPIEDAD"), ("B1", "VALOR"), ("C1", "DESCRIPCIÓN"), ("D1", "ORIGEN")):
            ss.set(celda, txt)

        ss.set("A2", "Material"); ss.set("B2", str(info["nombre"])); ss.setAlias("B2", "material_nombre")
        ss.set("C2", "Denominación del material"); ss.set("D2", origen)

        dens_num = info.get("densidad_num", "0.00000785")
        dens_desc = info.get("densidad_desc", f"{dens_num} kg / mm^3")
        ss.set("A3", "Densidad"); ss.set("B3", f"={dens_num}"); ss.setAlias("B3", "densidad_mat")
        ss.set("C3", str(dens_desc)); ss.set("D3", origen)

        c = info.get("color", (0.75, 0.75, 0.75))
        ss.set("A4", "Color_R"); ss.set("B4", f"={c[0]:.3f}"); ss.setAlias("B4", "color_r")
        ss.set("A5", "Color_G"); ss.set("B5", f"={c[1]:.3f}"); ss.setAlias("B5", "color_g")
        ss.set("A6", "Color_B"); ss.set("B6", f"={c[2]:.3f}"); ss.setAlias("B6", "color_b")

        t = info.get("transparencia", 0)
        ss.set("A7", "Transparencia"); ss.set("B7", f"={t}"); ss.setAlias("B7", "transparencia_mat")
        ss.set("C7", "0 a 100%"); ss.set("D7", origen)

        ss.set("A8", "Personalizado"); ss.set("B8", "=0"); ss.setAlias("B8", "apariencia_personalizada")
        ss.set("C8", "1 si el usuario modificó la apariencia en la GUI"); ss.set("D8", "calculado")

        mat_obj = self.nuevo("App::MaterialObjectPython", "Material_Propiedades")
        mat_obj.Material = {
            "Name": str(info["nombre"]),
            "Density": f"{dens_num} kg/mm^3",
            "DiffuseColor": f"({c[0]}, {c[1]}, {c[2]}, 1)",
            "Transparency": str(t),
        }
        self.auxiliares.append(mat_obj)
        self.doc.recompute()
        return ss

    # -- geometría ------------------------------------------------------------
    def cil(self, nombre, radio, altura, x=None, y=None, z=None):
        c = self.nuevo("Part::Cylinder", nombre)
        c.setExpression("Radius", radio)
        c.setExpression("Height", altura)
        for eje, expr in (("x", x), ("y", y), ("z", z)):
            if expr is not None:
                c.setExpression(f".Placement.Base.{eje}", expr)
        self.auxiliares.append(c)
        return c

    def cono(self, nombre, r1, r2, altura, x=None, y=None, z=None):
        c = self.nuevo("Part::Cone", nombre)
        c.setExpression("Radius1", r1)
        c.setExpression("Radius2", r2)
        c.setExpression("Height", altura)
        for eje, expr in (("x", x), ("y", y), ("z", z)):
            if expr is not None:
                c.setExpression(f".Placement.Base.{eje}", expr)
        self.auxiliares.append(c)
        return c

    def caja(self, nombre, largo, ancho, alto, x=None, y=None, z=None):
        b = self.nuevo("Part::Box", nombre)
        b.setExpression("Length", largo)
        b.setExpression("Width", ancho)
        b.setExpression("Height", alto)
        for eje, expr in (("x", x), ("y", y), ("z", z)):
            if expr is not None:
                b.setExpression(f".Placement.Base.{eje}", expr)
        self.auxiliares.append(b)
        return b

    def cil_x(self, nombre, radio, largo, x=None, y=None, z=None):
        """Cilindro con eje a lo largo de +X (para pasadores o agujeros transversales)."""
        c = self.cil(nombre, radio, largo, x=x, y=y, z=z)
        c.Placement.Rotation = App.Rotation(App.Vector(0, 1, 0), 90)
        return c

    def fusion(self, nombre, objetos):
        f = self.nuevo("Part::MultiFuse", nombre)
        f.Shapes, f.Refine = list(objetos), True
        self.auxiliares.append(f)
        return f

    def corte(self, nombre, base, herramienta):
        c = self.nuevo("Part::Cut", nombre)
        c.Base, c.Tool, c.Refine = base, herramienta, True
        self.auxiliares.append(c)
        return c

    def lcs(self, nombre, x=None, y=None, z=None, visible=False):
        o = self.nuevo("PartDesign::CoordinateSystem", nombre)
        for eje, expr in (("x", x), ("y", y), ("z", z)):
            if expr is not None:
                o.setExpression(f".Placement.Base.{eje}", expr)
        o.Visibility = visible                    # oculto por defecto en el 3D
        return o

    # -- reporte y cierre -----------------------------------------------------
    def reporte_fisico(self, solido, materiales=None):
        """Genera la hoja Reporte_Fisico calculando volumen y masa sin riesgo de ciclos DAG."""
        rep = self.nuevo("Spreadsheet::Sheet", "Reporte_Fisico")
        rep.set("A1", "PROPIEDAD"); rep.set("B1", "VALOR")
        rep.set("A2", "Volumen (mm^3)"); rep.set("B2", f"={solido.Name}.Shape.Volume")
        fila = 3
        if self.hoja_mat:
            rep.set(f"A{fila}", "Masa nominal (kg)")
            rep.set(f"B{fila}", f"={solido.Name}.Shape.Volume * <<Materiales>>.densidad_mat * 1 kg")
            fila += 1
        if materiales:
            for nombre, dens in materiales.items():
                rep.set(f"A{fila}", nombre)
                rep.set(f"B{fila}", f"={solido.Name}.Shape.Volume * {dens}")
                fila += 1
        return rep

    def cerrar(self, solido, ruta):
        import os
        # 1. Preservación automática de apariencia personalizada de archivo previo
        es_personalizado = False
        r_col, g_col, b_col, transp = None, None, None, None

        if os.path.exists(ruta):
            try:
                doc_prev = App.openDocument(ruta, True)
                mat_prev = doc_prev.getObject("Materiales")
                if mat_prev:
                    try:
                        p_val = float(mat_prev.get("apariencia_personalizada"))
                        if p_val > 0.5:
                            r_col = float(mat_prev.get("color_r"))
                            g_col = float(mat_prev.get("color_g"))
                            b_col = float(mat_prev.get("color_b"))
                            transp = float(mat_prev.get("transparencia_mat"))
                            es_personalizado = True
                    except Exception:
                        pass
                sol_prev = doc_prev.getObject(solido.Name)
                if not es_personalizado and sol_prev and hasattr(sol_prev, "ViewObject") and sol_prev.ViewObject:
                    sc = getattr(sol_prev.ViewObject, "ShapeColor", None)
                    tr = getattr(sol_prev.ViewObject, "Transparency", None)
                    # Ignorar el gris por defecto de FreeCAD (0.447, 0.475, 0.502) cuando el archivo se guardó sin GUI
                    es_gris_fc = sc and (abs(sc[0] - 0.447) < 0.02 and abs(sc[1] - 0.475) < 0.02 and abs(sc[2] - 0.502) < 0.02)
                    if sc and not es_gris_fc and self.hoja_mat:
                        def_r = float(self.hoja_mat.get("color_r"))
                        def_g = float(self.hoja_mat.get("color_g"))
                        def_b = float(self.hoja_mat.get("color_b"))
                        def_tr = float(self.hoja_mat.get("transparencia_mat"))
                        if (abs(sc[0] - def_r) > 0.01 or abs(sc[1] - def_g) > 0.01 or
                            abs(sc[2] - def_b) > 0.01 or abs(tr - def_tr) > 1):
                            r_col, g_col, b_col = sc[0], sc[1], sc[2]
                            transp = tr
                            es_personalizado = True
                App.closeDocument(doc_prev.Name)
            except Exception:
                pass

        if es_personalizado and self.hoja_mat:
            self.hoja_mat.set("B4", f"{r_col:.3f}")
            self.hoja_mat.set("B5", f"{g_col:.3f}")
            self.hoja_mat.set("B6", f"{b_col:.3f}")
            self.hoja_mat.set("B7", f"{transp:.1f}")
            self.hoja_mat.set("B8", "1")

        # 2. Aplicar apariencia al objeto nativo y ViewObject
        if self.hoja_mat:
            try:
                r = float(self.hoja_mat.get("color_r"))
                g = float(self.hoja_mat.get("color_g"))
                b = float(self.hoja_mat.get("color_b"))
                t = int(float(self.hoja_mat.get("transparencia_mat")))

                mat_obj = self.doc.getObject("Material_Propiedades")
                if mat_obj:
                    d = dict(mat_obj.Material)
                    d["DiffuseColor"] = f"({r}, {g}, {b}, 1)"
                    d["Transparency"] = str(t)
                    mat_obj.Material = d

                if App.GuiUp and hasattr(solido, "ViewObject") and solido.ViewObject:
                    solido.ViewObject.ShapeColor = (r, g, b)
                    solido.ViewObject.Transparency = t
            except Exception:
                pass

        # 3. Ocultar auxiliares y orígenes ANTES de guardar (funciona también en freecadcmd)
        for o in self.auxiliares:
            o.Visibility = False
        for o in self.doc.Objects:
            if o.TypeId in ("App::Origin", "App::Plane", "App::Line") or o.isDerivedFrom("Part::Datum"):
                o.Visibility = False
        solido.Visibility = True
        self.part.Visibility = True

        self.doc.recompute()
        self._guardar_manifiesto()
        os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
        self.doc.saveAs(ruta)
        print("Guardado:", ruta)
        if App.GuiUp:
            import FreeCADGui as Gui
            if Gui.activeDocument() and Gui.activeDocument().activeView():
                Gui.activeDocument().activeView().viewIsometric()
                Gui.SendMsgToActiveView("ViewFit")


class Ensamblaje:
    def __init__(self, nombre, ruta_salida, explosion_inicial="0.0"):
        import os
        print("FreeCAD", ".".join(App.Version()[:3]))
        self.nombre = nombre
        self.ruta = os.path.abspath(ruta_salida)
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)

        # 1. Preservar personalizaciones previas (colores, TRANSP_INSP, PERSONALIZADO)
        self.custom_prev = {}
        doc_previo = None
        cerrar_previo = False
        if nombre in App.listDocuments():
            doc_previo = App.getDocument(nombre)
        elif os.path.exists(self.ruta):
            try:
                doc_previo = App.openDocument(self.ruta, True)
                cerrar_previo = True
            except Exception:
                doc_previo = None

        if doc_previo:
            try:
                mg_prev = doc_previo.getObject("Materiales_Generales")
                if mg_prev:
                    r = 2
                    while True:
                        try:
                            inst = mg_prev.get(f"A{r}")
                        except Exception:
                            break
                        if not inst:
                            break
                        inst_str = str(inst)
                        try:
                            r_c = float(mg_prev.get(f"D{r}"))
                            g_c = float(mg_prev.get(f"E{r}"))
                            b_c = float(mg_prev.get(f"F{r}"))
                            tr_base = float(mg_prev.get(f"G{r}"))
                            tr_insp = float(mg_prev.get(f"H{r}"))
                            pers_flag = int(float(mg_prev.get(f"I{r}")))
                            if r_c > 1.0 or g_c > 1.0 or b_c > 1.0:
                                r_c, g_c, b_c = r_c / 255.0, g_c / 255.0, b_c / 255.0
                            r_c = max(0.0, min(1.0, r_c))
                            g_c = max(0.0, min(1.0, g_c))
                            b_c = max(0.0, min(1.0, b_c))
                            self.custom_prev[inst_str] = {
                                "color": (r_c, g_c, b_c),
                                "transp_base": tr_base,
                                "transp_insp": tr_insp,
                                "personalizado": (pers_flag == 1),
                            }
                        except Exception:
                            pass
                        r += 1
            except Exception:
                pass
            finally:
                if cerrar_previo and doc_previo:
                    App.closeDocument(doc_previo.Name)

        # Limpiar snapshots en memoria de macros (Movimiento Libre / Aislar) para no inyectar expresiones viejas
        for prefijo_macro in ("_mov_libre_", "_aislado_"):
            attr_m = f"{prefijo_macro}{nombre}"
            if hasattr(App, attr_m):
                delattr(App, attr_m)

        if nombre in App.listDocuments():
            self.doc = App.getDocument(nombre)
            self.asm = self.doc.getObject(nombre)
            if self.asm is None:
                self.asm = self.doc.addObject("App::Part", nombre)
            for o in list(self.doc.Objects):
                if o == self.asm or o.TypeId in ("App::Origin", "App::Plane", "App::Line"):
                    continue
                try:
                    self.doc.removeObject(o.Name)
                except Exception:
                    pass
        else:
            self.doc = App.newDocument(nombre)
            # Guardar antes de crear vínculos para que FreeCAD almacene rutas relativas en App::Link
            self.doc.saveAs(self.ruta)
            self.asm = self.doc.addObject("App::Part", nombre)
        self.pos_armadas = {}      # nombre_instancia -> Placement sin explotar
        self.conteo_bom = {}       # archivo -> [etiqueta, cantidad]
        self.componentes_inst = [] # metadatos de instancias para Materiales_Generales y Reporte_Fisico
        self.interfaces = []       # interfaces coaxiales declaradas para verificar_interfaces.py
        self.pares_rosca_ajuste = [] # pares (inst1, inst2) con interferencia intencional (rosca/ajuste)
        self.interferencias_plano = [] # interferencias del plano original documentadas en FICHA (AVISO)
        self.hoja = self._crear_hoja_maestra(explosion_inicial)

    def _crear_hoja_maestra(self, explosion_inicial):
        ss = self.asm.newObject("Spreadsheet::Sheet", "Parametros_Generales")
        ss.set("A1", "PARÁMETRO"); ss.set("B1", "VALOR"); ss.set("C1", "DESCRIPCIÓN"); ss.set("F1", "ORIGEN")
        ss.set("A2", "Factor de explosión"); ss.set("B2", str(explosion_inicial))
        ss.setAlias("B2", "explosion")
        ss.set("C2", "0.0 = Ensamblado | 1.0 = Vista Explotada (admite valores intermedios)")
        ss.set("F2", "usuario")
        ss.set("A3", "Modo de diseño global"); ss.set("B3", "3")
        ss.setAlias("B3", "modo_diseno_global")
        ss.set("C3", "1 = Impresión 3D | 2 = CNC/Planos | 3 = Render (sincroniza todas las piezas)")
        ss.set("F3", "usuario")
        self.doc.recompute()
        return ss

    def sincronizar_modo_diseno_piezas(self):
        try:
            val_raw = self.hoja.get("modo_diseno_global")
            if val_raw is None:
                return
            modo_global = int(float(str(val_raw).strip()))
        except Exception:
            return

        docs_hijos = set()
        for o in getattr(self.doc, "Objects", []):
            if o.TypeId == "App::Link" and getattr(o, "LinkedObject", None):
                lo = o.LinkedObject
                dh = getattr(lo, "Document", None)
                if dh and dh != self.doc:
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
        self.doc.recompute()

    def parametro_global(self, fila, alias, valor, descripcion="", origen="usuario"):
        ss = self.hoja
        ss.set(f"A{fila}", alias)
        ss.set(f"B{fila}", str(valor))
        ss.set(f"C{fila}", descripcion)
        ss.set(f"F{fila}", origen)
        ss.setAlias(f"B{fila}", alias)
        self.doc.recompute()

    def _leer_material_hijo(self, doc_hijo):
        mat_info = {
            "nombre": "Material Estándar",
            "densidad_num": "0.00000785",
            "color": (0.75, 0.75, 0.75),
            "transparencia": 0.0,
        }
        hm = doc_hijo.getObject("Materiales")
        if hm:
            try:
                mat_info["nombre"] = str(hm.get("material_nombre"))
                dens_val = hm.get("densidad_mat")
                mat_info["densidad_num"] = f"{float(dens_val):.10f}"
                mat_info["color"] = (float(hm.get("color_r")), float(hm.get("color_g")), float(hm.get("color_b")))
                mat_info["transparencia"] = float(hm.get("transparencia_mat"))
            except Exception:
                pass
        return mat_info

    def _aplicar_apariencia_link(self, link, sol_hijo, r_c, g_c, b_c, tr_efectiva):
        if not App.GuiUp:
            return
        try:
            if hasattr(link, "ViewObject") and link.ViewObject:
                vo = link.ViewObject
                vo.OverrideMaterial = True
                mat = App.Material()
                mat.DiffuseColor = (float(r_c), float(g_c), float(b_c))
                mat.Transparency = float(tr_efectiva) / 100.0
                if hasattr(vo, "ShapeAppearance"):
                    vo.ShapeAppearance = (mat,)
                elif hasattr(vo, "ShapeMaterial"):
                    vo.ShapeMaterial = mat
        except Exception:
            pass

    def insertar(self, ruta_fcstd, nombre_instancia, lcs_pieza="LCS_Origen",
                 en_instancia=None, lcs_destino="LCS_Origen",
                 offset=(0, 0, 0), rot_grados=(0, 0, 0), explosion_vec=(0, 0, 0),
                 expr_base=None):
        """
        Inserta un App::Link real apuntando al App::Part de ruta_fcstd,
        alinea 'lcs_pieza' con 'lcs_destino' de 'en_instancia' (o el origen global)
        y vincula el vector de desarme explosion_vec a <<Parametros_Generales>>.explosion.
        """
        import os
        ruta_abs = os.path.abspath(ruta_fcstd)
        if not os.path.exists(ruta_abs):
            raise FileNotFoundError(f"No existe la pieza a vincular: {ruta_abs}")

        doc_hijo = next((d for d in App.listDocuments().values()
                         if os.path.abspath(d.FileName) == ruta_abs), None)
        if doc_hijo is None:
            # Cargar en segundo plano (hidden=True) para no abrir 20+ pestañas en la GUI
            doc_hijo = App.openDocument(ruta_abs, True)

        # Asegurar que los objetos auxiliares del hijo estén ocultos
        for o in doc_hijo.Objects:
            if o.TypeId in ("App::Origin", "App::Plane", "App::Line") or o.isDerivedFrom("Part::Datum"):
                o.Visibility = False

        part_hijo = next((o for o in doc_hijo.Objects if o.TypeId == "App::Part"), None)
        if part_hijo is None:
            raise ValueError(f"No se encontró contenedor App::Part en {ruta_fcstd}")

        # Encontrar sólido final del hijo para volumen y color
        cands_sol = [o for o in doc_hijo.Objects
                     if o.isDerivedFrom("Part::Feature") and not o.isDerivedFrom("Part::Datum")
                     and getattr(o, "Shape", None) and o.Shape.Solids
                     and not any(p.isDerivedFrom("Part::Feature") and not p.isDerivedFrom("Part::Datum") for p in o.InList)]
        sol_hijo = cands_sol[-1] if cands_sol else None

        mat_info = self._leer_material_hijo(doc_hijo)
        if App.GuiUp and sol_hijo and hasattr(sol_hijo, "ViewObject") and sol_hijo.ViewObject:
            try:
                sol_hijo.ViewObject.ShapeColor = mat_info["color"]
                sol_hijo.ViewObject.Transparency = int(mat_info["transparencia"])
            except Exception:
                pass

        App.setActiveDocument(self.doc.Name)
        link = self.asm.newObject("App::Link", nombre_instancia)
        link.LinkedObject = part_hijo

        o_lcs_hijo = next((o for o in doc_hijo.Objects if o.Label == lcs_pieza or o.Name == lcs_pieza), None)
        p_hijo = o_lcs_hijo.Placement if o_lcs_hijo else App.Placement()

        if en_instancia is not None:
            doc_base = en_instancia.LinkedObject.Document
            o_lcs_dest = next((o for o in doc_base.Objects if o.Label == lcs_destino or o.Name == lcs_destino), None)
            p_local_dest = o_lcs_dest.Placement if o_lcs_dest else App.Placement()
            p_base = self.pos_armadas.get(en_instancia.Name, en_instancia.Placement)
            p_destino = p_base.multiply(p_local_dest)
        else:
            p_destino = App.Placement()

        p_off = App.Placement(App.Vector(*offset), App.Rotation(*rot_grados))
        p_final = p_destino.multiply(p_off).multiply(p_hijo.inverse())
        link.Placement = p_final
        self.pos_armadas[link.Name] = p_final

        ex, ey, ez = explosion_vec
        expr_dict = expr_base or {}
        if any(v != 0 for v in explosion_vec) or expr_dict:
            bx = expr_dict.get("x", f"{p_final.Base.x:.4f} mm")
            by = expr_dict.get("y", f"{p_final.Base.y:.4f} mm")
            bz = expr_dict.get("z", f"{p_final.Base.z:.4f} mm")
            if ex != 0 or "x" in expr_dict:
                link.setExpression(".Placement.Base.x", f"{bx} + ({ex} mm) * <<Parametros_Generales>>.explosion")
            if ey != 0 or "y" in expr_dict:
                link.setExpression(".Placement.Base.y", f"{by} + ({ey} mm) * <<Parametros_Generales>>.explosion")
            if ez != 0 or "z" in expr_dict:
                link.setExpression(".Placement.Base.z", f"{bz} + ({ez} mm) * <<Parametros_Generales>>.explosion")

        # Determinar color y transparencia (base vs personalizado/TRANSP_INSP preservado)
        def_r, def_g, def_b = mat_info["color"]
        tr_base = float(mat_info["transparencia"])
        if nombre_instancia in self.custom_prev:
            prev = self.custom_prev[nombre_instancia]
            r_c, g_c, b_c = prev["color"]
            tr_insp = prev["transp_insp"]
            es_pers = prev["personalizado"] or (
                abs(r_c - def_r) > 0.01 or abs(g_c - def_g) > 0.01 or abs(b_c - def_b) > 0.01
            )
            if not es_pers:
                r_c, g_c, b_c = def_r, def_g, def_b
        else:
            r_c, g_c, b_c = def_r, def_g, def_b
            tr_insp = 0.0
            es_pers = False

        tr_efectiva = int(tr_insp if tr_insp > 0 else tr_base)
        self._aplicar_apariencia_link(link, sol_hijo, r_c, g_c, b_c, tr_efectiva)

        clave = os.path.basename(ruta_abs)
        self.conteo_bom[clave] = [part_hijo.Label, self.conteo_bom.get(clave, [part_hijo.Label, 0])[1] + 1]
        self.componentes_inst.append({
            "nombre": nombre_instancia,
            "link": link,
            "doc_hijo": doc_hijo,
            "sol_hijo": sol_hijo,
            "material": mat_info["nombre"],
            "densidad": mat_info["densidad_num"],
            "color": (r_c, g_c, b_c),
            "transp_base": tr_base,
            "transp_insp": tr_insp,
            "personalizado": 1 if es_pers else 0,
        })
        return link

    def interfaz_coaxial(self, ref1, ref2, descripcion="", tol_mm=0.05):
        """
        Registra un par de patrones o cilindros que deben ser coaxiales en el ensamblaje armado.
        Formato de ref: 'NombreInstancia:PatronCilindro' (admite comodín '*', p. ej. 'Tapa_Interior_16b:M3_Guia_1_*').
        """
        self.interfaces.append({
            "ref1": ref1,
            "ref2": ref2,
            "descripcion": descripcion,
            "tol_mm": float(tol_mm),
        })

    def par_roscado(self, inst1, inst2):
        """Declara que entre inst1 e inst2 existe contacto roscado o ajuste (exento de reporte de colisión)."""
        n1 = inst1.Name if hasattr(inst1, "Name") else str(inst1)
        n2 = inst2.Name if hasattr(inst2, "Name") else str(inst2)
        self.pares_rosca_ajuste.append([n1, n2])

    def interferencia_plano_conocida(self, inst1, inst2, motivo=""):
        """Declara una interferencia propia de las cotas del plano original (se reporta como AVISO, no ERROR)."""
        n1 = inst1.Name if hasattr(inst1, "Name") else str(inst1)
        n2 = inst2.Name if hasattr(inst2, "Name") else str(inst2)
        self.interferencias_plano.append({"par": [n1, n2], "motivo": motivo})

    def cerrar(self):
        import json
        if not hasattr(self.asm, "Interfaces_Declaradas"):
            self.asm.addProperty(
                "App::PropertyString", "Interfaces_Declaradas", "_Control_IA",
                "Interfaces coaxiales y pares roscados declarados", 4
            )
        self.asm.Interfaces_Declaradas = json.dumps({
            "coaxiales": self.interfaces,
            "pares_rosca_ajuste": self.pares_rosca_ajuste,
            "interferencias_plano": self.interferencias_plano,
        }, ensure_ascii=False)
        # 1. Hoja Lista_de_Materiales (BOM)
        bom = self.asm.newObject("Spreadsheet::Sheet", "Lista_de_Materiales")
        bom.set("A1", "ARCHIVO"); bom.set("B1", "PIEZA"); bom.set("C1", "CANTIDAD")
        for idx, (arch, (etiqueta, cant)) in enumerate(self.conteo_bom.items(), start=2):
            bom.set(f"A{idx}", arch); bom.set(f"B{idx}", etiqueta); bom.set(f"C{idx}", str(cant))

        # 2. Hoja Materiales_Generales (con soporte de TRANSP_INSP y PERSONALIZADO)
        hmg = self.asm.newObject("Spreadsheet::Sheet", "Materiales_Generales")
        for celda, txt in (("A1", "COMPONENTE"), ("B1", "MATERIAL"), ("C1", "DENSIDAD"),
                           ("D1", "COLOR_R"), ("E1", "COLOR_G"), ("F1", "COLOR_B"),
                           ("G1", "TRANSP_BASE"), ("H1", "TRANSP_INSP"), ("I1", "PERSONALIZADO")):
            hmg.set(celda, txt)

        for r, info in enumerate(self.componentes_inst, start=2):
            hmg.set(f"A{r}", info["nombre"])
            hmg.set(f"B{r}", info["material"])
            hmg.set(f"C{r}", f"={info['densidad']}")
            hmg.set(f"D{r}", f"{info['color'][0]:.3f}")
            hmg.set(f"E{r}", f"{info['color'][1]:.3f}")
            hmg.set(f"F{r}", f"{info['color'][2]:.3f}")
            hmg.set(f"G{r}", f"{info['transp_base']:.1f}")
            hmg.set(f"H{r}", f"{info['transp_insp']:.1f}")
            hmg.set(f"I{r}", str(info["personalizado"]))

        # 3. Hoja Reporte_Fisico (Volumen vinculado al sólido hijo y Masa en kg)
        rep = self.asm.newObject("Spreadsheet::Sheet", "Reporte_Fisico")
        for celda, txt in (("A1", "COMPONENTE"), ("B1", "MATERIAL"), ("C1", "VOLUMEN (mm^3)"),
                           ("D1", "DENSIDAD (kg/mm^3)"), ("E1", "MASA (kg)")):
            rep.set(celda, txt)

        for r, info in enumerate(self.componentes_inst, start=2):
            rep.set(f"A{r}", info["nombre"])
            rep.set(f"B{r}", f"=<<Materiales_Generales>>.B{r}")
            if info["sol_hijo"] is not None:
                vol_expr = f"={info['doc_hijo'].Name}#{info['sol_hijo'].Name}.Shape.Volume"
            else:
                vol_expr = "=0"
            rep.set(f"C{r}", vol_expr)
            rep.set(f"D{r}", f"=<<Materiales_Generales>>.C{r}")
            rep.set(f"E{r}", f"=C{r} * D{r} * 1 kg")

        n_total = len(self.componentes_inst) + 2
        rep.set(f"A{n_total}", "MASA TOTAL ENSAMBLAJE")
        rep.set(f"E{n_total}", f"=sum(E2:E{n_total - 1})")

        # 4. Ocultar orígenes, planos y datums
        for o in self.doc.Objects:
            if o.TypeId in ("App::Origin", "App::Plane", "App::Line") or o.isDerivedFrom("Part::Datum"):
                o.Visibility = False
        self.asm.Visibility = True
        self.sincronizar_modo_diseno_piezas()
        self.doc.recompute()

        # Re-aplicar apariencia visual tras recompute si estamos en GUI
        for info in self.componentes_inst:
            tr_ef = int(info["transp_insp"] if info["transp_insp"] > 0 else info["transp_base"])
            self._aplicar_apariencia_link(
                info["link"], info["sol_hijo"],
                info["color"][0], info["color"][1], info["color"][2], tr_ef
            )

        self.doc.saveAs(self.ruta)
        print("Ensamblaje guardado:", self.ruta)
        if App.GuiUp:
            import FreeCADGui as Gui
            App.setActiveDocument(self.doc.Name)
            Gui.setActiveDocument(self.doc.Name)
            if Gui.activeDocument() and Gui.activeDocument().activeView():
                Gui.activeDocument().activeView().viewIsometric()
                Gui.SendMsgToActiveView("ViewFit")
            if hasattr(App, "_material_sync_observer") and App._material_sync_observer:
                try:
                    App._material_sync_observer.sync_document(self.doc)
                except Exception:
                    pass

