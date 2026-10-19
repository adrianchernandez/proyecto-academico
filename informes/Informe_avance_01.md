# Informe de avance N.º 1 — Práctica empresarial Postobón S.A.

**Título del proyecto:** Construcción de una herramienta estadística de reabastecimiento que permita reducir las devoluciones por productos vencidos en los puntos de venta de canal moderno — una herramienta para la planeación del stock mínimo.
**Estudiante:** Adrian Camilo Hernández Copete — Ingeniería Industrial, Universidad de Antioquia.
**Asesora interna:** Olga Cecilia Usuga Manco. **Asesora externa:** Kellys Johana Otero Palacio (Desarrollo Logístico, Postobón S.A.).
**Periodo cubierto:** 22/06/2026 – 18/09/2026 (meses 1 a 3 de 6).
**Fecha de corte:** 18 de septiembre de 2026.

Este informe está escrito para leerse de principio a fin: primero qué se propuso
y qué cambió en el calendario, luego lo hecho mes a mes, después los hallazgos
sobre los datos y los resultados del diagnóstico, y por último las dificultades y
lo que sigue. Las cifras salen del código en `codigo/` y las tablas en
`datos/procesados/`; cada hallazgo sobre los datos tiene un código H-nn en
`informes/Registro_hallazgos.md`.

---

## 1. Resumen ejecutivo

- La Fase 0 (contextualización) se completó en el mes 1. El mes 2 se perdió porque
  Postobón no entregó los datos; llegaron al inicio del mes 3. Todo el cronograma se
  corrió un mes hacia atrás.
- En el mes 3 se completó la **Fase 1** con los datos disponibles: se recibieron,
  verificaron y depuraron cuatro fuentes (colocación, notas crédito del Power BI GA05,
  vidas útiles, maestro de puntos de venta); se hizo el análisis exploratorio; se
  calculó el indicador principal y se sometieron los hallazgos a pruebas de robustez.
- **Indicador principal (24 meses, cajas físicas):** tasa de devolución por
  vencimiento de **1,55 %** en Éxito San Antonio (1.401 de 90.636 cajas) y **3,97 %**
  en Olímpica Villanueva (175 de 4.406 cajas). El vencimiento es el primer motivo de
  devolución en ambas tiendas (61 % y 62 % del total devuelto).
- **Hallazgo central (corregido tras la auditoría del 15/09):** la tasa de devolución
  crece de forma continua con la fracción de la vida útil del producto que consume
  el intervalo entre entregas: de 0,4 % a 12,4 % en Éxito y de 0,2 % a 17,1 % en
  Olímpica. Es el mecanismo que la herramienta debe controlar.
- **Hallazgo sobre los datos que sigue abierto:** un tercio de las líneas de nota
  crédito por vencimiento trae valor pero ninguna cantidad (desde julio/2025, solo
  centro 43). Las tasas anteriores son un piso; la cota superior sería 2,1 % en Éxito y
  12,4 % en Olímpica. Está pendiente aclarar con la asesora externa qué documento las
  genera.
- **Bloqueo:** la venta diaria al consumidor (sell-out) no se ha entregado. Con ella
  se calibra el modelo; sin ella el diagnóstico está completo pero la Fase 2 solo
  puede diseñarse, no calibrarse.
- **Estado frente a los objetivos específicos:** OE1 (diagnóstico) cumplido con los
  datos disponibles; OE2 (diseño del modelo) por iniciar en el mes 4; OE3
  (validación) programado para los meses 5 y 6.

---

## 2. Qué se propuso y qué cambió

### 2.1 Objetivo y alcance

Desarrollar una herramienta estadística de reabastecimiento basada en la
optimización del stock mínimo para reducir las devoluciones por caducidad en puntos
de venta del canal moderno. El entregable concreto es la **cantidad a pedir por SKU y
por tienda en cada ciclo**; el pronóstico de demanda, la rotación real y la vida útil
remanente son sus insumos.

El alcance se acotó a **dos puntos de venta** (Ex 039 Éxito San Antonio y St 341
Olímpica Villanueva, regional Antioquia) y a la **categoría BNA**, que en la
clasificación del GA05 corresponde a las etiquetas "BNA" y "Mundo Cero" (bebidas sin
azúcar del mismo portafolio; hallazgo H-09). Nada de lo que sigue se generaliza a
otras tiendas ni a otras categorías.

### 2.2 Cronograma propuesto frente al cronograma real

