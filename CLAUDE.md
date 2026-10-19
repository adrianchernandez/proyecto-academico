# Práctica empresarial — Postobón S.A. (Ingeniería Industrial, U. de A.)

## Identificación
- Estudiante: Adrian Camilo Hernández Copete, semestre 10, Ing. Industrial, U. de Antioquia.
- Empresa: Postobón S.A., área de Desarrollo Logístico, Medellín.
- Asesora interna (U. de A.): Olga Cecilia Usuga Manco.
- Asesora externa (Postobón): Kellys Johana Otero Palacio, Ingeniera de desarrollo logístico.
- Práctica: 22/06/2026 – 21/12/2026 (6 meses).

## Salida principal del modelo (definición central — no perder de vista)
El entregable concreto de la herramienta es la **cantidad a pedir** (unidades
a reabastecer) por SKU y por punto de venta (Éxito y Olímpica, cada uno con
su propio cálculo), en cada ciclo de reabastecimiento.
- Pronóstico de demanda, rotación real y vida útil remanente son los
  INSUMOS del cálculo, no el resultado.
- El resultado final que debe ver el encargado de pedido es un número por
  SKU/tienda: "pide X unidades de este SKU en esta tienda."
- El cálculo balancea dos fuerzas opuestas: evitar quiebre de stock (pedir
  muy poco) y evitar sobrestock que termine en vencimiento (pedir de más) —
  no es una minimización simple de la cantidad pedida.
- Cualquier función, script o salida que construya debe converger en esta
  cantidad a pedir; si un análisis no aporta a ese número final, verificar
  que sí corresponde a una fase intermedia (diagnóstico, pronóstico) y no
  se está desviando del objetivo.

## Objetivo general
Desarrollar una herramienta estadística de reabastecimiento basada en la
optimización del stock mínimo para reducir las devoluciones por caducidad en
puntos de venta del canal moderno.

## Objetivos específicos
1. Diagnosticar el estado actual de las devoluciones y el comportamiento
   histórico de ventas.
2. Diseñar un modelo estadístico de pronóstico y stock mínimo que integre
   rotación real y vida útil del producto.
3. Validar la herramienta mediante simulación de escenarios y prueba piloto
   frente a los parámetros tradicionales.

## Alcance (IMPORTANTE — restricción dura)
El proyecto se limita a:
- **2 puntos de venta**: Ex 039 Éxito San Antonio (SAP 1000129473) y
  St 341 Villanueva – Olímpica (SAP 1000205719), regional Antioquia.
- **Categoría BNA (Bebidas No Alcohólicas)**: los datos de ventas,
  devoluciones, colocación y vida útil disponibles son únicamente de esta
  categoría, no de todo el portafolio de Postobón. En la clasificación del
  Power BI GA05 esto corresponde a las etiquetas **"BNA" y "Mundo Cero"** (la
  línea sin azúcar de las mismas bebidas; hallazgo H-09). CCC (cerveza) y
  Nutrimenti quedan fuera. Constante `CLASIFICACIONES_ALCANCE` en `codigo/comun.py`.

Cualquier análisis, modelo, gráfico o resultado debe enmarcarse en estos dos
puntos de venta Y en la categoría BNA. No generalizar ni extrapolar
resultados a otros puntos de venta, otras categorías de producto, ni a "todo
el canal moderno" o "todo el portafolio" de forma general, salvo que se pida
explícitamente como reflexión teórica.

## Estado real del cronograma (desviación respecto a la propuesta)
La propuesta original ubicaba la recolección/depuración de datos en el mes 2.
Ese mes se perdió porque Postobón no entregó los datos a tiempo; apenas al
iniciar el mes 3 quedaron de entregarlos. Por lo tanto:
- Fase 1 (diagnóstico) arranca realmente en el mes 3, no en el mes 2.
- El resto de fases (diseño, validación, documentación) se corre
  proporcionalmente hacia atrás.
- Al redactar avances, informes o cronogramas, usar el cronograma real de
  abajo, NO el original de la propuesta, y nunca asumir que voy "a tiempo"
  según el documento inicial.
- Esta desviación (dependencia de datos externos) debe mencionarse como
  lección/dificultad cuando se redacte sobre avances o informes.

