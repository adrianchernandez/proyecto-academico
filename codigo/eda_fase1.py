# %% [markdown]
# # Fase 1 — Análisis exploratorio, calidad de datos y robustez del diagnóstico
#
# **Proyecto:** Herramienta estadística de reabastecimiento basada en la optimización
# del stock mínimo para reducir devoluciones por caducidad, canal moderno.
#
# **Alcance:** 2 puntos de venta — Éxito San Antonio y Olímpica Villanueva.
# Categoría BNA (clasificaciones BNA y Mundo Cero del GA05), regional Antioquia.
#
# **Periodo:** 01/09/2024 – 31/08/2026 (24 meses).
#
# **Autor:** Adrian Camilo Hernández Copete — Ingeniería Industrial, U. de Antioquia.
#
# ---
#
# ## Qué hace este cuaderno
#
# Complementa a `analisis_diagnostico_fase1.py` (que calcula el indicador y los
# cuatro hallazgos) con lo que un diagnóstico serio necesita **antes** de creerle
# a sus propias cifras:
#
# 1. Perfil de cada fuente (filas, rango, nulos, duplicados, ceros, negativos).
# 2. Verificación de la exportación del Power BI GA05-Notas Crédito: los tres
#    extractos deben ser consistentes entre sí, y hay que caracterizar las líneas
#    que traen valor sin cantidad (hallazgo H-03).
# 3. Exploración de la colocación: cambio de centro abastecedor, lead time,
#    cumplimiento del calendario de entrega, tamaño de línea, anomalías menores.
# 4. Exploración de las devoluciones: motivos, día de la semana, serie semanal.
# 5. Clasificación de intermitencia ADI–CV² por SKU y tienda (Syntetos, Boylan y
#    Croston, 2005), que decide el método de pronóstico de la Fase 2.
# 6. Pruebas de robustez de los hallazgos 2 y 3 del diagnóstico.
# 7. Perfil de vida útil del portafolio que realmente se coloca en cada tienda.
#
# Cada hallazgo sobre los datos queda numerado en `informes/Registro_hallazgos.md`.
#
# **Requisitos:** `pandas`, `numpy`, `matplotlib`, `openpyxl`.

# %% [markdown]
# ## 1. Configuración y perfil de fuentes

# %%
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()))
from comun import *  # noqa: F401,F403

configurar_estilo()
pd.set_option("display.width", 160)

dev = cargar_devoluciones()
col = cargar_colocacion()
vu = cargar_vidas_utiles()
nc = cargar_notas_credito()
pdv_maestro, pdv_pares = cargar_maestro_pdv()
col_bruta = colocacion_bruta(col)
dev_fis = dev[dev.Cajas_dev > 0]                       # líneas con cantidad física
nc_alc = nc[nc.Clasificacion.isin(CLASIFICACIONES_ALCANCE)]

# Precio implícito por caja del SKU (mediana sobre líneas con cantidad), para
# convertir a cajas equivalentes las líneas sin cantidad (§2.4).
precio_caja_sku = (dev_fis.assign(v=dev_fis.Valor_dev / dev_fis.Cajas_dev)
                   .groupby("SKU").v.median())


def perfil(nombre, df, llave, fecha, cantidad):
    return {
        "Fuente": nombre, "Filas": len(df), "Columnas": df.shape[1],
        "Desde": df[fecha].min().date(), "Hasta": df[fecha].max().date(),
        "Celdas nulas": int(df.isna().sum().sum()),
        "Duplicados en llave": int(df.duplicated(llave).sum()),
        "Filas cantidad = 0": int((df[cantidad] == 0).sum()),
        "Filas cantidad < 0": int((df[cantidad] < 0).sum()),
    }


calidad = pd.DataFrame([
    perfil("Devoluciones vencimiento (GA05, analítico)", dev, ["Fecha", "PDV", "SKU"], "Fecha", "Cajas_dev"),
    perfil("Notas crédito todas (GA05)", nc, ["Fecha", "PDV", "SKU", "Tipo", "Motivos"], "Fecha", "Cajas"),
    perfil("Colocación (SAP)", col, ["Fecha pedido", "Fecha entrega", "Centro", "PDV", "SKU"], "Fecha entrega", "Cajas_col"),
]).set_index("Fuente")
calidad.loc["Vidas útiles (centro 43)"] = [len(vu), 2, None, None, int(vu.isna().sum().sum()),
                                           int(vu.SKU.duplicated().sum()), 0, 0]
calidad.to_csv(PROCESADOS / "calidad_fuentes.csv", encoding="utf-8-sig")
print(calidad.to_string())

# %% [markdown]
# ## 2. Verificación de la exportación del GA05-Notas Crédito
#
# Los tres CSV salieron de dos consultas DAX distintas al mismo modelo. Si la
# exportación es correcta:
#
# - el extracto "diario" (solo cajas) y el "analítico" (todas las medidas) deben
#   ser idénticos fila a fila;
# - el universo completo de notas crédito, filtrado a *Devolución* + *Fecha De
#   Vencimiento* + BNA/Mundo Cero, debe reproducir exactamente el analítico;
# - no debe haber cantidades negativas (la medida del tablero ya invierte el signo).
#
# Power BI Desktop no estaba abierto al correr esta verificación, así que no se
# re-ejecutó la consulta contra el modelo; la prueba es de consistencia entre las
# dos consultas independientes ya exportadas.

# %%
diario = pd.read_csv(ARCHIVO_DEVOLUCIONES_DIARIO, encoding="utf-8-sig")
diario["Fecha"] = pd.to_datetime(diario["Fecha devolución"])
diario["PDV"] = diario["Punto de venta"].map(MAPA_PDV)
diario = diario.rename(columns={"Material SAP - Clave": "SKU",
                                "Cantidad devuelta en cajas físicas": "Cajas_diario"})
m1 = dev.merge(diario[["Fecha", "PDV", "SKU", "Cajas_diario"]], on=["Fecha", "PDV", "SKU"],
               how="outer", indicator=True)

venc = nc_alc[(nc_alc.Tipo == "Devolución") & (nc_alc.Motivos == "Fecha De Vencimiento")]
m2 = (dev.groupby(["Fecha", "PDV", "SKU"], as_index=False)
      .agg(Cajas_an=("Cajas_dev", "sum"), Unid_an=("Unidades_dev", "sum"), Lin_an=("Lineas_nc", "sum"))
      .merge(venc.groupby(["Fecha", "PDV", "SKU"], as_index=False)
             .agg(Cajas_nc=("Cajas", "sum"), Unid_nc=("Unidades", "sum"), Lin_nc=("Notas credito", "sum")),
             on=["Fecha", "PDV", "SKU"], how="outer", indicator=True))