| Mes | Propuesta (30/07/2026) | Real |
|---|---|---|
| M1 (22/06–21/07) | Fase 0 — Contextualización | Fase 0 completada |
| M2 (22/07–21/08) | Fase 1 — Recolección y depuración de datos; revisión de literatura | **Sin avance:** Postobón no entregó los datos |
| M3 (22/08–21/09) | Fase 1 — Diagnóstico y priorización; Fase 2 — inicio del diseño | Fase 1 completa: datos, verificación, exploración, diagnóstico, revisión de literatura, auditoría |
| M4 (22/09–21/10) | Fase 2 — pronóstico y fórmula de stock mínimo; Fase 3 — inicio simulación | Cierre de Fase 1 (priorización formal) + inicio Fase 2 |
| M5 (22/10–21/11) | Fase 2 — herramienta; Fase 3 — simulación y piloto | Cierre Fase 2 + inicio Fase 3 |
| M6 (22/11–21/12) | Fase 3 — análisis del piloto; Fase 4 — documentación y cierre | Cierre Fase 3 + Fase 4 |

La desviación tiene una sola causa: dependencia de datos externos. Se registra como
dificultad en la sección 8.

---

## 3. Mes 1 — Fase 0: contextualización (22/06 – 21/07)

Reconocimiento del área de Desarrollo Logístico, del proceso de reabastecimiento
en canal moderno y de la problemática de devoluciones por vencimiento. Se
identificaron los sistemas de origen de los datos (SAP para colocación, el tablero
Power BI GA05-Notas Crédito para devoluciones y rechazos, el maestro de vidas útiles
por centro y el maestro de puntos de venta con frecuencia de pedido y entrega) y se
acordó con la asesora externa el recorte del alcance a dos tiendas y una categoría.
Se entregó la propuesta (30/07/2026).

---

## 4. Mes 2 — sin avance por datos externos (22/07 – 21/08)

Los extractos no se entregaron en el mes. No se pudo iniciar la depuración ni el
diagnóstico. Al cerrar el mes quedó el compromiso de entrega para el inicio del mes
3, que se cumplió parcialmente: llegaron colocación, vidas útiles y el maestro de
puntos de venta, y se obtuvo acceso al modelo GA05; **la venta diaria sigue
pendiente**.

---

## 5. Mes 3 — Fase 1 (22/08 – 18/09)

### 5.1 Datos recibidos y su esquema

| Fuente | Origen | Grano | Filas | Periodo |
|---|---|---|---|---|
| `Colocacion.xlsx` | Extracto SAP | fecha pedido × fecha entrega × centro × cadena × SKU | 22.358 | 02/09/2024 – 31/08/2026 |
| `devoluciones_vencimiento_analitico.csv` | Consulta DAX al modelo GA05 (motivo *Fecha De Vencimiento*, tipo *Devolución*) | fecha × tienda × SKU | 1.979 | 06/09/2024 – 29/08/2026 |
| `notas_credito_todas_2024-09_2026-08.csv` | Segunda consulta DAX al GA05 (todos los motivos y tipos) | fecha × tienda × SKU × tipo × motivo | 3.513 | 02/09/2024 – 29/08/2026 |
| `Vidas utiles.XLSX` | Maestro SAP, centro 43 | SKU | 1.588 (365 activos en las dos tiendas, §5.9) | — |
| `Puntos de venta.xlsx` | Maestro comercial | tienda | 2 | — |

Las devoluciones no se exportaron desde un visual del tablero sino con una consulta
DAX directa al modelo tabular que Power BI Desktop levanta al abrir el `.pbix`, lo
que deja la extracción documentada y repetible (la consulta está en
`codigo/analisis_diagnostico_fase1.py`, §2).

### 5.2 Verificación de la exportación del GA05

Se comprobó que los tres extractos del GA05 sean consistentes entre sí (tabla
`verificacion_exportacion_ga05.csv`):

- El extracto diario (solo cajas) y el analítico (todas las medidas) son idénticos
  fila a fila (1.979 llaves, 0 diferencias).
- El universo completo de notas crédito, filtrado a *Devolución* + *Fecha De
  Vencimiento* + BNA/Mundo Cero, reproduce el analítico en filas, cajas (1.575,97),
  unidades (13.241) y número de líneas.
- No hay cantidades negativas (la medida del tablero ya invierte el signo), ni fechas
  fuera de la ventana, ni duplicados en la llave.

