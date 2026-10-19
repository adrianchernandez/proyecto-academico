# Pendiente: venta diaria de los puntos de venta (sell-out)

Postobón aún no entrega la venta diaria al consumidor de Éxito San Antonio y
Olímpica Villanueva (hallazgo H-13). Este archivo tiene dos partes: **lo que hay
que pegar en el chat cuando llegue el dato** y **lo que Claude hará con él**, en
orden, para que no haya que reconstruir el contexto.

---

## 1. Texto para pegar en el chat cuando tenga el archivo

> Ya tengo la venta diaria de los dos puntos de venta. El archivo está en
> `datos/crudos/<NOMBRE_DEL_ARCHIVO>` (formato: <xlsx / csv>, una fila por
> <día × SKU × tienda / otro grano>). La unidad de cantidad es <unidades / cajas
> físicas / otra>. <Sí / No> incluye devoluciones descontadas. <Sí / No> viene
> con inventario en tienda. Sigue el plan de `PENDIENTE_ventas_diarias.md`.

Si no se sabe alguno de los datos entre `< >`, dejarlo en blanco: el primer
paso del plan es averiguarlo del propio archivo.

Preguntas que conviene hacerle a la asesora externa **al recibir el archivo**
(si ya vienen respondidas, mejor):

1. ¿La cantidad está en unidades de venta al consumidor o en cajas físicas? ¿Cuál es
   el factor de conversión por SKU (el GA05 usa "cajas físicas")?
2. ¿La venta es neta de devoluciones del consumidor o bruta?
3. ¿Cubre exactamente el mismo periodo (01/09/2024 – 31/08/2026) y las dos tiendas
   (Ex 039 y St 341)?
4. ¿Existe el inventario en tienda (al menos un corte, idealmente diario)? Sin un
   inventario inicial no se puede reconstruir el saldo ni la vida útil remanente.
5. ¿Los días sin fila son días sin venta (cero real) o días sin registro?
6. ¿Viene con el código de material SAP (el mismo de colocación y GA05) o con el
   código/EAN de la cadena? Si es el de la cadena, hace falta la tabla de homologación.

---

## 2. Plan de trabajo con la venta diaria (lo que hará Claude, en este orden)

### Paso 0 — Registrar y proteger
- Confirmar que el archivo quedó en `datos/crudos/` (ignorado por git) y anotar en
  `CLAUDE.md` (sección "Fuentes de datos") su esquema real: columnas, tipos,
  grano, unidad, periodo.
- Abrir el hallazgo H-13 en `informes/Registro_hallazgos.md` con la fecha de recepción.

### Paso 1 — Calidad y depuración (nuevo cargador en `codigo/comun.py`)
- `cargar_ventas()`: normalizar columnas (`Fecha`, `PDV`, `SKU`, `Unidades_venta`,
  `Cajas_venta`), mapear tienda con `MAPA_PDV`/`MAPA_SAP`, convertir a cajas físicas
  con el factor por SKU (derivarlo del GA05: unidades ÷ cajas en líneas con
  cantidad, y contrastar con el que entregue Postobón).
- Controles: duplicados en la llave fecha × PDV × SKU, negativos, fechas fuera de
  ventana, SKU que no existen en colocación ni en vidas útiles, días sin registro
  frente a días sin venta, cobertura del calendario (¿hay ventas los domingos?).
- Documentar cada anomalía como hallazgo H-15, H-16, … antes de usar el dato.

### Paso 2 — Reconciliación sell-in vs. sell-out (`codigo/reconciliacion_ventas.py`)
- Por SKU × tienda × mes: colocación bruta, venta, devolución por vencimiento y
  el **saldo implícito acumulado** = colocación − venta − devoluciones. Un saldo que
  crece sin límite señala inventario fantasma o diferencia de unidades; un saldo
  negativo señala inventario inicial no observado (truncamiento, H-11).
- Razón venta ÷ colocación por SKU y tienda; distribución y casos extremos.
- Comparar la varianza mensual de colocación con la de venta (efecto látigo,
  Trapero y Pedregal, 2016): cuantificar cuánto ruido logístico tiene el sell-in.
- Reestimar el **consumo diario real** por SKU y tienda y rehacer con él la Fig. 10
  (fracción de vida útil consumida entre entregas, ahora con rotación real).

### Paso 3 — Rehacer la clasificación de demanda con ventas
- Recalcular ADI y CV² (Syntetos, Boylan y Croston, 2005) sobre la venta semanal y
  diaria por SKU × tienda (`eda_fase1.py` §5 ya tiene la función `intermitencia()`;
  basta pasarle la tabla de ventas). Actualizar `eda_intermitencia_*.csv` y la Fig. 8.
- Decidir por clase el método de pronóstico: SES para "suave", SBA para
  "intermitente"/"errática", TSB para "abultada" o con riesgo de descontinuación.

### Paso 4 — Reconstrucción del inventario y vida útil remanente (si hay inventario)
- Con inventario inicial (o un corte cualquiera) reconstruir el saldo diario por SKU
  y tienda: saldo_t = saldo_{t−1} + colocación_t − venta_t − devolución_t.
- Asignar edad al inventario por lotes (FIFO sobre las entregas) para estimar la
  vida útil remanente al momento de cada pedido: es el insumo del tope de la
  cantidad a pedir (Haijema y Minner, 2019).
- Si no hay inventario: declarar el supuesto (saldo inicial cero al inicio de la
  ventana o tras el primer mes sin devolución) y medir su sensibilidad.

### Paso 5 — Fase 2: diseño del modelo (`codigo/modelo_stock_minimo.py`)
- Pronóstico por SKU × tienda con el método de su clase, evaluado con MASE sobre
  una ventana de prueba (últimos 3–6 meses).
- Stock mínimo y cantidad a pedir por ciclo:
  `Q = max(0, min(nivel_objetivo, demanda_esperada_en_vida_util_remanente) − inventario_proyectado)`,
  redondeada al lote mínimo, con periodo de revisión tomado del **calendario real
  de entregas** de cada tienda (H-06) y lead time observado (1–3 días).
- Salida obligatoria: una tabla por ciclo con `PDV, SKU, cantidad_a_pedir` y las
  columnas de sustento (pronóstico, inventario proyectado, vida útil remanente,
  tope). Ese número es el entregable del proyecto.

### Paso 6 — Documentar y cerrar la sesión
- Actualizar `informes/Registro_hallazgos.md`, `informes/Informe_avance_01.md`
  (o abrir el `02`), `bitacora_avances.md`, `README.md`; regenerar cuadernos con
  `python codigo/sincronizar_notebooks.py`; commit
  `Fase 1/2: integración de venta diaria (Éxito y Olímpica)`.
- Mostrar el resumen de avance en el chat con el formato de `CLAUDE.md`.
