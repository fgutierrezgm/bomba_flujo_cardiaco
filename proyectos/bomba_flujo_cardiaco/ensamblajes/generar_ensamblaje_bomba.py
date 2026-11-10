# Ensamblaje general de vínculos (App::Link) de la bomba programable de simulación de flujo cardíaco (Plano Nº 0)
# Incluye las 19 piezas distintas (30 instancias vinculadas en total) desde el Plano Nº 2a hasta el Plano Nº 16b.
# Sin interfaz:  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/ensamblajes/generar_ensamblaje_bomba.py
# En vivo (MCP): ejecutado directamente con execute_python_file
import os
import sys

AQUI = os.path.dirname(os.path.abspath(globals().get("__file__", "ensamblaje.py")))
PROYECTO = os.path.dirname(AQUI)
PIEZAS = os.path.join(PROYECTO, "piezas")
RAIZ = PROYECTO
while RAIZ != os.path.dirname(RAIZ) and not os.path.isdir(os.path.join(RAIZ, "_herramientas")):
    RAIZ = os.path.dirname(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))
import importlib
import fc_helpers
importlib.reload(fc_helpers)
from fc_helpers import Ensamblaje

SALIDA = os.path.join(AQUI, "Ensamblaje_Bomba.FCStd")


def ruta_p(archivo):
    return os.path.join(PIEZAS, archivo)


ens = Ensamblaje("Ensamblaje_Bomba", SALIDA, explosion_inicial="0.0")
ens.parametro_global(3, "pos_embolo", "130.00 mm", "Posición axial Z del émbolo de Delrin (carrera)", origen="usuario")

# 1. Tapa Interior (Plano 16b), Cilindro de Vidrio (Plano 9) y Tapa Exterior (Plano 16a) encadenados por LCS
tapa_int = ens.insertar(
    ruta_p("Tapa_Interior_16b.FCStd"), "Tapa_Interior_16b",
    lcs_pieza="LCS_Origen",
    explosion_vec=(0, 0, -40),
)

cilindro = ens.insertar(
    ruta_p("Cilindro_09.FCStd"), "Cilindro_09",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Piso_Tubo_110_5",
)

tapa_ext = ens.insertar(
    ruta_p("Tapa_Exterior_16a.FCStd"), "Tapa_Exterior_16a",
    lcs_pieza="LCS_Piso_Tubo_110_5",
    en_instancia=cilindro, lcs_destino="LCS_Extremo_Sup",
    rot_grados=(0, 0, 180),
    explosion_vec=(0, 0, 40),
)

# 2. 2x Barras Guía (Plano 8) alineando su LCS_Hombro_Asiento con LCS_Guia_1 / LCS_Guia_2 de Tapa Interior
for i in (1, 2):
    ens.insertar(
        ruta_p("Guia_08.FCStd"), f"Guia_{i}_08",
        lcs_pieza="LCS_Hombro_Asiento",
        en_instancia=tapa_int, lcs_destino=f"LCS_Guia_{i}",
    )

# 3. 2x Sufridera Guía (Plano 5b) alineando su LCS_Cara_Sup con LCS_Guia_1 / LCS_Guia_2 de Tapa Interior
for i in (1, 2):
    ens.insertar(
        ruta_p("Sufridera_Guia_05b.FCStd"), f"Sufridera_Guia_{i}_05b",
        lcs_pieza="LCS_Cara_Sup",
        en_instancia=tapa_int, lcs_destino=f"LCS_Guia_{i}",
        explosion_vec=(0, 0, -15),
    )

# 4. Subconjunto móvil del Émbolo (Planos 10, 11, 12 y 2x Tope Sensor Pistón 5b), gobernado por pos_embolo
embolo = ens.insertar(
    ruta_p("Embolo_Delrin_10.FCStd"), "Embolo_Delrin_10",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo"},
)

ens.insertar(
    ruta_p("Centro_Embolo_1_11.FCStd"), "Centro_Embolo_1_11",
    lcs_pieza="LCS_Asiento_Brida",
    en_instancia=embolo, lcs_destino="LCS_Origen",
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo - Centro_Embolo_1_11#Parametros.h_brida"},
    explosion_vec=(0, 0, -15),
)

ens.insertar(
    ruta_p("Centro_Embolo_2_12.FCStd"), "Centro_Embolo_2_12",
    lcs_pieza="LCS_Origen",
    en_instancia=embolo, lcs_destino="LCS_Cara_Sup",
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo + Embolo_Delrin_10#Parametros.h_total"},
    explosion_vec=(0, 0, 15),
)

