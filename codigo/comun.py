"""Utilidades compartidas por los scripts del proyecto.

Centraliza lo que todos los análisis necesitan igual: la localización de la
raíz del proyecto, las rutas, la ventana de análisis, la identificación de los
dos puntos de venta, la paleta de figuras y —sobre todo— la carga y depuración
de cada fuente de datos de Postobón con las mismas reglas.

Regla de oro: **ningún script vuelve a leer un extracto crudo por su cuenta.**
Si una regla de depuración cambia (por ejemplo, cómo se tratan las filas de
nota crédito sin cantidad), se cambia aquí una sola vez y todos los análisis
la heredan.

Uso típico::

    from comun import *          # constantes, rutas, helpers de figuras
    dev = cargar_devoluciones()  # devoluciones por vencimiento (GA05)
    col = cargar_colocacion()    # colocación (sell-in)
    vu  = cargar_vidas_utiles()  # vida útil por SKU
    nc  = cargar_notas_credito() # universo de notas crédito (GA05)
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib as mpl

# La consola de Windows usa cp1252 por defecto y rompe con "→" o tildes.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
def raiz_proyecto() -> Path:
    """Sube desde este archivo hasta encontrar CLAUDE.md.

    Así el código corre igual desde la raíz, desde ``codigo/`` o desde un
    cuaderno abierto en cualquier directorio de trabajo.
    """
    inicio = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd().resolve()
    for carpeta in [inicio, *inicio.parents]:
        if (carpeta / "CLAUDE.md").exists():
            return carpeta
    return inicio


BASE = raiz_proyecto()
CRUDOS = BASE / "datos" / "crudos"            # extractos tal como salen de Power BI / SAP
PROCESADOS = BASE / "datos" / "procesados"    # tablas calculadas por el código
FIGURAS = BASE / "figuras"
PROCESADOS.mkdir(parents=True, exist_ok=True)
FIGURAS.mkdir(exist_ok=True)

ARCHIVO_DEVOLUCIONES = CRUDOS / "devoluciones_vencimiento_analitico.csv"
ARCHIVO_DEVOLUCIONES_DIARIO = CRUDOS / "devoluciones_vencimiento_diario_2024-09_2026-08.csv"
ARCHIVO_NOTAS_CREDITO = CRUDOS / "notas_credito_todas_2024-09_2026-08.csv"
ARCHIVO_COLOCACION = CRUDOS / "Colocacion.xlsx"
ARCHIVO_VIDAS_UTILES = CRUDOS / "Vidas utiles.XLSX"
ARCHIVO_PDV = CRUDOS / "Puntos de venta.xlsx"
# Plataforma CEN (Carvajal): descargas del mes de enero/2026, un archivo por
# documento con nombre GUID. CSV = devoluciones del portal Éxito; TXT = avisos
# de recibo de Olímpica (hallazgo H-16).
CARPETA_CEN_ENERO_2026 = CRUDOS / "Devoluciones enero 2026"
ARCHIVO_MAESTRO_PORTAFOLIO_EXITO = CRUDOS / "MAESTRO PORTAFOLIO EXITO.xlsx"
ARCHIVO_MAESTRO_PORTAFOLIO_OLIMPICA = CRUDOS / "MAESTRO PORTAFOLIO OLIMPICA.xlsx"

# ---------------------------------------------------------------------------
# Ventana de análisis
# ---------------------------------------------------------------------------
INICIO = pd.Timestamp("2024-09-01")
FIN = pd.Timestamp("2026-08-31")
DIAS_VENTANA = (FIN - INICIO).days + 1          # 730 días
CAL = pd.period_range(INICIO, FIN, freq="M")    # 24 meses

# ---------------------------------------------------------------------------
# Puntos de venta del alcance
# ---------------------------------------------------------------------------
# El código SAP identifica la CADENA, no la tienda. La tienda vive en el campo
# `Cliente` del modelo de Power BI y en `Cliente SAP - Clave` de colocación
# (que en este extracto solo contiene los dos PDV del estudio; ver validación 1
# de analisis_diagnostico_fase1.py).
SAP_EXITO = 1000129473
SAP_OLIMPICA = 1000205719
EXITO = "Éxito San Antonio"
OLIMPICA = "Olímpica Villanueva"
TIENDAS = [EXITO, OLIMPICA]
CORTO = {EXITO: "Éxito", OLIMPICA: "Olímpica"}
MAPA_SAP = {SAP_EXITO: EXITO, SAP_OLIMPICA: OLIMPICA}
MAPA_PDV = {"Ex 039 Exito San Antonio": EXITO, "St 341 Villanueva": OLIMPICA}
# Código de la tienda en los sistemas del cliente (CEN): dependencia Éxito 0039,
# tienda Olímpica 341.
DEPENDENCIA_EXITO = "0039"
TIENDA_OLIMPICA = "341"

# Clasificaciones del GA05 que forman el alcance "BNA" del proyecto. "Mundo
# Cero" es la línea sin azúcar de las mismas bebidas no alcohólicas (Pepsi
# Cero, Manzana Cero, etc.) y el archivo de colocación la incluye; CCC
# (cerveza) y Nutrimenti quedan fuera.
CLASIFICACIONES_ALCANCE = ["BNA", "Mundo Cero"]

# Días de entrega declarados en el maestro de puntos de venta (Hoja 1).
DIAS_SEMANA = ["L", "M", "X", "J", "V", "S", "D"]
DIAS_SEMANA_LARGO = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
DIAS_ENTREGA_MAESTRO = {EXITO: set("LMXJVS"), OLIMPICA: set("XS")}
DIAS_PEDIDO_MAESTRO = {EXITO: set("LMXJVS"), OLIMPICA: set("LJ")}

# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------
# Dos series categóricas (identidad = tienda, no magnitud). El par cian-naranja
# se eligió por separación bajo daltonismo: ΔE OKLab = 18,4 en protanopia y
# 25,8 en visión normal, ambos por encima del umbral de 8 y 15 respectivamente.
COLOR = {EXITO: "#0080A8", OLIMPICA: "#C05A22"}
COLOR_SUAVE = {EXITO: "#9CCFE0", OLIMPICA: "#E8B99E"}
TINTA = "#15191B"
TINTA_2 = "#3C474B"
GRIS = "#68767B"
REGLA = "#E0DFD8"
MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def configurar_estilo() -> None:
    mpl.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.edgecolor": REGLA, "axes.labelcolor": TINTA_2, "axes.titlesize": 12,
        "axes.titleweight": "bold", "axes.titlecolor": TINTA, "axes.titlelocation": "left",
        "axes.titlepad": 10, "axes.grid": True, "axes.axisbelow": True,
        "grid.color": REGLA, "grid.linewidth": 0.8,
        "xtick.color": GRIS, "ytick.color": GRIS,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "legend.frameon": False, "figure.facecolor": "white", "axes.facecolor": "white",
    })


def pct(x, d=2) -> str:
    """Formato colombiano: coma decimal, punto de miles."""
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def etiquetas_mes(periodos, paso=2):
    """Meses abreviados en español (matplotlib solo formatea en inglés)."""
    return [f"{MESES_ES[p.month - 1]} {p.year % 100:02d}" for p in periodos][::paso]


def limpiar_eje(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", visible=False)


def titulo_figura(fig, texto, y=1.02) -> None:
    """Título de la figura, alineado a la izquierda como los títulos de eje."""
    fig.suptitle(texto, x=0.125, ha="left", y=y,
                 fontsize=12, fontweight="bold", color=TINTA)


# ---------------------------------------------------------------------------
# Carga y depuración de fuentes
# ---------------------------------------------------------------------------
def cargar_devoluciones() -> pd.DataFrame:
    """Devoluciones por vencimiento (consulta DAX al GA05, ver script Fase 1).

    Grano: una fila por fecha × punto de venta × SKU (× centro, que no rompe
    la llave). Columnas normalizadas: ``Fecha``, ``PDV``, ``SKU``, ``Material``,
    ``Cajas_dev``, ``Unidades_dev``, ``Valor_dev``, ``Mes``, ``Semana``.

    Columna ``Solo_valor``: filas donde la nota crédito trae valor pero
    ninguna cantidad (cajas = unidades = hectolitros = 0). Aparecen solo desde
    julio/2025 y solo con centro 43 (hallazgo H-03 del registro de hallazgos).
    Se conservan para el valor y quedan marcadas para que cada análisis decida
    explícitamente qué hacer con ellas.
    """
    dev = pd.read_csv(ARCHIVO_DEVOLUCIONES, encoding="utf-8-sig")
    dev["Fecha"] = pd.to_datetime(dev["Fecha devolución"])
    dev["PDV"] = dev["Punto de venta"].map(MAPA_PDV)
    dev = dev.rename(columns={
        "Material SAP - Clave": "SKU",
        "Material SAP - Texto": "Material",
        "Centro - Clave": "Centro",
        "Cantidad devuelta en cajas físicas": "Cajas_dev",
        "Cantidad devuelta en unidades": "Unidades_dev",
        "Cantidad devuelta en hectolitros": "Hl_dev",
        "Valor neto devuelto": "Valor_dev",
        "Notas crédito": "Lineas_nc",
    })
    dev["Mes"] = dev["Fecha"].dt.to_period("M")
    dev["Semana"] = dev["Fecha"].dt.to_period("W")
    dev["Solo_valor"] = (dev["Cajas_dev"] == 0) & (dev["Unidades_dev"] == 0) & (dev["Valor_dev"] > 0)

    dup = dev.duplicated(["Fecha", "PDV", "SKU"]).sum()
    assert dup == 0, f"{dup} filas duplicadas en la llave fecha × PDV × SKU"
    assert (dev["Cajas_dev"] >= 0).all(), "Hay cantidades negativas en devoluciones"
    assert dev["PDV"].notna().all(), "Hay filas sin punto de venta mapeado"
    assert dev["Fecha"].between(INICIO, FIN).all(), "Hay fechas fuera de la ventana"
    return dev


def cargar_colocacion() -> pd.DataFrame:
    """Colocación (sell-in) por fecha de entrega, cadena y material.

    Columnas normalizadas: ``Fecha pedido``, ``Fecha entrega``, ``Centro``,
    ``PDV``, ``SKU``, ``Material``, ``Cajas_col``, ``Mes``, ``Semana``,
    ``Signo`` ('positiva' | 'negativa' | 'cero').

    El archivo viene NETO de notas crédito (filas negativas; hallazgo H-01):
    el denominador de cualquier tasa es la colocación BRUTA, es decir
    ``col[col.Signo == "positiva"]``. Las 150 filas en cero no aportan cajas y
    se excluyen de ambos lados.
    """
    col = pd.read_excel(ARCHIVO_COLOCACION)
    col = col.rename(columns={
        "Material SAP - Clave": "SKU",
        "Material SAP - Texto": "Material",
        "Centro - Clave": "Centro",
        "Cantidad colocada en cajas físicas": "Cajas_col",
    })
    col["PDV"] = col["Cliente SAP - Clave"].map(MAPA_SAP)
    col["Mes"] = col["Fecha entrega"].dt.to_period("M")
    col["Semana"] = col["Fecha entrega"].dt.to_period("W")
    col["Signo"] = np.select([col.Cajas_col > 0, col.Cajas_col < 0], ["positiva", "negativa"], "cero")
    col["Lead_dias"] = (col["Fecha entrega"] - col["Fecha pedido"]).dt.days
    col["dow_pedido"] = col["Fecha pedido"].dt.dayofweek.map(lambda i: DIAS_SEMANA[i])
    col["dow_entrega"] = col["Fecha entrega"].dt.dayofweek.map(lambda i: DIAS_SEMANA[i])

    assert col["PDV"].notna().all(), "Hay filas de colocación con cliente SAP fuera del alcance"
    assert (col["Lead_dias"] >= 0).all(), "Hay filas con fecha de pedido posterior a la entrega"
    assert col["Fecha entrega"].between(INICIO, FIN).all(), "Hay entregas fuera de la ventana"
    return col


def colocacion_bruta(col: pd.DataFrame) -> pd.DataFrame:
    """Solo las filas positivas: el denominador de toda tasa (hallazgo H-01)."""
    return col[col.Signo == "positiva"].copy()


def cargar_vidas_utiles() -> pd.DataFrame:
    """Vida útil en días por SKU. El maestro solo trae el centro 43.

    Ambos PDV recibieron del centro 79 hasta mayo/2025 y del 43 desde junio/2025
    (hallazgo H-05); no se validó si la vida útil difiere por planta: limitación
    declarada en los informes.
    """
    vu = pd.read_excel(ARCHIVO_VIDAS_UTILES)
    vu.columns = ["Centro", "SKU", "Material_vu", "Vida_util_dias"]
    vu = vu[vu["Centro"] == 43].groupby("SKU", as_index=False)["Vida_util_dias"].min()
    assert (vu.Vida_util_dias > 0).all()
    return vu


def cargar_notas_credito() -> pd.DataFrame:
    """Universo completo de notas crédito de los 2 PDV (todos los motivos,
    Devolución y Rechazo, todas las clasificaciones). Segunda consulta DAX del
    script de Fase 1. Sirve para validar la colocación y como base de contraste.
    """
    nc = pd.read_csv(ARCHIVO_NOTAS_CREDITO, encoding="utf-8-sig")
    nc["Fecha"] = pd.to_datetime(nc["Fecha"])
    nc["PDV"] = nc["Punto de venta"].map(MAPA_PDV)
    nc["Mes"] = nc["Fecha"].dt.to_period("M")
    nc["Solo_valor"] = (nc["Cajas"] == 0) & (nc["Unidades"] == 0)
    assert nc["PDV"].notna().all()
    return nc


def cargar_maestro_pdv() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(Hoja 1: frecuencia de pedido/entrega por PDV, Hoja 2: pares pedido→entrega)."""
    h1 = pd.read_excel(ARCHIVO_PDV, sheet_name="Hoja 1")
    h2 = pd.read_excel(ARCHIVO_PDV, sheet_name="Hoja 2")
    return h1, h2


