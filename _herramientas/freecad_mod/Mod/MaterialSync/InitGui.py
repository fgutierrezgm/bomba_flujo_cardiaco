# MaterialSync - Sincronizador automático en vivo entre hojas de Materiales y vista 3D en FreeCAD
import FreeCAD as App
import FreeCADGui as Gui


class MaterialSyncObserver:
    def __init__(self):
        self._in_sync = False

    @staticmethod
    def sanear_juntas_assembly(doc):
        """
        Sanea automáticamente los ViewProviders de juntas de Assembly::AssemblyObject
        si el documento fue generado en modo headless (freecadcmd), evitando errores
        de 'int object has no attribute redrawJointPlacements' en la GUI.
        """
        if not App.GuiUp or not doc:
            return
        try:
            import JointObject
            for o in getattr(doc, "Objects", []):
                if o.isDerivedFrom("App::FeaturePython") and getattr(o, "ViewObject", None):
                    vo = o.ViewObject
                    proxy = getattr(vo, "Proxy", None)
                    if hasattr(o, "JointType"):
                        if not isinstance(proxy, JointObject.ViewProviderJoint) or not hasattr(proxy, "app_obj"):
                            vp = JointObject.ViewProviderJoint(vo)
                            vp.app_obj = o
                            vp.attach(vo)
                    elif hasattr(o, "ObjectToGround"):
                        if not isinstance(proxy, JointObject.ViewProviderGroundedJoint) or not hasattr(proxy, "app_obj"):
                            vp = JointObject.ViewProviderGroundedJoint(vo)
                            vp.app_obj = o
                            vp.attach(vo)
        except Exception:
            pass

    @staticmethod
    def sincronizar_modo_diseno_global(doc):
        """
        Sincroniza el parámetro 'modo_diseno_global' de la hoja 'Parametros_Generales'
        del ensamblaje hacia la celda 'modo_diseno' (B2) de todas las piezas vinculadas.
        """
        if not doc or not hasattr(doc, "getObject"):
            return
        pg = doc.getObject("Parametros_Generales")
        if not pg:
            return
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

        actualizado = False
        for dh in docs_hijos:
            sp = dh.getObject("Parametros")
            if sp and hasattr(sp, "getAlias") and sp.getAlias("B2") == "modo_diseno":
                try:
                    cur_val = int(float(str(sp.get("B2")).strip()))
                except Exception:
                    cur_val = None
                if cur_val != modo_global:
                    sp.set("B2", str(modo_global))
                    dh.recompute()
                    actualizado = True

        if actualizado:
            doc.recompute()
            App.Console.PrintMessage(
                f"[ModoDiseno] Sincronizado modo_diseno = {modo_global} en {len(docs_hijos)} piezas vinculadas.\n"
            )

    @staticmethod
    def sincronizar_rotulos_planos(doc):
        """
        Sincroniza los campos globales de la hoja 'Datos_Rotulo' hacia todos los rótulos
        SVG ('TechDraw::DrawSVGTemplate') del documento de planos, estilo iProperties de Inventor.
        """
        if not doc or not hasattr(doc, "getObject"):
            return
        dr = doc.getObject("Datos_Rotulo")
        if not dr:
            return
        campos_globales = {}
        r = 2
        while r < 40:
            try:
                clave = dr.get(f"A{r}")
            except Exception:
                break
            if not clave:
                break
            clave_str = str(clave).strip()
            try:
                val = dr.get(f"B{r}")
                val_str = str(val).strip() if val is not None else ""
            except Exception:
                val_str = ""
            campos_globales[clave_str] = val_str
            r += 1

        if not campos_globales:
            return

        actualizados = 0
        for o in getattr(doc, "Objects", []):
            if o.TypeId == "TechDraw::DrawSVGTemplate" and hasattr(o, "EditableTexts"):
                et = dict(o.EditableTexts)
                cambio = False
                for k, v in campos_globales.items():
                    if k in et and et[k] != v:
                        et[k] = v
                        cambio = True
                if cambio:
                    o.EditableTexts = et
                    actualizados += 1

        if actualizados > 0:
            App.Console.PrintMessage(
                f"[RotuloSync] Actualizados automáticamente {actualizados} rótulos desde Datos_Rotulo.\n"
            )

    def slotActivatedDocument(self, doc):
        if self._in_sync or not doc:
            return
        self._in_sync = True
        try:
            self.sanear_juntas_assembly(doc)
            self.sincronizar_rotulos_planos(doc)
        finally:
            self._in_sync = False

    def slotCreatedDocument(self, doc):
        if self._in_sync or not doc:
            return
        self.sanear_juntas_assembly(doc)

    def slotChangedObject(self, obj, prop):
        if self._in_sync or not obj:
            return
        if obj.Name == "Parametros_Generales" and prop in ("B3", "modo_diseno_global"):
            self._in_sync = True
            try:
                self.sincronizar_modo_diseno_global(obj.Document)
            finally:
                self._in_sync = False
        elif obj.Name == "Datos_Rotulo":
            self.sincronizar_rotulos_planos(obj.Document)
        elif obj.Name in ("Materiales_Generales", "Materiales"):
            self.sync_document(obj.Document)

    def slotRecomputedObject(self, obj):
        if self._in_sync or not obj:
            return
        if obj.Name == "Datos_Rotulo":
            self.sincronizar_rotulos_planos(obj.Document)
        elif obj.Name in ("Materiales_Generales", "Materiales"):
            self.sync_document(obj.Document)

    def slotFinishRecomputeDocument(self, doc):
        if self._in_sync or not doc:
            return
        self._in_sync = True
        try:
            self.sanear_juntas_assembly(doc)
            self.sincronizar_rotulos_planos(doc)
        finally:
            self._in_sync = False
        if doc.getObject("Materiales_Generales") or doc.getObject("Materiales"):
            self.sync_document(doc)

    def sync_document(self, doc):
        if not doc or not hasattr(doc, "getObject") or not App.GuiUp:
            return
        self._in_sync = True
        try:
            # 1. Caso Hoja Materiales_Generales (Ensamblajes con App::Link o Part::Feature)
            mg = doc.getObject("Materiales_Generales")
            if mg:
                r = 2
                while True:
                    try:
                        inst = mg.get(f"A{r}")
                    except Exception:
                        break
                    if not inst:
                        break
                    inst_str = str(inst)
                    obj = doc.getObject(inst_str) or doc.getObject(f"{inst_str}_Solido")
                    if obj and hasattr(obj, "ViewObject") and obj.ViewObject:
                        try:
                            r_c = float(mg.get(f"D{r}"))
                            g_c = float(mg.get(f"E{r}"))
                            b_c = float(mg.get(f"F{r}"))
                            tr_base = float(mg.get(f"G{r}"))
                            tr_insp = float(mg.get(f"H{r}"))

                            # Normalización automática si se ingresó en escala 0-255
                            if r_c > 1.0 or g_c > 1.0 or b_c > 1.0:
                                r_c, g_c, b_c = r_c / 255.0, g_c / 255.0, b_c / 255.0
                            r_c = max(0.0, min(1.0, r_c))
                            g_c = max(0.0, min(1.0, g_c))
                            b_c = max(0.0, min(1.0, b_c))

                            tr = int(max(0, min(100, tr_insp if tr_insp > 0 else tr_base)))
                            vo = obj.ViewObject

                            if obj.TypeId == "App::Link":
                                sa = vo.ShapeAppearance[0] if getattr(vo, "ShapeAppearance", None) else None
                                cur_col = sa.DiffuseColor[:3] if sa else (-1, -1, -1)
                                cur_tr = int(round(sa.Transparency * 100.0)) if sa else -1
                                if (not vo.OverrideMaterial or
                                    abs(cur_col[0] - r_c) > 0.002 or
                                    abs(cur_col[1] - g_c) > 0.002 or
                                    abs(cur_col[2] - b_c) > 0.002 or
                                    abs(cur_tr - tr) > 0):
                                    vo.OverrideMaterial = True
                                    mat = App.Material()
                                    mat.DiffuseColor = (r_c, g_c, b_c)
                                    mat.Transparency = float(tr) / 100.0
                                    vo.ShapeAppearance = (mat,)
                                    mg.set(f"I{r}", "1")
                            elif hasattr(vo, "ShapeColor"):
                                if (abs(vo.ShapeColor[0] - r_c) > 0.002 or
                                    abs(vo.ShapeColor[1] - g_c) > 0.002 or
                                    abs(vo.ShapeColor[2] - b_c) > 0.002 or
                                    abs(vo.Transparency - tr) > 0):
                                    vo.ShapeColor = (r_c, g_c, b_c)
                                    vo.Transparency = tr
                                    mg.set(f"I{r}", "1")
                        except Exception:
                            pass
                    r += 1

            # 2. Caso Hoja Materiales (Piezas individuales)
            hm = doc.getObject("Materiales")
            if hm and not mg:
                sol = None
                for o in doc.Objects:
                    if o.isDerivedFrom("Part::Feature") and not o.isDerivedFrom("Part::Datum") and getattr(o, "Shape", None) and o.Shape.Solids:
                        sol = o
                        break
                if sol and hasattr(sol, "ViewObject") and sol.ViewObject:
                    try:
                        r_c = float(hm.get("color_r"))
                        g_c = float(hm.get("color_g"))
                        b_c = float(hm.get("color_b"))
                        tr = int(float(hm.get("transparencia_mat")))
                        if r_c > 1.0 or g_c > 1.0 or b_c > 1.0:
                            r_c, g_c, b_c = r_c / 255.0, g_c / 255.0, b_c / 255.0
                        r_c = max(0.0, min(1.0, r_c))
                        g_c = max(0.0, min(1.0, g_c))
                        b_c = max(0.0, min(1.0, b_c))
                        tr = max(0, min(100, tr))

                        vo = sol.ViewObject
                        if (abs(vo.ShapeColor[0] - r_c) > 0.002 or
                            abs(vo.ShapeColor[1] - g_c) > 0.002 or
                            abs(vo.ShapeColor[2] - b_c) > 0.002 or
                            abs(vo.Transparency - tr) > 0):
                            vo.ShapeColor = (r_c, g_c, b_c)
                            vo.Transparency = tr
                            hm.set("apariencia_personalizada", "1")
                    except Exception:
                        pass
        finally:
            self._in_sync = False


if App.GuiUp:
    if hasattr(App, "_material_sync_observer") and App._material_sync_observer:
        try:
            App.removeDocumentObserver(App._material_sync_observer)
        except Exception:
            pass
    obs = MaterialSyncObserver()
    App._material_sync_observer = obs
    App.addDocumentObserver(obs)
    if App.ActiveDocument:
        obs.sync_document(App.ActiveDocument)

    # Auto-iniciar MCP Bridge en loopback al abrir la GUI para diseño rápido en vivo
    try:
        from PySide.QtCore import QTimer

        def _autostart_mcp_bridge():
            try:
                from freecad.mcp_bridge import bridge
                if not bridge.is_running():
                    bridge.start()
                if hasattr(App, "MCPBridgeInjectUi"):
                    App.MCPBridgeInjectUi()
            except Exception:
                pass

        QTimer.singleShot(1500, _autostart_mcp_bridge)
    except Exception:
        pass