**Conclusión:** la exportación es correcta. Lo que sí apareció es un problema del
modelo o del documento de origen, no de la exportación: **635 de las 1.979 líneas
(32 %) traen valor neto pero cero cajas, cero unidades y cero hectolitros** (H-03).
Suman $26,6 millones (34,7 % del valor). Solo ocurren con centro 43 y desde julio de
2025, y en enero/2026 (Éxito) y enero–febrero/2026 (Olímpica) el 100 % de las líneas
viene así. Como los mismos SKU sí traen cajas en otras fechas, no es un problema de
conversión de unidades. Las tasas en cajas no las incluyen y por eso se leen como
piso; si esas líneas fueran producto físico al precio implícito de cada SKU, la tasa
subiría a 2,12 % en Éxito y a **12,44 %** en Olímpica. Está pendiente aclarar con la
asesora externa qué documento SAP las genera.

![Fig. 5 · Líneas de nota crédito por vencimiento con cantidad (barra llena) y sin cantidad (rayada), por mes y tienda. Las líneas sin cantidad aparecen desde julio de 2025, solo con centro 43; en Éxito ene/2026 y Olímpica ene–feb/2026 todas las líneas vienen sin cantidad.](figuras/fig5_ga05_lineas_sin_cantidad.png)

### 5.3 Depuración y calidad de los datos

Reglas aplicadas (todas en `codigo/comun.py`, que comparten los scripts):

1. **Colocación bruta como denominador (H-01).** El archivo de colocación venía neto de
   notas crédito: 2.239 filas negativas (10 %), 1.225 de 1.252 coinciden al decimal
   con una devolución de la misma fecha, tienda y SKU. Se usan solo las filas positivas;
   con el archivo tal como vino, las tasas se inflarían a 1,59 % y 4,33 %.
2. **Caja física como unidad (H-04).** Es la única medida presente en colocación y
   devoluciones; la columna de unidades del GA05 no es confiable (62 líneas con
   unidades = 0 y cajas > 0).
3. **Fecha `Día Transacción` (H-02).** La otra columna de fecha del modelo llega hasta
   el año 2204. Falta confirmar cuál es la contable.
4. **Líneas sin cantidad marcadas (H-03)**, excluidas de todo conteo físico y
   reportadas aparte en valor.
5. **Anomalías menores documentadas (H-10):** 150 filas de colocación en cero, 23 filas
   en domingo (todas notas crédito), un SKU no bebida (cilindro de CO2, sin vida
   útil), 8 SKU devueltos sin colocación en la ventana (16 cajas), una fila "Sin
   Asignar" y 10 rechazos revertidos en el universo de notas crédito.
6. **Truncamiento por la izquierda (H-11):** 12 SKU (203 cajas, 12,9 %) muestran más
   devolución que colocación porque se colocaron antes del 01/09/2024.

Dos hechos estructurales que salieron de la exploración y condicionan el modelo:

- **Cambio de centro abastecedor (H-05).** Ambas tiendas recibieron del centro 79 hasta
  el 31/05/2025 y del centro 43 desde junio/2025. El maestro de vidas útiles es solo
  del 43. Las líneas sin cantidad aparecen justo después del cambio.
- **Calendario real de entregas (H-06).** Éxito cumple el maestro (lunes a sábado) al
  100 %. Olímpica concentra el 82 % de sus líneas en miércoles y sábado, como dice el
  maestro, pero recibió el **21 % de su colocación** (442 líneas, 51 fechas) otros días
  de la semana, en 23 de los 24 meses. El periodo de revisión del modelo debe salir del
  calendario observado, no del maestro.

![Fig. 6 · Líneas de colocación entregadas por día de la semana frente a los días declarados en el maestro de puntos de venta. Éxito cumple el calendario al 100 %; Olímpica recibe el 21 % de su colocación en días no declarados.](figuras/fig6_calendario_entregas.png)

### 5.4 Análisis exploratorio

Resultados de `codigo/eda_fase1.py` (figuras 7 a 9 y 11 a 14). Primero la
estructura de cada tienda y las series; después las distribuciones y relaciones
entre las variables que describen a cada SKU.

#### 5.4.1 Estructura de reposición, intermitencia y vida útil

- **Estructura de reposición.** Éxito recibe 5,1 veces por semana con un lote mediano
  de 2 cajas por línea (35 % de las líneas son de una caja o menos); Olímpica 1,9
  veces por semana con lote mediano de 1 caja (62 % de las líneas de una caja o
  menos). Lead time pedido → entrega de 1 a 3 días, mediana 2, en ambas.
- **Intermitencia de la demanda (H-12, Fig. 8).** Clasificando cada SKU por ADI y CV²
  sobre la colocación semanal (Syntetos, Boylan y Croston, 2005), el **83 % de los SKU
  de Éxito y el 87 % de Olímpica son intermitentes o abultados** (ADI > 1,32). Por
  volumen, en Éxito el 34 % de las cajas está en 36 SKU "suaves" de alta rotación y el
  42 % en SKU "abultados"; en Olímpica el 75 % del volumen es intermitente y no hay
  ningún SKU suave. Esto decide el método de pronóstico de la Fase 2: suavización
  exponencial solo para los SKU suaves de Éxito; Croston/SBA o TSB para el resto.