def cargar_devoluciones_cen_exito(carpeta: Path = CARPETA_CEN_ENERO_2026) -> pd.DataFrame:
    """Devoluciones del portal Éxito descargadas del CEN (todas las tiendas).

    Un CSV por descarga, ancho fijo con relleno de espacios y codificación
    latin-1. Grano: devolución (``Devolucion``) × EAN. La cantidad viene en
    unidades de venta del EAN (la unidad del código de barras, que puede ser
    un empaque múltiple), no en cajas físicas: la conversión se hace en el
    script de cruce con el factor unidades/caja del GA05 (H-04, H-16).
    Columnas: ``Devolucion``, ``Dep_origen``, ``Tienda_origen``,
    ``Dep_recogida``, ``Tienda_recogida``, ``EAN``, ``Desc_EAN``,
    ``Unidades_cen``, ``Fecha_dev``, ``Fecha_recogida``, ``Archivo``.
    """
    partes = []
    for f in sorted(carpeta.glob("*.csv")):
        x = pd.read_csv(f, encoding="latin-1", dtype=str)
        x.columns = x.columns.str.strip()
        partes.append(x.apply(lambda s: s.str.strip()).assign(Archivo=f.name))
    cen = pd.concat(partes, ignore_index=True).rename(columns={
        "#DEVOL": "Devolucion", "DEP ORIGEN": "Dep_origen", "NOMDEP ORIGEN": "Tienda_origen",
        "DEP RECOGIDA": "Dep_recogida", "NOMDEP RECOGIDA": "Tienda_recogida",
        "EAN DESC": "Desc_EAN", "CANTIDAD": "Unidades_cen",
    })
    cen["Unidades_cen"] = cen["Unidades_cen"].astype(float)
    cen["Fecha_dev"] = pd.to_datetime(cen["FECHA DEVOL"], format="%Y%m%d")
    cen["Fecha_recogida"] = pd.to_datetime(cen["FECHA RECOGIDA"], format="%Y%m%d")
    cen = cen[["Devolucion", "Dep_origen", "Tienda_origen", "Dep_recogida", "Tienda_recogida",
               "EAN", "Desc_EAN", "Unidades_cen", "Fecha_dev", "Fecha_recogida", "Archivo"]]

    # Una misma devolución reaparece en otra descarga cuando la recogida se
    # reprograma (misma cantidad, otra fecha de recogida): se deja la versión
    # con la recogida más reciente.
    llave = ["Devolucion", "EAN"]
    rep = cen[cen.duplicated(llave, keep=False)]
    assert (rep.groupby(llave)["Unidades_cen"].nunique() == 1).all(), "Reprogramación con cantidad distinta"
    cen = (cen.sort_values("Fecha_recogida").drop_duplicates(llave, keep="last")
           .sort_values(["Fecha_dev", "Devolucion", "EAN"]).reset_index(drop=True))

    assert (cen["Unidades_cen"] > 0).all(), "Hay cantidades no positivas en el portal Éxito"
    assert cen.groupby("Devolucion")["Dep_origen"].nunique().max() == 1
    return cen


