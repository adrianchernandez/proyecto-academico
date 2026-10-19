# Pendientes y recomendaciones — lista viva única

Un solo lugar para todo lo que está por hacer, preguntar o decidir. Se consolida
desde el registro de hallazgos, la bitácora, el plan de venta diaria, las marcas
`[PENDIENTE]` del informe final y las recomendaciones dadas en el chat.

Reglas:
- Toda recomendación o pendiente que surja en una sesión se agrega aquí **en el
  momento**, con fecha de apertura y origen (H-nn, bitácora, informe o chat).
- Un ítem resuelto no se borra: se mueve a "Cerrados" con la fecha y una línea de
  cómo se resolvió, para trazabilidad ante la asesora.
- Cuando se pregunte "qué tengo pendiente", se lee este archivo; no se reconstruye
  de memoria.

Última actualización: 02/10/2026.

---

## 1. Bloqueos externos (dependen de Postobón)

| # | Pendiente | Origen | Abierto | Efecto mientras no llegue |
|---|---|---|---|---|
| B-1 | **Venta diaria al consumidor (sell-out)** de Ex 039 y St 341, 01/09/2024 – 31/08/2026 | H-13 | 2026-09-03 | Bloquea calibrar y validar el modelo; todo lo de Fase 2 sigue siendo borrador sobre colocación. Al llegar: `PENDIENTE_ventas_diarias.md`. |
| B-3 | **Devoluciones por vencimiento desde la plataforma CEN** (segunda fuente) para verificar si las 635 líneas del GA05 con valor y sin cantidad (404 Éxito, 231 Olímpica; $26,6 M) sí traen cantidad allí. Se pidieron el 18/09/2026. Al llegar: `PENDIENTE_devoluciones_CEN.md`. | H-03, chat 2026-09-18 | 2026-09-18 | Las tasas 1,55 % y 3,97 % siguen leyéndose como piso (cota superior 2,12 % y 12,44 %). El cruce decide entre rellenar cantidades (A), confirmar que son solo valor (B) o descartar la fuente (C). |
| B-3a | **Avance 02/10/2026 (H-16):** llegó enero/2026 del CEN. Éxito: las líneas sin cantidad **sí son devoluciones físicas** (34 de 34 SKU devueltos en el portal tienen línea en cero en el GA05; 23 con valor exacto = unidades × precio), pero el GA05 valora **4,3 veces** lo devuelto. Falta pedir el CEN de Éxito para **jul/2025 – abr/2026** (todos los meses con líneas en cero) para rellenar cantidades desde el portal. | H-16, chat 2026-10-02 | 2026-10-02 | La cantidad no se puede sacar de valor ÷ precio; mientras no llegue el resto, las tasas siguen como piso y la cota superior (2,12 %) queda sobrestimada. |
| B-4 | **Devoluciones de la tienda St 341 Villanueva desde el CEN de Olímpica.** Los 41 TXT recibidos son *avisos de recibo* del CD Barranquilla (8001), no devoluciones de Villanueva. | H-16, chat 2026-10-02 | 2026-10-02 | Olímpica (231 líneas sin cantidad, $11,3 M; cota 12,44 %) sigue sin verificar. |
| B-2 | **Inventario en tienda** (al menos un corte, idealmente diario) | H-13, `PENDIENTE_ventas_diarias.md` Paso 4 | 2026-09-15 | Sin él, el modelo asume inventario proyectado = 0 y vida útil remanente = vida útil total (ambos sesgan la cantidad a pedir al alza). |
| B-5 | **Vía directa a la tienda para B-1/B-2 (14/10/2026):** ya hay contacto con el gerente de Olímpica Villanueva y el subgerente de Éxito San Antonio; ambos aceptaron verbalmente gestionar la solicitud. Se redactó un WhatsApp para cada uno pidiendo venta diaria por PLU/EAN + inventario. Falta: enviarlo, y avisar a la asesora externa (Kellys) para que Postobón respalde la solicitud ante las cadenas. | Chat 2026-10-14 | 2026-10-14 | Alternativa a esperar la entrega interna de Postobón. Si llega, aplicar `PENDIENTE_ventas_diarias.md` (nota: vendrá con código de la cadena, no SAP → necesita homologación con los maestros de portafolio). |

## 2. Preguntas para la asesora externa (Kellys Otero)