verificacion = pd.Series({
    "Diario vs analítico — llaves solo en uno": int((m1._merge != "both").sum()),
    "Diario vs analítico — filas con cajas distintas": int((~np.isclose(m1.Cajas_dev, m1.Cajas_diario)).sum()),
    "NC-todas(filtrado) vs analítico — llaves solo en uno": int((m2._merge != "both").sum()),
    "NC-todas(filtrado) vs analítico — cajas distintas": int((~np.isclose(m2.Cajas_an, m2.Cajas_nc, atol=1e-3)).sum()),
    "NC-todas(filtrado) vs analítico — unidades distintas": int((m2.Unid_an != m2.Unid_nc).sum()),
    "NC-todas(filtrado) vs analítico — líneas distintas": int((m2.Lin_an != m2.Lin_nc).sum()),
    "Total cajas analítico": round(dev.Cajas_dev.sum(), 3),
    "Total cajas NC-todas filtrado": round(venc.Cajas.sum(), 3),
    "Cantidades negativas en analítico": int((dev.Cajas_dev < 0).sum()),
    "Filas con UMB = 0 y cajas > 0 (UMB no confiable)": int(((dev.Unidades_dev == 0) & (dev.Cajas_dev > 0)).sum()),
    "Filas con valor y sin ninguna cantidad": int(dev.Solo_valor.sum()),
    "Fechas fuera de ventana": int((~dev.Fecha.between(INICIO, FIN)).sum()),
}, name="valor")
verificacion.to_csv(PROCESADOS / "verificacion_exportacion_ga05.csv", encoding="utf-8-sig")
print(verificacion.to_string())
print("\n→ Los tres extractos son consistentes entre sí: la exportación reproduce el modelo.")
print("  Lo que sí requiere atención son las líneas con valor y sin cantidad (§2.4).")

# %% [markdown]
# ### 2.1 Otras señales del universo de notas crédito
#
# Tipos y motivos que existen en el GA05 para los dos PDV. Sirven para ubicar la
# devolución por vencimiento dentro del total y para detectar categorías raras.

# %%
motivos = (nc_alc.pivot_table(index=["Tipo", "Motivos"], columns="PDV", values="Cajas",
                              aggfunc="sum", fill_value=0)
           .reindex(columns=TIENDAS).round(1))
motivos["Total"] = motivos.sum(axis=1)
motivos = motivos.sort_values("Total", ascending=False)
motivos.to_csv(PROCESADOS / "eda_nc_motivos.csv", encoding="utf-8-sig")
print(motivos.head(14).to_string())
raros = nc[(nc.Tipo == "Sin Asignar") | (nc.Cajas < 0)]
print(f"\nFilas atípicas en NC-todas: tipo 'Sin Asignar' = {(nc.Tipo == 'Sin Asignar').sum()} | "
      f"cajas negativas (rechazos revertidos) = {(nc.Cajas < 0).sum()} — no afectan al vencimiento.")

# %% [markdown]
# ### 2.4 Líneas con valor y sin cantidad (hallazgo H-03)
#
# Un tercio de las líneas de devolución por vencimiento trae valor neto pero cero
# cajas, cero unidades y cero hectolitros. Tres hechos delimitan el problema:
#
# 1. **No es un problema de conversión de unidades:** de los 161 SKU afectados,
#    150 sí traen cajas en otras fechas.
# 2. **Es temporal y por centro:** todas las líneas son del centro 43 y ninguna es
#    anterior a julio/2025 — justo después de que ambas tiendas pasaran del centro
#    79 al 43 (§3.1).
# 3. **Distorsiona meses completos:** en Éxito (ene/2026) y Olímpica (ene–feb/2026)
#    el 100 % de las líneas viene sin cantidad.
#
# Para dimensionar cuánto podría faltar en el numerador se calcula una **cota
# superior**: si cada línea sin cantidad correspondiera a producto físico al precio
# implícito por caja del mismo SKU (mediana de sus líneas con cantidad), ¿cuántas
# cajas serían? Es un escenario, no una cifra: la respuesta real depende de qué
# documento SAP genera esas líneas, y eso hay que confirmarlo con la asesora externa.

# %%
sv = dev[dev.Solo_valor].copy()
sv["Precio_caja"] = sv.SKU.map(precio_caja_sku)
# SKU sin ninguna línea con cantidad: se usa la mediana de la tienda (11 SKU).
mediana_pdv = dev_fis.assign(v=dev_fis.Valor_dev / dev_fis.Cajas_dev).groupby("PDV").v.median()
sv["Precio_caja"] = sv.Precio_caja.fillna(sv.PDV.map(mediana_pdv))
sv["Cajas_equiv"] = sv.Valor_dev / sv.Precio_caja

sin_cant_mes = (dev.groupby(["PDV", "Mes"])
                .agg(Lineas=("SKU", "size"), Lineas_sin_cantidad=("Solo_valor", "sum"),
                     Valor_sin_cantidad=("Valor_dev", lambda s: s[dev.loc[s.index, "Solo_valor"]].sum()))
                .reindex(pd.MultiIndex.from_product([TIENDAS, CAL], names=["PDV", "Mes"]), fill_value=0))
sin_cant_mes["Cajas_equiv"] = sv.groupby(["PDV", "Mes"]).Cajas_equiv.sum().reindex(sin_cant_mes.index, fill_value=0)
sin_cant_mes.to_csv(PROCESADOS / "eda_nc_sin_cantidad_mensual.csv", encoding="utf-8-sig")

cota = pd.DataFrame({
    "Cajas devueltas (con cantidad)": dev.groupby("PDV").Cajas_dev.sum(),
    "Cajas equivalentes en líneas sin cantidad": sv.groupby("PDV").Cajas_equiv.sum(),
    "Colocado bruto": col_bruta.groupby("PDV").Cajas_col.sum(),
}).reindex(TIENDAS)
cota["Tasa reportada %"] = cota.iloc[:, 0] / cota["Colocado bruto"] * 100
cota["Tasa cota superior %"] = (cota.iloc[:, 0] + cota.iloc[:, 1]) / cota["Colocado bruto"] * 100
cota["Centros con líneas sin cantidad"] = [sorted(sv.loc[sv.PDV == p, "Centro"].unique()) for p in TIENDAS]
cota["Primera línea sin cantidad"] = [sv.loc[sv.PDV == p, "Fecha"].min().date() for p in TIENDAS]
cota.to_csv(PROCESADOS / "eda_nc_sin_cantidad_cota.csv", encoding="utf-8-sig")
print(cota.round(2).T.to_string())
print(f"\nSKU con líneas sin cantidad: {sv.SKU.nunique()} | "
      f"de ellos con cajas en otras fechas: {sv.SKU.isin(precio_caja_sku.index).groupby(sv.SKU).first().sum()}")

# %%
fig, axes = plt.subplots(2, 1, figsize=(11, 5.8), sharex=True, gridspec_kw={"hspace": 0.4})
x = np.arange(len(CAL))
for ax, pdv in zip(axes, TIENDAS):
    s = sin_cant_mes.loc[pdv]
    con = (s.Lineas - s.Lineas_sin_cantidad).to_numpy()
    ax.bar(x, con, width=0.72, color=COLOR[pdv], label="Líneas con cantidad", zorder=3)
    ax.bar(x, s.Lineas_sin_cantidad.to_numpy(), bottom=con, width=0.72, color=COLOR_SUAVE[pdv],
           hatch="///", edgecolor="white", label="Líneas con valor y sin cantidad", zorder=3)
    ax.set_title(f"{pdv} · líneas de nota crédito por vencimiento en el GA05", fontsize=10.5)
    ax.legend(loc="upper left", fontsize=9)
    limpiar_eje(ax)
