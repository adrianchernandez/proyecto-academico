# %% [markdown]
# # Cruce de devoluciones GA05 vs. plataforma CEN — enero/2026 (H-16)
#
# **Pregunta:** las notas crédito por vencimiento que el GA05 trae **sin
# cantidad** (`Solo_valor`, H-03) ¿corresponden a devoluciones físicas? En
# enero/2026 *todas* las líneas del GA05 de ambas tiendas están en cero
# (Éxito 148 líneas, Olímpica 69), así que ese mes es la prueba más limpia.
#
# **Fuente nueva:** carpeta `datos/crudos/Devoluciones enero 2026`, descargas
# de la plataforma CEN (Carvajal) con nombre GUID:
# - `*.csv` — devoluciones del **portal Éxito** (todas las tiendas, proveedor
#   Postobón), grano devolución × EAN, cantidad en unidades del EAN.
# - `*.txt` — documentos **AVISO RECIBO VALORIZADO** de **Olímpica**.
#
# El EAN se lleva a SKU SAP con `MAESTRO PORTAFOLIO EXITO.xlsx` (EAN/PLU →
# SAP por dependencia). El maestro de Olímpica no trae SKU SAP.
#
# **Lógica del cruce.** El GA05 no trae cantidad pero sí valor. Si la línea es
# una devolución física, su valor debe ser *unidades × precio unitario*. El
# precio unitario de cada SKU se toma de las líneas del GA05 que **sí** traen
# unidades (valor ÷ unidades, la más cercana a enero/2026, primero de la misma
# tienda). Así cada línea en cero se traduce a *unidades implícitas* y se
# compara con las unidades del CEN. La razón
# `k = valor GA05 ÷ (unidades CEN × precio)` dice cuántas veces el GA05 cobra
# la devolución física: k = 1 es coincidencia exacta.
#
# Salidas (en `datos/procesados/`):
# - `cen_exito_san_antonio_ene2026.csv`: devoluciones del CEN de la tienda 039
#   con SKU, clasificación, cajas físicas y precio de referencia.
# - `cruce_cen_ga05_sku_ene2026.csv`: por SKU, unidades CEN vs. GA05.
# - `cruce_cen_ga05_lineas_ene2026.csv`: cada línea del GA05 (ene–feb/2026,
#   Éxito) con sus unidades implícitas y su múltiplo k.
# - `cruce_cen_resumen_ene2026.csv`: cifras del resumen.
# - Figura 15.

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from comun import (PROCESADOS, FIGURAS, EXITO, OLIMPICA, COLOR, COLOR_SUAVE, GRIS, TINTA_2,
                   CLASIFICACIONES_ALCANCE, DEPENDENCIA_EXITO, configurar_estilo, limpiar_eje,
                   cargar_devoluciones, cargar_notas_credito, cargar_devoluciones_cen_exito,
                   cargar_avisos_cen_olimpica, cargar_maestro_portafolio_exito,
                   cargar_maestro_portafolio_olimpica)

ENERO = pd.Period("2026-01", "M")
TOL = 0.03          # tolerancia relativa para decir que dos valores "coinciden"

dev = cargar_devoluciones()          # GA05, vencimiento, BNA + Mundo Cero
nc = cargar_notas_credito()          # GA05, todos los motivos (para la clasificación)
cen = cargar_devoluciones_cen_exito()
avisos = cargar_avisos_cen_olimpica()
m_exito = cargar_maestro_portafolio_exito()
m_olim = cargar_maestro_portafolio_olimpica()

# %% [markdown]
# ## 1. Qué trae la carpeta
# El GA05 de enero/2026 está entero en cero en las dos tiendas: es el mes que
# se quiere verificar.

# %%
ga05_ene = (dev[dev.Mes == ENERO].groupby("PDV")
            .agg(lineas=("SKU", "size"), lineas_en_cero=("Solo_valor", "sum"),
                 valor=("Valor_dev", "sum"), cajas=("Cajas_dev", "sum")))
print("GA05, enero/2026 (vencimiento, BNA + Mundo Cero):")
print(ga05_ene.to_string(), "\n")

