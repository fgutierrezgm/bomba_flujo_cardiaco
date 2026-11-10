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


class Pieza:
    def __init__(self, nombre):
        print("FreeCAD", ".".join(App.Version()[:3]))
        self.nombre = nombre
        # Limpiar snapshots en memoria de macros (Movimiento Libre / Aislar) para no inyectar expresiones viejas
        for prefijo_macro in ("_mov_libre_", "_aislado_"):
            attr_m = f"{prefijo_macro}{nombre}"
            if hasattr(App, attr_m):
                delattr(App, attr_m)

        if nombre in App.listDocuments():
            App.closeDocument(nombre)
        self.doc = App.newDocument(nombre)
        self.part = self.doc.addObject("App::Part", nombre)
        self.hoja = None
        self.hoja_mat = None
        self.auxiliares = []      # herramientas y fusiones intermedias (se ocultan en la GUI)

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
        for r, (alias, desc, nominal, tipo, mecha, origen) in enumerate(filas, start=7):
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
            App.closeDocument(nombre)

        self.doc = App.newDocument(nombre)
        # Guardar antes de crear vínculos para que FreeCAD almacene rutas relativas en App::Link
        self.doc.saveAs(self.ruta)
        self.asm = self.doc.addObject("App::Part", nombre)
        self.pos_armadas = {}      # nombre_instancia -> Placement sin explotar
        self.conteo_bom = {}       # archivo -> [etiqueta, cantidad]
        self.componentes_inst = [] # metadatos de instancias para Materiales_Generales y Reporte_Fisico
        self.hoja = self._crear_hoja_maestra(explosion_inicial)

    def _crear_hoja_maestra(self, explosion_inicial):
        ss = self.asm.newObject("Spreadsheet::Sheet", "Parametros_Generales")
        ss.set("A1", "PARÁMETRO"); ss.set("B1", "VALOR"); ss.set("C1", "DESCRIPCIÓN"); ss.set("F1", "ORIGEN")
        ss.set("A2", "Factor de explosión"); ss.set("B2", str(explosion_inicial))
        ss.setAlias("B2", "explosion")
        ss.set("C2", "0.0 = Ensamblado | 1.0 = Vista Explotada (admite valores intermedios)")
        ss.set("F2", "usuario")
        self.doc.recompute()
        return ss

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

    def cerrar(self):
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