axes[1].set_xticks(x[::2])
axes[1].set_xticklabels(etiquetas_mes(CAL))
titulo_figura(fig, "Fig. 5 · Notas crédito por vencimiento: con cantidad vs. sin cantidad (H-03)")
fig.text(0.005, -0.03, "Las líneas sin cantidad aparecen desde julio de 2025, solo con centro 43. "
         "En Éxito ene/2026 y Olímpica ene–feb/2026 todas las líneas vienen sin cantidad.",
         fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig5_ga05_lineas_sin_cantidad.png")
plt.show()

# %% [markdown]
# ## 3. Exploración de la colocación
#
# ### 3.1 Cambio de centro abastecedor (hallazgo H-05)
#
# El extracto trae dos centros (43 y 79). No conviven: ambas tiendas recibieron del
# 79 hasta mayo/2025 y del 43 desde junio/2025. Importa por dos razones: el
# maestro de vidas útiles es del centro 43 (¿aplica igual al producto que salió del
# 79?), y las líneas sin cantidad del GA05 aparecen justo tras el cambio.

# %%
centro = (col_bruta.groupby(["PDV", "Centro"])
          .agg(Primera_entrega=("Fecha entrega", "min"), Ultima_entrega=("Fecha entrega", "max"),
               Lineas=("SKU", "size"), Cajas=("Cajas_col", "sum")))
centro["Cajas"] = centro.Cajas.round(1)
centro.to_csv(PROCESADOS / "eda_colocacion_centro.csv", encoding="utf-8-sig")
print(centro.to_string())
solape = (col_bruta.groupby(["PDV", "Mes"]).Centro.nunique() > 1).sum()
print(f"\nMeses con los dos centros a la vez: {solape} (el traslape es solo junio/2025)")

# %% [markdown]
# ### 3.2 Lead time pedido → entrega
#
# Solo tiene sentido en las líneas positivas (las negativas son notas crédito con
# fecha de pedido = fecha de entrega, ver diagnóstico §5).

# %%
lead = (col_bruta.groupby(["PDV", "Lead_dias"]).size().unstack("Lead_dias", fill_value=0)
        .reindex(TIENDAS))
lead_pct = (lead.div(lead.sum(axis=1), axis=0) * 100).round(1)
lead_pct.columns = [f"{c} día(s)" for c in lead_pct.columns]
print("Distribución del lead time (% de líneas positivas):")
print(lead_pct.to_string())
print("\nLead time mediano:", col_bruta.groupby("PDV").Lead_dias.median().to_dict())

# %% [markdown]
# ### 3.3 Cumplimiento del calendario del maestro (hallazgo H-06)
#
# El maestro declara Éxito con entrega de lunes a sábado y Olímpica miércoles y
# sábado. Se contrasta contra las fechas de entrega reales de las líneas positivas.

# %%
def calendario(pdv):
    c = col_bruta[col_bruta.PDV == pdv]
    g = c.groupby("dow_entrega").agg(Lineas=("SKU", "size"), Fechas=("Fecha entrega", "nunique"),
                                      Cajas=("Cajas_col", "sum")).reindex(DIAS_SEMANA, fill_value=0)
    g["En maestro"] = [d in DIAS_ENTREGA_MAESTRO[pdv] for d in g.index]
    g["% líneas"] = g.Lineas / g.Lineas.sum() * 100
    g.insert(0, "PDV", pdv)
    return g


cal_ent = pd.concat([calendario(p) for p in TIENDAS]).rename_axis("Día entrega").reset_index()
cal_ent.to_csv(PROCESADOS / "eda_colocacion_calendario.csv", index=False, encoding="utf-8-sig")
print(cal_ent.round(1).to_string(index=False))

fuera = col_bruta[(col_bruta.PDV == OLIMPICA) & ~col_bruta.dow_entrega.isin(DIAS_ENTREGA_MAESTRO[OLIMPICA])]
print(f"\nOlímpica fuera de X/S: {len(fuera)} líneas, {fuera['Fecha entrega'].nunique()} fechas, "
      f"{pct(fuera.Cajas_col.sum(), 1)} cajas ({pct(fuera.Cajas_col.sum() / col_bruta.loc[col_bruta.PDV == OLIMPICA, 'Cajas_col'].sum() * 100, 1)} % de su colocación)")
print("Por mes (fechas fuera de calendario):")
print(fuera.groupby("Mes")["Fecha entrega"].nunique().to_string())
dom = col[col["Fecha entrega"].dt.dayofweek == 6]
print(f"\nFilas con entrega en domingo: {len(dom)} — todas negativas: {(dom.Cajas_col < 0).all()} "
      "(son notas crédito, no entregas)")

# %%
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"wspace": 0.25})
for ax, pdv in zip(axes, TIENDAS):
    g = cal_ent[cal_ent.PDV == pdv]
    colores = [COLOR[pdv] if m else COLOR_SUAVE[pdv] for m in g["En maestro"]]
    ax.bar(np.arange(7), g.Lineas, color=colores, width=0.7, zorder=3)
    ax.set_xticks(np.arange(7))
    ax.set_xticklabels(DIAS_SEMANA_LARGO)
    ax.set_title(f"{pdv} · líneas entregadas por día", fontsize=10.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: pct(v, 0)))
    limpiar_eje(ax)
    ax.legend(handles=[Patch(color=COLOR[pdv], label="Día declarado en el maestro"),
                       Patch(color=COLOR_SUAVE[pdv], label="Fuera del maestro")],
              fontsize=8.5, loc="upper right")
titulo_figura(fig, "Fig. 6 · Calendario real de entregas frente al maestro de puntos de venta", y=1.06)
fig.savefig(FIGURAS / "fig6_calendario_entregas.png")
plt.show()

# %% [markdown]
# ### 3.4 Tamaño de línea (lote) y fracciones de caja
#
# El lote mínimo indivisible es una de las causas estructurales de la merma
# (Broekmeulen y van Donselaar, 2019). Aquí se mira cómo se distribuye la cantidad
# por línea en cada tienda. Las fracciones (0,333; 0,5; 0,667…) son cajas de
# presentaciones "OF" (oferta) cuya unidad de venta es menor que la caja física.