### Cronograma real ajustado
| Periodo | Contenido |
|---|---|
| M1 (22/06–21/07) | Fase 0 — Contextualización — completado |
| M2 (22/07–21/08) | Perdido, sin avances (datos externos no entregados) |
| M3 (22/08–21/09) ← estoy aquí | Fase 1 completa: recolección/depuración de datos (Éxito y Olímpica), revisión de literatura, diagnóstico inicial |
| M4 (22/09–21/10) | Cierre Fase 1 (priorización categorías/puntos críticos) + inicio Fase 2 (diseño modelo de pronóstico) |
| M5 (22/10–21/11) | Cierre Fase 2 (fórmula de stock mínimo + herramienta en Python/R) + inicio Fase 3 (simulación de escenarios) |
| M6 (22/11–21/12) | Cierre Fase 3 (prueba piloto + análisis/ajustes) + Fase 4 (documentación final, socialización, cierre) |

## Evaluación (ponderaciones)
- Propuesta: 20% (ya entregada)
- Seguimiento: 10%
- Informes parciales: 10%
- Informe final: 40%
- Sustentación: 20%

## Restricciones técnicas
- El modelo estadístico (pronóstico de demanda, cálculo de stock mínimo,
  simulación de escenarios) se construye en **Python o R, con código real**,
  nunca solo como fórmulas de Excel. Debe quedar documentado, replicable y
  ajustable.
- Excel y Power BI solo se usan para exploración inicial o presentación de
  resultados, no para el modelo en sí.
- Al ayudar con modelado: dar código funcional y explicar la lógica
  estadística detrás de cada paso (no solo el código sin justificación).
- Cualquier entregable (informe, gráfico, resultado numérico) debe trabajarse
  sobre datos reales de los 2 puntos de venta definidos (Éxito, Olímpica).
  Preguntas genéricas de teoría sí pueden responderse en general.

## Fuentes de datos (esquema real, actualizado 15/09/2026)
Todo vive en `datos/crudos/` y se carga SOLO a través de `codigo/comun.py`
(`cargar_devoluciones`, `cargar_colocacion`, `cargar_vidas_utiles`,
`cargar_notas_credito`, `cargar_maestro_pdv`, `cargar_devoluciones_cen_exito`,
`cargar_avisos_cen_olimpica`, `cargar_maestro_portafolio_exito/olimpica`). Ventana: 01/09/2024 – 31/08/2026.

| Archivo | Origen | Grano / columnas clave | Filas |
|---|---|---|---|
| `Colocacion.xlsx` | Extracto SAP | `Fecha pedido`, `Fecha entrega`, `Centro - Clave` (43/79), `Cliente SAP - Clave` (cadena), `Material SAP - Clave/Texto`, `Cantidad colocada en cajas físicas` | 22.358 |
| `devoluciones_vencimiento_analitico.csv` | Consulta DAX al modelo `GA05-Notas Credito.pbix` (motivo *Fecha De Vencimiento*, tipo *Devolución*, BNA + Mundo Cero) | `Fecha devolución`, `Centro`, `Cliente SAP`, `Punto de venta`, `Material SAP`, `Marca`, `Clasificacion`, unidades, cajas físicas, hectolitros, valor neto, n.º líneas | 1.979 |
| `devoluciones_vencimiento_diario_*.csv/.xlsx` | Misma consulta, solo cajas (entregable) | fecha × PDV × SKU | 1.979 |
| `notas_credito_todas_*.csv` | Segunda consulta DAX (todos los motivos, tipos y clasificaciones) | `Fecha`, `Punto de venta`, `SKU`, `Clasificacion`, `Tipo`, `Motivos`, `Cajas`, `Unidades`, `Notas credito` | 3.513 |
| `Vidas utiles.XLSX` | Maestro SAP, **solo centro 43** | `Ce.`, SKU, material, `Vida_util_dias` | 1.588 |
| `Puntos de venta.xlsx` | Maestro comercial (2 hojas) | CEDI, llave SAP, PDV, frecuencia de pedido y entrega; pares pedido→entrega | 2 PDV |
| `GA05-Notas Credito.pbix` | Modelo Power BI (94 MB) | Tabla `Devoluciones`; consulta DAX en `analisis_diagnostico_fase1.py` §2 | — |
| `Devoluciones enero 2026/*.csv` | Plataforma CEN, portal Éxito (31 descargas, nombre GUID) | `#DEVOL`, `DEP ORIGEN` (0039 = San Antonio), `EAN`, `CANTIDAD` (unidades del EAN), `FECHA DEVOL`, `FECHA RECOGIDA`; sin valor, motivo ni n.º de nota; todas las tiendas Éxito (H-16) | 8.511 (76 de la 039) |
| `Devoluciones enero 2026/*.txt` | CEN, Olímpica *AVISO RECIBO VALORIZADO* | Recibos del CD Barranquilla 8001 (no son devoluciones de Villanueva, H-16) | 277 ítems |
| `MAESTRO PORTAFOLIO EXITO.xlsx` | Maestro comercial Éxito | `Plu`, `Ean`, `SAP` (SKU Postobón), `Dependencia` (tienda) | 87.065 |
| `MAESTRO PORTAFOLIO OLIMPICA.xlsx` | Maestro comercial Olímpica (hoja ACT) | `Ce.`, `CEDI POSTOBON`, `EAN`, artículo Olímpica; **sin SKU SAP** y sin CEDI de Antioquia | 62.158 |

