# %% [markdown]
# # Fase 2 — Diseño del modelo de pronóstico de demanda y de la cantidad a pedir
#
# **Proyecto:** Herramienta estadística de reabastecimiento basada en la optimización
# del stock mínimo para reducir devoluciones por caducidad, canal moderno.
#
# **Alcance:** 2 puntos de venta — Éxito San Antonio y Olímpica Villanueva.
# Categoría BNA (clasificaciones BNA y Mundo Cero del GA05), regional Antioquia.
#
# **Autor:** Adrian Camilo Hernández Copete — Ingeniería Industrial, U. de Antioquia.
#
# ---
#
# ## ADVERTENCIA — léase antes de citar cualquier cifra de este script
#
# Todavía no se recibe la venta diaria al consumidor (hallazgo H-13,
# `informes/Registro_hallazgos.md`). Mientras tanto, la "demanda" que alimenta el
# pronóstico aquí es la **colocación semanal positiva (sell-in)**, la misma
# aproximación que ya se usó para la clasificación ADI–CV² de `eda_fase1.py`
# (Fig. 8, hallazgo H-12). Este script existe para dejar lista la **arquitectura**
# del modelo — selección de método de pronóstico por clase, fórmula de cantidad a
# pedir con tope de vida útil — y probarla de punta a punta con datos reales de
# colocación, entregas y vida útil.
#
# **Ninguna cifra que produzca este script (pronóstico, nivel objetivo, cantidad a
# pedir) es un resultado del proyecto.** Es un borrador de tubería (pipeline) para
# validar que la lógica corre. Se recalcula todo con la venta diaria en cuanto
# llegue, siguiendo `PENDIENTE_ventas_diarias.md` (Pasos 3 a 5). Lo que **sí** es
# real en este script: el calendario de entregas por tienda (maestro comercial),
# el lead time observado y la vida útil por SKU — esos tres no dependen de la
# venta diaria y ya se pueden fijar.
#
# ## 1. Lógica estadística del modelo
#
# El proyecto tiene dos preguntas separadas, en cascada:
#
# **(a) ¿Cuánto se va a vender? (pronóstico de demanda)**
# El diagnóstico de intermitencia (H-12) ya mostró que la inmensa mayoría de los
# SKU de ambas tiendas tiene demanda intermitente o abultada (ADI > 1,32): hay
# semanas en cero seguidas de picos, no una serie suave. Un promedio móvil o una
# suavización exponencial simple (SES) sobreestima sistemáticamente esas semanas
# en cero, y sesgan el nivel de stock hacia arriba (más vencimiento). Por eso se usa
# la clasificación de Syntetos, Boylan y Croston (2005) sobre dos estadísticos:
#
# - **ADI** = semanas activas ÷ semanas con demanda positiva (qué tan seguido llega demanda).
# - **CV²** = (desviación ÷ media)² del tamaño de la demanda cuando ocurre (qué tan errático es el tamaño).
#
# y un método de pronóstico distinto por cuadrante:
#
# | Clase | ADI | CV² | Método | Por qué |
# |---|---|---|---|---|
# | Suave | ≤1,32 | ≤0,49 | SES | Llega seguido y de tamaño estable; alcanza con suavizar. |
# | Errática | ≤1,32 | >0,49 | SBA | Llega seguido pero el tamaño varía mucho; Croston/SBA separa tamaño de frecuencia. |
# | Intermitente | >1,32 | ≤0,49 | SBA | Huecos largos, tamaño estable cuando aparece; Croston sesga al alza, SBA lo corrige. |
# | Abultada | >1,32 | >0,49 | TSB | Huecos largos y tamaño errático; mayor riesgo de descontinuación, TSB decae mejor a cero. |
#
# Croston separa la serie en "cuándo llega demanda" y "cuánto llega cuando aparece",
# suaviza cada componente por separado y pronostica su cociente. Croston está sesgado
# al alza (Syntetos y Boylan, 2001); **SBA** corrige ese sesgo con un factor
# (1 − α/2). **TSB** (Teunter, Syntetos y Babai, 2011) suaviza en cambio la
# *probabilidad* de que haya demanda en el periodo (no el intervalo), lo que le
# permite reaccionar y decaer hacia cero cuando un SKU deja de rotar — relevante
# aquí porque un SKU que se frena es justamente el que más riesgo de vencimiento
# genera.
#
# **(b) ¿Cuánto pedir, dado ese pronóstico? (cantidad a pedir)**
# No es una minimización simple: pedir de menos genera quiebre de stock, pedir de
# más genera vencimiento. Se usa un modelo clásico de **revisión periódica (R, S)**
# — el nivel objetivo cubre la demanda esperada durante el ciclo de revisión más el
# tiempo de entrega, con un colchón de seguridad proporcional a la variabilidad de
# la demanda — pero con una restricción que el modelo clásico no tiene: el nivel
# objetivo **nunca puede superar lo que la vida útil remanente permite vender**
# (Haijema y Minner, 2019). Esa segunda pieza es la que evita que, por perseguir
# nivel de servicio, el modelo pida más de lo que el producto alcanza a rotar antes
# de vencerse:
#
# ```
# demanda_ciclo   = d̄ · (R + L) / 7                       # d̄ en cajas/semana
# colchon         = z · σ · √((R + L) / 7)                 # seguridad por variabilidad
# nivel_objetivo  = demanda_ciclo + colchon                # clásico (R, S)
# tope_vida_util  = d̄ · vida_util_remanente / 7            # lo que la VU deja vender
# Q = max(0, min(nivel_objetivo, tope_vida_util) − inventario_proyectado)
# ```
#
# `R` (periodo de revisión) y `L` (lead time) se toman del calendario real de
# entregas y del lead time observado en colocación — son datos reales, no proxy.
# `d̄` (tasa de demanda) y `σ` (variabilidad) sí dependen del pronóstico y, por
# ahora, están calculados sobre colocación. `vida_util_remanente` se aproxima aquí
# por la vida útil total del SKU (sin descontar edad de inventario, porque todavía
# no hay inventario reconstruido) — simplificación declarada, se corrige en el
# Paso 4 de `PENDIENTE_ventas_diarias.md` en cuanto haya inventario en tienda.