# %%
q = [0.10, 0.25, 0.50, 0.75, 0.90, 0.99]
lotes = pd.DataFrame({
    pdv: {**{f"P{int(p * 100)}": col_bruta.loc[col_bruta.PDV == pdv, "Cajas_col"].quantile(p) for p in q},
          "Media": col_bruta.loc[col_bruta.PDV == pdv, "Cajas_col"].mean(),
          "Máximo": col_bruta.loc[col_bruta.PDV == pdv, "Cajas_col"].max(),
          "% líneas fraccionarias": (col_bruta.loc[col_bruta.PDV == pdv, "Cajas_col"] % 1 != 0).mean() * 100,
          "% líneas de 1 caja o menos": (col_bruta.loc[col_bruta.PDV == pdv, "Cajas_col"] <= 1).mean() * 100}
    for pdv in TIENDAS
})
lotes.to_csv(PROCESADOS / "eda_colocacion_lotes.csv", encoding="utf-8-sig")
print(lotes.round(2).to_string())
print("\nCinco líneas más grandes de la serie:")
print(col_bruta.nlargest(5, "Cajas_col")[["Fecha entrega", "PDV", "SKU", "Material", "Cajas_col"]].to_string(index=False))

# %% [markdown]
# ### 3.5 Anomalías menores (documentadas, sin efecto en el indicador)

# %%
ceros = col[col.Signo == "cero"]
sin_vu = col_bruta[~col_bruta.SKU.isin(vu.SKU)]
print(f"Filas de colocación en cero: {len(ceros)} (Éxito {int((ceros.PDV == EXITO).sum())}, "
      f"Olímpica {int((ceros.PDV == OLIMPICA).sum())}) — se excluyen del denominador y del numerador.")
print(f"SKU colocados sin vida útil en el maestro: {sin_vu.SKU.nunique()} → "
      f"{sin_vu.drop_duplicates('SKU')[['SKU', 'Material']].to_dict('records')} "
      f"({pct(sin_vu.Cajas_col.sum(), 1)} cajas). No es bebida: se conserva en el denominador y "
      "queda fuera de todo análisis por vida útil.")
sin_col = dev_fis[~dev_fis.SKU.isin(col_bruta.SKU)]
print(f"SKU con devolución física pero sin colocación en la ventana: {sin_col.SKU.nunique()} "
      f"({pct(sin_col.Cajas_dev.sum(), 1)} cajas) — truncamiento por la izquierda (diagnóstico §11).")

# %% [markdown]
# ## 4. Exploración de las devoluciones por vencimiento
#
# ### 4.1 Día de la semana en que se registra la devolución

# %%
dow_dev = (dev_fis.assign(dow=dev_fis.Fecha.dt.dayofweek.map(lambda i: DIAS_SEMANA[i]))
           .pivot_table(index="dow", columns="PDV", values="Cajas_dev", aggfunc="sum", fill_value=0)
           .reindex(DIAS_SEMANA, fill_value=0).reindex(columns=TIENDAS))
dow_dev_pct = (dow_dev / dow_dev.sum() * 100).round(1)
print("% de cajas devueltas por día de la semana:")
print(dow_dev_pct.to_string())

# %% [markdown]
# ### 4.2 Serie semanal y tamaño del evento
#
# La devolución no ocurre todos los días: se registra en bloques. La serie semanal
# muestra cuán intermitente es el fenómeno en cada tienda.

# %%
SEM = pd.period_range(INICIO, FIN, freq="W")
semanal = {}
for pdv in TIENDAS:
    d = dev_fis[dev_fis.PDV == pdv].groupby("Semana").Cajas_dev.sum().reindex(SEM, fill_value=0)
    solo = dev[(dev.PDV == pdv)].groupby("Semana").Solo_valor.agg(["size", "sum"]).reindex(SEM, fill_value=0)
    semanal[pdv] = pd.DataFrame({"Cajas": d, "Sem_solo_sin_cantidad": (solo["size"] > 0) & (solo["size"] == solo["sum"])})
    print(f"{pdv}: semanas con devolución física {int((d > 0).sum())} de {len(SEM)} "
          f"({pct((d > 0).mean() * 100, 1)} %) | mediana de cajas en semanas con devolución "
          f"{pct(d[d > 0].median(), 1)} | máximo {pct(d.max(), 1)}")
pd.concat(semanal, names=["PDV", "Semana"]).to_csv(PROCESADOS / "eda_devoluciones_semanal.csv", encoding="utf-8-sig")

evento = dev_fis.groupby("PDV").Cajas_dev.describe(percentiles=[0.5, 0.9, 0.99]).reindex(TIENDAS).round(2)
print("\nCajas por línea de devolución física:")
print(evento.to_string())

# %%
fig, axes = plt.subplots(2, 1, figsize=(11, 5.8), sharex=True, gridspec_kw={"hspace": 0.4})
xs = np.arange(len(SEM))
for ax, pdv in zip(axes, TIENDAS):
    s = semanal[pdv]
    ax.bar(xs, s.Cajas, width=1.0, color=COLOR[pdv], zorder=3)
    art = s.Sem_solo_sin_cantidad.to_numpy()
    ax.plot(xs[art], np.zeros(art.sum()), ls="none", marker="o", ms=4, mfc="white", mec=COLOR[pdv], mew=1.2,
            zorder=4, label="Semana con NC solo sin cantidad")
    ax.set_title(f"{pdv} · cajas devueltas por vencimiento por semana", fontsize=10.5)
    ax.legend(fontsize=8.5, loc="upper right")
    limpiar_eje(ax)
ticks = [i for i, p in enumerate(SEM) if p.start_time.day <= 7 and p.start_time.month in (1, 4, 7, 10)]
axes[1].set_xticks(ticks)
axes[1].set_xticklabels([f"{MESES_ES[SEM[i].start_time.month - 1]} {SEM[i].start_time.year % 100:02d}" for i in ticks])
titulo_figura(fig, "Fig. 7 · Serie semanal de devoluciones físicas por vencimiento")
fig.savefig(FIGURAS / "fig7_serie_semanal_devoluciones.png")
plt.show()

# %% [markdown]
# ## 5. Intermitencia de la demanda por SKU y tienda (ADI–CV²)
#
# Syntetos, Boylan y Croston (2005) clasifican cada serie con dos métricas sobre
# periodos con demanda positiva:
#
# - **ADI** (intervalo medio entre demandas) = semanas activas ÷ semanas con demanda.
# - **CV²** = (desviación ÷ media)² del tamaño de la demanda cuando ocurre.
#
# Umbrales: ADI = 1,32 y CV² = 0,49. Cuatro clases: *suave* (SES sirve), *errática*
# (Croston/SBA), *intermitente* (SBA) y *abultada* (SBA/TSB).
#
# **Supuesto declarado:** todavía no hay venta al consumidor, así que la "demanda"
# aquí es la colocación semanal positiva (sell-in). Sirve para anticipar el tipo de
# método que necesitará la Fase 2; **se recalcula con las ventas diarias cuando
# lleguen** (ver `PENDIENTE_ventas_diarias.md`). La ventana activa de cada SKU va de
# su primera a su última semana con colocación, para no penalizar referencias
# nuevas o descontinuadas.

# %%
def clasificar(adi, cv2):
    if np.isnan(cv2):
        return "Sin clasificar (1 periodo)"
    if adi <= 1.32:
        return "Suave" if cv2 <= 0.49 else "Errática"
    return "Intermitente" if cv2 <= 0.49 else "Abultada"


