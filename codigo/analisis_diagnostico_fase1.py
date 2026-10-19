# %% [markdown]
# # Diagnóstico Fase 1 — Devoluciones por vencimiento vs. colocación
#
# **Proyecto:** Herramienta estadística de reabastecimiento basada en la optimización
# del stock mínimo para reducir devoluciones por caducidad, canal moderno.
#
# **Alcance:** 2 puntos de venta — `Ex 039 Exito San Antonio` y `St 341 Villanueva`
# (Olímpica). Categoría BNA y Mundo Cero, regional Antioquia.
#
# **Periodo:** 01/09/2024 – 31/08/2026 (24 meses).
#
# **Autor:** Adrian Camilo Hernández Copete — Ingeniería Industrial, U. de Antioquia.
# Práctica empresarial, Desarrollo Logístico, Postobón S.A.
#
# ---
#
# ## Qué hace este cuaderno
#
# Reproduce íntegramente el diagnóstico de la Fase 1: depura las tres fuentes,
# valida dos supuestos críticos sobre los datos, calcula el indicador principal
# (tasa de devolución por vencimiento) y genera las cuatro figuras del informe.
#
# El cuaderno es la sustentación del informe: cada cifra citada allí sale de una
# celda de aquí, y cada decisión metodológica está justificada en el texto que
# precede al código.
#
# La exploración de datos y las pruebas de robustez de estos hallazgos están en
# `eda_fase1.py`; los hallazgos sobre los datos, numerados (H-01, H-02, …), en
# `informes/Registro_hallazgos.md`.
#
# **Requisitos:** `pandas`, `numpy`, `matplotlib`, `openpyxl`.

# %% [markdown]
# ## 1. Configuración
#
# Rutas, ventana, identificación de tiendas, paleta y funciones de carga viven en
# `comun.py`, compartido con el resto de scripts del proyecto, para que todos
# depuren los datos con las mismas reglas.

# %%
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Permite ejecutar el cuaderno desde cualquier directorio de trabajo.
sys.path.insert(0, str(Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()))
from comun import *  # noqa: F401,F403  (rutas, constantes, helpers y cargadores)

configurar_estilo()
print(f"Ventana: {INICIO:%Y-%m-%d} a {FIN:%Y-%m-%d}  ({DIAS_VENTANA} días)")

# %% [markdown]
# ## 2. Procedencia de los datos
#
# ### 2.1 Devoluciones — consulta DAX al modelo de Power BI
#
# Los datos NO se exportaron desde un visual del tablero. Se consultó directamente
# el modelo tabular que Power BI Desktop levanta al abrir `GA05-Notas Crédito.pbix`,
# lo que hace la extracción reproducible y auditable.
#
# La tabla del modelo es `Devoluciones`. La medida del tablero es
# `Cantidad = SUM([Cantidad UMB]) * -1`; el `* -1` se replica aquí porque las notas
# crédito se registran en negativo.
#
# Filtros aplicados (todos duros, definen el alcance del proyecto):
#
# | Filtro | Valor | Razón |
# |---|---|---|
# | `Rechazo o Dev` | `"Devolución"` | Los rechazos son logísticos (no salió al mercado, cliente cerrado), no son producto vencido en góndola |
# | `Motivos` | `"Fecha De Vencimiento"` | Objeto del estudio |
# | `Clasificación` | `BNA`, `Mundo Cero` | Categorías del alcance |
# | `Regional` | `Antioquia` | Alcance geográfico |
# | `Cliente` | los 2 PDV | Alcance |
# | `Día Transacción` | 2024-09-01 a 2026-08-31 | Ventana de 24 meses |
#
# **Por qué `Día Transacción` y no `Fecha`:** el modelo trae dos columnas de fecha.
# `Fecha` contiene registros inconsistentes (llega hasta el año 2204 y arranca en
# 2023); `Día Transacción` va de 2024-04-01 a 2026-08-31 sin anomalías. Difieren en
# ~50 % de las filas — **queda pendiente confirmar con la asesora externa cuál es la
# fecha contable de la devolución**.

# %%
CONSULTA_DAX = r"""
EVALUATE
SUMMARIZECOLUMNS(
    'Devoluciones'[Día Transacción],
    'Devoluciones'[Centro],
    'Devoluciones'[Cod Cliente SAP],
    'Devoluciones'[Nombre Cliente],
    'Devoluciones'[Cliente],
    'Devoluciones'[Cod Material],
    'Devoluciones'[Nombre Material],
    'Devoluciones'[Marca],
    'Devoluciones'[Clasificación],
    FILTER(ALL('Devoluciones'[Rechazo o Dev]), 'Devoluciones'[Rechazo o Dev] = "Devolución"),
    FILTER(ALL('Devoluciones'[Motivos]),       'Devoluciones'[Motivos] = "Fecha De Vencimiento"),
    FILTER(ALL('Devoluciones'[Clasificación]), 'Devoluciones'[Clasificación] IN {"BNA","Mundo Cero"}),
    FILTER(ALL('Devoluciones'[Regional]),      'Devoluciones'[Regional] = "Antioquia"),
    FILTER(ALL('Devoluciones'[Cliente]),
        'Devoluciones'[Cliente] IN {"Ex 039 Exito San Antonio","St 341 Villanueva"}),
    FILTER(ALL('Devoluciones'[Día Transacción]),
        'Devoluciones'[Día Transacción] >= DATE(2024,9,1)
     && 'Devoluciones'[Día Transacción] <= DATE(2026,8,31)),
    "Unidades_UMB",  SUM('Devoluciones'[Cantidad UMB])     * -1,
    "Cajas_fisicas", SUM('Devoluciones'[Cantidad CF])      * -1,
    "Hectolitros",   SUM('Devoluciones'[Cant Ventas Hec])  * -1,
    "Valor_neto",    SUM('Devoluciones'[Valor neto venta]) * -1,
    "Documentos",    COUNTROWS('Devoluciones')
)
"""
print(CONSULTA_DAX)


# %% [markdown]
# La función siguiente ejecuta esa consulta contra la instancia local de Analysis
# Services que Power BI Desktop levanta al abrir el `.pbix`. Solo hace falta para
# **regenerar** el extracto; el resto del cuaderno corre sobre el CSV ya exportado.
#
# El truco es que `msmdsrv.exe` (el motor tabular embebido) publica un puerto
# aleatorio en `127.0.0.1`, y el cliente ADOMD vive en la misma carpeta `bin\` del
# proceso — así que del proceso en ejecución se obtienen a la vez el puerto y la
# ruta de la DLL.