# %% [markdown]
# ## 2. Configuración y datos

# %%
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()))
from comun import *  # noqa: F401,F403

pd.set_option("display.width", 160)

col = cargar_colocacion()
col_bruta = colocacion_bruta(col)
vu = cargar_vidas_utiles()

# %% [markdown]
# ## 3. Clasificación ADI–CV² sobre la serie semanal (misma regla que Fig. 8 de `eda_fase1.py`)
#
# A diferencia de `eda_intermitencia_sku.csv` (que solo guarda semanas con demanda
# positiva para calcular ADI/CV²), aquí se necesita la **serie completa** por SKU y
# tienda, con ceros incluidos en las semanas sin colocación, porque Croston/SBA/TSB
# necesitan ver los huecos para estimar el intervalo entre demandas.

# %%
UMBRAL_ADI, UMBRAL_CV2 = 1.32, 0.49


def clasificar(adi: float, cv2: float) -> str:
    if np.isnan(cv2):
        return "Sin clasificar (1 periodo)"
    if adi <= UMBRAL_ADI:
        return "Suave" if cv2 <= UMBRAL_CV2 else "Errática"
    return "Intermitente" if cv2 <= UMBRAL_CV2 else "Abultada"


def series_semanales(df: pd.DataFrame, cantidad: str = "Cajas_col") -> dict:
    """Una serie semanal completa (con ceros) por (PDV, SKU), y su clasificación."""
    series, meta = {}, []
    for (pdv, sku), g in df.groupby(["PDV", "SKU"]):
        w = g.groupby("Semana")[cantidad].sum()
        if w.empty:
            continue
        idx = pd.period_range(w.index.min(), w.index.max(), freq="W")
        y = w.reindex(idx, fill_value=0.0)
        activas = len(y)
        con_demanda = (y > 0).sum()
        if con_demanda == 0:
            continue
        adi = activas / con_demanda
        tam = y[y > 0]
        cv2 = (tam.std(ddof=0) / tam.mean()) ** 2 if len(tam) > 1 else np.nan
        series[(pdv, sku)] = y
        meta.append({"PDV": pdv, "SKU": sku, "Material": g.Material.iloc[0],
                      "Semanas_activas": activas, "Semanas_con_demanda": int(con_demanda),
                      "ADI": adi, "CV2": cv2, "Clase": clasificar(adi, cv2)})
    return series, pd.DataFrame(meta)


