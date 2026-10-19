# Registro de hallazgos sobre los datos y el análisis

**Proyecto:** Herramienta estadística de reabastecimiento — Postobón S.A. / U. de Antioquia.
**Alcance:** Éxito San Antonio y Olímpica Villanueva, categoría BNA (clasificaciones BNA y Mundo Cero).

Este archivo es el registro **oportuno y acumulado** de todo lo que se descubre
sobre los datos, la exportación, el método o el propio análisis. Cada hallazgo
tiene un código (H-nn) que se cita desde el código, los informes y la bitácora.
Se agregan hallazgos al final; un hallazgo no se borra, se cierra (con la
decisión tomada) o queda abierto (con el responsable de resolverlo).

Convenciones de estado: **Abierto** (falta una respuesta externa o una decisión),
**Cerrado** (hay decisión documentada y aplicada en el código),
**Cerrado — corrige informe** (además obligó a corregir una cifra o afirmación
ya publicada en un informe anterior).

| Código | Fecha | Fuente | Hallazgo (una línea) | Estado |
|---|---|---|---|---|
| H-01 | 2026-09-03 | Colocación | El extracto venía neto de notas crédito (2.239 filas negativas) | Cerrado |
| H-02 | 2026-09-03 | GA05 | Dos columnas de fecha (`Fecha` vs `Día Transacción`), difieren en ~50 % de las filas | Abierto |
| H-03 | 2026-09-15 | GA05 | 635 líneas de vencimiento (32 %) traen valor pero ninguna cantidad; solo centro 43, desde jul/2025 | **Abierto** — corrige informe |
| H-04 | 2026-09-15 | GA05 | `Cantidad UMB` no es confiable (62 filas con UMB = 0 y cajas > 0) | Cerrado |
| H-05 | 2026-09-15 | Colocación | Ambas tiendas pasaron del centro 79 al 43 en junio/2025; el maestro de vidas útiles es solo del 43 | Abierto |
| H-06 | 2026-09-15 | Colocación | Olímpica recibe el 21 % de su colocación fuera de los días del maestro (X, S) | Abierto |
| H-07 | 2026-09-15 | Método | La "cobertura implícita" del diagnóstico equivale a 730 ÷ entregas; el grupo "excede vida útil" son SKU esporádicos | Cerrado — corrige informe |
| H-08 | 2026-09-15 | Método | La correlación de rezago 1 mes (r = 0,716) depende de un solo par de meses; no es un patrón | Cerrado — corrige informe |
| H-09 | 2026-09-15 | Alcance | Los datos incluyen la clasificación "Mundo Cero" además de "BNA" (9,8 % de las cajas devueltas) | Cerrado |
| H-10 | 2026-09-15 | Varias | Anomalías menores sin efecto en el indicador (filas en cero, domingos, SKU CO2, filas raras del GA05) | Cerrado |
| H-11 | 2026-09-03 | Método | Truncamiento por la izquierda: 12 SKU con más devolución que colocación en la ventana | Cerrado |
| H-12 | 2026-09-15 | EDA | 83 % (Éxito) y 87 % (Olímpica) de los SKU tienen demanda intermitente o abultada (ADI > 1,32) | Cerrado |
| H-13 | 2026-09-15 | Datos externos | La venta diaria al consumidor (sell-out) sigue sin entregarse | **Abierto** — bloqueo |
| H-14 | 2026-09-15 | Repositorio | El marco teórico vigente ("Marco teorico nuevo") no estaba dentro del proyecto | Cerrado |
| H-15 | 2026-09-18 | Método | Solo 365 de los 1.588 SKU del maestro de vidas útiles están activos en las dos tiendas | Abierto |
| H-16 | 2026-10-02 | CEN | Las líneas sin cantidad del GA05 sí son devoluciones físicas (Éxito ene/2026), pero su valor equivale a 4,3 veces lo devuelto; los TXT de Olímpica no son de Villanueva | **Abierto** |

