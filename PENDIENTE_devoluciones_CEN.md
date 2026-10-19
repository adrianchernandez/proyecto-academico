# Pendiente: devoluciones por vencimiento desde la plataforma CEN

> **Estado al 02/10/2026 (H-16):** llegó un primer envío, solo **enero/2026**
> (`datos/crudos/Devoluciones enero 2026`). Pasos 0–2 ejecutados para ese mes en
> `codigo/cruce_devoluciones_cen.py`. Resultado en Éxito: las líneas sin cantidad
> **sí son devoluciones físicas**, pero el GA05 las valora ≈ 4,3 veces (notas
> repetidas), así que la cantidad debe salir del portal y no de valor ÷ precio
> (variante del escenario A). Los TXT de Olímpica son avisos de recibo del CD
> Barranquilla, no devoluciones de Villanueva. Falta: CEN de Éxito jul/2025 –
> abr/2026 (B-3a), devoluciones de la tienda 341 (B-4) y respuesta a E-10/E-11.
> Esquema real del portal Éxito: grano devolución × EAN, cantidad en unidades del
> EAN, **sin** valor, motivo ni número de nota crédito (el cruce va por SKU y fecha).

El tablero GA05-Notas Crédito trae 635 líneas de devolución por vencimiento con
valor y **sin cantidad** (cajas = unidades = hectolitros = 0; hallazgo H-03). Pesan
$26,6 M (34,7 % del valor) y, si fueran físicas, subirían la tasa de 1,55 % a 2,12 %
en Éxito y de 3,97 % a 12,44 % en Olímpica. El 18/09/2026 se decidió pedir las
devoluciones desde una **segunda fuente, la plataforma CEN**, para ver si esas
mismas líneas allí sí traen cantidad. Este archivo tiene dos partes: **lo que hay
que pegar en el chat cuando llegue el extracto** y **lo que Claude hará con él**.

Cifras de referencia de las líneas sin cantidad (`comun.cargar_devoluciones()`,
columna `Solo_valor`):

| | Éxito San Antonio | Olímpica Villanueva |
|---|---|---|
| Líneas (fecha × SKU) | 404 | 231 |
| Notas crédito | 482 | 294 |
| SKU afectados | 128 | 72 |
| Valor neto | $15.253.694 | $11.349.205 |
| Fechas | 14/07/2025 – 16/04/2026 | 08/11/2025 – 15/04/2026 |
| Centro | 43 (todas) | 43 (todas) |

---

## 1. Texto para pegar en el chat cuando tenga el archivo

> Ya tengo las devoluciones desde la plataforma CEN. El archivo está en
> `datos/crudos/<NOMBRE_DEL_ARCHIVO>` (formato: <xlsx / csv>, una fila por
> <nota crédito × SKU / día × SKU × tienda / otro grano>). La cantidad viene en
> <unidades / cajas físicas / ambas>. <Sí / No> trae el número de documento o nota
> crédito SAP. <Sí / No> trae el motivo de la devolución. Cubre <periodo>. Sigue el
> plan de `PENDIENTE_devoluciones_CEN.md`.

Si no se sabe alguno de los datos entre `< >`, dejarlo en blanco: el primer paso es
averiguarlo del propio archivo.

Preguntas para la asesora externa **al recibir el extracto** (ideal: pedirlas con el
archivo):

1. ¿El CEN registra la devolución física en el punto de venta (recogida / baja en
   tienda) o el documento contable? Es decir, ¿es una fuente *anterior* a la nota
   crédito o una copia de ella?
2. ¿Trae el número de nota crédito o de documento SAP para cruzar línea a línea con el
   GA05? Sin esa llave el cruce se hace por fecha × tienda × SKU.
3. ¿La cantidad es en unidades de consumo o en cajas físicas? ¿Con qué factor por SKU?
4. ¿Incluye todos los motivos (vencimiento, avería, etc.) o solo vencimiento?
5. ¿Cubre desde sep/2024 o solo desde que las tiendas pasaron al centro 43 (jun/2025)?

---

## 2. Plan de trabajo con el extracto del CEN (lo que hará Claude, en este orden)

### Paso 0 — Registrar y proteger
- Guardar el archivo en `datos/crudos/` (ya está ignorado por git; verificar con
  `git status` que no aparece).
- Abrir el hallazgo **H-16 · Devoluciones desde la plataforma CEN** en
  `informes/Registro_hallazgos.md` con el esquema real del archivo (columnas, grano,
  filas, periodo) y actualizar la tabla de fuentes de `CLAUDE.md`.