# Tope 1 (en cara Z=0 del émbolo, +45°, enfrentando el Puerto_M12x1 de Tapa_Interior_16b)
ens.insertar(
    ruta_p("Sensor_Piston_05b.FCStd"), "Sensor_Piston_1_05b",
    lcs_pieza="LCS_Asiento_Embolo",
    en_instancia=embolo, lcs_destino="LCS_Sensor_1",
    rot_grados=(0, 0, 180),
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo + Sensor_Piston_05b#Parametros.l_vast"},
    explosion_vec=(0, 0, -20),
)

# Tope 2 (en cara Z=h_total del émbolo, -45°, enfrentando el Puerto_M12x1 de Tapa_Exterior_16a)
ens.insertar(
    ruta_p("Sensor_Piston_05b.FCStd"), "Sensor_Piston_2_05b",
    lcs_pieza="LCS_Asiento_Embolo",
    en_instancia=embolo, lcs_destino="LCS_Sensor_2",
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo + Embolo_Delrin_10#Parametros.h_total - Sensor_Piston_05b#Parametros.l_vast"},
    explosion_vec=(0, 0, 20),
)

# 5. Husillo y Tren de Transmisión encadenados por conectores LCS (Planos 14, 5a, 5b, 4, 3, 2b, 2a)
husillo = ens.insertar(
    ruta_p("Tornillo_Sin_Fin_14.FCStd"), "Tornillo_Sin_Fin_14",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Acople_Husillo",
)

ens.insertar(
    ruta_p("Sufridera_Eje_Ext_05a.FCStd"), "Sufridera_Eje_Ext_05a",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_ext, lcs_destino="LCS_Asiento_Sufridera_Ext",
    rot_grados=(0, 0, 180),
    explosion_vec=(0, 0, 55),
)

ens.insertar(
    ruta_p("Sufridera_Int_05b.FCStd"), "Sufridera_Int_05b",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Asiento_Sufridera_Int",
    explosion_vec=(0, 0, -50),
)

ens.insertar(
    ruta_p("Tapa_Sufridera_Int_05a.FCStd"), "Tapa_Sufridera_Int_05a",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    explosion_vec=(0, 0, -60),
)

adap_eje = ens.insertar(
    ruta_p("Adaptador_Eje_04.FCStd"), "Adaptador_Eje_04",
    lcs_pieza="LCS_Cara_Superior",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    explosion_vec=(0, 0, -75),
)

ens.insertar(
    ruta_p("Adaptador_Rodamiento_03.FCStd"), "Adaptador_Rodamiento_03",
    lcs_pieza="LCS_Tope_Superior",
    en_instancia=adap_eje, lcs_destino="LCS_Origen",
    explosion_vec=(0, 0, -95),
)

transm_2 = ens.insertar(
    ruta_p("Transmisor_2_02b.FCStd"), "Transmisor_2_02b",
    lcs_pieza="LCS_Pasador_3",
    en_instancia=husillo, lcs_destino="LCS_Pasador",
    explosion_vec=(0, 0, -120),
)

ens.insertar(
    ruta_p("Transmisor_1_02a.FCStd"), "Transmisor_1_02a",
    lcs_pieza="LCS_Extremo_Der",
    en_instancia=transm_2, lcs_destino="LCS_Asiento_Rodamiento",
    explosion_vec=(0, 0, -150),
)

# 6. Anillos prensa-tórica (2x Plano 13), Estructura Interior (2x Plano 7), Cierres (2x Plano 15) y Tensores (4x Plano 6)
ens.insertar(
    ruta_p("Anillo_Torica_13.FCStd"), "Anillo_Torica_Int_13",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Tope_Resalte",
    explosion_vec=(0, 0, -20),
)

ens.insertar(
    ruta_p("Anillo_Torica_13.FCStd"), "Anillo_Torica_Ext_13",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_ext, lcs_destino="LCS_Tope_Resalte",
    explosion_vec=(0, 0, 20),
)

estruct_1 = ens.insertar(
    ruta_p("Estructura_Interior_07.FCStd"), "Estructura_Interior_1_07",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Asiento_Carcasa_145mm",
    explosion_vec=(0, 0, -25),
)

estruct_2 = ens.insertar(
    ruta_p("Estructura_Interior_07.FCStd"), "Estructura_Interior_2_07",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_ext, lcs_destino="LCS_Asiento_Carcasa_145mm",
    explosion_vec=(0, 0, 25),
)

ens.insertar(
    ruta_p("Cierre_Estructura_15.FCStd"), "Cierre_Estructura_1_15",
    lcs_pieza="LCS_Origen",
    en_instancia=estruct_1, lcs_destino="LCS_Tope_Resalte",
    rot_grados=(45, 0, 0),
    explosion_vec=(0, 0, -15),
)

ens.insertar(
    ruta_p("Cierre_Estructura_15.FCStd"), "Cierre_Estructura_2_15",
    lcs_pieza="LCS_Origen",
    en_instancia=estruct_2, lcs_destino="LCS_Tope_Resalte",
    rot_grados=(45, 0, 0),
    explosion_vec=(0, 0, 15),
)