---

## H-01 · La colocación venía neta de notas crédito

- **Fecha:** 2026-09-03. **Fuente:** `Colocacion.xlsx`.
- **Evidencia:** 2.239 filas negativas (10,0 %). 1.225 de 1.252 cruces con devoluciones
  (misma fecha, PDV y SKU) coinciden al decimal. El 99,9 % de las filas con fecha de
  pedido = fecha de entrega son negativas. El 80,5 % de las cajas negativas son
  devoluciones y el 19,5 % rechazos; el archivo no descuenta los rechazos "No Salió Al
  Mercado" (nunca llegaron a la tienda). La devolución por vencimiento está descontada
  en un 95,5 % (Éxito) y 97,4 % (Olímpica).
- **Impacto:** usar el archivo tal como viene resta el numerador del denominador e
  infla la tasa (1,59 % y 4,33 % en vez de 1,55 % y 3,97 %).
- **Decisión:** toda tasa usa **colocación bruta** (solo filas positivas), función
  `colocacion_bruta()` de `codigo/comun.py`.
- **Estado:** Cerrado.

## H-02 · Dos columnas de fecha en el GA05

- **Fecha:** 2026-09-03. **Fuente:** modelo `GA05-Notas Credito.pbix`, tabla `Devoluciones`.
- **Evidencia:** `Fecha` tiene registros inconsistentes (llega al año 2204 y arranca en
  2023); `Día Transacción` va de 2024-04 a 2026-08 sin anomalías. Difieren en ~50 % de
  las filas.
- **Decisión provisional:** se usa `Día Transacción`.
- **Pendiente:** confirmar con la asesora externa cuál es la fecha contable de la nota
  crédito. **Estado:** Abierto.

## H-03 · Líneas de nota crédito con valor y sin cantidad

- **Fecha:** 2026-09-15. **Fuente:** `devoluciones_vencimiento_analitico.csv` (y el
  universo `notas_credito_todas`, donde ocurre lo mismo: 714 filas).
- **Evidencia (`eda_fase1.py` §2.4, `datos/procesados/eda_nc_sin_cantidad_*.csv`):**
  - 635 de 1.979 líneas (32,1 %) traen valor neto > 0 con cajas = unidades =
    hectolitros = 0. Suman **$26,6 millones, el 34,7 % del valor total** del extracto.
  - Por tienda: Éxito 404 líneas y $15,3 M (25,7 % de su valor); Olímpica 231 líneas y
    $11,3 M (**65,4 %** de su valor).
  - No es conversión de unidades: 150 de los 161 SKU afectados sí traen cajas en otras
    fechas. Además, 299 de las 635 líneas repiten exactamente el mismo valor para el
    mismo SKU en fechas distintas (parece un documento recurrente, no un retorno físico).
  - Solo aparecen con **centro 43** y **desde el 14/07/2025** (Éxito) y el 08/11/2025
    (Olímpica), es decir, después del cambio de centro abastecedor (H-05). Se
    concentran en dic/2025 – feb/2026.
  - En **Éxito enero/2026** y en **Olímpica enero y febrero/2026** el 100 % de las
    líneas viene sin cantidad.
  - Cota superior: si cada línea correspondiera a producto físico al precio implícito
    por caja de su SKU, serían 523 cajas más en Éxito y 373 en Olímpica; la tasa
    subiría de 1,55 % a **2,12 %** en Éxito y de 3,97 % a **12,44 %** en Olímpica.
- **Verificación de la exportación:** los tres CSV salidos del GA05 son consistentes
  entre sí (el extracto diario y el analítico son idénticos fila a fila; el universo de
  notas crédito filtrado a vencimiento + devolución + BNA/Mundo Cero reproduce el
  analítico en filas, cajas, unidades y líneas). **El problema no es la exportación,
  está en el modelo o en el documento SAP de origen.** Power BI Desktop estaba cerrado
  el 15/09, así que no se re-ejecutó la consulta DAX; la próxima vez que esté abierto
  conviene re-lanzarla y volver a correr `eda_fase1.py` §2.