def cargar_avisos_cen_olimpica(carpeta: Path = CARPETA_CEN_ENERO_2026) -> pd.DataFrame:
    """Documentos ``AVISO RECIBO VALORIZADO`` de Olímpica descargados del CEN.

    Texto tabulado con tres bloques de encabezado (cliente/centro, proveedor,
    pedido) y una tabla de ítems. Se devuelve una fila por ítem con el centro
    y el pedido del encabezado. Columnas: ``Centro``, ``Ciudad``, ``Pedido``,
    ``Fecha_pedido``, ``EAN``, ``Descripcion``, ``Factura``, ``Cantidad``,
    ``UM``, ``Valor_neto``, ``Archivo``.
    """
    num = lambda s: float(s.replace(",", "").strip() or 0)
    filas = []
    for f in sorted(carpeta.glob("*.txt")):
        lineas = [l.rstrip("\r\n") for l in f.open(encoding="utf-8")]
        lineas = [l for l in lineas if l.strip() and not l.startswith("____")]
        enc = {l.split("\t")[0]: lineas[i + 1].split("\t") for i, l in enumerate(lineas[:-1])
               if l.split("\t")[0] in ("NIT", "Pedido")}
        cliente, pedido = enc["NIT"], enc["Pedido"]
        for l in lineas:
            t = l.split("\t")
            if t[0].isdigit() and len(t[0]) >= 8 and len(t) >= 15:
                filas.append({
                    "Centro": cliente[5], "Ciudad": cliente[4], "Pedido": pedido[0],
                    "Fecha_pedido": pd.to_datetime(pedido[1], format="%d/%m/%Y"),
                    "EAN": t[0], "Descripcion": t[1], "Factura": t[2],
                    "Cantidad": num(t[4]), "UM": t[5], "Valor_neto": num(t[14]),
                    "Archivo": f.name,
                })
    return pd.DataFrame(filas)