# %%
def extraer_devoluciones_dax(consulta: str, destino: Path) -> Path:
    """Ejecuta una consulta DAX contra el .pbix abierto en Power BI Desktop.

    Requiere que `GA05-Notas Crédito.pbix` esté abierto y con el modelo cargado.
    Devuelve la ruta del CSV exportado.
    """
    import subprocess
    import tempfile

    consulta_tmp = Path(tempfile.gettempdir()) / "consulta.dax"
    consulta_tmp.write_text(consulta, encoding="utf-8")

    ps = r"""
$ErrorActionPreference = "Stop"
[System.Threading.Thread]::CurrentThread.CurrentCulture =
    [System.Globalization.CultureInfo]::InvariantCulture

$proc = @(Get-Process msmdsrv -ErrorAction SilentlyContinue)
if ($proc.Count -eq 0) { throw "Abre el .pbix en Power BI Desktop y espera a que cargue el modelo." }
if ($proc.Count -gt 1) { throw "Hay varias instancias de msmdsrv. Cierra las demas." }

$port = (Get-NetTCPConnection -State Listen -OwningProcess $proc[0].Id |
         Where-Object { $_.LocalAddress -eq '127.0.0.1' } |
         Select-Object -First 1).LocalPort

$dll = Join-Path (Split-Path $proc[0].Path -Parent) "Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($dll) | Out-Null

# El .dax debe leerse como UTF-8: Get-Content en PS 5.1 lee ANSI y rompe [Clasificación].
$dax = [System.IO.File]::ReadAllText("__CONSULTA__", [System.Text.Encoding]::UTF8)

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port")
$conn.Open()
try {
    $cmd = $conn.CreateCommand(); $cmd.CommandText = $dax
    $ad = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
    $ds = New-Object System.Data.DataSet
    $ad.Fill($ds) | Out-Null
} finally { $conn.Close() }

$ds.Tables[0] |
    Select-Object * -ExcludeProperty RowError,RowState,Table,ItemArray,HasErrors |
    Export-Csv -Path "__DESTINO__" -NoTypeInformation -Encoding UTF8
"Filas: $($ds.Tables[0].Rows.Count)"
""".replace("__CONSULTA__", str(consulta_tmp)).replace("__DESTINO__", str(destino))

    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    print(r.stdout.strip())
    return destino


# Para regenerar el extracto desde Power BI, descomentar:
# extraer_devoluciones_dax(CONSULTA_DAX, CRUDOS / "devoluciones_vencimiento_analitico.csv")

# %% [markdown]
# ## 3. Carga y depuración
#
# ### 3.1 Devoluciones por vencimiento
#
# Grano: una fila por **fecha × punto de venta × SKU**. La unidad de trabajo es la
# **caja física**, porque es la única que existe también en colocación y por tanto
# la única que permite calcular una tasa (numerador y denominador comparables).

# %%
dev = cargar_devoluciones()   # aplica los controles de integridad (llave única, sin negativos)

print(f"Devoluciones: {pct(len(dev), 0)} filas | "
      f"{dev.Fecha.min():%Y-%m-%d} a {dev.Fecha.max():%Y-%m-%d}")
print(f"Duplicados en la llave: {dev.duplicated(['Fecha', 'PDV', 'SKU']).sum()} | "
      f"cantidades negativas: {(dev.Cajas_dev < 0).sum()}")
dev.head(3)

# %% [markdown]
# #### 3.1.1 Notas crédito con valor pero sin cantidad (hallazgo H-03)
#
# Un tercio de las filas trae valor neto pero **cero cajas, cero unidades y cero
# hectolitros**. No es un problema de conversión de unidades (los mismos SKU sí
# traen cajas en otras fechas): son líneas de nota crédito que en el modelo GA05
# no cargan cantidad. Aparecen únicamente desde julio/2025 y únicamente con
# centro 43, es decir, después del cambio de centro abastecedor (§3.2).
#
# Consecuencias para este diagnóstico:
#
# - El **numerador en cajas no las incluye** (traen cero), así que la tasa de
#   devolución en cajas está calculada solo con las líneas que sí traen cantidad.
#   Si esas líneas correspondieran a producto físico devuelto, la tasa real sería
#   mayor (cota superior en `eda_fase1.py`, §2.4).
# - El **valor devuelto sí las incluye**, por lo que a partir de aquí el valor se
#   reporta separado: con cantidad y sin cantidad.
# - Los meses en que *todas* las líneas vienen sin cantidad (Éxito ene/2026;
#   Olímpica ene y feb/2026) **no son ceros reales** de devolución.
#
# Queda pendiente confirmar con la asesora externa qué documento SAP genera esas
# líneas (¿nota crédito solo por valor?, ¿baja en punto de venta sin retorno físico?).

# %%
sv = dev.groupby(["PDV", "Solo_valor"]).agg(Filas=("SKU", "size"), Valor=("Valor_dev", "sum")).unstack("Solo_valor")
sv.columns = ["Filas con cantidad", "Filas sin cantidad", "Valor con cantidad", "Valor sin cantidad"]
sv["% valor sin cantidad"] = sv["Valor sin cantidad"] / (sv["Valor con cantidad"] + sv["Valor sin cantidad"]) * 100
print(sv.round(1).to_string())
print(f"\nPrimera fila sin cantidad: {dev.loc[dev.Solo_valor, 'Fecha'].min():%Y-%m-%d} | "
      f"centros: {sorted(dev.loc[dev.Solo_valor, 'Centro'].unique())}")

meses_sin_cantidad = {}
for pdv in TIENDAS:
    m = dev[dev.PDV == pdv].groupby("Mes").Solo_valor.agg(["size", "sum"])
    meses_sin_cantidad[pdv] = list(m.index[(m["size"] > 0) & (m["size"] == m["sum"])])
    print(f"{pdv}: meses donde TODAS las líneas vienen sin cantidad → "
          f"{[str(p) for p in meses_sin_cantidad[pdv]]}")

# %% [markdown]
# ### 3.2 Colocación
#
# `Cliente SAP - Clave` identifica la cadena, y `Centro - Clave` la planta de origen
# (43 y 79). El centro **no** distingue el punto de venta: ambas tiendas recibieron
# del centro 79 hasta mayo/2025 y del centro 43 desde junio/2025 (hallazgo H-05,
# detalle en `eda_fase1.py`).

# %%
col = cargar_colocacion()

print(f"Colocación: {pct(len(col), 0)} filas | "
      f"{col['Fecha entrega'].min():%Y-%m-%d} a {col['Fecha entrega'].max():%Y-%m-%d}")
print(col.groupby(["PDV", "Centro"]).size().rename("filas").to_string())
print("\nPrimera y última entrega por centro:")
print(col.groupby(["PDV", "Centro"])["Fecha entrega"].agg(["min", "max"]).to_string())

# %% [markdown]
# ### 3.3 Vidas útiles y maestro de puntos de venta

# %%
vu = cargar_vidas_utiles()          # solo centro 43 (limitación declarada)
pdv_maestro, pdv_pares = cargar_maestro_pdv()
print(pdv_maestro.to_string(index=False))
print(f"\nVidas útiles (centro 43): {pct(len(vu), 0)} SKU")