- **Impacto sobre lo ya publicado (corregido el 15/09):**
  - "Éxito no registra devolución en 1 de 24 meses; Olímpica en 8" → **Éxito 0 meses en
    cero real; Olímpica 6**. Los otros tres meses tenían notas crédito sin cantidad.
  - "244 SKU con devolución en 195 días (Éxito), 112 en 50 días (Olímpica)" → con
    devolución **física**: 238 SKU en 168 días y 95 SKU en 35 días.
  - El valor devuelto se reporta ahora separado: Éxito $44,0 M con cantidad + $15,3 M
    sin cantidad; Olímpica $6,0 M + $11,3 M.
  - Las tasas en cajas (1,55 % y 3,97 %) no cambian, pero pasan a leerse como **piso**.
- **Decisión:** las líneas quedan marcadas (`Solo_valor`) en `comun.cargar_devoluciones()`;
  se excluyen de todo conteo físico y se reportan aparte en valor. La Fig. 1 marca con
  círculo hueco los meses afectados.
- **Pendiente (asesora externa):** ¿qué documento SAP genera una nota crédito por
  vencimiento sin cantidad? ¿Baja/destrucción en punto de venta sin retorno físico?
  ¿Nota crédito solo por valor (ajuste de precio)? ¿Un tipo de documento que el modelo
  GA05 no convierte a cajas? La respuesta decide si esas 900 cajas equivalentes entran
  o no al numerador. **Estado: Abierto.**
- **Acción (18/09/2026):** se pidieron las devoluciones desde una segunda fuente, la
  plataforma CEN, para verificar si esas mismas líneas allí traen cantidad. Plan de
  cruce y criterios de decisión en `PENDIENTE_devoluciones_CEN.md` (abrirá H-16).

## H-04 · `Cantidad UMB` no es confiable

- **Evidencia:** 62 líneas con unidades = 0 y cajas físicas > 0 (fracciones de caja de
  presentaciones "OF"). Las cajas físicas y los hectolitros sí son coherentes entre sí
  (35 de 259 SKU con variación > 5 % en hl/caja, atribuible a presentaciones surtidas).
- **Decisión:** la unidad de trabajo del proyecto es la **caja física**; las unidades
  solo se usan como referencia. **Estado:** Cerrado.

## H-05 · Cambio de centro abastecedor (79 → 43) en junio de 2025

- **Evidencia (`eda_colocacion_centro.csv`):** Éxito recibió del centro 79 del
  02/09/2024 al 31/05/2025 y del 43 desde el 03/06/2025; Olímpica igual (07/09/2024 –
  31/05/2025 y desde el 07/06/2025). No hay meses con los dos centros a la vez.
- **Impacto:** (a) el maestro de vidas útiles es del centro 43 y se aplicó a los 9
  primeros meses, abastecidos por el 79; (b) las líneas sin cantidad del GA05 (H-03)
  aparecen solo tras el cambio; (c) cualquier comparación "antes vs. después" del
  cambio debe tener en cuenta que no solo cambió el centro sino posiblemente el proceso
  de notas crédito.
- **Pendiente:** confirmar si la vida útil por SKU difiere entre centros 43 y 79.
  **Estado:** Abierto.

## H-06 · Olímpica recibe fuera de los días del maestro

- **Evidencia (`eda_colocacion_calendario.csv`, Fig. 6):** el maestro declara entrega
  miércoles y sábado. Sí concentran el 82 % de las líneas, pero **442 líneas en 51
  fechas (930 cajas, 21,1 % de la colocación de la tienda)** se entregaron lunes,
  martes, jueves o viernes, repartidas en 23 de los 24 meses (1 a 5 fechas por mes).
  Éxito cumple el maestro al 100 %.