print(f"Portal Éxito (CSV): {cen.Archivo.nunique()} archivos, {len(cen):,} líneas devolución × EAN "
      f"de {cen.Dep_origen.nunique()} tiendas Éxito/Carulla/Surtimax; "
      f"fecha de devolución {cen.Fecha_dev.min():%d/%m/%Y} – {cen.Fecha_dev.max():%d/%m/%Y}.")
print(f"Olímpica (TXT): {avisos.Archivo.nunique()} avisos de recibo, {len(avisos)} ítems, "
      f"pedidos {avisos.Fecha_pedido.min():%d/%m/%Y} – {avisos.Fecha_pedido.max():%d/%m/%Y}.")

# %% [markdown]
# ## 2. Olímpica: los TXT no son devoluciones de Villanueva
# Los 41 documentos son *avisos de recibo* (`Ctd.Recibida`, recibidor,
# factura) del **CD Barranquilla (8001)**, es decir, mercancía que Olímpica
# recibe en su centro de distribución de la costa. Ninguno es de la tienda
# 341 Villanueva y casi ningún EAN es de bebidas Postobón (BNA): son
# alimentos Bary, cerveza, café, compotas. Con esta carpeta **no se puede
# verificar Olímpica**; se pide el extracto correcto (ver PENDIENTES).

# %%
avisos["Familia_EAN"] = avisos.EAN.isin(m_olim.EAN).map({True: "Portafolio BNA Postobón (maestro Olímpica)",
                                                          False: "Otro (alimentos, cerveza, café…)"})
print(avisos.groupby(["Centro", "Familia_EAN"]).agg(avisos=("Archivo", "nunique"), items=("EAN", "size"),
                                                     cantidad=("Cantidad", "sum")).to_string())
print("\n¿Algún aviso de la tienda 341 / Villanueva?",
      avisos.Centro.str.contains("341|VILLANUEVA", case=False).any())
print("¿El maestro de Olímpica tiene la tienda 341?", (m_olim.Centro.str.lstrip("0") == "341").any(),
      "| CEDI de Antioquia en el maestro:",
      m_olim.CEDI.str.contains("Medell|Antioq|Itag|Bello", case=False, na=False).any())

# %% [markdown]
# ## 3. Éxito San Antonio (dependencia 0039) en el portal
# Se toman las devoluciones con **dependencia de origen 0039**. El EAN se
# lleva a SKU con el maestro de portafolio (primero las filas de la
# dependencia 39; si el EAN no está codificado ahí, cualquier dependencia,
# porque el EAN → SKU no cambia entre tiendas). La clasificación (BNA, Mundo
# Cero, CCC…) se toma del GA05. Los EAN sin SKU se clasifican por prefijo
# GS1 solo para saber qué se queda por fuera: 7707430 = cerveza (CCC),
# 7702439/7708024/7702509 = alimentos y café (fuera del alcance), el resto de
# prefijos Postobón = bebida BNA sin homologar.

# %%
sa = cen[cen.Dep_origen == DEPENDENCIA_EXITO].copy()
mapa = (pd.concat([m_exito[m_exito.Dependencia == DEPENDENCIA_EXITO], m_exito])
        .drop_duplicates("EAN")[["EAN", "SKU", "Desc_Postobon"]])
sa = sa.merge(mapa, on="EAN", how="left").astype({"SKU": "Int64"})
clas = nc.drop_duplicates("SKU").set_index("SKU")["Clasificacion"]
sa["Clasificacion"] = sa.SKU.map(clas)

PREFIJOS_FUERA = {"7707430": "CCC (cerveza)", "7702439": "Alimentos (fuera)",
                  "7708024": "Alimentos (fuera)", "7702509": "Alimentos (fuera)"}
sin_sku = sa.SKU.isna()
sa.loc[sin_sku, "Clasificacion"] = (sa.loc[sin_sku, "EAN"].str[:7].map(PREFIJOS_FUERA)
                                    .fillna("BNA sin SKU en el maestro"))
sa["Clasificacion"] = sa["Clasificacion"].fillna("Sin clasificación GA05")
sa["En_alcance"] = sa.Clasificacion.isin(CLASIFICACIONES_ALCANCE)