# %% [markdown]
# ## 4. Validación 1 — ¿la colocación corresponde realmente a estos dos PDV?
#
# El extracto de colocación viene a nivel de cadena, no de tienda. Antes de cruzarlo
# con devoluciones hay que descartar que contenga otras tiendas de Éxito u Olímpica
# en Antioquia, porque eso inflaría el denominador y haría inválida toda la tasa.
#
# **Prueba:** el maestro dice que Olímpica Villanueva pide lunes y jueves y recibe
# miércoles y sábado. Si el extracto fuera de varias tiendas, los días de entrega se
# repartirían por toda la semana. Si es una sola tienda, la masa debe concentrarse
# en miércoles y sábado.

# %%
DIAS = DIAS_SEMANA   # L, M, X, J, V, S, D (columnas dow_* ya vienen de comun.cargar_colocacion)

tab = (col[col.PDV == OLIMPICA]
       .pivot_table(index="dow_pedido", columns="dow_entrega",
                    values="SKU", aggfunc="size", fill_value=0)
       .reindex(index=DIAS, columns=DIAS, fill_value=0))
print("Olímpica Villanueva — día de pedido (filas) × día de entrega (columnas)")
print(tab.to_string())

# Estadístico de la prueba: qué proporción de las líneas se entrega en los días
# declarados por el maestro (miércoles y sábado). Si el extracto mezclara varias
# tiendas de la cadena, las entregas se repartirían por toda la semana.
masa = tab[["X", "S"]].values.sum() / tab.values.sum()
print(f"\nLíneas entregadas en X o S (días declarados del PDV): {pct(masa * 100, 1)} %")
print(f'Celdas dominantes: L→X = {tab.loc["L", "X"]} | '
      f'J→S = {tab.loc["J", "S"]} | V→S = {tab.loc["V", "S"]}')
print("→ El extracto corresponde a un solo punto de venta: St 341 Villanueva.")
print("  (El 15 % restante de líneas fuera de X/S se caracteriza en eda_fase1.py §3.3.)")

# %% [markdown]
# ## 5. Validación 2 — la colocación viene NETA de devoluciones
#
# Este es el hallazgo que obliga a corregir el denominador. El archivo tiene filas
# con cantidad negativa. La hipótesis es que son las notas crédito descontadas
# dentro del mismo extracto, no errores de digitación.
#
# **Dos pruebas independientes:**
#
# 1. Si son notas crédito, no tienen ciclo pedido→entrega: la fecha de pedido debe
#    coincidir con la de entrega.
# 2. Si son las mismas devoluciones, al cruzarlas por fecha + PDV + SKU el valor
#    absoluto debe coincidir con lo devuelto.

# %%
negativos = col[col.Signo == "negativa"]
positivos = colocacion_bruta(col)
ceros = col[col.Signo == "cero"]

print(f"Filas negativas: {pct(len(negativos), 0)} de {pct(len(col), 0)} "
      f"({pct((len(negativos)/len(col)) * 100, 1)} %) | {pct(negativos.Cajas_col.sum(), 1)} cajas")
print(f"Filas en cero: {len(ceros)} (no aportan cajas; se excluyen de ambos lados)")

# Prueba 1 — mismo día.
# Cuidado con la dirección de la condicional. Lo concluyente es P(negativa | mismo
# día), no P(mismo día | negativa): una nota crédito puede registrarse conservando
# la fecha del pedido original, así que no todas las negativas son del mismo día.
mismo_dia = col["Fecha pedido"] == col["Fecha entrega"]
p_neg_dado_mismodia = (col.loc[mismo_dia, "Cajas_col"] < 0).mean()
p_mismodia_dado_neg = mismo_dia.loc[negativos.index].mean()
print(f"Prueba 1a — de las {pct(mismo_dia.sum(), 0)} filas con pedido = entrega, "
      f"son negativas: {pct(p_neg_dado_mismodia * 100, 1)} %")
print(f"Prueba 1b — de las filas negativas, tienen pedido = entrega: "
      f"{pct(p_mismodia_dado_neg * 100, 1)} %")

# Prueba 2 — cruce con devoluciones
neg_k = (negativos.groupby(["PDV", "Fecha entrega", "SKU"], as_index=False)
         .Cajas_col.sum().rename(columns={"Fecha entrega": "Fecha", "Cajas_col": "CF_neg"}))
dev_k = dev.groupby(["PDV", "Fecha", "SKU"], as_index=False).Cajas_dev.sum()

cruce = neg_k.merge(dev_k, on=["PDV", "Fecha", "SKU"], how="inner")
cruce["identico"] = np.isclose(-cruce.CF_neg, cruce.Cajas_dev, atol=0.01)
print(f"Prueba 2 — llaves que cruzan: {pct(len(cruce), 0)} | "
      f"con valor absoluto idéntico: {pct(cruce.identico.sum(), 0)} "
      f"({pct((cruce.identico.mean()) * 100, 1)} %)")

print("\n→ Confirmado: la colocación viene neta de notas crédito.")
print("  El denominador de la tasa debe ser la COLOCACIÓN BRUTA (solo filas positivas).")

# %% [markdown]
# ### 5.1 ¿Qué son exactamente las filas negativas?
#
# Decir "son las devoluciones" es correcto en lo esencial pero impreciso en dos
# sentidos, y ambos importan para no citar mal las cifras. Para resolverlo se
# extrae del GA05 el universo completo de notas crédito de los dos PDV —todos los
# motivos y ambos tipos, Devolución y Rechazo— y se contrasta contra los negativos.

# %%
CONSULTA_DAX_NC = r"""
EVALUATE
SUMMARIZECOLUMNS(
    'Devoluciones'[Día Transacción], 'Devoluciones'[Cliente],
    'Devoluciones'[Cod Material],    'Devoluciones'[Nombre Material],
    'Devoluciones'[Clasificación],   'Devoluciones'[Rechazo o Dev], 'Devoluciones'[Motivos],
    FILTER(ALL('Devoluciones'[Regional]), 'Devoluciones'[Regional] = "Antioquia"),
    FILTER(ALL('Devoluciones'[Cliente]),
        'Devoluciones'[Cliente] IN {"Ex 039 Exito San Antonio","St 341 Villanueva"}),
    FILTER(ALL('Devoluciones'[Día Transacción]),
        'Devoluciones'[Día Transacción] >= DATE(2024,9,1)
     && 'Devoluciones'[Día Transacción] <= DATE(2026,8,31)),
    "Cajas_fisicas", SUM('Devoluciones'[Cantidad CF])  * -1,
    "Unidades",      SUM('Devoluciones'[Cantidad UMB]) * -1,
    "Documentos",    COUNTROWS('Devoluciones')
)
"""
# Sin filtro de Clasificación a propósito: sirve para comprobar qué categorías
# cubre realmente el archivo de colocación.

nc = cargar_notas_credito()

print("Alcance del archivo de colocación, por clasificación del GA05 (cajas):")
nc["SKU en colocación"] = nc.SKU.isin(set(col.SKU))
print(nc.pivot_table(index="Clasificacion", columns="SKU en colocación",
                     values="Cajas", aggfunc="sum", fill_value=0).round(1).to_string())