- **Vida útil del portafolio (Fig. 9).** Ponderada por cajas, la vida útil mediana es
  de 140 días en Éxito y 120 en Olímpica (160 y 150 por SKU). Casi la mitad de las
  cajas (49 % y 53 %) tiene vida útil de 120 días o menos.
- **Serie semanal de devoluciones (Fig. 7).** Éxito registra devolución física en 85
  de 106 semanas; Olímpica en 31. La devolución se registra en bloques, con picos los
  viernes en Éxito (29 % de las cajas) y los miércoles en Olímpica (33 %), es decir,
  en días de entrega: el camión que entrega recoge el vencido.
- **Motivos de devolución.** En el universo de notas crédito BNA/Mundo Cero, el
  vencimiento es el primer motivo de *devolución* en ambas tiendas; el mayor volumen de
  *rechazos* en Éxito es "No Salió Al Mercado" (4.871 cajas), producto que nunca llegó
  a la tienda y por eso no entra en el indicador.

![Fig. 7 · Cajas devueltas por vencimiento por semana. Éxito devuelve en 85 de 106 semanas; Olímpica en 31. Los círculos huecos marcan semanas cuyas notas crédito vienen todas sin cantidad (H-03).](figuras/fig7_serie_semanal_devoluciones.png)

![Fig. 8 · Clasificación ADI–CV² de la colocación semanal por SKU (Syntetos, Boylan y Croston, 2005). Casi todo el portafolio cae a la derecha del umbral ADI = 1,32: demanda intermitente o abultada.](figuras/fig8_intermitencia_adi_cv2.png)

![Fig. 9 · Porcentaje de cajas colocadas por rango de vida útil. Cerca de la mitad del volumen de ambas tiendas tiene vida útil de 120 días o menos.](figuras/fig9_vida_util_portafolio.png)

#### 5.4.2 Distribuciones y relaciones entre variables por SKU

Para cada SKU con al menos tres entregas en cada tienda (323 en Éxito, 141 en
Olímpica) se construyó una tabla con nueve variables: cajas colocadas, número de
entregas, lote medio, intervalo entre entregas, vida útil, intervalo ÷ vida útil,
ADI, CV² y tasa de devolución (`eda_variables_sku.csv`).

- **Diagramas de caja (Fig. 11).** Todas las variables de volumen y frecuencia son muy
  asimétricas, por eso se comparan medianas en escala logarítmica. Éxito tiene SKU con
  más entregas (mediana 31 frente a 13), lotes algo mayores (1,9 frente a 1,3 cajas) e
  intervalos mucho más cortos (12,9 frente a 35 días). La vida útil es prácticamente
  igual en las dos tiendas (mediana 168 y 160 días): **la diferencia entre tiendas no
  está en el producto sino en la frecuencia de reposición.** En consecuencia, la fracción
  intervalo ÷ vida útil es tres veces mayor en Olímpica (mediana 0,24 frente a 0,08).
- **Histogramas (Fig. 12).** La vida útil se concentra en unos pocos valores del
  maestro (112, 120, 180, 238, 270, 360 días); el lote medio se apila en 1–2 cajas; la
  tasa de devolución tiene una masa grande en cero y una cola larga.
- **Matriz de correlación de Spearman (Fig. 13).** Con la tasa de devolución, las
  variables que más correlacionan son intervalo ÷ vida útil (+0,36 en Éxito, +0,62 en
  Olímpica), ADI (+0,28 y +0,54) e intervalo entre entregas (+0,24 y +0,50). La vida
  útil sola correlaciona poco y en sentido negativo (−0,20 y −0,22); el lote medio, las
  cajas colocadas y el CV² casi nada. Intervalo y ADI son casi la misma información
  (ρ = 0,98), como corresponde.
- **Dispersión (Fig. 14).** La relación de la tasa con intervalo ÷ vida útil no es
  lineal: es casi nula por debajo de 0,05 y se abre a partir de 0,1, lo que justifica
  el análisis por tramos del hallazgo 3.

![Fig. 11 · Diagramas de caja de las variables por SKU, Éxito contra Olímpica. Escala logarítmica donde la distribución es muy asimétrica.](figuras/fig11_boxplots_variables_sku.png)

![Fig. 12 · Histogramas de las variables por SKU (densidad, por tienda).](figuras/fig12_histogramas_variables_sku.png)

