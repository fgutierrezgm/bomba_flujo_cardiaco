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
ens.parametro_global(4, "pos_tensor", "69.00 mm", "Semidistancia X/Y entre centros de tensores", origen="supuesto")

# 1. Tapas de extremo (Planos 16b y 16a)
tapa_int = ens.insertar(
    ruta_p("Tapa_Interior_16b.FCStd"), "Tapa_Interior_16b",
    lcs_pieza="LCS_Origen",
    offset=(0, 0, 0),
    explosion_vec=(0, 0, -40),
)

tapa_ext = ens.insertar(
    ruta_p("Tapa_Exterior_16a.FCStd"), "Tapa_Exterior_16a",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    offset=(0, 0, 281.0), rot_grados=(0, 0, 180),
    explosion_vec=(0, 0, 40),
)

# 2. Cilindro de vidrio borosilicato (Plano 9) apoyado en LCS_Piso_Tubo_110_5 de Tapa Interior
cilindro = ens.insertar(
    ruta_p("Cilindro_09.FCStd"), "Cilindro_09",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Piso_Tubo_110_5",
)

# 3. 2x Barras Guía (Plano 8) alineando su LCS_Hombro_Asiento con LCS_Guia_1 / LCS_Guia_2 de Tapa Interior
for i in (1, 2):
    ens.insertar(
        ruta_p("Guia_08.FCStd"), f"Guia_{i}_08",
        lcs_pieza="LCS_Hombro_Asiento",
        en_instancia=tapa_int, lcs_destino=f"LCS_Guia_{i}",
    )

# 4. 2x Sufridera Guía (Plano 5b) alineando su LCS_Cara_Sup con LCS_Guia_1 / LCS_Guia_2 de Tapa Interior
for i in (1, 2):
    ens.insertar(
        ruta_p("Sufridera_Guia_05b.FCStd"), f"Sufridera_Guia_{i}_05b",
        lcs_pieza="LCS_Cara_Sup",
        en_instancia=tapa_int, lcs_destino=f"LCS_Guia_{i}",
        explosion_vec=(0, 0, -15),
    )

# 5. Subconjunto móvil del Émbolo (Planos 10, 11, 12 y 2x Sensor Pistón 5b), gobernado por pos_embolo
embolo = ens.insertar(
    ruta_p("Embolo_Delrin_10.FCStd"), "Embolo_Delrin_10",
    lcs_pieza="LCS_Origen",
    offset=(0, 0, 130.0),
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo"},
)

ens.insertar(
    ruta_p("Centro_Embolo_1_11.FCStd"), "Centro_Embolo_1_11",
    lcs_pieza="LCS_Asiento_Brida",
    en_instancia=embolo, lcs_destino="LCS_Origen",
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo - 6 mm"},
    explosion_vec=(0, 0, -15),
)

ens.insertar(
    ruta_p("Centro_Embolo_2_12.FCStd"), "Centro_Embolo_2_12",
    lcs_pieza="LCS_Origen",
    en_instancia=embolo, lcs_destino="LCS_Cara_Sup",
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo + 20 mm"},
    explosion_vec=(0, 0, 15),
)

ens.insertar(
    ruta_p("Sensor_Piston_05b.FCStd"), "Sensor_Piston_1_05b",
    lcs_pieza="LCS_Asiento_Embolo",
    en_instancia=embolo, lcs_destino="LCS_Sensor_2",
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo + 12 mm"},
    explosion_vec=(0, 0, 20),
)

ens.insertar(
    ruta_p("Sensor_Piston_05b.FCStd"), "Sensor_Piston_2_05b",
    lcs_pieza="LCS_Asiento_Embolo",
    en_instancia=embolo, lcs_destino="LCS_Sensor_1",
    rot_grados=(0, 0, 180),
    expr_base={"z": "<<Parametros_Generales>>.pos_embolo + 8 mm"},
    explosion_vec=(0, 0, -20),
)

# 6. Husillo y Tren de Transmisión (Planos 14, 5a, 5b, 4, 3, 2b, 2a)
ens.insertar(
    ruta_p("Tornillo_Sin_Fin_14.FCStd"), "Tornillo_Sin_Fin_14",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    offset=(0, 0, 5.50),
)