### Paso 1 — Cargador en `codigo/comun.py`
- `ARCHIVO_DEVOLUCIONES_CEN` y `cargar_devoluciones_cen()` con columnas normalizadas
  `Fecha, PDV, SKU, Material, Cajas_cen, Unidades_cen, Valor_cen` (+ `Documento` si
  viene). Mapa de tienda con `MAPA_PDV` / `MAPA_SAP`; conversión a cajas físicas si
  la cantidad viene en unidades (factor por SKU tomado de las líneas del GA05 que
  traen unidades y cajas; recordar que `Cantidad UMB` no es confiable, H-04).
  Controles: sin duplicados en la llave, fechas dentro de la ventana, cantidades no
  negativas, PDV mapeado.
- Filtrar al alcance: dos tiendas, motivo vencimiento (si viene), clasificación BNA +
  Mundo Cero (si viene; si no, filtrar por los SKU del maestro de vidas útiles).

### Paso 2 — Cruce con el GA05 (`codigo/cruce_devoluciones_cen.py`)
El objetivo es responder tres preguntas, por tienda:

1. **¿Las líneas `Solo_valor` del GA05 tienen cantidad en el CEN?** Cruce por
   documento si existe; si no, por fecha × PDV × SKU con tolerancia de ±3 días.
   Salida: cuántas de las 404 (Éxito) y 231 (Olímpica) líneas encuentran pareja en
   el CEN, con qué cantidad, y si el valor coincide.
2. **¿Las líneas con cantidad coinciden entre fuentes?** Para las 1.344 líneas físicas
   del GA05, comparar cajas GA05 vs. cajas CEN (diferencia absoluta y relativa por
   línea, por mes y por SKU). Esto valida que el CEN es comparable antes de usarlo
   para rellenar.
3. **¿Hay devoluciones en el CEN que no están en el GA05, o al revés?** Conteo y
   cajas de líneas huérfanas en cada dirección.

Salidas en `datos/procesados/`: `cruce_cen_solo_valor_<tienda>.csv`,
`cruce_cen_coincidencia_<tienda>.csv`, `cruce_cen_resumen.csv`. Figura 15:
dispersión cajas GA05 vs. cajas CEN por línea y barras mensuales de las tres
categorías (coinciden / solo GA05 / solo CEN), separadas por tienda.

### Paso 3 — Decisión sobre el numerador
Según lo que salga del Paso 2 hay tres escenarios, y se elige uno **explícitamente**
(hallazgo H-16, decisión):

| Escenario | Evidencia | Qué se hace |
|---|---|---|
| A. El CEN trae cantidad para las líneas sin cantidad y coincide en las demás | ≥ 90 % de las líneas físicas coinciden en cajas (±10 %) y la mayoría de las `Solo_valor` encuentran pareja | `cargar_devoluciones()` rellena `Cajas_dev` de las líneas `Solo_valor` con el CEN (columna `Origen_cantidad` = "GA05" / "CEN"); se recalculan tasas, figuras 1, 4, 10 y tablas; se corrigen los cuatro informes ("corrige informe") y las tasas dejan de leerse como piso. |
| B. El CEN no trae cantidad para esas líneas (tampoco allí son físicas) | Las `Solo_valor` no aparecen en el CEN o aparecen con cantidad 0 | Se confirma que son documentos solo por valor (ajuste, no retorno físico): se cierran H-03 y E-2, las tasas actuales quedan como definitivas y la cota superior se elimina de los informes. |
| C. El CEN no es comparable (grano, unidad o cobertura distintos) | Coincidencia baja también en las líneas físicas | El CEN no sirve para rellenar; se documenta la limitación, se mantiene la lectura "piso / cota superior" y se insiste en la pregunta E-2 a la asesora. |

### Paso 4 — Propagar
- Si es el escenario A, volver a correr en orden `analisis_diagnostico_fase1.py`,
  `eda_fase1.py`, `sku_activos.py` y `modelo_stock_minimo.py`, y revisar que el
  universo de SKU activos (H-15) no cambie (las `Solo_valor` ya contaban como
  actividad, así que no debería).
- Actualizar `Resumen_diagnostico_Fase1.md` §2.2 y §3, `Informe_avance_01.md` §5.3 y
  §5.5, `Informe_final_borrador.md` §4.3 y §5.1.2, y regenerar los Word.
- Cerrar o actualizar en `PENDIENTES.md`: B-3, E-2 y la fila de H-03.

### Paso 5 — Documentar y cerrar la sesión
- Entrada en `bitacora_avances.md`, resumen de avance en el chat y commit
  `Fase 1: cruce de devoluciones GA05 vs. CEN (H-16)`.