print(sa.groupby("Clasificacion").agg(lineas=("EAN", "size"), devoluciones=("Devolucion", "nunique"),
                                      unidades=("Unidades_cen", "sum")).to_string())
print(f"\nRecogida: {sa.groupby('Tienda_recogida').size().to_dict()}")
print("\nEAN Postobón BNA sin SKU en el maestro (hay que pedir su homologación):")
print(sa[sa.Clasificacion == "BNA sin SKU en el maestro"]
      .groupby(["EAN", "Desc_EAN"]).Unidades_cen.sum().to_string())

# %% [markdown]
# ### 3.1 Precio unitario y factor unidades → cajas físicas
# - **Precio de referencia** del SKU: valor ÷ unidades de la línea del GA05
#   con unidades más cercana al 20/01/2026, primero de la misma tienda.
# - **Factor unidades por caja física**: mediana de unidades ÷ cajas en las
#   líneas del GA05 con ambas cantidades (H-04: la unidad del proyecto es la
#   caja física). Que el valor del GA05 cuadre exacto con *unidades CEN ×
#   precio* (sección 4) prueba que la "unidad" del CEN es la misma del GA05.

# %%
REF = pd.Timestamp("2026-01-20")
con_u = dev[dev.Unidades_dev > 0].assign(
    Precio=lambda x: x.Valor_dev / x.Unidades_dev,
    otra_tienda=lambda x: x.PDV != EXITO,
    distancia=lambda x: (x.Fecha - REF).abs())
precio = (con_u.sort_values(["otra_tienda", "distancia"]).groupby("SKU").first()
          [["Precio", "Fecha", "PDV"]].rename(columns={"Fecha": "Fecha_precio", "PDV": "PDV_precio"}))
factor = (dev[(dev.Cajas_dev > 0) & (dev.Unidades_dev > 0)]
          .assign(f=lambda x: x.Unidades_dev / x.Cajas_dev).groupby("SKU").f.median()
          .rename("Unid_por_caja"))

sa = sa.merge(precio, left_on="SKU", right_index=True, how="left") \
       .merge(factor, left_on="SKU", right_index=True, how="left")
sa["Cajas_cen"] = sa.Unidades_cen / sa.Unid_por_caja
sa["Valor_cen"] = sa.Unidades_cen * sa.Precio
sa.to_csv(PROCESADOS / "cen_exito_san_antonio_ene2026.csv", index=False, encoding="utf-8-sig")

bna = sa[sa.En_alcance]
print(f"Alcance BNA + Mundo Cero: {len(bna)} líneas, {bna.Devolucion.nunique()} devoluciones, "
      f"{bna.SKU.nunique()} SKU, {bna.Unidades_cen.sum():.0f} unidades = "
      f"{bna.Cajas_cen.sum():.1f} cajas físicas, valor a precio GA05 ${bna.Valor_cen.sum():,.0f}.")
print(f"SKU sin precio de referencia: {bna[bna.Precio.isna()].SKU.nunique()}; "
      f"sin factor de cajas: {bna[bna.Unid_por_caja.isna()].SKU.nunique()}")

# %% [markdown]
# ## 4. Cruce con las líneas en cero del GA05
# Ventana del GA05: 01/01 – 28/02/2026, porque la nota crédito se contabiliza
# días o semanas después de la devolución (fecha contable, H-02). Para cada
# línea del GA05 se calcula:
# - `Unid_implicitas = valor ÷ precio de referencia`;
# - `k = valor ÷ valor CEN del SKU en el mes` (cuántas veces el GA05 cobra lo
#   que el portal registra como devuelto físicamente).
#
# Una línea se clasifica como **1× (coincide)** si |k − 1| ≤ 3 %, **múltiplo
# exacto** si k es un entero ≥ 2 (± 3 %), **parcial** si k < 1 y el resto
# como **otro**. Los SKU del GA05 que no tienen devolución en el CEN quedan
# como **sin devolución en CEN**.