ens.insertar(
    ruta_p("Sufridera_Eje_Ext_05a.FCStd"), "Sufridera_Eje_Ext_05a",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_ext, lcs_destino="LCS_Origen",
    offset=(0, 0, 8.0),
    explosion_vec=(0, 0, 55),
)

ens.insertar(
    ruta_p("Sufridera_Int_05b.FCStd"), "Sufridera_Int_05b",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    offset=(0, 0, 2.31),
    explosion_vec=(0, 0, -50),
)

ens.insertar(
    ruta_p("Tapa_Sufridera_Int_05a.FCStd"), "Tapa_Sufridera_Int_05a",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    offset=(0, 0, 0.0),
    explosion_vec=(0, 0, -60),
)

ens.insertar(
    ruta_p("Adaptador_Eje_04.FCStd"), "Adaptador_Eje_04",
    lcs_pieza="LCS_Cara_Superior",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    offset=(0, 0, 0.0),
    explosion_vec=(0, 0, -75),
)

ens.insertar(
    ruta_p("Adaptador_Rodamiento_03.FCStd"), "Adaptador_Rodamiento_03",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    offset=(0, 0, -22.0),
    explosion_vec=(0, 0, -95),
)

transm_2 = ens.insertar(
    ruta_p("Transmisor_2_02b.FCStd"), "Transmisor_2_02b",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    offset=(0, 0, -106.42),
    explosion_vec=(0, 0, -120),
)

ens.insertar(
    ruta_p("Transmisor_1_02a.FCStd"), "Transmisor_1_02a",
    lcs_pieza="LCS_Extremo_Der",
    en_instancia=transm_2, lcs_destino="LCS_Asiento_Rodamiento",
    offset=(0, 0, 0.0),
    explosion_vec=(0, 0, -150),
)

# 7. Anillos prensa-tórica (2x Plano 13), Estructura Interior (2x Plano 7), Cierres (2x Plano 15) y Tensores (4x Plano 6)
ens.insertar(
    ruta_p("Anillo_Torica_13.FCStd"), "Anillo_Torica_Int_13",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Origen",
    offset=(0, 0, 30.0),
    explosion_vec=(0, 0, -20),
)

ens.insertar(
    ruta_p("Anillo_Torica_13.FCStd"), "Anillo_Torica_Ext_13",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_ext, lcs_destino="LCS_Origen",
    offset=(0, 0, 30.0),
    explosion_vec=(0, 0, 20),
)

estruct_1 = ens.insertar(
    ruta_p("Estructura_Interior_07.FCStd"), "Estructura_Interior_1_07",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_int, lcs_destino="LCS_Asiento_Carcasa_145mm",
    offset=(0, 0, 0.0),
    explosion_vec=(0, 0, -25),
)

estruct_2 = ens.insertar(
    ruta_p("Estructura_Interior_07.FCStd"), "Estructura_Interior_2_07",
    lcs_pieza="LCS_Origen",
    en_instancia=tapa_ext, lcs_destino="LCS_Asiento_Carcasa_145mm",
    offset=(0, 0, 0.0),
    explosion_vec=(0, 0, 25),
)

ens.insertar(
    ruta_p("Cierre_Estructura_15.FCStd"), "Cierre_Estructura_1_15",
    lcs_pieza="LCS_Origen",
    en_instancia=estruct_1, lcs_destino="LCS_Asiento_Tapa",
    offset=(0, 0, 0.0),
    explosion_vec=(0, 0, -15),
)

ens.insertar(
    ruta_p("Cierre_Estructura_15.FCStd"), "Cierre_Estructura_2_15",
    lcs_pieza="LCS_Origen",
    en_instancia=estruct_2, lcs_destino="LCS_Asiento_Tapa",
    offset=(0, 0, 0.0),
    explosion_vec=(0, 0, 15),
)

for idx, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1)), 1):
    ens.insertar(
        ruta_p("Tensor_06.FCStd"), f"Tensor_{idx}_06",
        lcs_pieza="LCS_Origen",
        en_instancia=estruct_1, lcs_destino=f"LCS_Tensor_{idx}",
        offset=(0, 0, -102.0),
        explosion_vec=(sx * 25, sy * 25, 0),
    )

ens.cerrar()