Reglas de depuración ya decididas (no rediscutir; detalle en
`informes/Registro_hallazgos.md`): denominador = colocación bruta (filas
positivas, H-01); unidad = caja física (H-04); fecha = `Día Transacción`
(H-02); las líneas de nota crédito con valor y sin cantidad quedan marcadas
`Solo_valor` y fuera de todo conteo físico (H-03); ambas tiendas cambiaron
del centro 79 al 43 en junio/2025 (H-05).

**Pendiente de recibir:** venta diaria al consumidor (sell-out) e inventario
en tienda (seguir `PENDIENTE_ventas_diarias.md`), y devoluciones desde la
plataforma CEN para contrastar las líneas sin cantidad del GA05 (H-03; seguir
`PENDIENTE_devoluciones_CEN.md`). Del CEN llegó solo enero/2026 (H-16): falta
Éxito jul/2025 – abr/2026 y las devoluciones de la tienda 341 de Olímpica. Al llegar cualquiera, actualizar esta tabla
con su esquema real.

## Resultados esperados de la herramienta (de la propuesta)
- Diagnóstico cuantificado de devoluciones por vencimiento en Éxito y
  Olímpica, con categorías/puntos críticos identificados.
- Modelo estadístico de pronóstico de demanda ajustado a vida útil.
- Herramienta funcional para calcular stock mínimo dinámico por SKU y punto
  de venta.
- Simulación comparativa: modelo propuesto vs. reabastecimiento tradicional.
- Documento metodológico replicable.

## Estructura del repositorio (definida el 04/09/2026)
```
CLAUDE.md                    contexto y reglas del proyecto
README.md                    mapa del repositorio y cómo reproducir el análisis
bitacora_avances.md          registro acumulado de avances
PENDIENTE_ventas_diarias.md  qué pegar y qué hacer cuando llegue la venta diaria
PENDIENTE_devoluciones_CEN.md  qué pegar y qué hacer cuando lleguen las devoluciones del CEN
PENDIENTES.md                lista viva única de pendientes, preguntas y recomendaciones
codigo/
  comun.py                   rutas, constantes, paleta y CARGADORES de datos (única puerta a datos/crudos)
  analisis_diagnostico_fase1.py/.ipynb   indicador, hallazgos 1–4, figuras 1–4, consultas DAX
  eda_fase1.py/.ipynb        calidad, verificación GA05, exploración, intermitencia, robustez,
                             gráficos básicos (cajas, histogramas, correlación, dispersión), figuras 5–14
  cruce_devoluciones_cen.py/.ipynb  cruce GA05 vs. plataforma CEN (H-16), figura 15
  sincronizar_notebooks.py   regenera los .ipynb desde los .py (sin salidas)
  generar_informe_docx.py    convierte informes/*.md a Word con las figuras embebidas
datos/crudos/                extractos de Postobón, CSV de las consultas DAX y el .pbix
datos/procesados/            tablas calculadas por el código
figuras/                     PNG generados por el código
informes/                    Registro_hallazgos.md, Informe_avance_NN.md, Informe_final_borrador.md,
                             Resumen_diagnostico_Fase1.md (versionados); .html no
documentos/                  propuesta, plantilla U. de A., Marco_teorico_nuevo.docx, contexto (no versionado)
```
Reglas al crear archivos nuevos:
- Código nuevo (pronóstico, stock mínimo, simulación) va en `codigo/`, nunca
  en la raíz, y **carga los datos con las funciones de `comun.py`** (nunca
  con `pd.read_*` directo sobre `datos/crudos/`), para que todos los scripts
  hereden las mismas reglas de depuración.
- Los scripts se escriben con celdas `# %%` y narrativa en markdown; el
  `.ipynb` se regenera con `python codigo/sincronizar_notebooks.py` y nunca
  se edita a mano ni se guarda con salidas.
