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

Genera 27 láminas IRAM (3 de conjunto + 24 de piezas individuales a escala 3D):
  - Hoja 1 (A2): Plano Nº 0a - Conjunto General Armado (Frente, Planta, Corte A-A e Isométrica)
  - Hoja 2 (A2): Plano Nº 0b - Ensamblaje Explosionado + 2 Subensamblajes
  - Hoja 3 (A3): Plano Nº 0c - Lista de Materiales IRAM 4508 (31 ítems / 48 un.)
  - Hojas 4..27 (A4/A3): Planos de detalle e impresión/mecanizado de las 24 piezas
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
    acotar_angulo_centrado_iram,
    acotar_detalles_y_roscas_corte_iram,
    acotar_diametro_exacto_iram,
    acotar_distancia_coords_iram,
    acotar_vista_circular_iram,
    acotar_vista_perfil_o_corte_iram,
    agregar_circulo_centros_iram,
    agregar_ejes_simetria_iram,
    agregar_llamada_lider_iram,
    agregar_marcas_plano_corte_iram,
    asegurar_plantillas_iram,
    buscar_arista_circulo_exacto,
    crear_circulo_rosca_34_iram,
    crear_cuadro_cotas_editable_iram,
    crear_rosca_cosmetica_vista_iram,
    crear_solido_corte_parcial_z,
    crear_vista_detalle_especifico_iram,
    crear_vista_detalle_roscas_iram,
    estimar_altura_cuadro_html_mm,
    estilizar_vista_iram,
    generar_svg_bloque_cotas_pieza,
    generar_svg_tabla_bom_iram,
    obtener_ruta_fcpat,
    obtener_ruta_hatch_iram,
    proyectar_a_2d_vista,
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
        "detalles": "Brida Ø120,80x22,65 mm; bolsillos sufr. guía Ø15,50x2,37; paso central Ø30,20",
        "notas_taller": [
            "Impresión 3D esc. 0,755 (PLA+/PETG): cara de asiento de vidrio plana sin pandeo.",
            "Bolsillos para sufrideras de guía ampliados a Ø15,50 mm (prof. 2,37 mm en X=±28,31).",
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
        "detalles": "Brida Ø15,10x2,27 mm; paso guía Ø7,95 mm; escalón +Z Ø8,90x1,15 p/ O-Ring #40; 4x Ø2,34 en PCD Ø11,32",
        "notas_taller": [
            "Cantidad total: 2 unidades idénticas (alojadas en bolsillos inferiores -Z de Tapa Interior 16b).",
            "Agujero central ampliado a Ø7,95 mm para paso sin roce de barra guía.",
            "Escalón superior (+Z) Ø8,90 × prof. 1,15 mm aloja O-Ring 6,0×1,5 mm (#40) contra bolsillo de #3.",
        ],
        "features_extra": [
            ("d_ext", "15.10 mm", "Diámetro exterior de sufridera"),
            ("h_total", "2.27 mm", "Espesor total"),
            ("aloj_oring", "Ø8.90 x 1.15 mm (+Z)", "Escalón superior para O-Ring guía 6,0×1,5 (#40)"),
            ("pcd_4x", "4x Ø2.34 @ PCD 11.32", "4 agujeros de fijación en DBC Ø11,32 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Sufridera_Guia_1B_3D", "Sufridera_Guia_2B_3D"],
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
        "detalles": "Pistón Ø75,72×15,10 mm; garganta O-Ring Ø69,60×5,20 mm; aloj. núcleo Ø22,65; 2× Ø10,57",
        "notas_taller": [
            "Torneado en Delrin POM-C a escala 0,755 para cilindro interior Ø76,00 ±0,20 mm.",
            "Garganta perimetral Ø69,60 mm, ancho 5,20 mm (Z=4,95 – 10,15) para O-Ring Ø68×4,00 NBR 70.",
            "2 alojamientos guía 2× Ø10,57 (DBC Ø56,62); 1 sensor Ø6,04 a 45°; 4 ciegos Ø1,86×6,04 (DBC Ø28,24).",
        ],
        "features_extra": [
            ("d_ext", "75.72 mm", "Diámetro exterior del émbolo (hacia Ø76 vidrio)"),
            ("d_fondo_oring", "69.60 mm", "Diámetro de fondo de ranura para O-Ring 68×4,00"),
            ("z_ranura", "4.95 - 10.15 mm", "Posición axial ranura O-Ring (ancho 5,20 mm)"),
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
        "detalles": "Brida Ø33,98 / cuello Ø21,75 × 18,72 mm; rosca trap. 90° p=3,00; 4× Ø3,24 + 3× Ø2,20 M2,5",
        "notas_taller": [
            "Rosca trap. 90° pasante p=3,00 (Ø fondo 11,40 / cresta 9,70); enroscar por abajo desde espiga Ø8,80 de #14.",
            "Cuello Ø21,75 mm (juego FDM en Ø22,65); brida 4× Ø3,24 cajeado Ø5,43×0,94; frente 3× Ø2,20×6,00 (120°).",
        ],
        "features_extra": [
            ("Brida exterior", "Ø33,98 × 3,78 mm", "Diámetro y espesor de brida de asiento"),
            ("Cuello cilíndrico", "Ø21,75 mm (Z=3,78..18,72)", "Ajuste deslizante libre FDM en émbolo Ø22,65"),
            ("Rosca trap. interna", "Trap. 90° p=3,00 (1 ent.)", "Ø fondo 11,40 / Ø menor 9,70; chaflán 1,20×45°"),
            ("Fijación a émbolo", "4× Ø3,24 + caj. Ø5,43×0,94", "Corona DBC Ø28,32 para M2,5"),
            ("Fijación frontal CE2", "3× Ø2,20 × 6,00 (DBC Ø15,86)", "Pre-taladro M2,5 a 90° / 210° / 330°"),
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
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Varilla Ø8,22 × 220,65 mm; espiga Ø6,71×22,65 (tope hombro Z=22,65) + rosca p=1,25×9,82",
        "notas_taller": [
            "Espiga Ø6,71×22,65 mm atraviesa tapa 16b (Ø7,00 real) y sufridera #6; el hombro Ø8,22 hace tope en Z=22,65.",
            "Cuerpo macizo Ø8,22×198,00 mm; rosca triangular p=1,25×9,82 (Ø núcl. 5,47) para tuerca 3D (#31).",
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
        "detalles": "Eje tubular Ø15,10 / Ø7,55 / Ø6,04 × 95,89 mm; aloj. int. Ø9,06×50,59; 2× pasador Ø3,02",
        "notas_taller": [
            "Tornear concéntrico en AISI 304/316L entre puntos. Chaflanar aristas 0,38×45°.",
            "Aloj. axial Ø9,06 × 50,59 mm desde boca tubo; 2× pasadores Ø3,02 a 10,95 y 44,93 mm de la boca (Z=84,94 y 50,96).",
        ],
        "features_extra": [
            ("Cuerpo tubular", "Ø15,10 × 60,41 mm (Z=35,48..95,89)", "Tramo exterior superior con taladros de pasador"),
            ("Tramo intermedio", "Ø7,55 × 24,15 mm (Z=11,33..35,48)", "Espiga escalonada de salida hacia motor"),
            ("Espiga acoplamiento", "Ø6,04 × 11,33 mm (Z=0..11,33)", "Extremo de acoplamiento al motor paso a paso"),
            ("Alojamiento axial int.", "Ø9,06 × 50,59 mm (Z=45,30..95,89)", "Cavidad receptora del vástago Ø9,06 de Transmisor B"),
            ("Pasadores transversales", "2× Ø3,02 mm", "A 10,95 mm (Z=84,94) y 44,93 mm (Z=50,96) de la boca"),
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
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Husillo trap. 90° p=3,00 (Ø10,50/Ø8,80 x 192,15); punta inf. Ø8,80x13,15 (Op. 2); pasador Ø3,45",
        "notas_taller": [
            "Imprimir verticalmente en PLA (altura capa 0,16 mm, >=5 perímetros en Z=0 – 15 mm) usando versión _Impresion.",
            "Opción 2: espiga inferior uniforme Ø8,80 mm (Z=179 – 192,15) para pasar Centro #8 por debajo sin interferencia.",
        ],
        "features_extra": [
            ("d_rosca_trap", "Ø10.50 / Ø8.80 mm", "Rosca trapezoidal 90° p=3,00 mm (cresta/núcleo)"),
            ("d_espigas", "Ø8.80 × 13,15 mm", "Espiga lisa inferior uniforme (= raíz rosca Opción 2)"),
            ("d_acople", "Ø6.49 / transv. Ø3.45", "Acople eje Transmisor B y pasador en Z=5,68 mm"),
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
            "En ensamblaje se rota +22,5° respecto a #17 para alejar la fijación de las escotaduras guía.",
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
        "detalles": "Brida Ø30,20 / nariz Ø13,59 x 9,82 mm; paso unificado Ø9,20 FDM (Op. 2); 4x Ø2,64",
        "notas_taller": [
            "Encastra en bolsillo de Tapa Exterior 16a (brida Ø30,60 / nariz Ø14,00).",
            "Opción 2: diámetro interior unificado a Ø9,20 mm (espiga Ø8,80 + holg. 0,40; repasar c/mecha Ø9,0-9,2 mm).",
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
        "detalles": "Cuerpo Ø43,03x12,46 mm; paso Ø30,28; despeje Ø15,60; 4x Ø2,40+caj.Ø4,10@45°; 4x ciego Ø1,85@22,5°",
        "notas_taller": [
            "Montaje derecho (+Z arriba): las cabezas Allen M2x14 quedan embutidas 1 mm en cajeados sup. a 45°.",
            "Cara +Z posee 4x ciegos piloto Ø1,85 × 6,50 mm a 22,5°/112,5° (PCD Ø37,00) para fijación de #15 con M2x8.",
            "Despeje semicircular para arandelas/tuercas de barras guía ampliado a Ø15,60 mm a X=±28,31 (pared 4,54 mm a pilotos).",
        ],
        "features_extra": [
            ("d_int", "30.28 mm", "Diámetro interior central"),
            ("pcd_45", "4x Ø2.40 + caj. Ø4.10x3.00 @ PCD 37.76", "4 pasantes cajeados a 45° (#17->#3 c/ M2x14)"),
            ("pcd_ortog", "4x Ø1.85 x 6.50 @ PCD 37.00 (22.5°)", "4 agujeros ciegos piloto M2 rotados 22,5° (desde #15)"),
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
        "detalles": "Tensor partido esc. 0,755: cuerpo Ø16,61×151,81 + espiga tri. R3,00×30 (L=181,81)",
        "notas_taller": [
            "4 unidades. Espiga triangular macho R3,00 mm × 30,00 mm (holgura -0,25 mm radial respecto a #22).",
            "Encastre en cavidad #22; extremo libre con agujero axial ciego Ø6,32 × 12,08 mm (tornillo M6 #33).",
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
        "detalles": "Tensor partido esc. 0,755: Ø18,12 / Ø16,61×14,35 × 139,09 mm; cavidad tri. R3,25×30 mm",
        "notas_taller": [
            "4 unidades. Cavidad triangular hembra R3,25 mm × 30,00 mm (juego +0,25 mm radial sobre R3,00 de #21).",
            "Extremo rebajado Ø16,61×14,35 mm con agujero axial ciego Ø6,32 × 12,08 mm (tornillo M6 #33).",
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
            "Montada en extremo superior (Z=+80,63 – +88,18) sobre los 4 Tensores Parte 1.",
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
        "archivo": "Piezas_Comerciales/Rulemanes/Rodamiento_SKF_609.FCStd",
        "denominacion": "Rodamiento Rígido de Bolas SKF 609",
        "plano_ref": "Comercial SKF",
        "material": "Acero SAE 1045 / 52100",
        "detalles": "Código comercial: SKF 609-2Z / DIN 625-1 (Ø9 x Ø24 x 7 mm)",
        "es_comercial": True,
        "instancias": ["Rodamiento_SKF_609"],
    },
    {
        "item": 25,
        "archivo": "Piezas_Comerciales/Retenes/Reten_10x22x7.FCStd",
        "denominacion": "Retén Radial de Eje 10x22x7",
        "plano_ref": "Comercial DIN 3760",
        "material": "Elastómero NBR / Viton",
        "detalles": "Código comercial: Retén DBH / SAV 10x22x7 — DIN 3760 Forma A",
        "es_comercial": True,
        "instancias": ["Reten_10x22x7"],
    },
    {
        "item": 26,
        "archivo": "Piezas_Comerciales/Orrings/ORing_75x3_55.FCStd",
        "denominacion": "O-Ring Estático Camisa Ø75x3,55",
        "plano_ref": "Comercial ISO 3601",
        "material": "Elastómero NBR / Viton",
        "detalles": "Código comercial: O-Ring DIN 3771 Ø75,0 x 3,55 mm (sello camisa vidrio)",
        "es_comercial": True,
        "instancias": ["ORing_Camisa_Int", "ORing_Camisa_Ext"],
    },
    {
        "item": 27,
        "archivo": "Piezas_Comerciales/Orrings/ORing_68x4_00.FCStd",
        "denominacion": "O-Ring Dinámico Émbolo Ø68×4,00",
        "plano_ref": "Comercial ISO 3601",
        "material": "Elastómero NBR 70 / Viton",
        "detalles": "Código comercial: O-Ring ISO 3601 / DIN 3771 Ø68,0 × 4,00 mm NBR 70 (ranura Ø69,60×5,20)",
        "es_comercial": True,
        "instancias": ["ORing_Embolo_3D"],
    },
    {
        "item": 28,
        "archivo": "Piezas_Comerciales/Orrings/ORing_11_2x1_8.FCStd",
        "denominacion": "O-Ring Estático de Eje Ø11,2x1,8",
        "plano_ref": "Comercial ISO 3601",
        "material": "Elastómero NBR / Viton",
        "detalles": "Código comercial: O-Ring DIN 3771 Ø11,2 x 1,80 mm (sello eje transmisor)",
        "es_comercial": True,
        "instancias": ["ORing_Eje_11_2x1_8"],
    },
    {
        "item": 29,
        "archivo": "Piezas_Comerciales/Pasadores/Pasador_3x14.FCStd",
        "denominacion": "Pasador Elástico Ø3x14 mm",
        "plano_ref": "Comercial ISO 8752",
        "material": "Acero SAE 1045",
        "detalles": "Código comercial: Espina elástica ISO 8752 / DIN 1481 — Ø3 x 14 mm",
        "es_comercial": True,
        "instancias": ["Pasador_3x14_1", "Pasador_3x14_2"],
    },
    {
        "item": 30,
        "archivo": "Piezas_Comerciales/Pasadores/Pasador_3x10.FCStd",
        "denominacion": "Pasador Elástico Ø3x10 mm",
        "plano_ref": "Comercial ISO 8752",
        "material": "Acero SAE 1045",
        "detalles": "Código comercial: Espina elástica ISO 8752 / DIN 1481 — Ø3 x 10 mm",
        "es_comercial": True,
        "instancias": ["Pasador_3x10_3"],
    },
    {
        "item": 31,
        "archivo": "Tuerca_Guia_08_3D.FCStd",
        "denominacion": "Tuerca Hexagonal Guía (Impresión 3D)",
        "plano_ref": "Plano Nº 8b-3D",
        "plano_original": "Plano Nº 8b-3D",
        "hoja_plano": "Plano_24_Tuerca_Guia_08_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Hexágono 13,00x6,00 mm; rosca triangular p=1,25 mm (holgura FDM 0,50 mm)",
        "notas_taller": [
            "Cantidad: 2 unidades. Rosca triangular p=1,25 mm hermanada con Guía 08 3D.",
            "Holgura FDM 0,50 mm radial (Ø fondo 7,71 mm en CAD -> ~7,16 mm impreso).",
        ],
        "features_extra": [
            ("s_hex", "13.00 mm", "Distancia entre caras del hexágono"),
            ("h_tuerca", "6.00 mm", "Altura total con biseles 0,60 mm"),
            ("rosca", "Triang. p=1.25 mm", "Ø fondo CAD 7,71 mm / cresta 6,47 mm"),
        ],
        "es_comercial": False,
        "instancias": ["Tuerca_Guia_1_08_3D", "Tuerca_Guia_2_08_3D"],
    },
    {
        "item": 32,
        "archivo": "Arandela_Guia_08_3D.FCStd",
        "denominacion": "Arandela Asiento Guía (Impresión 3D)",
        "plano_ref": "Plano Nº 8c-3D",
        "plano_original": "Plano Nº 8c-3D",
        "hoja_plano": "Plano_25_Arandela_Guia_08_3D",
        "material": "PLA+ / PETG Estructural",
        "tol_gral": "FDM ±0,20 mm",
        "detalles": "Arandela Ø13,59×Ø7,20×4,00 mm (Ø13,19×Ø7,60 FDM); asiento de Tuerca #31 en #3",
        "notas_taller": [
            "Cantidad: 2 unidades. Calza 1,74 mm en rebaje Ø13,59 (+Z) de Tapa 16b (#3) y sobresale 2,26 mm.",
            "Permite ajustar Tuerca Guía (#31) sin que sus vértices rocen ni dañen la tapa.",
        ],
        "features_extra": [
            ("d_ext", "13.59 mm (13.19 FDM)", "Diámetro exterior para rebaje Ø13,59 de #3"),
            ("d_int", "7.20 mm (7.60 FDM)", "Paso holgado para espiga de Guía #11"),
            ("h_total", "4.00 mm", "Espesor axial total (chaflanes 0,40×45°)"),
        ],
        "es_comercial": False,
        "instancias": ["Arandela_Guia_1_08_3D", "Arandela_Guia_2_08_3D"],
    },
    {
        "item": 33,
        "denominacion": "Tornillo / Espárrago Hex. M6 × 20 DIN 912/933",
        "plano_ref": "DIN 912 / ISO 4762",
        "material": "Acero Inox. A2-70",
        "detalles": "Fijación axial extremos de 4× Tensores (#21/#22, aloj. Ø6,32×12,08) c/ arandela",
        "es_buloneria": True,
        "cantidad": 8,
    },
    {
        "item": 34,
        "denominacion": "Tornillo Allen M4 × 25 DIN 912 (+ arandela)",
        "plano_ref": "DIN 912 / ISO 4762",
        "material": "Acero Inox. A2-70",
        "detalles": "Fijación de 2× Cierres Estructura (#20, Ø4,15) sobre Estructura Int. (#19, Ø3,12)",
        "es_buloneria": True,
        "cantidad": 8,
    },
    {
        "item": 35,
        "denominacion": "Tornillo Allen M4 × 16 DIN 912",
        "plano_ref": "DIN 912 / ISO 4762",
        "material": "Acero Inox. A2-70",
        "detalles": "Fijación motor en Tapa Motor Superior (#23, Ø4,15 pasante c/ cajeado Ø7,85)",
        "es_buloneria": True,
        "cantidad": 4,
    },
    {
        "item": 36,
        "denominacion": "Tornillo Avellanado M2 × 10 DIN 965",
        "plano_ref": "DIN 965 / ISO 7046",
        "material": "Acero Inox. A2-70",
        "detalles": "8× Anillos Tórica (#18→#1/#3, DBC Ø98,16) + 4× Tapa Sufridera Int. (#5→#4, DBC Ø28,32)",
        "es_buloneria": True,
        "cantidad": 12,
    },
    {
        "item": 37,
        "denominacion": "Tornillo Allen M2 × 5..8 / M2,5×6 DIN 912",
        "plano_ref": "DIN 912 / ISO 4762",
        "material": "Acero Inox. A2-70",
        "detalles": "8× M2×5 Sufr. Guía (#6→#3) + 4× M2,5×6 Sufr. Eje Ext. (#16→#1) + 4× M2×8 Adapt. Rod. (#15→#17)",
        "es_buloneria": True,
        "cantidad": 16,
    },
    {
        "item": 38,
        "denominacion": "Tornillo Allen M2 × 14 DIN 912",
        "plano_ref": "DIN 912 / ISO 4762",
        "material": "Acero Inox. A2-70",
        "detalles": "Fijación Adaptador de Eje (#17→#3, cajeado Ø4,10×3,00 a 45°, DBC Ø37,76)",
        "es_buloneria": True,
        "cantidad": 4,
    },
    {
        "item": 39,
        "denominacion": "Tornillo M2,5 (4× Allen ×10 + 3× Avell. ×8)",
        "plano_ref": "DIN 912 / DIN 965",
        "material": "Acero Inox. A2-70",
        "detalles": "4× Allen M2,5×10 CE1→Émbolo (#8→#7, Ø3,24) + 3× Avell. M2,5×8 CE2→CE1 (#9→#8)",
        "es_buloneria": True,
        "cantidad": 7,
    },
    {
        "item": 40,
        "archivo": "Piezas_Comerciales/Orrings/ORing_6_0x1_5.FCStd",
        "denominacion": "O-Ring Dinámico Guía Ø6,0×1,50",
        "plano_ref": "Comercial ISO 3601",
        "material": "Elastómero NBR 70 / Viton",
        "detalles": "Código comercial: O-Ring ISO 3601 / DIN 3771 Ø6,0 × 1,50 mm NBR 70 (en escalón Ø8,90 de #6)",
        "es_comercial": True,
        "instancias": ["ORing_Guia_1", "ORing_Guia_2"],
    },
]

RESUMEN_BULONERIA_ESTANDAR_3D = [
    "Todos los elementos roscados estándar se detallan en los ítems numerados #33 a #39 (acero inoxidable A2-70).",
    "En bridas impresas en PLA+/PETG sin inserto metálico (aloj. Ø1,86 / Ø2,20 / Ø3,12), realizar pre-roscado manual o tornillo autorroscante moderado.",
    "Torque recomendado en PLA+/PETG: M2 = 0,25 N·m | M2,5 = 0,45 N·m | M4 = 1,2 N·m | M6 = 2,5 N·m (usar arandela plana bajo cabeza Allen).",
    "Sellado y ajuste FDM: holgura radial base +0,20 mm en alojamientos; en guía Ø6,71 y tuerca #31 se calibró juego específico impreso.",
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
            if f < 7:
                continue
            try:
                simb = str(param_sp.get(f"A{f}")).strip()
            except Exception:
                continue
            if (
                not simb
                or simb.startswith("mej_")
                or simb in (
                    "ALIAS",
                    "SIMBOLO",
                    "modo_diseno",
                    "escala",
                    "esc",
                    "holgura",
                    "holgura_fdm",
                    "Modo de diseño",
                    "Escala",
                    "Holgura FDM",
                    "Escala efectiva",
                    "Holgura efectiva",
                )
            ):
                continue
            try:
                v_nom = param_sp.get(f"B{f}")
                if hasattr(v_nom, "Value"):
                    u_str = str(getattr(v_nom, "UserString", "")).lower()
                    num = float(v_nom.Value)
                    if "deg" in u_str or "°" in u_str:
                        val_txt = f"{num:.2f}°"
                    elif "mm" in u_str or "m" in u_str:
                        val_txt = f"{num:.2f} mm"
                    else:
                        val_txt = f"{num:.2f}"
                elif isinstance(v_nom, (int, float)):
                    val_txt = f"{float(v_nom):.2f} mm"
                else:
                    s_val = str(v_nom).strip()
                    val_txt = s_val if s_val else "-"
            except Exception:
                val_txt = "-"
            try:
                desc = str(param_sp.get(f"C{f}")).strip()
            except Exception:
                desc = ""
            if not desc or desc == val_txt or desc.startswith("=") or desc.upper() in ("NOMINAL", "VALOR EFECTIVO", "VALOR"):
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


def _proyectar_pt_vista(pt3d, centro_vista, direction=None, x_direction=None):
    """Proyecta un punto 3D al plano 2D sin escalar de una vista TechDraw."""
    rel = pt3d - centro_vista
    ux = (x_direction if x_direction is not None else App.Vector(1.0, 1.0, 0.0)).normalize()
    uz_dir = (direction if direction is not None else App.Vector(1.0, -1.0, 1.0)).normalize()
    uy = uz_dir.cross(ux).normalize()
    return rel.dot(ux), rel.dot(uy)


def _agregar_globo(
    doc_planos,
    page,
    vista,
    item_num,
    pt3d_centro,
    centro_vista,
    escala_vista,
    dx,
    dy,
    prefijo="",
    direction=None,
    x_direction=None,
    sufijo="",
):
    """Proyecta un punto 3D al sistema de `DrawViewBalloon` (coordenadas de la vista fuente)."""
    ox, oy = _proyectar_pt_vista(pt3d_centro, centro_vista, direction=direction, x_direction=x_direction)

    nombre_bal = f"Globo_{prefijo}_{item_num:02d}"
    if sufijo:
        nombre_bal += f"_{sufijo}"
    bal = doc_planos.addObject("TechDraw::DrawViewBalloon", nombre_bal)
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


def _distribuir_globos_en_columnas(
    doc_planos,
    page,
    vista,
    items_specs,
    centro_vista,
    escala_vista,
    x_col_izq,
    x_col_der,
    y_min_hoja,
    y_max_hoja,
    prefijo,
    direction=None,
    x_direction=None,
    paso_min_mm=9.5,
):
    """Coloca globos ordenados en columnas izquierda/derecha sin superposiciones ni cruces.

    items_specs: lista de tuplas (item_num, pt3d_anchor, lado ('L'|'R'), sufijo_opcional)
    """
    vx = float(vista.X.Value) if hasattr(vista.X, "Value") else float(vista.X)
    vy = float(vista.Y.Value) if hasattr(vista.Y, "Value") else float(vista.Y)

    for lado, x_target in (("L", x_col_izq), ("R", x_col_der)):
        grupo = []
        for spec in items_specs:
            if len(spec) == 3:
                it_num, pt3d, ld = spec
                suf = ""
            else:
                it_num, pt3d, ld, suf = spec
            if ld != lado or pt3d is None:
                continue
            ox, oy = _proyectar_pt_vista(pt3d, centro_vista, direction=direction, x_direction=x_direction)
            ax = vx + ox * escala_vista
            ay = vy + oy * escala_vista
            grupo.append([it_num, pt3d, ax, ay, ay, suf])

        if not grupo:
            continue

        # Orden ascendente en Y (de abajo hacia arriba) para mantener orden visual y cero cruces
        grupo.sort(key=lambda r: r[3])

        # Relajar espaciado vertical mínimo manteniendo las burbujas dentro de [y_min_hoja, y_max_hoja]
        n = len(grupo)
        span = max(0.0, y_max_hoja - y_min_hoja)
        paso = min(paso_min_mm, (span / max(1, n - 1)) if n > 1 else paso_min_mm)

        grupo[0][4] = max(y_min_hoja, min(y_max_hoja, grupo[0][3]))
        for i in range(1, n):
            grupo[i][4] = max(grupo[i][3], grupo[i - 1][4] + paso)
        if grupo[-1][4] > y_max_hoja:
            grupo[-1][4] = y_max_hoja
            for i in range(n - 2, -1, -1):
                grupo[i][4] = min(grupo[i][4], grupo[i + 1][4] - paso)
        if grupo[0][4] < y_min_hoja:
            grupo[0][4] = y_min_hoja
            for i in range(1, n):
                grupo[i][4] = max(grupo[i][4], grupo[i - 1][4] + paso)

        for it_num, pt3d, ax, _ay, ty, suf in grupo:
            dx = x_target - ax
            dy = ty - _ay
            _agregar_globo(
                doc_planos,
                page,
                vista,
                it_num,
                pt3d,
                centro_vista,
                escala_vista,
                dx,
                dy,
                prefijo=prefijo,
                direction=direction,
                x_direction=x_direction,
                sufijo=suf,
            )


def _agregar_linea_trayectoria_3d(
    vista,
    pt3d_a,
    pt3d_b,
    centro_vista,
    direction=None,
    x_direction=None,
    estilo=2,
    grosor=0.22,
    color=(0.12, 0.34, 0.70, 1.0),
):
    """Dibuja una línea cosmética de trayectoria de ensamblaje entre dos puntos 3D."""
    x1, y1 = _proyectar_pt_vista(pt3d_a, centro_vista, direction=direction, x_direction=x_direction)
    x2, y2 = _proyectar_pt_vista(pt3d_b, centro_vista, direction=direction, x_direction=x_direction)
    try:
        vista.makeCosmeticLine(
            App.Vector(x1, y1, 0.0), App.Vector(x2, y2, 0.0), int(estilo), float(grosor), color
        )
    except Exception:
        pass


def _generar_svg_recuadro_subensamblaje(titulo, subt, ancho_mm, alto_mm):
    W, H = ancho_mm, alto_mm
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">
  <rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{H - 1.0:.1f}" fill="none" stroke="#000000" stroke-width="0.45"/>
  <rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="8.0" fill="#eef3f8" stroke="#000000" stroke-width="0.45"/>
  <text x="4.0" y="5.6" font-family="Liberation Sans, Arial, sans-serif" font-size="3.1" font-weight="bold">{titulo}</text>
  <text x="{W - 4.0:.1f}" y="5.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.7" text-anchor="end">{subt}</text>
</svg>"""


def _generar_svg_guia_armado_00b(ancho_mm, alto_mm):
    W, H = ancho_mm, alto_mm
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">
  <rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{H - 1.0:.1f}" fill="#ffffff" stroke="#000000" stroke-width="0.5"/>
  <rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="8.5" fill="#1d3557" stroke="#000000" stroke-width="0.5"/>
  <text x="4.0" y="6.1" font-family="Liberation Sans, Arial, sans-serif" font-size="3.2" font-weight="bold" fill="#ffffff">GUÍA DE MONTAJE Y REFERENCIAS CRUZADAS</text>

  <text x="4.0" y="14.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.9" font-weight="bold" fill="#1d3557">1. SUBCONJUNTOS DEL LEGAJO</text>
  <text x="5.0" y="19.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.5">• <tspan font-weight="bold">General (Izq.):</tspan> Carcasa (#1, #2, #3, #19, #20, #23) y tensores (#21, #22).</text>
  <text x="5.0" y="24.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.5">• <tspan font-weight="bold">Detalle A (Arr.):</tspan> Émbolo móvil (#7, #8, #9, #10 x2) + O-ring (#27).</text>
  <text x="5.0" y="28.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.5">• <tspan font-weight="bold">Detalle B (Abj.):</tspan> Cadena rotativa completa (#12..#16, #29, #30).</text>
  <rect x="3.5" y="31.5" width="{W - 7.0:.1f}" height="12.5" fill="#fff4e5" stroke="#c75000" stroke-width="0.4"/>
  <text x="5.5" y="36.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.7" font-weight="bold" fill="#9a3412">VER DETALLE AMPLIADO EN PLANO Nº 0d-3D (Hoja 4):</text>
  <text x="5.5" y="40.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.45" fill="#111111">Tapa Interior (#3), SKF 609 (#24), Retén (#25), Sufr. Guía (#6 x2), Arand. (#32 x2).</text>

  <line x1="3.5" y1="47.5" x2="{W - 3.5:.1f}" y2="47.5" stroke="#cccccc" stroke-width="0.35"/>
  <text x="4.0" y="53.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.9" font-weight="bold" fill="#1d3557">2. ADVERTENCIAS ANTI-ERROR EN TAPA INTERIOR (#3)</text>
  <text x="5.0" y="58.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.45"><tspan font-weight="bold" fill="#b91c1c">A.</tspan> Sufridera Int. (#4), Retén (#25) y Tapa (#5) entran en #3 SOLO desde</text>
  <text x="9.0" y="62.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.45"><tspan font-weight="bold">ABAJO (-Z, lado cámara)</tspan>. El labio del retén mira hacia la cámara (-Z).</text>
  <text x="5.0" y="67.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.45"><tspan font-weight="bold" fill="#b91c1c">B.</tspan> Rulemán SKF 609 (#24) calza desde <tspan font-weight="bold">ABAJO (-Z)</tspan> en Adaptador (#15).</text>
  <text x="5.0" y="72.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.45"><tspan font-weight="bold" fill="#b91c1c">C.</tspan> Desfase angular: #17→#3 a <tspan font-weight="bold">45°</tspan>; #15→#17 a <tspan font-weight="bold">22,5°</tspan>.</text>
  <text x="5.0" y="77.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.45"><tspan font-weight="bold" fill="#b91c1c">D.</tspan> 2x Sufridera Guía (#6) van abajo (-Z) y 2x Arandela (#32) arriba (+Z) en #3.</text>
  <text x="9.0" y="81.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.45">Tuercas (#31) roscan arriba (+Z) sobre Arandelas (#32); hombro de #11 abajo.</text>

  <line x1="3.5" y1="85.0" x2="{W - 3.5:.1f}" y2="85.0" stroke="#cccccc" stroke-width="0.35"/>
  <text x="4.0" y="90.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.9" font-weight="bold" fill="#1d3557">3. MAPA COMPLETO DE JUNTAS Y O-RINGS (6 U. + 1 RETÉN)</text>
  <rect x="3.5" y="92.8" width="{W - 7.0:.1f}" height="6.0" fill="#eef3f8" stroke="#64748b" stroke-width="0.3"/>
  <text x="5.5" y="96.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">Ítem</text>
  <text x="16.0" y="96.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">Elemento / Medida</text>
  <text x="72.0" y="96.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">Cant.</text>
  <text x="84.0" y="96.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">Ubicación Exacta en Bomba</text>

  <text x="5.5" y="103.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">#26</text>
  <text x="16.0" y="103.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">O-Ring 75 × 3,55 mm</text>
  <text x="74.0" y="103.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">2</text>
  <text x="84.0" y="103.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">Extremos camisa (#2) en #3 y #1</text>

  <text x="5.5" y="108.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">#27</text>
  <text x="16.0" y="108.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">O-Ring 68 × 4,00 mm</text>
  <text x="74.0" y="108.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">1</text>
  <text x="84.0" y="108.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">Ranura periférica Émbolo (#7)</text>

  <text x="5.5" y="113.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">#28</text>
  <text x="16.0" y="113.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">O-Ring 11,2 × 1,8 mm</text>
  <text x="74.0" y="113.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">1</text>
  <text x="84.0" y="113.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">Cuello Ø9,82 Transm. B (#13) / #15</text>

  <text x="5.5" y="118.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">#40</text>
  <text x="16.0" y="118.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">O-Ring 6,0 × 1,50 mm</text>
  <text x="74.0" y="118.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">2</text>
  <text x="84.0" y="118.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">Guías #11 entre bolsillo #3 y #6</text>

  <text x="5.5" y="123.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">#25</text>
  <text x="16.0" y="123.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">Retén 10 × 22 × 7 mm</text>
  <text x="74.0" y="123.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">1</text>
  <text x="84.0" y="123.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">Aloj. Ø22,40 en #4 (labio a -Z)</text>

  <text x="5.5" y="128.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">#18</text>
  <text x="16.0" y="128.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">Anillo Tórica 13 (3D)</text>
  <text x="74.0" y="128.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">2</text>
  <text x="84.0" y="128.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">Prensor de O-Rings #26 (#3 y #1)</text>

  <line x1="3.5" y1="133.5" x2="{W - 3.5:.1f}" y2="133.5" stroke="#cccccc" stroke-width="0.35"/>
  <text x="4.0" y="139.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.55" font-weight="bold" fill="#1d3557">4. SENTIDO DE PROYECCIÓN</text>
  <text x="5.0" y="144.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">• <tspan font-weight="bold">+Z (Arriba):</tspan> Lado seco / acoplamiento a motor eléctrico.</text>
  <text x="5.0" y="148.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">• <tspan font-weight="bold">-Z (Abajo):</tspan> Lado cámara húmeda, camisa (#2) y tapa exterior (#1).</text>
  <text x="5.0" y="152.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2" fill="#475569">Líneas azules segmentadas: ejes coaxiales de inserción real.</text>
</svg>"""


def _generar_svg_secuencia_tapa_int_00d(ancho_mm, alto_mm):
    W, H = ancho_mm, alto_mm
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">
  <rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="{H - 1.0:.1f}" fill="#ffffff" stroke="#000000" stroke-width="0.5"/>
  <rect x="0.5" y="0.5" width="{W - 1.0:.1f}" height="8.5" fill="#1d3557" stroke="#000000" stroke-width="0.5"/>
  <text x="4.0" y="6.0" font-family="Liberation Sans, Arial, sans-serif" font-size="3.1" font-weight="bold" fill="#ffffff">SECUENCIA DE ARMADO Y SELLOS — TAPA INTERIOR (#3)</text>

  <text x="4.0" y="14.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.8" font-weight="bold" fill="#1d3557">A. ORDEN DE ARMADO SIN CONFLICTOS (PASOS 1 A 7)</text>

  <text x="4.5" y="20.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold" fill="#1d3557">PASO 1 (Guías inf. -Z):</tspan> Alojar <tspan font-weight="bold">2x O-Ring #40 (6×1,5)</tspan> y <tspan font-weight="bold">2x Sufridera #6</tspan> en bolsillos</text>
  <text x="8.0" y="23.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">Ø15,50 de Tapa Int. (#3) en X=±28,31; fijar c/ 4x M2×5 (PCD Ø11,32).</text>
  <text x="8.0" y="27.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">Pasar c/ Guía #11 desde -Z hasta hacer tope su hombro Ø8,22→Ø6,71.</text>

  <text x="4.5" y="33.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold" fill="#1d3557">PASO 2 (Guías sup. +Z):</tspan> Colocar <tspan font-weight="bold">2x Arandela Guía #32</tspan> en rebajes</text>
  <text x="8.0" y="36.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">Ø13,59 (+Z) de #3 y roscar <tspan font-weight="bold">Tuercas Guía #31</tspan> en +Z hasta ajustar.</text>
  <text x="8.0" y="40.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" fill="#9a3412">(Apoyo elevado sobre #32; #31 queda alojada en escotaduras Ø15,6 de #17).</text>

  <text x="4.5" y="46.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold" fill="#1d3557">PASO 3 (Sello central -Z):</tspan> Desde <tspan font-weight="bold">ABAJO (-Z)</tspan>, insertar <tspan font-weight="bold">Sufridera #4</tspan> en</text>
  <text x="8.0" y="50.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">cavidad Ø34,05 de #3; luego <tspan font-weight="bold">Retén #25 (10×22×7)</tspan> con el labio hacia</text>
  <text x="8.0" y="53.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">cámara (-Z) y cerrar con <tspan font-weight="bold">Tapa Sufridera #5</tspan> (4x torn. PCD Ø28,32).</text>

  <text x="4.5" y="59.4" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold" fill="#1d3557">PASO 4 (Rulemán en #15):</tspan> Prensar <tspan font-weight="bold">SKF 609 (#24)</tspan> desde <tspan font-weight="bold">ABAJO (-Z)</tspan></text>
  <text x="8.0" y="63.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">en cavidad Ø24,40 de <tspan font-weight="bold">Adaptador Rodamiento #15</tspan> hasta hacer tope.</text>

  <text x="4.5" y="68.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold" fill="#1d3557">PASO 5 (Eje B y O-Ring):</tspan> Pasar <tspan font-weight="bold">Transmisor B #13</tspan> desde -Z hacia +Z.</text>
  <text x="8.0" y="72.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">Colocar <tspan font-weight="bold">O-Ring 11,2×1,8 #28</tspan> en cuello Ø9,82 (arriba del SKF 609 #24).</text>

  <text x="4.5" y="78.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold" fill="#1d3557">PASO 6 (Bridas +Z):</tspan> Fijar <tspan font-weight="bold">Adaptador Eje #17 (+Z arriba)</tspan> a #3 c/ 4× M2×14 a <tspan font-weight="bold">45°</tspan>.</text>
  <text x="8.0" y="82.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">Luego fijar conjunto <tspan font-weight="bold">#15+#24</tspan> sobre #17 c/ 4× M2×8 a <tspan font-weight="bold">22,5°</tspan>.</text>

  <text x="4.5" y="87.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold" fill="#1d3557">PASO 7 (Cierre y Camisa):</tspan> Montar <tspan font-weight="bold">Est. Int. #19</tspan> y <tspan font-weight="bold">Cierre #20</tspan> en +Z.</text>
  <text x="8.0" y="91.4" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4">En -Z: asentar <tspan font-weight="bold">O-Ring 75×3,55 #26</tspan> + <tspan font-weight="bold">Anillo #18</tspan> e insertar <tspan font-weight="bold">Camisa #2</tspan>.</text>

  <rect x="3.5" y="96.5" width="{W - 7.0:.1f}" height="43.5" fill="#fef2f2" stroke="#b91c1c" stroke-width="0.45"/>
  <rect x="3.5" y="96.5" width="{W - 7.0:.1f}" height="6.8" fill="#b91c1c" stroke="#b91c1c" stroke-width="0.45"/>
  <text x="6.0" y="101.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.65" font-weight="bold" fill="#ffffff">B. CHEQUEOS CRÍTICOS ANTI-ERROR ANTES DE CERRAR</text>
  <text x="5.5" y="108.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold">1. NO invertir #4/#25/#5:</tspan> #3 tiene escalón Ø30,20 arriba; solo entran desde -Z.</text>
  <text x="5.5" y="114.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold">2. NO forzar #24 por arriba:</tspan> #15 tiene agujero sup. Ø15,60; SKF 609 entra por -Z.</text>
  <text x="5.5" y="119.9" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold">3. Escotaduras de #17:</tspan> Alinear las dos muescas Ø15,6 sobre X=±28,31 (#31).</text>
  <text x="5.5" y="125.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold">4. Desfase 22,5° de bridas:</tspan> #17→#3 (PCD Ø37,8 a 45°) ≠ #15→#17 (PCD Ø37,0 a 22,5°).</text>
  <text x="5.5" y="131.3" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold">5. Sentido de Guía #11:</tspan> Rosca p=1,25 hacia +Z (#31). Extremo liso hacia cámara -Z.</text>
  <text x="5.5" y="137.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.4"><tspan font-weight="bold">6. Sensor y #19:</tspan> Bolsillo cable sensor a +45° libre entre nervios estructurales.</text>

  <text x="4.0" y="148.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.8" font-weight="bold" fill="#1d3557">C. MAPA DE TODOS LOS SELLOS Y O-RINGS</text>
  <rect x="3.5" y="151.0" width="{W - 7.0:.1f}" height="6.2" fill="#eef3f8" stroke="#64748b" stroke-width="0.3"/>
  <text x="5.5" y="155.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">Ítem</text>
  <text x="15.5" y="155.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">Denominación</text>
  <text x="65.0" y="155.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">Cant.</text>
  <text x="76.0" y="155.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35" font-weight="bold">Asiento y Lado</text>

  <text x="5.5" y="161.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">#25</text>
  <text x="15.5" y="161.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">Retén 10×22×7</text>
  <text x="67.0" y="161.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">1</text>
  <text x="76.0" y="161.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">Dentro de #4 (-Z, sello eje #13)</text>

  <text x="5.5" y="166.4" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">#28</text>
  <text x="15.5" y="166.4" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">O-Ring 11,2×1,8</text>
  <text x="67.0" y="166.4" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">1</text>
  <text x="76.0" y="166.4" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">Cuello #13 dentro de #15 (+Z)</text>

  <text x="5.5" y="171.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">#40</text>
  <text x="15.5" y="171.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">O-Ring 6,0×1,5</text>
  <text x="67.0" y="171.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">2</text>
  <text x="76.0" y="171.6" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">Bolsillo #3 / #6 (+Z, guías #11)</text>

  <text x="5.5" y="176.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">#26</text>
  <text x="15.5" y="176.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">O-Ring 75×3,55</text>
  <text x="67.0" y="176.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">2</text>
  <text x="76.0" y="176.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">Camisa #2 / #3 (-Z) y #1 (ext.)</text>

  <text x="5.5" y="182.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">#18</text>
  <text x="15.5" y="182.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">Anillo Tórica 13</text>
  <text x="67.0" y="182.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">2</text>
  <text x="76.0" y="182.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">Prensor de #26 (4x torn. R=49,1)</text>

  <text x="5.5" y="187.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3" font-weight="bold">#27</text>
  <text x="15.5" y="187.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">O-Ring 68×4,00</text>
  <text x="67.0" y="187.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">1</text>
  <text x="76.0" y="187.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.3">Pistón móvil Émbolo #7 (cámara)</text>

  <line x1="3.5" y1="191.5" x2="{W - 3.5:.1f}" y2="191.5" stroke="#cccccc" stroke-width="0.35"/>
  <text x="4.0" y="197.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.65" font-weight="bold" fill="#1d3557">D. CONVENCIÓN DE VISTAS EN ESTA LÁMINA</text>
  <text x="5.0" y="203.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">• <tspan font-weight="bold">Vista A (Izq.):</tspan> Explosión isométrica completa a escala 1:2.</text>
  <text x="5.0" y="207.8" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">• <tspan font-weight="bold">Vista B (Centro):</tspan> Corte longitudinal A-A (Y=0) mostrando cavidades</text>
  <text x="8.0" y="212.2" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">internas Ø34,05, Ø24,40, Ø15,50, hombros y labios.</text>
  <text x="5.0" y="217.0" font-family="Liberation Sans, Arial, sans-serif" font-size="2.35">• <tspan font-weight="bold">Vista C (Arr. Der.):</tspan> Planta +Z con desfase angular de bridas.</text>
  <text x="5.0" y="222.5" font-family="Liberation Sans, Arial, sans-serif" font-size="2.2" fill="#475569">Nota: Cilindro (#2) y Guías (#11) mostrados en tramo superior funcional.</text>
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

    # 1. Leer ensamblaje 3D para extraer placements exactos de cada una de las 48 instancias catalogadas
    instancias_catalogo = {
        ins for e in CATALOGO_ITEMS_BOM_3D for ins in e.get("instancias", [])
    }
    doc_assy = App.openDocument(RUTA_ENSAMBLAJE_3D)
    doc_assy.recompute()
    shapes_ens = {}
    for o in doc_assy.Objects:
        if o.TypeId == "App::Link" and getattr(o, "LinkedObject", None) and o.Name in instancias_catalogo:
            sh = o.Shape.copy() if (hasattr(o, "Shape") and not o.Shape.isNull()) else None
            if sh is None or not getattr(sh, "Solids", None):
                lo = o.LinkedObject
                grp = getattr(lo, "Group", []) or getattr(lo.Document, "Objects", [])
                sols = [
                    g for g in grp
                    if g.isDerivedFrom("Part::Feature")
                    and not g.isDerivedFrom("Part::Datum")
                    and not g.Shape.isNull()
                    and g.Shape.Solids
                ]
                if sols:
                    fins = [g for g in sols if not any(p.isDerivedFrom("Part::Feature") for p in g.InList)]
                    elegido = fins[-1] if fins else max(sols, key=lambda g: g.Shape.Volume)
                    sh = elegido.Shape.copy()
                    pl_tot = o.Placement.multiply(getattr(lo, "Placement", App.Placement()))
                    sh.transformShape(pl_tot.toMatrix())
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
        if entrada.get("es_buloneria"):
            cant = int(entrada.get("cantidad", 0))
            items_bom_completos.append(
                {
                    "item": it_num,
                    "cantidad": cant,
                    "denominacion": entrada["denominacion"],
                    "plano_ref": entrada["plano_ref"],
                    "material": entrada["material"],
                    "detalles": entrada["detalles"],
                    "masa_g": 0.0,
                    "es_comercial": True,
                    "es_buloneria": True,
                }
            )
            continue

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
    total_hojas = 4 + sum(
        1 for e in CATALOGO_ITEMS_BOM_3D if not e.get("es_comercial") and not e.get("es_buloneria")
    )  # 4 + 24 = 28

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

    x_col_00a = 100.0
    v_arm_planta = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Planta")
    page_00a.addView(v_arm_planta)
    v_arm_planta.Source = [obj_ens]
    v_arm_planta.Direction = App.Vector(0, 0, 1)
    v_arm_planta.XDirection = App.Vector(1, 0, 0)
    v_arm_planta.ScaleType = "Custom"
    v_arm_planta.Scale = 0.5
    v_arm_planta.X = x_col_00a
    v_arm_planta.Y = 74.0
    v_arm_planta.Caption = ""
    estilizar_vista_iram(v_arm_planta, mostrar_ocultas=False, mostrar_centros=True)

    v_arm_frente = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Frente")
    page_00a.addView(v_arm_frente)
    v_arm_frente.Source = [obj_ens]
    v_arm_frente.Direction = App.Vector(0, -1, 0)
    v_arm_frente.XDirection = App.Vector(1, 0, 0)
    v_arm_frente.ScaleType = "Custom"
    v_arm_frente.Scale = 0.5
    v_arm_frente.X = x_col_00a
    v_arm_frente.Y = 248.0
    v_arm_frente.Caption = ""
    estilizar_vista_iram(v_arm_frente, mostrar_ocultas=False, mostrar_centros=True)

    # Clasificación IRAM 4507 para Corte A-A: rayado alternado +45° / -45° en carcasas y sellos;
    # piezas macizas (guías, ejes transmisores, tornillo sin fin, sensores, pasadores, rodamiento) SIN rayado.
    PARTES_GRUPO_B_00A = (
        "Cilindro_09_3D", "Estructura_Interior_", "Tapa_Sufridera_Int_",
        "Adaptador_Rodamiento_", "Centro_Embolo_1_", "Reten_", "ORing_",
        "Tuerca_Guia_", "Tensor_",
    )
    PARTES_MACIZAS_EJES_00A = (
        "Guia_", "Tornillo_Sin_Fin_", "Transmisor_A_", "Transmisor_B_",
        "Sensor_Piston_", "Pasador_",
    )
    shs_00a_a, shs_00a_b, shs_00a_rod, shs_00a_ejes = [], [], [], []
    for nm_ins, sh_ins in shapes_ens.items():
        if nm_ins.startswith("Rodamiento_"):
            shs_00a_rod.append(sh_ins)
        elif nm_ins.startswith(PARTES_MACIZAS_EJES_00A):
            shs_00a_ejes.append(sh_ins)
        elif nm_ins.startswith(PARTES_GRUPO_B_00A):
            shs_00a_b.append(sh_ins)
        else:
            shs_00a_a.append(sh_ins)

    def _crear_subcomp_00a(nombre_obj, lista_sh):
        o = doc_planos.addObject("Part::Feature", nombre_obj)
        o.Shape = Part.makeCompound(lista_sh)
        if getattr(o, "ViewObject", None):
            o.ViewObject.Visibility = False
        grupo_fuentes.addObject(o)
        return o

    obj_ens_a = _crear_subcomp_00a("Ensamblaje_00a_GrupoA", shs_00a_a)
    obj_ens_b = _crear_subcomp_00a("Ensamblaje_00a_GrupoB", shs_00a_b)
    obj_ens_rod = _crear_subcomp_00a("Ensamblaje_00a_Rodam", shs_00a_rod)
    obj_ens_ejes = _crear_subcomp_00a("Ensamblaje_00a_EjesMacizos", shs_00a_ejes)

    x_corte_00a = 292.0
    vp_dummy_a = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Dummy_BaseA")
    vp_dummy_a.Source = [obj_ens_a]
    vp_dummy_a.Direction = App.Vector(0, 0, 1)
    vp_dummy_a.XDirection = App.Vector(1, 0, 0)
    v_arm_corte = doc_planos.addObject("TechDraw::DrawViewSection", "V00a_Corte_AA")
    page_00a.addView(v_arm_corte)
    v_arm_corte.BaseView = vp_dummy_a
    v_arm_corte.Source = [obj_ens_a]
    v_arm_corte.Direction = App.Vector(0, -1, 0)
    v_arm_corte.XDirection = App.Vector(1, 0, 0)
    v_arm_corte.SectionNormal = App.Vector(0, -1, 0)
    v_arm_corte.SectionDirection = "Up"
    v_arm_corte.SectionOrigin = App.Vector(bb_ens.Center.x, bb_ens.Center.y, obj_ens_a.Shape.BoundBox.Center.z)
    v_arm_corte.SectionSymbol = "A"
    v_arm_corte.SectionLineStretch = 1.0
    v_arm_corte.FuseBeforeCut = False
    v_arm_corte.CutSurfaceDisplay = "SvgHatch"
    hatch_45l = obtener_ruta_hatch_iram("45L")
    if hatch_45l:
        v_arm_corte.FileHatchPattern = hatch_45l
    v_arm_corte.HatchScale = 2.0
    v_arm_corte.ScaleType = "Custom"
    v_arm_corte.Scale = 0.5
    v_arm_corte.X = x_corte_00a
    v_arm_corte.Y = 248.0
    v_arm_corte.Caption = ""
    estilizar_vista_iram(v_arm_corte, mostrar_ocultas=False, mostrar_centros=True)

    # Capas auxiliares del Corte A-A usando vistas base fuera de página para no duplicar línea A-A
    vp_dummy_b = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Dummy_BaseB")
    vp_dummy_b.Source = [obj_ens_b]
    vp_dummy_b.Direction = App.Vector(0, 0, 1)
    vp_dummy_b.XDirection = App.Vector(1, 0, 0)
    v_arm_corte_b = doc_planos.addObject("TechDraw::DrawViewSection", "V00a_Corte_AA_GrupoB")
    page_00a.addView(v_arm_corte_b)
    v_arm_corte_b.BaseView = vp_dummy_b
    v_arm_corte_b.Source = [obj_ens_b]
    v_arm_corte_b.Direction = App.Vector(0, -1, 0)
    v_arm_corte_b.XDirection = App.Vector(1, 0, 0)
    v_arm_corte_b.SectionNormal = App.Vector(0, -1, 0)
    v_arm_corte_b.SectionOrigin = App.Vector(bb_ens.Center.x, bb_ens.Center.y, obj_ens_b.Shape.BoundBox.Center.z)
    v_arm_corte_b.FuseBeforeCut = False
    v_arm_corte_b.CutSurfaceDisplay = "SvgHatch"
    hatch_45r = obtener_ruta_hatch_iram("45R")
    if hatch_45r:
        v_arm_corte_b.FileHatchPattern = hatch_45r
    v_arm_corte_b.HatchScale = 1.45
    v_arm_corte_b.ScaleType = "Custom"
    v_arm_corte_b.Scale = 0.5
    v_arm_corte_b.X = x_corte_00a
    v_arm_corte_b.Y = 248.0
    v_arm_corte_b.Caption = ""
    estilizar_vista_iram(v_arm_corte_b, mostrar_ocultas=False, mostrar_centros=False)

    vp_dummy_rod = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Dummy_BaseRod")
    vp_dummy_rod.Source = [obj_ens_rod]
    vp_dummy_rod.Direction = App.Vector(0, 0, 1)
    vp_dummy_rod.XDirection = App.Vector(1, 0, 0)
    v_arm_corte_rod = doc_planos.addObject("TechDraw::DrawViewSection", "V00a_Corte_AA_Rodam")
    page_00a.addView(v_arm_corte_rod)
    v_arm_corte_rod.BaseView = vp_dummy_rod
    v_arm_corte_rod.Source = [obj_ens_rod]
    v_arm_corte_rod.Direction = App.Vector(0, -1, 0)
    v_arm_corte_rod.XDirection = App.Vector(1, 0, 0)
    v_arm_corte_rod.SectionNormal = App.Vector(0, -1, 0)
    v_arm_corte_rod.SectionOrigin = App.Vector(bb_ens.Center.x, bb_ens.Center.y, obj_ens_rod.Shape.BoundBox.Center.z)
    v_arm_corte_rod.FuseBeforeCut = False
    v_arm_corte_rod.CutSurfaceDisplay = "Hide"
    v_arm_corte_rod.ScaleType = "Custom"
    v_arm_corte_rod.Scale = 0.5
    v_arm_corte_rod.X = x_corte_00a
    v_arm_corte_rod.Y = 248.0
    v_arm_corte_rod.Caption = ""
    estilizar_vista_iram(v_arm_corte_rod, mostrar_ocultas=False, mostrar_centros=False)

    v_arm_corte_ejes = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Corte_AA_Ejes")
    page_00a.addView(v_arm_corte_ejes)
    v_arm_corte_ejes.Source = [obj_ens_ejes]
    v_arm_corte_ejes.Direction = App.Vector(0, -1, 0)
    v_arm_corte_ejes.XDirection = App.Vector(1, 0, 0)
    v_arm_corte_ejes.ScaleType = "Custom"
    v_arm_corte_ejes.Scale = 0.5
    v_arm_corte_ejes.X = x_corte_00a
    v_arm_corte_ejes.Y = 248.0
    v_arm_corte_ejes.Caption = ""
    estilizar_vista_iram(v_arm_corte_ejes, mostrar_ocultas=False, mostrar_centros=False)

    v_arm_iso = doc_planos.addObject("TechDraw::DrawViewPart", "V00a_Isometrica")
    page_00a.addView(v_arm_iso)
    v_arm_iso.Source = [obj_ens]
    v_arm_iso.Direction = App.Vector(1, -1, 1)
    v_arm_iso.XDirection = App.Vector(1, 1, 0)
    v_arm_iso.ScaleType = "Custom"
    v_arm_iso.Scale = 0.42
    v_arm_iso.X = 486.0
    v_arm_iso.Y = 258.0
    v_arm_iso.Caption = ""
    estilizar_vista_iram(v_arm_iso, mostrar_ocultas=False, mostrar_centros=False)

    for nm, txt, xv, yv in [
        ("Txt_00a_Planta", ["VISTA SUPERIOR (1:2)"], x_col_00a, 24.0),
        ("Txt_00a_Frente", ["VISTA FRONTAL (1:2)"], x_col_00a, 358.0),
        ("Txt_00a_Corte", ["CORTE LONGITUDINAL A - A (1:2)", "IRAM 4507: Ejes/guías/sinfín sin rayar"], x_corte_00a, 360.0),
        ("Txt_00a_Iso", ["PERSPECTIVA ISOMÉTRICA (1:2,4)"], 486.0, 358.0),
    ]:
        an = doc_planos.addObject("TechDraw::DrawViewAnnotation", nm)
        page_00a.addView(an)
        an.Text = txt
        an.TextSize = 3.6
        an.X = xv
        an.Y = yv

    an_00a_ref = doc_planos.addObject("TechDraw::DrawViewAnnotation", "Nota_00a_Referencias")
    page_00a.addView(an_00a_ref)
    an_00a_ref.Text = [
        "REFERENCIAS CRUZADAS DEL LEGAJO (IRAM 4501-2 ISO-E):",
        "• Despiece explotado completo y Detalles A/B: ver Plano Nº 0b-3D (Hoja 2)",
        "• Lista de materiales (40 ítems: 50 piezas + bulonería #33..#39): Plano Nº 0c-3D",
        "• Secuencia de armado y sellos de Tapa Interior (#3): ver Plano Nº 0d-3D",
        "• Tolerancia general impresión FDM: ±0,20 mm | Ejes torneados según plano.",
    ]
    an_00a_ref.Font = "Liberation Sans"
    an_00a_ref.TextSize = 2.85
    an_00a_ref.LineSpace = 105
    an_00a_ref.X = 486.0
    an_00a_ref.Y = 92.0

    # =========================================================================
    # HOJA 2: PLANO 00b - VISTA EXPLOTADA GENERAL (48 UN.) + DETALLES A Y B (A2)
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

    inst_a_item = {}
    for entrada in CATALOGO_ITEMS_BOM_3D:
        for ins in entrada.get("instancias", []):
            inst_a_item[ins] = entrada["item"]

    # Recuadro Columna Izquierda: Vista Explotada General
    simb_gen = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_Gen_Explotada")
    page_00b.addView(simb_gen)
    simb_gen.Symbol = _generar_svg_recuadro_subensamblaje(
        "VISTA EXPLOTADA GENERAL (50 PIEZAS)", "ESCALA 1:4", 218.0, 392.0
    )
    simb_gen.X = 136.0
    simb_gen.Y = 210.0

    # Desplazamientos en orden físico real de montaje (desde +Z motor hacia -Z cámara exterior)
    offsets_gen = {
        "Tapa_Motor_01_3D": App.Vector(0, 0, 440),
        "Transmisor_A_02a_3D": App.Vector(0, 0, 370),
        "Pasador_3x14_1": App.Vector(0, -35, 370),
        "Cierre_Estructura_1_15_3D": App.Vector(0, 0, 325),
        "Estructura_Interior_1_07_3D": App.Vector(0, 0, 300),
        "Transmisor_B_02b_3D": App.Vector(0, 0, 215),
        "Pasador_3x14_2": App.Vector(0, -35, 215),
        "Pasador_3x10_3": App.Vector(0, -35, 215),
        "Adaptador_Rodamiento_03_3D": App.Vector(0, 0, 158),
        "ORing_Eje_11_2x1_8": App.Vector(0, 0, 135),
        "Rodamiento_SKF_609": App.Vector(0, 0, 118),
        "Adaptador_Eje_04_3D": App.Vector(0, 0, 88),
        "Tuerca_Guia_1_08_3D": App.Vector(0, 0, 62),
        "Tuerca_Guia_2_08_3D": App.Vector(0, 0, 62),
        "Arandela_Guia_1_08_3D": App.Vector(0, 0, 42),
        "Arandela_Guia_2_08_3D": App.Vector(0, 0, 42),
        "Tapa_Interior_16b_3D": App.Vector(0, 0, 20),
        "ORing_Guia_1": App.Vector(0, 0, -2),
        "ORing_Guia_2": App.Vector(0, 0, -2),
        "Sufridera_Guia_1B_3D": App.Vector(0, 0, -16),
        "Sufridera_Guia_2B_3D": App.Vector(0, 0, -16),
        "Sufridera_Int_05b_3D": App.Vector(0, 0, -32),
        "Reten_10x22x7": App.Vector(0, 0, -52),
        "Tapa_Sufridera_Int_05a_3D": App.Vector(0, 0, -70),
        "ORing_Camisa_Int": App.Vector(0, 0, -90),
        "Anillo_Torica_Int_13_3D": App.Vector(0, 0, -112),
        "Centro_Embolo_2_12_3D": App.Vector(0, 0, -92),
        "Sensor_Piston_1_3D": App.Vector(34, 34, -92),
        "Embolo_Delrin_10_3D": App.Vector(0, 0, -118),
        "ORing_Embolo_3D": App.Vector(0, 0, -142),
        "Centro_Embolo_1_11_3D": App.Vector(0, 0, -158),
        "Sensor_Piston_2_3D": App.Vector(34, 34, -158),
        "Guia_1_08_3D": App.Vector(0, 0, -265),
        "Guia_2_08_3D": App.Vector(0, 0, -265),
        "Tornillo_Sin_Fin_14_3D": App.Vector(0, 0, -255),
        "Cilindro_09_3D": App.Vector(0, 0, -445),
        "ORing_Camisa_Ext": App.Vector(0, 0, -478),
        "Anillo_Torica_Ext_13_3D": App.Vector(0, 0, -512),
        "Tapa_Exterior_16a_3D": App.Vector(0, 0, -542),
        "Sufridera_Eje_Ext_05a_3D": App.Vector(0, 0, -568),
        "Estructura_Interior_2_07_3D": App.Vector(0, 0, -595),
        "Cierre_Estructura_2_15_3D": App.Vector(0, 0, -620),
        "Tensor_1_Parte_1": App.Vector(58, 58, 80),
        "Tensor_2_Parte_1": App.Vector(-58, 58, 80),
        "Tensor_3_Parte_1": App.Vector(-58, -58, 80),
        "Tensor_4_Parte_1": App.Vector(58, -58, 80),
        "Tensor_1_Parte_2": App.Vector(58, 58, -360),
        "Tensor_2_Parte_2": App.Vector(-58, 58, -360),
        "Tensor_3_Parte_2": App.Vector(-58, -58, -360),
        "Tensor_4_Parte_2": App.Vector(58, -58, -360),
    }

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

    # Anclajes limpios sobre instancias representativas en Vista Explotada General
    punto_oring_ext = None
    if "ORing_Camisa_Ext" in shapes_ens:
        sh_oe = shapes_ens["ORing_Camisa_Ext"].copy()
        sh_oe.translate(offsets_gen.get("ORing_Camisa_Ext", App.Vector(0, 0, 0)))
        bb_oe = sh_oe.BoundBox
        punto_oring_ext = App.Vector(bb_oe.XMin + 3.0, bb_oe.Center.y, bb_oe.Center.z)

    for it_num, ins_pref, side_r in [
        (1, "Tapa_Exterior_16a_3D", False),
        (2, "Cilindro_09_3D", False),
        (3, "Tapa_Interior_16b_3D", True),
        (4, "Sufridera_Int_05b_3D", False),
        (5, "Tapa_Sufridera_Int_05a_3D", False),
        (6, "Sufridera_Guia_1B_3D", False),
        (7, "Embolo_Delrin_10_3D", False),
        (8, "Centro_Embolo_1_11_3D", False),
        (9, "Centro_Embolo_2_12_3D", False),
        (10, "Sensor_Piston_1_3D", True),
        (11, "Guia_2_08_3D", True),
        (12, "Transmisor_A_02a_3D", True),
        (13, "Transmisor_B_02b_3D", True),
        (14, "Tornillo_Sin_Fin_14_3D", True),
        (15, "Adaptador_Rodamiento_03_3D", True),
        (16, "Sufridera_Eje_Ext_05a_3D", True),
        (17, "Adaptador_Eje_04_3D", True),
        (18, "Anillo_Torica_Int_13_3D", False),
        (19, "Estructura_Interior_1_07_3D", False),
        (20, "Cierre_Estructura_2_15_3D", False),
        (21, "Tensor_1_Parte_1", True),
        (22, "Tensor_1_Parte_2", True),
        (23, "Tapa_Motor_01_3D", True),
        (24, "Rodamiento_SKF_609", True),
        (25, "Reten_10x22x7", False),
        (26, "ORing_Camisa_Int", False),
        (27, "ORing_Embolo_3D", False),
        (28, "ORing_Eje_11_2x1_8", False),
        (31, "Tuerca_Guia_1_08_3D", False),
        (32, "Arandela_Guia_1_08_3D", False),
        (40, "ORing_Guia_1", False),
    ]:
        if ins_pref in shapes_ens:
            sh_c = shapes_ens[ins_pref].copy()
            sh_c.translate(offsets_gen.get(ins_pref, App.Vector(0, 0, 0)))
            bb_c = sh_c.BoundBox
            if it_num == 1:
                puntos_globo_gen[it_num] = App.Vector(bb_c.XMin + 4.0, bb_c.YMin + 4.0, bb_c.Center.z)
            elif it_num in (2, 3, 18, 19, 20, 26, 27):
                xr = bb_c.XMax - 3.0 if side_r else bb_c.XMin + 3.0
                puntos_globo_gen[it_num] = App.Vector(xr, bb_c.Center.y, bb_c.Center.z)
            elif it_num in (11,):
                puntos_globo_gen[it_num] = App.Vector(28.31, 0.0, bb_c.Center.z)
            else:
                puntos_globo_gen[it_num] = bb_c.Center

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
    v_exp_gen.X = 136.0
    v_exp_gen.Y = 203.0
    v_exp_gen.Caption = ""
    estilizar_vista_iram(v_exp_gen, mostrar_ocultas=False, mostrar_centros=False)

    centro_gen = comp_exp_gen.BoundBox.Center
    globos_gen_cols = [
        (23, puntos_globo_gen.get(23), "R"),
        (12, puntos_globo_gen.get(12), "R"),
        (13, puntos_globo_gen.get(13), "R"),
        (15, puntos_globo_gen.get(15), "R"),
        (24, puntos_globo_gen.get(24), "R"),
        (17, puntos_globo_gen.get(17), "R"),
        (3,  puntos_globo_gen.get(3),  "R"),
        (21, puntos_globo_gen.get(21), "R"),
        (10, puntos_globo_gen.get(10), "R"),
        (11, puntos_globo_gen.get(11), "R"),
        (14, puntos_globo_gen.get(14), "R"),
        (22, puntos_globo_gen.get(22), "R"),
        (16, puntos_globo_gen.get(16), "R"),
        (19, puntos_globo_gen.get(19), "L"),
        (28, puntos_globo_gen.get(28), "L"),
        (31, puntos_globo_gen.get(31), "L"),
        (32, puntos_globo_gen.get(32), "L"),
        (6,  puntos_globo_gen.get(6),  "L"),
        (4,  puntos_globo_gen.get(4),  "L"),
        (25, puntos_globo_gen.get(25), "L"),
        (5,  puntos_globo_gen.get(5),  "L"),
        (26, puntos_globo_gen.get(26), "L"),
        (18, puntos_globo_gen.get(18), "L"),
        (8,  puntos_globo_gen.get(8),  "L"),
        (7,  puntos_globo_gen.get(7),  "L"),
        (27, puntos_globo_gen.get(27), "L"),
        (9,  puntos_globo_gen.get(9),  "L"),
        (2,  puntos_globo_gen.get(2),  "L"),
        (26, punto_oring_ext,          "L", "ext"),
        (1,  puntos_globo_gen.get(1),  "L"),
        (20, puntos_globo_gen.get(20), "L"),
    ]
    _distribuir_globos_en_columnas(
        doc_planos,
        page_00b,
        v_exp_gen,
        globos_gen_cols,
        centro_gen,
        escala_exp_gen,
        x_col_izq=37.0,
        x_col_der=235.0,
        y_min_hoja=22.0,
        y_max_hoja=390.0,
        prefijo="Gen",
        paso_min_mm=10.0,
    )

    # --- 2.2 Detalle A: Subensamblaje Móvil del Émbolo y Sellado (arriba derecha) ---
    simb_sub1 = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_Sub_Embolo")
    page_00b.addView(simb_sub1)
    simb_sub1.Symbol = _generar_svg_recuadro_subensamblaje(
        "DETALLE A: SUBENSAMBLAJE MÓVIL DEL ÉMBOLO Y SELLADO",
        "ESCALA 1:1,4 — Guías fijas ver Plano 0d-3D",
        330.0,
        182.0,
    )
    simb_sub1.X = 415.0
    simb_sub1.Y = 315.0

    shapes_sub_emb = []
    puntos_sub_emb = {}

    def _add_emb(ins, dz, dx=0.0, dy=0.0, it_override=None, suf=""):
        sh_e = shapes_ens[ins].copy()
        # Re-centrar Z respecto a Centro Z de Embolo_Delrin (-72.45) para apilado limpio
        sh_e.translate(App.Vector(dx, dy, dz + 72.45))
        shapes_sub_emb.append(sh_e)
        it_num = it_override if it_override is not None else inst_a_item[ins]
        key = (it_num, suf) if suf else it_num
        puntos_sub_emb[key] = sh_e.BoundBox.Center

    _add_emb("Centro_Embolo_2_12_3D", 55.0)
    _add_emb("Sensor_Piston_1_3D", 55.0, dx=38.0, dy=38.0, suf="s1")
    _add_emb("Embolo_Delrin_10_3D", 0.0)
    _add_emb("ORing_Embolo_3D", -32.0)
    _add_emb("Centro_Embolo_1_11_3D", -64.0)
    _add_emb("Sensor_Piston_2_3D", -64.0, dx=38.0, dy=38.0, suf="s2")

    comp_sub_emb = Part.makeCompound(shapes_sub_emb)
    obj_sub_emb = doc_planos.addObject("Part::Feature", "Subensamblaje_Embolo_3D")
    obj_sub_emb.Shape = comp_sub_emb
    if getattr(obj_sub_emb, "ViewObject", None):
        obj_sub_emb.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_sub_emb)

    escala_sub_emb = 0.72
    v_sub_emb = doc_planos.addObject("TechDraw::DrawViewPart", "V00b_Sub_Embolo")
    page_00b.addView(v_sub_emb)
    v_sub_emb.Source = [obj_sub_emb]
    v_sub_emb.Direction = App.Vector(1, -1, 1)
    v_sub_emb.XDirection = App.Vector(1, 1, 0)
    v_sub_emb.ScaleType = "Custom"
    v_sub_emb.Scale = escala_sub_emb
    v_sub_emb.X = 368.0
    v_sub_emb.Y = 309.0
    v_sub_emb.Caption = ""
    estilizar_vista_iram(v_sub_emb, mostrar_ocultas=False, mostrar_centros=False)

    centro_sub_emb = comp_sub_emb.BoundBox.Center
    _distribuir_globos_en_columnas(
        doc_planos,
        page_00b,
        v_sub_emb,
        [
            (7,  puntos_sub_emb[7],          "L"),
            (27, puntos_sub_emb[27],         "L"),
            (8,  puntos_sub_emb[8],          "L"),
            (9,  puntos_sub_emb[9],          "R", "r9"),
            (10, puntos_sub_emb[(10, "s1")], "R", "s1"),
            (10, puntos_sub_emb[(10, "s2")], "R", "s2"),
        ],
        centro_sub_emb,
        escala_sub_emb,
        x_col_izq=276.0,
        x_col_der=444.0,
        y_min_hoja=236.0,
        y_max_hoja=386.0,
        prefijo="Emb",
        paso_min_mm=12.0,
    )

    an_emb_nota = doc_planos.addObject("TechDraw::DrawViewAnnotation", "Nota_Detalle_A_Embolo")
    page_00b.addView(an_emb_nota)
    an_emb_nota.Text = [
        "DESLIZAMIENTO SOBRE GUÍAS (#11):",
        "• Los agujeros 2× Ø10,57 en ±28,31",
        "  de Émbolo (#7) deslizan sobre",
        "  Guías Ø8,22 (#11) tope en #3.",
        "• Rosca central de #8/#9 acopla",
        "  con Tornillo Sin Fin (#14).",
        "• Bloques Sensor (#10 x2) calzan",
        "  a 45° con pasta/tornillo.",
        "• Armado completo de guías y",
        "  sufrideras #6: Plano Nº 0d-3D.",
    ]
    an_emb_nota.Font = "Liberation Sans"
    an_emb_nota.TextSize = 2.8
    an_emb_nota.LineSpace = 95
    an_emb_nota.X = 516.0
    an_emb_nota.Y = 315.0

    # --- 2.3 Detalle B: Tren Rotativo Completo en Orientación Real (abajo centro) ---
    simb_sub2 = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_Sub_Transmision")
    page_00b.addView(simb_sub2)
    simb_sub2.Symbol = _generar_svg_recuadro_subensamblaje(
        "DETALLE B: TREN ROTATIVO COMPLETO", "ESC. 1:2,5 — Orient. real", 155.0, 206.0
    )
    simb_sub2.X = 327.5
    simb_sub2.Y = 117.0

    shapes_sub_tr = []
    puntos_sub_tr = {}
    # Apilado dinámico de arriba (+Z) hacia abajo (-Z) usando orientación real ensamblada (shapes_ens)
    orden_sub_tr = [
        ("Transmisor_A_02a_3D",       12,  4.0, (0.0, 0.0)),
        ("Pasador_3x14_2",            29,  0.0, (-18.0, -18.0)),
        ("Adaptador_Rodamiento_03_3D",15,  9.5, (0.0, 0.0)),
        ("ORing_Eje_11_2x1_8",        28,  8.5, (0.0, 0.0)),
        ("Rodamiento_SKF_609",        24,  9.5, (0.0, 0.0)),
        ("Adaptador_Eje_04_3D",       17,  9.5, (0.0, 0.0)),
        ("Sufridera_Int_05b_3D",       4,  8.5, (0.0, 0.0)),
        ("Reten_10x22x7",             25,  8.5, (0.0, 0.0)),
        ("Tapa_Sufridera_Int_05a_3D",  5,  8.0, (0.0, 0.0)),
        ("Transmisor_B_02b_3D",       13,  4.5, (0.0, 0.0)),
        ("Pasador_3x10_3",            30,  0.0, (18.0, 18.0)),
        ("Tornillo_Sin_Fin_14_3D",    14,  4.5, (0.0, 0.0)),
        ("Sufridera_Eje_Ext_05a_3D",  16,  0.0, (0.0, 0.0)),
    ]
    z_cursor_tr = 215.0
    pasadores_traj = []
    for ins_name, it_id, gap_below, (off_x, off_y) in orden_sub_tr:
        sh_t = shapes_ens[ins_name].copy()
        bb_t = sh_t.BoundBox
        if abs(off_x) > 1e-3 or abs(off_y) > 1e-3:
            z_dest = prev_mid_z - bb_t.Center.z
            pasadores_traj.append((App.Vector(0.0, 0.0, prev_mid_z), App.Vector(off_x, off_y, prev_mid_z)))
        else:
            z_dest = z_cursor_tr - bb_t.ZMax
            prev_mid_z = z_cursor_tr - 0.5 * bb_t.ZLength
            z_cursor_tr -= (bb_t.ZLength + gap_below)
        sh_t.translate(App.Vector(off_x, off_y, z_dest))
        shapes_sub_tr.append(sh_t)
        puntos_sub_tr[it_id] = sh_t.BoundBox.Center

    comp_sub_tr = Part.makeCompound(shapes_sub_tr)
    obj_sub_tr = doc_planos.addObject("Part::Feature", "Subensamblaje_Transmision_3D")
    obj_sub_tr.Shape = comp_sub_tr
    if getattr(obj_sub_tr, "ViewObject", None):
        obj_sub_tr.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_sub_tr)

    escala_sub_tr = 0.40
    v_sub_tr = doc_planos.addObject("TechDraw::DrawViewPart", "V00b_Sub_Transmision")
    page_00b.addView(v_sub_tr)
    v_sub_tr.Source = [obj_sub_tr]
    v_sub_tr.Direction = App.Vector(1, -1, 1)
    v_sub_tr.XDirection = App.Vector(1, 1, 0)
    v_sub_tr.ScaleType = "Custom"
    v_sub_tr.Scale = escala_sub_tr
    v_sub_tr.X = 327.5
    v_sub_tr.Y = 113.0
    v_sub_tr.Caption = ""
    estilizar_vista_iram(v_sub_tr, mostrar_ocultas=False, mostrar_centros=False)

    centro_sub_tr = comp_sub_tr.BoundBox.Center
    _distribuir_globos_en_columnas(
        doc_planos,
        page_00b,
        v_sub_tr,
        [
            (12, puntos_sub_tr[12], "R"),
            (15, puntos_sub_tr[15], "R"),
            (24, puntos_sub_tr[24], "R"),
            (4,  puntos_sub_tr[4],  "R"),
            (5,  puntos_sub_tr[5],  "R"),
            (30, puntos_sub_tr[30], "R"),
            (16, puntos_sub_tr[16], "R"),
            (29, puntos_sub_tr[29], "L"),
            (28, puntos_sub_tr[28], "L"),
            (17, puntos_sub_tr[17], "L"),
            (25, puntos_sub_tr[25], "L"),
            (13, puntos_sub_tr[13], "L"),
            (14, puntos_sub_tr[14], "L"),
        ],
        centro_sub_tr,
        escala_sub_tr,
        x_col_izq=260.0,
        x_col_der=395.0,
        y_min_hoja=19.0,
        y_max_hoja=207.0,
        prefijo="Tr",
        paso_min_mm=11.5,
    )

    # --- 2.4 Panel Técnico de Referencias y Sellos (abajo derecha sobre rótulo) ---
    simb_guia_00b = doc_planos.addObject("TechDraw::DrawViewSymbol", "Panel_Guia_Armado_00b")
    page_00b.addView(simb_guia_00b)
    simb_guia_00b.Symbol = _generar_svg_guia_armado_00b(171.0, 155.0)
    simb_guia_00b.X = 494.5
    simb_guia_00b.Y = 142.5

    # =========================================================================
    # HOJA 3: PLANO 00c - LISTA DE MATERIALES Y DESPIECE IRAM 4508 (A3)
    # =========================================================================
    rotulo_00c = dict(campos_base)
    rotulo_00c.update(
        {
            "ESCALA": "S/E",
            "FORMATO": "IRAM A3",
            "HOJA": f"3/{total_hojas}",
            "TITULO": "Lista de Materiales 3D (40 Ítems: 50 Piezas + Bulonería)",
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
    simbolo_bom.Scale = 0.87
    simbolo_bom.X = 216.0
    simbolo_bom.Y = 171.0

    # =========================================================================
    # HOJA 4: PLANO 00d - DETALLE EXPLOTADO Y SECCIÓN DE TAPA INTERIOR INTERMEDIA (A2)
    # =========================================================================
    rotulo_00d = dict(campos_base)
    rotulo_00d.update(
        {
            "ESCALA": "1:2 / 1:2,8",
            "FORMATO": "IRAM A2",
            "HOJA": f"4/{total_hojas}",
            "TITULO": "Tapa Interior — Rulemán, Retén y Guías",
            "MATERIAL": "Según Tabla IRAM 4508",
            "MASA": "Subconj. Hub",
            "TOL_GRAL": "FDM ±0,20 mm",
            "NUM_PLANO": "Plano Nº 0d-3D",
        }
    )
    page_00d, _ = _crear_pagina_iram(
        doc_planos,
        "Plano_00d_Explotada_Tapa_Interior_3D",
        "Plano_00d_Explotada_Tapa_Interior_3D",
        "A2",
        rutas_plantillas,
        rotulo_00d,
    )

    def _clip_z_rango(sh_in, zmin_c, zmax_c):
        caja = Part.makeBox(300.0, 300.0, zmax_c - zmin_c, App.Vector(-150.0, -150.0, zmin_c))
        return sh_in.common(caja)

    # Construcción desde shapes_ens (orientación real montada en Piloto_Impresion_3D_Assembly)
    # Separación calibrada para evitar oclusión de #15/#28 bajo #19 y de #6 (inf.) bajo #3 en Vista Iso.
    specs_00d = [
        ("Transmisor_B_02b_3D",        App.Vector(0, 0, 345), None),
        ("Cierre_Estructura_1_15_3D",  App.Vector(0, 0, 296), None),
        ("Estructura_Interior_1_07_3D",App.Vector(0, 0, 258), None),
        ("Adaptador_Rodamiento_03_3D", App.Vector(0, 0, 148), None),
        ("ORing_Eje_11_2x1_8",         App.Vector(0, 0, 122), None),
        ("Rodamiento_SKF_609",         App.Vector(0, 0,  98), None),
        ("Adaptador_Eje_04_3D",        App.Vector(0, 0,  68), None),
        ("Tuerca_Guia_1_08_3D",        App.Vector(0, 0,  42), None),
        ("Tuerca_Guia_2_08_3D",        App.Vector(0, 0,  42), None),
        ("Arandela_Guia_1_08_3D",      App.Vector(0, 0,  22), None),
        ("Arandela_Guia_2_08_3D",      App.Vector(0, 0,  22), None),
        ("Tapa_Interior_16b_3D",       App.Vector(0, 0,   0), None),
        ("ORing_Guia_1",               App.Vector(0, 0, -34), None),
        ("ORing_Guia_2",               App.Vector(0, 0, -34), None),
        ("Sufridera_Guia_1B_3D",       App.Vector(0, 0, -56), None),
        ("Sufridera_Guia_2B_3D",       App.Vector(0, 0, -56), None),
        ("Sufridera_Int_05b_3D",       App.Vector(0, 0, -80), None),
        ("Reten_10x22x7",              App.Vector(0, 0,-102), None),
        ("Tapa_Sufridera_Int_05a_3D",  App.Vector(0, 0,-124), None),
        ("ORing_Camisa_Int",           App.Vector(0, 0,-144), None),
        ("Anillo_Torica_Int_13_3D",    App.Vector(0, 0,-166), None),
        ("Cilindro_09_3D",             App.Vector(0, 0,-198), (-16.0, 20.0)),
        ("Guia_1_08_3D",               App.Vector(0, 0,-266), (-12.0, 40.0)),
        ("Guia_2_08_3D",               App.Vector(0, 0,-266), (-12.0, 40.0)),
    ]

    shapes_00d = []
    anchors_00d = {}
    for ins, off, zclip in specs_00d:
        sh_i = shapes_ens[ins].copy()
        if zclip is not None:
            sh_i = _clip_z_rango(sh_i, zclip[0], zclip[1])
        sh_i.translate(off)
        shapes_00d.append(sh_i)
        anchors_00d[ins] = sh_i.BoundBox

    # Ajustes de anclaje fino para globos (que apunten al borde visible y no al vacío central de anillos)
    pt_00d = {
        (13, ""):    anchors_00d["Transmisor_B_02b_3D"].Center,
        (20, ""):    App.Vector(anchors_00d["Cierre_Estructura_1_15_3D"].XMax - 4.0, 0.0, anchors_00d["Cierre_Estructura_1_15_3D"].Center.z),
        (19, ""):    App.Vector(anchors_00d["Estructura_Interior_1_07_3D"].XMin + 4.0, 0.0, anchors_00d["Estructura_Interior_1_07_3D"].Center.z),
        (15, ""):    App.Vector(anchors_00d["Adaptador_Rodamiento_03_3D"].XMax - 5.0, 0.0, anchors_00d["Adaptador_Rodamiento_03_3D"].Center.z),
        (28, ""):    App.Vector(anchors_00d["ORing_Eje_11_2x1_8"].XMin + 1.5, 0.0, anchors_00d["ORing_Eje_11_2x1_8"].Center.z),
        (24, ""):    App.Vector(anchors_00d["Rodamiento_SKF_609"].XMax - 2.0, 0.0, anchors_00d["Rodamiento_SKF_609"].Center.z),
        (17, ""):    App.Vector(anchors_00d["Adaptador_Eje_04_3D"].XMax - 3.0, 0.0, anchors_00d["Adaptador_Eje_04_3D"].Center.z),
        (31, ""):    anchors_00d["Tuerca_Guia_1_08_3D"].Center,
        (32, ""):    anchors_00d["Arandela_Guia_1_08_3D"].Center,
        (3,  ""):    App.Vector(anchors_00d["Tapa_Interior_16b_3D"].XMax - 6.0, 0.0, anchors_00d["Tapa_Interior_16b_3D"].Center.z),
        (40, ""):    anchors_00d["ORing_Guia_1"].Center,
        (6,  ""):    anchors_00d["Sufridera_Guia_1B_3D"].Center,
        (4,  ""):    App.Vector(anchors_00d["Sufridera_Int_05b_3D"].XMax - 3.0, 0.0, anchors_00d["Sufridera_Int_05b_3D"].Center.z),
        (25, ""):    App.Vector(anchors_00d["Reten_10x22x7"].XMin + 2.5, 0.0, anchors_00d["Reten_10x22x7"].Center.z),
        (5,  ""):    App.Vector(anchors_00d["Tapa_Sufridera_Int_05a_3D"].XMax - 3.0, 0.0, anchors_00d["Tapa_Sufridera_Int_05a_3D"].Center.z),
        (26, ""):    App.Vector(anchors_00d["ORing_Camisa_Int"].XMin + 2.5, 0.0, anchors_00d["ORing_Camisa_Int"].Center.z),
        (18, ""):    App.Vector(anchors_00d["Anillo_Torica_Int_13_3D"].XMax - 4.0, 0.0, anchors_00d["Anillo_Torica_Int_13_3D"].Center.z),
        (2,  ""):    App.Vector(anchors_00d["Cilindro_09_3D"].XMin + 3.0, 0.0, anchors_00d["Cilindro_09_3D"].Center.z),
        (11, ""):    App.Vector(28.31, 0.0, anchors_00d["Guia_2_08_3D"].Center.z),
    }

    comp_00d = Part.makeCompound(shapes_00d)
    obj_00d = doc_planos.addObject("Part::Feature", "Subensamblaje_Tapa_Interior_00d")
    obj_00d.Shape = comp_00d
    if getattr(obj_00d, "ViewObject", None):
        obj_00d.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_00d)

    # Sólido limpio para Vista C (Planta superior +Z de alineación de bridas y guías)
    shapes_00d_planta = [
        shapes_ens[n].copy()
        for n in (
            "Tapa_Interior_16b_3D",
            "Arandela_Guia_1_08_3D",
            "Arandela_Guia_2_08_3D",
            "Tuerca_Guia_1_08_3D",
            "Tuerca_Guia_2_08_3D",
            "Adaptador_Eje_04_3D",
            "Adaptador_Rodamiento_03_3D",
        )
    ]
    comp_00d_planta = Part.makeCompound(shapes_00d_planta)
    obj_00d_planta = doc_planos.addObject("Part::Feature", "Planta_Tapa_Interior_00d")
    obj_00d_planta.Shape = comp_00d_planta
    if getattr(obj_00d_planta, "ViewObject", None):
        obj_00d_planta.ViewObject.Visibility = False
    grupo_fuentes.addObject(obj_00d_planta)

    # --- 4.1 Recuadros de Vista A, Vista B y Vista C ---
    simb_00d_a = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_00d_VistaA")
    page_00d.addView(simb_00d_a)
    simb_00d_a.Symbol = _generar_svg_recuadro_subensamblaje(
        "VISTA A: EXPLOTADA ISOMÉTRICA TAPA INTERIOR", "ESCALA 1:2", 205.0, 392.0
    )
    simb_00d_a.X = 129.5
    simb_00d_a.Y = 210.0

    simb_00d_b = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_00d_VistaB")
    page_00d.addView(simb_00d_b)
    simb_00d_b.Symbol = _generar_svg_recuadro_subensamblaje(
        "VISTA B: CORTE LONGITUDINAL A-A (Y = 0)", "ESCALA 1:2", 170.0, 392.0
    )
    simb_00d_b.X = 321.0
    simb_00d_b.Y = 210.0

    simb_00d_c = doc_planos.addObject("TechDraw::DrawViewSymbol", "Recuadro_00d_VistaC")
    page_00d.addView(simb_00d_c)
    simb_00d_c.Symbol = _generar_svg_recuadro_subensamblaje(
        "VISTA C: ALINEACIÓN ANGULAR (+Z)", "ESCALA 1:2,8", 170.0, 108.0
    )
    simb_00d_c.X = 495.0
    simb_00d_c.Y = 352.0

    # --- 4.2 Vista A: Explotada Isométrica 1:2 ---
    escala_00d_ab = 0.50
    v_00d_iso = doc_planos.addObject("TechDraw::DrawViewPart", "V00d_Iso_Tapa_Interior")
    page_00d.addView(v_00d_iso)
    v_00d_iso.Source = [obj_00d]
    v_00d_iso.Direction = App.Vector(1, -1, 1)
    v_00d_iso.XDirection = App.Vector(1, 1, 0)
    v_00d_iso.ScaleType = "Custom"
    v_00d_iso.Scale = escala_00d_ab
    v_00d_iso.X = 129.5
    v_00d_iso.Y = 204.0
    v_00d_iso.Caption = ""
    estilizar_vista_iram(v_00d_iso, mostrar_ocultas=False, mostrar_centros=False)

    centro_00d = comp_00d.BoundBox.Center
    globos_00d_a = [
        (13, pt_00d[(13, "")],    "R"),
        (20, pt_00d[(20, "")],    "R"),
        (15, pt_00d[(15, "")],    "R"),
        (24, pt_00d[(24, "")],    "R"),
        (17, pt_00d[(17, "")],    "R"),
        (3,  pt_00d[(3,  "")],    "R"),
        (4,  pt_00d[(4,  "")],    "R"),
        (5,  pt_00d[(5,  "")],    "R"),
        (18, pt_00d[(18, "")],    "R"),
        (11, pt_00d[(11, "")],    "R"),
        (19, pt_00d[(19, "")],    "L"),
        (28, pt_00d[(28, "")],    "L"),
        (31, pt_00d[(31, "")],    "L"),
        (32, pt_00d[(32, "")],    "L"),
        (40, pt_00d[(40, "")],    "L"),
        (6,  pt_00d[(6,  "")],    "L"),
        (25, pt_00d[(25, "")],    "L"),
        (26, pt_00d[(26, "")],    "L"),
        (2,  pt_00d[(2,  "")],    "L"),
    ]
    _distribuir_globos_en_columnas(
        doc_planos,
        page_00d,
        v_00d_iso,
        globos_00d_a,
        centro_00d,
        escala_00d_ab,
        x_col_izq=39.0,
        x_col_der=220.0,
        y_min_hoja=24.0,
        y_max_hoja=388.0,
        prefijo="00dA",
        paso_min_mm=11.0,
    )

    # --- 4.3 Vista C: Planta Superior +Z (1:2,8) — usa obj_00d como BaseView para que Corte A-A corte las 22 piezas ---
    escala_00d_c = round(1.0 / 2.8, 4)
    dir_top = App.Vector(0, 0, 1)
    xdir_top = App.Vector(1, 0, 0)
    v_00d_planta = doc_planos.addObject("TechDraw::DrawViewPart", "V00d_Planta_Alineacion")
    page_00d.addView(v_00d_planta)
    v_00d_planta.Source = [obj_00d]
    v_00d_planta.Direction = dir_top
    v_00d_planta.XDirection = xdir_top
    v_00d_planta.ScaleType = "Custom"
    v_00d_planta.Scale = escala_00d_c
    v_00d_planta.X = 465.0
    v_00d_planta.Y = 348.0
    v_00d_planta.Caption = ""
    estilizar_vista_iram(v_00d_planta, mostrar_ocultas=False, mostrar_centros=True)

    # Globos clave sobre Vista C para distinguir #19 (ext.), #15 (22,5°), #17 (45°), #31 (guías ±28,31)
    _distribuir_globos_en_columnas(
        doc_planos,
        page_00d,
        v_00d_planta,
        [
            (19, App.Vector(-64.0,  22.0, centro_00d.z), "L"),
            (17, App.Vector(-15.0, -15.0, centro_00d.z), "L"),
            (15, App.Vector( 17.09,  7.08, centro_00d.z), "R"),
            (31, App.Vector( 28.31,  0.0, centro_00d.z), "R"),
        ],
        centro_00d,
        escala_00d_c,
        x_col_izq=421.0,
        x_col_der=505.0,
        y_min_hoja=310.0,
        y_max_hoja=390.0,
        prefijo="00dC",
        direction=dir_top,
        x_direction=xdir_top,
        paso_min_mm=12.0,
    )

    an_00d_c = doc_planos.addObject("TechDraw::DrawViewAnnotation", "Nota_00d_Planta_PCD")
    page_00d.addView(an_00d_c)
    an_00d_c.Text = [
        "PLANO CORTE A-A (Y=0)",
        "• Guías: X=±28,31 (#31/#6)",
        "• #17→#3: 4x a 45° (Ø37,8)",
        "• #15→#17: 4x a 22,5° (Ø37,0)",
        "• Muescas Ø15,6 libran #31.",
        "• Bolsillo sensor: +45° libre.",
    ]
    an_00d_c.Font = "Liberation Sans"
    an_00d_c.TextSize = 2.45
    an_00d_c.LineSpace = 95
    an_00d_c.X = 543.0
    an_00d_c.Y = 349.0

    # --- 4.4 Vista B: Corte Longitudinal Explotado A-A por Y=0 (1:2) ---
    dir_sec = App.Vector(0, -1, 0)
    xdir_sec = App.Vector(1, 0, 0)
    v_00d_sec = doc_planos.addObject("TechDraw::DrawViewSection", "V00d_Corte_AA_Tapa_Interior")
    page_00d.addView(v_00d_sec)
    v_00d_sec.BaseView = v_00d_planta
    v_00d_sec.Source = [obj_00d]
    v_00d_sec.Direction = dir_sec
    v_00d_sec.SectionNormal = App.Vector(0, -1, 0)
    v_00d_sec.SectionOrigin = App.Vector(0, 0, centro_00d.z)
    v_00d_sec.XDirection = xdir_sec
    v_00d_sec.SectionSymbol = "A"
    v_00d_sec.FuseBeforeCut = False
    v_00d_sec.CutSurfaceDisplay = "SvgHatch"
    if hasattr(v_00d_sec, "HatchScale"):
        v_00d_sec.HatchScale = 0.75
    v_00d_sec.ScaleType = "Custom"
    v_00d_sec.Scale = escala_00d_ab
    v_00d_sec.X = 321.0
    v_00d_sec.Y = 204.0
    v_00d_sec.Caption = ""
    estilizar_vista_iram(v_00d_sec, mostrar_ocultas=False, mostrar_centros=False)

    globos_00d_b = [
        (13, pt_00d[(13, "")],    "R"),
        (20, pt_00d[(20, "")],    "R"),
        (15, pt_00d[(15, "")],    "R"),
        (24, pt_00d[(24, "")],    "R"),
        (17, pt_00d[(17, "")],    "R"),
        (3,  pt_00d[(3,  "")],    "R"),
        (4,  pt_00d[(4,  "")],    "R"),
        (5,  pt_00d[(5,  "")],    "R"),
        (18, pt_00d[(18, "")],    "R"),
        (11, pt_00d[(11, "")],    "R"),
        (19, pt_00d[(19, "")],    "L"),
        (28, pt_00d[(28, "")],    "L"),
        (31, pt_00d[(31, "")],    "L"),
        (32, pt_00d[(32, "")],    "L"),
        (40, pt_00d[(40, "")],    "L"),
        (6,  pt_00d[(6,  "")],    "L"),
        (25, pt_00d[(25, "")],    "L"),
        (26, pt_00d[(26, "")],    "L"),
        (2,  pt_00d[(2,  "")],    "L"),
    ]
    _distribuir_globos_en_columnas(
        doc_planos,
        page_00d,
        v_00d_sec,
        globos_00d_b,
        centro_00d,
        escala_00d_ab,
        x_col_izq=247.0,
        x_col_der=395.0,
        y_min_hoja=24.0,
        y_max_hoja=388.0,
        prefijo="00dB",
        direction=dir_sec,
        x_direction=xdir_sec,
        paso_min_mm=11.0,
    )

    an_00d_top = doc_planos.addObject("TechDraw::DrawViewAnnotation", "Nota_00d_Lado_Motor")
    page_00d.addView(an_00d_top)
    an_00d_top.Text = ["▲ LADO MOTOR / SECO (+Z) ▲"]
    an_00d_top.Font = "Liberation Sans"
    an_00d_top.TextSize = 2.9
    an_00d_top.TextStyle = "Bold"
    an_00d_top.X = 321.0
    an_00d_top.Y = 392.0

    an_00d_bot = doc_planos.addObject("TechDraw::DrawViewAnnotation", "Nota_00d_Lado_Camara")
    page_00d.addView(an_00d_bot)
    an_00d_bot.Text = ["▼ LADO CÁMARA / HÚMEDO (-Z) — Guías y Cilindro: tramo sup. ▼"]
    an_00d_bot.Font = "Liberation Sans"
    an_00d_bot.TextSize = 2.6
    an_00d_bot.TextStyle = "Bold"
    an_00d_bot.X = 321.0
    an_00d_bot.Y = 20.0

    # --- 4.5 Panel de Secuencia y O-Rings (abajo derecha sobre rótulo) ---
    simb_00d_seq = doc_planos.addObject("TechDraw::DrawViewSymbol", "Panel_Secuencia_Tapa_Int_00d")
    page_00d.addView(simb_00d_seq)
    simb_00d_seq.Symbol = _generar_svg_secuencia_tapa_int_00d(170.0, 229.0)
    simb_00d_seq.X = 495.0
    simb_00d_seq.Y = 179.5

    # =========================================================================
    # HOJAS 5 A 28: 24 PLANOS INDIVIDUALES DE PIEZAS A ESCALA 3D
    # =========================================================================
    # HOJAS 5..28: PLANOS INDIVIDUALES AUTÓNOMOS DE PIEZAS 3D (IRAM 4501/4502/4507/4513)
    # =========================================================================
    ESPECIFICACIONES_HOJAS_3D = {
        1: {
            "familia": "A", "formato": "A3", "escala": 1.0, "escala_txt": "1:1",
            "extra_y_titulo": 48.0,
            "resumen": [
                ("Diámetro exterior de brida", "Ø120,80 mm"),
                ("Espesor / altura total", "22,65 mm"),
                ("Alojamiento camisa vidrio", "Ø83,43 × 5,36 (fondo a 10,57)"),
                ("Escalones sello / centrado", "Ø90,68 × 5,21 | Ø109,47 × 3,40"),
                ("Cavidades centrales cámara", "Ø30,60 × 4,23 | Ø14,00 × 6,45"),
                ("Guías de émbolo (ciegas)", "2× Ø10,57 × 8,31 @ X=±28,31"),
                ("Puertos axiales / purga 45°", "2× Ø6,47/Ø3,70 (Y) | Ø8,24 (-135°)"),
                ("Coronas ciegas Ø1,86", "DBC Ø115,20 | Ø98,16 | Ø21,90"),
            ],
            "planta": {
                "diams": [
                    (120.80, -35.0, 14.0, "", None),
                    {"d": 10.57, "cx": -28.31, "cy": 0.0, "ang": 145.0, "r_off": 48.0},
                    {"d": 3.70, "cx": 0.0, "cy": -28.31, "ang": -138.0, "r_off": 46.0},
                    {"d": 8.24, "cx": -20.02, "cy": 20.02, "ang": 135.0, "r_off": 46.0},
                    {"d": 1.86, "cx": 57.57, "cy": 0.0, "ang": 38.0, "r_off": 26.0},
                ],
                "dbcs": [
                    (115.20, 4, 0.0, None, 20.0, None),
                    (98.16, 4, 0.0, None, -20.0, None),
                    (21.90, 4, 0.0, None, 140.0, None),
                ],
                "dists": [
                    {"p1": (-28.31, 0.0, 12.08), "p2": (28.31, 0.0, 12.08), "tipo": "DistanceX", "oy": 68.0},
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (54.735, 19.25), "p2": (54.735, 22.65), "tipo": "DistanceY", "ax": 72.0},
                    {"p1": (33.595, 3.77), "p2": (33.595, 12.08), "tipo": "DistanceY", "ax": 84.0},
                    {"p1": (60.40, 0.0), "p2": (60.40, 22.65), "tipo": "DistanceY", "ax": 96.0},
                    {"p1": (-45.34, 17.44), "p2": (-45.34, 22.65), "tipo": "DistanceY", "ax": -72.0},
                    {"p1": (-41.715, 12.08), "p2": (-41.715, 22.65), "tipo": "DistanceY", "ax": -84.0},
                    {"p1": (-7.00, 1.40), "p2": (-7.00, 22.65), "tipo": "DistanceY", "ax": -96.0},
                    {"p1": (-7.00, 1.40), "p2": (7.00, 1.40), "tipo": "DistanceX", "ay": 18.0, "pref": "Ø"},
                    {"p1": (-15.30, 7.85), "p2": (15.30, 7.85), "tipo": "DistanceX", "ay": 25.0, "pref": "Ø"},
                    {"p1": (-45.34, 17.44), "p2": (45.34, 17.44), "tipo": "DistanceX", "ay": 32.0, "pref": "Ø"},
                    {"p1": (-54.735, 19.25), "p2": (54.735, 19.25), "tipo": "DistanceX", "ay": 39.0, "pref": "Ø"},
                    {"p1": (-41.715, 12.08), "p2": (41.715, 12.08), "tipo": "DistanceX", "oy": -18.0, "pref": "Ø"},
                ],
                "lideres": [((60.4, 19.0), (34.0, 12.0), "0,38×45°")],
            },
        },
        2: {
            "familia": "A", "formato": "A3", "escala": 0.5, "escala_txt": "1:2",
            "resumen": [
                ("Diámetro exterior tubo", "Ø83,00 ± 0,20 mm"),
                ("Diámetro interior camisa", "Ø76,00 ± 0,20 mm"),
                ("Longitud total rectificada", "188,75 ± 0,30 mm"),
                ("Espesor nominal de pared", "3,50 mm (vidrio sodocálcico)"),
                ("Perpendicularidad extremos", "⊥ 0,15 | A (caras pulidas al agua)"),
            ],
            "planta": {
                "diams": [
                    (83.00, -40.0, 14.0, "", 0.20),
                    (76.00, 135.0, 14.0, "", 0.20),
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (41.5, 0.0), "p2": (41.5, 188.75), "tipo": "DistanceY", "ox": 18.0, "tol_sym": 0.30},
                    {"p1": (38.0, 0.0), "p2": (41.5, 0.0), "tipo": "DistanceX", "oy": -18.0},
                ],
                "lideres": [
                    ((-41.5, 94.375), (-20.0, 0.0), "A", "Square"),
                    ((39.75, 188.75), (20.0, 14.0), "⊥ 0,15 | A", "Rectangle"),
                ],
            },
        },
        3: {
            "familia": "A", "formato": "A3", "escala": 1.0, "escala_txt": "1:1",
            "extra_y_titulo": 48.0,
            "resumen": [
                ("Diámetro exterior de brida", "Ø120,80 mm"),
                ("Espesor total de tapa", "22,65 mm"),
                ("Asiento vidrio / O-Ring (-Z)", "Ø83,43 × 6,12 | Ø90,68×5,21 | Ø109,47×3,40"),
                ("Alojamiento sufridera retén", "Ø34,05 × 7,92 | paso Ø30,20 (+Z)"),
                ("Guías (±28,31): paso y tope", "Ø15,50×2,37 | Ø7,63 | Ø13,59×1,74"),
                ("Puerto sensor a +45°", "Ø8,24 pas. @ R=28,87 (20,41; 20,41)"),
                ("Coronas tornillos Ø1,86", "DBC Ø37,76 | 2×Ø11,32 | Ø98,16 | Ø115,20"),
            ],
            "planta": {
                "diams": [
                    (120.80, -35.0, 14.0, "", None),
                    {"d": 13.59, "cx": -28.31, "cy": 0.0, "ang": 148.0, "r_off": 48.0},
                    {"d": 7.63, "cx": 28.31, "cy": 0.0, "ang": 42.0, "r_off": 48.0},
                    {"d": 8.24, "cx": 20.41, "cy": -20.41, "ang": -45.0, "r_off": 44.0},
                    {"d": 6.47, "cx": 0.0, "cy": -28.31, "ang": -140.0, "r_off": 46.0},
                    {"d": 3.70, "cx": 0.0, "cy": 28.31, "ang": 145.0, "r_off": 48.0},
                    {"d": 1.86, "cx": 13.35, "cy": -13.35, "ang": -72.0, "r_off": 52.0},
                ],
                "dbcs": [
                    (115.20, 4, 0.0, None, 20.0, None),
                    (98.16, 4, 0.0, None, -20.0, None),
                    (37.76, 4, 45.0, None, 135.0, None),
                    (11.32, 4, 0.0, None, -55.0, None, 28.31, 0.0),
                    (11.32, 4, 0.0, None, None, None, -28.31, 0.0),
                ],
                "dists": [
                    {"p1": (-28.31, 0.0, 11.33), "p2": (28.31, 0.0, 11.33), "tipo": "DistanceX", "oy": 68.0},
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (35.10, 20.91), "p2": (35.10, 22.65), "tipo": "DistanceY", "ax": 72.0},
                    {"p1": (36.06, 11.33), "p2": (36.06, 13.70), "tipo": "DistanceY", "ax": 84.0},
                    {"p1": (54.735, 0.0), "p2": (54.735, 3.40), "tipo": "DistanceY", "ax": 96.0},
                    {"p1": (60.40, 0.0), "p2": (60.40, 22.65), "tipo": "DistanceY", "ax": 108.0},
                    {"p1": (-45.34, 0.0), "p2": (-45.34, 5.21), "tipo": "DistanceY", "ax": -72.0},
                    {"p1": (-41.715, 0.0), "p2": (-41.715, 11.33), "tipo": "DistanceY", "ax": -84.0},
                    {"p1": (-17.025, 11.33), "p2": (-17.025, 19.25), "tipo": "DistanceY", "ax": -96.0},
                    {"p1": (-15.10, 22.65), "p2": (15.10, 22.65), "tipo": "DistanceX", "ay": 18.0, "pref": "Ø"},
                    {"p1": (-17.025, 19.25), "p2": (17.025, 19.25), "tipo": "DistanceX", "ay": 25.0, "pref": "Ø"},
                    {"p1": (-45.34, 5.21), "p2": (45.34, 5.21), "tipo": "DistanceX", "ay": 32.0, "pref": "Ø"},
                    {"p1": (-54.735, 3.40), "p2": (54.735, 3.40), "tipo": "DistanceX", "ay": 39.0, "pref": "Ø"},
                    {"p1": (-41.715, 11.33), "p2": (41.715, 11.33), "tipo": "DistanceX", "oy": -18.0, "pref": "Ø"},
                    {"p1": (20.56, 11.33), "p2": (36.06, 11.33), "tipo": "DistanceX", "ay": -28.0, "pref": "Ø"},
                ],
                "lideres": [((60.4, 18.87), (32.0, 12.0), "0,38×45°")],
            },
        },
        4: {
            "familia": "A", "formato": "A4", "escala": 1.5, "escala_txt": "1,5:1",
            "resumen": [
                ("Diámetro exterior de brida", "Ø33,98 mm (escalón base 0,90 mm)"),
                ("Altura total (extensión retén)", "7,12 mm"),
                ("Alojamiento retén 10×22×7", "Ø22,40 mm (ajuste FDM)"),
                ("Fijación ciega a Tapa 16b", "4× Ø1,86 × 3,78 mm @ DBC Ø28,32"),
                ("Chaflanes de arista", "0,20 × 45°"),
            ],
            "planta": {
                "diams": [
                    (33.98, 135.0, 11.0, "", None),
                    (22.40, -140.0, 12.0, "", None),
                    {"d": 1.86, "cx": 14.16, "cy": 0.0, "ang": -22.0, "r_off": 24.0},
                ],
                "dbcs": [(28.32, 4, 0.0, None, 45.0, None)],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (15.08, 3.34), "p2": (15.08, 7.12), "tipo": "DistanceY", "ax": 36.0},
                    {"p1": (16.99, 0.0), "p2": (16.99, 7.12), "tipo": "DistanceY", "ax": 48.0},
                    {"p1": (-16.99, 0.0), "p2": (-16.99, 0.90), "tipo": "DistanceY", "ax": -36.0},
                ],
                "lideres": [((16.99, 6.7), (16.0, 12.0), "0,20×45°")],
            },
        },
        5: {
            "familia": "A", "formato": "A4", "escala": 1.5, "escala_txt": "1,5:1",
            "resumen": [
                ("Diámetro exterior de tapa", "Ø33,98 mm"),
                ("Espesor axial total", "1,51 mm (impresión 100% sólida)"),
                ("Paso central eje Transm. B", "Ø11,80 mm (holgura FDM)"),
                ("Fijación avellanada a #4", "4× Ø2,27 c/ avell. Ø3,02×90° @ DBC Ø28,32"),
            ],
            "planta": {
                "diams": [
                    (33.98, 135.0, 11.0, "", None),
                    (11.80, -140.0, 13.0, "", None),
                    {"d": 2.27, "cx": 14.16, "cy": 0.0, "ang": -20.0, "r_off": 22.0},
                    {"d": 3.02, "cx": 0.0, "cy": 14.16, "ang": 65.0, "r_off": 20.0},
                ],
                "dbcs": [(28.32, 4, 0.0, None, 45.0, None)],
                "lideres": [],
            },
            "corte": {
                "dists": [{"p1": (16.61, 0.0), "p2": (16.61, 1.51), "tipo": "DistanceY", "ax": 36.0}],
                "lideres": [((16.99, 1.1), (16.0, 14.0), "0,20×45°")],
            },
        },
        6: {
            "familia": "A", "formato": "A4", "escala": 3.0, "escala_txt": "3:1",
            "resumen": [
                ("Diámetro exterior sufridera", "Ø15,10 mm (2 unidades en -Z)"),
                ("Espesor axial total", "2,27 mm"),
                ("Paso central guía #11", "Ø7,95 mm (libre s/ roce sobre Ø6,71)"),
                ("Alojamiento O-Ring #40 (+Z)", "Escalón Ø8,90 × 1,15 mm (O-Ring 6,0×1,5)"),
                ("Fijación avellanada a #3", "4× Ø2,34 c/ avell. Ø3,02×90° @ DBC Ø11,32"),
            ],
            "planta": {
                "diams": [
                    (15.10, 135.0, 12.0, "", None),
                    (8.90, 45.0, 15.0, "", None),
                    (7.95, -140.0, 14.0, "", None),
                    {"d": 2.34, "cx": 5.66, "cy": 0.0, "ang": -15.0, "r_off": 24.0},
                    {"d": 3.02, "cx": 0.0, "cy": 5.66, "ang": 68.0, "r_off": 22.0},
                ],
                "dbcs": [(11.32, 4, 0.0, None, -45.0, None)],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (7.17, 0.0), "p2": (7.17, 2.27), "tipo": "DistanceY", "ax": 34.0},
                    {"p1": (-4.45, 0.0), "p2": (-4.45, 1.15), "tipo": "DistanceY", "ax": -34.0},
                ],
                "lideres": [((7.55, 1.8), (18.0, 14.0), "0,38×45°")],
            },
        },
        7: {
            "familia": "A", "formato": "A3", "escala": 1.0, "escala_txt": "1:1",
            "resumen": [
                ("Diámetro exterior pistón", "Ø75,72 mm (Delrin POM-C)"),
                ("Altura total del émbolo", "15,10 mm"),
                ("Garganta O-Ring 68×4,00", "Ø69,60 × 5,20 mm (fondo desde Z=4,95)"),
                ("Alojamiento núcleo CE1", "Ø22,65 pasante central"),
                ("Bujes barras guía (#11)", "2× Ø10,57 pas. @ X=±28,31 (56,62)"),
                ("Tornillos / Sensor AISI 430", "4× Ø1,86×6,04 (DBC Ø28,24) | Ø6,04@45°"),
            ],
            "planta": {
                "diams": [
                    (75.72, 25.0, 14.0, "", None),
                    (22.65, -135.0, 32.0, "", None),
                    {"d": 10.57, "cx": 28.31, "cy": 0.0, "ang": -28.0, "r_off": 32.0},
                    {"d": 6.04, "cx": 20.02, "cy": -20.02, "ang": -48.0, "r_off": 36.0},
                ],
                "dbcs": [(28.24, 4, 0.0, None, -40.0, None)],
                "dists": [
                    {"p1": (-28.31, 0.0, 7.55), "p2": (28.31, 0.0, 7.55), "tipo": "DistanceX", "oy": 50.0},
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (15.05, 0.0), "p2": (15.05, 6.04), "tipo": "DistanceY", "ax": 48.0},
                    {"p1": (37.86, 0.0), "p2": (37.86, 15.10), "tipo": "DistanceY", "ax": 60.0},
                    {"p1": (-34.80, 4.95), "p2": (-34.80, 10.15), "tipo": "DistanceY", "ax": -48.0},
                    {"p1": (-37.86, 0.0), "p2": (-37.86, 4.95), "tipo": "DistanceY", "ax": -60.0},
                    {"p1": (-34.80, 7.55), "p2": (34.80, 7.55), "tipo": "DistanceX", "oy": 18.0, "pref": "Ø"},
                    {"p1": (13.19, 15.10), "p2": (15.05, 15.10), "tipo": "DistanceX", "ay": 26.0, "pref": "Ø"},
                ],
                "lideres": [((-37.86, 14.3), (-16.0, 14.0), "0,75×45°")],
            },
        },
        8: {
            "familia": "A", "formato": "A3", "escala": 2.0, "escala_txt": "2:1",
            "x_vistas": 106.0,
            "resumen": [
                ("Brida exterior y cuello", "Ø33,98 × 3,78 | cuello Ø21,75 (H=18,72)"),
                ("Fijación a Émbolo (#7)", "4× Ø3,24 + caj. Ø5,43×0,94 @ DBC Ø28,32"),
                ("Fijación ciega a CE2 (#9)", "3× Ø2,20×6,00 @ DBC Ø15,86 (90°/210°/330°)"),
                ("Rosca trapecial 90° int.", "p=3,00 | Ø11,40 máx. / Ø9,70 mín. (h=0,85)"),
                ("Entrada de rosca / aristas", "Chaflán entrada 1,20×45° | ext. 0,38×45°"),
            ],
            "planta": {
                "diams": [
                    (33.98, -40.0, 12.0, "", None),
                    (21.75, 45.0, 22.0, "", None),
                    (9.70, -140.0, 40.0, "", None),
                    {"d": 3.24, "cx": 14.16, "cy": 0.0, "ang": -20.0, "r_off": 24.0},
                    {"d": 2.20, "cx": 0.0, "cy": -7.93, "ang": -75.0, "r_off": 42.0},
                ],
                "dbcs": [
                    (28.32, 4, 0.0, None, 32.0, None),
                    (15.86, 3, 90.0, None, 130.0, None, 0.0, 0.0, 30.0),
                ],
                "angulos": [
                    {"a1": 90.0, "a2": 210.0, "r_in": 4.0, "r_out": 10.5, "r_papel": 28.0},
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (16.88, 0.0), "p2": (16.88, 0.94), "tipo": "DistanceY", "ax": 46.0},
                    {"p1": (10.495, 18.72), "p2": (16.61, 0.0), "tipo": "DistanceY", "ax": 58.0},
                    {"p1": (-16.61, 0.0), "p2": (-16.61, 3.78), "tipo": "DistanceY", "ax": -46.0},
                    {"p1": (-5.70, 9.0), "p2": (5.70, 9.0), "tipo": "DistanceX", "oy": 28.0, "pref": "Ø"},
                ],
                "lideres": [
                    ((5.2, 1.2), (-20.0, -20.0), "1,20×45°"),
                    ((-16.61, 18.34), (-22.0, 14.0), "0,38×45°"),
                ],
                "detalles": [{
                    "ref": "B", "x": 208.0, "y": 214.0, "radio": 4.2, "escala": 4.0,
                    "anchor_rz": (5.1, 9.0),
                    "cotas": [
                        {"p1_rz": (4.85, 7.50), "p2_rz": (4.85, 10.50), "tipo": "DistanceY", "ox": -22.0},
                        {"p1_rz": (4.85, 9.00), "p2_rz": (5.70, 9.00), "tipo": "DistanceX", "ay": 26.0},
                    ],
                    "lideres": [],
                }],
            },
        },
        9: {
            "familia": "A", "formato": "A4", "escala": 1.5, "escala_txt": "1,5:1",
            "resumen": [
                ("Diámetro exterior tapa CE2", "Ø33,98 mm"),
                ("Espesor total de brida", "3,78 mm"),
                ("Paso central de eje sinfín", "Ø11,32 pasante"),
                ("Fijación a CE1 (#8)", "3× Ø2,64 avell. Ø3,77×90° @ DBC Ø15,86 (120°)"),
            ],
            "planta": {
                "diams": [
                    (33.98, -40.0, 12.0, "", None),
                    (11.32, 125.0, 30.0, "", None),
                    {"d": 2.64, "cx": 0.0, "cy": -7.93, "ang": -115.0, "r_off": 28.0},
                    {"d": 3.77, "cx": 6.87, "cy": 3.97, "ang": 25.0, "r_off": 26.0},
                ],
                "dbcs": [(15.86, 3, 90.0, None, -140.0, None, 0.0, 0.0, 24.0)],
                "angulos": [
                    {"a1": 90.0, "a2": 210.0, "r_in": 3.5, "r_out": 10.5, "r_papel": 17.5},
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [{"p1": (16.99, 0.0), "p2": (16.99, 3.78), "tipo": "DistanceY", "ax": 36.0}],
                "lideres": [((16.99, 3.4), (16.0, 16.0), "0,38×45°")],
            },
        },
        10: {
            "familia": "B", "formato": "A4", "escala": 3.0, "escala_txt": "3:1",
            "titulo_y": 191.0,
            "resumen": [
                ("Material magnético obligatorio", "Acero Inox. Ferrítico AISI 430"),
                ("Cabeza sensora", "Ø15,10 × 5,29 mm (Z=0 – 5,29)"),
                ("Espiga de montaje en émbolo", "Ø6,04 × 6,03 mm (Z=5,29 – 11,32)"),
                ("Longitud total / chaflanes", "11,32 mm | aristas 0,38×45°"),
            ],
            "corte": {
                "dists": [
                    {"p1": (7.55, 0.0), "p2": (7.55, 11.32), "tipo": "DistanceX", "ay": -34.0},
                    {"p1": (-7.55, 0.0), "p2": (-7.55, 5.29), "tipo": "DistanceX", "ay": 32.0},
                    {"p1": (-7.55, 2.6), "p2": (7.55, 2.6), "tipo": "DistanceY", "ox": -18.0, "pref": "Ø"},
                    {"p1": (-3.02, 8.5), "p2": (3.02, 8.5), "tipo": "DistanceY", "ox": 18.0, "pref": "Ø"},
                ],
                "lideres": [((-3.02, 10.95), (18.0, 22.0), "0,38×45°")],
            },
            "planta": {
                "diams": [],
            },
        },
        11: {
            "familia": "B", "formato": "A3", "escala": 1.0, "escala_txt": "1:1",
            "x_vistas": 144.0,
            "titulo_y": 250.0,
            "sin_planta": True,
            "resumen": [
                ("Cuerpo guía cilíndrico", "Ø8,22 × 198,00 mm (Z=22,65 – 220,65)"),
                ("Espiga reducida lado tapa", "Ø6,71 × 22,65 mm (hasta hombro Z=22,65)"),
                ("Tope axial de montaje", "Hombro Ø8,22 → Ø6,71 apoya en #3/#6"),
                ("Longitud total varilla", "220,65 mm (Acero Inox. 304/316L)"),
                ("Rosca extremo para Tuerca #31", "Ø6,71 × p=1,25 × 9,82 (Ø núcl. 5,47; h=0,62)"),
            ],
            "corte": {
                "dists": [
                    {"p1": (4.11, 0.0), "p2": (4.11, 220.65), "tipo": "DistanceX", "oy": -22.0},
                    {"p1": (-4.11, 0.0), "p2": (-4.11, 22.65), "tipo": "DistanceX", "oy": 24.0},
                    {"p1": (-4.11, 130.0), "p2": (4.11, 130.0), "tipo": "DistanceY", "ox": 0.0, "ay": 18.0, "pref": "Ø"},
                ],
                "lideres": [((-4.11, 219.9), (-26.0, 22.0), "0,76×45°")],
                "detalles": [{
                    "ref": "B", "x": 134.0, "y": 94.0, "radio": 16.5, "escala": 4.0,
                    "anchor_rz": (0.0, 14.0),
                    "rosca_cosm": [{"z_ini": 0.0, "z_fin": 9.82, "d_mayor": 6.71, "d_menor": 5.47, "tipo": "externa"}],
                    "cotas": [
                        {"p1_rz": (-3.355, 0.0), "p2_rz": (-3.355, 9.82), "tipo": "DistanceX", "ay": 41.0},
                        {"p1_rz": (4.11, 0.0), "p2_rz": (4.11, 22.65), "tipo": "DistanceX", "oy": -28.0},
                        {"p1_rz": (-3.355, 16.0), "p2_rz": (3.355, 16.0), "tipo": "DistanceY", "ax": 54.0, "ay": 0.0, "pref": "Ø"},
                        {"p1_rz": (-2.735, 3.45), "p2_rz": (2.735, 3.45), "tipo": "DistanceY", "ax": -78.0, "ay": 0.0, "pref": "Ø"},
                        {"p1_rz": (3.355, 3.11), "p2_rz": (3.355, 4.36), "tipo": "DistanceX", "ay": 26.0},
                    ],
                    "lideres": [((-3.355, 0.38), (-24.0, -28.0), "0,38×45°")],
                }],
            },
        },
        12: {
            "familia": "B", "formato": "A3", "escala": 2.0, "escala_txt": "2:1",
            "x_vistas": 128.0,
            "titulo_y": 240.0,
            "sin_planta": True,
            "breakouts": [(41.5, 96.2)],
            "resumen": [
                ("Longitud total eje Transm. A", "95,89 mm (AISI 304/316L)"),
                ("Espiga acoplamiento motor", "Ø6,04 × 11,33 mm (Z=0 – 11,33)"),
                ("Tramo intermedio escalonado", "Ø7,55 × 24,15 mm (hasta Z=35,48)"),
                ("Camisa exterior / aloj. int.", "Ø15,10 × 60,41 | ciego Ø9,06 × 50,59"),
                ("Pasadores transversales (Y)", "2× Ø3,02 mm @ 10,95 y 44,93 de boca"),
            ],
            "corte": {
                "diams": [
                    {"d": 3.02, "vista": "sec", "cx": 3.02, "cy": 0.0, "ang": 115.0, "r_off": 24.0},
                ],
                "dists": [
                    {"p1": (7.55, 0.0), "p2": (7.55, 95.89), "tipo": "DistanceX", "ay": -40.0},
                    {"p1": (-3.02, 0.0), "p2": (-3.02, 11.33), "tipo": "DistanceX", "ay": 20.0},
                    {"p1": (3.775, 0.0), "p2": (3.775, 35.48), "tipo": "DistanceX", "ay": 28.0},
                    {"p1": (-4.53, 45.30), "p2": (-4.53, 95.89), "tipo": "DistanceX", "ay": 28.0},
                    {"p1": (1.51, 84.94), "p2": (1.51, 95.89), "tipo": "DistanceX", "ay": -20.0},
                    {"p1": (1.51, 50.96), "p2": (1.51, 95.89), "tipo": "DistanceX", "ay": -28.0},
                    {"p1": (-3.02, 5.5), "p2": (3.02, 5.5), "tipo": "DistanceY", "ox": 0.0, "ay": -20.0, "pref": "Ø"},
                    {"p1": (-3.775, 23.0), "p2": (3.775, 23.0), "tipo": "DistanceY", "ox": 0.0, "ay": -20.0, "pref": "Ø"},
                    {"p1": (-7.55, 95.51), "p2": (7.55, 95.51), "tipo": "DistanceY", "ox": 24.0, "pref": "Ø"},
                    {"p1": (-4.53, 95.51), "p2": (4.53, 95.51), "tipo": "DistanceY", "ox": 12.0, "pref": "Ø"},
                ],
                "lideres": [((-7.55, 95.5), (-18.0, 22.0), "0,38×45°")],
            },
        },
        13: {
            "familia": "B", "formato": "A3", "escala": 2.0, "escala_txt": "2:1",
            "x_vistas": 144.0,
            "titulo_y": 244.0,
            "sin_planta": True,
            "resumen": [
                ("Longitud total eje Transm. B", "95,82 mm (macizo AISI 304/316L)"),
                ("Vástago izquierdo / cuello #28", "Ø9,06 (0 – 50,58) | Ø9,81 (50,58 – 54,36)"),
                ("Cuerpo central y pista retén", "Ø11,32 (54,36 – 70,22) | Ø10,57 (70,22 – 84,56)"),
                ("Espiga derecha acople CE1", "Ø6,02 × 11,26 mm (84,56 – 95,82)"),
                ("Terminación pista retén #25", "Ra ≤ 0,4 μm rectificado (zona Ø10,57)"),
                ("Pasadores transversales (Y)", "3× Ø3,02 mm @ Z=5,66 | 39,64 | 90,22"),
            ],
            "corte": {
                "diams": [
                    {"d": 3.02, "vista": "sec", "cx": -8.27, "cy": 0.0, "ang": 132.0, "r_off": 25.0},
                ],
                "dists": [
                    {"p1": (5.66, 0.0), "p2": (5.66, 95.82), "tipo": "DistanceX", "oy": -40.0},
                    {"p1": (-4.53, 0.0), "p2": (-4.53, 50.58), "tipo": "DistanceX", "oy": 18.0},
                    {"p1": (-4.905, 0.0), "p2": (-4.905, 54.36), "tipo": "DistanceX", "oy": 25.0},
                    {"p1": (-5.66, 0.0), "p2": (-5.66, 70.22), "tipo": "DistanceX", "oy": 32.0},
                    {"p1": (-5.285, 0.0), "p2": (-5.285, 84.56), "tipo": "DistanceX", "oy": 39.0},
                    {"p1": (0.0, 0.0), "p2": (0.0, 5.66), "tipo": "DistanceX", "oy": -18.0},
                    {"p1": (0.0, 0.0), "p2": (0.0, 39.64), "tipo": "DistanceX", "oy": -25.0},
                    {"p1": (0.0, 0.0), "p2": (0.0, 90.22), "tipo": "DistanceX", "oy": -32.0},
                    {"p1": (-4.53, 0.0), "p2": (4.53, 0.0), "tipo": "DistanceY", "ox": -12.0, "pref": "Ø"},
                    {"p1": (-4.905, 50.58), "p2": (4.905, 50.58), "tipo": "DistanceY", "ox": 0.0, "ay": -22.5, "pref": "Ø"},
                    {"p1": (-5.66, 62.0), "p2": (5.66, 62.0), "tipo": "DistanceY", "ox": 0.0, "ay": 22.0, "pref": "Ø"},
                    {"p1": (-5.285, 84.56), "p2": (5.285, 84.56), "tipo": "DistanceY", "ox": 0.0, "ay": 22.0, "pref": "Ø"},
                    {"p1": (-3.01, 95.82), "p2": (3.01, 95.82), "tipo": "DistanceY", "ox": 11.0, "pref": "Ø"},
                ],
                "lideres": [((3.01, 95.44), (16.0, 22.0), "0,38×45°")],
            },
        },
        14: {
            "familia": "B", "formato": "A3", "escala": 1.0, "escala_txt": "1:1",
            "titulo_y": 256.0,
            "sin_planta": True,
            "breakouts": [(-0.4, 13.8)],
            "resumen": [
                ("Longitud total tornillo sin fin", "192,15 mm (PLA+ / PETG 3D)"),
                ("Rosca trapecial 90° (p=3,00)", "Ø10,50 ext. / Ø8,80 núcl. (Z=14 – 179)"),
                ("Geometría hélice / cresta", "h=0,85 | cresta 0,60 | fondo 0,90"),
                ("Alojamiento ciego izquierdo", "Ø6,49 × 11,32 + pasador Ø3,45 @ Z=5,68"),
                ("Espiga inf. unificada (Op. 2)", "Ø8,80 × 13,15 mm (Z=179,00 – 192,15)"),
            ],
            "corte": {
                "diams": [
                    {"d": 3.45, "vista": "break_0", "cx": -1.32, "cy": 0.0, "ang": -130.0, "r_off": 18.0},
                ],
                "dists": [
                    {"p1": (5.25, 0.0), "p2": (5.25, 192.15), "tipo": "DistanceX", "ay": -22.0},
                    {"p1": (-5.25, 0.0), "p2": (-5.25, 14.00), "tipo": "DistanceX", "oy": 20.0},
                    {"p1": (-5.25, 14.00), "p2": (-5.25, 179.00), "tipo": "DistanceX", "oy": 20.0},
                    {"p1": (-5.25, 165.0), "p2": (5.25, 165.0), "tipo": "DistanceY", "ox": 0.0, "ay": -24.0, "pref": "Ø"},
                ],
                "lideres": [],
                "detalles": [
                    {
                        "ref": "B", "x": 78.0, "y": 92.0, "radio": 13.0, "escala": 3.0,
                        "anchor_rz": (0.0, 9.0),
                        "cotas": [
                            {"p1_rz": (3.245, 0.0), "p2_rz": (3.245, 11.32), "tipo": "DistanceX", "ay": -24.0},
                            {"p1_rz": (-3.245, 0.0), "p2_rz": (-3.245, 5.68), "tipo": "DistanceX", "ay": 33.0},
                            {"p1_rz": (-3.245, 0.0), "p2_rz": (3.245, 0.0), "tipo": "DistanceY", "ax": -46.0, "pref": "Ø"},
                            {"p1_rz": (5.25, 15.20), "p2_rz": (5.25, 18.20), "tipo": "DistanceX", "ay": 26.0},
                            {"p1_rz": (4.40, 14.32), "p2_rz": (5.25, 15.20), "tipo": "DistanceY", "ax": 44.0},
                        ],
                        "lideres": [],
                    },
                    {
                        "ref": "C", "x": 194.0, "y": 92.0, "radio": 12.0, "escala": 3.0,
                        "anchor_rz": (0.0, 184.0),
                        "cotas": [
                            {"p1_rz": (-4.40, 179.00), "p2_rz": (-4.40, 192.15), "tipo": "DistanceX", "oy": 26.0},
                            {"p1_rz": (-4.40, 192.15), "p2_rz": (4.40, 192.15), "tipo": "DistanceY", "ox": 22.0, "pref": "Ø"},
                        ],
                        "lideres": [],
                    },
                ],
            },
        },
        15: {
            "familia": "A", "formato": "A4", "escala": 1.25, "escala_txt": "1,25:1",
            "extra_y_titulo": 26.0,
            "resumen": [
                ("Brida y cuello adaptador", "Ø41,52 × 3,78 | cuello Ø30,20 (H=19,25)"),
                ("Garganta O-Ring / centrado", "Ø28,31 × 2,16 mm (Z=6,66 – 8,82)"),
                ("Cavidad rodamiento SKF 609", "Ø24,40 × 7,60 (tope axial a Z=11,65)"),
                ("Paso eje superior / O-Ring", "Ø15,60 mm (Z=0 – 11,65)"),
                ("Fijación avellanada a #17", "4× Ø2,34 avell. Ø3,02×90° @ DBC Ø37,00"),
            ],
            "planta": {
                "diams": [
                    (41.52, 115.0, 10.0, "", None),
                    (30.20, 55.0, 14.0, "", None),
                    (15.60, 155.0, 24.0, "", None),
                    {"d": 2.34, "cx": 18.50, "cy": 0.0, "ang": 18.0, "r_off": 24.0},
                ],
                "dbcs": [(37.00, 4, 0.0, None, -135.0, None, 0.0, 0.0, 18.0)],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (14.155, 6.66), "p2": (14.155, 8.82), "tipo": "DistanceY", "ax": 34.0},
                    {"p1": (14.155, 0.0), "p2": (14.155, 6.66), "tipo": "DistanceY", "ax": 45.0},
                    {"p1": (14.72, 0.0), "p2": (14.72, 19.25), "tipo": "DistanceY", "ax": 56.0},
                    {"p1": (-20.39, 0.0), "p2": (-20.39, 3.78), "tipo": "DistanceY", "ax": -33.0},
                    {"p1": (-12.20, 11.65), "p2": (-12.20, 19.25), "tipo": "DistanceY", "ax": -43.0},
                    {"p1": (-14.155, 7.74), "p2": (14.155, 7.74), "tipo": "DistanceX", "ay": -20.0, "pref": "Ø"},
                    {"p1": (-12.20, 18.99), "p2": (12.20, 18.99), "tipo": "DistanceX", "ay": 21.0, "pref": "Ø"},
                    {"p1": (16.99, 0.0), "p2": (20.01, 0.0), "tipo": "DistanceX", "ay": 21.0, "pref": "Ø"},
                ],
                "lideres": [((-20.39, 3.4), (-6.0, 30.0), "0,38×45°")],
            },
        },
        16: {
            "familia": "A", "formato": "A4", "escala": 1.5, "escala_txt": "1,5:1",
            "resumen": [
                ("Brida exterior y saliente", "Ø30,20 × 3,77 | cuello Ø13,59 (H=9,82)"),
                ("Paso eje unificado (Op. 2)", "Ø9,20 pasante (espiga Ø8,80 + holg. 0,40)"),
                ("Fijación avellanada a #1", "4× Ø2,64 avell. Ø3,78×90° @ DBC Ø21,90"),
            ],
            "planta": {
                "diams": [
                    (30.20, 135.0, 12.0, "", None),
                    (13.59, 45.0, 14.0, "", None),
                    (9.20, -140.0, 24.0, "", None),
                    {"d": 2.64, "cx": 10.95, "cy": 0.0, "ang": 20.0, "r_off": 24.0},
                ],
                "dbcs": [(21.90, 4, 0.0, None, -45.0, None)],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (14.72, 0.0), "p2": (14.72, 9.815), "tipo": "DistanceY", "ax": 38.0},
                    {"p1": (-14.72, 0.0), "p2": (-14.72, 3.77), "tipo": "DistanceY", "ax": -34.0},
                    {"p1": (-4.60, 0.0), "p2": (4.60, 0.0), "tipo": "DistanceX", "ay": 20.0, "pref": "Ø"},
                    {"p1": (-12.84, 0.0), "p2": (-9.06, 0.0), "tipo": "DistanceX", "ay": 14.0, "pref": "Ø"},
                ],
                "lideres": [((15.10, 3.4), (24.0, 16.0), "0,38×45°")],
            },
        },
        17: {
            "familia": "A", "formato": "A3", "escala": 1.5, "escala_txt": "1,5:1",
            "x_vistas": 106.0,
            "resumen": [
                ("Cuerpo cilíndrico y altura", "Ø43,03 × 12,46 mm | paso int. Ø30,28 mm"),
                ("Escotaduras despeje #31", "2× muescas Ø15,60 @ X=±28,31 (56,62)"),
                ("Patrón fijación a #3 (±45°)", "4× pas. Ø2,40 + caj. Ø4,10×3,00 @ DBC Ø37,76"),
                ("Patrón ciego a #15 (22,5°)", "4× piloto M2 Ø1,85 × 6,50 (+Z) @ DBC Ø37,00"),
            ],
            "planta": {
                "diams": [
                    (43.03, -45.0, 14.0, "", None),
                    (30.28, 140.0, 24.0, "", None),
                    {"d": 15.60, "cx": 28.31, "cy": 0.0, "ang": -12.0, "r_off": 24.0, "min_arc": 30.0},
                    {"d": 4.10, "cx": -13.35, "cy": 13.35, "ang": 122.0, "r_off": 36.0},
                    {"d": 2.40, "cx": 13.35, "cy": -13.35, "ang": -52.0, "r_off": 36.0},
                    {"d": 1.85, "cx": 7.08, "cy": -17.09, "ang": -72.0, "r_off": 38.0},
                ],
                "dbcs": [(37.76, 4, 45.0, None, 24.0, None, 0.0, 0.0, 20.0)],
                "marcas_corte": [
                    {"pts": [(-28.0, -28.0), (28.0, 28.0)], "letra": "B", "vec": (-0.7071, 0.7071), "lbl_pos": [(-24.0, -30.0), (30.0, 24.0)]},
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (21.515, 0.0), "p2": (21.515, 12.46), "tipo": "DistanceY", "ax": 44.0},
                ],
                "lideres": [((-20.51, 6.23), (-20.0, 18.0), "0,38×45°")],
                "aux_sec": {
                    "ref": "B", "x": 212.0, "y": 212.0, "escala": 1.5,
                    "dir": (0.70710678, -0.70710678, 0.0),
                    "xdir": (0.70710678, 0.70710678, 0.0),
                    "normal": (0.70710678, -0.70710678, 0.0),
                    "titulo": "SECCIÓN B - B (1,5:1)",
                    "dists": [
                        {"pt1_3d": (14.80, 14.80, 9.46), "pt2_3d": (14.80, 14.80, 12.46), "tipo": "DistanceY", "ox": 16.0},
                        {"pt1_3d": (11.90, 11.90, 12.46), "pt2_3d": (14.80, 14.80, 12.46), "tipo": "DistanceX", "oy": 11.0, "pref": "Ø"},
                        {"pt1_3d": (12.50, 12.50, 0.0), "pt2_3d": (14.20, 14.20, 0.0), "tipo": "DistanceX", "oy": -16.0, "pref": "Ø"},
                    ],
                    "lideres_3d": [],
                },
            },
        },
        18: {
            "familia": "A", "formato": "A3", "escala": 1.0, "escala_txt": "1:1",
            "resumen": [
                ("Diámetro exterior anillo prensa", "Ø105,70 mm (2 unidades: en #1 y #3)"),
                ("Diámetro interior pasante", "Ø84,18 mm"),
                ("Espesor axial total", "3,78 mm"),
                ("Fijación avellanada", "4× Ø2,34 avell. Ø2,64×90° @ DBC Ø98,16"),
            ],
            "planta": {
                "diams": [
                    (105.70, -40.0, 14.0, "", None),
                    (84.18, 145.0, 26.0, "", None),
                    {"d": 2.34, "cx": 0.0, "cy": 49.08, "ang": 58.0, "r_off": 24.0},
                ],
                "dbcs": [(98.16, 4, 0.0, None, 40.0, None)],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (52.85, 0.0), "p2": (52.85, 3.78), "tipo": "DistanceY", "ox": 16.0},
                    {"p1": (47.75, 0.0), "p2": (50.40, 0.0), "tipo": "DistanceX", "ay": 16.0, "pref": "Ø"},
                ],
                "lideres": [((-52.85, 3.4), (-18.0, 12.0), "0,38×45°")],
            },
        },
        19: {
            "familia": "A", "formato": "A3", "escala": 0.85, "escala_txt": "1:1,2",
            "resumen": [
                ("Placa cuadrada exterior", "138,17 × 138,17 × 15,10 mm"),
                ("Escalón centrado / paso int.", "Ø121,18 × 5,66 | pasante Ø109,55"),
                ("Paso de 4 tensores (#21/#22)", "4× Ø16,69 en cuadrado 108,72 × 108,72"),
                ("Fijación ciega a Tapa #3", "4× Ø2,64 × 9,44 @ DBC Ø115,20 (0°/90°)"),
                ("Fijación pasante a Cierre #20", "4× Ø3,12 @ DBC Ø127,80 (desfase 35°)"),
            ],
            "planta": {
                "diams": [
                    (121.18, -25.0, 26.0, "", None),
                    (109.55, 160.0, 28.0, "", None),
                    {"d": 16.69, "cx": 54.36, "cy": 54.36, "ang": 45.0, "r_off": 18.0},
                    {"d": 2.64, "cx": 0.0, "cy": -57.58, "ang": 115.0, "r_off": 22.0},
                    {"d": 3.12, "cx": 52.34, "cy": -36.65, "ang": -22.0, "r_off": 24.0},
                ],
                "dbcs": [
                    (127.80, 4, 35.0, None, -155.0, None, 0.0, 0.0, 24.0),
                    (115.20, 4, 0.0, None, 15.0, None, 0.0, 0.0, 24.0),
                ],
                "angulos": [
                    {"a1": 0.0, "a2": 35.0, "r_in": 24.0, "r_out": 46.0, "r_papel": 40.0},
                ],
                "dists": [
                    {"p1": (-69.085, 0.0, 7.55), "p2": (69.085, 0.0, 7.55), "tipo": "DistanceX", "ay": 64.0},
                    {"p1": (0.0, -69.085, 7.55), "p2": (0.0, 69.085, 7.55), "tipo": "DistanceY", "ax": -84.0},
                    {"p1": (-54.36, -54.36, 7.55), "p2": (54.36, -54.36, 7.55), "tipo": "DistanceX", "ay": -64.5},
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (56.26, 0.0), "p2": (56.26, 9.44), "tipo": "DistanceY", "ax": 72.0},
                    {"p1": (69.085, 0.0), "p2": (69.085, 15.10), "tipo": "DistanceY", "ax": 84.0},
                    {"p1": (-60.59, 9.44), "p2": (-60.59, 15.10), "tipo": "DistanceY", "ax": -72.0},
                    {"p1": (-60.59, 14.72), "p2": (60.59, 14.72), "tipo": "DistanceX", "ay": 20.0, "pref": "Ø"},
                    {"p1": (-54.775, 4.5), "p2": (54.775, 4.5), "tipo": "DistanceX", "ay": -20.0, "pref": "Ø"},
                ],
                "lideres": [
                    ((69.085, 14.3), (38.0, 18.0), "0,75×45°"),
                    ((-60.59, 14.72), (-20.0, 16.0), "0,38×45°"),
                ],
            },
        },
        20: {
            "familia": "A", "formato": "A3", "escala": 0.85, "escala_txt": "1:1,2",
            "resumen": [
                ("Diámetro exterior de cierre", "Ø133,63 mm (2 unidades)"),
                ("Altura total y fondo sólido", "21,52 mm (pared de fondo 7,55 mm)"),
                ("Cajeado interior centrador", "Ø120,88 × 13,97 mm (Z=7,55 – 21,52)"),
                ("Paso interior libre", "Ø98,15 pasante"),
                ("Fijación pasante a #19", "4× Ø4,15 @ DBC Ø127,80 (0°/90°)"),
            ],
            "planta": {
                "diams": [
                    (133.63, -35.0, 14.0, "", None),
                    (98.15, 145.0, 24.0, "", None),
                    {"d": 4.15, "cx": 0.0, "cy": 63.90, "ang": 100.0, "r_off": 24.0},
                ],
                "dbcs": [(127.80, 4, 0.0, None, 25.0, None, 0.0, 0.0, 18.0)],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (66.815, 0.0), "p2": (66.815, 21.52), "tipo": "DistanceY", "ax": 70.0},
                    {"p1": (-60.44, 7.55), "p2": (-60.44, 21.52), "tipo": "DistanceY", "ax": -70.0},
                    {"p1": (-60.44, 0.0), "p2": (-60.44, 7.55), "tipo": "DistanceY", "ax": -82.0},
                    {"p1": (-60.44, 21.14), "p2": (60.44, 21.14), "tipo": "DistanceX", "ay": 22.0, "pref": "Ø"},
                ],
                "lideres": [((66.815, 21.1), (24.0, 16.0), "0,38×45°")],
            },
        },
        21: {
            "familia": "B", "formato": "A3", "escala": 1.0, "escala_txt": "1:1",
            "sin_planta": True,
            "breakouts": [(134.0, 152.2)],
            "resumen": [
                ("Longitud total tensor macho", "181,81 mm (cuerpo 151,81 + espiga 30,00)"),
                ("Cuerpo cilíndrico principal", "Ø16,61 mm (Z=0 – 151,81)"),
                ("Espiga triangular acople (#22)", "Triáng. equil. R=3,00 (lado 5,20) × 30,00"),
                ("Alojamiento ciego extremo", "Ø6,32 × 12,08 mm (para M6 #33)"),
            ],
            "corte": {
                "dists": [
                    {"p1": (8.305, -30.0), "p2": (8.305, 151.81), "tipo": "DistanceX", "oy": -25.0},
                    {"p1": (-3.00, -30.0), "p2": (-3.00, 0.0), "tipo": "DistanceX", "oy": 28.0},
                    {"p1": (-8.305, 0.0), "p2": (-8.305, 151.81), "tipo": "DistanceX", "oy": 28.0},
                    {"p1": (3.16, 139.73), "p2": (3.16, 151.81), "tipo": "DistanceX", "oy": -15.0},
                    {"p1": (-8.305, 65.0), "p2": (8.305, 65.0), "tipo": "DistanceY", "ox": 0.0, "ay": 20.0, "pref": "Ø"},
                    {"p1": (-3.16, 151.81), "p2": (3.16, 151.81), "tipo": "DistanceY", "ox": 14.0, "pref": "Ø"},
                ],
                "marcas_corte_ext": [{"pts": [(-75.9, -10.0), (-75.9, 10.0)], "letra": "B", "vec": (-1.0, 0.0), "lbl_pos": [(-69.0, -14.0), (-69.0, 14.0)]}],
                "lideres": [((8.305, 151.4), (24.0, 14.0), "0,38×45°", "None", "break_0")],
                "aux_sec": {
                    "ref": "B", "x": 134.0, "y": 100.0, "escala": 2.0,
                    "dir": (0.0, 0.0, 1.0), "xdir": (1.0, 0.0, 0.0), "normal": (0.0, 0.0, 1.0),
                    "sec_origin_z": -15.0,
                    "titulo": "SECCIÓN B - B (2:1)",
                    "tri_lado": 5.20, "tri_r": 3.00,
                    "lideres_2d": [((3.0, 0.0), (14.0, 4.0), "R=3,00")],
                },
            },
        },
        22: {
            "familia": "B", "formato": "A3", "escala": 1.5, "escala_txt": "1,5:1",
            "x_vistas": 144.0,
            "titulo_y": 258.0,
            "sin_planta": True,
            "breakouts": [(-0.4, 16.0), (105.0, 139.5)],
            "resumen": [
                ("Longitud total tensor hembra", "139,09 mm"),
                ("Cuerpo / espiga de encastre", "Ø18,12 | escalón Ø16,61 × 14,35 mm"),
                ("Alojamiento ciego izquierdo", "Ø6,32 × 12,08 mm (para M6 #33)"),
                ("Cavidad triangular hembra", "Triáng. equil. R=3,25 (lado 5,63) × 30,00"),
            ],
            "corte": {
                "dists": [
                    {"p1": (9.06, 0.0), "p2": (9.06, 139.09), "tipo": "DistanceX", "oy": -28.0},
                    {"p1": (-8.305, 0.0), "p2": (-8.305, 14.35), "tipo": "DistanceX", "ay": 22.0},
                    {"p1": (3.16, 0.0), "p2": (3.16, 12.08), "tipo": "DistanceX", "oy": -19.0},
                    {"p1": (-3.25, 109.09), "p2": (-3.25, 139.09), "tipo": "DistanceX", "oy": 24.0},
                    {"p1": (-8.305, 7.0), "p2": (8.305, 7.0), "tipo": "DistanceY", "ox": 0.0, "ay": 42.0, "pref": "Ø"},
                    {"p1": (-9.06, 70.0), "p2": (9.06, 70.0), "tipo": "DistanceY", "ox": 0.0, "ay": 26.0, "pref": "Ø"},
                    {"p1": (-3.16, 6.0), "p2": (3.16, 6.0), "tipo": "DistanceY", "ox": 0.0, "ay": -38.0, "pref": "Ø"},
                ],
                "lideres": [((9.06, 138.7), (20.0, 14.0), "0,38×45°", "None", "break_1")],
                "aux_end": {
                    "ref": "DER", "x": 134.0, "y": 100.0, "escala": 2.0,
                    "dir": (0.0, 0.0, 1.0), "xdir": (1.0, 0.0, 0.0),
                    "titulo": "VISTA LATERAL DERECHA (2:1)",
                    "tri_lado": 5.63, "tri_r": 3.25,
                    "lideres_2d": [((3.25, 0.0), (14.0, 6.0), "R=3,25")],
                },
            },
        },
        23: {
            "familia": "A", "formato": "A3", "escala": 0.70, "escala_txt": "1:1,4",
            "cut_45": True,
            "resumen": [
                ("Placa cuadrada motor superior", "138,17 × 138,17 × 7,55 mm"),
                ("Alojamiento piloto motor", "Ø30,20 mm pasante central"),
                ("Fijación motor (±45°)", "4× Ø4,15 + caj. Ø7,85×1,51 (cuadr. 35,18)"),
                ("Alojamiento 4 tensores", "4× Ø16,69 pasante (cuadr. 108,72 × 108,72)"),
                ("Corte diagonal A-A (45°)", "Sección por diagonal X=Y (+Ø16,69 / Ø7,85 / Ø30,20)"),
            ],
            "planta": {
                "diams": [
                    (30.20, 108.0, 20.0, "", None),
                    {"d": 16.69, "cx": -54.36, "cy": 54.36, "ang": 135.0, "r_off": 18.0},
                ],
                "marcas_corte": [
                    {"pts": [(-74.0, -74.0), (74.0, 74.0)], "letra": "A", "vec": (-0.7071, 0.7071), "lbl_pos": [(-68.0, -74.0), (74.0, 68.0)]},
                ],
                "dists": [
                    {"p1": (-69.085, 0.0, 3.775), "p2": (69.085, 0.0, 3.775), "tipo": "DistanceX", "oy": 62.0},
                    {"p1": (0.0, -69.085, 3.775), "p2": (0.0, 69.085, 3.775), "tipo": "DistanceY", "ox": 62.0},
                    {"p1": (-54.36, -54.36, 3.775), "p2": (54.36, -54.36, 3.775), "tipo": "DistanceX", "oy": -58.0},
                    {"p1": (-17.59, -17.59, 6.04), "p2": (17.59, -17.59, 6.04), "tipo": "DistanceX", "oy": -22.0},
                ],
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"pt1_3d": (64.77, 64.77, 0.0), "pt2_3d": (64.77, 64.77, 7.55), "tipo": "DistanceY", "ox": 18.0},
                    {"pt1_3d": (20.36, 20.36, 6.04), "pt2_3d": (20.36, 20.36, 7.55), "tipo": "DistanceY", "ox": -12.0, "ay": -11.0},
                ],
                "lideres_3d": [
                    ((64.77, 64.77, 7.2), (24.0, 18.0), "0,75×45°"),
                    ((11.68, 11.68, 7.2), (-20.0, 14.0), "0,75×45°"),
                ],
            },
        },
        31: {
            "familia": "A", "formato": "A4", "escala": 3.0, "escala_txt": "3:1",
            "resumen": [
                ("Hexágono entre caras / vértices", "13,00 mm (e=15,01 mm entre vértices)"),
                ("Altura total de tuerca", "6,00 mm (biseles 0,60×45°)"),
                ("Rosca interior FDM (Guía #11)", "Ø7,71 fondo / Ø6,47 cresta | paso p=1,25"),
                ("Holgura radial impresa", "+0,50 mm calibrada para PLA+/PETG"),
            ],
            "planta": {
                "diams": [],
                "rosca_34": 7.71,
                "hex_ec": 13.00,
                "hex_ec_ox": -40.0,
                "lideres": [],
            },
            "corte": {
                "dists": [
                    {"p1": (6.50, 0.0), "p2": (6.50, 6.00), "tipo": "DistanceY", "ax": 38.0},
                    {"p1": (-3.855, 3.0), "p2": (3.855, 3.0), "tipo": "DistanceX", "oy": 18.0, "pref": "Ø"},
                ],
                "lideres": [((6.5, 0.3), (20.0, -8.0), "0,60×45°")],
            },
        },
        32: {
            "familia": "A", "formato": "A4", "escala": 3.0, "escala_txt": "3:1",
            "resumen": [
                ("Diámetro exterior (encastre #3)", "Ø13,19 mm FDM (nom. Ø13,59 mm)"),
                ("Diámetro interior (paso guía #11)", "Ø7,60 mm FDM (nom. Ø7,20 mm)"),
                ("Espesor axial total", "4,00 mm (1,74 en #3 + 2,26 saliente)"),
                ("Chaflanes de arista", "0,40 × 45° (ext. e int.)"),
            ],
            "planta": {
                "diams": [(13.19, 135.0, 12.0, "", None), (7.60, -140.0, 14.0, "", None)],
                "lideres": [],
            },
            "corte": {
                "dists": [{"p1": (6.195, 0.0), "p2": (6.195, 4.00), "tipo": "DistanceY", "ax": 34.0}],
                "lideres": [((-6.595, 3.6), (-18.0, 14.0), "0,40×45°")],
            },
        },
    }

    def _p2d_desde_rz(vista, bb_ref, r_x, z_abs, y3=0.0):
        c_ref = bb_ref.Center
        return proyectar_a_2d_vista(App.Vector(r_x, y3, z_abs), c_ref, vista.Direction, vista.XDirection)

    def _agregar_marcas_corte_con_letras(doc_p, page_p, vista, pts_model, letra, vec_flecha, lbl_pts, nombre_pref):
        agregar_marcas_plano_corte_iram(vista, pts_model, letra=letra, vec_flecha_2d=vec_flecha)
        esc_v = float(getattr(vista, "Scale", 1.0) or 1.0)
        vx = float(vista.X.Value) if hasattr(vista.X, "Value") else float(vista.X)
        vy = float(vista.Y.Value) if hasattr(vista.Y, "Value") else float(vista.Y)
        for idx_l, (lx, ly) in enumerate(lbl_pts):
            ann = doc_p.addObject("TechDraw::DrawViewAnnotation", f"{nombre_pref}_LblCorte_{letra}_{idx_l}")
            page_p.addView(ann)
            ann.Text = [letra]
            ann.TextSize = 3.6
            ann.X = vx + float(lx) * esc_v
            ann.Y = vy + float(ly) * esc_v

    def _construir_vistas_hoja_pieza_3d(doc_p, page_p, it_num, obj_p, sh_p, spec, W_hoja, H_hoja, x_vistas, y_base_min, pat_file, grupo_fuentes):
        bb = sh_p.BoundBox
        esc = float(spec["escala"])
        esc_txt = spec["escala_txt"]
        fam = spec["familia"]
        vistas = {"obj": obj_p, "bb": bb, "subs": []}

        if fam == "A":
            h_planta = max(4.0, bb.YLength * esc)
            w_corte = max(4.0, (bb.XLength * 1.414 if spec.get("cut_45") else bb.XLength) * esc)
            h_corte = max(4.0, bb.ZLength * esc)
            pad_planta_inf = 15.0 if H_hoja < 240.0 else 18.0
            y_planta_min = y_base_min + max(pad_planta_inf + 0.5 * h_planta, 24.0)
            top_margen = 42.0 if H_hoja < 240.0 else 44.0
            y_corte_max = (H_hoja - top_margen) - 0.5 * h_corte
            if H_hoja < 240.0:
                gap_vistas = 28.0 if (h_corte + h_planta) < 82.0 else 22.0
            else:
                gap_vistas = 34.0 if (h_corte + h_planta) < 165.0 else 28.0
            altura_stack = h_corte + gap_vistas + h_planta
            espacio_col = (y_corte_max + 0.5 * h_corte) - (y_planta_min - 0.5 * h_planta)
            holgura_vert = max(0.0, 0.5 * (espacio_col - altura_stack))
            y_planta = y_planta_min + holgura_vert
            y_corte = min(y_corte_max, y_planta + 0.5 * h_planta + gap_vistas + 0.5 * h_corte)

            v_sup = doc_p.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Planta")
            page_p.addView(v_sup)
            v_sup.Source = [obj_p]
            v_sup.Direction = App.Vector(0, 0, 1)
            v_sup.XDirection = App.Vector(1, 0, 0)
            v_sup.ScaleType = "Custom"
            v_sup.Scale = esc
            v_sup.X = x_vistas
            v_sup.Y = y_planta
            v_sup.Caption = ""
            estilizar_vista_iram(v_sup, mostrar_ocultas=False, mostrar_centros=True)

            v_sec = doc_p.addObject("TechDraw::DrawViewSection", f"VP_{it_num:02d}_Corte_AA")
            page_p.addView(v_sec)
            if spec.get("cut_45"):
                vp_dum = doc_p.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Dummy_BaseA")
                vp_dum.Source = [obj_p]
                vp_dum.Direction = App.Vector(0, 0, 1)
                vp_dum.XDirection = App.Vector(1, 0, 0)
                v_sec.BaseView = vp_dum
                v_sec.Direction = App.Vector(0.70710678, -0.70710678, 0.0)
                v_sec.XDirection = App.Vector(0.70710678, 0.70710678, 0.0)
                v_sec.SectionNormal = App.Vector(0.70710678, -0.70710678, 0.0)
            else:
                v_sec.BaseView = v_sup
                v_sec.Direction = App.Vector(0, -1, 0)
                v_sec.XDirection = App.Vector(1, 0, 0)
                v_sec.SectionNormal = App.Vector(0, -1, 0)
            v_sec.Source = [obj_p]
            v_sec.SectionDirection = "Up"
            if it_num == 31:
                v_sec.SectionOrigin = App.Vector(bb.Center.x, bb.Center.y + 0.05, bb.Center.z)
            else:
                v_sec.SectionOrigin = bb.Center
            v_sec.SectionSymbol = "A"
            v_sec.SectionLineStretch = 1.0
            v_sec.ScaleType = "Custom"
            v_sec.Scale = esc
            v_sec.X = x_vistas
            v_sec.Y = y_corte
            v_sec.Caption = ""
            v_sec.FuseBeforeCut = True
            if it_num == 31:
                v_sec.CutSurfaceDisplay = "SvgHatch"
                v_sec.HatchScale = 1.0
            else:
                v_sec.CutSurfaceDisplay = "PatHatch"
                if pat_file:
                    v_sec.FileGeomPattern = pat_file
                    v_sec.NameGeomPattern = "Diagonal4"
                    v_sec.HatchScale = 2.0
            estilizar_vista_iram(v_sec, mostrar_ocultas=False, mostrar_centros=True)

            vistas["sup"] = v_sup
            vistas["sec"] = v_sec

            aux_cfg = spec.get("corte", {}).get("aux_sec")
            if aux_cfg:
                vp_dum_b = doc_p.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Dummy_BaseB")
                vp_dum_b.Source = [obj_p]
                vp_dum_b.Direction = App.Vector(0, 0, 1)
                vp_dum_b.XDirection = App.Vector(1, 0, 0)
                v_aux = doc_p.addObject("TechDraw::DrawViewSection", f"VP_{it_num:02d}_Corte_BB")
                page_p.addView(v_aux)
                v_aux.BaseView = vp_dum_b
                v_aux.Source = [obj_p]
                v_aux.Direction = App.Vector(*aux_cfg["dir"])
                v_aux.XDirection = App.Vector(*aux_cfg["xdir"])
                v_aux.SectionNormal = App.Vector(*aux_cfg["normal"])
                v_aux.SectionOrigin = bb.Center
                v_aux.SectionSymbol = aux_cfg["ref"]
                v_aux.ScaleType = "Custom"
                v_aux.Scale = float(aux_cfg["escala"])
                v_aux.X = float(aux_cfg["x"])
                v_aux.Y = float(aux_cfg["y"])
                v_aux.Caption = ""
                v_aux.FuseBeforeCut = True
                v_aux.CutSurfaceDisplay = "PatHatch"
                if pat_file:
                    v_aux.FileGeomPattern = pat_file
                    v_aux.NameGeomPattern = "Diagonal4"
                    v_aux.HatchScale = 2.0
                estilizar_vista_iram(v_aux, mostrar_ocultas=False, mostrar_centros=False)
                t_aux = doc_p.addObject("TechDraw::DrawViewAnnotation", f"Txt_{it_num:02d}_Aux")
                page_p.addView(t_aux)
                t_aux.Text = [aux_cfg["titulo"]]
                t_aux.TextSize = 3.2
                t_aux.X = float(aux_cfg["x"])
                t_aux.Y = float(aux_cfg["y"]) + 0.5 * bb.ZLength * float(aux_cfg["escala"]) + 16.0
                vistas["aux"] = v_aux

            for nm_t, txt_t, xt, yt, sz in [
                (f"Txt_{it_num:02d}_Corte", [f"SECCIÓN A - A ({esc_txt})"], x_vistas, min(H_hoja - 17.5, y_corte + 0.5 * h_corte + 23.0), 3.4),
                (f"Txt_{it_num:02d}_Planta", [f"VISTA SUPERIOR ({esc_txt})"], x_vistas, max(15.0 if H_hoja < 240.0 else y_base_min + 2.0, y_planta - max(0.5 * h_planta + 16.5, 22.0)), 3.1),
            ]:
                t_an = doc_p.addObject("TechDraw::DrawViewAnnotation", nm_t)
                page_p.addView(t_an)
                t_an.Text = txt_t
                t_an.TextSize = sz
                t_an.X = xt
                t_an.Y = yt
        else:
            # Familia B: ejes / varillas / tornillos horizontales (IRAM 4507: exterior macizo + corte parcial opcional)
            tiene_bajo = bool(spec.get("corte", {}).get("detalles") or spec.get("corte", {}).get("aux_sec") or spec.get("corte", {}).get("aux_end") or not spec.get("sin_planta", False))
            y_ext = (206.0 if H_hoja > 240.0 else 148.0) if tiene_bajo else (168.0 if H_hoja > 240.0 else 124.0)
            v_ext = doc_p.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Frente")
            page_p.addView(v_ext)
            v_ext.Source = [obj_p]
            v_ext.Direction = App.Vector(0, -1, 0)
            v_ext.XDirection = App.Vector(0, 0, 1)
            v_ext.ScaleType = "Custom"
            v_ext.Scale = esc
            v_ext.X = x_vistas
            v_ext.Y = y_ext
            v_ext.Caption = ""
            estilizar_vista_iram(v_ext, mostrar_ocultas=False, mostrar_centros=False)
            vistas["sec"] = v_ext

            for idx_b, (zb_a, zb_b) in enumerate(spec.get("breakouts", [])):
                sh_sub = crear_solido_corte_parcial_z(sh_p, zb_a, zb_b)
                obj_sub = doc_p.addObject("Part::Feature", f"Solido_{it_num:02d}_Break_{idx_b}")
                obj_sub.Shape = sh_sub
                if getattr(obj_sub, "ViewObject", None):
                    obj_sub.ViewObject.Visibility = False
                grupo_fuentes.addObject(obj_sub)
                vp_dum = doc_p.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_DumBreak_{idx_b}")
                vp_dum.Source = [obj_sub]
                vp_dum.Direction = App.Vector(0, 0, 1)
                vp_dum.XDirection = App.Vector(0, 0, 1)
                v_br = doc_p.addObject("TechDraw::DrawViewSection", f"VP_{it_num:02d}_Break_{idx_b}")
                page_p.addView(v_br)
                v_br.BaseView = vp_dum
                v_br.Source = [obj_sub]
                v_br.Direction = App.Vector(0, -1, 0)
                v_br.XDirection = App.Vector(0, 0, 1)
                v_br.SectionNormal = App.Vector(0, -1, 0)
                v_br.SectionOrigin = sh_sub.BoundBox.Center
                v_br.FuseBeforeCut = False
                v_br.CutSurfaceDisplay = "PatHatch"
                if pat_file:
                    v_br.FileGeomPattern = pat_file
                    v_br.NameGeomPattern = "Diagonal4"
                    v_br.HatchScale = 1.6
                v_br.ScaleType = "Custom"
                v_br.Scale = esc
                v_br.X = x_vistas
                v_br.Y = y_ext
                v_br.Caption = ""
                estilizar_vista_iram(v_br, mostrar_ocultas=False, mostrar_centros=False)
                vistas["subs"].append((v_br, sh_sub.BoundBox))

            if not spec.get("sin_planta", False):
                v_sup = doc_p.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Planta")
                page_p.addView(v_sup)
                v_sup.Source = [obj_p]
                v_sup.Direction = App.Vector(0, 0, 1)
                v_sup.XDirection = App.Vector(1, 0, 0)
                v_sup.ScaleType = "Custom"
                v_sup.Scale = esc
                v_sup.X = x_vistas
                v_sup.Y = 74.0
                v_sup.Caption = ""
                estilizar_vista_iram(v_sup, mostrar_ocultas=False, mostrar_centros=True)
                vistas["sup"] = v_sup
                t_s = doc_p.addObject("TechDraw::DrawViewAnnotation", f"Txt_{it_num:02d}_Planta")
                page_p.addView(t_s)
                t_s.Text = [f"VISTA LATERAL ({esc_txt})"]
                t_s.TextSize = 3.0
                t_s.X = x_vistas
                t_s.Y = 34.0

            aux_cfg = spec.get("corte", {}).get("aux_sec")
            if aux_cfg:
                vp_dum_b = doc_p.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_Dummy_BaseB")
                vp_dum_b.Source = [obj_p]
                vp_dum_b.Direction = App.Vector(0, -1, 0)
                vp_dum_b.XDirection = App.Vector(1, 0, 0)
                v_aux = doc_p.addObject("TechDraw::DrawViewSection", f"VP_{it_num:02d}_Corte_BB")
                page_p.addView(v_aux)
                v_aux.BaseView = vp_dum_b
                v_aux.Source = [obj_p]
                v_aux.Direction = App.Vector(*aux_cfg["dir"])
                v_aux.XDirection = App.Vector(*aux_cfg["xdir"])
                v_aux.SectionNormal = App.Vector(*aux_cfg["normal"])
                v_aux.SectionOrigin = App.Vector(bb.Center.x, bb.Center.y, aux_cfg["sec_origin_z"])
                v_aux.SectionSymbol = aux_cfg["ref"]
                v_aux.ScaleType = "Custom"
                v_aux.Scale = float(aux_cfg["escala"])
                v_aux.X = float(aux_cfg["x"])
                v_aux.Y = float(aux_cfg["y"])
                v_aux.Caption = ""
                v_aux.CutSurfaceDisplay = "PatHatch"
                if pat_file:
                    v_aux.FileGeomPattern = pat_file
                    v_aux.NameGeomPattern = "Diagonal4"
                    v_aux.HatchScale = 1.6
                estilizar_vista_iram(v_aux, mostrar_ocultas=False, mostrar_centros=True)
                t_aux = doc_p.addObject("TechDraw::DrawViewAnnotation", f"Txt_{it_num:02d}_Aux")
                page_p.addView(t_aux)
                t_aux.Text = [aux_cfg["titulo"]]
                t_aux.TextSize = 3.2
                t_aux.X = float(aux_cfg["x"])
                t_aux.Y = float(aux_cfg["y"]) + 30.0
                vistas["aux"] = v_aux

            aux_end = spec.get("corte", {}).get("aux_end")
            if aux_end:
                v_end = doc_p.addObject("TechDraw::DrawViewPart", f"VP_{it_num:02d}_LateralDer")
                page_p.addView(v_end)
                v_end.Source = [obj_p]
                v_end.Direction = App.Vector(*aux_end["dir"])
                v_end.XDirection = App.Vector(*aux_end["xdir"])
                v_end.ScaleType = "Custom"
                v_end.Scale = float(aux_end["escala"])
                v_end.X = float(aux_end["x"])
                v_end.Y = float(aux_end["y"])
                v_end.Caption = ""
                estilizar_vista_iram(v_end, mostrar_ocultas=False, mostrar_centros=True)
                t_end = doc_p.addObject("TechDraw::DrawViewAnnotation", f"Txt_{it_num:02d}_Aux")
                page_p.addView(t_end)
                t_end.Text = [aux_end["titulo"]]
                t_end.TextSize = 3.2
                t_end.X = float(aux_end["x"])
                t_end.Y = float(aux_end["y"]) + 32.0
                vistas["aux"] = v_end

            t_f = doc_p.addObject("TechDraw::DrawViewAnnotation", f"Txt_{it_num:02d}_Corte")
            page_p.addView(t_f)
            lbl_br = " (VISTA EXTERIOR + CORTE PARCIAL)" if spec.get("breakouts") else " (VISTA EXTERIOR)"
            t_f.Text = [f"ELEVACIÓN PRINCIPAL ({esc_txt}){lbl_br}"]
            t_f.TextSize = 3.3
            t_f.X = x_vistas
            t_f.Y = min(H_hoja - 17.5, y_ext + 42.0)

        return vistas

    def _acotar_hoja_pieza_3d(doc_p, page_p, it_num, vistas, spec, fmt_i):
        total = 0
        bb = vistas["bb"]
        v_sup = vistas.get("sup")
        v_sec = vistas.get("sec")
        fam = spec["familia"]

        # 1. Alinear cortes parciales en Familia B usando desplazamientos exactos de BoundBox
        if fam == "B" and v_sec and vistas["subs"]:
            vx0 = float(v_sec.X.Value)
            vy0 = float(v_sec.Y.Value)
            esc0 = float(v_sec.Scale)
            for v_br, bb_sub in vistas["subs"]:
                v_br.X = vx0 + (bb_sub.Center.z - bb.Center.z) * esc0
                v_br.Y = vy0 - (bb_sub.Center.x - bb.Center.x) * esc0
            # Trazar eje de simetría longitudinal exacto sobre eje físico (X=0, Y=0)
            p_ax1 = _p2d_desde_rz(v_sec, bb, 0.0, bb.ZMin - 4.0)
            p_ax2 = _p2d_desde_rz(v_sec, bb, 0.0, bb.ZMax + 4.0)
            try:
                v_sec.makeCosmeticLine(
                    App.Vector(p_ax1[0], p_ax1[1], 0.0),
                    App.Vector(p_ax2[0], p_ax2[1], 0.0),
                    4, 0.18, (0.0, 0.0, 0.0, 1.0),
                )
            except Exception:
                pass

        # 2. Acotación en Vista Superior / Lateral (Planta)
        if v_sup:
            pl_spec = spec.get("planta", {})
            for idx_d, d_item in enumerate(pl_spec.get("diams", [])):
                if isinstance(d_item, dict):
                    d_nom = d_item["d"]
                    ang_d = d_item.get("ang", 45.0)
                    r_off = d_item.get("r_off", 12.0)
                    pref_d = d_item.get("pref", "")
                    tol_s = d_item.get("tol_sym")
                    cx_d = d_item.get("cx", 0.0)
                    cy_d = d_item.get("cy", 0.0)
                    cant_d = d_item.get("cant", 1)
                    min_arc_d = d_item.get("min_arc")
                    suf_d = d_item.get("suf", "")
                    fmt_d = d_item.get("fmt", "%.2w")
                    tol_dd = d_item.get("tol_d", 0.16)
                    tol_cd = d_item.get("tol_c", 0.25)
                else:
                    d_nom, ang_d, r_off, pref_d, tol_s = d_item[:5]
                    cx_d = d_item[5] if len(d_item) > 5 else 0.0
                    cy_d = d_item[6] if len(d_item) > 6 else 0.0
                    cant_d = d_item[7] if len(d_item) > 7 else 1
                    min_arc_d = d_item[8] if len(d_item) > 8 else None
                    suf_d = ""
                    fmt_d = "%.2w"
                    tol_dd = 0.16
                    tol_cd = 0.25
                dm = acotar_diametro_exacto_iram(
                    doc_p, page_p, v_sup, f"Cota_{it_num:02d}_P",
                    d_nom, cx_math=cx_d, cy_math=cy_d,
                    ang_deg=ang_d, r_offset=r_off, cantidad=cant_d,
                    fmt=fmt_d, prefijo_txt=pref_d, sufijo=suf_d, tol_sym=tol_s,
                    tol_d=tol_dd, tol_c=tol_cd, min_arc_deg=min_arc_d,
                )
                if dm:
                    total += 1
            for idx_b, dbc_cfg in enumerate(pl_spec.get("dbcs", [])):
                d_dbc, n_ag, ang0, d_ag, ang_dim, txt_ag = dbc_cfg[:6]
                cx_m = dbc_cfg[6] if len(dbc_cfg) > 6 else 0.0
                cy_m = dbc_cfg[7] if len(dbc_cfg) > 7 else 0.0
                r_off_dbc = float(dbc_cfg[8]) if len(dbc_cfg) > 8 and dbc_cfg[8] is not None else 14.0
                agregar_circulo_centros_iram(v_sup, d_dbc, n_aguj=n_ag, ang_ini_deg=ang0, cx_math=cx_m, cy_math=cy_m)
                if ang_dim is not None:
                    dm_dbc = acotar_diametro_exacto_iram(
                        doc_p, page_p, v_sup, f"Cota_{it_num:02d}_DBC{idx_b}",
                        d_dbc, cx_math=cx_m, cy_math=cy_m,
                        ang_deg=ang_dim, r_offset=r_off_dbc, prefijo_txt="DBC ", forzar_diametro_cosmetico=True,
                    )
                    if dm_dbc:
                        total += 1
                if d_ag and txt_ag:
                    rad_a = math.radians(ang0)
                    pt_a = (cx_m + 0.5 * d_dbc * math.cos(rad_a), cy_m + 0.5 * d_dbc * math.sin(rad_a))
                    sx = 1.0 if pt_a[0] >= cx_m else -1.0
                    sy = 1.0 if pt_a[1] >= cy_m else -1.0
                    agregar_llamada_lider_iram(doc_p, page_p, v_sup, f"Lider_{it_num:02d}_DBC{idx_b}", pt_a, (sx * 26.0, sy * 18.0), txt_ag)
            for idx_an, ang_cfg in enumerate(pl_spec.get("angulos", [])):
                dm_an = acotar_angulo_centrado_iram(
                    doc_p, page_p, v_sup, f"Cota_{it_num:02d}_Ang{idx_an}",
                    ang_cfg["a1"], ang_cfg["a2"],
                    r_rayo_in=ang_cfg.get("r_in", 2.0),
                    r_rayo_out=ang_cfg.get("r_out", 12.0),
                    r_cota_papel=ang_cfg.get("r_papel", 18.0),
                    cx_math=ang_cfg.get("cx", 0.0),
                    cy_math=ang_cfg.get("cy", 0.0),
                )
                if dm_an:
                    total += 1
            if pl_spec.get("rosca_34"):
                crear_circulo_rosca_34_iram(v_sup, float(pl_spec["rosca_34"]))
            if pl_spec.get("hex_ec"):
                ec_half = 0.5 * float(pl_spec["hex_ec"])
                dm_ec = acotar_distancia_coords_iram(
                    doc_p, page_p, v_sup, f"Cota_{it_num:02d}_EntreCaras",
                    (0.0, -ec_half), (0.0, ec_half), tipo="DistanceY",
                    offset_x=float(pl_spec.get("hex_ec_ox", -24.0)),
                    sufijo_txt=pl_spec.get("hex_ec_suf", ""),
                )
                if dm_ec:
                    total += 1
            for idx_dt, dt in enumerate(pl_spec.get("dists", [])):
                p1_2 = proyectar_a_2d_vista(App.Vector(*dt["p1"]), bb.Center, v_sup.Direction, v_sup.XDirection)
                p2_2 = proyectar_a_2d_vista(App.Vector(*dt["p2"]), bb.Center, v_sup.Direction, v_sup.XDirection)
                dm_dt = acotar_distancia_coords_iram(
                    doc_p, page_p, v_sup, f"Cota_{it_num:02d}_PD{idx_dt}",
                    p1_2, p2_2, tipo=dt.get("tipo", "DistanceX"),
                    offset_x=dt.get("ox", 0.0), offset_y=dt.get("oy", 0.0),
                    x_abs_vista=dt.get("ax"), y_abs_vista=dt.get("ay"),
                    prefijo_txt=dt.get("pref", ""), sufijo_txt=dt.get("suf", ""),
                )
                if dm_dt:
                    total += 1
            for idx_mc, mc in enumerate(pl_spec.get("marcas_corte", [])):
                _agregar_marcas_corte_con_letras(
                    doc_p, page_p, v_sup, mc["pts"], mc["letra"], mc["vec"], mc["lbl_pos"], f"MC_{it_num:02d}_{idx_mc}"
                )
            for idx_l, (pt2, off2, txt2) in enumerate(pl_spec.get("lideres", [])):
                agregar_llamada_lider_iram(doc_p, page_p, v_sup, f"Lider_{it_num:02d}_P{idx_l}", pt2, off2, txt2)
            agregar_ejes_simetria_iram(v_sup, es_revolucion=False)

        # 3. Acotación en Sección A-A / Elevación Principal
        def _resolver_vista_ref(clave_v):
            if clave_v in ("break_0", "break_1") and vistas.get("subs"):
                idx_br = 0 if clave_v == "break_0" else 1
                if idx_br < len(vistas["subs"]):
                    return vistas["subs"][idx_br]
            if clave_v == "aux" and vistas.get("aux"):
                return vistas["aux"], bb
            if clave_v == "planta" and v_sup:
                return v_sup, bb
            return v_sec, bb

        c_spec = spec.get("corte", {})
        if v_sec:
            for idx_mc, mc in enumerate(c_spec.get("marcas_corte_ext", [])):
                _agregar_marcas_corte_con_letras(
                    doc_p, page_p, v_sec, mc["pts"], mc["letra"], mc["vec"], mc["lbl_pos"], f"MCE_{it_num:02d}_{idx_mc}"
                )
            for idx_cd, d_item in enumerate(c_spec.get("diams", [])):
                v_tgt, _ = _resolver_vista_ref(d_item.get("vista", "sec"))
                if not v_tgt:
                    continue
                dm_cd = acotar_diametro_exacto_iram(
                    doc_p, page_p, v_tgt, f"Cota_{it_num:02d}_CD",
                    d_item["d"], cx_math=d_item.get("cx", 0.0), cy_math=d_item.get("cy", 0.0),
                    ang_deg=d_item.get("ang", 45.0), r_offset=d_item.get("r_off", 14.0),
                    cantidad=d_item.get("cant", 1), fmt=d_item.get("fmt", "%.2w"),
                    prefijo_txt=d_item.get("pref", ""), sufijo=d_item.get("suf", ""),
                    tol_sym=d_item.get("tol_sym"), tol_d=d_item.get("tol_d", 0.16),
                    tol_c=d_item.get("tol_c", 0.25), min_arc_deg=d_item.get("min_arc"),
                )
                if dm_cd:
                    total += 1
            for idx_d, dcfg in enumerate(c_spec.get("dists", [])):
                if dcfg.get("lbl_only"):
                    continue
                v_tgt, bb_tgt = _resolver_vista_ref(dcfg.get("vista", "sec"))
                if not v_tgt:
                    continue
                if "p1_2d" in dcfg and "p2_2d" in dcfg:
                    q1 = tuple(dcfg["p1_2d"])
                    q2 = tuple(dcfg["p2_2d"])
                elif "pt1_3d" in dcfg:
                    q1 = proyectar_a_2d_vista(App.Vector(*dcfg["pt1_3d"]), bb_tgt.Center, v_tgt.Direction, v_tgt.XDirection)
                    q2 = proyectar_a_2d_vista(App.Vector(*dcfg["pt2_3d"]), bb_tgt.Center, v_tgt.Direction, v_tgt.XDirection)
                else:
                    r1, z1 = dcfg["p1"]
                    r2, z2 = dcfg["p2"]
                    q1 = _p2d_desde_rz(v_tgt, bb_tgt, r1, z1)
                    q2 = _p2d_desde_rz(v_tgt, bb_tgt, r2, z2)
                dm_c = acotar_distancia_coords_iram(
                    doc_p, page_p, v_tgt, f"Cota_{it_num:02d}_C{idx_d}",
                    q1, q2, tipo=dcfg.get("tipo", "DistanceY"),
                    offset_x=dcfg.get("ox", 0.0), offset_y=dcfg.get("oy", 0.0),
                    x_abs_vista=dcfg.get("ax"), y_abs_vista=dcfg.get("ay"),
                    prefijo_txt=dcfg.get("pref", ""), sufijo_txt=dcfg.get("suf", ""),
                    tol_sym=dcfg.get("tol_sym"),
                )
                if dm_c:
                    total += 1
            for idx_l, nl in enumerate(c_spec.get("lideres", [])):
                rz_pt, off_l, txt_l = nl[0], nl[1], nl[2]
                simb_l = nl[3] if len(nl) > 3 else "None"
                clave_lv = nl[4] if len(nl) > 4 else "sec"
                v_ltgt, bb_ltgt = _resolver_vista_ref(clave_lv)
                pt_2 = _p2d_desde_rz(v_ltgt, bb_ltgt, rz_pt[0], rz_pt[1])
                agregar_llamada_lider_iram(doc_p, page_p, v_ltgt, f"Lider_{it_num:02d}_C{idx_l}", pt_2, off_l, txt_l, simbolo=simb_l)
            for idx_l3, nl3 in enumerate(c_spec.get("lideres_3d", [])):
                p3, off_l, txt_l = nl3[0], nl3[1], nl3[2]
                pt_2 = proyectar_a_2d_vista(App.Vector(*p3), bb.Center, v_sec.Direction, v_sec.XDirection)
                agregar_llamada_lider_iram(doc_p, page_p, v_sec, f"Lider_{it_num:02d}_C3_{idx_l3}", pt_2, off_l, txt_l)
            if fam == "A":
                agregar_ejes_simetria_iram(v_sec, es_revolucion=True)

            # 4. Vistas de detalle específicas (IRAM 4520 / cajeras)
            for idx_dt, dtc in enumerate(c_spec.get("detalles", [])):
                anc_2d = _p2d_desde_rz(v_sec, bb, dtc["anchor_rz"][0], dtc["anchor_rz"][1])
                rc_list = []
                for rc in dtc.get("rosca_cosm", []):
                    p_ri = _p2d_desde_rz(v_sec, bb, 0.0, rc["z_ini"])
                    p_rf = _p2d_desde_rz(v_sec, bb, 0.0, rc["z_fin"])
                    rc_list.append({
                        "x_ini": p_ri[0] - anc_2d[0], "x_fin": p_rf[0] - anc_2d[0],
                        "y_c": p_ri[1] - anc_2d[1], "d_mayor": rc["d_mayor"], "d_menor": rc["d_menor"],
                        "tipo": rc.get("tipo", "externa"),
                    })
                cot_rel = []
                for cr in dtc.get("cotas", []):
                    u1 = _p2d_desde_rz(v_sec, bb, cr["p1_rz"][0], cr["p1_rz"][1])
                    u2 = _p2d_desde_rz(v_sec, bb, cr["p2_rz"][0], cr["p2_rz"][1])
                    cot_rel.append({
                        "p1": (u1[0] - anc_2d[0], u1[1] - anc_2d[1]),
                        "p2": (u2[0] - anc_2d[0], u2[1] - anc_2d[1]),
                        "tipo": cr.get("tipo", "DistanceX"),
                        "ox": cr.get("ox", 0.0), "oy": cr.get("oy", 0.0),
                        "ax": cr.get("ax"), "ay": cr.get("ay"),
                        "pref": cr.get("pref", ""), "suf": cr.get("suf", ""),
                    })
                lid_det = []
                for ld in dtc.get("lideres", []):
                    ul = _p2d_desde_rz(v_sec, bb, ld[0][0], ld[0][1])
                    lid_det.append({"pt": (ul[0] - anc_2d[0], ul[1] - anc_2d[1]), "off": ld[1], "texto": ld[2]})
                _, c_dv = crear_vista_detalle_especifico_iram(
                    doc_p, page_p, v_sec, f"VP_{it_num:02d}",
                    anchor_point=App.Vector(anc_2d[0], anc_2d[1], 0.0),
                    x_detalle=dtc["x"], y_detalle=dtc["y"],
                    radio_corte=dtc["radio"], escala_detalle=dtc["escala"], ref_letra=dtc["ref"],
                    cotas_relativas=cot_rel, rosca_cosmetica=rc_list, notas_lider=lid_det,
                )
                total += len(c_dv)

        # 5. Vistas auxiliares o secciones B-B / Lateral derecha
        v_aux = vistas.get("aux")
        if v_aux:
            aux_cfg = c_spec.get("aux_sec") or c_spec.get("aux_end")
            if aux_cfg:
                for idx_ad, ad in enumerate(aux_cfg.get("dists", [])):
                    if ad.get("lbl_only"):
                        continue
                    q1 = proyectar_a_2d_vista(App.Vector(*ad["pt1_3d"]), bb.Center, v_aux.Direction, v_aux.XDirection)
                    q2 = proyectar_a_2d_vista(App.Vector(*ad["pt2_3d"]), bb.Center, v_aux.Direction, v_aux.XDirection)
                    dm_a = acotar_distancia_coords_iram(
                        doc_p, page_p, v_aux, f"Cota_{it_num:02d}_Aux{idx_ad}",
                        q1, q2, tipo=ad.get("tipo", "DistanceY"),
                        offset_x=ad.get("ox", 0.0), offset_y=ad.get("oy", 0.0),
                        x_abs_vista=ad.get("ax"), y_abs_vista=ad.get("ay"),
                        prefijo_txt=ad.get("pref", ""), sufijo_txt=ad.get("suf", ""),
                        tol_sym=ad.get("tol_sym"),
                    )
                    if dm_a:
                        total += 1
                for idx_al, (p3, off_a, txt_a) in enumerate(aux_cfg.get("lideres_3d", [])):
                    pt_2 = proyectar_a_2d_vista(App.Vector(*p3), bb.Center, v_aux.Direction, v_aux.XDirection)
                    agregar_llamada_lider_iram(doc_p, page_p, v_aux, f"Lider_{it_num:02d}_A3_{idx_al}", pt_2, off_a, txt_a)
                for idx_al2, (p2, off_a, txt_a) in enumerate(aux_cfg.get("lideres_2d", [])):
                    agregar_llamada_lider_iram(doc_p, page_p, v_aux, f"Lider_{it_num:02d}_A2_{idx_al2}", p2, off_a, txt_a)
                if aux_cfg.get("tri_r"):
                    esc_ax = float(v_aux.Scale)
                    try:
                        v_aux.makeCosmeticCircle(App.Vector(0.0, 0.0, 0.0), float(aux_cfg["tri_r"]), 4, 0.16, (0.0, 0.0, 0.0, 1.0))
                    except Exception:
                        pass
                    # Buscar arista recta de triángulo equilátero real para acotar su lado exacto
                    try:
                        lado_obj = float(aux_cfg["tri_lado"])
                        for i_e, ed in enumerate(v_aux.getVisibleEdges()):
                            if len(getattr(ed, "Vertexes", [])) == 2 and abs(ed.Length / esc_ax - lado_obj) <= 0.25:
                                dm_t = doc_p.addObject("TechDraw::DrawViewDimension", f"Cota_{it_num:02d}_TriLado")
                                page_p.addView(dm_t)
                                dm_t.Type = "Distance"
                                dm_t.References2D = [(v_aux, f"Edge{i_e}")]
                                dm_t.FormatSpec = aux_cfg.get("tri_fmt", "%.2w")
                                dm_t.X = 0.0
                                dm_t.Y = -26.0
                                vo_t = getattr(dm_t, "ViewObject", None)
                                if vo_t:
                                    vo_t.Fontsize = 3.0
                                    vo_t.Color = (0.0, 0.0, 0.0)
                                total += 1
                                break
                    except Exception:
                        pass
                agregar_ejes_simetria_iram(v_aux, es_revolucion=False)

        return total

    num_hoja_actual = 5
    piezas_meta = {}
    vistas_piezas = {}
    for entrada in CATALOGO_ITEMS_BOM_3D:
        if entrada.get("es_comercial") or entrada.get("es_buloneria"):
            continue

        it_num = entrada["item"]
        spec = ESPECIFICACIONES_HOJAS_3D[it_num]
        info = datos_piezas[it_num]
        sh_p = info["shape"]
        masa_g = info["masa_g"]
        nombre_hoja = entrada["hoja_plano"]

        obj_p = doc_planos.addObject("Part::Feature", f"Solido_Item_{it_num:02d}")
        obj_p.Label = entrada["denominacion"]
        obj_p.Shape = sh_p
        if getattr(obj_p, "ViewObject", None):
            obj_p.ViewObject.Visibility = False
        grupo_fuentes.addObject(obj_p)

        bb = sh_p.BoundBox
        formato = spec["formato"]
        escala_num = spec["escala"]
        escala_txt = spec["escala_txt"]
        W_hoja, H_hoja = FORMATOS_IRAM[formato]
        piezas_meta[it_num] = formato

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
            x_vistas = spec.get("x_vistas", 76.0)
            x_der, ancho_tabla, font_tabla_pt = 228.0, 104.0, 5.2
            y_base_min = 44.0 if spec["familia"] == "A" else 14.0
        else:
            x_vistas = spec.get("x_vistas", 132.0)
            x_der, ancho_tabla, font_tabla_pt = 330.0, 144.0, 5.8
            y_base_min = 14.0

        H_tabla_real = estimar_altura_cuadro_html_mm(
            spec["resumen"], entrada["notas_taller"], ancho_mm=ancho_tabla, font_pt=font_tabla_pt
        )

        y_iso_min = 65.0 + H_tabla_real + 10.0
        y_iso_max = H_hoja - 14.0
        y_iso = 0.5 * (y_iso_min + y_iso_max)
        h_iso_est = max(10.0, (bb.XLength + bb.YLength) * 0.41 + bb.ZLength * 0.82)
        escala_iso = round(escala_num * 0.68, 3)
        h_iso_disp = max(18.0, (y_iso_max - y_iso_min) - 12.0)
        if h_iso_est * escala_iso > h_iso_disp:
            escala_iso = round(max(0.10, h_iso_disp / h_iso_est), 3)

        vistas_piezas[it_num] = _construir_vistas_hoja_pieza_3d(
            doc_planos, page_p, it_num, obj_p, sh_p, spec, W_hoja, H_hoja, x_vistas, y_base_min, pat_file, grupo_fuentes
        )

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

        t_iso = doc_planos.addObject("TechDraw::DrawViewAnnotation", f"Txt_{it_num:02d}_Iso")
        page_p.addView(t_iso)
        t_iso.Text = ["PERSPECTIVA ISOMÉTRICA"]
        t_iso.TextSize = 3.1
        t_iso.X = x_der
        t_iso.Y = min(H_hoja - 17.0, y_iso + 0.5 * h_iso_disp + 3.0)

        crear_cuadro_cotas_editable_iram(
            doc_planos,
            page_p,
            f"VP_{it_num:02d}_Cuadro_Cotas",
            spec["resumen"],
            entrada["notas_taller"],
            ancho_mm=ancho_tabla,
            x_centro=x_der,
            y_base_min=65.0,
            font_pt=font_tabla_pt,
        )

        num_hoja_actual += 1

    # 4. Recomputar vistas HLR antes de medir y acotar (esperando hilos HLR pesados como V00a_Frente)
    print(f"Calculando proyecciones HLR de las {total_hojas} láminas IRAM 3D...")
    doc_planos.recompute()
    import time as _time_hlr
    _vistas_hlr = [
        v for v in doc_planos.Objects
        if hasattr(v, "getVisibleEdges") and getattr(v, "InList", [])
        and "Dummy" not in str(v.Name) and "DumBreak" not in str(v.Name)
    ]
    _t_ini_hlr = _time_hlr.time()
    _hlr_timeout = 60.0 if App.GuiUp else 8.0
    while _time_hlr.time() - _t_ini_hlr < _hlr_timeout:
        if all(len(v.getVisibleEdges()) > 0 for v in _vistas_hlr):
            break
        if App.GuiUp:
            try:
                import FreeCADGui as Gui
                Gui.updateGui()
            except Exception:
                pass
        else:
            doc_planos.recompute()
        _time_hlr.sleep(0.20)

    # Alinear con precisión analítica todas las capas del Corte A-A respecto de V00a_Frente y V00a_Corte_AA
    centro_ens = comp_ens.BoundBox.Center
    centro_a = obj_ens_a.Shape.BoundBox.Center
    centro_b = obj_ens_b.Shape.BoundBox.Center
    centro_rod = obj_ens_rod.Shape.BoundBox.Center
    centro_ejes = obj_ens_ejes.Shape.BoundBox.Center

    v_arm_corte.Y = float(v_arm_frente.Y.Value) + (centro_a.z - centro_ens.z) * 0.5
    vx_corte = float(v_arm_corte.X.Value)
    vy_corte = float(v_arm_corte.Y.Value)
    for v_cap, c_cap in (
        (v_arm_corte_b, centro_b),
        (v_arm_corte_rod, centro_rod),
        (v_arm_corte_ejes, centro_ejes),
    ):
        v_cap.X = vx_corte + (c_cap.x - centro_a.x) * 0.5
        v_cap.Y = vy_corte + (c_cap.z - centro_a.z) * 0.5

    # Marcas de plano de corte A-A en V00a_Planta (sin superponer con cotas)
    _agregar_marcas_corte_con_letras(
        doc_planos, page_00a, v_arm_planta,
        [(-74.0, 0.0), (74.0, 0.0)], "A", (0.0, 1.0),
        [(-74.0, -7.5), (74.0, -7.5)], "MC_00a",
    )

    # Líneas cosméticas de trayectoria coaxial y de ejes de guía en Plano 00b y Plano 00d
    # Vista Explotada General 00b (eje central + ejes guía X=±28,31)
    _agregar_linea_trayectoria_3d(
        v_exp_gen, App.Vector(0, 0, -850), App.Vector(0, 0, 540), centro_gen, estilo=4, grosor=0.22
    )
    for xg in (-28.31, 28.31):
        _agregar_linea_trayectoria_3d(
            v_exp_gen, App.Vector(xg, 0, -455), App.Vector(xg, 0, 95), centro_gen, estilo=2, grosor=0.18
        )

    # Detalle A (Émbolo): eje central + ambos ejes deslizantes de guía + trayectorias radiales de sensores
    _agregar_linea_trayectoria_3d(
        v_sub_emb, App.Vector(0, 0, -40), App.Vector(0, 0, 105), centro_sub_emb, estilo=4, grosor=0.22
    )
    for xg in (-28.31, 28.31):
        _agregar_linea_trayectoria_3d(
            v_sub_emb, App.Vector(xg, 0, -30), App.Vector(xg, 0, 95), centro_sub_emb, estilo=2, grosor=0.18
        )
    _agregar_linea_trayectoria_3d(
        v_sub_emb, App.Vector(20.0, 20.0, 68.3), App.Vector(58.0, 58.0, 68.3), centro_sub_emb, estilo=2, grosor=0.20,
        color=(0.75, 0.25, 0.08, 1.0),
    )
    _agregar_linea_trayectoria_3d(
        v_sub_emb, App.Vector(-20.0, 20.0, -75.2), App.Vector(-56.0, -4.0, -75.2), centro_sub_emb, estilo=2, grosor=0.20,
        color=(0.75, 0.25, 0.08, 1.0),
    )

    # Detalle B (Tren Rotativo): eje central coaxial + trayectorias radiales de pasadores #29 y #30
    _agregar_linea_trayectoria_3d(
        v_sub_tr,
        App.Vector(0, 0, comp_sub_tr.BoundBox.ZMin - 8.0),
        App.Vector(0, 0, comp_sub_tr.BoundBox.ZMax + 8.0),
        centro_sub_tr,
        estilo=4,
        grosor=0.22,
    )
    for pa, pb in pasadores_traj:
        _agregar_linea_trayectoria_3d(
            v_sub_tr, pa, pb, centro_sub_tr, estilo=2, grosor=0.20, color=(0.75, 0.25, 0.08, 1.0)
        )

    # Plano 00d Vista A (Isométrica) y Vista B (Corte A-A): eje central y ejes de guía X=±28,31
    z_bot_00d = comp_00d.BoundBox.ZMin - 10.0
    z_top_00d = comp_00d.BoundBox.ZMax + 10.0
    for vista_00d, dir_v, xdir_v in (
        (v_00d_iso, None, None),
        (v_00d_sec, dir_sec, xdir_sec),
    ):
        _agregar_linea_trayectoria_3d(
            vista_00d,
            App.Vector(0, 0, z_bot_00d),
            App.Vector(0, 0, z_top_00d),
            centro_00d,
            direction=dir_v,
            x_direction=xdir_v,
            estilo=4,
            grosor=0.24,
        )
        for xg in (-28.31, 28.31):
            _agregar_linea_trayectoria_3d(
                vista_00d,
                App.Vector(xg, 0, anchors_00d["Guia_1_08_3D"].ZMin - 4.0),
                App.Vector(xg, 0, anchors_00d["Adaptador_Eje_04_3D"].ZMax + 8.0),
                centro_00d,
                direction=dir_v,
                x_direction=xdir_v,
                estilo=2,
                grosor=0.20,
                color=(0.75, 0.25, 0.08, 1.0),
            )

    # Plano 00d Vista C (Planta): ejes perpendiculares centrados en centro_00d
    _agregar_linea_trayectoria_3d(
        v_00d_planta,
        App.Vector(0.0, -72.0, centro_00d.z),
        App.Vector(0.0, 72.0, centro_00d.z),
        centro_00d,
        direction=dir_top,
        x_direction=xdir_top,
        estilo=4,
        grosor=0.20,
    )

    for entrada in CATALOGO_ITEMS_BOM_3D:
        if entrada.get("es_comercial") or entrada.get("es_buloneria"):
            continue
        it_num = entrada["item"]
        v_iso = doc_planos.getObject(f"VP_{it_num:02d}_Iso")
        t_iso = doc_planos.getObject(f"Txt_{it_num:02d}_Iso")
        if v_iso and t_iso:
            try:
                e_iso = v_iso.getVisibleEdges()
                if e_iso:
                    ymin_iso = min(e.BoundBox.YMin for e in e_iso)
                    ymax_iso = max(e.BoundBox.YMax for e in e_iso)
                    half_h_iso = 0.5 * (ymax_iso - ymin_iso)
                    fmt_i = piezas_meta[it_num]
                    H_i = FORMATOS_IRAM[fmt_i][1]
                    t_iso.Y = min(H_i - 17.0, float(v_iso.Y.Value) + half_h_iso + 7.5)
            except Exception:
                pass

    # Acotación normativa IRAM completa en Conjunto Armado 00a y en cada hoja individual 5..28
    total_cotas = 0
    for nm_c, vista_00a, p1_00a, p2_00a, tipo_00a, ox_00a, oy_00a in [
        ("Cota_00a_Ancho", v_arm_planta, (-69.085, 0.0), (69.085, 0.0), "DistanceX", 0.0, 44.0),
        ("Cota_00a_Prof", v_arm_planta, (0.0, -69.085), (0.0, 69.085), "DistanceY", -46.0, 0.0),
        ("Cota_00a_AltoTotal", v_arm_frente, (0.0, bb_ens.ZMin - centro_ens.z), (0.0, bb_ens.ZMax - centro_ens.z), "DistanceY", -48.0, 0.0),
    ]:
        dm_00a = acotar_distancia_coords_iram(
            doc_planos, page_00a, vista_00a, nm_c, p1_00a, p2_00a, tipo=tipo_00a, offset_x=ox_00a, offset_y=oy_00a
        )
        if dm_00a:
            total_cotas += 1

    agregar_ejes_simetria_iram(v_arm_planta, es_revolucion=False)
    agregar_ejes_simetria_iram(v_arm_frente, es_revolucion=False)
    agregar_ejes_simetria_iram(v_arm_corte, es_revolucion=False)

    # Globos de identificación clave en V00a_Corte_AA
    def _pt_corte_00a(ins_nm, rx_off=0.0, z_frac=0.5):
        if ins_nm not in shapes_ens:
            return None
        b = shapes_ens[ins_nm].BoundBox
        return App.Vector(b.Center.x + rx_off, 0.0, b.ZMin + z_frac * b.ZLength)

    globos_00a = [
        (23, _pt_corte_00a("Tapa_Motor_01_3D", -40.0, 0.5), "L"),
        (19, _pt_corte_00a("Estructura_Interior_1_07_3D", -60.0, 0.5), "L"),
        (17, _pt_corte_00a("Adaptador_Eje_04_3D", -18.0, 0.5), "L"),
        (24, _pt_corte_00a("Rodamiento_SKF_609", -9.0, 0.5), "L"),
        (4,  _pt_corte_00a("Sufridera_Int_05b_3D", -14.0, 0.5), "L"),
        (25, _pt_corte_00a("Reten_10x22x7", -8.0, 0.5), "L"),
        (5,  _pt_corte_00a("Tapa_Sufridera_Int_05a_3D", -14.0, 0.5), "L"),
        (18, _pt_corte_00a("Anillo_Torica_Int_13_3D", -48.0, 0.5), "L"),
        (7,  _pt_corte_00a("Embolo_Delrin_10_3D", -26.0, 0.5), "L"),
        (8,  _pt_corte_00a("Centro_Embolo_1_11_3D", -12.0, 0.22), "L"),
        (1,  _pt_corte_00a("Tapa_Exterior_16a_3D", -48.0, 0.5), "L"),
        (12, _pt_corte_00a("Transmisor_A_02a_3D", 5.0, 0.5), "R"),
        (20, _pt_corte_00a("Cierre_Estructura_1_15_3D", 62.0, 0.5), "R"),
        (13, _pt_corte_00a("Transmisor_B_02b_3D", 5.0, 0.5), "R"),
        (15, _pt_corte_00a("Adaptador_Rodamiento_03_3D", 16.0, 0.5), "R"),
        (31, _pt_corte_00a("Tuerca_Guia_1_08_3D", 0.0, 0.5), "R"),
        (3,  _pt_corte_00a("Tapa_Interior_16b_3D", 48.0, 0.5), "R"),
        (9,  _pt_corte_00a("Centro_Embolo_2_12_3D", 12.0, 0.5), "R"),
        (27, _pt_corte_00a("ORing_Embolo_3D", 35.0, 0.5), "R"),
        (14, _pt_corte_00a("Tornillo_Sin_Fin_14_3D", 4.0, 0.45), "R"),
        (11, _pt_corte_00a("Guia_1_08_3D", 0.0, 0.35), "R"),
        (2,  _pt_corte_00a("Cilindro_09_3D", 39.5, 0.25), "R"),
        (10, _pt_corte_00a("Sensor_Piston_1_3D", 0.0, 0.5), "R"),
    ]
    _distribuir_globos_en_columnas(
        doc_planos,
        page_00a,
        v_arm_corte,
        globos_00a,
        centro_a,
        0.5,
        x_col_izq=204.0,
        x_col_der=380.0,
        y_min_hoja=145.0,
        y_max_hoja=355.0,
        prefijo="00a",
        direction=App.Vector(0, -1, 0),
        x_direction=App.Vector(1, 0, 0),
        paso_min_mm=10.2,
    )

    for entrada in CATALOGO_ITEMS_BOM_3D:
        if entrada.get("es_comercial") or entrada.get("es_buloneria"):
            continue
        it_num = entrada["item"]
        spec = ESPECIFICACIONES_HOJAS_3D[it_num]
        fmt_i = piezas_meta[it_num]
        page_p = doc_planos.getObject(entrada["hoja_plano"])
        vistas_p = vistas_piezas[it_num]
        n_cotas_p = _acotar_hoja_pieza_3d(doc_planos, page_p, it_num, vistas_p, spec, fmt_i)
        total_cotas += n_cotas_p

        v_sec = vistas_p.get("sec")
        t_corte = doc_planos.getObject(f"Txt_{it_num:02d}_Corte")
        if v_sec and t_corte:
            try:
                e_sec = v_sec.getVisibleEdges()
                if e_sec:
                    ymax_sec = max(e.BoundBox.YMax for e in e_sec)
                    half_h_sec = 0.5 * (ymax_sec - min(e.BoundBox.YMin for e in e_sec))
                    H_c = FORMATOS_IRAM[fmt_i][1]
                    if "titulo_y" in spec:
                        t_corte.Y = min(H_c - 17.5, float(spec["titulo_y"]))
                    else:
                        extra_y = float(spec.get("extra_y_titulo", 24.0 if spec["familia"] == "A" else 34.0))
                        t_corte.Y = min(H_c - 17.5, float(v_sec.Y.Value) + half_h_sec + extra_y)
            except Exception:
                pass

    doc_planos.recompute()
    doc_planos.saveAs(RUTA_SALIDA_FCSTD)
    print(f"Legajo 3D maestro guardado ({total_hojas} hojas, {total_cotas} cotas geométricas): {RUTA_SALIDA_FCSTD}")

    # 5. Guardar cada lámina individual liviana en `planos/hojas_3d/` (incluyendo Datos_Rotulo y Tabla_BOM_IRAM)
    # Preserva la edición manual del usuario en Planos 20..25 (ítems 20,21,22,23,31,32) salvo FORZAR_EDITADAS=1,
    # actualizando únicamente su VP_XX_Cuadro_Cotas a formato editable TechDraw::DrawRichAnno sin recortes.
    os.makedirs(DIR_HOJAS_3D, exist_ok=True)
    _entrada_por_hoja = {
        ent_h["hoja_plano"]: ent_h
        for ent_h in CATALOGO_ITEMS_BOM_3D
        if not ent_h.get("es_comercial") and not ent_h.get("es_buloneria") and "hoja_plano" in ent_h
    }
    _ITEMS_EDITADOS_USUARIO = {20, 21, 22, 23, 31, 32}
    _forzar_editadas = os.environ.get("FORZAR_EDITADAS") == "1"
    paginas = [o for o in doc_planos.Objects if o.TypeId == "TechDraw::DrawPage"]
    for pag in paginas:
        ruta_ind = os.path.join(DIR_HOJAS_3D, f"{pag.Name}.FCStd")
        ent_m = _entrada_por_hoja.get(pag.Name)
        if ent_m and ent_m["item"] in _ITEMS_EDITADOS_USUARIO and os.path.exists(ruta_ind) and not _forzar_editadas:
            it_m = ent_m["item"]
            spec_m = ESPECIFICACIONES_HOJAS_3D[it_m]
            d_man = App.openDocument(ruta_ind)
            pg_m = d_man.getObject(pag.Name)
            if pg_m is not None:
                old_cc = d_man.getObject(f"VP_{it_m:02d}_Cuadro_Cotas")
                if old_cc is not None:
                    try:
                        pg_m.removeView(old_cc)
                    except Exception:
                        pass
                    d_man.removeObject(old_cc.Name)
                if spec_m["formato"] == "A4":
                    x_der_m, ancho_tbl_m, pt_tbl_m, H_m = 228.0, 104.0, 5.2, 210.0
                else:
                    x_der_m, ancho_tbl_m, pt_tbl_m, H_m = 330.0, 144.0, 5.8, 297.0
                _, y_top_m, _ = crear_cuadro_cotas_editable_iram(
                    d_man,
                    pg_m,
                    f"VP_{it_m:02d}_Cuadro_Cotas",
                    spec_m["resumen"],
                    ent_m["notas_taller"],
                    ancho_mm=ancho_tbl_m,
                    x_centro=x_der_m,
                    y_base_min=65.0,
                    font_pt=pt_tbl_m,
                )
                v_iso_m = d_man.getObject(f"VP_{it_m:02d}_Iso")
                t_iso_m = d_man.getObject(f"Txt_{it_m:02d}_Iso")
                if v_iso_m is not None:
                    try:
                        e_iso_m = v_iso_m.getVisibleEdges()
                        h_half = (
                            0.5 * (max(ed.BoundBox.YMax for ed in e_iso_m) - min(ed.BoundBox.YMin for ed in e_iso_m))
                            if e_iso_m
                            else 18.0
                        )
                        y_iso_cur = float(v_iso_m.Y.Value)
                        y_need_min = y_top_m + 10.0 + h_half
                        y_max_iso = H_m - 22.0 - h_half
                        if y_iso_cur < y_need_min and y_max_iso >= y_need_min - 8.0:
                            y_new = min(y_max_iso, max(y_need_min, 0.5 * (y_top_m + 10.0 + H_m - 14.0)))
                            dy_m = y_new - y_iso_cur
                            v_iso_m.Y = y_new
                            if t_iso_m is not None:
                                t_iso_m.Y = min(H_m - 17.0, float(t_iso_m.Y.Value) + dy_m)
                    except Exception:
                        pass
                d_man.recompute()
                d_man.save()
                App.closeDocument(d_man.Name)
                print(f"  [PRESERVADA EDICIÓN MANUAL + CUADRO EDITABLE] {pag.Name}.FCStd")
                continue
            App.closeDocument(d_man.Name)

        d_ind = App.newDocument(pag.Name)
        d_ind.copyObject(pag, True)
        d_ind.copyObject(dr, False)
        d_ind.copyObject(tb, False)
        for obj_i in d_ind.Objects:
            if obj_i.isDerivedFrom("Part::Feature") and getattr(obj_i, "ViewObject", None):
                obj_i.ViewObject.Visibility = False
        d_ind.recompute()
        d_ind.saveAs(ruta_ind)
        App.closeDocument(d_ind.Name)
    print(f"Generadas/actualizadas {len(paginas)} hojas individuales livianas en: {DIR_HOJAS_3D}")

    # 6. Exportación opcional a PDF únicamente bajo EXPORTAR_PDF=1 (Regla 3.1)
    if os.environ.get("EXPORTAR_PDF") == "1" and App.GuiUp:
        dir_pdf = os.path.join(DIR_PLANOS, "pdf_3d")
        os.makedirs(dir_pdf, exist_ok=True)
        import TechDrawGui
        import FreeCADGui as Gui
        t_esp = _time_hlr.time()
        while _time_hlr.time() - t_esp < 45.0:
            Gui.updateGui()
            if all(len(v.getVisibleEdges()) > 0 for v in _vistas_hlr):
                break
            _time_hlr.sleep(0.20)
        for _ in range(5):
            Gui.updateGui()
            _time_hlr.sleep(0.08)
        for o in paginas:
            ruta_pdf = os.path.join(dir_pdf, f"{o.Name}.pdf")
            TechDrawGui.exportPageAsPdf(o, ruta_pdf)
            print("Exportado PDF:", ruta_pdf)

    if not App.GuiUp:
        App.closeDocument(doc_planos.Name)
    elif os.environ.get("QUIT_ON_FINISH") == "1":
        App.closeDocument(doc_planos.Name)
        os._exit(0)


if __name__ in ("__main__", "generar_planos_impresion_3d"):
    import traceback
    try:
        main()
    except Exception:
        traceback.print_exc()
        if App.GuiUp and os.environ.get("QUIT_ON_FINISH") == "1":
            os._exit(1)
        sys.exit(1)