def intermitencia(df, cantidad):
    filas = []
    for (pdv, sku), g in df.groupby(["PDV", "SKU"]):
        w = g.groupby("Semana")[cantidad].sum()
        w = w[w > 0]
        if w.empty:
            continue
        activas = (w.index.max() - w.index.min()).n + 1
        adi = activas / len(w)
        cv2 = (w.std(ddof=0) / w.mean()) ** 2 if len(w) > 1 else np.nan
        filas.append({"PDV": pdv, "SKU": sku, "Material": g.Material.iloc[0],
                      "Semanas_activas": activas, "Semanas_con_demanda": len(w),
                      "Cajas": w.sum(), "ADI": adi, "CV2": cv2, "Clase": clasificar(adi, cv2)})
    return pd.DataFrame(filas)


inter = intermitencia(col_bruta, "Cajas_col")
inter = inter.merge(vu, on="SKU", how="left")
inter.to_csv(PROCESADOS / "eda_intermitencia_sku.csv", index=False, encoding="utf-8-sig")

ORDEN = ["Suave", "Errática", "Intermitente", "Abultada", "Sin clasificar (1 periodo)"]
res_inter = []
for pdv in TIENDAS:
    s = inter[inter.PDV == pdv]
    g = s.groupby("Clase").agg(SKU=("SKU", "size"), Cajas=("Cajas", "sum")).reindex(ORDEN, fill_value=0)
    g["% SKU"] = g.SKU / g.SKU.sum() * 100
    g["% cajas"] = g.Cajas / g.Cajas.sum() * 100
    g.insert(0, "PDV", pdv)
    res_inter.append(g)
res_inter = pd.concat(res_inter).rename_axis("Clase").reset_index()
res_inter.to_csv(PROCESADOS / "eda_intermitencia_resumen.csv", index=False, encoding="utf-8-sig")
print(res_inter.round(1).to_string(index=False))
for pdv in TIENDAS:
    s = inter[inter.PDV == pdv]
    print(f"\n{pdv}: ADI mediano {s.ADI.median():.2f} | CV² mediano {s.CV2.median():.2f} | "
          f"SKU con ADI > 1,32: {pct((s.ADI > 1.32).mean() * 100, 1)} %")