series, clas = series_semanales(col_bruta, "Cajas_col")
clas = clas.merge(vu, on="SKU", how="left")
print("Clasificación ADI-CV² (colocación semanal, proxy de demanda):")
print(clas.groupby(["PDV", "Clase"]).size().unstack(fill_value=0))

# %% [markdown]
# ## 4. Métodos de pronóstico por clase
#
# Los tres métodos intermitentes (Croston, SBA, TSB) reciben la serie semanal
# completa (con ceros) y devuelven, para cada semana, la tasa de demanda esperada
# **por periodo** ya suavizada — no hay que multiplicar por la probabilidad aparte.
# El pronóstico a futuro es plano: el último valor suavizado se sostiene hacia
# adelante, como es estándar en Croston y sus variantes (no hay componente de
# tendencia ni estacionalidad en este primer diseño).

# %%
def ses(y: np.ndarray, alpha: float = 0.2) -> np.ndarray:
    """Suavización exponencial simple. Sirve para series sin huecos (clase Suave)."""
    y = np.asarray(y, dtype=float)
    f = np.zeros(len(y))
    f[0] = y[0]
    for t in range(1, len(y)):
        f[t] = alpha * y[t - 1] + (1 - alpha) * f[t - 1]
    return f


def croston(y: np.ndarray, alpha: float = 0.1) -> np.ndarray:
    """Croston (1972): suaviza tamaño e intervalo por separado, pronostica su cociente."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    f = np.zeros(n)
    z = x = 0.0
    q = 1
    primero = np.flatnonzero(y > 0)
    if len(primero) == 0:
        return f
    i0 = primero[0]
    z, x = y[i0], 1.0
    f[: i0 + 1] = z / x
    for t in range(i0 + 1, n):
        if y[t] > 0:
            z = alpha * y[t] + (1 - alpha) * z
            x = alpha * q + (1 - alpha) * x
            q = 1
        else:
            q += 1
        f[t] = z / x if x > 0 else np.nan
    return f


def sba(y: np.ndarray, alpha: float = 0.1) -> np.ndarray:
    """Syntetos-Boylan Approximation: corrige el sesgo al alza de Croston (factor 1 − α/2)."""
    return croston(y, alpha) * (1 - alpha / 2)


def tsb(y: np.ndarray, alpha_p: float = 0.1, alpha_d: float = 0.1) -> np.ndarray:
    """Teunter-Syntetos-Babai (2011): suaviza la PROBABILIDAD de demanda cada periodo
    (no el intervalo), lo que le permite decaer hacia cero cuando el SKU deja de rotar."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    p = np.zeros(n)
    z = np.zeros(n)
    ocurre = y > 0
    p[0] = float(ocurre[0])
    z[0] = y[0] if ocurre[0] else 0.0
    for t in range(1, n):
        p[t] = alpha_p * ocurre[t] + (1 - alpha_p) * p[t - 1]
        z[t] = alpha_d * y[t] + (1 - alpha_d) * z[t - 1] if ocurre[t] else z[t - 1]
    return p * z


METODO_POR_CLASE = {
    "Suave": lambda y: ses(y, alpha=0.2),
    "Errática": lambda y: sba(y, alpha=0.1),
    "Intermitente": lambda y: sba(y, alpha=0.1),
    "Abultada": lambda y: tsb(y, alpha_p=0.1, alpha_d=0.1),
    "Sin clasificar (1 periodo)": lambda y: ses(y, alpha=0.2),
}


def pronosticar(y: np.ndarray, clase: str) -> np.ndarray:
    return METODO_POR_CLASE.get(clase, METODO_POR_CLASE["Sin clasificar (1 periodo)"])(y)

