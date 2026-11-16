import FreeCAD as App
import Part
import math

# =====================================================================
#  TEST DE ROSCAS PARA FDM: M4 (ISO) + TORNILLO SINFÍN TRAPEZOIDAL
#  Roscas helicoidales B-Rep reales, sin OpenSCAD.
# =====================================================================

NOMBRE_DOC = "Test_Roscas_M4_y_Sinfin"

# ---- Perfiles --------------------------------------------------------
# d      = diámetro mayor nominal
# paso   = paso de la hélice (rosca de 1 entrada => avance = paso)
# prof   = profundidad del diente del tornillo
# cresta = ancho de la cresta truncada del tornillo
# flanco = semiángulo de cada flanco medido desde el plano perpendicular al eje
#          (45 => flancos a 45°, ángulo incluido 90°; 30 => ISO 60°)

M4 = dict(d=4.0, paso=0.7, prof=0.6134 * 0.7, cresta=0.7 / 8, flanco=30.0)

PASO_SF = 3.0          # si escalás el sinfín, cambiá d y PASO_SF juntos
SINFIN = dict(d=14.0, paso=PASO_SF,
              prof=0.38 * PASO_SF,       # profundidad de diente 0.38 x paso
              cresta=0.24 * PASO_SF,     # cresta truncada 0.24 x paso
              flanco=45.0)

SINFIN_HOLG_RAD = 0.20   # holgura radial (mm)
SINFIN_HOLG_AX = 0.25    # holgura axial TOTAL = backlash (mm)

# Holguras radiales a probar en M4 (1 punto = la primera, 2 puntos = la segunda...)
# Con paso 0.7 y diente de 0.43 mm, más de ~0.20 deja casi sin engrane.
HOLGURAS_M4 = [0.05, 0.10, 0.15, 0.20]

LARGO_SINFIN = 18.0
LARGO_TUERCA = 12.0

HUECO_MIN = 0.10   # separación mínima entre vueltas del barrido (evita autointersección)
PUNTA_MIN = 0.05   # ancho mínimo de la punta del diente de la tuerca


# ---- Utilidades ------------------------------------------------------
def _tan(P):
    return math.tan(math.radians(P["flanco"]))


def _a_solido(s):
    """Asegura un sólido con volumen positivo."""
    if s.ShapeType == "Shell":
        s = Part.Solid(s)
    elif s.ShapeType == "Compound" and s.Solids:
        s = s.Solids[0]
    if s.Volume < 0:
        s.reverse()
    return s


def _revolucion(pts_rz):
    v = [App.Vector(r, 0, z) for r, z in pts_rz]
    cara = Part.Face(Part.makePolygon(v + [v[0]]))
    return cara.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)


def _hexagono(radio_circ, alto):
    v = [App.Vector(radio_circ * math.cos(math.radians(a)),
                    radio_circ * math.sin(math.radians(a)), 0)
         for a in range(0, 360, 60)]
    return Part.Face(Part.makePolygon(v + [v[0]])).extrude(App.Vector(0, 0, alto))


def _barrido_helicoidal(pts_rz, paso, largo):
    """Barre un perfil (lista de (r, z), simétrico en z=0) a lo largo de una hélice.
    El sólido resultante cubre z desde -paso hasta largo+paso (se recorta después)."""
    r_ref = sum(p[0] for p in pts_rz) / len(pts_rz)   # radio de la hélice, dentro del perfil
    v = [App.Vector(r, 0, z) for r, z in pts_rz]
    perfil = Part.makePolygon(v + [v[0]])
    helice = Part.Wire(Part.makeHelix(paso, largo + 2 * paso, r_ref).Edges)
    s = _a_solido(helice.makePipeShell([perfil], True, True))   # Frenet = True
    s.translate(App.Vector(0, 0, -paso))
    return s