| # | Pregunta | Origen | Abierto | Qué decide |
|---|---|---|---|---|
| E-1 | ¿Cuál es la fecha contable de la nota crédito en el GA05: `Fecha` o `Día Transacción`? Se está usando `Día Transacción`. | H-02 | 2026-09-03 | Si cambia, se recalcula la serie mensual del diagnóstico. |
| E-2 | ¿Qué documento SAP genera una nota crédito por vencimiento **con valor y sin cantidad** (635 líneas, $26,6 M, solo centro 43, desde jul/2025)? ¿Baja en tienda sin retorno, ajuste de precio, tipo que el GA05 no convierte a cajas? Se complementa con el extracto del CEN (B-3). **02/10:** el CEN de enero/2026 muestra que en Éxito sí son devoluciones físicas (H-16); la pregunta queda en por qué el valor se repite (E-10). | H-03 | 2026-09-15 | Si esas líneas son físicas, la tasa sube de 1,55 % a 2,12 % (Éxito) y de 3,97 % a 12,44 % (Olímpica). |
| E-3 | ¿La vida útil por SKU difiere entre el centro 43 y el 79? El maestro solo trae el 43 y se aplicó a los 9 meses abastecidos por el 79. | H-05 | 2026-09-15 | Validez del tope de vida útil para sep/2024 – may/2025. |
| E-4 | Las entregas de Olímpica fuera de miércoles y sábado (21 % de su colocación): ¿pedidos extraordinarios, reprogramaciones o error de registro? | H-06 | 2026-09-15 | Cómo se define el periodo de revisión de Olímpica en el modelo (ver C-1). |
| E-5 | **Lote mínimo de pedido** por cadena (¿la cantidad se pide en cajas enteras, en múltiplos, en unidades?). | Chat 2026-09-16; informe §4.5.5 | 2026-09-16 | Redondeo de la cantidad a pedir. |
| E-6 | ¿Postobón tiene un **nivel de servicio objetivo** definido para el canal moderno? El modelo parte de z = 1,28 (≈ 90 %). | Chat 2026-09-16; informe §4.5.5 | 2026-09-16 | Colchón de seguridad del modelo; si no hay uno, se calibra en Fase 3. |
| E-8 | El SKU 1100 **CILINDRO CO2** aparece en la colocación de Éxito pero no está en el maestro de vidas útiles ni es una bebida: ¿se excluye del alcance BNA? (Único SKU con movimiento sin vida útil; `datos/procesados/sku_sin_vida_util.csv`.) | `sku_activos.py`, H-15 | 2026-09-18 | Si se confirma, el universo del modelo queda en 365 SKU activos (346 Éxito, 181 Olímpica) y se filtra en `cargar_colocacion()`. |
| E-7 | Las seis preguntas de recepción de la venta diaria (unidad, neto/bruto, periodo, inventario, días sin fila, código SAP vs. EAN). | `PENDIENTE_ventas_diarias.md` §1 | 2026-09-15 | Se hacen **al recibir el archivo**, no antes. |
| E-9 | ¿Postobón tiene acceso a un portal EDI/VMI/CPFR de Éxito y Olímpica con venta en punto por SKU-tienda, distinto del extracto SAP de colocación? Si existe, es una vía más directa que esperar la entrega interna del sell-out (B-1). | Chat 2026-09-28 | 2026-09-28 | Si existe, reemplaza o adelanta B-1; si no existe, confirma que colocación es el único proxy disponible. |
| E-10 | En el GA05, las notas crédito sin cantidad de Éxito en enero/2026 repiten el valor de la devolución física: 27 líneas son múltiplos exactos (2× a 7×; 14 el 29/01) y 73 de 148 repiten el mismo valor en otra fecha. ¿Son **notas crédito duplicadas** (posible cobro duplicado de Éxito, ≈ $3,8 M en exceso solo en 34 SKU de enero) o un efecto del modelo Power BI? Llevar ejemplo: Uva 1,5 L (SKU 23349), 23 unidades devueltas el 08/01 → GA05 $310.500 el 29/01 (4×) + $77.625 el 02/02 (1×). | H-16 | 2026-10-02 | Decide si la tasa por valor sirve; si es duplicado real, es un hallazgo financiero para Postobón. |
| E-11 | Homologar a SKU SAP 8 EAN de BNA que Éxito devolvió y no están en el maestro de portafolio: 7702090022797, 7702090036862, 7702090044331, 7702090048810, 7702192070603, 7702192128434, 7707133074702, 7707151700522 (37 unidades en enero/2026). | H-16 | 2026-10-02 | 13 líneas BNA quedan fuera del cruce. |