# %% [markdown]
# ## 5. Validación: backtest simple con MASE
#
# Para cada SKU con al menos 16 semanas activas se separan las últimas 8 semanas
# como prueba. El pronóstico de la prueba es el último valor suavizado del
# entrenamiento, sostenido plano. El **MASE** (Hyndman y Koehler, 2006) compara ese
# error contra el de un pronóstico ingenuo (repetir la semana anterior) calculado
# en el propio entrenamiento: MASE < 1 significa que el método le gana al ingenuo.
# Con colocación como proxy este backtest solo sirve para decidir si la arquitectura
# (elegir método por clase) tiene sentido; se repite con venta real antes de fijar
# los parámetros de producción.

# %%
def mase(y_prueba: np.ndarray, f_prueba: np.ndarray, y_entrena: np.ndarray) -> float:
    escala = np.mean(np.abs(np.diff(y_entrena)))
    if escala == 0 or np.isnan(escala):
        return np.nan
    return np.mean(np.abs(y_prueba - f_prueba)) / escala


HORIZONTE_PRUEBA = 8
MIN_SEMANAS = 2 * HORIZONTE_PRUEBA

resultados = []
for (pdv, sku), y in series.items():
    fila_clas = clas[(clas.PDV == pdv) & (clas.SKU == sku)]
    if fila_clas.empty:
        continue
    clase = fila_clas.Clase.iloc[0]
    y = y.to_numpy()
    if len(y) < MIN_SEMANAS:
        continue
    entrena, prueba = y[:-HORIZONTE_PRUEBA], y[-HORIZONTE_PRUEBA:]
    f_entrena = pronosticar(entrena, clase)
    f_plano = np.repeat(f_entrena[-1], HORIZONTE_PRUEBA)
    resultados.append({"PDV": pdv, "SKU": sku, "Clase": clase,
                        "Semanas_entrenamiento": len(entrena), "MASE": mase(prueba, f_plano, entrena)})

backtest = pd.DataFrame(resultados)
backtest.to_csv(PROCESADOS / "modelo_backtest_mase_proxy_colocacion.csv", index=False, encoding="utf-8-sig")
print(f"\nBacktest: {len(backtest)} SKU con ≥ {MIN_SEMANAS} semanas activas "
      f"(de {len(series)} SKU con serie semanal).")
print(backtest.groupby(["PDV", "Clase"]).MASE.agg(["count", "median"]).round(2))

# %% [markdown]
# ## 6. Parámetros reales de reabastecimiento por tienda
#
# `R` (periodo de revisión) se toma del calendario del maestro comercial: Éxito
# recibe pedido 6 días de la semana (revisión casi diaria), Olímpica solo 2
# (X y S, hallazgo H-06) — la diferencia de frecuencia entre tiendas que ya
# se documentó en el informe de avance N.º 1. `L` (lead time) es la mediana
# observada en colocación. Ninguno de los dos depende de la venta diaria.

# %%
parametros_pdv = {}
for pdv in TIENDAS:
    dias_entrega = len(DIAS_ENTREGA_MAESTRO[pdv])
    R = 7 / dias_entrega                                   # días entre revisiones, en promedio
    L = col.loc[col.PDV == pdv, "Lead_dias"].median()
    parametros_pdv[pdv] = {"R_dias": R, "L_dias": L}
    print(f"{pdv}: revisión cada {R:.1f} días ({dias_entrega} entregas/semana en el maestro) "
          f"| lead time mediano {L:.0f} día(s)")

# %% [markdown]
# ## 7. Fórmula de cantidad a pedir (borrador, con demanda proxy)
#
# `z` fija el nivel de servicio del colchón de seguridad (no del tope de vida útil,
# que es una restricción dura, no un nivel de servicio). Se deja z = 1,28 (≈90%)
# como punto de partida razonable para un piloto; se ajusta en la Fase 3 al
# simular escenarios. `sigma_semanal` se calcula sobre la serie semanal completa
# (incluye los ceros), porque es la variabilidad periodo a periodo la que importa
# para el colchón, no solo la variabilidad del tamaño cuando hay demanda (esa es CV²).

# %%
Z_SERVICIO = 1.28


