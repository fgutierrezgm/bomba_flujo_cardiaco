#!/usr/bin/env python3
"""
Generador del legajo técnico completo bajo normas IRAM para el modelo de
IMPRESIÓN 3D A ESCALA (0,755 + holguras FDM ±0,20 mm):

  Ensamblaje fuente:
    proyectos/bomba_flujo_cardiaco/ensamblajes/Piloto_Impresion_3D_Assembly.FCStd

  Salida maestra (.FCStd):
    proyectos/bomba_flujo_cardiaco/planos/Planos_Impresion_3D.FCStd
  Hojas individuales livianas (.FCStd):
    proyectos/bomba_flujo_cardiaco/planos/hojas_3d/<NombreHoja>.FCStd

Genera 26 láminas IRAM (3 de conjunto + 23 de piezas individuales a escala 3D):
  - Hoja 1 (A2): Plano Nº 0a - Conjunto General Armado y Corte Longitudinal A-A
  - Hoja 2 (A2): Plano Nº 0b - Vista Explotada General (46 piezas) + 2 Subensamblajes
  - Hoja 3 (A3): Plano Nº 0c - Lista de Materiales IRAM 4508 (30 ítems / 46 un.)
  - Hojas 4..26 (A4/A3): Planos de detalle e impresión/mecanizado de las 23 piezas
    (con cotas reales medidas sobre la geometría 3D a escala 0,755 y cuadro técnico).

Regla técnica AGENTS.md 3.1: exporta SOLO `.FCStd` por defecto.
Si se define `EXPORTAR_PDF=1` en el entorno, exporta además todas las hojas a `planos/pdf_3d/`.
"""
import math
import os
import re
import sys

import FreeCAD as App
import Part


DIR_PLANOS = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
DIR_PROYECTO = os.path.abspath(os.path.join(DIR_PLANOS, ".."))
RAIZ = os.path.abspath(os.path.join(DIR_PROYECTO, "..", ".."))
DIR_PIEZAS = os.path.join(DIR_PROYECTO, "piezas")
DIR_ELEM_COM = os.path.join(DIR_PIEZAS, "Elementos_comericales")
DIR_PLANTILLAS = os.path.join(RAIZ, "_plantillas")
DIR_HERRAMIENTAS = os.path.join(RAIZ, "_herramientas")

RUTA_ENSAMBLAJE_3D = os.path.join(DIR_PROYECTO, "ensamblajes", "Piloto_Impresion_3D_Assembly.FCStd")
RUTA_SALIDA_FCSTD = os.path.join(DIR_PLANOS, "Planos_Impresion_3D.FCStd")
DIR_HOJAS_3D = os.path.join(DIR_PLANOS, "hojas_3d")

if DIR_HERRAMIENTAS not in sys.path:
    sys.path.insert(0, DIR_HERRAMIENTAS)

from planos_iram import (
    FORMATOS_IRAM,
    acotar_detalles_y_roscas_corte_iram,
    acotar_vista_circular_iram,
    acotar_vista_perfil_o_corte_iram,
    agregar_ejes_simetria_iram,
    asegurar_plantillas_iram,
    estilizar_vista_iram,
    generar_svg_bloque_cotas_pieza,
    generar_svg_tabla_bom_iram,
    obtener_ruta_fcpat,
    seleccionar_formato_y_escala,
)