## 3. Preguntas para la asesora interna (Olga Usuga)

| # | Pregunta | Origen | Abierto | Qué decide |
|---|---|---|---|---|
| I-1 | ¿El cuerpo del informe final exige IEEE o basta APA 7 (compatible con NTC 5613)? | `CLAUDE.md`, informe final (encabezado) | 2026-09-15 | Formato de citas de todo el informe. |

## 4. Tareas de código

| # | Tarea | Origen | Abierto | Depende de |
|---|---|---|---|---|
| C-1 | Tomar el periodo de revisión de Olímpica del **calendario real de entregas** (fechas observadas), no del maestro (hoy 7 ÷ 2 = 3,5 días en `modelo_stock_minimo.py`). | H-06 (impacto) vs. `modelo_stock_minimo.py` §6 | 2026-09-16 | Respuesta E-4 ayuda, pero puede hacerse ya con las fechas observadas. |
| C-2 | Esqueleto de `cargar_ventas()` en `codigo/comun.py` (columnas normalizadas `Fecha, PDV, SKU, Unidades_venta, Cajas_venta`, mapa de tienda, conversión a cajas, controles), para que al llegar el archivo solo se ajusten nombres. | Chat 2026-09-16; `PENDIENTE_ventas_diarias.md` Paso 1 | 2026-09-16 | Nada; se puede hacer ya. |
| C-3 | Reconciliación sell-in vs. sell-out (`codigo/reconciliacion_ventas.py`): saldo implícito, razón venta ÷ colocación, varianza sell-in vs. venta, rehacer Fig. 10 con rotación real. | `PENDIENTE_ventas_diarias.md` Paso 2 | 2026-09-15 | B-1. |
| C-4 | Reclasificación ADI–CV² con venta real y actualización de Fig. 8 y `eda_intermitencia_*.csv`. | `PENDIENTE_ventas_diarias.md` Paso 3; H-12 | 2026-09-15 | B-1. |
| C-5 | Reconstrucción del inventario diario y vida útil remanente por lote (FIFO). | `PENDIENTE_ventas_diarias.md` Paso 4 | 2026-09-15 | B-1, B-2. |
| C-6 | Recalibrar `modelo_stock_minimo.py` con venta real: α por clase (minimizando MASE), z, inventario proyectado real, vida útil remanente real, redondeo a lote. | `PENDIENTE_ventas_diarias.md` Paso 5; informe §4.5.5 | 2026-09-16 | B-1, B-2, E-5, E-6. |
| C-7 | Priorización de SKU críticos (clasificación multicriterio: volumen, vida útil, lote, intermitencia) para el piloto. Se dejó a propósito para después de la venta real. | Cronograma M4; informe §3.5 | 2026-09-16 | B-1. |
| C-10 | Usar `datos/procesados/sku_activos.csv` como universo de SKU del modelo (`modelo_stock_minimo.py`) y de la priorización C-7, en vez del maestro completo de 1.588. Revisar los 13 SKU con devolución pero sin colocación en la tienda (6 Éxito, 9 Olímpica): probablemente colocados antes de sep/2024 o con colocación neteada (H-01). | `sku_activos.py`, chat 2026-09-18 | 2026-09-18 | Nada; se puede hacer ya. |
| C-8 | Simulación de escenarios Fase 3 (`codigo/simulacion_escenarios.py`): política propuesta vs. tradicional; métricas cajas vencidas, quiebres, nivel de servicio, valor; sensibilidad a inventario inicial, vida útil del centro 79 y líneas sin cantidad. | Informe §4.4 y §5.3 | 2026-09-15 | C-6. |
| C-9 | Re-ejecutar la consulta DAX con Power BI abierto para cerrar formalmente la verificación de la exportación del GA05. | Bitácora 2026-09-15 | 2026-09-15 | Tener Power BI Desktop abierto con el `.pbix`. |
| C-11 | Consulta DAX del GA05 a **nivel de número de nota crédito** para Éxito ene–feb/2026, para ver si las notas repetidas (E-10) son documentos distintos o filas duplicadas del modelo. | H-16 | 2026-10-02 | Power BI Desktop abierto (igual que C-9). |
| C-12 | Al llegar el CEN completo (B-3a, B-4): extender `cruce_devoluciones_cen.py` a todos los meses y, si se confirma, rellenar `Cajas_dev` de las líneas `Solo_valor` con las cajas del portal en `cargar_devoluciones()` (columna `Origen_cantidad`), recalcular tasas y figuras 1, 4, 10. | H-16, `PENDIENTE_devoluciones_CEN.md` Pasos 3–4 | 2026-10-02 | B-3a, B-4, E-10. |

