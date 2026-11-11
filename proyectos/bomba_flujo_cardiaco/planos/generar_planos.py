#!/usr/bin/env python3
"""
Generador automático del legajo completo de planos técnicos IRAM (TechDraw)
para el proyecto Bomba de Simulación de Flujo Cardíaco (FCAI - UNCUYO).

Contenido generado en `proyectos/bomba_flujo_cardiaco/planos/Planos_Bomba_Flujo_Cardiaco.FCStd`:
1. Hoja de cálculo `Datos_Rotulo`: campos maestros del rótulo FCAI-UNCUYO sincronizados
   automáticamente con todas las hojas de planos (estilo iProperties de Inventor).
2. Hoja de cálculo `Tabla_BOM_IRAM`: lista de materiales completa (27 ítems = 40 instancias)
   ordenada por secuencia de montaje (1..21 piezas fabricadas, 22..27 piezas comerciales).
3. `Plano_00a_Conjunto_Armado` (IRAM A2, Escala 1:2): Vista general frontal, Corte Longitudinal A-A,
   Vista Isométrica 3D y cotas generales del conjunto armado.
4. `Plano_00b_Vista_Explotada` (IRAM A2, Escala 1:2): Vista isométrica explotada con los 27 globos
   IRAM (`TechDraw::DrawViewBalloon`) dispuestos en sentido horario y numerados 1..27 en coincidencia
   exacta con `Tabla_BOM_IRAM` (sin dejar explotado el archivo `Piloto_Embolo_Assembly.FCStd`).
5. `Plano_00c_Lista_Materiales` (IRAM A3): Lámina de Lista de Materiales (IRAM 4508) con cantidades,
   denominación, número de plano, material, código comercial/norma, masa unitaria y resumen de bulonería.
6. `Plano_01` a `Plano_21` (21 planos de fabricación de piezas): Vistas ISO-E (Planta/Frente + Corte
   Longitudinal A-A + Isométrica), conmutación temporal a `modo_diseno = 2` (CNC/Planos, roscas a
   diámetro de mecha según Regla 3.4), cotas geométricas `TechDraw::DrawViewDimension` y cuadro
   técnico de parámetros, roscas y tolerancias extraído de la hoja `Parametros` de cada pieza.

Ejecución:
  /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/planos/generar_planos.py

Exportación opcional de PDFs bajo demanda (Regla 3.1: desactivada por defecto):
  EXPORTAR_PDF=1 /snap/bin/freecad.cmd proyectos/bomba_flujo_cardiaco/planos/generar_planos.py
"""
import math
import os
import sys
import FreeCAD as App
import Part

AQUI = os.path.dirname(
    os.path.abspath(
        globals().get(
            "__file__",
            "proyectos/bomba_flujo_cardiaco/planos/generar_planos.py",
        )
    )
)
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "_herramientas"))

from planos_iram import (
    FORMATOS_IRAM,
    acotar_vista_circular_iram,
    acotar_vista_perfil_o_corte_iram,
    asegurar_plantillas_iram,
    estilizar_vista_iram,
    generar_svg_bloque_cotas_pieza,
    generar_svg_tabla_bom_iram,
    seleccionar_formato_y_escala,
)

DIR_PROYECTO = os.path.abspath(os.path.join(AQUI, ".."))
DIR_PIEZAS = os.path.join(DIR_PROYECTO, "piezas")
DIR_ENSAMBLAJES = os.path.join(DIR_PROYECTO, "ensamblajes")
DIR_PLANOS = os.path.join(DIR_PROYECTO, "planos")
DIR_PLANTILLAS = os.path.join(RAIZ, "_plantillas")

RUTA_ASM = os.path.join(DIR_ENSAMBLAJES, "Piloto_Embolo_Assembly.FCStd")
RUTA_SALIDA_FCSTD = os.path.join(DIR_PLANOS, "Planos_Bomba_Flujo_Cardiaco.FCStd")


