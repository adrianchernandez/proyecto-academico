# %% [markdown]
# # Cruce de SKU activos (Fase 1 → insumo de Fase 2)
#
# **Pregunta:** ¿cuántos SKU del maestro de vidas útiles están realmente
# activos en los dos puntos de venta? Un SKU se considera *activo* si en la
# ventana 01/09/2024 – 31/08/2026 tuvo al menos una colocación bruta
# (fila positiva, H-01) **o** al menos una devolución por vencimiento
# (incluidas las líneas `Solo_valor`, H-03, porque igual prueban que el SKU
# se movió en la tienda).
#
# Salidas (en `datos/procesados/`):
# - `sku_activos.csv`: maestro de vidas útiles filtrado a los SKU activos,
#   con banderas por tienda (colocación / devolución) y totales.
# - `sku_activos_resumen.csv`: conteo por tienda y por tipo de evidencia.
#
# El resultado alimenta la Fase 2: el universo de SKU para el que se calcula
# la cantidad a pedir es el de SKU activos, no el maestro completo (1.588).

# %%
import pandas as pd
from comun import (PROCESADOS, TIENDAS, CORTO, cargar_colocacion, colocacion_bruta,
                   cargar_devoluciones, cargar_vidas_utiles)

PROCESADOS.mkdir(parents=True, exist_ok=True)

vu = cargar_vidas_utiles()                    # 1 fila por SKU, solo centro 43
col = colocacion_bruta(cargar_colocacion())   # denominador: filas positivas (H-01)
dev = cargar_devoluciones()                   # incluye Solo_valor (H-03)

# %% [markdown]
# ## 1. Evidencia de actividad por SKU y tienda
# Para cada tienda se construye el conjunto de SKU con colocación y el de SKU
# con devolución; la unión de ambos es el conjunto de SKU activos en esa tienda.

# %%
def resumen_sku(df, valor, prefijo):
    """Agrega por SKU × PDV: cajas totales, n.º de fechas y primera/última fecha."""
    fecha = "Fecha entrega" if prefijo == "col" else "Fecha"
    g = df.groupby(["SKU", "PDV"]).agg(
        cajas=(valor, "sum"), fechas=(fecha, "nunique"),
        primera=(fecha, "min"), ultima=(fecha, "max"))
    return g.unstack("PDV")

rc = resumen_sku(col, "Cajas_col", "col")
rd = resumen_sku(dev, "Cajas_dev", "dev")

tabla = vu.set_index("SKU").copy()
tabla["Material"] = (pd.concat([col[["SKU", "Material"]], dev[["SKU", "Material"]]])
                     .drop_duplicates("SKU").set_index("SKU")["Material"])

for t in TIENDAS:
    c = CORTO[t]
    tabla[f"Col_{c}"] = tabla.index.isin(rc["cajas"].dropna(subset=[t]).index) if t in rc["cajas"] else False
    tabla[f"Dev_{c}"] = tabla.index.isin(rd["cajas"].dropna(subset=[t]).index) if t in rd["cajas"] else False
    tabla[f"Activo_{c}"] = tabla[f"Col_{c}"] | tabla[f"Dev_{c}"]
    tabla[f"Cajas_col_{c}"] = rc["cajas"].get(t).reindex(tabla.index).fillna(0)
    tabla[f"Cajas_dev_{c}"] = rd["cajas"].get(t).reindex(tabla.index).fillna(0)
    tabla[f"Entregas_{c}"] = rc["fechas"].get(t).reindex(tabla.index).fillna(0).astype(int)
    tabla[f"Ultima_entrega_{c}"] = rc["ultima"].get(t).reindex(tabla.index)

tabla["Activo"] = tabla[[f"Activo_{CORTO[t]}" for t in TIENDAS]].any(axis=1)

# %% [markdown]
# ## 2. SKU fuera del maestro de vidas útiles
# Los SKU que se mueven en las tiendas pero no están en el maestro (centro 43)
# no pueden entrar al modelo sin vida útil: se listan aparte para pedirlos.

# %%
sku_mov = set(col.SKU) | set(dev.SKU)
sin_vu = sorted(sku_mov - set(vu.SKU))
faltantes = (pd.concat([col[["SKU", "Material", "PDV"]], dev[["SKU", "Material", "PDV"]]])
             .query("SKU in @sin_vu").groupby(["SKU", "Material"])["PDV"]
             .agg(lambda s: " / ".join(sorted(set(CORTO[p] for p in s)))).reset_index())

# %% [markdown]
# ## 3. Resumen

# %%
filas = []
for t in TIENDAS:
    c = CORTO[t]
    filas.append({
        "Tienda": c,
        "SKU con colocación": int(tabla[f"Col_{c}"].sum()),
        "SKU con devolución": int(tabla[f"Dev_{c}"].sum()),
        "Con ambas": int((tabla[f"Col_{c}"] & tabla[f"Dev_{c}"]).sum()),
        "Solo devolución (sin colocación)": int((tabla[f"Dev_{c}"] & ~tabla[f"Col_{c}"]).sum()),
        "SKU activos": int(tabla[f"Activo_{c}"].sum()),
    })
filas.append({
    "Tienda": "Ambas (unión)",
    "SKU con colocación": int(tabla[[f"Col_{CORTO[t]}" for t in TIENDAS]].any(axis=1).sum()),
    "SKU con devolución": int(tabla[[f"Dev_{CORTO[t]}" for t in TIENDAS]].any(axis=1).sum()),
    "Con ambas": int((tabla[[f"Col_{CORTO[t]}" for t in TIENDAS]].any(axis=1)
                      & tabla[[f"Dev_{CORTO[t]}" for t in TIENDAS]].any(axis=1)).sum()),
    "Solo devolución (sin colocación)": int((tabla[[f"Dev_{CORTO[t]}" for t in TIENDAS]].any(axis=1)
                                            & ~tabla[[f"Col_{CORTO[t]}" for t in TIENDAS]].any(axis=1)).sum()),
    "SKU activos": int(tabla["Activo"].sum()),
})
resumen = pd.DataFrame(filas)

print(f"Maestro de vidas útiles (centro 43): {len(vu)} SKU")
print(f"SKU con movimiento en las tiendas:   {len(sku_mov)} "
      f"(en maestro: {len(sku_mov & set(vu.SKU))}, sin vida útil: {len(sin_vu)})")
print(f"SKU activos en ambas tiendas a la vez: "
      f"{int((tabla['Activo_Éxito'] & tabla['Activo_Olímpica']).sum())}")
print(resumen.to_string(index=False))
if len(faltantes):
    print("\nSKU con movimiento pero sin vida útil en el maestro:")
    print(faltantes.to_string(index=False))

# %%
activos = tabla[tabla["Activo"]].reset_index()
activos.to_csv(PROCESADOS / "sku_activos.csv", index=False, encoding="utf-8-sig")
resumen.to_csv(PROCESADOS / "sku_activos_resumen.csv", index=False, encoding="utf-8-sig")
faltantes.to_csv(PROCESADOS / "sku_sin_vida_util.csv", index=False, encoding="utf-8-sig")
with pd.ExcelWriter(PROCESADOS / "sku_activos.xlsx") as xw:
    resumen.to_excel(xw, sheet_name="Resumen", index=False)
    activos.to_excel(xw, sheet_name="SKU activos", index=False)
    faltantes.to_excel(xw, sheet_name="Sin vida util", index=False)
print(f"\nGuardado: {PROCESADOS / 'sku_activos.xlsx'} ({len(activos)} SKU activos)")