- **Impacto:** el "ciclo equivalente de 3,7 días" del diagnóstico es un promedio; el
  calendario real de Olímpica es dos entregas fijas por semana más entregas
  extraordinarias. Para el modelo, el periodo de revisión de Olímpica debe tomarse del
  calendario real (fechas de entrega observadas), no del maestro.
- **Pendiente:** preguntar si las entregas fuera de X/S son pedidos extraordinarios,
  reprogramaciones o errores de registro. **Estado:** Abierto.

## H-07 · La "cobertura implícita" del diagnóstico era 730 ÷ entregas

- **Evidencia (`eda_fase1.py` §6.1, `robustez_cobertura_*.csv`, Fig. 10):**
  cobertura = lote medio ÷ consumo diario = (cajas ÷ entregas) ÷ (cajas ÷ 730) =
  730 ÷ entregas. Un SKU con dos entregas en la misma semana queda con "cobertura" de
  365 días. Los 39 SKU de Éxito y 50 de Olímpica del grupo "cobertura > vida útil"
  tienen una mediana de 3 y 2 entregas y una vida comercial mediana de 25 y 22 días:
  son referencias esporádicas (nuevas, descontinuadas o de temporada), no lotes grandes.
  Con el intervalo real entre entregas — (última − primera) ÷ (entregas − 1), SKU con
  ≥ 3 entregas — **solo un SKU por tienda supera su vida útil**.
- **Lo que sí muestran los datos (y es más fuerte):** la tasa de devolución crece de
  forma monótona con la fracción de la vida útil que consume el intervalo entre
  entregas. Éxito: 0,42 % cuando el intervalo es < 5 % de la vida útil, 4,2 % en 5–10 %,
  6,9 % en 10–20 %, 12,4 % en 35–50 %. Olímpica: 0,18 %, 0,14 %, 1,9 %, 2,6 %, 14,4 %,
  17,1 % en 50–100 %. Spearman(fracción, tasa) = +0,49 (Éxito, n = 244) y +0,61
  (Olímpica, n = 71).
- **Decisión:** el Hallazgo 3 del diagnóstico se **reformula**: no es "los SKU cuyo
  lote cubre más días que la vida útil devuelven 4,7×", sino "la tasa de devolución
  crece de forma continua con la fracción de vida útil consumida entre entregas". La
  Fig. 3 se conserva en el código por trazabilidad, pero el informe usa la Fig. 10. Para
  el modelo: la variable que importa es intervalo entre entregas ÷ vida útil remanente
  al momento de la entrega, y el tope a la cantidad a pedir debe depender de ella de
  forma continua. **Estado:** Cerrado — corrige informe.

## H-08 · La correlación de rezago 1 mes no es un patrón

- **Evidencia (`robustez_rezago.csv`):** Éxito, rezago 1 mes: Pearson 0,716; Spearman
  **0,030**; Pearson sin diciembre/2024 y enero/2025: **−0,088**. Con 24 puntos, un solo
  par (14.860 cajas en diciembre → 239 cajas devueltas en enero) sostiene toda la
  correlación. Olímpica: ninguna correlación relevante con ningún método.
- **Decisión:** el Hallazgo 2 del diagnóstico se **reformula** como un **episodio
  documentado** (caso de sobrecolocación de Bretaña 300 ml en diciembre/2024 seguido de
  la peor tasa de la serie, con el 71 % de la devolución de enero en la familia Hit
  1.000 ml Tetra), no como una regla "la colocación de un mes predice la devolución del
  siguiente". La ventana de decisión sigue siendo válida como argumento cualitativo:
  hay que acotar la cantidad a pedir *antes* de que el inventario supere la vida útil.
  **Estado:** Cerrado — corrige informe.

## H-09 · El alcance incluye la clasificación "Mundo Cero"