def cargar_maestro_portafolio_exito() -> pd.DataFrame:
    """Maestro EAN/PLU ↔ SKU SAP de Postobón por dependencia (tienda) Éxito.

    El EAN viene como texto con punto final ("7702090039245.") y hay códigos
    SAP "#N/D" (sin homologar), que se descartan. Columnas: ``PLU``, ``EAN``,
    ``SKU``, ``Desc_Postobon``, ``Dependencia``, ``SAP_tienda``, ``Tienda``.
    """
    m = pd.read_excel(ARCHIVO_MAESTRO_PORTAFOLIO_EXITO, dtype=str)
    m.columns = m.columns.str.strip()
    m = m.rename(columns={"Plu": "PLU", "Descripcion Postobon": "Desc_Postobon",
                          "SAP Tienda": "SAP_tienda", "DependenciaDesc": "Tienda"})
    m["EAN"] = m["Ean"].str.replace(r"\.0*$", "", regex=True).str.strip()
    m["SKU"] = pd.to_numeric(m["SAP"], errors="coerce")
    m["Dependencia"] = m["Dependencia"].str.strip().str.zfill(4)
    m = m[m["SKU"].notna()].astype({"SKU": int})
    assert m.groupby("EAN")["SKU"].nunique().max() == 1, "Un EAN apunta a varios SKU"
    return m[["PLU", "EAN", "SKU", "Desc_Postobon", "Dependencia", "SAP_tienda", "Tienda"]]