# ---- Tornillo (rosca externa) ----------------------------------------
def tornillo(P, largo, achique=0.0):
    """Tornillo con chaflán de 45° en la punta. 'achique' reduce todo el perfil
    radialmente (para que un macho impreso entre en una tuerca metálica)."""
    paso, t = P["paso"], _tan(P)
    r_max = P["d"] / 2 - achique
    r_raiz = r_max - P["prof"]

    # Ancho del diente: w(r) = cresta + 2*t*(r_max - r). Se limita a (paso - HUECO_MIN)
    # para que las vueltas del barrido no se toquen (con 45° y 0.38/0.24 la base
    # vale exactamente el paso: raíz en V sin plano).
    w_max = paso - HUECO_MIN
    r_c = r_max - (w_max - P["cresta"]) / (2 * t)
    r_f = max(r_c, r_raiz - 0.05)
    w_f = P["cresta"] + 2 * t * (r_max - r_f)
    r_in = r_raiz - 0.3                                 # se hunde en el núcleo

    pts = [(r_max, -P["cresta"] / 2), (r_max, P["cresta"] / 2),
           (r_f, w_f / 2), (r_in, w_f / 2), (r_in, -w_f / 2), (r_f, -w_f / 2)]
    diente = _barrido_helicoidal(pts, paso, largo)

    nucleo = Part.makeCylinder(r_raiz, largo + 2 * paso, App.Vector(0, 0, -paso))
    nucleo.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 180)   # costura lejos de la hélice
    bruto = nucleo.fuse(diente)

    R = r_max + 0.3
    r_punta = r_raiz - 0.1
    z0 = largo - (R - r_punta)                          # chaflán exacto a 45°
    envolvente = _revolucion([(0, 0), (R, 0), (R, z0), (r_punta, largo), (0, largo)])
    return bruto.common(envolvente)


# ---- Rosca interna (tuerca / agujero roscado) -------------------------
def _diente_interno(P, largo, hol_rad, hol_ax):
    """Diente helicoidal de la tuerca = ranura del tornillo nominal menos holguras.
    Ancho a radio r:  w(r) = paso - ancho_tornillo(r) - hol_ax."""
    paso, t = P["paso"], _tan(P)
    r_max = P["d"] / 2
    r_raiz = r_max - P["prof"]
    if hol_ax is None:                                   # holgura uniforme tipo "offset radial"
        hol_ax = 2 * hol_rad * t

    def w(r):
        return paso - (P["cresta"] + 2 * t * (r_max - r)) - hol_ax

    r_base = r_max + hol_rad                             # fondo de la tuerca = radio del agujero
    r_punta = r_raiz + hol_rad                           # punta del diente (hacia el eje)
    r_punta = max(r_punta, r_max - (paso - P["cresta"] - hol_ax - PUNTA_MIN) / (2 * t))
    w_punta = w(r_punta)
    if w_punta < 0.4:
        print("  Aviso: punta del diente de la tuerca = %.2f mm (menor que un "
              "ancho de extrusión típico de 0.4 mm)" % w_punta)

    w_max = paso - HUECO_MIN
    r_c = r_max - (paso - P["cresta"] - hol_ax - w_max) / (2 * t)
    r_f = min(r_base + 0.1, r_c)                         # el flanco se prolonga dentro de la pared
    w_f = w(r_f)
    r_out = r_base + 0.6                                 # se hunde en la pared para fusionar

    pts = [(r_punta, -w_punta / 2), (r_punta, w_punta / 2),
           (r_f, w_f / 2), (r_out, w_f / 2), (r_out, -w_f / 2), (r_f, -w_f / 2)]
    diente = _barrido_helicoidal(pts, paso, largo)
    recorte = Part.makeCylinder(r_out + 1.0, largo)
    return diente.common(recorte), r_base


def rosca_interna(cuerpo, P, largo, pos, hol_rad, hol_ax=None):
    """Hace un agujero roscado pasante de 'largo' mm en 'cuerpo', con base en 'pos'."""
    diente, r_base = _diente_interno(P, largo, hol_rad, hol_ax)
    taladro = Part.makeCylinder(r_base, largo + 1.0, App.Vector(0, 0, -0.5))
    taladro.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 180)
    taladro.translate(pos)
    diente.translate(pos)
    return cuerpo.cut(taladro).fuse(diente)


# =====================================================================
#  CONSTRUCCIÓN
# =====================================================================
if NOMBRE_DOC in App.listDocuments():
    App.closeDocument(NOMBRE_DOC)
doc = App.newDocument(NOMBRE_DOC)


def agregar(nombre, shape):
    try:
        shape = shape.removeSplitter()
    except Exception:
        pass
    obj = doc.addObject("Part::Feature", nombre)
    obj.Shape = shape
    return obj