![Fig. 13 · Matriz de correlación de Spearman entre las variables por SKU, por tienda. La última fila muestra qué correlaciona con la tasa de devolución.](figuras/fig13_correlacion_spearman.png)

![Fig. 14 · Tasa de devolución por SKU frente a intervalo ÷ vida útil, intervalo entre entregas, vida útil y lote medio (SKU con ≥ 20 cajas; tamaño ∝ cajas).](figuras/fig14_dispersion_tasa_variables.png)

### 5.5 Diagnóstico: indicador y hallazgos

| Indicador (01/09/2024 – 31/08/2026) | Éxito San Antonio | Olímpica Villanueva |
|---|---|---|
| Colocado bruto (cajas) | 90.635,7 | 4.406,3 |
| Devuelto por vencimiento, líneas con cantidad (cajas) | 1.401,3 | 174,7 |
| **Tasa de devolución por vencimiento** | **1,55 %** | **3,97 %** |
| Cota superior si las líneas sin cantidad fueran físicas (H-03) | 2,12 % | 12,44 % |
| Valor devuelto en líneas con cantidad | $44,0 M | $6,0 M |
| Valor en líneas sin cantidad | $15,3 M | $11,3 M |
| SKU con devolución física / días con devolución física (de 730) | 238 / 168 | 95 / 35 |
| Meses en cero real (de 24) | 0 | 6 |
| Devoluciones por todos los motivos (cajas) / tasa | 2.298,6 / 2,54 % | 281,8 / 6,39 % |
| Vencimiento sobre el total devuelto | 61,0 % | 62,0 % |

Olímpica devuelve 2,6 veces más que Éxito en proporción a lo que recibe, moviendo el
4,6 % del volumen.

**Hallazgo 1 — Trayectorias opuestas (Fig. 1).** Éxito viene bajando desde 2025 y
cierra en 1,28 % (agosto/2026); Olímpica arranca en cero el primer semestre y desde
abril/2025 se mueve entre 4 % y 15 %, cerrando en 4,00 %. Los seis meses en cero de
Olímpica son reales (sin ninguna nota crédito); los tres meses restantes en cero de
ambas tiendas (Éxito ene/2026; Olímpica ene y feb/2026) son un efecto de las líneas
sin cantidad y no se leen como ausencia de devolución.

![Fig. 1 · Tasa mensual de devolución por vencimiento (cajas devueltas ÷ cajas colocadas brutas). Marcador hueco: mes cuyas notas crédito vienen todas sin cantidad, no es un cero real.](figuras/fig1_tasa_mensual.png)

**Hallazgo 2 — Un episodio de sobrecolocación, no un patrón de rezago (H-08).** En
diciembre/2024 Éxito recibió 14.860 cajas (4,5 veces su mediana mensual), el 64 % en
un solo SKU (Bretaña 300 ml vidrio no retornable, 9.562 cajas); enero/2025 devolvió
239 cajas, la peor tasa de la serie (10,43 %), el 71 % en la familia Hit 1.000 ml
Tetra. El diagnóstico inicial lo generalizó como "la colocación de un mes predice la
devolución del siguiente" (r = 0,716). La prueba de robustez lo desmiente: la
correlación de Spearman es 0,03 y, sin ese par de meses, Pearson es −0,09. Se
conserva como **caso documentado** de lo que la herramienta debe evitar (acotar la
cantidad antes de que el inventario supere la vida útil), no como regla.

![Fig. 2 · Colocación bruta mensual por tienda (escalas independientes: Éxito mueve 20 veces el volumen de Olímpica). El pico de diciembre de 2024 en Éxito es un solo SKU en un 64 %.](figuras/fig2_colocacion_mensual.png)

**Hallazgo 3 — La tasa crece con la fracción de vida útil consumida entre entregas
(H-07, Fig. 10).** El diagnóstico inicial reportó que los SKU cuyo "lote cubre más
días que su vida útil" devolvían 4,7 veces más (Éxito) y 2,6 veces más (Olímpica).
La auditoría mostró que esa cobertura equivalía a 730 ÷ número de entregas, y que el
grupo "excede" era en realidad de referencias esporádicas (2–3 entregas en dos
años). Con el intervalo real entre entregas, solo un SKU por tienda supera su vida
útil. Lo que los datos sí muestran, y con más fuerza, es un **gradiente monótono**:

| Intervalo entre entregas ÷ vida útil | Tasa Éxito (SKU) | Tasa Olímpica (SKU) |
|---|---|---|
| < 5 % | 0,42 % (90) | 0,18 % (3) |
| 5 – 10 % | 4,23 % (101) | 0,14 % (16) |
| 10 – 20 % | 6,87 % (82) | 1,88 % (45) |
| 20 – 35 % | 4,88 % (37) | 2,60 % (39) |
| 35 – 50 % | 12,38 % (9) | 14,40 % (24) |
| 50 – 100 % | 7,58 % (3) | 17,14 % (13) |

Spearman entre la fracción y la tasa por SKU: +0,49 (Éxito) y +0,61 (Olímpica). Es la
formulación que pasa al modelo: la variable de control es el intervalo entre entregas
frente a la vida útil remanente, y la cantidad a pedir debe acotarse de forma continua
con ella. Esto también explica por qué Olímpica está peor: su intervalo mediano entre
entregas es de 35 días frente a 13 en Éxito, sobre vidas útiles parecidas.

![Fig. 10 · Tasa de devolución según la fracción de la vida útil que consume el intervalo entre entregas (SKU con ≥ 3 entregas). Reemplaza al corte binario del diagnóstico inicial.](figuras/fig10_gradiente_intervalo_vida_util.png)

**Hallazgo 4 — Concentración (Fig. 4).** 60 de los 238 SKU con devolución física en
Éxito (25 %) y 32 de 95 en Olímpica (34 %) explican el 80 % de las cajas devueltas. En
Éxito la familia Hit 1.000 ml Tetra concentra el 24 % de la devolución de la tienda; en
Olímpica el perfil es repartido (el primer SKU no llega al 9 %). Es la base del piloto.

![Fig. 4 · Diez SKU con mayor devolución por vencimiento en cada tienda (cajas físicas, 24 meses; escalas independientes).](figuras/fig4_pareto_sku.png)

### 5.6 Revisión de literatura

Se construyó el marco teórico definitivo para el informe final
(`documentos/Marco_teorico_nuevo.docx`, 23 referencias verificadas una a una contra
la fuente original), organizado en seis ejes alineados con los hallazgos: (1)
pronóstico de demanda intermitente — Croston (1972), Syntetos y Boylan (2005),
Teunter, Syntetos y Babai (2011), MASE de Hyndman y Koehler (2006); (2) políticas de
reabastecimiento perecedero con tope por vida útil y lote mínimo — Broekmeulen y van
Donselaar (2009, 2019), Haijema y Minner (2019), Li, Yu y Wu (2016); (3) frecuencia
de entrega y periodo de revisión — Silver, Pyke y Peterson (1998); (4) sell-out
frente a sell-in e inventario fantasma — Fildes, Ma y Kolassa (2022), Trapero y
Pedregal (2016), DeHoratius y Raman (2008), Chen (2021); (5) clasificación
multicriterio de SKU — Ramanathan (2006), Ng (2007); (6) especificidades de bebidas y
FMCG — Amorim, Günther y Almada-Lobo (2012), Ballou (2004), Chopra y Meindl (2016),
FAO (2024), Nahmias (1982), Van Donselaar et al. (2006), Hyndman y Athanasopoulos
(2021).

La literatura respalda las tres decisiones de diseño que salen del diagnóstico:
métodos para demanda intermitente evaluados con MASE; la vida útil remanente y el
lote mínimo como restricción activa (tope) de la cantidad a pedir; y el periodo de
revisión de cada tienda como parámetro estructural.

### 5.7 Priorización preliminar para el piloto

Se propone arrancar la Fase 3 con los 60 SKU críticos de Éxito y los 32 de Olímpica
(80 % de la devolución con menos de un tercio de las referencias), ordenados dentro de
cada tienda por la fracción de vida útil consumida entre entregas. La priorización
formal (con clasificación multicriterio, Ng 2007) se cierra en el mes 4 cuando se
disponga de la venta diaria para incluir la rotación real como criterio.

### 5.8 Auditoría del 15/09 y trazabilidad

Se auditó el proyecto completo (código, informes y datos). Resultados: el código se
reorganizó en un módulo común (`comun.py`) que centraliza rutas, constantes y reglas
de depuración; se agregó el análisis exploratorio y de robustez (`eda_fase1.py`); los
cuadernos se regeneran desde los scripts (`sincronizar_notebooks.py`) sin salidas,
para que ningún dato de Postobón quede en el historial; se creó el registro numerado
de hallazgos; y se corrigieron en los informes las tres afirmaciones que no
resistieron las pruebas (ceros "reales", rezago de un mes, corte binario de cobertura).

### 5.9 Universo de SKU activos (18/09, H-15)