print("→ La colocación cubre BNA y Mundo Cero. CCC y Nutrimenti no están.\n")

nc_bna = nc[nc.Clasificacion.isin(["BNA", "Mundo Cero"])]

# %% [markdown]
# **Primera imprecisión: ninguna fila negativa queda huérfana, pero no todas son
# devoluciones.** Un quinto son rechazos.

# %%
nc_k = nc_bna.groupby(["PDV", "Fecha", "SKU", "Tipo"], as_index=False).Cajas.sum()
huerfanas = neg_k.merge(nc_k.groupby(["PDV", "Fecha", "SKU"], as_index=False).Cajas.sum(),
                        on=["PDV", "Fecha", "SKU"], how="left", indicator=True)
print(f"Llaves negativas sin ninguna nota crédito que las explique: "
      f"{(huerfanas._merge == 'left_only').sum()} de {len(neg_k)}")

mezcla = nc_k.merge(neg_k, on=["PDV", "Fecha", "SKU"], how="inner")
comp = mezcla.groupby("Tipo").Cajas.agg(Llaves="size", Cajas="sum")
comp["%"] = comp.Cajas / comp.Cajas.sum() * 100
print("\nComposición de las cajas negativas, por tipo de nota crédito:")
print(comp.round(1).to_string())

# %% [markdown]
# **Segunda imprecisión: el archivo no descuenta todas las notas crédito.** Lo que
# nunca llegó a la tienda tampoco se pudo colocar, así que no hay nada que restar —
# de ahí que el motivo "No Salió Al Mercado" quede casi por completo fuera.

# %%
sin_descontar = nc_k.merge(neg_k, on=["PDV", "Fecha", "SKU"], how="left", indicator=True)
sin_descontar = sin_descontar[sin_descontar._merge == "left_only"]
print("Notas crédito BNA/Mundo Cero NO descontadas de la colocación (cajas):")
print(sin_descontar.groupby(["PDV", "Tipo"]).Cajas.agg(Llaves="size", Cajas="sum").round(1).to_string())
print("\nMotivos que más quedan fuera:")
print(nc_bna.merge(neg_k, on=["PDV", "Fecha", "SKU"], how="left", indicator=True)
      .query("_merge == 'left_only'").groupby(["Tipo", "Motivos"]).Cajas.sum()
      .nlargest(5).round(1).to_string())

# %% [markdown]
# **Lo que sí importa para este estudio:** prácticamente toda la devolución por
# vencimiento —el numerador de la tasa— sí fue descontada de la colocación. Por eso
# usar el archivo tal como viene restaría el numerador del denominador, y por eso
# el denominador correcto es la colocación bruta.

# %%
venc_k = (nc_bna[(nc_bna.Tipo == "Devolución") & (nc_bna.Motivos == "Fecha De Vencimiento")]
          .groupby(["PDV", "Fecha", "SKU"], as_index=False).Cajas.sum())
chk = venc_k.merge(neg_k, on=["PDV", "Fecha", "SKU"], how="left", indicator=True)
chk["descontada"] = chk._merge == "both"
r = chk.groupby(["PDV", "descontada"]).Cajas.sum().unstack()
r.columns = ["No descontada", "Descontada"]
r["% descontado"] = r["Descontada"] / r.sum(axis=1) * 100
print(r.round(1).to_string())

print("\nImpacto sobre la tasa:")
for pdv in TIENDAS:
    bruto = positivos.loc[positivos.PDV == pdv, "Cajas_col"].sum()
    neto = col.loc[col.PDV == pdv, "Cajas_col"].sum()
    d = dev.loc[dev.PDV == pdv, "Cajas_dev"].sum()
    print(f"{pdv:<22} con bruto {pct((d/bruto) * 100, 2)} %  |  "
          f"con neto {pct((d/neto) * 100, 2)} %  (inflada)")

# %% [markdown]
# A partir de aquí, `col_bruta` es el denominador de toda tasa.

# %%
col_bruta = positivos.copy()

# %% [markdown]
# ## 6. Indicador principal — tasa de devolución por vencimiento
#
# $$\text{Tasa}_{p} = \frac{\sum \text{cajas devueltas por vencimiento en } p}{\sum \text{cajas colocadas brutas en } p}$$
#
# Es una proporción sobre el mismo punto de venta y periodo. No se compara contra el
# portafolio total ni contra otras tiendas del canal: el alcance del proyecto son
# estos dos PDV y la categoría BNA/Mundo Cero.

# %%
# Conteos de SKU y días: solo líneas con cantidad física (Cajas_dev > 0). Las
# líneas sin cantidad (§3.1.1) se cuentan aparte para no inflar el numerador.
dev_fis = dev[dev.Cajas_dev > 0]
resumen = pd.DataFrame({
    "Colocado bruto": col_bruta.groupby("PDV").Cajas_col.sum(),
    # Los denominadores de devolución salen del GA05, NO de los negativos de
    # colocación: el archivo solo descuenta parte de las notas crédito (§5.1).
    "Devoluciones (todos los motivos)": nc_bna[nc_bna.Tipo == "Devolución"].groupby("PDV").Cajas.sum(),
    "Rechazos (todos los motivos)": nc_bna[nc_bna.Tipo == "Rechazo"].groupby("PDV").Cajas.sum(),
    "Devuelto vencimiento": dev.groupby("PDV").Cajas_dev.sum(),
    "Valor devuelto (líneas con cantidad)": dev_fis.groupby("PDV").Valor_dev.sum(),
    "Valor en NC sin cantidad": dev[dev.Solo_valor].groupby("PDV").Valor_dev.sum(),
    "Valor devuelto (total GA05)": dev.groupby("PDV").Valor_dev.sum(),
    "SKU con devolución física": dev_fis.groupby("PDV").SKU.nunique(),
    "Días con devolución física": dev_fis.groupby("PDV").Fecha.nunique(),
    "Líneas NC sin cantidad": dev.groupby("PDV").Solo_valor.sum(),
}).reindex(TIENDAS)

resumen["Tasa vencimiento %"] = resumen["Devuelto vencimiento"] / resumen["Colocado bruto"] * 100
resumen["Tasa devolución total %"] = resumen["Devoluciones (todos los motivos)"] / resumen["Colocado bruto"] * 100
resumen["% vencim. sobre devoluciones"] = (resumen["Devuelto vencimiento"]
                                           / resumen["Devoluciones (todos los motivos)"] * 100)

print(resumen.T.to_string(float_format=lambda v: f"{pct(v, 2)}"))
print(f"\nOlímpica devuelve {pct(resumen.loc[OLIMPICA,'Tasa vencimiento %'] / resumen.loc[EXITO,'Tasa vencimiento %'], 1)}× "
      f"más que Éxito en proporción a lo que recibe,")
