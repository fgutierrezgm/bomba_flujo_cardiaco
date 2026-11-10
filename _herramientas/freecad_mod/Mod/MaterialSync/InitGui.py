# MaterialSync - Sincronizador automático en vivo entre hojas de Materiales y vista 3D en FreeCAD
import FreeCAD as App
import FreeCADGui as Gui


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


class MaterialSyncObserver:
    def __init__(self):
        self._in_sync = False

    def slotActivatedDocument(self, doc):
        sanear_juntas_assembly(doc)

    def slotCreatedDocument(self, doc):
        sanear_juntas_assembly(doc)

    def slotChangedObject(self, obj, prop):
        if self._in_sync or not obj:
            return
        if obj.Name in ("Materiales_Generales", "Materiales"):
            self.sync_document(obj.Document)

    def slotRecomputedObject(self, obj):
        if self._in_sync or not obj:
            return
        if obj.Name in ("Materiales_Generales", "Materiales"):
            self.sync_document(obj.Document)

    def slotFinishRecomputeDocument(self, doc):
        sanear_juntas_assembly(doc)
        if self._in_sync or not doc:
            return
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