- **Evidencia:** el GA05 clasifica las bebidas sin azúcar (Pepsi Cero, Manzana Cero,
  Colombiana Cero…) como "Mundo Cero", separado de "BNA". 211 líneas y 155 cajas
  devueltas (9,8 %) son Mundo Cero; el archivo de colocación las incluye. Las
  clasificaciones CCC (cerveza) y Nutrimenti no están en la colocación y quedan fuera.
- **Decisión:** el alcance "BNA" del proyecto se entiende como bebidas no alcohólicas
  del portafolio Postobón = clasificaciones **BNA y Mundo Cero** del GA05. Constante
  `CLASIFICACIONES_ALCANCE` en `comun.py`; anotado en `CLAUDE.md`. **Estado:** Cerrado.

## H-10 · Anomalías menores (sin efecto en el indicador)

- 150 filas de colocación en cero (90 Éxito, 60 Olímpica): se excluyen de ambos lados.
- 23 filas con fecha de entrega en domingo, todas negativas (notas crédito): no son
  entregas.
- SKU 1100 "CILINDRO CO2" (17 cajas, Éxito): no es bebida y no tiene vida útil; se deja
  en el denominador y fuera de los análisis por vida útil.
- 8 SKU con devolución física pero sin colocación en la ventana (16,3 cajas): efecto de
  truncamiento (H-11), casi todos bebidas de avena/almendra Hatsu.
- En el universo de notas crédito: 1 fila tipo "Sin Asignar" (motivo "#") y 10 filas de
  rechazo con cajas negativas (reversiones); ninguna toca al vencimiento.
- Lead time pedido → entrega: 1 a 3 días (mediana 2) en ambas tiendas; sin valores
  imposibles.
- **Estado:** Cerrado.

## H-11 · Truncamiento por la izquierda

- **Evidencia:** 7 SKU en Éxito y 5 en Olímpica con más devolución que colocación en la
  ventana (203 de 1.576 cajas, 12,9 %), concentrados en enero/2025 y en SKU de vida
  útil larga (238 d). Se colocaron antes del 01/09/2024.
- **Decisión:** se declara como limitación; para calibrar el modelo se descartarán los
  primeros meses o se acotará a vida útil corta. **Estado:** Cerrado.

## H-12 · La demanda (aproximada por colocación) es intermitente en casi todos los SKU

- **Evidencia (`eda_intermitencia_*.csv`, Fig. 8):** sobre colocación semanal positiva
  en la ventana activa de cada SKU, el 83,0 % de los SKU de Éxito y el 86,6 % de
  Olímpica tienen ADI > 1,32. Por cajas: en Éxito el 33,6 % del volumen es "suave"
  (36 SKU de alta rotación) y el 41,5 % "abultado"; en Olímpica el 75 % del volumen es
  "intermitente" y no hay ningún SKU "suave".
- **Implicación (Fase 2):** la suavización exponencial simple solo sirve para el
  puñado de SKU suaves de Éxito; el resto exige Croston/SBA o TSB, y la precisión se
  mide con MASE. Se recalcula con la venta diaria cuando llegue (H-13).
- **Estado:** Cerrado (como hallazgo; la clasificación definitiva se hará con ventas).

## H-13 · Venta diaria al consumidor pendiente

- La venta diaria de las dos tiendas (sell-out) no se ha entregado. Sin ella, el
  consumo real se aproxima con la colocación, lo que basta para diagnosticar pero no
  para calibrar ni validar el modelo. Instrucciones para cuando llegue:
  `PENDIENTE_ventas_diarias.md`. **Estado:** Abierto — bloqueo externo.

## H-14 · El marco teórico vigente no estaba en el repositorio

- `CLAUDE.md` citaba un archivo "Marco teorico nuevo" que no existía en el proyecto;
  estaba en la carpeta de Descargas (`Marco teorico nuevo.docx`, 23 referencias). Se
  copió a `documentos/Marco_teorico_nuevo.docx` junto con
  `documentos/Contexto_Proyecto_MarcoTeorico.md`; la versión visual
  (`Revision de literatura.html`, sin lista de referencias) se movió de la raíz a
  `documentos/Revision_de_literatura.html`. El modelo `GA05-Notas Credito.pbix` se
  movió a `datos/crudos/`. **Estado:** Cerrado.