# %%
ga = dev[(dev.PDV == EXITO) & dev.Fecha.between("2026-01-01", "2026-02-28")].copy()
ga = ga.merge(precio[["Precio"]], left_on="SKU", right_index=True, how="left")
ga["Unid_implicitas"] = ga.Valor_dev / ga.Precio

por_sku_cen = bna.groupby("SKU").agg(Unidades_cen=("Unidades_cen", "sum"), Cajas_cen=("Cajas_cen", "sum"),
                                     Valor_cen=("Valor_cen", "sum"), Devoluciones_cen=("Devolucion", "nunique"),
                                     Primera_dev=("Fecha_dev", "min"), Ultima_dev=("Fecha_dev", "max"))
ga = ga.merge(por_sku_cen[["Unidades_cen", "Valor_cen"]], left_on="SKU", right_index=True, how="left")
ga["k"] = ga.Valor_dev / ga.Valor_cen


def tipo_linea(r):
    if pd.isna(r.Valor_cen):
        return "Sin devolución en CEN"
    if pd.isna(r.k):
        return "Sin precio de referencia"
    if abs(r.k - 1) <= TOL:
        return "1× (coincide)"
    if r.k >= 2 - TOL and abs(r.k - round(r.k)) <= TOL * r.k:
        return "Múltiplo exacto (≥2×)"
    if r.k < 1:
        return "Parcial (<1×)"
    return "Otro"


ga["Tipo"] = ga.apply(tipo_linea, axis=1)
# Valor idéntico del mismo SKU en dos o más fechas: posible nota repetida.
ga["Valor_repetido"] = ga.groupby(["SKU", ga.Valor_dev.round(0)]).Fecha.transform("nunique") > 1
ga.to_csv(PROCESADOS / "cruce_cen_ga05_lineas_ene2026.csv", index=False, encoding="utf-8-sig")

print(ga.groupby(["Mes", "Tipo"]).agg(lineas=("SKU", "size"), sku=("SKU", "nunique"),
                                      valor=("Valor_dev", "sum")).round(0).to_string())

# %% [markdown]
# ### 4.1 Por SKU
# Para cada SKU con devolución física en el CEN: unidades CEN frente a las
# unidades implícitas del GA05 en enero y en febrero, y si existe al menos una
# línea que coincide exacto (1×).

# %%
g_mes = ga.pivot_table(index="SKU", columns=ga.Mes.astype(str), values=["Valor_dev", "Unid_implicitas"],
                       aggfunc="sum")
g_mes.columns = [f"{a}_{b}" for a, b in g_mes.columns]
tab = (por_sku_cen.join(precio[["Precio"]]).join(factor)
       .join(g_mes)
       .join(ga.groupby("SKU").Tipo.agg(lambda s: (s == "1× (coincide)").any()).rename("Tiene_linea_1x"))
       .join(ga.groupby("SKU").k.max().rename("k_max")))
tab.insert(0, "Material", bna.drop_duplicates("SKU").set_index("SKU").Desc_Postobon)
tab["Razon_valor_ene"] = tab["Valor_dev_2026-01"] / tab.Valor_cen
tab = tab.sort_values("Valor_cen", ascending=False)
tab.to_csv(PROCESADOS / "cruce_cen_ga05_sku_ene2026.csv", encoding="utf-8-sig")
print(tab[["Material", "Unidades_cen", "Cajas_cen", "Unid_implicitas_2026-01", "Unid_implicitas_2026-02",
           "Tiene_linea_1x", "k_max"]].round(1).to_string())

# %% [markdown]
# ## 5. Resumen