print("Generando test de roscas (puede tardar de 30 s a un par de minutos)...")

# 1. PLACA M4: 4 postes macho (atrás) + 4 agujeros hembra (adelante)
ESP = 6.0
PASO_X = 14.0
Y_POSTE = 14.0
ALTO_POSTE = 8.0

placa = Part.makeBox(58, 27, ESP, App.Vector(-8, -9, 0))
for i, hol in enumerate(HOLGURAS_M4):
    x = i * PASO_X
    print("  M4 #%d  holgura radial %.2f mm" % (i + 1, hol))
    placa = rosca_interna(placa, M4, ESP, App.Vector(x, 0, 0), hol)
    poste = tornillo(M4, ALTO_POSTE + 0.5, achique=hol)
    poste.translate(App.Vector(x, Y_POSTE, ESP - 0.5))
    placa = placa.fuse(poste)
    for p in range(i + 1):                               # i+1 puntitos hundidos
        px = x + (p - i / 2.0) * 2.0
        placa = placa.cut(Part.makeCylinder(0.7, 1.5, App.Vector(px, -6.5, ESP - 1.0)))
agregar("Placa_Test_M4", placa)

# 2. GUÍA M4 HORIZONTAL con dos planos (apoya el plano sobre la cama)
rosca_g = tornillo(M4, 12.0, achique=0.15)
vastago = Part.makeCylinder(2.0, 10.5, App.Vector(0, 0, -10.0))
guia = vastago.fuse(rosca_g)
guia.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)           # eje Z -> eje X
guia = guia.common(Part.makeBox(40, 10, 3.0, App.Vector(-20, -5, -1.5)))  # planos en z = +-1.5
guia.translate(App.Vector(10, 30, 1.5))                              # plano inferior en Z = 0
agregar("Guia_M4_Horizontal", guia)

# 3. SINFÍN trapezoidal + TUERCA
rosca_sf = tornillo(SINFIN, LARGO_SINFIN)
rosca_sf.translate(App.Vector(0, 0, 3.5))                            # 0.5 mm de solape con la cabeza
macho = _hexagono(11.0, 4.0).fuse(rosca_sf)
macho.translate(App.Vector(75.0, 5.0, 0.0))
agregar("SinFin_Macho", macho)

tuerca = rosca_interna(_hexagono(13.0, LARGO_TUERCA), SINFIN, LARGO_TUERCA,
                       App.Vector(0, 0, 0), SINFIN_HOLG_RAD, SINFIN_HOLG_AX)
tuerca.translate(App.Vector(75.0, 38.0, 0.0))
agregar("SinFin_Tuerca", tuerca)

# 4. HOJA DE REFERENCIA
ss = doc.addObject("Spreadsheet::Sheet", "Tabla_Referencia")
ss.set("A1", "MARCA (PUNTITOS)")
ss.set("B1", "HOLGURA RADIAL")
ss.set("C1", "DIAM. M4 MACHO")
ss.set("D1", "DIAM. AGUJERO M4")
for idx, h in enumerate(HOLGURAS_M4, start=1):
    r = idx + 1
    ss.set("A%d" % r, "%d punto(s)" % idx)
    ss.set("B%d" % r, "%.2f mm" % h)
    ss.set("C%d" % r, "%.2f mm" % (M4["d"] - 2 * h))
    ss.set("D%d" % r, "%.2f mm" % (M4["d"] + 2 * h))
ss.set("A7", "SINFIN")
ss.set("B7", "d=%.1f  paso=%.2f  prof=%.2f  cresta=%.2f  flancos=%.0f grados" %
       (SINFIN["d"], SINFIN["paso"], SINFIN["prof"], SINFIN["cresta"], SINFIN["flanco"]))
ss.set("A8", "Holgura radial")
ss.set("B8", "%.2f mm" % SINFIN_HOLG_RAD)
ss.set("A9", "Holgura axial (backlash)")
ss.set("B9", "%.2f mm" % SINFIN_HOLG_AX)

doc.recompute()

# Verificación rápida
for o in doc.Objects:
    if o.isDerivedFrom("Part::Feature"):
        print("  %-22s válido=%s  volumen=%.1f mm3" % (o.Name, o.Shape.isValid(), o.Shape.Volume))

if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
print("Listo.")