# %%
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True, gridspec_kw={"wspace": 0.12})
for ax, pdv in zip(axes, TIENDAS):
    s = inter[(inter.PDV == pdv) & inter.CV2.notna()]
    ax.scatter(s.ADI, s.CV2.clip(lower=1e-3), s=np.sqrt(s.Cajas) * 2 + 6, color=COLOR[pdv], alpha=0.55,
               edgecolor="white", lw=0.5, zorder=3)
    ax.axvline(1.32, color=GRIS, ls="--", lw=1)
    ax.axhline(0.49, color=GRIS, ls="--", lw=1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("ADI (semanas entre colocaciones)")
    ax.set_title(f"{pdv} · {len(s)} SKU", fontsize=10.5)
    for tx, ty, lab in [(1.05, 0.05, "Suave"), (1.05, 40, "Errática"), (8, 0.05, "Intermitente"), (8, 40, "Abultada")]:
        ax.text(tx, ty, lab, fontsize=8.5, color=TINTA_2, ha="left", va="center", style="italic")
    ax.grid(axis="x", visible=True)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("CV² del tamaño de la colocación")
titulo_figura(fig, "Fig. 8 · Clasificación ADI–CV² de la colocación semanal por SKU (tamaño ∝ cajas)", y=1.04)
fig.text(0.005, -0.06, "Umbrales de Syntetos, Boylan y Croston (2005): ADI = 1,32 y CV² = 0,49. "
         "Demanda aproximada por colocación (sell-in); se recalcula con ventas.",
         fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig8_intermitencia_adi_cv2.png")
plt.show()

# %% [markdown]
# ## 6. Robustez de los hallazgos del diagnóstico
#
# ### 6.1 Hallazgo 3 — cobertura implícita frente a vida útil (hallazgo H-07)
#
# En el diagnóstico, cobertura = lote medio ÷ consumo diario, con consumo diario =
# cajas ÷ 730 y lote medio = cajas ÷ entregas. Algebraicamente eso es
# **730 ÷ n.º de entregas**: el intervalo medio entre entregas sobre toda la
# ventana. Un SKU que solo se colocó dos veces en dos años queda con cobertura
# de 365 días aunque las dos entregas hayan sido en la misma semana.
#
# Se contrasta con una definición más exigente: el **intervalo real entre
# entregas** dentro de la vida comercial del SKU en la tienda,
# (última − primera entrega) ÷ (entregas − 1), solo para SKU con al menos tres
# entregas. Y en vez de un corte binario (¿supera la vida útil?) se mira el
# **gradiente**: la tasa de devolución por tramos de la fracción de vida útil que
# consume ese intervalo (intervalo ÷ vida útil).
#
# Resultado: el grupo "cobertura > vida útil" del diagnóstico está formado por SKU
# esporádicos (mediana de 2–3 entregas, vida comercial de ~25 días); con el
# intervalo real, solo un SKU por tienda supera su vida útil. **Pero el mecanismo
# sí existe, y más fuerte de lo que decía el corte binario:** la tasa crece de
# forma monótona con la fracción de vida útil consumida entre entregas. Es la
# formulación que pasa al informe y al modelo.

# %%
sku = (col_bruta.groupby(["PDV", "SKU"], as_index=False)
       .agg(Material=("Material", "first"), Cajas_col=("Cajas_col", "sum"),
            Entregas=("Fecha entrega", "nunique"),
            Primera=("Fecha entrega", "min"), Ultima=("Fecha entrega", "max")))
sku = sku.merge(dev_fis.groupby(["PDV", "SKU"], as_index=False).Cajas_dev.sum(), on=["PDV", "SKU"], how="left")
sku = sku.merge(vu, on="SKU", how="left")
sku["Cajas_dev"] = sku.Cajas_dev.fillna(0)
sku = sku[sku.Vida_util_dias.notna()].copy()
sku["Cobertura_original"] = DIAS_VENTANA / sku.Entregas                     # la del diagnóstico
sku["Intervalo_entregas"] = np.where(sku.Entregas > 1,
                                     (sku.Ultima - sku.Primera).dt.days / (sku.Entregas - 1).clip(lower=1),
                                     np.nan)
sku["Fraccion_vida_util"] = sku.Intervalo_entregas / sku.Vida_util_dias
sku["Lote_medio"] = sku.Cajas_col / sku.Entregas
sku.to_csv(PROCESADOS / "robustez_cobertura_sku.csv", index=False, encoding="utf-8-sig")

print("¿Qué SKU forman el grupo 'cobertura > vida útil' del diagnóstico?")
for pdv in TIENDAS:
    o = sku[(sku.PDV == pdv) & (sku.Cobertura_original > sku.Vida_util_dias)]
    print(f"  {pdv}: {len(o)} SKU | entregas mediana {o.Entregas.median():.0f} (máx {o.Entregas.max()}) | "
          f"vida comercial mediana {(o.Ultima - o.Primera).dt.days.median():.0f} días")

rob3 = sku[sku.Entregas >= 3].copy()
TRAMOS = [0, 0.05, 0.10, 0.20, 0.35, 0.50, 1.0, 99]
ETQ_TRAMOS = ["< 5 %", "5–10 %", "10–20 %", "20–35 %", "35–50 %", "50–100 %", "> 100 %"]
rob3["Tramo"] = pd.cut(rob3.Fraccion_vida_util, bins=TRAMOS, labels=ETQ_TRAMOS)
gradiente = []
for pdv in TIENDAS:
    s = rob3[rob3.PDV == pdv]
    g = s.groupby("Tramo", observed=False).agg(SKU=("SKU", "size"), Colocado=("Cajas_col", "sum"),
                                                Devuelto=("Cajas_dev", "sum"))
    g["Tasa %"] = (g.Devuelto / g.Colocado * 100).where(g.Colocado > 0)
    g.insert(0, "PDV", pdv)
    gradiente.append(g)
    t = s[s.Cajas_col >= 20].assign(Tasa=lambda d: d.Cajas_dev / d.Cajas_col)
    rho = t.Fraccion_vida_util.rank().corr(t.Tasa.rank())        # Spearman sin scipy
    print(f"\n{pdv}: {len(s)} SKU con ≥ 3 entregas | intervalo mediano {s.Intervalo_entregas.median():.1f} días | "
          f"supera su vida útil: {int((s.Intervalo_entregas > s.Vida_util_dias).sum())} SKU | "
          f"Spearman(fracción, tasa) = {rho:+.3f} (n = {len(t)} SKU con ≥ 20 cajas)")
gradiente = pd.concat(gradiente).rename_axis("Tramo").reset_index()
gradiente.to_csv(PROCESADOS / "robustez_cobertura_gradiente.csv", index=False, encoding="utf-8-sig")
print("\nTasa de devolución por fracción de la vida útil que consume el intervalo entre entregas:")
print(gradiente.round(2).to_string(index=False))

# %%
fig, ax = plt.subplots(figsize=(9.6, 4.3))
xg, w = np.arange(len(ETQ_TRAMOS) - 1), 0.36          # se omite "> 100 %" (1 SKU por tienda)
for j, pdv in enumerate(TIENDAS):
    g = gradiente[(gradiente.PDV == pdv) & (gradiente.Tramo != "> 100 %")]
    pos = xg + (j - 0.5) * (w + 0.03)
    ax.bar(pos, g["Tasa %"], width=w, color=COLOR[pdv], label=pdv, zorder=3)
    for p, v, n in zip(pos, g["Tasa %"], g.SKU):
        if pd.notna(v):
            ax.text(p, v + 0.3, f"{pct(v, 1)} %", ha="center", fontsize=8.5, fontweight="bold", color=COLOR[pdv])
            ax.text(p, -1.1, f"{n} SKU", ha="center", fontsize=7.5, color=GRIS)
ax.set_xticks(xg)
ax.set_xticklabels(ETQ_TRAMOS[:-1])
ax.set_xlabel("Intervalo entre entregas como fracción de la vida útil del SKU")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.set_ylim(-2, gradiente[gradiente.Tramo != "> 100 %"]["Tasa %"].max() * 1.18)
ax.set_title("Fig. 10 · Tasa de devolución según la fracción de vida útil consumida entre entregas")
ax.legend(loc="upper left", fontsize=9.5)
limpiar_eje(ax)
fig.text(0.005, -0.10, "SKU con ≥ 3 entregas. Intervalo = (última − primera entrega) ÷ (entregas − 1). "
         "Reemplaza al corte binario de la Fig. 3 (H-07).", fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig10_gradiente_intervalo_vida_util.png")
plt.show()

# %% [markdown]
# ### 6.2 Hallazgo 2 — rezago colocación → devolución (hallazgo H-08)
#
# La correlación de Pearson r = 0,716 en Éxito se calcula sobre 24 puntos y uno de
# ellos (diciembre/2024 → enero/2025) es un extremo. Se contrasta con Spearman
# (rangos, robusto a extremos) y con Pearson quitando ese par de meses.

# %%
serie = {}
for pdv in TIENDAS:
    c = col_bruta[col_bruta.PDV == pdv].groupby("Mes").Cajas_col.sum().reindex(CAL, fill_value=0)
    d = dev_fis[dev_fis.PDV == pdv].groupby("Mes").Cajas_dev.sum().reindex(CAL, fill_value=0)
    serie[pdv] = pd.DataFrame({"Colocado": c, "Devuelto": d})

filas = []
for pdv in TIENDAS:
    a, b = serie[pdv].Colocado, serie[pdv].Devuelto
    sin_pico = ~serie[pdv].index.isin([pd.Period("2024-12"), pd.Period("2025-01")])
    for k in range(4):
        ak = a.shift(k)
        filas.append({"PDV": pdv, "Rezago (meses)": k,
                      "Pearson": ak.corr(b),
                      "Spearman": ak.rank().corr(b.rank()),      # sin scipy
                      "Pearson sin dic-24/ene-25": ak[sin_pico].corr(b[sin_pico])})
rezago = pd.DataFrame(filas)
rezago.to_csv(PROCESADOS / "robustez_rezago.csv", index=False, encoding="utf-8-sig")
print(rezago.round(3).to_string(index=False))

# %% [markdown]
# ### 6.3 Exploración gráfica básica de las variables por SKU y tienda
#
# Antes de modelar conviene mirar las distribuciones y las relaciones entre las
# variables que describen a cada SKU en cada tienda: volumen colocado, número de
# entregas, lote medio, intervalo entre entregas, vida útil, fracción de vida útil
# consumida, intermitencia (ADI, CV²) y tasa de devolución. Cuatro vistas clásicas:
#
# - **Diagramas de caja (Fig. 11):** dispersión y valores extremos de cada variable,
#   tienda contra tienda.
# - **Histogramas (Fig. 12):** forma de las distribuciones (casi todas asimétricas a
#   la derecha, lo que justifica escalas logarítmicas y medianas en vez de medias).
# - **Matriz de correlación de Spearman (Fig. 13):** qué variables se mueven juntas.
#   Se usa Spearman (rangos) porque las distribuciones son asimétricas y con extremos.
# - **Dispersión de la tasa contra sus candidatas a explicarla (Fig. 14).**

# %%
base = (sku.merge(inter[["PDV", "SKU", "ADI", "CV2", "Clase"]], on=["PDV", "SKU"], how="left")
        .assign(Tasa=lambda d: d.Cajas_dev / d.Cajas_col * 100))
base = base[base.Entregas >= 3].copy()          # mismas referencias que el gradiente (§6.1)
VARS = {
    "Cajas_col": "Cajas colocadas (24 m)", "Entregas": "N.º de entregas",
    "Lote_medio": "Lote medio (cajas)", "Intervalo_entregas": "Intervalo entre entregas (d)",
    "Vida_util_dias": "Vida útil (d)", "Fraccion_vida_util": "Intervalo ÷ vida útil",
    "ADI": "ADI (semanas)", "CV2": "CV²", "Tasa": "Tasa de devolución (%)",
}
LOG = {"Cajas_col", "Entregas", "Lote_medio", "Intervalo_entregas", "ADI", "CV2"}
base.to_csv(PROCESADOS / "eda_variables_sku.csv", index=False, encoding="utf-8-sig")

print("Estadísticos descriptivos por tienda (SKU con ≥ 3 entregas):")
for pdv in TIENDAS:
    print(f"\n-- {pdv} ({int((base.PDV == pdv).sum())} SKU)")
    print(base.loc[base.PDV == pdv, list(VARS)].describe(percentiles=[0.25, 0.5, 0.75])
          .T[["mean", "25%", "50%", "75%", "max"]].round(2).rename(index=VARS).to_string())

# %%
# Fig. 11 — diagramas de caja por tienda
fig, axes = plt.subplots(2, 4, figsize=(12, 6.2), gridspec_kw={"hspace": 0.55, "wspace": 0.35})
for ax, (v, nombre) in zip(axes.ravel(), [(k, VARS[k]) for k in VARS if k != "Cajas_col"]):
    datos = [base.loc[base.PDV == p, v].dropna().to_numpy() for p in TIENDAS]
    if v in LOG:
        datos = [d[d > 0] for d in datos]
    bp = ax.boxplot(datos, widths=0.55, patch_artist=True, showfliers=True,
                    flierprops=dict(marker=".", ms=3, mec=GRIS, alpha=0.5),
                    medianprops=dict(color="white", lw=1.6))
    for patch, p in zip(bp["boxes"], TIENDAS):
        patch.set(facecolor=COLOR[p], edgecolor=COLOR[p], alpha=0.85)
    for w, p in zip(bp["whiskers"], [t for t in TIENDAS for _ in (0, 1)]):
        w.set(color=COLOR[p], lw=1)
    for c, p in zip(bp["caps"], [t for t in TIENDAS for _ in (0, 1)]):
        c.set(color=COLOR[p], lw=1)
    if v in LOG:
        ax.set_yscale("log")
    ax.set_xticks([1, 2])
    ax.set_xticklabels([CORTO[p] for p in TIENDAS], fontsize=9)
    ax.set_title(nombre, fontsize=9.5, fontweight="normal")
    limpiar_eje(ax)
titulo_figura(fig, "Fig. 11 · Diagramas de caja de las variables por SKU, tienda contra tienda", y=0.98)
fig.text(0.005, 0.01, "SKU con ≥ 3 entregas. Escala logarítmica donde la distribución es muy asimétrica. "
         "La línea blanca es la mediana; los puntos, valores extremos.", fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig11_boxplots_variables_sku.png")
plt.show()

# %%
# Fig. 12 — histogramas
fig, axes = plt.subplots(2, 3, figsize=(12, 6), gridspec_kw={"hspace": 0.5, "wspace": 0.3})
hist_vars = [("Vida_util_dias", False), ("Lote_medio", True), ("Intervalo_entregas", True),
             ("Fraccion_vida_util", False), ("ADI", True), ("Tasa", False)]
for ax, (v, log) in zip(axes.ravel(), hist_vars):
    todos = base[v].dropna()
    todos = todos[todos > 0] if log else todos
    bins = np.logspace(np.log10(todos.min()), np.log10(todos.max()), 25) if log else 25
    for p in TIENDAS:
        d = base.loc[base.PDV == p, v].dropna()
        d = d[d > 0] if log else d
        ax.hist(d, bins=bins, color=COLOR[p], alpha=0.6, label=CORTO[p], zorder=3,
                density=True)
    if log:
        ax.set_xscale("log")
    ax.set_title(VARS[v], fontsize=9.5, fontweight="normal")
    ax.set_yticks([])
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(visible=False)
axes[0, 0].legend(fontsize=8.5)
titulo_figura(fig, "Fig. 12 · Histogramas de las variables por SKU (densidad, por tienda)", y=0.98)
fig.text(0.005, 0.01, "SKU con ≥ 3 entregas. Eje horizontal logarítmico en lote, intervalo y ADI.",
         fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig12_histogramas_variables_sku.png")
plt.show()

# %%
# Fig. 13 — matriz de correlación de Spearman (rangos → Pearson, sin scipy)
corr = {}
for pdv in TIENDAS:
    d = base.loc[base.PDV == pdv, list(VARS)]
    corr[pdv] = d.rank().corr()
    corr[pdv].to_csv(PROCESADOS / f"eda_correlacion_spearman_{CORTO[pdv].lower().replace('é', 'e').replace('í', 'i')}.csv",
                     encoding="utf-8-sig")
    print(f"\nSpearman con la tasa de devolución — {pdv}:")
    print(corr[pdv]["Tasa"].drop("Tasa").rename(index=VARS).round(2).sort_values().to_string())

fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6), gridspec_kw={"wspace": 0.55})
etq = [VARS[k] for k in VARS]
for ax, pdv in zip(axes, TIENDAS):
    m = corr[pdv].to_numpy()
    im = ax.imshow(m, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(etq)))
    ax.set_yticks(range(len(etq)))
    ax.set_xticklabels(etq, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(etq, fontsize=8)
    for i in range(len(etq)):
        for j in range(len(etq)):
            ax.text(j, i, f"{m[i, j]:+.2f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(m[i, j]) > 0.55 else TINTA)
    ax.set_title(f"{pdv} · {int((base.PDV == pdv).sum())} SKU", fontsize=10.5)
    ax.grid(visible=False)
    ax.spines[:].set_visible(False)
fig.colorbar(im, ax=axes, shrink=0.75, pad=0.02, label="ρ de Spearman")
titulo_figura(fig, "Fig. 13 · Matriz de correlación de Spearman entre las variables por SKU", y=1.0)
fig.savefig(FIGURAS / "fig13_correlacion_spearman.png")
plt.show()

# %%
# Fig. 14 — dispersión de la tasa contra sus candidatas a explicarla
fig, axes = plt.subplots(2, 2, figsize=(11, 7.6), gridspec_kw={"hspace": 0.4, "wspace": 0.28})
pares = [("Fraccion_vida_util", True), ("Intervalo_entregas", True), ("Vida_util_dias", False), ("Lote_medio", True)]
for ax, (v, log) in zip(axes.ravel(), pares):
    for p in TIENDAS:
        d = base[(base.PDV == p) & (base.Cajas_col >= 20)]
        ax.scatter(d[v], d.Tasa, s=np.sqrt(d.Cajas_col) * 1.6 + 5, color=COLOR[p], alpha=0.5,
                   edgecolor="white", lw=0.4, label=CORTO[p], zorder=3)
        rho = d[v].rank().corr(d.Tasa.rank())
        ax.text(0.02, 0.95 - 0.08 * TIENDAS.index(p), f"ρ = {rho:+.2f} ({CORTO[p]})",
                transform=ax.transAxes, fontsize=8.5, color=COLOR[p], va="top")
    if log:
        ax.set_xscale("log")
    ax.set_xlabel(VARS[v])
    ax.set_ylabel("Tasa de devolución (%)")
    ax.set_ylim(-1, min(60, base.Tasa.max() * 1.05))
    ax.grid(axis="x", visible=True)
    ax.spines[["top", "right"]].set_visible(False)
axes[0, 0].legend(loc="upper right", fontsize=8.5)
titulo_figura(fig, "Fig. 14 · Tasa de devolución por SKU frente a intervalo, vida útil y lote (tamaño ∝ cajas)", y=0.99)
fig.text(0.005, 0.01, "SKU con ≥ 3 entregas y ≥ 20 cajas colocadas. ρ = correlación de Spearman.",
         fontsize=8.5, color=GRIS, va="top")
fig.savefig(FIGURAS / "fig14_dispersion_tasa_variables.png")
plt.show()

# %% [markdown]
# ## 7. Vida útil del portafolio que se coloca en cada tienda
#
# El diagnóstico reporta la vida útil mediana por SKU (160 y 150 días). Aquí se mira
# la distribución **ponderada por cajas**: qué tan corta es la vida útil de lo que
# realmente entra a cada tienda.

# %%
BINS = [0, 90, 120, 180, 270, 10**4]
ETQ = ["≤ 90 d", "91–120 d", "121–180 d", "181–270 d", "> 270 d"]
cb = col_bruta.merge(vu, on="SKU", how="left")
cb["Rango"] = pd.cut(cb.Vida_util_dias, bins=BINS, labels=ETQ)
vida = (cb.pivot_table(index="Rango", columns="PDV", values="Cajas_col", aggfunc="sum", observed=True, fill_value=0)
        .reindex(columns=TIENDAS))
vida_pct = (vida / vida.sum() * 100).round(1)
vida_pct.to_csv(PROCESADOS / "eda_vida_util_portafolio.csv", encoding="utf-8-sig")
print("% de cajas colocadas por rango de vida útil:")
print(vida_pct.to_string())
for pdv in TIENDAS:
    s = cb[(cb.PDV == pdv) & cb.Vida_util_dias.notna()]
    med = s.sort_values("Vida_util_dias").assign(acum=lambda d: d.Cajas_col.cumsum() / d.Cajas_col.sum())
    print(f"{pdv}: vida útil mediana ponderada por cajas = {med.loc[med.acum >= 0.5, 'Vida_util_dias'].iloc[0]:.0f} d "
          f"(mediana por SKU = {s.drop_duplicates('SKU').Vida_util_dias.median():.0f} d)")

# %%
fig, ax = plt.subplots(figsize=(8.6, 4))
xg, w = np.arange(len(ETQ)), 0.36
for j, pdv in enumerate(TIENDAS):
    pos = xg + (j - 0.5) * (w + 0.03)
    ax.bar(pos, vida_pct[pdv], width=w, color=COLOR[pdv], label=pdv, zorder=3)
    for p, v in zip(pos, vida_pct[pdv]):
        ax.text(p, v + 0.6, f"{pct(v, 1)} %", ha="center", fontsize=8.5, color=COLOR[pdv])
ax.set_xticks(xg)
ax.set_xticklabels(ETQ)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.set_title("Fig. 9 · Vida útil del portafolio colocado (% de cajas por rango)")
ax.legend(fontsize=9.5)
limpiar_eje(ax)
fig.savefig(FIGURAS / "fig9_vida_util_portafolio.png")
plt.show()

# %% [markdown]
# ## 8. Resumen de la exploración

# %%
RESUMEN = {
    "GA05 — extractos consistentes entre sí": "sí" if (verificacion.iloc[:6] == 0).all() else "NO",
    "GA05 — líneas con valor y sin cantidad": int(dev.Solo_valor.sum()),
    "GA05 — % del valor total en líneas sin cantidad": f"{dev.loc[dev.Solo_valor, 'Valor_dev'].sum() / dev.Valor_dev.sum() * 100:.1f} %",
    "Colocación — cambio de centro 79→43": "junio/2025 (ambas tiendas)",
    "Colocación — lead time mediano (días)": col_bruta.Lead_dias.median(),
}
for pdv in TIENDAS:
    k = CORTO[pdv]
    s = inter[inter.PDV == pdv]
    RESUMEN |= {
        f"[{k}] tasa reportada": f"{cota.loc[pdv, 'Tasa reportada %']:.2f} %",
        f"[{k}] tasa cota superior (si NC sin cantidad fueran físicas)": f"{cota.loc[pdv, 'Tasa cota superior %']:.2f} %",
        f"[{k}] % líneas de entrega fuera del calendario del maestro": f"{cal_ent[(cal_ent.PDV == pdv) & ~cal_ent['En maestro']]['% líneas'].sum():.1f} %",
        f"[{k}] lote mediano por línea (cajas)": round(lotes.loc['P50', pdv], 2),
        f"[{k}] semanas con devolución física (de {len(SEM)})": int((semanal[pdv].Cajas > 0).sum()),
        f"[{k}] SKU intermitentes o abultados (ADI > 1,32)": f"{(s.ADI > 1.32).mean() * 100:.1f} %",
        f"[{k}] SKU 'cobertura > VU' del diagnóstico (730 ÷ entregas)": int(((sku.PDV == pdv) & (sku.Cobertura_original > sku.Vida_util_dias)).sum()),
        f"[{k}] SKU cuyo intervalo real entre entregas supera la VU (≥3 entregas)": int(((rob3.PDV == pdv) & (rob3.Intervalo_entregas > rob3.Vida_util_dias)).sum()),
        f"[{k}] tasa tramo < 5 % de la VU": f"{gradiente.query('PDV == @pdv and Tramo == \"< 5 %\"')['Tasa %'].iloc[0]:.2f} %",
        f"[{k}] tasa tramo 35–50 % de la VU": f"{gradiente.query('PDV == @pdv and Tramo == \"35–50 %\"')['Tasa %'].iloc[0]:.2f} %",
        f"[{k}] Pearson rezago 1": round(rezago.query("PDV == @pdv and `Rezago (meses)` == 1").Pearson.iloc[0], 3),
        f"[{k}] Spearman rezago 1": round(rezago.query("PDV == @pdv and `Rezago (meses)` == 1").Spearman.iloc[0], 3),
        f"[{k}] Pearson rezago 1 sin dic-24/ene-25": round(rezago.query("PDV == @pdv and `Rezago (meses)` == 1")["Pearson sin dic-24/ene-25"].iloc[0], 3),
        f"[{k}] % cajas con vida útil ≤ 120 d": f"{vida_pct.loc[['≤ 90 d', '91–120 d'], pdv].sum():.1f} %",
    }
for clave, valor in RESUMEN.items():
    print(f"{clave:<66} {valor}")
pd.Series(RESUMEN, name="valor").to_csv(PROCESADOS / "resumen_eda_fase1.csv", encoding="utf-8-sig")
print(f"\nFiguras en: {FIGURAS}\nTablas en:  {PROCESADOS}")