# Catálogo maestro de los 27 ítems del conjunto (1..21 piezas fabricadas + 22..27 comerciales)
# Ordenados por secuencia lógica de armado/despiece y con vectores de explosión 3D dedicados.
CATALOGO_ITEMS_BOM = [
    # --- PIEZAS FABRICADAS (Ítems 1 a 21) ---
    {
        "item": 1,
        "archivo": "Tapa_Exterior_16a.FCStd",
        "instancia_ref": "Tapa_Exterior_16a",
        "instancias": ["Tapa_Exterior_16a"],
        "denominacion": "Tapa Exterior Frontal",
        "plano_original": "Plano Nº 16a",
        "hoja_plano": "Plano_01_Tapa_Exterior_16a",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Brida ciega Ø200x12 mm; aloj. cilindro Ø110 H7; puerto M12x1 a 45°",
        "notas_taller": [
            "Tolerancia general de mecanizado: ISO 2768-mK.",
            "Alojamiento de camisa acrílica Ø110 H7 y asiento de O-Ring.",
            "Agujero roscado M12x1 (mecha Ø10.8 mm en Modo 2) inclinado a 45°.",
            "4 agujeros pasantes Ø18 mm en cuadrado de 138x138 mm para tensores.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, 0.0, -175.0),
    },
    {
        "item": 2,
        "archivo": "Cilindro_09.FCStd",
        "instancia_ref": "Cilindro_09",
        "instancias": ["Cilindro_09"],
        "denominacion": "Cilindro Acrílico (Camisa)",
        "plano_original": "Plano Nº 9",
        "hoja_plano": "Plano_02_Cilindro_09",
        "material": "Acrílico Transparente (PMMA)",
        "detalles": "Tubo calibrado Ø110 x Ø100 x 250 mm; interior bruñido Ra <= 0.4 um",
        "notas_taller": [
            "Tubo de PMMA extruido/colado transparente óptico sin porosidades.",
            "Diámetro interior Ø100 H8 pulido para deslizamiento de O-Ring NBR.",
            "Frenteado perpendicular al eje (perpendicularidad <= 0.05 mm).",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, 0.0, -90.0),
    },
    {
        "item": 3,
        "archivo": "Tapa_Interior_16b.FCStd",
        "instancia_ref": "Tapa_Interior_16b",
        "instancias": ["Tapa_Interior_16b"],
        "denominacion": "Tapa Interior Intermedia",
        "plano_original": "Plano Nº 16b",
        "hoja_plano": "Plano_03_Tapa_Interior_16b",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Brida intermedia Ø200x12 mm; paso de vástago y guías; puerto M12x1",
        "notas_taller": [
            "Tolerancia general ISO 2768-mK; paralelismo entre caras <= 0.03 mm.",
            "2 patrones de 4x M3 (mecha Ø2.5 mm) para fijar sufrideras de guías.",
            "Puerto inclinado M12x1 para sensor inductivo de carrera interior.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, 0.0, 0.0),
    },
    {
        "item": 4,
        "archivo": "Sufridera_Int_05b.FCStd",
        "instancia_ref": "Sufridera_Int_05b",
        "instancias": ["Sufridera_Int_05b"],
        "denominacion": "Sufridera Interior Portarretén",
        "plano_original": "Plano Nº 5b",
        "hoja_plano": "Plano_04_Sufridera_Int_05b",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Cuerpo Ø45x18 mm; alojamiento de retén Ø30 H7 x 7 mm; 4x M3",
        "notas_taller": [
            "Alojamiento de retén radial Ø30 H7 x 7 mm de profundidad.",
            "4 agujeros roscados M3x0.5 en DBC Ø38 mm para tapa de sufridera.",
        ],
        "es_comercial": False,
        "vec_exp": (-65.0, 65.0, 35.0),
    },
    {
        "item": 5,
        "archivo": "Tapa_Sufridera_Int_05a.FCStd",
        "instancia_ref": "Tapa_Sufridera_Int_05a",
        "instancias": ["Tapa_Sufridera_Int_05a"],
        "denominacion": "Tapa de Sufridera Interior",
        "plano_original": "Plano Nº 5a",
        "hoja_plano": "Plano_05_Tapa_Sufridera_Int_05a",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Brida de retención Ø45x7 mm; paso central Ø20 mm; 4x Ø3.4 mm",
        "notas_taller": [
            "4 agujeros pasantes Ø3.4 mm en DBC Ø38 mm para tornillos M3.",
            "Rebaje escalonado concéntrico con Sufridera Interior (Plano 5b).",
        ],
        "es_comercial": False,
        "vec_exp": (-95.0, 95.0, 65.0),
    },
    {
        "item": 6,
        "archivo": "Sufridera_Guia_05b.FCStd",
        "instancia_ref": "Sufridera_Guia_1_05b",
        "instancias": ["Sufridera_Guia_1_05b", "Sufridera_Guia_2_05b"],
        "denominacion": "Sufridera de Barra Guía",
        "plano_original": "Plano Nº 5b",
        "hoja_plano": "Plano_06_Sufridera_Guia_05b",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Portabuje guía Ø34x20 mm; alojamiento Ø14 H7; brida con 4x Ø3.4 mm",
        "notas_taller": [
            "Alojamiento central pasante Ø14 H7 para buje de bronce 12x14x20.",
            "4 agujeros pasantes Ø3.4 mm en DBC Ø26 mm para fijación M3 a Tapa 16b.",
        ],
        "es_comercial": False,
        "vec_exp": (85.0, -85.0, 35.0),
    },
    {
        "item": 7,
        "archivo": "Embolo_Delrin_10.FCStd",
        "instancia_ref": "Embolo_Delrin_10",
        "instancias": ["Embolo_Delrin_10"],
        "denominacion": "Émbolo Principal (Pistón)",
        "plano_original": "Plano Nº 10",
        "hoja_plano": "Plano_07_Embolo_Delrin_10",
        "material": "Delrin (POM - Acetal)",
        "detalles": "Disco Ø99x25 mm; ranura perimetral O-Ring Ø97x3.5; 2x M6 guías; 4x M3",
        "notas_taller": [
            "Mecanizado en acetal (POM) blanco; diámetro exterior Ø99.0 -0.05/-0.10 mm.",
            "Ranura perimetral para O-Ring Ø97x3.5 mm sin aristas cortantes.",
            "2 agujeros roscados M6x1 en DBC Ø70 mm para barras guía y 4x M3 centrales.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, 95.0, -70.0),
    },
    {
        "item": 8,
        "archivo": "Centro_Embolo_1_11.FCStd",
        "instancia_ref": "Centro_Embolo_1_11",
        "instancias": ["Centro_Embolo_1_11"],
        "denominacion": "Centro de Émbolo 1 (Núcleo)",
        "plano_original": "Plano Nº 11",
        "hoja_plano": "Plano_08_Centro_Embolo_1_11",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Núcleo Ø54/Ø34x25 mm; rosca central M12x1.75; 4x Ø3.4 y 3x M3",
        "notas_taller": [
            "Rosca central M12x1.75 (mecha Ø10.2 mm en Modo 2) perpendicular a la base.",
            "Ajuste deslizante del cubo Ø34 g6 en el alojamiento central del Émbolo Delrin.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, 145.0, -45.0),
    },
    {
        "item": 9,
        "archivo": "Centro_Embolo_2_12.FCStd",
        "instancia_ref": "Centro_Embolo_2_12",
        "instancias": ["Centro_Embolo_2_12"],
        "denominacion": "Centro de Émbolo 2 (Contratapa)",
        "plano_original": "Plano Nº 12",
        "hoja_plano": "Plano_09_Centro_Embolo_2_12",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Tapa anular Ø54x5 mm; agujero central Ø15 mm; 3x pasantes Ø3.4 mm",
        "notas_taller": [
            "3 agujeros pasantes Ø3.4 mm en DBC Ø44 mm coincidiendo con Centro Émbolo 1.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, 185.0, -25.0),
    },
    {
        "item": 10,
        "archivo": "Sensor_Piston_05b.FCStd",
        "instancia_ref": "Sensor_Piston_1_05b",
        "instancias": ["Sensor_Piston_1_05b", "Sensor_Piston_2_05b"],
        "denominacion": "Target Magnético de Pistón",
        "plano_original": "Plano Nº 5b (Inf.)",
        "hoja_plano": "Plano_10_Sensor_Piston_05b",
        "material": "Acero Inox. Ferrítico AISI 430",
        "detalles": "Buje objetivo inductivo Ø12xØ6x10 mm (material ferromagnético obligatorio)",
        "notas_taller": [
            "CRÍTICO: Fabricar en AISI 430 o SAE 1045 niquelado (ferromagnético) para disparo de sensor LJ12A3.",
        ],
        "es_comercial": False,
        "vec_exp": (-85.0, -85.0, -65.0),
    },
    {
        "item": 11,
        "archivo": "Guia_08.FCStd",
        "instancia_ref": "Guia_1_08",
        "instancias": ["Guia_1_08", "Guia_2_08"],
        "denominacion": "Barra Guía de Émbolo",
        "plano_original": "Plano Nº 8",
        "hoja_plano": "Plano_11_Guia_08",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Vástago rectificado Ø12 g6 x 195 mm; espiga roscada M6x1 x 10 mm",
        "notas_taller": [
            "Superficie cilíndrica Ø12 g6 rectificada y pulida (Ra <= 0.4 um) para bujes guía.",
            "Espiga extrema roscada M6x1 concéntrica con el vástago.",
        ],
        "es_comercial": False,
        "vec_exp": (115.0, 0.0, 75.0),
    },
    {
        "item": 12,
        "archivo": "Transmisor_1_02a.FCStd",
        "instancia_ref": "Transmisor_1_02a",
        "instancias": ["Transmisor_1_02a"],
        "denominacion": "Eje Transmisor 1 (Vástago)",
        "plano_original": "Plano Nº 2a",
        "hoja_plano": "Plano_12_Transmisor_1_02a",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Vástago principal Ø14 h7 / Ø12 x 250 mm; rosca M12x1.75; 2x Ø4 pasador",
        "notas_taller": [
            "Tramo Ø14 h7 rectificado (Ra <= 0.4 um) en zona de labio del retén 14x30x7.",
            "2 agujeros transversales Ø4 H11 en espiga posterior para pasadores elásticos.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, -110.0, 40.0),
    },
    {
        "item": 13,
        "archivo": "Transmisor_2_02b.FCStd",
        "instancia_ref": "Transmisor_2_02b",
        "instancias": ["Transmisor_2_02b"],
        "denominacion": "Eje Transmisor 2 (Manguito)",
        "plano_original": "Plano Nº 2b",
        "hoja_plano": "Plano_13_Transmisor_2_02b",
        "material": "Acero Inoxidable AISI 304",
        "detalles": "Acople tubular Ø20 / Ø14.5 x 98 mm; alojamientos Ø12 H7 y 3x Ø4 pasador",
        "notas_taller": [
            "Alojamientos interiores Ø12 H7 concéntricos para espigas de Transmisor 1 y Tornillo Sin Fin.",
            "3 agujeros transversales pasantes Ø4 H11 para pasadores elásticos ISO 8752.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, -130.0, 125.0),
    },
    {
        "item": 14,
        "archivo": "Tornillo_Sin_Fin_14.FCStd",
        "instancia_ref": "Tornillo_Sin_Fin_14",
        "instancias": ["Tornillo_Sin_Fin_14"],
        "denominacion": "Tornillo Sin Fin (Husillo)",
        "plano_original": "Plano Nº 14 (Sup.)",
        "hoja_plano": "Plano_14_Tornillo_Sin_Fin_14",
        "material": "Acero SAE 1045",
        "detalles": "Husillo de potencia Ø18 / espiga Ø12 x 237 mm; agujero transversal Ø4",
        "notas_taller": [
            "Espiga delantera Ø12 g6 x 35 mm con agujero transversal Ø4 mm para pasador.",
            "Coaxialidad entre tramo roscado Ø18 y espiga Ø12 <= 0.02 mm.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, 0.0, 265.0),
    },
    {
        "item": 15,
        "archivo": "Adaptador_Rodamiento_03.FCStd",
        "instancia_ref": "Adaptador_Rodamiento_03",
        "instancias": ["Adaptador_Rodamiento_03"],
        "denominacion": "Adaptador de Rodamiento",
        "plano_original": "Plano Nº 3",
        "hoja_plano": "Plano_15_Adaptador_Rodamiento_03",
        "material": "Acero SAE 1045",
        "detalles": "Manguito escalonado Ø45/Ø26 x 48.5 mm; paso interior Ø16 mm (holgura T2)",
        "notas_taller": [
            "Agujero interior actualizado a Ø16.0 mm para libre paso del cuello Ø14.5 de Transmisor 2.",
            "6 agujeros pasantes Ø4.5 mm en brida Ø45 mm.",
        ],
        "es_comercial": False,
        "vec_exp": (-110.0, 40.0, 130.0),
    },
    {
        "item": 16,
        "archivo": "Sufridera_Eje_Ext_05a.FCStd",
        "instancia_ref": "Sufridera_Eje_Ext_05a",
        "instancias": ["Sufridera_Eje_Ext_05a"],
        "denominacion": "Sufridera de Eje Exterior",
        "plano_original": "Plano Nº 5a (Sup.)",
        "hoja_plano": "Plano_16_Sufridera_Eje_Ext_05a",
        "material": "Acero SAE 1045",
        "detalles": "Caja portarrodamiento Ø45x24 mm; alojamiento Ø32 H7 para SKF 6201",
        "notas_taller": [
            "Alojamiento interior Ø32 H7 x 10 mm para rodamiento rígido de bolas SKF 6201.",
        ],
        "es_comercial": False,
        "vec_exp": (-135.0, -30.0, 185.0),
    },
    {
        "item": 17,
        "archivo": "Adaptador_Eje_04.FCStd",
        "instancia_ref": "Adaptador_Eje_04",
        "instancias": ["Adaptador_Eje_04"],
        "denominacion": "Adaptador del Eje",
        "plano_original": "Plano Nº 4",
        "hoja_plano": "Plano_17_Adaptador_Eje_04",
        "material": "Delrin (POM - Acetal)",
        "detalles": "Cuerpo Ø57x16.5 mm; paso interior Ø40.1 mm; 4x Ø3.1 y 4x M3 en DBC Ø50 mm",
        "notas_taller": [
            "Mecanizado en Delrin / POM blanco; tolerancia general ISO 2768-mK.",
            "4 agujeros pasantes Ø3.1 mm con cajeado Ø4.5 x 5 mm a 0/90/180/270°.",
            "4 agujeros roscados M3x0.5 a 45/135/225/315° en DBC Ø50 mm.",
        ],
        "es_comercial": False,
        "vec_exp": (-80.0, -60.0, 95.0),
    },
    {
        "item": 18,
        "archivo": "Anillo_Torica_13.FCStd",
        "instancia_ref": "Anillo_Torica_Int_13",
        "instancias": ["Anillo_Torica_Int_13", "Anillo_Torica_Ext_13"],
        "denominacion": "Anillo de Junta Tórica",
        "plano_original": "Plano Nº 13",
        "hoja_plano": "Plano_18_Anillo_Torica_13",
        "material": "PVC Rígido",
        "detalles": "Anillo plano Ø140 x Ø111.5 x 5 mm; 6 agujeros avellanados a 90° en DBC Ø130 mm",
        "notas_taller": [
            "Mecanizado en PVC rígido o Delrin.",
            "6 agujeros pasantes Ø3.1 mm con avellanado a 90° Ø3.5 mm en DBC Ø130 mm.",
        ],
        "es_comercial": False,
        "vec_exp": (0.0, 0.0, -135.0),
    },
    {
        "item": 19,
        "archivo": "Estructura_Interior_07.FCStd",
        "instancia_ref": "Estructura_Interior_1_07",
        "instancias": ["Estructura_Interior_1_07", "Estructura_Interior_2_07"],
        "denominacion": "Anillo de Estructura Interior",
        "plano_original": "Plano Nº 7",
        "hoja_plano": "Plano_19_Estructura_Interior_07",
        "material": "Acero SAE 1045",
        "detalles": "Brida anular Ø176 x Ø110 x 17 mm; rebaje Ø140x5 mm; 4x M5 en DBC Ø158 mm",
        "notas_taller": [
            "4 agujeros roscados M5x0.8 (mecha Ø4.2 mm en Modo 2) en DBC Ø158 mm.",
            "Alojamiento Ø140 H8 x 5 mm para anillo de cierre y junta tórica.",
        ],
        "es_comercial": False,
        "vec_exp": (-115.0, 115.0, 110.0),
    },
    {
        "item": 20,
        "archivo": "Cierre_Estructura_15.FCStd",
        "instancia_ref": "Cierre_Estructura_1_15",
        "instancias": ["Cierre_Estructura_1_15", "Cierre_Estructura_2_15"],
        "denominacion": "Brida de Cierre de Estructura",
        "plano_original": "Plano Nº 15",
        "hoja_plano": "Plano_20_Cierre_Estructura_15",
        "material": "Acero SAE 1045",
        "detalles": "Anillo de cierre Ø176 x Ø94 x 12 mm; encastre Ø140x5 mm; 4x Ø5.5",
        "notas_taller": [
            "4 agujeros pasantes Ø5.5 mm en DBC Ø158 mm para tornillos M5.",
        ],
        "es_comercial": False,
        "vec_exp": (115.0, 115.0, 165.0),
    },
    {
        "item": 21,
        "archivo": "Tensor_06.FCStd",
        "instancia_ref": "Tensor_1_06",
        "instancias": ["Tensor_1_06", "Tensor_2_06", "Tensor_3_06", "Tensor_4_06"],
        "denominacion": "Tensor Estructural de la Bomba",
        "plano_original": "Plano Nº 6",
        "hoja_plano": "Plano_21_Tensor_06",
        "material": "Acero SAE 1045",
        "detalles": "Barra tensora Ø22 x 288 mm; extremos roscados M16x2 x 25 mm",
        "notas_taller": [
            "Hombros a 238 mm entre caras de apoyo; roscas extremas M16x2.",
        ],
        "es_comercial": False,
        "vec_exp": (130.0, 95.0, -40.0),
    },
    # --- COMPONENTES COMERCIALES NORMALIZADOS (Ítems 22 a 27) ---
    {
        "item": 22,
        "archivo": "Rodamiento_SKF_6201.FCStd",
        "instancia_ref": "Rodamiento_SKF_6201",
        "instancias": ["Rodamiento_SKF_6201"],
        "denominacion": "Rodamiento Rígido de Bolas",
        "plano_original": "Comercial SKF",
        "hoja_plano": None,
        "material": "Acero al Cromo SAE 52100",
        "detalles": "Código comercial: SKF 6201-2Z / Norma DIN 625-1 (Ø12 x Ø32 x 10 mm)",
        "notas_taller": [],
        "es_comercial": True,
        "vec_exp": (-145.0, -75.0, 160.0),
    },
    {
        "item": 23,
        "archivo": "Reten_14x30x7.FCStd",
        "instancia_ref": "Reten_14x30x7",
        "instancias": ["Reten_14x30x7"],
        "denominacion": "Retén Radial de Eje",
        "plano_original": "Comercial DIN 3760",
        "hoja_plano": None,
        "material": "Elastómero NBR + Alma Acero",
        "detalles": "Código comercial: Retén DBH / SAV 14x30x7 — Norma DIN 3760 Forma A",
        "notas_taller": [],
        "es_comercial": True,
        "vec_exp": (-80.0, 80.0, 50.0),
    },
    {
        "item": 24,
        "archivo": "Buje_Guia_12x14x20.FCStd",
        "instancia_ref": "Buje_Guia_1",
        "instancias": ["Buje_Guia_1", "Buje_Guia_2"],
        "denominacion": "Buje Guía Autolubricado",
        "plano_original": "Comercial DIN 1850",
        "hoja_plano": None,
        "material": "Bronce Sinterizado SAE 660",
        "detalles": "Código comercial: Buje cilíndrico DIN 1850 / ISO 2795 — Ø12 x Ø14 x 20 mm",
        "notas_taller": [],
        "es_comercial": True,
        "vec_exp": (105.0, -105.0, 55.0),
    },
    {
        "item": 25,
        "archivo": "ORing_Embolo_97x3_5.FCStd",
        "instancia_ref": "ORing_Embolo",
        "instancias": ["ORing_Embolo"],
        "denominacion": "O-Ring de Émbolo Principal",
        "plano_original": "Comercial ISO 3601",
        "hoja_plano": None,
        "material": "Caucho Nitrílico NBR 70 Shore A",
        "detalles": "Código comercial: O-Ring métrico Parker / DBH Ø97.0 x 3.5 mm (ISO 3601)",
        "notas_taller": [],
        "es_comercial": True,
        "vec_exp": (0.0, 120.0, -90.0),
    },
    {
        "item": 26,
        "archivo": "Pasador_Cilindrico_4x18.FCStd",
        "instancia_ref": "Pasador_Transm_1",
        "instancias": ["Pasador_Transm_1", "Pasador_Transm_2", "Pasador_Transm_3"],
        "denominacion": "Pasador Elástico de Transmisión",
        "plano_original": "Comercial ISO 8752",
        "hoja_plano": None,
        "material": "Acero para Muelles DIN 17222",
        "detalles": "Código comercial: Espina elástica ranurada pesada ISO 8752 / DIN 1481 — Ø4 x 14 mm",
        "notas_taller": [],
        "es_comercial": True,
        "vec_exp": (45.0, -145.0, 110.0),
    },
    {
        "item": 27,
        "archivo": "Sensor_Inductivo_LJ12A3.FCStd",
        "instancia_ref": "Sensor_Inductivo_Int",
        "instancias": ["Sensor_Inductivo_Int", "Sensor_Inductivo_Ext"],
        "denominacion": "Sensor de Proximidad Inductivo",
        "plano_original": "Comercial M12x1",
        "hoja_plano": None,
        "material": "Latón Niquelado + ABS",
        "detalles": "Código comercial: LJ12A3-4-Z/BX (M12x1, NPN NO, Sn=4 mm, 6-36 VDC)",
        "notas_taller": [],
        "es_comercial": True,
        "vec_exp": (-125.0, 0.0, -25.0),
    },
]

RESUMEN_BULONERIA_ESTANDAR = [
    "16x Tuerca Hexagonal M16x2 — Norma DIN 934 / ISO 4032 (Acero cincado grado 8) + 16x Arandela plana DIN 125 A17.",
    "8x Tornillo Allen Cilíndrico M5x16 — Norma DIN 912 / ISO 4762 (Inox A2-70) para Cierre de Estructura (Ítems 19 y 21).",
    "8x Tornillo Allen Cilíndrico M3x12 — Norma DIN 912 / ISO 4762 (Inox A2-70) para Sufrideras de Guía (Ítem 6 a Ítem 3).",
    "4x Tornillo Allen Cilíndrico M3x10 — Norma DIN 912 / ISO 4762 (Inox A2-70) para Tapa Sufridera Interior (Ítem 5 a Ítem 4).",
    "4x Tornillo Allen Cabeza Fresada M3x12 — Norma DIN 7991 / ISO 10642 (Inox A2-70) para Centro de Émbolo 1 a Delrin.",
    "3x Tornillo Allen Cilíndrico M3x10 — Norma DIN 912 / ISO 4762 (Inox A2-70) para Centro de Émbolo 2 a Centro de Émbolo 1.",
]


def _extraer_shape_solido_documento(doc_pieza, modo_diseno_forzado=None):
    """
    Abre o toma un documento de pieza, opcionalmente conmuta su `modo_diseno` (por ejemplo a 2
    para planos CNC donde las roscas se muestran a diámetro de mecha según Regla 3.4),
    extrae una copia independiente de su `Shape` y su masa en gramos, y restaura el modo original.
    """
    sp = doc_pieza.getObject("Parametros")
    modo_orig = None
    if sp and modo_diseno_forzado is not None:
        try:
            modo_orig = str(sp.get("B2")).strip()
            if modo_orig != str(modo_diseno_forzado):
                sp.set("B2", str(modo_diseno_forzado))
                doc_pieza.recompute()
        except Exception:
            modo_orig = None

    part_obj = next((o for o in doc_pieza.Objects if o.TypeId == "App::Part"), None)
    solido_principal = None
    if part_obj:
        # Buscar el último sólido visible o el que contiene "_Solido"
        candidatos = [
            o
            for o in part_obj.Group
            if o.isDerivedFrom("Part::Feature")
            and not o.isDerivedFrom("Part::Datum")
            and getattr(o, "Shape", None)
            and o.Shape.Solids
        ]
        for c in candidatos:
            if c.Name.endswith("_Solido"):
                solido_principal = c
                break
        if not solido_principal and candidatos:
            solido_principal = candidatos[-1]

    if solido_principal is None:
        shape_copia = Part.getShape(part_obj) if part_obj else Part.Shape()
    else:
        shape_copia = solido_principal.Shape.copy()

    # Masa unitaria desde Reporte_Fisico o calculada por volumen
    masa_g = 0.0
    rf = doc_pieza.getObject("Reporte_Fisico")
    if rf:
        try:
            masa_g = float(rf.get("masa_g"))
        except Exception:
            masa_g = 0.0
    if masa_g <= 0.0 and shape_copia and not shape_copia.isNull():
        hm = doc_pieza.getObject("Materiales")
        dens = 7850.0
        if hm:
            try:
                dens = float(hm.get("densidad"))
            except Exception:
                pass
        masa_g = (shape_copia.Volume * 1e-9) * dens * 1000.0

    # Extraer filas de parámetros funcionales para el cuadro técnico
    filas_param = []
    if sp:
        for fila in range(2, 60):
            try:
                alias = sp.getAlias(f"B{fila}")
            except Exception:
                alias = None
            if not alias:
                continue
            if alias in ("modo_diseno", "escala", "holgura_fdm", "esc", "holgura") or alias.startswith("mej_"):
                continue
            try:
                val = sp.get(f"B{fila}")
                unid = sp.get(f"C{fila}") or "mm"
                desc = sp.get(f"E{fila}") or alias
                if isinstance(val, (int, float)):
                    val_str = f"{float(val):.2f} {unid}".strip()
                else:
                    val_str = f"{val} {unid}".strip()
                filas_param.append((alias, val_str, str(desc)))
            except Exception:
                pass

    # Restaurar modo original si fue cambiado
    if sp and modo_orig is not None and str(modo_diseno_forzado) != modo_orig:
        try:
            sp.set("B2", modo_orig)
            doc_pieza.recompute()
        except Exception:
            pass

    return shape_copia, masa_g, filas_param


def crear_hoja_datos_rotulo(doc):
    """
    Crea la hoja maestra `Datos_Rotulo` que gobierna todos los rótulos del documento.
    Cualquier cambio en la columna B actualiza automáticamente las 24 láminas gracias
    a `MaterialSyncObserver.sincronizar_rotulos_planos`.
    """
    dr = doc.addObject("Spreadsheet::Sheet", "Datos_Rotulo")
    dr.Label = "Datos_Rotulo"
    dr.set("A1", "CAMPO_ROTULO")
    dr.set("B1", "VALOR_GLOBAL")
    dr.set("C1", "DESCRIPCION")

    campos = [
        ("INSTITUCION", "Facultad de Ciencias Aplicadas a la Industria - UNCUYO", "Institución académica"),
        ("CARRERA", "Ingeniería Mecánica", "Carrera / Especialidad"),
        ("CATEDRA", "Máquinas Térmicas e Hidráulicas", "Asignatura / Cátedra"),
        ("CURSO", "4to Año - Segundo semestre", "Curso / Año de cursado"),
        ("PROFESOR", "Profesor: Analía Bonino", "Docente responsable"),
        ("PROYECTO", "Diseño y construcción de una bomba de simulación de flujo cardíaco", "Nombre del proyecto"),
        ("AUTOR", "Dib.: F. Gutiérrez", "Autor / Dibujante de los planos"),
        ("APROBADO", "Apr.: Ing. A. Bonino", "Revisión y aprobación"),
        ("FECHA", "10/11/2026", "Fecha de emisión del legajo"),
        ("TOL_GRAL", "ISO 2768-mK", "Tolerancia general de fabricación"),
    ]
    campos_dict = {}
    for idx, (clave, valor, desc) in enumerate(campos, start=2):
        dr.set(f"A{idx}", clave)
        dr.set(f"B{idx}", f"'{valor}'")
        dr.set(f"C{idx}", f"'{desc}'")
        campos_dict[clave] = valor
        try:
            dr.setAlias(f"B{idx}", clave.lower())
        except Exception:
            pass
    return dr, campos_dict


def crear_hoja_tabla_bom_iram(doc, items_bom):
    """Crea la hoja de cálculo nativa `Tabla_BOM_IRAM` con los 27 ítems del conjunto."""
    tb = doc.addObject("Spreadsheet::Sheet", "Tabla_BOM_IRAM")
    tb.Label = "Tabla_BOM_IRAM"
    encabezados = [
        ("A1", "ITEM"),
        ("B1", "CANT"),
        ("C1", "DENOMINACION"),
        ("D1", "PLANO_REF"),
        ("E1", "MATERIAL"),
        ("F1", "NORMA_CODIGO_DETALLES"),
        ("G1", "MASA_UNIT_G"),
        ("H1", "MASA_TOTAL_G"),
        ("I1", "TIPO"),
    ]
    for celda, texto in encabezados:
        tb.set(celda, texto)

    masa_total_conjunto = 0.0
    for idx, it in enumerate(items_bom, start=2):
        masa_sub = it["masa_g"] * it["cantidad"]
        masa_total_conjunto += masa_sub
        tb.set(f"A{idx}", str(it["item"]))
        tb.set(f"B{idx}", str(it["cantidad"]))
        tb.set(f"C{idx}", f"'{it['denominacion']}'")
        tb.set(f"D{idx}", f"'{it['plano_original']}'")
        tb.set(f"E{idx}", f"'{it['material']}'")
        tb.set(f"F{idx}", f"'{it['detalles']}'")
        tb.set(f"G{idx}", f"{it['masa_g']:.2f}")
        tb.set(f"H{idx}", f"{masa_sub:.2f}")
        tb.set(f"I{idx}", "'COMERCIAL'" if it["es_comercial"] else "'FABRICADA'")

    fila_tot = len(items_bom) + 2
    tb.set(f"F{fila_tot}", "'MASA TOTAL ESTIMADA DEL CONJUNTO (g):'")
    tb.set(f"H{fila_tot}", f"{masa_total_conjunto:.2f}")
    return tb, masa_total_conjunto


def generar_svg_recuadro_subensamblaje(titulo, subtexto, ancho_mm, alto_mm):
    """Genera un marco técnico SVG con cabecera destacada para delimitar subensamblajes."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{ancho_mm:.1f}mm" height="{alto_mm:.1f}mm" viewBox="0 0 {ancho_mm:.1f} {alto_mm:.1f}">
  <rect x="0.5" y="0.5" width="{ancho_mm - 1.0:.1f}" height="{alto_mm - 1.0:.1f}" fill="#fafcff" stroke="#254a6e" stroke-width="0.50" stroke-dasharray="5,2" rx="2"/>
  <rect x="0.5" y="0.5" width="{ancho_mm - 1.0:.1f}" height="7.8" fill="#e8f0fe" stroke="#254a6e" stroke-width="0.50" rx="2"/>
  <text x="4.5" y="5.3" font-family="Liberation Sans, Arial, sans-serif" font-size="2.9" font-weight="bold" fill="#17324d">{titulo}</text>
  <text x="{ancho_mm - 4.5:.1f}" y="5.3" font-family="Liberation Sans, Arial, sans-serif" font-size="2.5" font-weight="bold" fill="#254a6e" text-anchor="end">{subtexto}</text>
</svg>"""


def agregar_globo_item(doc, page, vista, it_num, pt3d, pt_centro_comp, escala, dx, dy, prefijo):
    """
    Coloca un globo de despiece IRAM (TechDraw::DrawViewBalloon) con origen en la posición 2D
    exacta de la pieza y etiqueta desplazada (dx, dy).
    """
    u_hat = App.Vector(1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0), 0.0)
    v_hat = App.Vector(-1.0 / math.sqrt(6.0), 1.0 / math.sqrt(6.0), 2.0 / math.sqrt(6.0))
    ox = (pt3d.dot(u_hat) - pt_centro_comp.dot(u_hat)) * escala
    oy = (pt3d.dot(v_hat) - pt_centro_comp.dot(v_hat)) * escala
    globo = doc.addObject("TechDraw::DrawViewBalloon", f"Globo_{prefijo}_{it_num:02d}")
    page.addView(globo)
    globo.SourceView = vista
    globo.BubbleShape = "Circular"
    globo.EndType = "Filled arrow"
    globo.Text = str(it_num)
    globo.OriginX = ox
    globo.OriginY = oy
    globo.X = ox + dx
    globo.Y = oy + dy
    return globo


def _crear_pagina_iram(doc, nombre_obj, etiqueta, formato, rutas_plantillas, textos_rotulo):
    page = doc.addObject("TechDraw::DrawPage", nombre_obj)
    page.Label = etiqueta
    page.KeepUpdated = True

    tmpl = doc.addObject("TechDraw::DrawSVGTemplate", f"Template_{nombre_obj}")
    tmpl.Template = rutas_plantillas[formato]
    page.Template = tmpl

    et = dict(tmpl.EditableTexts)
    for k, v in textos_rotulo.items():
        if k in et:
            et[k] = str(v)
    tmpl.EditableTexts = et
    return page, tmpl


def main():
    print("FreeCAD", ".".join(App.Version()[:3]))
    os.makedirs(DIR_PLANOS, exist_ok=True)
    rutas_plantillas = asegurar_plantillas_iram(DIR_PLANTILLAS)

    # 1. Abrir el ensamblaje Piloto_Embolo_Assembly para leer los Placements de las 40 instancias
    if not os.path.exists(RUTA_ASM):
        raise FileNotFoundError(f"No se encontró el ensamblaje: {RUTA_ASM}")
    doc_asm = App.openDocument(RUTA_ASM, True)
    asm_obj = next((o for o in doc_asm.Objects if o.TypeId == "Assembly::AssemblyObject"), None)
    if asm_obj is None:
        raise RuntimeError("No se encontró el objeto Assembly::AssemblyObject en Piloto_Embolo_Assembly.FCStd")

    placements_instancias = {}
    for o in asm_obj.Group:
        if o.TypeId == "App::Link":
            placements_instancias[o.Name] = App.Placement(o.Placement)

    # 2. Extraer Shapes en Modo 2 (CNC/Planos), masas y parámetros de las 27 piezas del catálogo
    datos_piezas = {}
    items_bom_completos = []

    for entrada in CATALOGO_ITEMS_BOM:
        ruta_fcstd = os.path.join(DIR_PIEZAS, entrada["archivo"])
        doc_p = next(
            (d for d in App.listDocuments().values() if os.path.abspath(getattr(d, "FileName", "")) == os.path.abspath(ruta_fcstd)),
            None,
        )
        if doc_p is None:
            doc_p = App.openDocument(ruta_fcstd, True)

        modo_forzado = 2 if not entrada["es_comercial"] else None
        shape_p, masa_g, filas_param = _extraer_shape_solido_documento(doc_p, modo_diseno_forzado=modo_forzado)
        datos_piezas[entrada["item"]] = {
            "shape": shape_p,
            "masa_g": masa_g,
            "filas_param": filas_param,
            "entrada": entrada,
        }
        items_bom_completos.append(
            {
                "item": entrada["item"],
                "cantidad": len(entrada["instancias"]),
                "denominacion": entrada["denominacion"],
                "plano_ref": entrada["plano_original"],
                " plano_original": entrada["plano_original"],
                "plano_original": entrada["plano_original"],
                "material": entrada["material"],
                "detalles": entrada["detalles"],
                "masa_g": masa_g,
                "es_comercial": entrada["es_comercial"],
            }
        )

    # 3. Crear documento maestro de planos
    doc_planos = App.newDocument("Planos_Bomba_Flujo_Cardiaco")
    dr, campos_base_rotulo = crear_hoja_datos_rotulo(doc_planos)
    _, masa_total_g = crear_hoja_tabla_bom_iram(doc_planos, items_bom_completos)
    doc_planos.recompute()
    total_hojas = 3 + sum(1 for e in CATALOGO_ITEMS_BOM if not e["es_comercial"])  # 24 hojas en total

    # Contenedor oculto para los sólidos auxiliares de proyección (Modo 2)
    grupo_fuentes = doc_planos.addObject("App::DocumentObjectGroup", "Modelos_Fuente_TechDraw")
    grupo_fuentes.Label = "Modelos_Fuente_TechDraw"

    # =========================================================================
    # HOJA 1: PLANO 00a - CONJUNTO GENERAL ARMADO Y CORTE LONGITUDINAL (A2, 1:2)
    # =========================================================================
    shapes_armadas = []
    for entrada in CATALOGO_ITEMS_BOM:
        sh_base = datos_piezas[entrada["item"]]["shape"]
        for inst_name in entrada["instancias"]:
            plc = placements_instancias.get(inst_name)
            if plc is not None and not sh_base.isNull():
                sh_inst = sh_base.copy()
                sh_inst.Placement = plc.multiply(sh_inst.Placement)
                shapes_armadas.append(sh_inst)

    comp_armado = Part.makeCompound(shapes_armadas)
    obj_armado = doc_planos.addObject("Part::Feature", "Conjunto_Armado_Solido")
    obj_armado.Shape = comp_armado
    if getattr(obj_armado, "ViewObject", None):
        obj_armado.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_armado)

    rotulo_00a = dict(campos_base_rotulo)
    rotulo_00a.update(
        {
            "ESCALA": "1:2",
            "FORMATO": "IRAM A2",
            "HOJA": f"1/{total_hojas}",
            "TITULO": "Conjunto General Armado y Corte Longitudinal",
            "MATERIAL": "Conjunto Multimaterial",
            "MASA": f"Masa: {masa_total_g / 1000.0:.2f} kg",
            "NUM_PLANO": "Plano Nº 0a",
        }
    )
    page_00a, _ = _crear_pagina_iram(
        doc_planos,
        "Plano_00a_Conjunto_Armado",
        "Plano_00a_Conjunto_Armado",
        "A2",
        rutas_plantillas,
        rotulo_00a,
    )

    # Vista Frontal longitudinal (eje Z horizontal o vertical; ponemos eje Z vertical e X horizontal)
    v_arm_frente = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Frente")
    page_00a.addView(v_arm_frente)
    v_arm_frente.Source = [obj_armado]
    v_arm_frente.Direction = App.Vector(0, -1, 0)
    v_arm_frente.XDirection = App.Vector(1, 0, 0)
    v_arm_frente.ScaleType = "Custom"
    v_arm_frente.Scale = 0.5
    v_arm_frente.X = 120.0
    v_arm_frente.Y = 215.0
    v_arm_frente.Caption = "Vista Frontal Exterior (Escala 1:2)"
    estilizar_vista_iram(v_arm_frente, mostrar_ocultas=False, mostrar_centros=True)

    # Corte Longitudinal A-A pasando por el plano XZ central
    v_arm_corte = doc_planos.addObject("TechDraw::DrawViewSection", "V00a_Corte_AA")
    page_00a.addView(v_arm_corte)
    v_arm_corte.BaseView = v_arm_frente
    v_arm_corte.Source = [obj_armado]
    v_arm_corte.SectionNormal = App.Vector(0, -1, 0)
    v_arm_corte.SectionDirection = "Right"
    v_arm_corte.SectionOrigin = App.Vector(0, 0, 210)
    v_arm_corte.SectionSymbol = "A"
    v_arm_corte.ScaleType = "Custom"
    v_arm_corte.Scale = 0.5
    v_arm_corte.X = 285.0
    v_arm_corte.Y = 215.0
    v_arm_corte.Caption = "Corte Longitudinal A-A (Carrera máx. pistón = 200 mm)"
    estilizar_vista_iram(v_arm_corte, mostrar_ocultas=False, mostrar_centros=True)

    # Vista Isométrica 3D del conjunto armado
    v_arm_iso = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Isometrica")
    page_00a.addView(v_arm_iso)
    v_arm_iso.Source = [obj_armado]
    v_arm_iso.Direction = App.Vector(1, -1, 1)
    v_arm_iso.XDirection = App.Vector(1, 1, 0)
    v_arm_iso.ScaleType = "Custom"
    v_arm_iso.Scale = 0.5
    v_arm_iso.X = 465.0
    v_arm_iso.Y = 250.0
    v_arm_iso.Caption = "Perspectiva Isométrica Armado (Escala 1:2)"
    estilizar_vista_iram(v_arm_iso, mostrar_ocultas=False, mostrar_centros=False)

    # =========================================================================
    # HOJA 2: PLANO 00b - VISTA EXPLOTADA REORGANIZADA POR SUBENSAMBLAJES (IRAM A2)
    # =========================================================================
    rotulo_00b = dict(campos_base_rotulo)
    rotulo_00b.update(
        {
            "ESCALA": "Indicada",
            "FORMATO": "IRAM A2",
            "HOJA": f"2/{total_hojas}",
            "TITULO": "Vista Explotada General y Despiece por Subensamblajes (Ítems 1 a 27)",
            "MATERIAL": "Ver Plano Nº 0c (BOM)",
            "MASA": f"Masa: {masa_total_g / 1000.0:.2f} kg",
            "NUM_PLANO": "Plano Nº 0b",
        }
    )
    page_00b, _ = _crear_pagina_iram(
        doc_planos,
        "Plano_00b_Vista_Explotada",
        "Plano_00b_Vista_Explotada",
        "A2",
        rutas_plantillas,
        rotulo_00b,
    )

    # -------------------------------------------------------------------------
    # 2.1 COMPUESTO Y VISTA EXPLOTADA GENERAL DE LA MÁQUINA (SECTOR SUPERIOR)
    # Explosión axial pura y separación radial de columnas/tensores
    # -------------------------------------------------------------------------
    shapes_exp_gen = []
    puntos_gen_3d = {}

    desplazamientos_gen = {
        # Frontal (-Z)
        "Tapa_Exterior_16a": App.Vector(0, 0, -480),
        "Sensor_Inductivo_Ext": App.Vector(-75, -75, -480),
        "Anillo_Torica_Ext_13": App.Vector(0, 0, -380),
        "Cilindro_09": App.Vector(0, 0, -270),
        # Piston group in general view
        "Embolo_Delrin_10": App.Vector(0, 0, -130),
        "ORing_Embolo": App.Vector(0, 0, -130),
        "Centro_Embolo_1_11": App.Vector(0, 0, -130),
        "Centro_Embolo_2_12": App.Vector(0, 0, -130),
        "Sensor_Piston_1_05b": App.Vector(0, 0, -130),
        "Sensor_Piston_2_05b": App.Vector(0, 0, -130),
        "Buje_Guia_1": App.Vector(0, 0, -130),
        "Buje_Guia_2": App.Vector(0, 0, -130),
        # Central stator
        "Anillo_Torica_Int_13": App.Vector(0, 0, -50),
        "Tapa_Interior_16b": App.Vector(0, 0, 0),
        "Sensor_Inductivo_Int": App.Vector(-75, 75, 0),
        # Guías
        "Sufridera_Guia_1_05b": App.Vector(0, 0, 70),
        "Sufridera_Guia_2_05b": App.Vector(0, 0, 70),
        "Guia_1_08": App.Vector(0, 0, 140),
        "Guia_2_08": App.Vector(0, 0, 140),
        # Transmission group in general view
        "Reten_14x30x7": App.Vector(0, 0, 50),
        "Sufridera_Int_05b": App.Vector(0, 0, 85),
        "Tapa_Sufridera_Int_05a": App.Vector(0, 0, 120),
        "Transmisor_1_02a": App.Vector(0, 0, 160),
        "Transmisor_2_02b": App.Vector(0, 0, 240),
        "Pasador_Transm_1": App.Vector(0, 0, 240),
        "Pasador_Transm_2": App.Vector(0, 0, 240),
        "Pasador_Transm_3": App.Vector(0, 0, 240),
        "Adaptador_Rodamiento_03": App.Vector(0, 0, 310),
        "Rodamiento_SKF_6201": App.Vector(0, 0, 350),
        "Sufridera_Eje_Ext_05a": App.Vector(0, 0, 390),
        "Adaptador_Eje_04": App.Vector(0, 0, 430),
        "Tornillo_Sin_Fin_14": App.Vector(0, 0, 500),
        # Estructura exterior (separación radial)
        "Estructura_Interior_1_07": App.Vector(0, -160, 0),
        "Cierre_Estructura_1_15": App.Vector(0, -220, 0),
        "Estructura_Interior_2_07": App.Vector(0, 160, 0),
        "Cierre_Estructura_2_15": App.Vector(0, 220, 0),
        # 4 Tensores (desplazados radialmente hacia los 4 vértices)
        "Tensor_1_06": App.Vector(85, 85, 0),
        "Tensor_2_06": App.Vector(-85, 85, 0),
        "Tensor_3_06": App.Vector(-85, -85, 0),
        "Tensor_4_06": App.Vector(85, -85, 0),
    }

    for entrada in CATALOGO_ITEMS_BOM:
        it_num = entrada["item"]
        sh_base = datos_piezas[it_num]["shape"]
        inst_ref = entrada["instancia_ref"]

        for inst_name in entrada["instancias"]:
            plc_base = placements_instancias.get(inst_name)
            if plc_base is None or sh_base.isNull():
                continue
            sh_i = sh_base.copy()
            sh_i.Placement = plc_base.multiply(sh_i.Placement)
            v_desp = desplazamientos_gen.get(inst_name, App.Vector(0, 0, 0))
            sh_i.translate(v_desp)
            shapes_exp_gen.append(sh_i)
            if inst_name == inst_ref or it_num not in puntos_gen_3d:
                puntos_gen_3d[it_num] = sh_i.BoundBox.Center

    comp_exp_gen = Part.makeCompound(shapes_exp_gen)
    obj_exp_gen = doc_planos.addObject("Part::Feature", "Conjunto_Explotado_General")
    obj_exp_gen.Shape = comp_exp_gen
    if getattr(obj_exp_gen, "ViewObject", None):
        obj_exp_gen.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_exp_gen)

    escala_exp_gen = 0.25
    v_exp_gen = doc_planos.addObject("TechDraw::DrawViewPart", "V00b_Explotada_General")
    page_00b.addView(v_exp_gen)
    v_exp_gen.Source = [obj_exp_gen]
    v_exp_gen.Direction = App.Vector(1, -1, 1)
    v_exp_gen.XDirection = App.Vector(1, 1, 0)
    v_exp_gen.ScaleType = "Custom"
    v_exp_gen.Scale = escala_exp_gen
    v_exp_gen.X = 295.0
    v_exp_gen.Y = 295.0
    v_exp_gen.Caption = "VISTA EXPLOTADA GENERAL DE LA MÁQUINA (Secuencia Longitudinal de Montaje)"
    estilizar_vista_iram(v_exp_gen, mostrar_ocultas=False, mostrar_centros=False)

    centro_gen = comp_exp_gen.BoundBox.Center
    globos_general = [
        (1, -38.0, -35.0),
        (2, -26.0, 36.0),
        (3, -15.0, 36.0),
        (6, 22.0, 32.0),
        (11, 28.0, 36.0),
        (14, 45.0, 24.0),
        (18, -32.0, -36.0),
        (19, -36.0, 32.0),
        (20, -36.0, -35.0),
        (21, 36.0, -36.0),
        (27, -35.0, 24.0),
    ]
    for it_num, dx, dy in globos_general:
        pt3d = puntos_gen_3d.get(it_num)
        if pt3d is not None:
            agregar_globo_item(
                doc_planos, page_00b, v_exp_gen, it_num, pt3d, centro_gen, escala_exp_gen, dx, dy, "Gen"
            )

    # -------------------------------------------------------------------------
    # 2.2 SUBENSAMBLAJE I: CONJUNTO DEL ÉMBOLO Y SELLADO (SECTOR INFERIOR IZQ.)
    # Escala ampliada 1:1.3 con O-Ring, bujes, contratapa y targets magnéticos
    # -------------------------------------------------------------------------
    simb_sub1 = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_Sub_Embolo")
    page_00b.addView(simb_sub1)
    simb_sub1.Symbol = generar_svg_recuadro_subensamblaje(
        "DETALLE A: SUBENSAMBLAJE DEL ÉMBOLO Y SELLADO", "ESCALA 1:1.3", 215.0, 160.0
    )
    simb_sub1.X = 138.0
    simb_sub1.Y = 105.0

    shapes_sub_emb = []
    puntos_sub_emb = {}

    sh_emb = datos_piezas[7]["shape"].copy()
    shapes_sub_emb.append(sh_emb)
    puntos_sub_emb[7] = sh_emb.BoundBox.Center

    sh_oring = datos_piezas[25]["shape"].copy()
    sh_oring.translate(App.Vector(0, 0, -35))
    shapes_sub_emb.append(sh_oring)
    puntos_sub_emb[25] = sh_oring.BoundBox.Center

    sh_ce1 = datos_piezas[8]["shape"].copy()
    sh_ce1.translate(App.Vector(0, 0, -80))
    shapes_sub_emb.append(sh_ce1)
    puntos_sub_emb[8] = sh_ce1.BoundBox.Center

    sh_t1 = datos_piezas[10]["shape"].copy()
    sh_t1.translate(App.Vector(0, 35, -125))
    shapes_sub_emb.append(sh_t1)
    puntos_sub_emb[10] = sh_t1.BoundBox.Center

    sh_ce2 = datos_piezas[9]["shape"].copy()
    sh_ce2.translate(App.Vector(0, 0, 50))
    shapes_sub_emb.append(sh_ce2)
    puntos_sub_emb[9] = sh_ce2.BoundBox.Center

    sh_t2 = datos_piezas[10]["shape"].copy()
    sh_t2.translate(App.Vector(0, -35, 95))
    shapes_sub_emb.append(sh_t2)

    sh_b1 = datos_piezas[24]["shape"].copy()
    sh_b1.translate(App.Vector(-35, 0, 60))
    shapes_sub_emb.append(sh_b1)
    puntos_sub_emb[24] = sh_b1.BoundBox.Center

    sh_b2 = datos_piezas[24]["shape"].copy()
    sh_b2.translate(App.Vector(35, 0, 60))
    shapes_sub_emb.append(sh_b2)

    comp_sub_emb = Part.makeCompound(shapes_sub_emb)
    obj_sub_emb = doc_planos.addObject("Part::Feature", "Subensamblaje_Embolo_Solido")
    obj_sub_emb.Shape = comp_sub_emb
    if getattr(obj_sub_emb, "ViewObject", None):
        obj_sub_emb.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_sub_emb)

    escala_sub_emb = 0.75
    v_sub_emb = doc_planos.addObject("TechDraw::DrawViewPart", "V00b_Sub_Embolo")
    page_00b.addView(v_sub_emb)
    v_sub_emb.Source = [obj_sub_emb]
    v_sub_emb.Direction = App.Vector(1, -1, 1)
    v_sub_emb.XDirection = App.Vector(1, 1, 0)
    v_sub_emb.ScaleType = "Custom"
    v_sub_emb.Scale = escala_sub_emb
    v_sub_emb.X = 138.0
    v_sub_emb.Y = 100.0
    v_sub_emb.Caption = "Subensamblaje del Émbolo (Despiece Explícito)"
    estilizar_vista_iram(v_sub_emb, mostrar_ocultas=False, mostrar_centros=False)

    centro_sub_emb = comp_sub_emb.BoundBox.Center
    globos_sub_emb = [
        (7, 0.0, -35.0),
        (25, -34.0, -22.0),
        (8, -34.0, -28.0),
        (10, -34.0, 24.0),
        (9, 32.0, 28.0),
        (24, 34.0, -26.0),
    ]
    for it_num, dx, dy in globos_sub_emb:
        pt3d = puntos_sub_emb.get(it_num)
        if pt3d is not None:
            agregar_globo_item(
                doc_planos, page_00b, v_sub_emb, it_num, pt3d, centro_sub_emb, escala_sub_emb, dx, dy, "Emb"
            )

    # -------------------------------------------------------------------------
    # 2.3 SUBENSAMBLAJE II: TRANSMISIÓN Y SELLADO DE EJE (SECTOR INFERIOR DER.)
    # Escala ampliada 1:1.8 con rodamientos, retenes, sufrideras y pasadores
    # -------------------------------------------------------------------------
    simb_sub2 = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_Sub_Transmision")
    page_00b.addView(simb_sub2)
    simb_sub2.Symbol = generar_svg_recuadro_subensamblaje(
        "DETALLE B: SISTEMA DE TRANSMISIÓN Y SELLADO", "ESCALA 1:1.8", 245.0, 160.0
    )
    simb_sub2.X = 375.0
    simb_sub2.Y = 105.0

    shapes_sub_transm = []
    puntos_sub_transm = {}

    sh_transm2 = datos_piezas[13]["shape"].copy()
    shapes_sub_transm.append(sh_transm2)
    puntos_sub_transm[13] = sh_transm2.BoundBox.Center

    sh_transm1 = datos_piezas[12]["shape"].copy()
    sh_transm1.translate(App.Vector(0, 0, -135))
    shapes_sub_transm.append(sh_transm1)
    puntos_sub_transm[12] = sh_transm1.BoundBox.Center

    sh_ret = datos_piezas[23]["shape"].copy()
    sh_ret.translate(App.Vector(0, 0, -195))
    shapes_sub_transm.append(sh_ret)
    puntos_sub_transm[23] = sh_ret.BoundBox.Center

    sh_sufr_int = datos_piezas[4]["shape"].copy()
    sh_sufr_int.translate(App.Vector(0, 0, -230))
    shapes_sub_transm.append(sh_sufr_int)
    puntos_sub_transm[4] = sh_sufr_int.BoundBox.Center

    sh_tapa_sufr = datos_piezas[5]["shape"].copy()
    sh_tapa_sufr.translate(App.Vector(0, 0, -265))
    shapes_sub_transm.append(sh_tapa_sufr)
    puntos_sub_transm[5] = sh_tapa_sufr.BoundBox.Center

    sh_pas1 = datos_piezas[26]["shape"].copy()
    sh_pas1.translate(App.Vector(0, -45, -35))
    shapes_sub_transm.append(sh_pas1)
    puntos_sub_transm[26] = sh_pas1.BoundBox.Center

    sh_pas2 = datos_piezas[26]["shape"].copy()
    sh_pas2.translate(App.Vector(0, 45, -15))
    shapes_sub_transm.append(sh_pas2)

    sh_pas3 = datos_piezas[26]["shape"].copy()
    sh_pas3.translate(App.Vector(45, 0, 30))
    shapes_sub_transm.append(sh_pas3)

    sh_arod = datos_piezas[15]["shape"].copy()
    sh_arod.translate(App.Vector(0, 0, 80))
    shapes_sub_transm.append(sh_arod)
    puntos_sub_transm[15] = sh_arod.BoundBox.Center

    sh_skf = datos_piezas[22]["shape"].copy()
    sh_skf.translate(App.Vector(0, 0, 120))
    shapes_sub_transm.append(sh_skf)
    puntos_sub_transm[22] = sh_skf.BoundBox.Center

    sh_sufr_ext = datos_piezas[16]["shape"].copy()
    sh_sufr_ext.translate(App.Vector(0, 0, 160))
    shapes_sub_transm.append(sh_sufr_ext)
    puntos_sub_transm[16] = sh_sufr_ext.BoundBox.Center

    sh_aeje = datos_piezas[17]["shape"].copy()
    sh_aeje.translate(App.Vector(0, 0, 200))
    shapes_sub_transm.append(sh_aeje)
    puntos_sub_transm[17] = sh_aeje.BoundBox.Center

    sh_hus = datos_piezas[14]["shape"].copy()
    sh_hus.translate(App.Vector(0, 0, 270))
    shapes_sub_transm.append(sh_hus)
    puntos_sub_transm[14] = sh_hus.BoundBox.Center

    comp_sub_transm = Part.makeCompound(shapes_sub_transm)
    obj_sub_transm = doc_planos.addObject("Part::Feature", "Subensamblaje_Transmision_Solido")
    obj_sub_transm.Shape = comp_sub_transm
    if getattr(obj_sub_transm, "ViewObject", None):
        obj_sub_transm.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_sub_transm)

    escala_sub_transm = 0.52
    v_sub_transm = doc_planos.addObject("TechDraw::DrawViewPart", "V00b_Sub_Transmision")
    page_00b.addView(v_sub_transm)
    v_sub_transm.Source = [obj_sub_transm]
    v_sub_transm.Direction = App.Vector(1, -1, 1)
    v_sub_transm.XDirection = App.Vector(1, 1, 0)
    v_sub_transm.ScaleType = "Custom"
    v_sub_transm.Scale = escala_sub_transm
    v_sub_transm.X = 375.0
    v_sub_transm.Y = 100.0
    v_sub_transm.Caption = "Subensamblaje de Transmisión y Rodamientos (Despiece Explícito)"
    estilizar_vista_iram(v_sub_transm, mostrar_ocultas=False, mostrar_centros=False)

    centro_sub_transm = comp_sub_transm.BoundBox.Center
    globos_sub_transm = [
        (4, -34.0, -26.0),
        (5, -34.0, 26.0),
        (12, -34.0, -22.0),
        (13, 0.0, 32.0),
        (14, 38.0, 24.0),
        (15, 26.0, 32.0),
        (16, 26.0, 30.0),
        (17, 26.0, -28.0),
        (22, 24.0, -28.0),
        (23, -34.0, 18.0),
        (26, -24.0, -30.0),
    ]
    for it_num, dx, dy in globos_sub_transm:
        pt3d = puntos_sub_transm.get(it_num)
        if pt3d is not None:
            agregar_globo_item(
                doc_planos, page_00b, v_sub_transm, it_num, pt3d, centro_sub_transm, escala_sub_transm, dx, dy, "Tr"
            )

    # =========================================================================
    # HOJA 3: PLANO 00c - LISTA DE MATERIALES Y DESPIECE IRAM 4508 (A3)
    # =========================================================================
    rotulo_00c = dict(campos_base_rotulo)
    rotulo_00c.update(
        {
            "ESCALA": "S/E",
            "FORMATO": "IRAM A3",
            "HOJA": f"3/{total_hojas}",
            "TITULO": "Lista de Materiales Completa y Componentes Comerciales",
            "MATERIAL": "Según Tabla IRAM 4508",
            "MASA": f"Total: {masa_total_g / 1000.0:.2f} kg",
            "NUM_PLANO": "Plano Nº 0c",
        }
    )
    page_00c, _ = _crear_pagina_iram(
        doc_planos,
        "Plano_00c_Lista_Materiales",
        "Plano_00c_Lista_Materiales",
        "A3",
        rutas_plantillas,
        rotulo_00c,
    )

    simbolo_bom = doc_planos.addObject("TechDraw::DrawViewSymbol", "Tabla_BOM_Visual")
    page_00c.addView(simbolo_bom)
    simbolo_bom.Symbol = generar_svg_tabla_bom_iram(items_bom_completos, RESUMEN_BULONERIA_ESTANDAR, ancho_mm=382.0)
    simbolo_bom.X = 217.5
    simbolo_bom.Y = 185.0

    # =========================================================================
    # HOJAS 4 A 24: 21 PLANOS DE DETALLE DE LAS PIEZAS FABRICADAS (Ítems 1..21)
    # =========================================================================
    num_hoja_actual = 4
    for entrada in CATALOGO_ITEMS_BOM:
        if entrada["es_comercial"]:
            continue

        it_num = entrada["item"]
        info = datos_piezas[it_num]
        sh_p = info["shape"]
        masa_g = info["masa_g"]
        filas_param = info["filas_param"]
        nombre_hoja = entrada["hoja_plano"]

        # Crear objeto Part::Feature en el documento de planos con la geometría en Modo 2 (CNC/Planos)
        obj_p = doc_planos.addObject("Part::Feature", f"Solido_Item_{it_num:02d}")
        obj_p.Label = entrada["denominacion"]
        obj_p.Shape = sh_p
        if getattr(obj_p, "ViewObject", None):
            obj_p.ViewObject.Visibility = False
        grupo_fuentes.addObject(obj_p)

        bb = sh_p.BoundBox
        formato, escala_num, escala_txt = seleccionar_formato_y_escala(bb, es_conjunto=False)
        W_hoja, H_hoja = FORMATOS_IRAM[formato]

        rotulo_p = dict(campos_base_rotulo)
        rotulo_p.update(
            {
                "ESCALA": escala_txt,
                "FORMATO": f"IRAM {formato}",
                "HOJA": f"{num_hoja_actual}/{total_hojas}",
                "TITULO": f"{entrada['denominacion']} (Ítem #{it_num} - Cant: {len(entrada['instancias'])})",
                "MATERIAL": entrada["material"],
                "MASA": f"Masa: {masa_g:.1f} g",
                "NUM_PLANO": entrada["plano_original"],
            }
        )
        page_p, _ = _crear_pagina_iram(
            doc_planos,
            nombre_hoja,
            nombre_hoja,
            formato,
            rutas_plantillas,
            rotulo_p,
        )

        # Posiciones de vistas adaptadas al formato (A4 vs A3) dejando el tercio derecho para Isométrica + Cuadro Técnico
        if formato == "A4":
            x_vistas = 82.0
            y_planta = 148.0
            y_corte = 62.0
            x_der = 225.0
            y_iso = 165.0
            y_tabla = 105.0
            ancho_tabla = 96.0
            escala_tabla = 0.78
        else:
            x_vistas = 125.0
            y_planta = 208.0
            y_corte = 88.0
            x_der = 322.0
            y_iso = 232.0
            y_tabla = 140.0
            ancho_tabla = 145.0
            escala_tabla = 0.95

        # 1. Vista Superior / Frontal Circular (Planta desde +Z)
        v_sup = doc_planos.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Planta")
        page_p.addView(v_sup)
        v_sup.Source = [obj_p]
        v_sup.Direction = App.Vector(0, 0, 1)
        v_sup.XDirection = App.Vector(1, 0, 0)
        v_sup.ScaleType = "Custom"
        v_sup.Scale = escala_num
        v_sup.X = x_vistas
        v_sup.Y = y_planta
        v_sup.Caption = f"Vista Superior (Escala {escala_txt})"
        estilizar_vista_iram(v_sup, mostrar_ocultas=False, mostrar_centros=True)

        # 2. Vista en Corte Longitudinal A-A (pasando por el eje de simetría Z)
        v_sec = doc_planos.addObject("TechDraw::DrawViewSection", f"VP_{it_num:02d}_Corte_AA")
        page_p.addView(v_sec)
        v_sec.BaseView = v_sup
        v_sec.Source = [obj_p]
        v_sec.SectionNormal = App.Vector(0, -1, 0)
        v_sec.SectionDirection = "Down"
        v_sec.SectionOrigin = bb.Center
        v_sec.SectionSymbol = "A"
        v_sec.ScaleType = "Custom"
        v_sec.Scale = escala_num
        v_sec.X = x_vistas
        v_sec.Y = y_corte
        v_sec.Caption = f"Corte Longitudinal A-A (Escala {escala_txt})"
        estilizar_vista_iram(v_sec, mostrar_ocultas=False, mostrar_centros=True)

        # 3. Vista Isométrica 3D de referencia
        v_iso = doc_planos.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Iso")
        page_p.addView(v_iso)
        v_iso.Source = [obj_p]
        v_iso.Direction = App.Vector(1, -1, 1)
        v_iso.XDirection = App.Vector(1, 1, 0)
        v_iso.ScaleType = "Custom"
        v_iso.Scale = round(escala_num * 0.70, 3)
        v_iso.X = x_der
        v_iso.Y = y_iso
        v_iso.Caption = "Perspectiva Isométrica"
        estilizar_vista_iram(v_iso, mostrar_ocultas=False, mostrar_centros=False)

        # 4. Cuadro técnico vectorial de parámetros, roscas y tolerancias extraído de `Parametros`
        simb_cotas = doc_planos.addObject("TechDraw::DrawViewSymbol", f"VP_{it_num:02d}_Cuadro_Cotas")
        page_p.addView(simb_cotas)
        simb_cotas.Symbol = generar_svg_bloque_cotas_pieza(
            filas_param, entrada["notas_taller"], ancho_mm=ancho_tabla
        )
        simb_cotas.ScaleType = "Custom"
        simb_cotas.Scale = escala_tabla
        simb_cotas.X = x_der
        simb_cotas.Y = y_tabla

        num_hoja_actual += 1

    # Recomputar las vistas proyectadas para que OCCT HLR genere las aristas 2D antes de acotar
    print("Calculando proyecciones HLR de las 24 láminas IRAM...")
    doc_planos.recompute()

    # Aplicar acotación geométrica automática (`TechDraw::DrawViewDimension`) en todas las vistas
    total_cotas_geom = 0
    cotas_00a = acotar_vista_perfil_o_corte_iram(doc_planos, page_00a, v_arm_frente, "Cota_00a")
    total_cotas_geom += len(cotas_00a)

    for entrada in CATALOGO_ITEMS_BOM:
        if entrada["es_comercial"]:
            continue
        it_num = entrada["item"]
        page_p = doc_planos.getObject(entrada["hoja_plano"])
        v_sup = doc_planos.getObject(f"VP_{it_num:02d}_Planta")
        v_sec = doc_planos.getObject(f"VP_{it_num:02d}_Corte_AA")
        if page_p and v_sup:
            c_diam = acotar_vista_circular_iram(doc_planos, page_p, v_sup, f"Cota_{it_num:02d}", max_diametros=3)
            total_cotas_geom += len(c_diam)
        if page_p and v_sec:
            c_lin = acotar_vista_perfil_o_corte_iram(doc_planos, page_p, v_sec, f"Cota_{it_num:02d}")
            total_cotas_geom += len(c_lin)

    doc_planos.recompute()
    doc_planos.saveAs(RUTA_SALIDA_FCSTD)
    print(f"Legajo guardado exitosamente ({total_hojas} hojas, {total_cotas_geom} cotas geométricas): {RUTA_SALIDA_FCSTD}")

    # Guardar además cada lámina por separado en `planos/hojas/` para apertura rápida y exportación PDF sin trabar Qt
    dir_hojas = os.path.join(DIR_PLANOS, "hojas")
    os.makedirs(dir_hojas, exist_ok=True)
    paginas = [o for o in doc_planos.Objects if o.TypeId == "TechDraw::DrawPage"]
    for pag in paginas:
        d_ind = App.newDocument(pag.Name)
        d_ind.copyObject(pag, True)
        d_ind.copyObject(dr, False)
        for obj_i in d_ind.Objects:
            if obj_i.isDerivedFrom("Part::Feature") and getattr(obj_i, "ViewObject", None):
                obj_i.ViewObject.Visibility = False
        d_ind.recompute()
        d_ind.saveAs(os.path.join(dir_hojas, f"{pag.Name}.FCStd"))
        App.closeDocument(d_ind.Name)
    print(f"Generadas {len(paginas)} hojas individuales livianas en: {dir_hojas}")

    # Exportación opcional a PDF si el usuario define EXPORTAR_PDF=1 (Regla 3.1: desactivada por defecto)
    if os.environ.get("EXPORTAR_PDF") == "1":
        dir_pdf = os.path.join(DIR_PLANOS, "pdf")
        os.makedirs(dir_pdf, exist_ok=True)
        import TechDrawGui
        for o in doc_planos.Objects:
            if o.TypeId == "TechDraw::DrawPage":
                ruta_pdf = os.path.join(dir_pdf, f"{o.Name}.pdf")
                TechDrawGui.exportPageAsPdf(o, ruta_pdf)
                print("Exportado PDF:", ruta_pdf)


if __name__ in ("__main__", "generar_planos"):
    import traceback
    try:
        main()
    except Exception:
        traceback.print_exc()