print(f"moviendo apenas el {pct((resumen.loc[OLIMPICA,'Colocado bruto']/resumen['Colocado bruto'].sum()) * 100, 1)} % del volumen.")

# %% [markdown]
# ## 7. Figura 1 — serie mensual de la tasa
#
# Se reindexa el calendario completo de 24 meses para que los meses **sin devolución
# aparezcan como cero y no como hueco**. Hay que distinguir dos tipos de cero:
#
# - **Cero real:** no hubo ninguna nota crédito por vencimiento en el mes. Es un
#   cero estructural que condiciona el método de pronóstico de la Fase 2.
# - **Cero por líneas sin cantidad (H-03):** sí hubo notas crédito, pero todas
#   vinieron con valor y sin cajas (Éxito ene/2026; Olímpica ene y feb/2026).
#   No se pueden leer como ausencia de devolución. En la figura van con marcador
#   hueco.

# %%
serie = {}
for pdv in TIENDAS:
    c = col_bruta[col_bruta.PDV == pdv].groupby("Mes").Cajas_col.sum().reindex(CAL, fill_value=0)
    d = dev[dev.PDV == pdv].groupby("Mes").Cajas_dev.sum().reindex(CAL, fill_value=0)
    lineas = dev[dev.PDV == pdv].groupby("Mes").size().reindex(CAL, fill_value=0)
    sin_cant = dev[dev.PDV == pdv].groupby("Mes").Solo_valor.sum().reindex(CAL, fill_value=0)
    serie[pdv] = pd.DataFrame({
        "Colocado": c, "Devuelto": d,
        "Tasa": (d / c * 100).replace([np.inf, -np.inf], np.nan),
        "Lineas_nc": lineas, "Lineas_sin_cantidad": sin_cant,
        # Cero real: tasa 0 y ninguna línea de NC en el mes.
        "Cero_real": (d == 0) & (lineas == 0),
        # Cero artificial: tasa 0 pero sí hubo líneas, todas sin cantidad.
        "Cero_sin_cantidad": (d == 0) & (lineas > 0) & (lineas == sin_cant),
    })

mensual = pd.concat(serie, names=["PDV", "Mes"])
mensual.to_csv(PROCESADOS / "analisis_tasa_mensual.csv", encoding="utf-8-sig")
print(mensual.round(2).to_string())
for pdv in TIENDAS:
    print(f"{pdv}: ceros reales = {int(serie[pdv].Cero_real.sum())} meses | "
          f"ceros por líneas sin cantidad = {int(serie[pdv].Cero_sin_cantidad.sum())} meses")

# %%
fig, ax = plt.subplots(figsize=(11, 4.4))
x = np.arange(len(CAL))

for pdv in TIENDAS:
    ax.plot(x, serie[pdv]["Tasa"], color=COLOR[pdv], lw=2, marker="o", ms=4.5,
            mec="white", mew=1.2, label=pdv, zorder=3)
    # Meses cuyo cero viene de líneas sin cantidad: marcador hueco encima.
    art = serie[pdv]["Cero_sin_cantidad"].to_numpy()
    ax.plot(x[art], serie[pdv]["Tasa"].to_numpy()[art], ls="none", marker="o", ms=7,
            mfc="white", mec=COLOR[pdv], mew=1.6, zorder=4)
    ax.annotate(f"{pct(serie[pdv]['Tasa'].iloc[-1])} %",
                (x[-1], serie[pdv]["Tasa"].iloc[-1]), xytext=(8, 0),
                textcoords="offset points", va="center",
                color=COLOR[pdv], fontsize=9.5, fontweight="bold")
ax.plot([], [], ls="none", marker="o", ms=7, mfc="white", mec=GRIS, mew=1.6,
        label="Cero por NC sin cantidad (no es cero real)")

# Anotación del episodio de enero 2025
i_ene = list(CAL).index(pd.Period("2025-01"))
ax.annotate("Ene 2025: 10,43 %\ntras el pico de colocación de diciembre",
            (i_ene, serie[EXITO]["Tasa"].iloc[i_ene]), xytext=(28, -6),
            textcoords="offset points", fontsize=9, color=TINTA_2,
            arrowprops=dict(arrowstyle="-", color=GRIS, lw=0.9))