## 5. Tareas de documentación

| # | Tarea | Origen | Abierto | Depende de |
|---|---|---|---|---|
| D-1 | Informe parcial (segundo informe de avance). Se dejó a propósito para cuando haya venta real. | Cronograma; chat 2026-09-16 | 2026-09-16 | B-1. |
| D-2 | Informe final §5.2 (resultados Fase 2): reconciliación, clasificación definitiva, MASE por clase, tabla de salida por ciclo. | Informe §5.2 | 2026-09-15 | C-3 a C-6. |
| D-3 | Informe final §4.4 (diseño de la simulación) y §5.3 (resultados Fase 3). | Informe §4.4, §5.3 | 2026-09-15 | C-8. |
| D-4 | Informe final: Resumen (cierre Fase 2/3), Abstract, §1.4 estructura del documento, §6 conclusiones, Anexo E (código) y Anexo F (guía de uso para el encargado de pedidos). | Informe (marcas `[PENDIENTE]`) | 2026-09-15 | D-2, D-3. |
| D-5 | Pegar el texto completo del marco teórico (`documentos/Marco_teorico_nuevo.docx`) en el `.docx` final; hoy §3 es resumen. | Informe §3 (nota) | 2026-09-15 | Cierre del informe. |
| D-6 | Mencionar en todo informe de avance la dificultad del mes 2 (datos externos no entregados) como lección. | `CLAUDE.md` | 2026-09-04 | Cada informe. |
| D-7 | Incorporar H-16 a los informes (Resumen Fase 1 §2.2, Informe final §4.3/§5.1.2): las líneas sin cantidad son físicas en Éxito pero la cota por valor está sobrestimada. Hacerlo cuando el cruce cubra todos los meses, para no publicar una cifra de un solo mes. | H-16 | 2026-10-02 | C-12. |

## 6. Recomendaciones metodológicas dadas en el chat (no son tareas, son criterios a recordar)

| # | Recomendación | Fecha | Estado |
|---|---|---|---|
| R-1 | Ninguna cifra producida con colocación como proxy de demanda se reporta como resultado del modelo; solo prueba que la tubería corre. | 2026-09-16 | Vigente hasta B-1. |
| R-2 | El tope de vida útil es una restricción dura, no un nivel de servicio: cuando manda, el pedido queda por debajo del nivel nominal y eso es deseado. | 2026-09-16 | Vigente (informe §4.5.5). |
| R-3 | Si el MASE de una clase no le gana al ingenuo con venta real, se revisa la asignación de método antes de simular. | 2026-09-16 | Vigente (informe §4.5.4). |
| R-4 | Toda cifra pasa por una prueba de sensibilidad y se registra como hallazgo H-nn antes de entrar a un informe evaluado. | 2026-09-15 | Vigente (regla del proyecto). |
| R-5 | Si el sell-out (B-1) nunca llega: (a) confirmar con Kellys si hay portal EDI/VMI directo de las cadenas (E-9); (b) si no, el modelo se entrega calibrado sobre sell-in (colocación) + devoluciones como mejor proxy disponible, documentando la ausencia de venta real como limitación metodológica explícita del informe final (afecta el objetivo específico 2), no como un vacío sin explicar. | 2026-09-28 | Vigente hasta que se resuelva B-1 o E-9. |

---

## Cerrados

| # | Pendiente | Cerrado | Cómo |
|---|---|---|---|
| — | Diseñar la arquitectura del modelo de pronóstico y la fórmula de cantidad a pedir (cronograma M4, adelantado). | 2026-09-16 | `codigo/modelo_stock_minimo.py` + informe §4.5. Queda como borrador hasta B-1 (ver C-6). |
| — | Redactar la sección metodológica de Fase 2 del informe final. | 2026-09-16 | Informe §4.5, commit `b716a54`. |
| — | Mover `GA05-Notas Credito.pbix` a `datos/crudos/`. | 2026-09-15 | Hecho (bitácora 2026-09-15). |