- Nada que lea un dato de Postobón debe apuntar a la raíz: los insumos están
  en `datos/crudos/` y las salidas se escriben en `datos/procesados/`.
- El código no usa `Path.cwd()`: `comun.raiz_proyecto()` localiza la raíz
  subiendo hasta encontrar `CLAUDE.md`.
- La raíz solo guarda los archivos de contexto/registro listados arriba;
  `datos/`, `figuras/`, `informes/*.html` y `documentos/` no se versionan.
- Numeración de figuras: continua entre scripts (1–4 diagnóstico, 5–14 EDA);
  las nuevas siguen desde la 16 (la 15 es el cruce CEN).
- Los informes se escriben en Markdown en `informes/` con las figuras
  referenciadas como `![leyenda](figuras/figN.png)` (ruta desde la raíz) y en
  el punto donde se discuten; la versión Word se genera con
  `python codigo/generar_informe_docx.py informes/<informe>.md` y no se
  versiona (contiene cifras de la operación).

## Registro de hallazgos (documentar oportunamente)
Todo hallazgo sobre los datos, la exportación o el método se anota **en el
momento** en `informes/Registro_hallazgos.md` con código H-nn (fecha, fuente,
evidencia con cifras, impacto, decisión, estado Abierto/Cerrado). El código y
los informes citan ese código. Un hallazgo que corrija una cifra ya publicada
se marca "corrige informe" y se corrige el informe en la misma sesión.
Hallazgos abiertos al 15/09/2026 para agenda con la asesora externa: H-02
(fecha contable), H-03 (notas crédito sin cantidad), H-05 (vida útil del
centro 79), H-06 (entregas de Olímpica fuera de X/S), H-13 (venta diaria),
H-16 (CEN: notas sin cantidad físicas pero valoradas varias veces en el GA05).

## Estado de los hallazgos del diagnóstico (no volver a la versión del 03/09)
La auditoría del 15/09/2026 reformuló dos hallazgos del diagnóstico inicial:
- Hallazgo 2 ("rezago de un mes", r = 0,716) es un **episodio** (dic/2024 →
  ene/2025), no un patrón: Spearman 0,03 (H-08).
- Hallazgo 3 ("cobertura > vida útil devuelve 4,7×") se reemplaza por el
  **gradiente**: la tasa crece de forma monótona con intervalo entre entregas ÷
  vida útil (Fig. 10; Spearman +0,49 Éxito, +0,61 Olímpica) (H-07).
Las tasas 1,55 % (Éxito) y 3,97 % (Olímpica) se leen como **piso** por las
notas crédito sin cantidad (cota superior 2,12 % y 12,44 %, H-03).

## Qué falta y se agregará después (a propósito, no ahora)
- Esquema real de los datos (cuando lleguen).
- Convenciones de nombres, librerías elegidas, etc. — se documentan cuando
  se decidan, no antes.

## Formato de citación
APA (compatible con NTC 5613). Verificar con la asesora si el cuerpo del
informe exige IEEE.

## Marco teórico ya definido (no reinventar)
**Vigente para el informe final:** el archivo
`documentos/Marco_teorico_nuevo.docx` (copiado el 15/09/2026 desde Descargas;
su síntesis y las 23 referencias ya están en
`informes/Informe_final_borrador.md` §3 y Referencias) contiene el marco
teórico vigente y verificado para el informe final de la práctica (no para la
propuesta, que ya fue entregada y evaluada y no debe modificarse).
`documentos/Revision_de_literatura.html` es la versión visual del mismo marco
(sin lista de referencias) y `documentos/Contexto_Proyecto_MarcoTeorico.md` el
contexto con el que se construyó. Este documento reemplaza en profundidad y especificidad
al marco teórico breve de 5 ejes que aparece dentro de la propuesta 
original — úsalo como referencia principal para cualquier trabajo 
relacionado con el sustento teórico del proyecto (redacción del informe, 
ampliación de secciones, discusión de resultados frente a la literatura, 
etc.). Todas sus 23 referencias fueron verificadas una por una contra la 
fuente original (autor, año, revista, volumen y páginas reales); no agregues 
ni cites fuentes nuevas sobre este tema sin la misma verificación.


## Resumen de avance al cierre de cada sesión con progreso real
Cada vez que en una sesión se logre un avance real del proyecto (no solo
exploración o pruebas fallidas) — ej. se depuró un dataset, se ajustó el
modelo de pronóstico, se calculó el stock mínimo para un SKU/tienda, se
corrió una simulación — generar al final un resumen breve en este formato,
para que yo lo copie directo al chat de claude.ai donde redacto los
entregables (informes, seguimiento, etc.):