for idx, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1)), 1):
    ens.insertar(
        ruta_p("Tensor_06.FCStd"), f"Tensor_{idx}_06",
        lcs_pieza="LCS_Asiento_Estructura_1",
        en_instancia=estruct_1, lcs_destino=f"LCS_Tensor_{idx}",
        explosion_vec=(sx * 25, sy * 25, 0),
    )

# 7. Declaración de interfaces coaxiales y pares roscados para verificar_interfaces.py
ens.interfaz_coaxial("Tapa_Interior_16b:M3_Guia_1_*", "Sufridera_Guia_1_05b:Agujero_[1-4]", "4x M3 Sufridera Guía 1 <-> Tapa Interior")
ens.interfaz_coaxial("Tapa_Interior_16b:M3_Guia_2_*", "Sufridera_Guia_2_05b:Agujero_[1-4]", "4x M3 Sufridera Guía 2 <-> Tapa Interior")
ens.interfaz_coaxial("Tapa_Interior_16b:Puerto_M12x1", "Embolo_Delrin_10:M8_Sensor_1", "Sensor inductivo Tapa Interior <-> Tope FC 1 (Émbolo Z=0)")
ens.interfaz_coaxial("Tapa_Exterior_16a:Puerto_M12x1", "Embolo_Delrin_10:M8_Sensor_2", "Sensor inductivo Tapa Exterior <-> Tope FC 2 (Émbolo Z=20)")
ens.interfaz_coaxial("Embolo_Delrin_10:M3_Inf_*", "Centro_Embolo_1_11:Aguj_Brida_*", "4x M3 Centro Émbolo 1 <-> Émbolo Delrin", tol_mm=0.06)
ens.interfaz_coaxial("Centro_Embolo_1_11:M3_Sup_*", "Centro_Embolo_2_12:Aguj_M3_*", "3x M3 Centro Émbolo 1 <-> Centro Émbolo 2")
ens.interfaz_coaxial("Transmisor_1_02a:Agujero_Pasador_1", "Transmisor_2_02b:Pasador_1", "Pasador transversal 1 Transmisor 1 <-> Transmisor 2")
ens.interfaz_coaxial("Transmisor_1_02a:Agujero_Pasador_2", "Transmisor_2_02b:Pasador_2", "Pasador transversal 2 Transmisor 1 <-> Transmisor 2")
ens.interfaz_coaxial("Transmisor_2_02b:Pasador_3", "Tornillo_Sin_Fin_14:Agujero_Pasador", "Pasador transversal 3 Transmisor 2 <-> Tornillo Sin Fin")
ens.interfaz_coaxial("Estructura_Interior_1_07:Rosca_M5_*", "Cierre_Estructura_1_15:Aguj_Brida_*", "4x M5 Estructura Interior 1 <-> Cierre 1")
ens.interfaz_coaxial("Estructura_Interior_2_07:Rosca_M5_*", "Cierre_Estructura_2_15:Aguj_Brida_*", "4x M5 Estructura Interior 2 <-> Cierre 2")

ens.par_roscado("Embolo_Delrin_10", "Sensor_Piston_1_05b")
ens.par_roscado("Embolo_Delrin_10", "Sensor_Piston_2_05b")
ens.par_roscado("Centro_Embolo_1_11", "Tornillo_Sin_Fin_14")
ens.par_roscado("Centro_Embolo_2_12", "Tornillo_Sin_Fin_14")
ens.par_roscado("Tornillo_Sin_Fin_14", "Transmisor_2_02b")

# Interferencias propias de las cotas del legajo original documentadas en las FICHAs (se reportan como AVISO)
ens.interferencia_plano_conocida(
    "Tapa_Interior_16b", "Sufridera_Int_05b",
    "FICHA 16b Secc. 5: rebaje d_reb2=41.00 mm en Plano 16b vs d_ext=45.00 mm en Plano 5b"
)
ens.interferencia_plano_conocida(
    "Adaptador_Rodamiento_03", "Transmisor_2_02b",
    "FICHA 03/02b: agujero d_paso=13.10 mm en Plano 3 vs collar d_collar=15.00 mm en Plano 2b"
)
ens.interferencia_plano_conocida(
    "Adaptador_Rodamiento_03", "Transmisor_1_02a",
    "FICHA 03/02a: solape axial del manguito Ø20 mm de Plano 2a con la base de Plano 3"
)
for est_i, cie_i in (("1", "Cierre_Estructura_1_15"), ("2", "Cierre_Estructura_2_15")):
    for t_i in range(1, 5):
        ens.interferencia_plano_conocida(
            cie_i, f"Tensor_{t_i}_06",
            "FICHA 15/07: brida d_ext=176 mm (R=88 mm) roza tensores Ø22 en (69,69) (R_int=86.58 mm)"
        )

ens.cerrar()