El maestro de vidas útiles trae 1.588 SKU del centro 43, pero el modelo solo necesita
los que realmente se mueven en las dos tiendas. Se cruzó el maestro con la colocación
bruta (H-01) y con las devoluciones por vencimiento (incluidas las líneas sin cantidad,
H-03) de los 24 meses: un SKU es *activo* en una tienda si tuvo al menos una colocación
o una devolución allí (`codigo/sku_activos.py`; `datos/procesados/sku_activos.xlsx`).

| Tienda | Con colocación | Con devolución | Solo devolución | SKU activos |
|---|---|---|---|---|
| Éxito San Antonio | 340 | 244 | 6 | **346** |
| Olímpica Villanueva | 172 | 112 | 9 | **181** |
| Unión (activos en al menos una) | 352 | 270 | 13 | **365** |

Solo el 23 % del maestro está activo; 162 SKU son comunes a ambas tiendas y Olímpica
maneja cerca de la mitad del surtido de Éxito. Un único SKU con movimiento carece de
vida útil (1100 CILINDRO CO2, en Éxito), que no es una bebida y se excluye del alcance
BNA salvo indicación contraria de la asesora externa. Los 13 SKU con devolución sin
colocación bruta son referencias descontinuadas o con colocación anterior a la ventana
(6 aparecen en la colocación solo con filas negativas o en cero; 2 de Olímpica se
colocaron en Éxito) y pesan 1,1 % y 1,2 % de la devolución, así que no alteran el
indicador. Este universo de 346 y 181 SKU es la base de la clasificación de la demanda,
de la priorización de SKU críticos (§5.7) y del cálculo de la cantidad a pedir.

---

## 6. Estado frente a los objetivos específicos

| Objetivo específico | Estado al 18/09/2026 |
|---|---|
| OE1. Diagnosticar el estado actual de las devoluciones y el comportamiento histórico de ventas | **Cumplido en lo que permiten los datos**: devoluciones diagnosticadas y priorizadas; el comportamiento de ventas se aproximó con la colocación porque la venta diaria no se ha entregado |
| OE2. Diseñar un modelo estadístico de pronóstico y stock mínimo que integre rotación real y vida útil | Por iniciar (mes 4). Ya definidos: clase de método por SKU (ADI–CV²), forma del tope por vida útil, periodo de revisión por tienda |
| OE3. Validar la herramienta mediante simulación y prueba piloto | Programado para los meses 5 y 6; piloto preliminar identificado (60 + 32 SKU) |

---

## 7. Entregables producidos hasta la fecha

| Entregable | Ubicación |
|---|---|
| Código reproducible del diagnóstico y de la exploración (scripts y cuadernos) | `codigo/analisis_diagnostico_fase1.py`, `codigo/eda_fase1.py`, `codigo/sku_activos.py`, `codigo/comun.py` |
| Consultas DAX documentadas para extraer devoluciones del GA05 | `codigo/analisis_diagnostico_fase1.py` §2 y §5.1 |
| Tablas de resultados (indicador, por SKU, mensual, calidad, robustez, intermitencia, correlaciones, SKU activos) | `datos/procesados/*.csv` (29 tablas) y `sku_activos.xlsx` |
| Figuras 1 a 14 | `figuras/` |
| Este informe en Word, con las figuras embebidas | `informes/Informe_avance_01.docx` (generado con `codigo/generar_informe_docx.py`) |
| Resumen metodológico del diagnóstico (corregido el 15/09) | `informes/Resumen_diagnostico_Fase1.md` |
| Informe visual del diagnóstico | `informes/Informe_diagnostico_Fase1.html` |
| Registro de hallazgos H-01 a H-15 | `informes/Registro_hallazgos.md` |
| Marco teórico verificado (23 referencias) | `documentos/Marco_teorico_nuevo.docx` |
| Borrador del informe final con la estructura de la plantilla U. de A. | `informes/Informe_final_borrador.md` |
| Bitácora de avances y repositorio git local (sin datos de la empresa) | `bitacora_avances.md`, `.git` |

---

## 8. Dificultades, decisiones y lecciones

1. **Dependencia de datos externos.** El mes 2 se perdió por la entrega tardía; al
   18/09 la venta diaria sigue pendiente. Decisión: no esperar; el diagnóstico se hizo
   con colocación como proxy de rotación, declarando el supuesto, y se dejó escrito el
   plan exacto para integrar la venta cuando llegue (`PENDIENTE_ventas_diarias.md`).
2. **Los extractos no se pueden usar tal como llegan.** La colocación venía neta de
   devoluciones (H-01) y el GA05 trae un tercio de líneas sin cantidad (H-03). Lección:
   validar cada extracto contra una fuente independiente *antes* de calcular, y dejar
   la validación en código.