## H-15 · Solo 365 de los 1.588 SKU del maestro de vidas útiles están activos en las dos tiendas

- **Fecha:** 2026-09-18. **Fuente:** `codigo/sku_activos.py` (cruce maestro de vidas
  útiles × colocación bruta × devoluciones por vencimiento, sep/2024 – ago/2026).
- **Evidencia:** un SKU se considera activo si tuvo al menos una colocación bruta
  (H-01) o una devolución por vencimiento (incluidas las líneas `Solo_valor`, H-03) en
  la tienda. Resultado: 346 SKU activos en Éxito (340 con colocación, 244 con
  devolución), 181 en Olímpica (172 y 112), 365 en la unión y 162 comunes a ambas.
  Es el 23 % del maestro. Un solo SKU con movimiento no tiene vida útil: 1100
  CILINDRO CO2 (Éxito), que no es una bebida. 13 SKU (6 Éxito, 9 Olímpica) tienen
  devolución sin colocación bruta en la tienda: 6 de ellos aparecen en la colocación
  solo con filas negativas o en cero (colocación neteada, H-01), 2 de Olímpica se
  colocaron en Éxito; pesan 15,1 cajas (1,1 %) en Éxito y 2,1 (1,2 %) en Olímpica.
- **Impacto:** el universo del modelo de cantidad a pedir y de la priorización de SKU
  críticos es el de SKU activos (`datos/procesados/sku_activos.csv`), no el maestro
  completo. Los 13 SKU solo con devolución no alteran el indicador (denominador
  bruto, H-01) y se tratan como SKU descontinuados o de colocación anterior a la
  ventana.
- **Decisión:** universo = 365 SKU activos por tienda (346 / 181). El CILINDRO CO2 se
  excluye del alcance BNA salvo indicación contraria de la asesora externa (pregunta
  E-8 en `PENDIENTES.md`). **Estado:** Abierto (confirmar E-8).

## H-16 · Devoluciones desde la plataforma CEN: las líneas sin cantidad son físicas, pero el GA05 las valora varias veces

- **Fecha:** 2026-10-02. **Fuente:** carpeta `datos/crudos/Devoluciones enero 2026`
  (descargas del CEN con nombre GUID), `MAESTRO PORTAFOLIO EXITO.xlsx` y
  `MAESTRO PORTAFOLIO OLIMPICA.xlsx`. Código: `codigo/cruce_devoluciones_cen.py`
  (cargadores nuevos en `comun.py`). Mes elegido: enero/2026, porque en el GA05
  **todas** las líneas de ese mes vienen sin cantidad (Éxito 148, $8,15 M;
  Olímpica 69, $4,69 M).
- **Esquema real recibido:**
  - 31 CSV = devoluciones del **portal Éxito**, proveedor Postobón, 240 tiendas del
    grupo; grano devolución × EAN; columnas `#DEVOL`, `DEP ORIGEN` (tienda),
    `DEP RECOGIDA`, `EAN`, `EAN DESC`, `CANTIDAD` (unidades del EAN), `FECHA DEVOL`,
    `FECHA RECOGIDA`; 8.549 líneas (8.511 tras quitar 38 que reaparecen en otra
    descarga con la recogida reprogramada; misma cantidad). No trae valor, motivo ni
    número de nota crédito.
  - 41 TXT = **AVISO RECIBO VALORIZADO** de Olímpica, todos del **CD Barranquilla
    (8001)**, pedidos del 30/12/2025 al 20/01/2026; 277 ítems, 274 de ellos alimentos,
    cerveza o café (solo 3 EAN del portafolio BNA). Son recibos de mercancía en un
    centro de distribución, **no devoluciones de la tienda 341 Villanueva**. El
    maestro de Olímpica tampoco trae SKU SAP ni CEDI de Antioquia.