# -----------------------------------------------------------------------------
# CATÁLOGO MAESTRO DE LOS 30 ÍTEMS DEL ENSAMBLAJE DE IMPRESIÓN 3D (46 UNIDADES)
# Coincidencia 1:1 con Piloto_Impresion_3D_Assembly.FCStd
# -----------------------------------------------------------------------------
CATALOGO_ITEMS_BOM_3D = [
    # --- 23 Piezas Fabricadas / Impresas en 3D (Ítems 1..23) ---
    {
        "item": 1,
        "archivo": "Tapa_Exterior_16a_3D.FCStd",
        "denominacion": "Tapa Exterior 16a (Impr. 3D)",
        "plano_ref": "Plano Nº 16a-3D",
        "plano_original": "Plano Nº 16a-3D",
        "hoja_plano": "Plano_01_Tapa_Exterior_16a_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Brida Ø120,80x22,65 mm; aloj. vidrio Ø83,43; brida ext. Ø30,60 FDM; puerto 45°",
        "notas_taller": [
            "Impresión 3D esc. 0,755 (PLA+/PETG): relleno >= 40% giroide, 5 perímetros.",
            "Alojamientos adaptados con holgura FDM: brida Ø30,60 mm y nariz Ø14,00 mm.",
            "Dos alojamientos guía Ø10,57 mm a ±28,31 mm entre centros (56,62 mm).",
        ],
        "features_extra": [
            ("d_ext_brida", "120.80 mm", "Diámetro exterior de brida (esc. 0,755)"),
            ("h_total", "22.65 mm", "Espesor / altura total en Z"),
            ("d_aloj_camisa", "83.43 mm", "Alojamiento camisa vidrio Ø83 (+holgura)"),
            ("d_escalon_int", "90.68 / 109.47 mm", "Escalones de asiento y centrado"),
            ("c_guias", "2x Ø10.57 @ ±28.31", "Alojamientos extremos de barras guía"),
            ("puerto_45", "Ø8.24 @ (-20.02,-20.02)", "Puerto sensor / purga a 45°"),
            ("puertos_axial", "2x Ø6.47 / Ø3.70 @ ±28.31", "Puertos hidráulicos sobre eje Y"),
        ],
        "es_comercial": False,
        "instancias": ["Tapa_Exterior_16a_3D"],
    },
    {
        "item": 2,
        "archivo": "Cilindro_09_3D.FCStd",
        "denominacion": "Cilindro Camisa Vidrio (Esc. 0,755)",
        "plano_ref": "Plano Nº 9-3D",
        "plano_original": "Plano Nº 9-3D",
        "hoja_plano": "Plano_02_Cilindro_09_3D",
        "material": "Vidrio Sodocálcico",
        "tol_gral": "ISO 2768-mK",
        "detalles": "Tubo vidrio Ø83,00 ext. x Ø76,00 int. x 188,75 mm; pared 3,50 mm",
        "notas_taller": [
            "Tubo comercial de Vidrio Sodocálcico cortado a L = 188,75 ± 0,30 mm.",
            "Amolar y pulir ambos extremos al agua a 90° respecto del eje para asiento en O-Rings.",
        ],
        "features_extra": [
            ("e_pared", "3.50 mm", "Espesor nominal de pared del tubo de vidrio"),
        ],
        "es_comercial": False,
        "instancias": ["Cilindro_09_3D"],
    },
    {
        "item": 3,
        "archivo": "Tapa_Interior_16b_3D.FCStd",
        "denominacion": "Tapa Interior Intermedia (Impr. 3D)",
        "plano_ref": "Plano Nº 16b-3D",
        "plano_original": "Plano Nº 16b-3D",
        "hoja_plano": "Plano_03_Tapa_Interior_16b_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Brida Ø120,80x22,65 mm; bolsillos sufr. guía Ø15,50x2,50; paso central Ø30,20",
        "notas_taller": [
            "Impresión 3D esc. 0,755 (PLA+/PETG): cara de asiento de vidrio plana sin pandeo.",
            "Bolsillos para sufrideras de guía ampliados a Ø15,50 mm (prof. 2,50 mm en X=±28,31).",
            "Repasar alojamiento sufridera Ø34,05 mm y paso Ø7,63 mm si hay costura Z.",
        ],
        "features_extra": [
            ("d_ext_brida", "120.80 mm", "Diámetro exterior de brida (esc. 0,755)"),
            ("h_total", "22.65 mm", "Espesor / altura total en Z"),
            ("d_aloj_camisa", "83.43 mm", "Alojamiento camisa vidrio Ø83 (+holgura)"),
            ("d_aloj_sufr_c", "34.05 / 30.20 mm", "Cajeras centrales retén y sufridera"),
            ("c_paso_guias", "2x Ø13.59 / Ø7.63 @ ±28.31", "Escalón de guía y paso varillas"),
            ("puerto_45", "Ø8.24 @ (20.41,20.41)", "Puerto sensor / purga a 45°"),
            ("puertos_axial", "2x Ø6.47 / Ø3.70 @ ±28.31", "Puertos hidráulicos sobre eje Y"),
        ],
        "es_comercial": False,
        "instancias": ["Tapa_Interior_16b_3D"],
    },
    {
        "item": 4,
        "archivo": "Sufridera_Int_05b_3D.FCStd",
        "denominacion": "Sufridera Interior Retén (Impr. 3D)",
        "plano_ref": "Plano Nº 5b-3D",
        "plano_original": "Plano Nº 5b-3D",
        "hoja_plano": "Plano_04_Sufridera_Int_05b_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Brida Ø33,98x7,12 mm; aloj. retén 10x22x7 adapt. Ø22,40 FDM; 4x Ø1,86",
        "notas_taller": [
            "Alojamiento para retén 10x22x7 mm llevado a Ø22,40 mm (ajuste FDM).",
            "Altura total 7,12 mm (cuerpo 6,42 mm + extensión 0,70 mm para alojar retén 7 mm).",
        ],
        "features_extra": [
            ("h_total", "7.12 mm", "Altura total con extensión de retén (+0,70 mm)"),
            ("pcd_4x", "4x Ø1.86 @ PCD 28.32", "4 agujeros fijación en DBC Ø28,32 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Sufridera_Int_05b_3D"],
    },
    {
        "item": 5,
        "archivo": "Tapa_Sufridera_Int_05a_3D.FCStd",
        "denominacion": "Tapa Sufridera Interior (Impr. 3D)",
        "plano_ref": "Plano Nº 5a-3D",
        "plano_original": "Plano Nº 5a-3D",
        "hoja_plano": "Plano_05_Tapa_Sufridera_Int_05a_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Brida plana Ø33,98x1,51 mm; paso central eje Ø11,80 mm FDM; 4x Ø2,27",
        "notas_taller": [
            "Imprimir 100% sólido (1,51 mm espesor). Paso eje B adaptado a Ø11,80 mm.",
        ],
        "features_extra": [
            ("d_ext", "33.98 mm", "Diámetro exterior de brida"),
            ("h_total", "1.51 mm", "Espesor axial de tapa"),
            ("pcd_4x", "4x Ø2.27 @ PCD 28.32", "4 agujeros pasantes en DBC Ø28,32 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Tapa_Sufridera_Int_05a_3D"],
    },
    {
        "item": 6,
        "archivo": "Sufridera_Guia_05b_3D.FCStd",
        "denominacion": "Sufridera Guía de Émbolo (Impr. 3D)",
        "plano_ref": "Plano Nº 5c-3D",
        "plano_original": "Plano Nº 5c-3D",
        "hoja_plano": "Plano_06_Sufridera_Guia_05b_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Brida Ø15,10x2,27 mm; paso guía Ø7,95 mm FDM; 4x Ø2,34 en PCD Ø11,32",
        "notas_taller": [
            "Cantidad total: 4 unidades idénticas (2 pares sobre Tapa Interior 16b).",
            "Agujero central ampliado a Ø7,95 mm para paso sin roce de barra guía.",
        ],
        "features_extra": [
            ("d_ext", "15.10 mm", "Diámetro exterior de sufridera"),
            ("h_total", "2.27 mm", "Espesor total"),
            ("pcd_4x", "4x Ø2.34 @ PCD 11.32", "4 agujeros de fijación en DBC Ø11,32 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Sufridera_Guia_1A_3D", "Sufridera_Guia_1B_3D", "Sufridera_Guia_2A_3D", "Sufridera_Guia_2B_3D"],
    },
    {
        "item": 7,
        "archivo": "Embolo_Delrin_10_3D.FCStd",
        "denominacion": "Émbolo Principal (Esc. 0,755)",
        "plano_ref": "Plano Nº 10-3D",
        "plano_original": "Plano Nº 10-3D",
        "hoja_plano": "Plano_07_Embolo_Delrin_10_3D",
        "material": "Delrin POM-C",
        "tol_gral": "ISO 2768-mK",
        "detalles": "Pistón Ø75,72x15,10 mm; garganta O-Ring Ø71,34; aloj. núcleo Ø22,65; 2x Ø10,57",
        "notas_taller": [
            "Mecanizado en Delrin POM-C a escala 0,755 para cilindro interior Ø76,00 mm.",
            "Garganta perimetral Ø71,34 mm (Z=5,75..8,87) para O-Ring Ø69x3,55 mm.",
            "2 alojamientos guía Ø10,57 a ±28,31 mm; 1 aloj. sensor Ø6,04 a 45° (r=28,31).",
        ],
        "features_extra": [
            ("d_ext", "75.72 mm", "Diámetro exterior del émbolo (hacia Ø76 vidrio)"),
            ("d_fondo_oring", "71.34 mm", "Diámetro de fondo de ranura para O-Ring 69x3,55"),
            ("z_ranura", "5.75 - 8.87 mm", "Posición axial ranura O-Ring (ancho 3,12 mm)"),
            ("d_cajera_nuc", "22.65 mm", "Alojamiento central de Centro de Émbolo 1"),
            ("c_guias", "2x Ø10.57 @ ±28.31", "Fijación extremos roscados barras guía"),
            ("c_sensor", "Ø6.04 @ (20.02,20.02)", "Alojamiento de target magnético AISI 430"),
            ("pcd_4x", "4x Ø1.86 @ PCD 28.24", "4 agujeros fijación núcleo Centro Émbolo"),
        ],
        "es_comercial": False,
        "instancias": ["Embolo_Delrin_10_3D"],
    },
    {
        "item": 8,
        "archivo": "Centro_Embolo_1_11_3D.FCStd",
        "denominacion": "Centro de Émbolo 1 (Impresión 3D)",
        "plano_ref": "Plano Nº 11-3D",
        "plano_original": "Plano Nº 11-3D",
        "hoja_plano": "Plano_08_Centro_Embolo_1_11_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Brida Ø33,98 / cubo Ø22,65 x 18,72 mm; paso central Ø8,94; 4x Ø2,64 y 3x Ø1,86",
        "notas_taller": [
            "Impresión 3D con 100% relleno en zona del cubo Ø22,65 mm.",
            "Verificar ajuste sin holgura excesiva sobre punta roscada de Transmisor B.",
        ],
        "features_extra": [
            ("d_brida", "33.98 mm", "Diámetro exterior de brida (espesor 3,78 mm)"),
            ("d_cubo", "22.65 mm", "Diámetro de encastre en émbolo (Z=3,78..18,72)"),
            ("d_central", "8.94 mm", "Agujero central para acoplamiento de eje"),
            ("pcd_4x", "4x Ø2.64 @ PCD 28.32", "4 agujeros fijación a émbolo Delrin"),
            ("pcd_3x", "3x Ø1.86 @ PCD 15.86", "3 agujeros roscados para contratapa 12"),
        ],
        "es_comercial": False,
        "instancias": ["Centro_Embolo_1_11_3D"],
    },
    {
        "item": 9,
        "archivo": "Centro_Embolo_2_12_3D.FCStd",
        "denominacion": "Centro de Émbolo 2 (Impresión 3D)",
        "plano_ref": "Plano Nº 12-3D",
        "plano_original": "Plano Nº 12-3D",
        "hoja_plano": "Plano_09_Centro_Embolo_2_12_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Tapa anular Ø33,98x3,78 mm; paso central Ø11,32; 3x Ø2,64 en PCD Ø15,86",
        "notas_taller": [
            "Contratapa de fijación de Centro de Émbolo 1 al émbolo Delrin.",
        ],
        "features_extra": [
            ("d_ext", "33.98 mm", "Diámetro exterior de contratapa"),
            ("d_int", "11.32 mm", "Diámetro paso central"),
            ("pcd_3x", "3x Ø2.64 @ PCD 15.86", "3 agujeros pasantes a 120° en DBC Ø15,86"),
        ],
        "es_comercial": False,
        "instancias": ["Centro_Embolo_2_12_3D"],
    },
    {
        "item": 10,
        "archivo": "Sensor_Piston_05b_3D.FCStd",
        "denominacion": "Sensor Magnético Pistón (AISI 430)",
        "plano_ref": "Plano Nº 5d-3D",
        "plano_original": "Plano Nº 5d-3D",
        "hoja_plano": "Plano_10_Sensor_Piston_05b_3D",
        "material": "Acero Inox. Ferrítico AISI 430",
        "tol_gral": "ISO 2768-mK",
        "detalles": "Target Ø15,10x11,32 mm con espiga Ø6,04 mm; material ferromagnético obligatorio",
        "notas_taller": [
            "MATERIAL OBLIGATORIO: Acero Inoxidable Ferrítico AISI 430 (magnético).",
            "NO sustituir por AISI 304/316L (austenítico no detectado por sensor inductivo).",
        ],
        "features_extra": [
            ("d_cabeza", "15.10 mm", "Diámetro de cabeza sensora (Z=5,29..11,32)"),
            ("d_espiga", "6.04 mm", "Diámetro de espiga de montaje (Z=0..5,29)"),
        ],
        "es_comercial": False,
        "instancias": ["Sensor_Piston_1_3D", "Sensor_Piston_2_3D"],
    },
    {
        "item": 11,
        "archivo": "Guia_08_3D.FCStd",
        "denominacion": "Eje Guía de Émbolo (L=220,65 mm)",
        "plano_ref": "Plano Nº 8-3D",
        "plano_original": "Plano Nº 8-3D",
        "hoja_plano": "Plano_11_Guia_08_3D",
        "material": "Acero Inox. AISI 304/316L",
        "tol_gral": "ISO 2768-mK",
        "detalles": "Varilla Ø8,66 g6 x 220,65 mm; espiga Ø7,15x22,65 y extremo roscado Ø7,55x9,82",
        "notas_taller": [
            "Longitud calibrada L = 220,65 mm para encastre exacto en Tapas 16a y 16b 3D.",
            "Cuerpo central Ø8,66 mm; espiga lisa inferior Ø7,15 x 22,65 mm; rosca superior 9,82 mm.",
        ],
        "features_extra": [],
        "es_comercial": False,
        "instancias": ["Guia_1_08_3D", "Guia_2_08_3D"],
    },
    {
        "item": 12,
        "archivo": "Transmisor_A_02a_3D.FCStd",
        "denominacion": "Eje Transmisor A Motor (Esc. 0,755)",
        "plano_ref": "Plano Nº 2a-3D",
        "plano_original": "Plano Nº 2a-3D",
        "hoja_plano": "Plano_12_Transmisor_A_02a_3D",
        "material": "Acero Inox. AISI 304/316L",
        "tol_gral": "ISO 2768-mK",
        "detalles": "Eje escalonado Ø15,10 / Ø9,06 / Ø7,55 x 95,89 mm; 2x taladros pasador Ø3,02 mm",
        "notas_taller": [
            "Tornear concéntrico en AISI 304/316L entre puntos. Chaflanar aristas 0,3x45°.",
            "Taladrar 2 agujeros transversales Ø3,02 mm a Z=50,96 y Z=84,94 mm para pasador Ø3x14.",
        ],
        "features_extra": [
            ("d_cuello_max", "15.10 mm", "Diámetro máximo de acople tubular (Z=0..35,48)"),
            ("d_asiento_609", "9.06 mm", "Diámetro asiento SKF 609 (Z=45,30..95,89)"),
            ("d_int_aloj", "7.55 / 6.04 mm", "Alojamientos interiores axiales en extremos"),
            ("c_pasadores", "2x transv. Ø3.02", "Taladros para Pasador 3x14 en Z=50,96 y Z=84,94"),
        ],
        "es_comercial": False,
        "instancias": ["Transmisor_A_02a_3D"],
    },
    {
        "item": 13,
        "archivo": "Transmisor_B_02b_3D.FCStd",
        "denominacion": "Eje Transmisor B Retén (Esc. 0,755)",
        "plano_ref": "Plano Nº 2b-3D",
        "plano_original": "Plano Nº 2b-3D",
        "hoja_plano": "Plano_13_Transmisor_B_02b_3D",
        "material": "Acero Inox. AISI 304/316L",
        "tol_gral": "ISO 2768-mK",
        "detalles": "Eje pistón Ø11,32 / Ø10,57 / Ø9,81 / Ø9,06 x 95,82 mm; 3x pasador Ø3,02 mm",
        "notas_taller": [
            "Pista del retén 10x22x7 (zona Ø9,81/10,57) terminación rectificada Ra <= 0,4 um.",
            "3 taladros transversales Ø3,02 mm en Z=5,66; 39,64 y 90,22 mm.",
        ],
        "features_extra": [
            ("d_brida_max", "11.32 mm", "Diámetro mayor (Z=54,36..95,82)"),
            ("d_tramo_reten", "9.81 - 10.57 mm", "Zona de trabajo del retén radial 10x22x7"),
            ("d_espiga", "9.06 / 6.02 mm", "Escalón de extremo y agujero axial"),
            ("c_pasadores", "3x transv. Ø3.02", "Taladros en Z=5,66; Z=39,64 y Z=90,22 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Transmisor_B_02b_3D"],
    },
    {
        "item": 14,
        "archivo": "Tornillo_Sin_Fin_14_3D.FCStd",
        "denominacion": "Tornillo Sin Fin Central (Esc. 0,755)",
        "plano_ref": "Plano Nº 14-3D",
        "plano_original": "Plano Nº 14-3D",
        "hoja_plano": "Plano_14_Tornillo_Sin_Fin_14_3D",
        "material": "Acero SAE 1045",
        "tol_gral": "ISO 2768-mK",
        "detalles": "Husillo Ø10,57 / espigas Ø9,06 x 192,15 mm; taladro transversal Ø3,02 mm",
        "notas_taller": [
            "Longitud total 192,15 mm; tramos extremos Ø9,06 mm con 1 taladro Ø3,02 en Z=5,68.",
        ],
        "features_extra": [
            ("d_husillo", "10.57 / 9.81 mm", "Diámetro exterior de zona central del husillo"),
            ("d_espigas", "9.06 / 6.04 mm", "Extremos de apoyo en Tapa Ext. y acople eje"),
            ("c_pasador", "1x transv. Ø3.02", "Taladro para Pasador 3x10 en Z=5,68 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Tornillo_Sin_Fin_14_3D"],
    },
    {
        "item": 15,
        "archivo": "Adaptador_Rodamiento_03_3D.FCStd",
        "denominacion": "Adaptador Rodamiento SKF 609 (Impr. 3D)",
        "plano_ref": "Plano Nº 3-3D",
        "plano_original": "Plano Nº 3-3D",
        "hoja_plano": "Plano_15_Adaptador_Rodamiento_03_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Cuerpo Ø41,52x19,25 mm; aloj. SKF 609 Ø24,40 (z=11,65); paso Ø15,60; 4x Ø2,34",
        "notas_taller": [
            "Alojamiento adaptado a SKF 609-2Z: Ø24,40 mm desde Z=11,65 mm hasta Z=19,25 mm.",
            "Paso de eje transmisor A ampliado a Ø15,60 mm con holgura FDM.",
        ],
        "features_extra": [
            ("d_escalon", "30.20 / 28.31 mm", "Escalones exteriores de centrado axial"),
            ("pcd_4x", "4x Ø2.34 @ PCD 37.00", "4 agujeros de fijación en DBC Ø37,00 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Adaptador_Rodamiento_03_3D"],
    },
    {
        "item": 16,
        "archivo": "Sufridera_Eje_Ext_05a_3D.FCStd",
        "denominacion": "Sufridera Eje Exterior (Impr. 3D)",
        "plano_ref": "Plano Nº 5e-3D",
        "plano_original": "Plano Nº 5e-3D",
        "hoja_plano": "Plano_16_Sufridera_Eje_Ext_05a_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Brida Ø30,20 / nariz Ø13,59 x 9,81 mm; paso Ø10,22 / Ø9,46 FDM; 4x Ø2,64",
        "notas_taller": [
            "Encastra en bolsillo de Tapa Exterior 16a (brida Ø30,60 / nariz Ø14,00).",
            "Diámetros interiores adaptados a puntas de husillo: Ø10,22 y Ø9,46 mm.",
        ],
        "features_extra": [
            ("d_nariz", "13.59 mm", "Diámetro exterior de nariz (Z=0..5,96 / Z=3,85)"),
            ("pcd_4x", "4x Ø2.64 @ PCD 21.90", "4 agujeros fijación en DBC Ø21,90 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Sufridera_Eje_Ext_05a_3D"],
    },
    {
        "item": 17,
        "archivo": "Adaptador_Eje_04_3D.FCStd",
        "denominacion": "Adaptador de Eje (Impresión 3D)",
        "plano_ref": "Plano Nº 4-3D",
        "plano_original": "Plano Nº 4-3D",
        "hoja_plano": "Plano_17_Adaptador_Eje_04_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Cuerpo Ø43,03x12,46 mm; paso Ø30,28; 2x despeje Ø15,60 a ±28,31; 8x Ø2,34/2,57",
        "notas_taller": [
            "Despeje semicircular para sufrideras de barras guía ampliado a Ø15,60 mm.",
        ],
        "features_extra": [
            ("d_int", "30.28 mm", "Diámetro interior central"),
            ("pcd_ortog", "4x Ø3.02/2.34 @ PCD 37.76", "4 agujeros en ejes ortogonales 0°/90°"),
            ("pcd_45", "4x Ø2.57 @ PCD 37.76", "4 agujeros en ejes a 45°"),
        ],
        "es_comercial": False,
        "instancias": ["Adaptador_Eje_04_3D"],
    },
    {
        "item": 18,
        "archivo": "Anillo_Torica_13_3D.FCStd",
        "denominacion": "Anillo Prensa Tórica (Impresión 3D)",
        "plano_ref": "Plano Nº 13-3D",
        "plano_original": "Plano Nº 13-3D",
        "hoja_plano": "Plano_18_Anillo_Torica_13_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Anillo plano Ø105,70 x Ø84,18 x 3,78 mm; 4x Ø2,34 en PCD Ø98,16 mm",
        "notas_taller": [
            "Cantidad total: 2 piezas (prensa los O-Rings 75x3,55 en Tapa 16a y Tapa 16b).",
        ],
        "features_extra": [
            ("d_ext", "105.70 mm", "Diámetro exterior del anillo"),
            ("d_int", "84.18 mm", "Diámetro interior de paso camisa vidrio"),
            ("pcd_4x", "4x Ø2.34 @ PCD 98.16", "4 agujeros de fijación en DBC Ø98,16 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Anillo_Torica_Int_13_3D", "Anillo_Torica_Ext_13_3D"],
    },
    {
        "item": 19,
        "archivo": "Estructura_Interior_07_3D.FCStd",
        "denominacion": "Estructura Interior / Brida (Impr. 3D)",
        "plano_ref": "Plano Nº 7-3D",
        "plano_original": "Plano Nº 7-3D",
        "hoja_plano": "Plano_19_Estructura_Interior_07_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Placa 138,17x138,17x15,10 mm; aloj. Ø121,18; paso Ø109,55; 4x Ø16,69 tensores",
        "notas_taller": [
            "Cantidad: 2 unidades idénticas (fijan las tapas mediante los 4 tensores 06).",
            "Distancia entre centros de 4 tensores: cuadro 108,72 x 108,72 mm (PCD Ø153,74).",
        ],
        "features_extra": [
            ("d_aloj_cierre", "121.18 mm", "Rebaje centrado (Z=9,44..15,10 mm)"),
            ("d_paso_int", "109.55 mm", "Diámetro interior pasante"),
            ("c_tensores", "4x Ø16.69 @ 108.72x108.72", "Alojamiento 4 tensores (PCD Ø153,74 mm)"),
            ("pcd_fij", "4x Ø3.12 (127.8) / 4x Ø2.64 (115.2)", "Taladros perimetrales de fijación"),
        ],
        "es_comercial": False,
        "instancias": ["Estructura_Interior_1_07_3D", "Estructura_Interior_2_07_3D"],
    },
    {
        "item": 20,
        "archivo": "Cierre_Estructura_15_3D.FCStd",
        "denominacion": "Cierre de Estructura (Impresión 3D)",
        "plano_ref": "Plano Nº 15-3D",
        "plano_original": "Plano Nº 15-3D",
        "hoja_plano": "Plano_20_Cierre_Estructura_15_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Brida Ø133,63x21,52 mm; encastre Ø120,88; paso Ø98,15; 4x Ø4,15 en PCD Ø127,80",
        "notas_taller": [
            "Cantidad: 2 unidades (cierre posterior superior e inferior de tapas 16b y 16a).",
        ],
        "features_extra": [
            ("d_ext", "133.63 mm", "Diámetro exterior de brida"),
            ("d_encastre", "120.88 mm", "Diámetro de encastre (escalón Z=7,55..21,52)"),
            ("d_int", "98.15 mm", "Diámetro interior pasante"),
            ("pcd_4x", "4x Ø4.15 @ PCD 127.80", "4 agujeros fijación en DBC Ø127,80 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Cierre_Estructura_1_15_3D", "Cierre_Estructura_2_15_3D"],
    },
    {
        "item": 21,
        "archivo": "Tensor_Parte_1_06.FCStd",
        "denominacion": "Tensor Sup. - Parte 1 (Impr. 3D)",
        "plano_ref": "Plano Nº 6a-3D",
        "plano_original": "Plano Nº 6a-3D",
        "hoja_plano": "Plano_21_Tensor_Parte_1_06",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Tensor partido esc. 0,755: cuerpo Ø16,61x151,81 + espiga 30 mm (L=181,81)",
        "notas_taller": [
            "Cantidad: 4 unidades. Imprimir horizontal o con balsa y alta adhesión.",
            "Encastra por espiga triangular de 30 mm (r_esp=3,16) en Tensor Parte 2.",
        ],
        "features_extra": [],
        "es_comercial": False,
        "instancias": ["Tensor_1_Parte_1", "Tensor_2_Parte_1", "Tensor_3_Parte_1", "Tensor_4_Parte_1"],
    },
    {
        "item": 22,
        "archivo": "Tensor_Parte_2_06.FCStd",
        "denominacion": "Tensor Inf. - Parte 2 (Impr. 3D)",
        "plano_ref": "Plano Nº 6b-3D",
        "plano_original": "Plano Nº 6b-3D",
        "hoja_plano": "Plano_22_Tensor_Parte_2_06",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Tensor partido esc. 0,755: Ø18,12 / Ø16,61 x 139,09 mm; cavidad triangular 30 mm",
        "notas_taller": [
            "Cantidad: 4 unidades. Recibe la espiga triangular de Tensor Parte 1 (prof. 30 mm).",
        ],
        "features_extra": [],
        "es_comercial": False,
        "instancias": ["Tensor_1_Parte_2", "Tensor_2_Parte_2", "Tensor_3_Parte_2", "Tensor_4_Parte_2"],
    },
    {
        "item": 23,
        "archivo": "Tapa_Motor_01_3D.FCStd",
        "denominacion": "Tapa Motor Superior (Impresión 3D)",
        "plano_ref": "Plano Nº 1-3D",
        "plano_original": "Plano Nº 1-3D",
        "hoja_plano": "Plano_23_Tapa_Motor_01_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Placa 138,17x138,16x7,55 mm; piloto motor Ø30,20; 4x Ø16,69; 4x Ø7,85/Ø4,15",
        "notas_taller": [
            "Montada en extremo superior (Z=+80,63..+88,18) sobre los 4 Tensores Parte 1.",
            "Piloto motor Ø30,20 mm y 4 tornillos NEMA en cuadro 35,18 x 35,18 mm (±17,59).",
        ],
        "features_extra": [
            ("d_piloto_mot", "30.20 mm", "Piloto central de alineación de motor"),
            ("c_tensores", "4x Ø16.69 @ 108.72x108.72", "Alojamiento superior 4 tensores"),
            ("c_motor", "4x Ø4.15 / Ø7.85 @ ±17.59", "Fijación motor (cuadro 35,18 x 35,18 mm)"),
        ],
        "es_comercial": False,
        "instancias": ["Tapa_Motor_01_3D"],
    },
    # --- 7 Ítems Comerciales Adaptados al Prototipo 3D (Ítems 24..30) ---
    {
        "item": 24,
        "archivo": "Elementos_comericales/Rodamiento_SKF_609.FCStd",
        "denominacion": "Rodamiento Rígido de Bolas SKF 609",
        "plano_ref": "Comercial SKF",
        "material": "Acero SAE 1045 / 52100",
        "detalles": "Código comercial: SKF 609-2Z / DIN 625-1 (Ø9 x Ø24 x 7 mm)",
        "es_comercial": True,
        "instancias": ["Rodamiento_SKF_609"],
    },
    {
        "item": 25,
        "archivo": "Elementos_comericales/Reten_10x22x7.FCStd",
        "denominacion": "Retén Radial de Eje 10x22x7",
        "plano_ref": "Comercial DIN 3760",
        "material": "Elastómero NBR / Viton",
        "detalles": "Código comercial: Retén DBH / SAV 10x22x7 — DIN 3760 Forma A",
        "es_comercial": True,
        "instancias": ["Reten_10x22x7"],
    },
    {
        "item": 26,
        "archivo": "Elementos_comericales/ORing_75x3_55.FCStd",
        "denominacion": "O-Ring Estático Camisa Ø75x3,55",
        "plano_ref": "Comercial ISO 3601",
        "material": "Elastómero NBR / Viton",
        "detalles": "Código comercial: O-Ring DIN 3771 Ø75,0 x 3,55 mm (sello camisa vidrio)",
        "es_comercial": True,
        "instancias": ["ORing_Camisa_Int", "ORing_Camisa_Ext"],
    },
    {
        "item": 27,
        "archivo": "Elementos_comericales/ORing_69x3_55.FCStd",
        "denominacion": "O-Ring Dinámico Émbolo Ø69x3,55",
        "plano_ref": "Comercial ISO 3601",
        "material": "Elastómero NBR / Viton",
        "detalles": "Código comercial: O-Ring DIN 3771 Ø69,0 x 3,55 mm (sello pistón Delrin)",
        "es_comercial": True,
        "instancias": ["ORing_Embolo_3D"],
    },
    {
        "item": 28,
        "archivo": "Elementos_comericales/ORing_11_2x1_8.FCStd",
        "denominacion": "O-Ring Estático de Eje Ø11,2x1,8",
        "plano_ref": "Comercial ISO 3601",
        "material": "Elastómero NBR / Viton",
        "detalles": "Código comercial: O-Ring DIN 3771 Ø11,2 x 1,80 mm (sello eje transmisor)",
        "es_comercial": True,
        "instancias": ["ORing_Eje_11_2x1_8"],
    },
    {
        "item": 29,
        "archivo": "Elementos_comericales/Pasador_3x14.FCStd",
        "denominacion": "Pasador Elástico Ø3x14 mm",
        "plano_ref": "Comercial ISO 8752",
        "material": "Acero SAE 1045",
        "detalles": "Código comercial: Espina elástica ISO 8752 / DIN 1481 — Ø3 x 14 mm",
        "es_comercial": True,
        "instancias": ["Pasador_3x14_1", "Pasador_3x14_2"],
    },
    {
        "item": 30,
        "archivo": "Elementos_comericales/Pasador_3x10.FCStd",
        "denominacion": "Pasador Elástico Ø3x10 mm",
        "plano_ref": "Comercial ISO 8752",
        "material": "Acero SAE 1045",
        "detalles": "Código comercial: Espina elástica ISO 8752 / DIN 1481 — Ø3 x 10 mm",
        "es_comercial": True,
        "instancias": ["Pasador_3x10_3"],
    },
]

RESUMEN_BULONERIA_ESTANDAR_3D = [
    "Tornillería de fijación métrica a escala 0,755 (M2 / M2,5 / M3 / M4 según taladros del conjunto).",
    "4x Varillas Tensores partidas (Parte 1 + Parte 2) con tornillos axiales en extremos (agujero Ø6,32 mm).",
    "Tornillería M2,5 / M3 para Sufridera Interior (05b), Tapa Sufridera (05a), Anillos Tóricos (13) y Centro Émbolo.",
    "4x Tornillos M3/M4 en Tapa Motor Superior (01) para fijación de motor acoplado (cuadro 35,18 x 35,18 mm).",
    "Nota: Piezas impresas en PLA+/PETG incluyen holgura FDM de +0,20 mm en radios de alojamientos críticos.",
]


def _extraer_shape_solido_y_params(ruta_fcstd):
    """
    Abre un `.FCStd` del modelo 3D en su geometría actual (Modo 1 Impresión 3D / Modo 3 Comercial),
    extrae su Shape sólido principal, volumen, masa real (desde Materiales) y parámetros.
    """
    nombre_base = os.path.basename(ruta_fcstd)
    doc_temp = App.openDocument(ruta_fcstd)
    doc_temp.recompute()

    # 1. Extraer sólido principal
    shape_final = None
    part_objs = [o for o in doc_temp.Objects if o.TypeId == "App::Part"]
    if part_objs:
        p0 = part_objs[0]
        if hasattr(p0, "Shape") and not p0.Shape.isNull() and p0.Shape.Solids:
            shape_final = p0.Shape.copy()
        else:
            sols_p = [
                g for g in p0.Group
                if g.isDerivedFrom("Part::Feature")
                and not g.isDerivedFrom("Part::Datum")
                and not g.Shape.isNull()
                and g.Shape.Solids
            ]
            if sols_p:
                finales = [o for o in sols_p if not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
                elegido = (finales[-1] if finales else max(sols_p, key=lambda o: o.Shape.Volume))
                shape_final = elegido.Shape.copy()

    if shape_final is None:
        candidatos = [
            o for o in doc_temp.Objects
            if o.isDerivedFrom("Part::Feature")
            and not o.isDerivedFrom("Part::Datum")
            and not o.Shape.isNull()
            and o.Shape.Solids
        ]
        if not candidatos:
            App.closeDocument(doc_temp.Name)
            raise RuntimeError(f"No se encontró sólido válido en {ruta_fcstd}")
        finales = [o for o in candidatos if not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
        elegido = (finales[-1] if finales else max(candidatos, key=lambda o: o.Shape.Volume))
        shape_final = elegido.Shape.copy()

    # 2. Extraer densidad y masa desde hoja Materiales
    densidad_kg_mm3 = 1.24e-6  # PLA+ por defecto
    mat_sp = doc_temp.getObject("Materiales")
    if mat_sp:
        for celda in ("C2", "C3"):
            try:
                val = str(mat_sp.get(celda))
                m = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", val)
                if m:
                    num = float(m.group(0))
                    if num > 100.0:  # kg/m^3 -> convertir a kg/mm^3
                        num = num * 1e-9
                    elif num > 0.1:  # g/cm^3 -> convertir a kg/mm^3
                        num = num * 1e-6
                    densidad_kg_mm3 = num
                    break
            except Exception:
                pass
    masa_g = shape_final.Volume * densidad_kg_mm3 * 1000.0

    # 3. Extraer parámetros desde Parametros
    filas_param = []
    param_sp = doc_temp.getObject("Parametros")
    if param_sp:
        celdas = param_sp.getNonEmptyCells() if hasattr(param_sp, "getNonEmptyCells") else param_sp.getUsedCells()
        filas = sorted({int(c[1:]) for c in celdas if c.startswith("A") and c[1:].isdigit()})
        for f in filas:
            if f < 5:
                continue
            try:
                simb = str(param_sp.get(f"A{f}")).strip()
            except Exception:
                continue
            if not simb or simb in ("ALIAS", "SIMBOLO", "escala", "esc", "holgura", "holgura_fdm"):
                continue
            try:
                v_nom = param_sp.get(f"B{f}")
                val_txt = f"{float(v_nom):.2f} mm" if isinstance(v_nom, (int, float)) else str(v_nom)
            except Exception:
                val_txt = "-"
            try:
                desc = str(param_sp.get(f"D{f}")).strip()
            except Exception:
                desc = ""
            if not desc or desc == val_txt:
                desc = simb.replace("_", " ").capitalize()
            filas_param.append((simb, val_txt, desc))

    App.closeDocument(doc_temp.Name)
    return {
        "shape": shape_final,
        "masa_g": masa_g,
        "filas_param": filas_param,
        "archivo": nombre_base,
    }


def _crear_hoja_datos_rotulo_3d(doc_planos):
    """Crea la hoja central Datos_Rotulo para el legajo de Impresión 3D."""
    dr = doc_planos.addObject("Spreadsheet::Sheet", "Datos_Rotulo")
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
        ("PROYECTO", "Bomba de Flujo Cardíaco - Modelo Impresión 3D (Esc. 75,5%)", "Proyecto 3D a escala"),
        ("AUTOR", "Dib.: F. Gutiérrez", "Autor / Dibujante"),
        ("APROBADO", "Apr.: Ing. A. Bonino", "Revisión y aprobación"),
        ("FECHA", "12/11/2026", "Fecha de emisión"),
        ("TOL_GRAL", "FDM ±0,20 mm", "Tolerancia general impresión 3D"),
    ]
    base_dict = {}
    for idx, (k, v, dsc) in enumerate(campos, start=2):
        dr.set(f"A{idx}", k)
        dr.set(f"B{idx}", v)
        dr.set(f"C{idx}", dsc)
        base_dict[k] = v
    return dr, base_dict


def _crear_hoja_tabla_bom_3d(doc_planos, items_bom, masa_total_g):
    """Crea la hoja Tabla_BOM_IRAM para trazabilidad y validación."""
    tb = doc_planos.addObject("Spreadsheet::Sheet", "Tabla_BOM_IRAM")
    tb.Label = "Tabla_BOM_IRAM"
    headers = ["ITEM", "CANT", "DENOMINACION", "PLANO_REF", "MATERIAL", "NORMA_CODIGO_DETALLES", "MASA_UNIT_G"]
    for idx_c, h in enumerate(headers):
        tb.set(f"{chr(65 + idx_c)}1", h)

    for idx_r, it in enumerate(items_bom, start=2):
        tb.set(f"A{idx_r}", str(it["item"]))
        tb.set(f"B{idx_r}", str(it["cantidad"]))
        tb.set(f"C{idx_r}", it["denominacion"])
        tb.set(f"D{idx_r}", it["plano_ref"])
        tb.set(f"E{idx_r}", it["material"])
        tb.set(f"F{idx_r}", it["detalles"])
        tb.set(f"G{idx_r}", f"{it['masa_g']:.2f}")

    fila_tot = len(items_bom) + 2
    tb.set(f"F{fila_tot}", "MASA TOTAL ESTIMADA DEL CONJUNTO 3D (g):")
    tb.set(f"G{fila_tot}", f"{masa_total_g:.2f}")
    return tb


def _crear_pagina_iram(doc_planos, nombre_pagina, titulo_pagina, formato, rutas_plantillas, rotulo):
    page = doc_planos.addObject("TechDraw::DrawPage", nombre_pagina)
    page.Label = titulo_pagina
    tpl = doc_planos.addObject("TechDraw::DrawSVGTemplate", f"Template_{nombre_pagina}")
    tpl.Template = rutas_plantillas[formato]
    page.Template = tpl
    for k, v in rotulo.items():
        try:
            tpl.setEditFieldContent(k, str(v))
        except Exception:
            pass
    return page, tpl


def _agregar_globo(doc_planos, page, vista, item_num, pt3d_centro, centro_vista, escala_vista, dx, dy, prefijo=""):
    """Proyecta un punto 3D isométrico al sistema de `DrawViewBalloon` (coordenadas de la vista fuente)."""
    rel = pt3d_centro - centro_vista
    # Vectores unitarios de proyección isométrica estándar en planos_iram / generar_planos
    ux = App.Vector(1.0, 1.0, 0.0).normalize()
    uz_dir = App.Vector(1.0, -1.0, 1.0).normalize()
    uy = uz_dir.cross(ux).normalize()  # (-1, 1, 2)/sqrt(6)

    # FreeCAD TechDraw escala OriginX/Y y X/Y de DrawViewBalloon por SourceView.Scale
    ox = rel.dot(ux)
    oy = rel.dot(uy)

    bal = doc_planos.addObject("TechDraw::DrawViewBalloon", f"Globo_{prefijo}_{item_num:02d}")
    page.addView(bal)
    bal.SourceView = vista
    bal.OriginX = ox
    bal.OriginY = oy
    bal.X = ox + (dx / escala_vista)
    bal.Y = oy + (dy / escala_vista)
    bal.Text = str(item_num)
    bal.BubbleShape = "Circular"
    bal.EndType = "Filled arrow"
    bal.ShapeScale = 0.78
    bal.KinkLength = 3.5
    vo = getattr(bal, "ViewObject", None)
    if vo:
        try:
            vo.Fontsize = 3.2
            vo.LineWidth = 0.25
        except Exception:
            pass
    return bal


def _generar_svg_recuadro_subensamblaje(titulo, subt, ancho_mm, alto_mm):
    W, H = ancho_mm, alto_mm
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">
  <rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{H - 1.0:.1f}" fill="none" stroke="#000000" stroke-width="0.45"/>
  <rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="8.0" fill="#eef3f8" stroke="#000000" stroke-width="0.45"/>
  <text x="4.0" y="5.6" font-family="Liberation Sans, Arial, sans-serif" font-size="3.1" font-weight="bold">{titulo}</text>
  <text x="{W - 4.0:.1f}" y="5.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.7" text-anchor="end">{subt}</text>
</svg>"""


def main():
    print("=================================================================")
    print("GENERADOR DE PLANOS IRAM - MODELO IMPRESIÓN 3D (ESCALA 0,755)")
    print("FreeCAD:", ".".join(str(x) for x in App.Version()[:3]))
    print("=================================================================")

    if not os.path.exists(RUTA_ENSAMBLAJE_3D):
        raise FileNotFoundError(f"Falta el ensamblaje 3D: {RUTA_ENSAMBLAJE_3D}")

    rutas_plantillas = asegurar_plantillas_iram(DIR_PLANTILLAS)
    pat_file = obtener_ruta_fcpat()
    if not pat_file:
        print("AVISO: No se encontró FCPat.pat; el rayado de cortes podría omitirse.")

    # 1. Leer ensamblaje 3D para extraer placements exactos de cada una de las 46 instancias
    doc_assy = App.openDocument(RUTA_ENSAMBLAJE_3D)
    doc_assy.recompute()
    shapes_ens = {}
    for o in doc_assy.Objects:
        if o.TypeId == "App::Link" and getattr(o, "LinkedObject", None):
            sh = o.Shape.copy() if (hasattr(o, "Shape") and not o.Shape.isNull()) else None
            if sh is not None:
                shapes_ens[o.Name] = sh
    App.closeDocument(doc_assy.Name)
    print(f"Instancias leídas desde {os.path.basename(RUTA_ENSAMBLAJE_3D)}: {len(shapes_ens)}")

    # 2. Extraer Shape real, masa y parámetros de cada uno de los 30 archivos fuente (Modo 1 / Modo 3)
    datos_piezas = {}
    items_bom_completos = []
    masa_total_g = 0.0

    for entrada in CATALOGO_ITEMS_BOM_3D:
        it_num = entrada["item"]
        ruta_f = os.path.join(DIR_PIEZAS, entrada["archivo"])
        if not os.path.exists(ruta_f):
            raise FileNotFoundError(f"No se encontró pieza ítem {it_num}: {ruta_f}")
        info = _extraer_shape_solido_y_params(ruta_f)

        # Fusionar parámetros del archivo con características funcionales verificadas en el sólido
        filas_unicas = []
        vistos = set()
        for simb, val, desc in info["filas_param"]:
            filas_unicas.append((simb, val, desc))
            vistos.add(simb)
        for simb, val, desc in entrada.get("features_extra", []):
            if simb not in vistos:
                filas_unicas.append((simb, val, desc))
                vistos.add(simb)
        info["filas_param"] = filas_unicas
        datos_piezas[it_num] = info

        cant = len(entrada["instancias"])
        masa_u = info["masa_g"]
        masa_total_g += masa_u * cant

        items_bom_completos.append(
            {
                "item": it_num,
                "cantidad": cant,
                "denominacion": entrada["denominacion"],
                "plano_ref": entrada["plano_ref"],
                "material": entrada["material"],
                "detalles": entrada["detalles"],
                "masa_g": masa_u,
                "es_comercial": entrada["es_comercial"],
            }
        )

    print(f"BOM 3D procesada: {len(items_bom_completos)} ítems, masa total = {masa_total_g:.1f} g ({masa_total_g/1000.0:.2f} kg)")

    # 3. Crear documento maestro Planos_Impresion_3D
    nombre_doc = "Planos_Impresion_3D"
    try:
        prev = App.getDocument(nombre_doc)
        if prev:
            App.closeDocument(prev.Name)
    except Exception:
        pass

    doc_planos = App.newDocument(nombre_doc)
    grupo_fuentes = doc_planos.addObject("App::DocumentObjectGroup", "Solidos_Fuente_Planos_3D")

    dr, campos_base = _crear_hoja_datos_rotulo_3d(doc_planos)
    tb = _crear_hoja_tabla_bom_3d(doc_planos, items_bom_completos, masa_total_g)
    total_hojas = 3 + sum(1 for e in CATALOGO_ITEMS_BOM_3D if not e["es_comercial"])  # 3 + 23 = 26

    # =========================================================================
    # HOJA 1: PLANO 00a - CONJUNTO GENERAL ARMADO Y CORTE LONGITUDINAL A-A (A2)
    # =========================================================================
    comp_ens = Part.makeCompound(list(shapes_ens.values()))
    bb_ens = comp_ens.BoundBox

    obj_ens = doc_planos.addObject("Part::Feature", "Ensamblaje_3D_Armado")
    obj_ens.Shape = comp_ens
    if getattr(obj_ens, "ViewObject", None):
        obj_ens.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_ens)

    rotulo_00a = dict(campos_base)
    rotulo_00a.update(
        {
            "ESCALA": "1:2",
            "FORMATO": "IRAM A2",
            "HOJA": f"1/{total_hojas}",
            "TITULO": "Conjunto General Armado - Prototipo Impresión 3D",
            "MATERIAL": "PLA+/PETG, Vidrio, Inox, Delrin",
            "MASA": f"{masa_total_g / 1000.0:.2f} kg",
            "TOL_GRAL": "FDM ±0,20 mm",
            "NUM_PLANO": "Plano Nº 0a-3D",
        }
    )
    page_00a, _ = _crear_pagina_iram(
        doc_planos, "Plano_00a_Conjunto_Armado_3D", "Plano_00a_Conjunto_Armado_3D", "A2", rutas_plantillas, rotulo_00a
    )

    v_arm_frente = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Frente")
    page_00a.addView(v_arm_frente)
    v_arm_frente.Source = [obj_ens]
    v_arm_frente.Direction = App.Vector(0, -1, 0)
    v_arm_frente.XDirection = App.Vector(1, 0, 0)
    v_arm_frente.ScaleType = "Custom"
    v_arm_frente.Scale = 0.5
    v_arm_frente.X = 125.0
    v_arm_frente.Y = 215.0
    v_arm_frente.Caption = ""
    estilizar_vista_iram(v_arm_frente, mostrar_ocultas=False, mostrar_centros=True)

    v_arm_corte = doc_planos.addObject("TechDraw::DrawViewSection", "V00a_Corte_AA")
    page_00a.addView(v_arm_corte)
    v_arm_corte.BaseView = v_arm_frente
    v_arm_corte.Source = [obj_ens]
    v_arm_corte.Direction = App.Vector(0, -1, 0)
    v_arm_corte.XDirection = App.Vector(1, 0, 0)
    v_arm_corte.SectionNormal = App.Vector(0, -1, 0)
    v_arm_corte.SectionDirection = "Up"
    v_arm_corte.SectionOrigin = bb_ens.Center
    v_arm_corte.SectionSymbol = "A"
    v_arm_corte.SectionLineStretch = 1.0
    v_arm_corte.FuseBeforeCut = False
    v_arm_corte.CutSurfaceDisplay = "PatHatch"
    if pat_file:
        v_arm_corte.FileGeomPattern = pat_file
        v_arm_corte.NameGeomPattern = "Diagonal4"
        v_arm_corte.HatchScale = 2.0
    v_arm_corte.ScaleType = "Custom"
    v_arm_corte.Scale = 0.5
    v_arm_corte.X = 295.0
    v_arm_corte.Y = 215.0
    v_arm_corte.Caption = ""
    estilizar_vista_iram(v_arm_corte, mostrar_ocultas=False, mostrar_centros=True)

    v_arm_iso = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Isometrica")
    page_00a.addView(v_arm_iso)
    v_arm_iso.Source = [obj_ens]
    v_arm_iso.Direction = App.Vector(1, -1, 1)
    v_arm_iso.XDirection = App.Vector(1, 1, 0)
    v_arm_iso.ScaleType = "Custom"
    v_arm_iso.Scale = 0.45
    v_arm_iso.X = 470.0
    v_arm_iso.Y = 235.0
    v_arm_iso.Caption = ""
    estilizar_vista_iram(v_arm_iso, mostrar_ocultas=False, mostrar_centros=False)

    for nm, txt, xv, yv in [
        ("Txt_00a_Frente", ["VISTA FRONTAL (1:2)"], 125.0, 336.0),
        ("Txt_00a_Corte", ["CORTE LONGITUDINAL A - A (1:2)"], 295.0, 336.0),
        ("Txt_00a_Iso", ["PERSPECTIVA ISOMÉTRICA (1:2,2)"], 470.0, 336.0),
    ]:
        an = doc_planos.addObject("TechDraw::DrawViewAnnotation", nm)
        page_00a.addView(an)
        an.Text = txt
        an.TextSize = 3.8
        an.X = xv
        an.Y = yv

    # =========================================================================
    # HOJA 2: PLANO 00b - VISTA EXPLOTADA GENERAL (46 UN.) + 2 SUBENSAMBLAJES (A2)
    # =========================================================================
    rotulo_00b = dict(campos_base)
    rotulo_00b.update(
        {
            "ESCALA": "Varias",
            "FORMATO": "IRAM A2",
            "HOJA": f"2/{total_hojas}",
            "TITULO": "Vista Explotada y Subensamblajes - Impresión 3D",
            "MATERIAL": "Según Tabla IRAM 4508",
            "MASA": f"{masa_total_g / 1000.0:.2f} kg",
            "TOL_GRAL": "FDM ±0,20 mm",
            "NUM_PLANO": "Plano Nº 0b-3D",
        }
    )
    page_00b, _ = _crear_pagina_iram(
        doc_planos, "Plano_00b_Vista_Explotada_3D", "Plano_00b_Vista_Explotada_3D", "A2", rutas_plantillas, rotulo_00b
    )

    # Desplazamientos de explosión limpia por instancia (todos en mm del ensamblaje 3D)
    offsets_gen = {
        "Tapa_Motor_01_3D": App.Vector(0, 0, 175),
        "Cierre_Estructura_1_15_3D": App.Vector(0, 0, 115),
        "Estructura_Interior_1_07_3D": App.Vector(0, 0, 80),
        "Tapa_Interior_16b_3D": App.Vector(0, 0, 45),
        "Anillo_Torica_Int_13_3D": App.Vector(0, 0, 22),
        "ORing_Camisa_Int": App.Vector(0, 0, 10),
        "Cilindro_09_3D": App.Vector(0, 0, 0),
        "ORing_Camisa_Ext": App.Vector(0, 0, -25),
        "Anillo_Torica_Ext_13_3D": App.Vector(0, 0, -45),
        "Tapa_Exterior_16a_3D": App.Vector(0, 0, -75),
        "Estructura_Interior_2_07_3D": App.Vector(0, 0, -110),
        "Cierre_Estructura_2_15_3D": App.Vector(0, 0, -145),
        # Tensores partidos explotados radialmente en Z (+/-) para distinguir Parte 1 y Parte 2
        "Tensor_1_Parte_1": App.Vector(65, 65, 35),
        "Tensor_2_Parte_1": App.Vector(-65, 65, 35),
        "Tensor_3_Parte_1": App.Vector(-65, -65, 35),
        "Tensor_4_Parte_1": App.Vector(65, -65, 35),
        "Tensor_1_Parte_2": App.Vector(65, 65, -45),
        "Tensor_2_Parte_2": App.Vector(-65, 65, -45),
        "Tensor_3_Parte_2": App.Vector(-65, -65, -45),
        "Tensor_4_Parte_2": App.Vector(65, -65, -45),
        # Tren central interno desplazado levemente hacia +Z o en su eje
        "Transmisor_A_02a_3D": App.Vector(0, 0, 130),
        "Transmisor_B_02b_3D": App.Vector(0, 0, 75),
        "Tornillo_Sin_Fin_14_3D": App.Vector(0, 0, -20),
        "Adaptador_Rodamiento_03_3D": App.Vector(0, 0, 95),
        "Rodamiento_SKF_609": App.Vector(0, 0, 108),
        "Sufridera_Int_05b_3D": App.Vector(0, 0, 62),
        "Reten_10x22x7": App.Vector(0, 0, 70),
        "Tapa_Sufridera_Int_05a_3D": App.Vector(0, 0, 52),
        "Adaptador_Eje_04_3D": App.Vector(0, 0, 38),
        "Sufridera_Eje_Ext_05a_3D": App.Vector(0, 0, -90),
    }

    inst_a_item = {}
    for entrada in CATALOGO_ITEMS_BOM_3D:
        for ins in entrada["instancias"]:
            inst_a_item[ins] = entrada["item"]

    shapes_exp_gen = []
    puntos_globo_gen = {}
    for ins, sh in shapes_ens.items():
        sh_c = sh.copy()
        off = offsets_gen.get(ins, App.Vector(0, 0, 0))
        sh_c.translate(off)
        shapes_exp_gen.append(sh_c)
        it_num = inst_a_item.get(ins)
        if it_num and it_num not in puntos_globo_gen:
            puntos_globo_gen[it_num] = sh_c.BoundBox.Center

    # Preferencias de instancias representativas para los 10 globos de Vista Explotada General
    for it_num, ins_pref in [
        (1, "Tapa_Exterior_16a_3D"),
        (2, "Cilindro_09_3D"),
        (3, "Tapa_Interior_16b_3D"),
        (18, "Anillo_Torica_Int_13_3D"),
        (19, "Estructura_Interior_1_07_3D"),
        (20, "Cierre_Estructura_2_15_3D"),
        (21, "Tensor_4_Parte_1"),
        (22, "Tensor_4_Parte_2"),
        (23, "Tapa_Motor_01_3D"),
        (26, "ORing_Camisa_Ext"),
    ]:
        if ins_pref in shapes_ens:
            sh_c = shapes_ens[ins_pref].copy()
            sh_c.translate(offsets_gen.get(ins_pref, App.Vector(0, 0, 0)))
            puntos_globo_gen[it_num] = sh_c.BoundBox.Center

    comp_exp_gen = Part.makeCompound(shapes_exp_gen)
    obj_exp_gen = doc_planos.addObject("Part::Feature", "Ensamblaje_3D_Explotado_General")
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
    v_exp_gen.Y = 300.0
    v_exp_gen.Caption = "Vista Explotada General del Prototipo 3D (Esc. 1:4) — Ítems estructurales y camisa"
    estilizar_vista_iram(v_exp_gen, mostrar_ocultas=False, mostrar_centros=False)

    centro_gen = comp_exp_gen.BoundBox.Center
    globos_gen = [
        (23, 58.0, 20.0),
        (19, -62.0, 24.0),
        (3, 64.0, 20.0),
        (18, -62.0, 10.0),
        (2, 66.0, -10.0),
        (26, -62.0, 14.0),
        (1, -62.0, 0.0),
        (20, -62.0, -4.0),
        (21, 66.0, 16.0),
        (22, 64.0, -14.0),
    ]
    for it_num, dx, dy in globos_gen:
        pt3d = puntos_globo_gen.get(it_num)
        if pt3d is not None:
            _agregar_globo(doc_planos, page_00b, v_exp_gen, it_num, pt3d, centro_gen, escala_exp_gen, dx, dy, "Gen")

    # --- 2.2 Subensamblaje I: Émbolo y Guías (abajo izquierda) ---
    simb_sub1 = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_Sub_Embolo")
    page_00b.addView(simb_sub1)
    simb_sub1.Symbol = _generar_svg_recuadro_subensamblaje(
        "DETALLE A: SUBENSAMBLAJE DE ÉMBOLO Y GUÍAS", "ESCALA 1:2", 178.0, 152.0
    )
    simb_sub1.X = 120.0
    simb_sub1.Y = 96.0

    shapes_sub_emb = []
    puntos_sub_emb = {}

    sh_emb = datos_piezas[7]["shape"].copy()
    shapes_sub_emb.append(sh_emb)
    puntos_sub_emb[7] = sh_emb.BoundBox.Center

    sh_or_emb = datos_piezas[27]["shape"].copy()
    sh_or_emb.translate(App.Vector(0, 0, -26))
    shapes_sub_emb.append(sh_or_emb)
    puntos_sub_emb[27] = App.Vector(34.5, 0, -26)

    sh_ce1 = datos_piezas[8]["shape"].copy()
    sh_ce1.translate(App.Vector(0, 0, 32))
    shapes_sub_emb.append(sh_ce1)
    puntos_sub_emb[8] = sh_ce1.BoundBox.Center

    sh_ce2 = datos_piezas[9]["shape"].copy()
    sh_ce2.translate(App.Vector(0, 0, -45))
    shapes_sub_emb.append(sh_ce2)
    puntos_sub_emb[9] = sh_ce2.BoundBox.Center

    sh_sens = datos_piezas[10]["shape"].copy()
    sh_sens.translate(App.Vector(20.02, 20.02, 26))
    shapes_sub_emb.append(sh_sens)
    puntos_sub_emb[10] = sh_sens.BoundBox.Center

    sh_sg1 = datos_piezas[6]["shape"].copy()
    sh_sg1.translate(App.Vector(-28.31, 0, 48))
    shapes_sub_emb.append(sh_sg1)
    puntos_sub_emb[6] = sh_sg1.BoundBox.Center

    sh_g1 = datos_piezas[11]["shape"].copy()
    sh_g1.translate(App.Vector(28.31, 0, -90))
    shapes_sub_emb.append(sh_g1)
    puntos_sub_emb[11] = App.Vector(28.31, 0, 15)

    comp_sub_emb = Part.makeCompound(shapes_sub_emb)
    obj_sub_emb = doc_planos.addObject("Part::Feature", "Subensamblaje_Embolo_3D")
    obj_sub_emb.Shape = comp_sub_emb
    if getattr(obj_sub_emb, "ViewObject", None):
        obj_sub_emb.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_sub_emb)

    escala_sub_emb = 0.45
    v_sub_emb = doc_planos.addObject("TechDraw::DrawViewPart", "V00b_Sub_Embolo")
    page_00b.addView(v_sub_emb)
    v_sub_emb.Source = [obj_sub_emb]
    v_sub_emb.Direction = App.Vector(1, -1, 1)
    v_sub_emb.XDirection = App.Vector(1, 1, 0)
    v_sub_emb.ScaleType = "Custom"
    v_sub_emb.Scale = escala_sub_emb
    v_sub_emb.X = 120.0
    v_sub_emb.Y = 95.0
    v_sub_emb.Caption = ""
    estilizar_vista_iram(v_sub_emb, mostrar_ocultas=False, mostrar_centros=False)

    centro_sub_emb = comp_sub_emb.BoundBox.Center
    for it_num, dx, dy in [
        (7, -36.0, 10.0),
        (27, -36.0, -16.0),
        (8, -32.0, 26.0),
        (9, 32.0, -24.0),
        (10, 38.0, 14.0),
        (6, -42.0, 32.0),
        (11, 42.0, -6.0),
    ]:
        _agregar_globo(doc_planos, page_00b, v_sub_emb, it_num, puntos_sub_emb[it_num], centro_sub_emb, escala_sub_emb, dx, dy, "Emb")

    # --- 2.3 Subensamblaje II: Transmisión y Sellado de Eje (abajo centro-derecha) ---
    simb_sub2 = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_Sub_Transmision")
    page_00b.addView(simb_sub2)
    simb_sub2.Symbol = _generar_svg_recuadro_subensamblaje(
        "DETALLE B: SISTEMA DE TRANSMISIÓN Y SELLADO DE EJE", "ESCALA 1:3,5", 184.0, 152.0
    )
    simb_sub2.X = 308.0
    simb_sub2.Y = 96.0

    shapes_sub_tr = []
    puntos_sub_tr = {}

    def _add_tr(item_id, dz, dx=0.0, dy=0.0, rot_deg=0.0):
        sh_t = datos_piezas[item_id]["shape"].copy()
        if rot_deg != 0.0:
            sh_t.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), rot_deg)
        sh_t.translate(App.Vector(dx, dy, dz))
        shapes_sub_tr.append(sh_t)
        puntos_sub_tr[item_id] = sh_t.BoundBox.Center

    _add_tr(14, -135)                # Tornillo Sin Fin (abajo)
    _add_tr(16, -100)                # Sufridera Eje Ext
    _add_tr(30, -85, dy=-22, rot_deg=90)   # Pasador 3x10
    _add_tr(5,  -72)                 # Tapa Sufridera Int
    _add_tr(25, -58)                 # Retén 10x22x7
    _add_tr(4,  -42)                 # Sufridera Int
    _add_tr(13, -10)                 # Transmisor B
    _add_tr(28, 30, dy=-20)          # O-Ring 11.2x1.8
    _add_tr(17, 45)                  # Adaptador Eje
    _add_tr(29, 62, dy=-26, rot_deg=90)    # Pasador 3x14
    _add_tr(15, 82)                  # Adaptador Rodamiento
    _add_tr(24, 108)                 # SKF 609
    _add_tr(12, 130)                 # Transmisor A

    comp_sub_tr = Part.makeCompound(shapes_sub_tr)
    obj_sub_tr = doc_planos.addObject("Part::Feature", "Subensamblaje_Transmision_3D")
    obj_sub_tr.Shape = comp_sub_tr
    if getattr(obj_sub_tr, "ViewObject", None):
        obj_sub_tr.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_sub_tr)

    escala_sub_tr = 0.28
    v_sub_tr = doc_planos.addObject("TechDraw::DrawViewPart", "V00b_Sub_Transmision")
    page_00b.addView(v_sub_tr)
    v_sub_tr.Source = [obj_sub_tr]
    v_sub_tr.Direction = App.Vector(1, -1, 1)
    v_sub_tr.XDirection = App.Vector(1, 1, 0)
    v_sub_tr.ScaleType = "Custom"
    v_sub_tr.Scale = escala_sub_tr
    v_sub_tr.X = 308.0
    v_sub_tr.Y = 96.0
    v_sub_tr.Caption = ""
    estilizar_vista_iram(v_sub_tr, mostrar_ocultas=False, mostrar_centros=False)

    centro_sub_tr = comp_sub_tr.BoundBox.Center
    for it_num, dx, dy in [
        (12, 46.0, 14.0),
        (24, 46.0, 4.0),
        (15, -46.0, 16.0),
        (29, -50.0, 8.0),
        (17, 46.0, -4.0),
        (28, -50.0, 0.0),
        (13, 46.0, -16.0),
        (4,  -46.0, -8.0),
        (25, -48.0, -16.0),
        (5,  -46.0, -24.0),
        (30, 48.0, -26.0),
        (16, -46.0, -31.0),
        (14, 46.0, -22.0),
    ]:
        _agregar_globo(doc_planos, page_00b, v_sub_tr, it_num, puntos_sub_tr[it_num], centro_sub_tr, escala_sub_tr, dx, dy, "Tr")

    # =========================================================================
    # HOJA 3: PLANO 00c - LISTA DE MATERIALES Y DESPIECE IRAM 4508 (A3)
    # =========================================================================
    rotulo_00c = dict(campos_base)
    rotulo_00c.update(
        {
            "ESCALA": "S/E",
            "FORMATO": "IRAM A3",
            "HOJA": f"3/{total_hojas}",
            "TITULO": "Lista de Materiales 3D (30 Ítems / 46 Piezas)",
            "MATERIAL": "Según Tabla IRAM 4508",
            "MASA": f"Total: {masa_total_g / 1000.0:.2f} kg",
            "TOL_GRAL": "FDM ±0,20 mm",
            "NUM_PLANO": "Plano Nº 0c-3D",
        }
    )
    page_00c, _ = _crear_pagina_iram(
        doc_planos, "Plano_00c_Lista_Materiales_3D", "Plano_00c_Lista_Materiales_3D", "A3", rutas_plantillas, rotulo_00c
    )

    simbolo_bom = doc_planos.addObject("TechDraw::DrawViewSymbol", "Tabla_BOM_Visual")
    page_00c.addView(simbolo_bom)
    simbolo_bom.Symbol = generar_svg_tabla_bom_iram(
        items_bom_completos, RESUMEN_BULONERIA_ESTANDAR_3D, ancho_mm=382.0
    )
    simbolo_bom.ScaleType = "Custom"
    simbolo_bom.Scale = 0.96
    simbolo_bom.X = 217.5
    simbolo_bom.Y = 175.0

    # =========================================================================
    # HOJAS 4 A 26: 23 PLANOS INDIVIDUALES DE PIEZAS A ESCALA 3D (Ítems 1..23)
    # =========================================================================
    num_hoja_actual = 4
    piezas_meta = {}
    for entrada in CATALOGO_ITEMS_BOM_3D:
        if entrada["es_comercial"]:
            continue

        it_num = entrada["item"]
        info = datos_piezas[it_num]
        sh_p = info["shape"]
        masa_g = info["masa_g"]
        filas_param = info["filas_param"]
        nombre_hoja = entrada["hoja_plano"]

        obj_p = doc_planos.addObject("Part::Feature", f"Solido_Item_{it_num:02d}")
        obj_p.Label = entrada["denominacion"]
        obj_p.Shape = sh_p
        if getattr(obj_p, "ViewObject", None):
            obj_p.ViewObject.Visibility = False
        grupo_fuentes.addObject(obj_p)

        bb = sh_p.BoundBox
        formato, escala_num, escala_txt = seleccionar_formato_y_escala(bb, es_conjunto=False)
        # Promover A4 -> A3 si al chocar con el rótulo la columna de vistas + cotas queda apretada
        if formato == "A4":
            w_p = max(4.0, bb.XLength * escala_num)
            h_p = max(4.0, bb.YLength * escala_num)
            h_c = max(4.0, bb.ZLength * escala_num)
            rx_a4 = (FORMATOS_IRAM["A4"][0] - 10.0) - 175.0  # 112.0 mm
            if (86.0 + 0.5 * w_p + 18.0) >= rx_a4 and (h_p + h_c + 52.0) > (FORMATOS_IRAM["A4"][1] - 18.0 - 64.0 - 12.0):
                formato = "A3"
        W_hoja, H_hoja = FORMATOS_IRAM[formato]
        es_rev = abs(bb.XLength - bb.YLength) <= 0.5
        piezas_meta[it_num] = (formato, es_rev)

        rotulo_p = dict(campos_base)
        rotulo_p.update(
            {
                "ESCALA": escala_txt,
                "FORMATO": f"IRAM {formato}",
                "HOJA": f"{num_hoja_actual}/{total_hojas}",
                "TITULO": f"{entrada['denominacion']} (#{it_num} x{len(entrada['instancias'])})",
                "MATERIAL": entrada["material"],
                "MASA": f"{masa_g:.1f} g",
                "TOL_GRAL": entrada.get("tol_gral", "FDM ±0,20 mm"),
                "NUM_PLANO": entrada["plano_original"],
            }
        )
        page_p, _ = _crear_pagina_iram(doc_planos, nombre_hoja, nombre_hoja, formato, rutas_plantillas, rotulo_p)

        if formato == "A4":
            x_vistas, x_der, ancho_tabla, max_h_tabla, max_esc_tabla = 86.0, 224.0, 108.0, 74.0, 0.82
        else:
            x_vistas, x_der, ancho_tabla, max_h_tabla, max_esc_tabla = 132.0, 322.0, 148.0, 138.0, 0.95

        svg_cuadro = generar_svg_bloque_cotas_pieza(filas_param, entrada["notas_taller"], ancho_mm=ancho_tabla)
        m_h_tbl = re.search(r'height="([\d.]+)mm"', svg_cuadro)
        H_raw_tabla = float(m_h_tbl.group(1)) if m_h_tbl else (14.0 + min(len(filas_param), 22) * 4.2)
        escala_tabla = round(min(max_esc_tabla, max_h_tabla / max(1.0, H_raw_tabla)), 3)

        H_tabla_real = H_raw_tabla * escala_tabla
        y_tabla = 65.0 + 0.5 * H_tabla_real

        y_iso_min = 65.0 + H_tabla_real + 14.0
        y_iso_max = H_hoja - 13.0
        y_iso = 0.5 * (y_iso_min + y_iso_max)
        h_iso_est = max(10.0, (bb.XLength + bb.YLength) * 0.41 + bb.ZLength * 0.82)
        escala_iso = round(escala_num * 0.70, 3)
        h_iso_disp = max(18.0, (y_iso_max - y_iso_min) - 12.0)
        if h_iso_est * escala_iso > h_iso_disp:
            escala_iso = round(max(0.10, h_iso_disp / h_iso_est), 3)

        h_planta = max(4.0, bb.YLength * escala_num)
        h_corte = max(4.0, bb.ZLength * escala_num)
        w_corte = max(4.0, bb.XLength * escala_num)
        rx_rotulo = (W_hoja - 10.0) - 175.0
        if (x_vistas + 0.5 * w_corte + 18.0) >= rx_rotulo:
            y_base_min = 64.0
        else:
            y_base_min = 14.0

        # Disposición ISO-E (Primer Diedro): Sección A-A ARRIBA, Planta ABAJO
        y_planta_min = y_base_min + 16.0 + 0.5 * h_planta
        y_corte_max = (H_hoja - 35.0) - 0.5 * h_corte
        gap_vistas = 34.0 if (h_corte + h_planta) < 170.0 else 28.0
        altura_stack = h_corte + gap_vistas + h_planta
        espacio_col = (y_corte_max + 0.5 * h_corte) - (y_planta_min - 0.5 * h_planta)
        holgura_vert = max(0.0, 0.5 * (espacio_col - altura_stack))
        y_planta = y_planta_min + holgura_vert
        y_corte = min(y_corte_max, y_planta + 0.5 * h_planta + gap_vistas + 0.5 * h_corte)

        v_sup = doc_planos.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Planta")
        page_p.addView(v_sup)
        v_sup.Source = [obj_p]
        v_sup.Direction = App.Vector(0, 0, 1)
        v_sup.XDirection = App.Vector(1, 0, 0)
        v_sup.ScaleType = "Custom"
        v_sup.Scale = escala_num
        v_sup.X = x_vistas
        v_sup.Y = y_planta
        v_sup.Caption = ""
        estilizar_vista_iram(v_sup, mostrar_ocultas=False, mostrar_centros=True)

        v_sec = doc_planos.addObject("TechDraw::DrawViewSection", f"VP_{it_num:02d}_Corte_AA")
        page_p.addView(v_sec)
        v_sec.BaseView = v_sup
        v_sec.Source = [obj_p]
        v_sec.Direction = App.Vector(0, -1, 0)
        v_sec.XDirection = App.Vector(1, 0, 0)
        v_sec.SectionNormal = App.Vector(0, -1, 0)
        v_sec.SectionDirection = "Up"
        v_sec.SectionOrigin = bb.Center
        v_sec.SectionSymbol = "A"
        v_sec.SectionLineStretch = 1.0
        v_sec.ScaleType = "Custom"
        v_sec.Scale = escala_num
        v_sec.X = x_vistas
        v_sec.Y = y_corte
        v_sec.Caption = ""
        v_sec.FuseBeforeCut = True
        v_sec.CutSurfaceDisplay = "PatHatch"
        if pat_file:
            v_sec.FileGeomPattern = pat_file
            v_sec.NameGeomPattern = "Diagonal4"
            v_sec.HatchScale = 2.0
        estilizar_vista_iram(v_sec, mostrar_ocultas=False, mostrar_centros=True)

        v_iso = doc_planos.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Iso")
        page_p.addView(v_iso)
        v_iso.Source = [obj_p]
        v_iso.Direction = App.Vector(1, -1, 1)
        v_iso.XDirection = App.Vector(1, 1, 0)
        v_iso.ScaleType = "Custom"
        v_iso.Scale = escala_iso
        v_iso.X = x_der
        v_iso.Y = y_iso
        v_iso.Caption = ""
        estilizar_vista_iram(v_iso, mostrar_ocultas=False, mostrar_centros=False)

        for nm_t, txt_t, xt, yt, sz in [
            (f"Txt_{it_num:02d}_Corte", [f"SECCIÓN A - A ({escala_txt})"], x_vistas, min(H_hoja - 11.5, y_corte + 0.5 * h_corte + 23.5), 3.5),
            (f"Txt_{it_num:02d}_Planta", [f"VISTA SUPERIOR ({escala_txt})"], x_vistas, max(y_base_min + 1.5, y_planta - 0.5 * h_planta - 11.5), 3.2),
            (f"Txt_{it_num:02d}_Iso", ["PERSPECTIVA ISOMÉTRICA"], x_der, min(H_hoja - 11.5, y_iso + 0.5 * h_iso_disp + 3.0), 3.2),
        ]:
            t_an = doc_planos.addObject("TechDraw::DrawViewAnnotation", nm_t)
            page_p.addView(t_an)
            t_an.Text = txt_t
            t_an.TextSize = sz
            t_an.X = xt
            t_an.Y = yt

        simb_cotas = doc_planos.addObject("TechDraw::DrawViewSymbol", f"VP_{it_num:02d}_Cuadro_Cotas")
        page_p.addView(simb_cotas)
        simb_cotas.Symbol = svg_cuadro
        simb_cotas.ScaleType = "Custom"
        simb_cotas.Scale = escala_tabla
        simb_cotas.X = x_der
        simb_cotas.Y = y_tabla

        num_hoja_actual += 1

    # 4. Recomputar vistas HLR antes de medir y acotar
    print(f"Calculando proyecciones HLR de las {total_hojas} láminas IRAM 3D...")
    doc_planos.recompute()

    # Alinear verticalmente V00a_Corte_AA con V00a_Frente según proyección HLR real
    try:
        ef = v_arm_frente.getVisibleEdges()
        ec = v_arm_corte.getVisibleEdges()
        if ef and ec:
            cy_f = 0.5 * (min(e.BoundBox.YMin for e in ef) + max(e.BoundBox.YMax for e in ef))
            cy_c = 0.5 * (min(e.BoundBox.YMin for e in ec) + max(e.BoundBox.YMax for e in ec))
            v_arm_corte.Y = float(v_arm_frente.Y.Value) + cy_f - cy_c
    except Exception:
        pass

    # Acotación geométrica automática ANTES de agregar ejes de simetría cosméticos
    # (así `getVisibleEdges()` no incluye líneas cosméticas como aristas acotables)
    total_cotas = 0
    c_00a = acotar_vista_perfil_o_corte_iram(
        doc_planos, page_00a, v_arm_frente, "Cota_00a", es_revolucion=False, formato="A2"
    )
    total_cotas += len(c_00a)
    agregar_ejes_simetria_iram(v_arm_frente, es_revolucion=False)
    agregar_ejes_simetria_iram(v_arm_corte, es_revolucion=False)

    for entrada in CATALOGO_ITEMS_BOM_3D:
        if entrada["es_comercial"]:
            continue
        it_num = entrada["item"]
        info = datos_piezas[it_num]
        fmt_i, es_rev = piezas_meta[it_num]
        page_p = doc_planos.getObject(entrada["hoja_plano"])
        v_sup = doc_planos.getObject(f"VP_{it_num:02d}_Planta")
        v_sec = doc_planos.getObject(f"VP_{it_num:02d}_Corte_AA")

        if v_sup:
            c_d = acotar_vista_circular_iram(doc_planos, page_p, v_sup, f"Cota_{it_num:02d}", max_diametros=3, formato=fmt_i)
            total_cotas += len(c_d)
            agregar_ejes_simetria_iram(v_sup, es_revolucion=es_rev)
        if v_sec:
            c_l = acotar_vista_perfil_o_corte_iram(doc_planos, page_p, v_sec, f"Cota_{it_num:02d}", es_revolucion=es_rev, formato=fmt_i)
            total_cotas += len(c_l)
            c_det = acotar_detalles_y_roscas_corte_iram(
                doc_planos, page_p, v_sec, f"Cota_{it_num:02d}", info["filas_param"], cotas_existentes=c_l, formato=fmt_i
            )
            total_cotas += len(c_det)
            agregar_ejes_simetria_iram(v_sec, es_revolucion=es_rev)

    doc_planos.recompute()
    doc_planos.saveAs(RUTA_SALIDA_FCSTD)
    print(f"Legajo 3D maestro guardado ({total_hojas} hojas, {total_cotas} cotas geométricas): {RUTA_SALIDA_FCSTD}")

    # 5. Guardar cada lámina individual liviana en `planos/hojas_3d/` (incluyendo Datos_Rotulo y Tabla_BOM_IRAM)
    os.makedirs(DIR_HOJAS_3D, exist_ok=True)
    paginas = [o for o in doc_planos.Objects if o.TypeId == "TechDraw::DrawPage"]
    for pag in paginas:
        d_ind = App.newDocument(pag.Name)
        d_ind.copyObject(pag, True)
        d_ind.copyObject(dr, False)
        d_ind.copyObject(tb, False)
        for obj_i in d_ind.Objects:
            if obj_i.isDerivedFrom("Part::Feature") and getattr(obj_i, "ViewObject", None):
                obj_i.ViewObject.Visibility = False
        d_ind.recompute()
        d_ind.saveAs(os.path.join(DIR_HOJAS_3D, f"{pag.Name}.FCStd"))
        App.closeDocument(d_ind.Name)
    print(f"Generadas {len(paginas)} hojas individuales livianas en: {DIR_HOJAS_3D}")

    # 6. Exportación opcional a PDF únicamente bajo EXPORTAR_PDF=1 (Regla 3.1)
    if os.environ.get("EXPORTAR_PDF") == "1":
        dir_pdf = os.path.join(DIR_PLANOS, "pdf_3d")
        os.makedirs(dir_pdf, exist_ok=True)
        import TechDrawGui
        for o in paginas:
            ruta_pdf = os.path.join(dir_pdf, f"{o.Name}.pdf")
            TechDrawGui.exportPageAsPdf(o, ruta_pdf)
            print("Exportado PDF:", ruta_pdf)

    if not App.GuiUp:
        App.closeDocument(doc_planos.Name)


if __name__ in ("__main__", "generar_planos_impresion_3d"):
    import traceback
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