def cargar_maestro_portafolio_olimpica() -> pd.DataFrame:
    """Portafolio de Postobón codificado en Olímpica (hoja ACT): EAN, artículo
    Olímpica, marca y subcategoría por centro. **No trae el SKU SAP de
    Postobón**, solo el código de artículo de Olímpica. Columnas: ``Centro``,
    ``CEDI``, ``EAN``, ``Marca``, ``Subcategoria``, ``Articulo``, ``Texto``, ``Razon``.
    """
    m = pd.read_excel(ARCHIVO_MAESTRO_PORTAFOLIO_OLIMPICA, sheet_name="ACT", dtype=str)
    m.columns = m.columns.str.strip()
    m = m.rename(columns={"Ce.": "Centro", "CEDI POSTOBON": "CEDI", "Texto breve de artículo": "Texto",
                          "RAZON": "Razon"})
    return m[["Centro", "CEDI", "EAN", "Marca", "Subcategoria", "Articulo", "Texto", "Razon"]]


def cargar_todo() -> dict:
    return {
        "dev": cargar_devoluciones(),
        "col": cargar_colocacion(),
        "vu": cargar_vidas_utiles(),
        "nc": cargar_notas_credito(),
        "pdv": cargar_maestro_pdv(),
    }


__all__ = [
    "BASE", "CRUDOS", "PROCESADOS", "FIGURAS",
    "ARCHIVO_DEVOLUCIONES", "ARCHIVO_DEVOLUCIONES_DIARIO", "ARCHIVO_NOTAS_CREDITO",
    "ARCHIVO_COLOCACION", "ARCHIVO_VIDAS_UTILES", "ARCHIVO_PDV",
    "CARPETA_CEN_ENERO_2026", "ARCHIVO_MAESTRO_PORTAFOLIO_EXITO", "ARCHIVO_MAESTRO_PORTAFOLIO_OLIMPICA",
    "DEPENDENCIA_EXITO", "TIENDA_OLIMPICA",
    "INICIO", "FIN", "DIAS_VENTANA", "CAL",
    "SAP_EXITO", "SAP_OLIMPICA", "EXITO", "OLIMPICA", "TIENDAS", "CORTO",
    "MAPA_SAP", "MAPA_PDV", "CLASIFICACIONES_ALCANCE",
    "DIAS_SEMANA", "DIAS_SEMANA_LARGO", "DIAS_ENTREGA_MAESTRO", "DIAS_PEDIDO_MAESTRO",
    "COLOR", "COLOR_SUAVE", "TINTA", "TINTA_2", "GRIS", "REGLA", "MESES_ES",
    "configurar_estilo", "pct", "etiquetas_mes", "limpiar_eje", "titulo_figura",
    "raiz_proyecto", "cargar_devoluciones", "cargar_colocacion", "colocacion_bruta",
    "cargar_vidas_utiles", "cargar_notas_credito", "cargar_maestro_pdv", "cargar_todo",
    "cargar_devoluciones_cen_exito", "cargar_avisos_cen_olimpica",
    "cargar_maestro_portafolio_exito", "cargar_maestro_portafolio_olimpica",
]