3. **Los hallazgos propios también hay que auditarlos.** Dos de los cuatro hallazgos
   del primer diagnóstico no resistieron pruebas de robustez sencillas (correlación de
   rangos, redefinición de una variable). Se corrigieron en menos de dos semanas y
   antes de llegar a un informe evaluado. Lección: toda cifra que va a un informe pasa
   por una prueba de sensibilidad y queda registrada con su código H-nn.
4. **Cambios operativos en medio de la serie.** El cambio de centro (H-05) y las
   entregas fuera de calendario en Olímpica (H-06) no estaban en ninguna
   documentación entregada; salieron de los datos. Ambos van a la agenda con la asesora
   externa.

---

## 9. Próximos pasos (mes 4: 22/09 – 21/10)

1. Agenda con la asesora externa: (a) origen de las notas crédito sin cantidad (H-03);
   (b) fecha contable del GA05 (H-02); (c) vida útil del centro 79 (H-05); (d) entregas
   de Olímpica fuera de miércoles/sábado (H-06); (e) fecha de entrega de la venta
   diaria e inventario en tienda (H-13).
2. Con Power BI Desktop abierto, re-ejecutar la consulta DAX y correr
   `eda_fase1.py` §2 para cerrar formalmente la verificación de la exportación.
3. Al recibir la venta diaria: ejecutar el plan de `PENDIENTE_ventas_diarias.md`
   (calidad, reconciliación sell-in/sell-out, intermitencia con ventas, reconstrucción
   de inventario) y cerrar la priorización del piloto.
4. Iniciar la Fase 2: implementar en Python el pronóstico por clase de SKU (SES /
   SBA / TSB), evaluado con MASE, y la fórmula de cantidad a pedir con tope por vida
   útil remanente y periodo de revisión por tienda.

---

## Anexo A — Figuras

| Figura | Contenido | Script |
|---|---|---|
| Fig. 1 | Tasa mensual de devolución por vencimiento, con marca de meses afectados por H-03 | diagnóstico §7 |
| Fig. 2 | Colocación bruta mensual por tienda | diagnóstico §8 |
| Fig. 3 | Tasa por corte binario cobertura/vida útil (se conserva por trazabilidad; reemplazada por la Fig. 10) | diagnóstico §9 |
| Fig. 4 | Diez SKU con mayor devolución por tienda | diagnóstico §10 |
| Fig. 5 | Líneas de nota crédito con y sin cantidad por mes (H-03) | EDA §2.4 |
| Fig. 6 | Calendario real de entregas frente al maestro (H-06) | EDA §3.3 |
| Fig. 7 | Serie semanal de devoluciones físicas | EDA §4.2 |
| Fig. 8 | Clasificación ADI–CV² por SKU (H-12) | EDA §5 |
| Fig. 9 | Vida útil del portafolio colocado, ponderada por cajas | EDA §7 |
| Fig. 10 | Tasa de devolución según la fracción de vida útil consumida entre entregas (H-07) | EDA §6.1 |
| Fig. 11 | Diagramas de caja de las variables por SKU, tienda contra tienda | EDA §6.3 |
| Fig. 12 | Histogramas de las variables por SKU | EDA §6.3 |
| Fig. 13 | Matriz de correlación de Spearman entre variables por SKU | EDA §6.3 |
| Fig. 14 | Dispersión de la tasa de devolución frente a intervalo, vida útil y lote | EDA §6.3 |

La Fig. 3 (corte binario cobertura/vida útil, versión del 03/09) se conserva solo
por trazabilidad:

![Fig. 3 · Tasa por corte binario "cobertura ≤ / > vida útil" del diagnóstico inicial. Su definición de cobertura (730 ÷ entregas) agrupaba SKU esporádicos; reemplazada por la Fig. 10 (H-07).](figuras/fig3_cobertura_vida_util.png)

## Anexo B — Reproducción

```bash
python codigo/analisis_diagnostico_fase1.py   # indicador, hallazgos, figuras 1–4
python codigo/eda_fase1.py                    # calidad, exploración, robustez, figuras 5–14
python codigo/sku_activos.py                  # universo de SKU activos por tienda (H-15)
python codigo/sincronizar_notebooks.py        # regenera los .ipynb desde los .py
python codigo/generar_informe_docx.py informes/Informe_avance_01.md   # versión Word con figuras
```

Requiere `pandas`, `numpy`, `matplotlib` y `openpyxl`. Los datos de Postobón viven
en `datos/crudos/` y no se versionan.