# %%
ene = ga[ga.Mes == ENERO]
sku_ga_ene = set(ene.SKU)
sku_cen = set(bna.SKU)
valor_cen = bna.Valor_cen.sum()
r = {
    "GA05 ene/2026 Éxito: líneas (todas en cero)": len(ene),
    "GA05 ene/2026 Éxito: SKU": len(sku_ga_ene),
    "GA05 ene/2026 Éxito: valor": ene.Valor_dev.sum(),
    "CEN ene/2026 San Antonio BNA: devoluciones": bna.Devolucion.nunique(),
    "CEN ene/2026 San Antonio BNA: SKU": len(sku_cen),
    "CEN ene/2026 San Antonio BNA: unidades": bna.Unidades_cen.sum(),
    "CEN ene/2026 San Antonio BNA: cajas físicas": bna.Cajas_cen.sum(),
    "CEN ene/2026 San Antonio BNA: valor a precio GA05": valor_cen,
    "SKU CEN con línea en cero en GA05 ene–feb": len(sku_cen & set(ga.SKU)),
    "SKU CEN con línea en cero en GA05 enero": len(sku_cen & sku_ga_ene),
    "SKU CEN con al menos una línea 1× exacta": int(tab.Tiene_linea_1x.sum()),
    "SKU GA05 enero sin devolución en CEN": len(sku_ga_ene - sku_cen),
    "Valor GA05 enero de SKU sin devolución en CEN": ene[~ene.SKU.isin(sku_cen)].Valor_dev.sum(),
    "Valor GA05 enero de SKU con devolución CEN": ene[ene.SKU.isin(sku_cen)].Valor_dev.sum(),
    "Razón valor GA05 enero ÷ valor CEN (mismos SKU)": ene[ene.SKU.isin(sku_cen)].Valor_dev.sum() / valor_cen,
    "Líneas GA05 ene–feb múltiplo exacto ≥2×": int((ga.Tipo == "Múltiplo exacto (≥2×)").sum()),
    "Valor de líneas múltiplo exacto ≥2×": ga[ga.Tipo == "Múltiplo exacto (≥2×)"].Valor_dev.sum(),
    "Líneas GA05 ene–feb con valor repetido en otra fecha": int(ga.Valor_repetido.sum()),
}
resumen = pd.Series(r, name="Valor")
resumen.to_csv(PROCESADOS / "cruce_cen_resumen_ene2026.csv", encoding="utf-8-sig")
print(resumen.apply(lambda v: f"{v:,.2f}" if isinstance(v, float) else f"{v:,}").to_string())

# %% [markdown]
# ## 6. Figura 15 — unidades del CEN vs. unidades implícitas del GA05
# Una fila por SKU con devolución física en el CEN (Éxito San Antonio,
# enero/2026). El punto relleno es lo que el portal registra como devuelto;
# el hueco, lo que implica el valor de las notas crédito sin cantidad del
# GA05 (enero + febrero). Si el GA05 fuera una copia contable fiel, ambos
# puntos coincidirían.

# %%
configurar_estilo()
f = tab.dropna(subset=["Precio"]).copy()
f["GA05"] = f[["Unid_implicitas_2026-01", "Unid_implicitas_2026-02"]].sum(axis=1)
f = f.sort_values("Unidades_cen")
y = np.arange(len(f))
fig, ax = plt.subplots(figsize=(8, 0.26 * len(f) + 1.2))
ax.hlines(y, f.Unidades_cen, f.GA05, color=COLOR_SUAVE[EXITO], lw=1.6, zorder=1)
ax.scatter(f.Unidades_cen, y, s=28, color=COLOR[EXITO], zorder=3, label="Unidades devueltas (portal CEN)")
ax.scatter(f.GA05, y, s=28, facecolor="white", edgecolor=COLOR[EXITO], lw=1.4, zorder=3,
           label="Unidades implícitas GA05 (valor ÷ precio)")
ax.set_xscale("log")
ticks = [1, 2, 5, 10, 20, 50, 100, 200]
ax.set_xticks(ticks, [str(t) for t in ticks])
ax.minorticks_off()
ax.set_yticks(y, [f"{s} {str(n)[:28]}" for s, n in zip(f.index, f.Material)], fontsize=7)
ax.set_xlabel("Unidades (escala log)")
ax.legend(loc="lower right", fontsize=8, frameon=False)
ax.set_title("Éxito San Antonio, devoluciones BNA de enero/2026: las notas sin cantidad\n"
             "del GA05 valen varias veces lo que el portal registra como devuelto",
             loc="left", fontsize=10, color=TINTA_2)
limpiar_eje(ax)
fig.tight_layout()
fig.savefig(FIGURAS / "fig15_cruce_cen_ga05_exito.png", dpi=200, bbox_inches="tight")
plt.close(fig)