def cantidad_a_pedir(d_semanal: float, sigma_semanal: float, vida_util_dias: float,
                      R_dias: float, L_dias: float, inventario_proyectado: float = 0.0,
                      z: float = Z_SERVICIO) -> dict:
    semanas_ciclo = (R_dias + L_dias) / 7
    demanda_ciclo = d_semanal * semanas_ciclo
    colchon = z * sigma_semanal * np.sqrt(semanas_ciclo)
    nivel_objetivo = demanda_ciclo + colchon
    tope_vida_util = d_semanal * vida_util_dias / 7
    limitado_por_vu = tope_vida_util < nivel_objetivo
    cantidad = max(0.0, min(nivel_objetivo, tope_vida_util) - inventario_proyectado)
    return {"Demanda_ciclo": demanda_ciclo, "Colchon": colchon, "Nivel_objetivo": nivel_objetivo,
            "Tope_vida_util": tope_vida_util, "Limitado_por_vida_util": limitado_por_vu,
            "Cantidad_a_pedir": cantidad}


filas = []
for (pdv, sku), y in series.items():
    fila_clas = clas[(clas.PDV == pdv) & (clas.SKU == sku)]
    if fila_clas.empty or pd.isna(fila_clas.Vida_util_dias.iloc[0]):
        continue  # sin vida útil (SKU fuera del maestro del centro 43): no se puede topar
    clase = fila_clas.Clase.iloc[0]
    vida_util = fila_clas.Vida_util_dias.iloc[0]
    y_arr = y.to_numpy()
    f = pronosticar(y_arr, clase)
    d_semanal = f[-1] if len(f) and not np.isnan(f[-1]) else 0.0
    sigma_semanal = y_arr.std(ddof=0)
    params = parametros_pdv[pdv]
    # Supuesto declarado: inventario_proyectado = 0 porque aún no hay inventario en
    # tienda reconstruido (H-13, Paso 4 de PENDIENTE_ventas_diarias.md). Sesga la
    # cantidad al alza: se corrige en cuanto llegue el inventario.
    salida = cantidad_a_pedir(d_semanal, sigma_semanal, vida_util, params["R_dias"], params["L_dias"])
    filas.append({"PDV": pdv, "SKU": sku, "Material": fila_clas.Material.iloc[0], "Clase": clase,
                  "Pronostico_semanal_cajas": round(d_semanal, 2), "Vida_util_dias": vida_util, **salida})

borrador = pd.DataFrame(filas)
borrador.to_csv(PROCESADOS / "stock_minimo_BORRADOR_proxy_colocacion.csv", index=False, encoding="utf-8-sig")

print(f"\nTubería completa: {len(borrador)} combinaciones SKU x tienda con Q calculada (BORRADOR, demanda = colocación).")
for pdv in TIENDAS:
    b = borrador[borrador.PDV == pdv]
    print(f"{pdv}: {len(b)} SKU | {pct((b.Limitado_por_vida_util.mean() * 100), 1)} % "
          f"con el tope de vida útil activo (el pedido quedó topado, no por nivel de servicio) | "
          f"Q mediana {b.Cantidad_a_pedir.median():.1f} cajas")

# %% [markdown]
# ## 8. Qué falta para que estas cifras dejen de ser un borrador
#
# 1. **Demanda real** (H-13): reemplazar `col_bruta` por `cargar_ventas()` cuando
#    exista, y recalcular la clasificación ADI–CV² y este pronóstico sobre venta
#    diaria/semanal real, no sobre colocación.
# 2. **Inventario proyectado real** (Paso 4 de `PENDIENTE_ventas_diarias.md`):
#    hoy se asume 0 en `cantidad_a_pedir`; con inventario reconstruido se resta el
#    saldo esperado al momento de la entrega, no cero.
# 3. **Vida útil remanente, no vida útil total**: hoy el tope usa la vida útil del
#    SKU completa; con inventario por lotes (FIFO) se puede estimar la vida útil que
#    de verdad le queda al lote que se va a vender primero.
# 4. **Calibración de z y de los umbrales ADI/CV²** en la simulación de escenarios
#    (Fase 3), comparando contra el reabastecimiento tradicional.
# 5. **Prioridad de SKU** (tarea del cronograma que se dejó pendiente a propósito):
#    una vez esté la venta real, ordenar los SKU por el peor cruce de rotación baja
#    y vida útil corta antes de pedir la prueba piloto — no todos los SKU necesitan
#    el mismo nivel de detalle en la validación.