```
### Avance — [fecha]
**Fase/objetivo relacionado:** (ej. Fase 1 – Diagnóstico)
**Qué se hizo:** (2-4 líneas, en lenguaje claro, no solo técnico)
**Resultados clave / cifras:** (números concretos si los hay, separados
Éxito vs. Olímpica cuando aplique)
**Decisiones o supuestos tomados:** (si se decidió algo metodológico,
ej. qué método de pronóstico se usó y por qué)
**Pendientes / bloqueos:** (si algo quedó a medias o depende de algo externo)
**Próximo paso:**
```

No generar este resumen tras cada mensaje — solo al cierre de una sesión
donde hubo avance real, o cuando yo lo pida explícitamente ("hazme el
resumen de avance").

## Lista única de pendientes (`PENDIENTES.md`)
- Es el único lugar donde viven los pendientes, las preguntas para las asesoras
  y las recomendaciones dadas en el chat. Consolida el registro de hallazgos, la
  bitácora, `PENDIENTE_ventas_diarias.md`, `PENDIENTE_devoluciones_CEN.md` y las marcas `[PENDIENTE]` del informe.
- **Cada vez que se dé una recomendación o surja un pendiente en una sesión, se
  agrega a `PENDIENTES.md` en el mismo momento** (con fecha y origen), no al
  cierre. Si no queda ahí, se pierde.
- Un pendiente resuelto se mueve a "Cerrados" con fecha y cómo se resolvió; no se
  borra.
- Cuando pregunte "qué tengo pendiente", "qué me recomendaste" o similar, leer
  `PENDIENTES.md` y responder desde ahí, no reconstruir de memoria.
- Los hallazgos abiertos del `Registro_hallazgos.md` se reflejan ahí como
  preguntas; al cerrarse un hallazgo se cierra también su fila.

## Bitácora acumulada (trazabilidad histórica)
Además de mostrar el resumen de avance en el chat, mantener un archivo
`bitacora_avances.md` en la raíz del proyecto:
- Si el archivo no existe, crearlo.
- Cada avance real se **agrega al final** del archivo (nunca sobrescribir ni
  borrar entradas anteriores), con el mismo formato de la sección anterior,
  separado del resto por una línea `---`.
- Este archivo es el registro histórico completo de la práctica: sirve para
  reconstruir qué se hizo mes a mes frente al cronograma real, como respaldo
  ante la asesora, y como insumo directo para el informe final y la
  sustentación.
- Si en algún momento pido "revisa la bitácora" o "resume el avance del mes
  X", leer este archivo en vez de reconstruir de memoria.

## Control de versiones del código (git)
- Si el proyecto de código aún no tiene repositorio, inicializarlo
  (`git init`) apenas se empiece a escribir código real.
- **IMPORTANTE — confidencialidad de datos:** los datos de Postobón (ventas,
  devoluciones, vida útil, maestro de tiendas) son información de la empresa
  y NUNCA deben quedar versionados en git. Crear/mantener un `.gitignore`
  que excluya carpetas o archivos de datos crudos/procesados (ej. `data/`,
  `*.csv`, `*.xlsx` con datos reales), credenciales, y cualquier ruta de
  conexión a sistemas internos. Solo se versiona código, scripts, y
  resultados agregados si hace falta compartirlos (sin datos identificables
  de la operación real).
- Cada vez que haya un avance real de código (mismo criterio que el resumen
  de avance y la bitácora), hacer un commit con mensaje breve y descriptivo
  ligado a la fase/objetivo, ej.:
  `git commit -m "Fase 1: depuración inicial de ventas Éxito y Olímpica"`.
- Commits locales no requieren pedir permiso. Si en algún momento se sube el
  repositorio a un remoto (ej. GitHub), debe ser **privado** — nunca
  público — y confirmar conmigo antes de hacer push.
- Con esto, al cierre de cada sesión con avance real quedan tres cosas
  actualizadas: el resumen que te muestro en el chat, la entrada en
  `bitacora_avances.md`, y el commit en git.

## Cómo trabajar conmigo en este proyecto
- Soy directo y breve en las peticiones; usa tu criterio sobre qué es
  necesario incluir, no te limites a lo literal.
- Si construyes código de modelado, explica primero la lógica estadística en
  pocas líneas y luego el código.
- Si el resultado o análisis no distingue explícitamente entre Éxito y
  Olímpica, probablemente está mal — revisar antes de entregar.