ax.set_xticks(x[::2])
ax.set_xticklabels(etiquetas_mes(CAL), rotation=0)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.set_ylim(-0.6, 17)
ax.set_xlim(-0.7, len(CAL) + 2.6)
ax.set_title("Fig. 1 · Tasa mensual de devolución por vencimiento")
ax.legend(loc="upper left", fontsize=9.5, ncols=3)
limpiar_eje(ax)
fig.text(0.005, -0.06,
         "Cajas devueltas por vencimiento sobre cajas colocadas brutas, por mes de transacción.\n"
         "Marcador lleno en cero = no hubo nota crédito por vencimiento (cero real). "
         "Marcador hueco = sí hubo notas crédito, pero todas sin cantidad (H-03).",
         fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig1_tasa_mensual.png")
plt.show()

# %% [markdown]
# ## 8. Figura 2 y rezago — colocación mensual y correlación cruzada
#
# Las dos series de colocación van en **paneles separados** porque Éxito mueve 20,6
# veces el volumen de Olímpica; forzarlas a un eje común aplastaría a Olímpica, y
# usar dos escalas en un mismo panel (doble eje) haría la comparación engañosa.
#
# **Correlación cruzada:** se correlaciona la colocación del mes *t−k* con la
# devolución del mes *t*, para *k* = 0…3. Si el vencimiento fuera consecuencia del
# sobrestock, el máximo debe aparecer en un rezago positivo y no en el mes corriente.

# %%
print("Correlación colocación(t−k) vs devolución(t):\n")
rezagos = {}
for pdv in TIENDAS:
    a, b = serie[pdv]["Colocado"], serie[pdv]["Devuelto"]
    r = {k: a.shift(k).corr(b) for k in range(4)}
    rezagos[pdv] = r
    mejor = max(r, key=lambda k: r[k])
    print(f"{pdv:<22} " + "  ".join(f"k={k}: {v:+.3f}" for k, v in r.items())
          + f"   → máximo en k={mejor}")

pico = serie[EXITO]["Colocado"]
print(f"\nDic 2024 en Éxito: {pct(pico.loc[pd.Period('2024-12')], 1)} cajas, "
      f"{pct(pico.loc[pd.Period('2024-12')] / pico.median(), 1)}× la mediana mensual "
      f"({pct(pico.median(), 1)}).")

# %%
fig, axes = plt.subplots(2, 1, figsize=(11, 5.6), sharex=True,
                         gridspec_kw={"hspace": 0.42})
for ax, pdv in zip(axes, TIENDAS):
    ax.bar(x, serie[pdv]["Colocado"], width=0.72, color=COLOR[pdv], zorder=3)
    ax.set_title(f"{pdv} · cajas colocadas brutas", fontsize=10.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{pct(v, 0)}".replace(",", ".")))
    limpiar_eje(ax)

axes[0].annotate("Dic 2024: 14.860 cajas,\n4,5× la mediana mensual",
                 (3, serie[EXITO]["Colocado"].iloc[3]), xytext=(18, -22),
                 textcoords="offset points", fontsize=9, color=TINTA_2,
                 arrowprops=dict(arrowstyle="-", color=GRIS, lw=0.9))
axes[1].set_xticks(x[::2])
axes[1].set_xticklabels(etiquetas_mes(CAL))
titulo_figura(fig, "Fig. 2 · Colocación bruta mensual")
fig.savefig(FIGURAS / "fig2_colocacion_mensual.png")
plt.show()

# %% [markdown]
# ## 9. Figura 3 — cobertura implícita frente a vida útil
#
# Este es el **mecanismo causal** del proyecto y la justificación estadística del
# modelo de stock mínimo.
#
# Para cada SKU y tienda se define:
#
# $$\text{consumo diario} = \frac{\text{cajas colocadas brutas}}{730}
# \qquad
# \text{lote medio} = \frac{\text{cajas colocadas brutas}}{\text{n.º de entregas}}$$
#
# $$\text{cobertura implícita (días)} = \frac{\text{lote medio}}{\text{consumo diario}}$$
#
# La cobertura responde: *¿cuántos días de rotación cubre un pedido típico de este
# SKU en esta tienda?* Si esa cifra supera la vida útil del producto, el lote no
# alcanza a venderse antes de vencerse — la devolución es estructural, no un
# accidente de demanda.
#
# **Supuesto declarado:** el consumo diario se aproxima con la colocación promedio
# porque no se dispone de venta al consumidor. Sobre 24 meses es razonable asumir
# que lo que entra se vende; para calibrar el modelo de la Fase 2 hace falta el
# sell-out real.

# %%
sku = (col_bruta.groupby(["PDV", "SKU", "Material"], as_index=False)
       .agg(Cajas_col=("Cajas_col", "sum"), Entregas=("Fecha entrega", "nunique")))
# Merge EXTERNO a propósito: hay SKU devueltos que no aparecen en colocación
# (efecto de truncamiento, ver sección 11). Un merge interno los descartaría y
# subestimaría tanto el total devuelto como el conteo de referencias críticas.
# El cruce va por PDV + SKU, NUNCA incluyendo el nombre del material: colocación lo
# escribe en mayúsculas y devoluciones en capitalizado, así que usarlo como llave
# duplicaría cada referencia en dos filas.
dev_sku = (dev.groupby(["PDV", "SKU"], as_index=False)
           .agg(Material_dev=("Material", "first"),
                Cajas_dev=("Cajas_dev", "sum"),
                Valor_dev=("Valor_dev", "sum"),
                Eventos=("Cajas_dev", "size")))
sku = sku.merge(dev_sku, on=["PDV", "SKU"], how="outer")
sku["Material"] = sku["Material"].fillna(sku["Material_dev"])
sku = sku.drop(columns="Material_dev")
sku = sku.merge(vu, on="SKU", how="left")
COLS0 = ["Cajas_col", "Entregas", "Cajas_dev", "Valor_dev", "Eventos"]
sku[COLS0] = sku[COLS0].fillna(0)

with np.errstate(divide="ignore", invalid="ignore"):
    sku["Consumo_dia"] = sku.Cajas_col / DIAS_VENTANA
    sku["Lote_medio"] = sku.Cajas_col / sku.Entregas
    sku["Cobertura_dias"] = sku.Lote_medio / sku.Consumo_dia
    sku["Tasa_%"] = np.where(sku.Cajas_col > 0, sku.Cajas_dev / sku.Cajas_col * 100, np.nan)
sku["Excede_vida_util"] = sku.Cobertura_dias > sku.Vida_util_dias

sku.to_csv(PROCESADOS / "analisis_cobertura_sku.csv", index=False, encoding="utf-8-sig")

# La cobertura solo está definida donde hubo colocación observada.
cob = sku[sku.Cajas_col > 0]

grupos = {}
for pdv in TIENDAS:
    s = cob[(cob.PDV == pdv) & cob.Vida_util_dias.notna()]
    g = s.groupby("Excede_vida_util").agg(SKU=("SKU", "size"),
                                          Colocado=("Cajas_col", "sum"),
                                          Devuelto=("Cajas_dev", "sum"))
    g["Tasa_%"] = g.Devuelto / g.Colocado * 100
    g.index = ["Cobertura ≤ vida útil", "Cobertura > vida útil"]
    grupos[pdv] = g
    print(f"-- {pdv}")
    print(g.round(2).to_string())
    print(f"   razón de tasas: {pct(g.loc['Cobertura > vida útil','Tasa_%'] / g.loc['Cobertura ≤ vida útil','Tasa_%'], 1)}×")
    print(f"   cobertura mediana {s.Cobertura_dias.median():.1f} d | "
          f"vida útil mediana {s.Vida_util_dias.median():.0f} d\n")

# %%
fig, ax = plt.subplots(figsize=(8.6, 4.2))
etiquetas = ["Cobertura ≤ vida útil", "Cobertura > vida útil"]
xg, w = np.arange(2), 0.34

for j, pdv in enumerate(TIENDAS):
    vals = [grupos[pdv].loc[e, "Tasa_%"] for e in etiquetas]
    pos = xg + (j - 0.5) * (w + 0.03)
    ax.bar(pos, vals, width=w, color=COLOR[pdv], label=pdv, zorder=3)
    for p, v in zip(pos, vals):
        ax.text(p, v + 0.22, f"{pct(v)} %", ha="center", fontsize=10,
                fontweight="bold", color=COLOR[pdv])

sub = [f"{grupos[EXITO].loc[e,'SKU']:.0f} SKU en Éxito · {grupos[OLIMPICA].loc[e,'SKU']:.0f} en Olímpica"
       for e in etiquetas]
ax.set_xticks(xg)
ax.set_xticklabels([f"{e}\n{s}" for e, s in zip(etiquetas, sub)], fontsize=10)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.set_ylim(0, 10.4)
ax.set_title("Fig. 3 · Tasa de devolución según cobertura del lote frente a vida útil")
ax.legend(loc="upper left", fontsize=9.5)
limpiar_eje(ax)
fig.text(0.005, -0.10,
         "Cobertura implícita = lote medio por entrega ÷ consumo diario promedio del SKU en la tienda.",
         fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig3_cobertura_vida_util.png")
plt.show()

# %% [markdown]
# ### 9.1 Por qué Olímpica está peor: estructura de reposición
#
# La diferencia entre tiendas no está en el producto sino en la frecuencia de
# entrega. Con menos entregas, cada pedido debe cubrir más días y el lote mínimo
# indivisible pesa más sobre una rotación pequeña.

# %%
estructura = pd.DataFrame({
    pdv: {
        "Días con entrega (de 730)": col_bruta[col_bruta.PDV == pdv]["Fecha entrega"].nunique(),
        "Entregas por semana": col_bruta[col_bruta.PDV == pdv]["Fecha entrega"].nunique() / DIAS_VENTANA * 7,
        "SKU distintos colocados": col_bruta[col_bruta.PDV == pdv].SKU.nunique(),
        "Líneas por entrega": len(col_bruta[col_bruta.PDV == pdv]) / col_bruta[col_bruta.PDV == pdv]["Fecha entrega"].nunique(),
        "Lote medio por línea (cajas)": col_bruta[col_bruta.PDV == pdv].Cajas_col.mean(),
        "Cobertura mediana (días)": cob[(cob.PDV == pdv) & cob.Vida_util_dias.notna()].Cobertura_dias.median(),
        "Vida útil mediana (días)": cob[(cob.PDV == pdv) & cob.Vida_util_dias.notna()].Vida_util_dias.median(),
        "Ciclo equivalente (días)": DIAS_VENTANA / col_bruta[col_bruta.PDV == pdv]["Fecha entrega"].nunique(),
    } for pdv in TIENDAS
})
print(estructura.round(2).to_string())

# %% [markdown]
# ### 9.2 Tasa por rango de vida útil
#
# Si la vida útil corta fuera un factor de riesgo por sí sola, la tasa debería caer
# a medida que el producto dura más. Eso ocurre en Olímpica de forma monótona, pero
# no en Éxito: su alta frecuencia de entrega ya absorbe el riesgo de vida útil corta.

# %%
BINS = [0, 90, 120, 180, 270, 10**4]
ETQ = ["≤ 90 d", "91–120 d", "121–180 d", "181–270 d", "> 270 d"]
sku["Rango"] = pd.cut(sku.Vida_util_dias, bins=BINS, labels=ETQ)

rango = []
for pdv in TIENDAS:
    s = sku[(sku.PDV == pdv) & sku.Vida_util_dias.notna()]
    g = s.groupby("Rango", observed=True).agg(SKU=("SKU", "size"),
                                              Colocado=("Cajas_col", "sum"),
                                              Devuelto=("Cajas_dev", "sum"))
    g["Tasa_%"] = g.Devuelto / g.Colocado * 100
    rango.append(g.assign(PDV=pdv))
rango = pd.concat(rango).set_index("PDV", append=True).swaplevel().sort_index()
print(rango.round(2).to_string())

# %% [markdown]
# ## 10. Figura 4 y Pareto — concentración por SKU
#
# El principio de Pareto aplicado a la devolución: se ordenan los SKU de mayor a
# menor cajas devueltas y se busca cuántos acumulan el 80 %. Si la concentración es
# alta, el piloto de la Fase 3 puede acotarse a esas referencias sin perder cobertura
# del problema.

# %%
pareto = {}
for pdv in TIENDAS:
    s = (sku[(sku.PDV == pdv) & (sku.Cajas_dev > 0)]
         .sort_values("Cajas_dev", ascending=False).reset_index(drop=True))
    s["Acum_%"] = s.Cajas_dev.cumsum() / s.Cajas_dev.sum() * 100
    n80 = int((s["Acum_%"] < 80).sum()) + 1
    pareto[pdv] = s
    print(f"{pdv:<22} {n80:>3} SKU de {len(s):>3} ({pct((n80/len(s)) * 100, 1)} %) explican el 80 % de las cajas devueltas")

sku.sort_values(["PDV", "Cajas_dev"], ascending=[True, False]).to_csv(
    PROCESADOS / "analisis_por_sku.csv", index=False, encoding="utf-8-sig")

# %%
def acortar(s, n=42):
    # Colocación escribe el material en MAYÚSCULAS y devoluciones capitalizado.
    # Se homogeneiza para que la figura no mezcle los dos estilos.
    s = " ".join(str(s).split()).title()
    for a, b in [(" Ml", " ml"), ("Ml ", "ml "), (" Of", " OF"), (" Nr ", " NR "),
                 ("Vnr", "VNR"), (" X ", " x ")]:
        s = s.replace(a, b)
    return s if len(s) <= n else s[: n - 1] + "…"


fig, axes = plt.subplots(2, 1, figsize=(11, 7.2), gridspec_kw={"hspace": 0.34})
for ax, pdv in zip(axes, TIENDAS):
    top = pareto[pdv].head(10).iloc[::-1]
    y = np.arange(len(top))
    ax.barh(y, top.Cajas_dev, height=0.68, color=COLOR[pdv], zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([acortar(m) for m in top.Material], fontsize=9)
    for yy, v in zip(y, top.Cajas_dev):
        ax.text(v + top.Cajas_dev.max() * 0.012, yy, pct(v, 1),
                va="center", fontsize=8.5, color=GRIS)
    ax.set_xlim(0, top.Cajas_dev.max() * 1.14)
    ax.set_title(f"{pdv} · cajas devueltas por vencimiento", fontsize=10.5)
    ax.grid(axis="y", visible=False)
    ax.spines[["top", "right", "left"]].set_visible(False)

titulo_figura(fig, "Fig. 4 · Diez SKU con mayor devolución por vencimiento", y=1.01)
fig.text(0.005, -0.03, "Escalas independientes por tienda.", fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig4_pareto_sku.png")
plt.show()

# %% [markdown]
# ### 10.1 Concentración por familia y marca
#
# Los perfiles de las dos tiendas no se parecen, y eso importa: no se puede diseñar
# una regla única de stock mínimo y aplicarla igual en ambas.

# %%
def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").upper()


# El maestro escribe el gramaje de forma inconsistente: "HIT 1.000 ML" y "HIT 1.000ML".
mask_hit1l = dev.Material.map(sin_tildes).str.contains(r"HIT 1.?000\s*ML", regex=True)
print(f"Familia Hit 1.000 ml Tetra: {dev.loc[mask_hit1l, 'SKU'].nunique()} SKU distintos\n")
for pdv in TIENDAS:
    tot = dev.loc[dev.PDV == pdv, "Cajas_dev"].sum()
    fam = dev.loc[mask_hit1l & (dev.PDV == pdv), "Cajas_dev"].sum()
    top_marca = dev[dev.PDV == pdv].groupby("Marca").Cajas_dev.sum().nlargest(1)
    print(f"{pdv}")
    print(f"   familia Hit 1.000 ml Tetra: {pct(fam, 1)} cajas ({pct((fam/tot) * 100, 1)} % de la tienda)")
    print(f"   marca líder: {top_marca.index[0]} con {pct(top_marca.iloc[0], 1)} cajas "
          f"({pct((top_marca.iloc[0]/tot) * 100, 1)} %)")
    print(f"   primer SKU: {pct((pareto[pdv].Cajas_dev.iloc[0]/tot) * 100, 1)} % del total\n")

# Aporte de la familia Hit 1 L al episodio de enero 2025
ene = (dev.Mes == pd.Period("2025-01")) & (dev.PDV == EXITO)
print(f"Enero 2025 en Éxito: {pct(dev.loc[ene,'Cajas_dev'].sum(), 1)} cajas devueltas, "
      f"de las cuales {pct(dev.loc[ene & mask_hit1l,'Cajas_dev'].sum(), 1)} "
      f"({pct((dev.loc[ene & mask_hit1l,'Cajas_dev'].sum()/dev.loc[ene,'Cajas_dev'].sum()) * 100, 1)} %) "
      "son la familia Hit 1.000 ml Tetra.")

# %% [markdown]
# ## 11. Control de calidad — truncamiento por la izquierda
#
# Algunos SKU muestran más devolución que colocación registrada, lo que da tasas
# superiores al 100 %. No es un error de cálculo: con vidas útiles de hasta 360 días,
# el producto devuelto en los primeros meses se colocó **antes** de que empiece la
# ventana de datos (01/09/2024).
#
# Se cuantifica el efecto para acotar hasta dónde son válidas las conclusiones.

# %%
imposibles = sku[(sku.Cajas_dev > 0) & (sku.Cajas_dev > sku.Cajas_col)]
print(f"SKU con devolución > colocación: {len(imposibles)} "
      f"({pct(imposibles.Cajas_dev.sum(), 1)} de {pct(sku.Cajas_dev.sum(), 1)} cajas, "
      f"{pct((imposibles.Cajas_dev.sum()/sku.Cajas_dev.sum()) * 100, 1)} % del total)")
print(imposibles.groupby("PDV").agg(SKU=("SKU", "size"),
                                    Cajas_dev=("Cajas_dev", "sum")).round(1).to_string())
print("\nTop 5 casos:")
print(imposibles.nlargest(5, "Cajas_dev")[
    ["PDV", "SKU", "Material", "Cajas_col", "Cajas_dev", "Vida_util_dias"]
].to_string(index=False))
print("\n→ Concentrados en enero de 2025 y en SKU de vida útil larga (238 d).")
print("  Para el modelo: descartar los primeros meses o acotar a vida útil corta.")

# %% [markdown]
# ## 12. Resumen de resultados
#
# Consolidación de todas las cifras que sustentan el informe.

# %%
CIFRAS = {
    "Ventana (días)": DIAS_VENTANA,
    "Filas de devolución": len(dev),
    "Filas de colocación": len(col),
    "Filas negativas en colocación": len(negativos),
    "% filas negativas": f"{pct((len(negativos)/len(col)) * 100, 1)} %",
    "Cruces negativos↔devoluciones idénticos": f"{cruce.identico.sum()} de {len(cruce)}",
}
for pdv in TIENDAS:
    k = "Éxito" if pdv == EXITO else "Olímpica"
    CIFRAS |= {
        f"[{k}] colocado bruto (cajas)": round(resumen.loc[pdv, "Colocado bruto"], 1),
        f"[{k}] devuelto vencimiento (cajas)": round(resumen.loc[pdv, "Devuelto vencimiento"], 1),
        f"[{k}] tasa de vencimiento": f"{resumen.loc[pdv,'Tasa vencimiento %']:.2f} %",
        f"[{k}] valor devuelto (líneas con cantidad)": f"${pct(resumen.loc[pdv,'Valor devuelto (líneas con cantidad)'], 0)}",
        f"[{k}] valor en NC sin cantidad": f"${pct(resumen.loc[pdv,'Valor en NC sin cantidad'], 0)}",
        f"[{k}] valor devuelto (total GA05)": f"${pct(resumen.loc[pdv,'Valor devuelto (total GA05)'], 0)}",
        f"[{k}] SKU con devolución física": int(resumen.loc[pdv, "SKU con devolución física"]),
        f"[{k}] días con devolución física": int(resumen.loc[pdv, "Días con devolución física"]),
        f"[{k}] líneas NC sin cantidad": int(resumen.loc[pdv, "Líneas NC sin cantidad"]),
        f"[{k}] meses en cero real": int(serie[pdv].Cero_real.sum()),
        f"[{k}] meses en cero por NC sin cantidad": int(serie[pdv].Cero_sin_cantidad.sum()),
        f"[{k}] devoluciones totales (cajas)": round(resumen.loc[pdv, "Devoluciones (todos los motivos)"], 1),
        f"[{k}] vencimiento sobre devoluciones": f"{resumen.loc[pdv,'% vencim. sobre devoluciones']:.1f} %",
        f"[{k}] tasa de devolución total": f"{resumen.loc[pdv,'Tasa devolución total %']:.2f} %",
        f"[{k}] entregas por semana": round(estructura.loc["Entregas por semana", pdv], 1),
        f"[{k}] cobertura mediana (días)": round(estructura.loc["Cobertura mediana (días)", pdv], 1),
        f"[{k}] tasa cobertura ≤ vida útil": f"{grupos[pdv].loc['Cobertura ≤ vida útil','Tasa_%']:.2f} %",
        f"[{k}] tasa cobertura > vida útil": f"{grupos[pdv].loc['Cobertura > vida útil','Tasa_%']:.2f} %",
        f"[{k}] correlación rezago 1 mes": round(rezagos[pdv][1], 3),
    }

for clave, valor in CIFRAS.items():
    print(f"{clave:<48} {valor}")

pd.Series(CIFRAS, name="valor").to_csv(PROCESADOS / "resumen_cifras_diagnostico.csv",
                                       encoding="utf-8-sig")
print(f"\nFiguras en: {FIGURAS}")
print(f"Tablas en:  {PROCESADOS}")

# %% [markdown]
# ---
#
# ## 13. Conclusiones que pasan a la Fase 2
#
# 1. **El pronóstico no puede ser una suavización exponencial sobre la serie diaria.**
#    Hay devolución física en menos de un tercio de los días en Éxito y en menos de
#    un décimo en Olímpica, con ceros reales intercalados (los meses en cero por
#    líneas sin cantidad, H-03, se excluyen de esa lectura). La serie es
#    intermitente: corresponde agregar a semana o mes, o usar métodos de demanda
#    intermitente tipo Croston/SBA. La clasificación ADI–CV² por SKU está en
#    `eda_fase1.py` §5.
#
# 2. **La vida útil entra como tope duro, no como penalización suave.** El grupo
#    cobertura-mayor-que-vida-útil concentra tasas de 7 % a 9 %. La cantidad a pedir
#    debe acotarse arriba por la demanda esperada dentro de la vida útil remanente.
#
# 3. **La frecuencia de entrega es un parámetro por tienda, no un supuesto.** 5,1
#    entregas semanales en Éxito contra 1,9 en Olímpica dan ciclos de 1,4 y 3,7 días
#    equivalentes. El mismo SKU necesita stock mínimo distinto en cada punto de venta.
#
# **Bloqueo:** falta la venta al consumidor (sell-out) o el inventario en tienda.
# Sin eso el consumo diario sigue siendo una aproximación y el modelo no se puede
# calibrar ni validar contra los parámetros tradicionales.