- **Evidencia (Éxito San Antonio, dependencia 0039):**
  - 76 líneas del portal en enero/2026; 45 en el alcance BNA + Mundo Cero (17
    devoluciones, 34 SKU, **280 unidades = 37,0 cajas físicas**, valor a precio GA05
    $1,14 M). Fuera: 11 líneas de cerveza (CCC), 7 de alimentos (recogidas en el CEDI
    Vegas) y 13 líneas BNA (37 unidades) cuyos 8 EAN no están en el maestro de Éxito.
  - **Los 34 SKU devueltos físicamente tienen líneas sin cantidad en el GA05** entre
    enero y febrero/2026 (30 de ellos ya en enero). Las líneas en cero son, por lo
    tanto, devoluciones físicas reales y no solo ajustes de valor.
  - **En 23 de los 34 SKU hay una línea del GA05 cuyo valor es exactamente unidades
    del portal × precio unitario** (± 3 %), con el precio tomado de las líneas del GA05
    que sí traen unidades. Ejemplo: Uva 1,5 L (SKU 23349), 23 unidades × $3.375 =
    $77.625, igual a la línea del 02/02/2026. Esto valida además que la "unidad" del
    portal es la misma unidad del GA05.
  - **Pero el GA05 cuenta el valor varias veces.** En los mismos SKU, el valor de enero
    en el GA05 es **4,34 veces** el valor físico del portal. 27 líneas (ene–feb) son
    múltiplos enteros exactos de la devolución física (2× a 7×; 14 de ellas el
    29/01/2026, p. ej. Uva = 4 × $77.625) y 73 de las 148 líneas de enero repiten el
    mismo valor del mismo SKU en otra fecha (consistente con las 299 repeticiones
    vistas en H-03). La cota superior por valor de H-03 asigna a Éxito enero/2026
    unas 303 cajas equivalentes; el portal registra 37 cajas BNA con SKU.
  - 26 SKU del GA05 de enero (valor $3,22 M) no tienen devolución en el portal ese
    mes: pueden ser devoluciones de diciembre (la carpeta no trae diciembre para la
    tienda 039), los 8 EAN sin homologar, o más repeticiones.
- **Impacto:** (1) para Éxito se descarta el escenario B del plan (no son solo valor):
  las líneas sin cantidad sí son producto devuelto. (2) La cantidad **no** puede
  reconstruirse dividiendo el valor del GA05 por el precio, porque el valor está
  multiplicado: la cota superior por valor (2,12 % Éxito) queda sobrestimada y la tasa
  real está entre el piso (1,55 %) y esa cota, más cerca del piso. (3) Si las notas
  repetidas son documentos reales y no un efecto del modelo Power BI, hay un posible
  **cobro duplicado** de Éxito a Postobón (≈ $3,8 M en exceso solo en los 34 SKU de
  enero), que es un tema financiero para la asesora externa. (4) Olímpica no se puede
  verificar con este envío.
- **Decisión:** no se modifica `cargar_devoluciones()` con un solo mes y una sola
  tienda. La fuente de cantidad para las líneas sin cantidad será el **portal CEN**
  (unidades → cajas con el factor del GA05), no el valor del GA05. Se piden: el
  extracto CEN de Éxito para jul/2025 – abr/2026, el de devoluciones de la tienda 341
  de Olímpica, la homologación de los 8 EAN y el detalle por número de nota crédito
  del GA05 para separar notas repetidas de un artefacto del modelo. Salidas:
  `datos/procesados/cen_exito_san_antonio_ene2026.csv`,
  `cruce_cen_ga05_sku_ene2026.csv`, `cruce_cen_ga05_lineas_ene2026.csv`,
  `cruce_cen_resumen_ene2026.csv`; Fig. 15. **Estado:** Abierto.
