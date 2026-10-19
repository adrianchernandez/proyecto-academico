# Informe final de práctica — BORRADOR EN CONSTRUCCIÓN

> Estructura tomada de la plantilla oficial
> `documentos/Plantilla_UdeA_APA7_2025_v.2_Semestre-de-Industria.docx`
> (Resumen, Abstract, 1. Introducción, 2. Objetivos, 3. Marco teórico,
> 4. Metodología, 5. Análisis de resultados, 6. Conclusiones y recomendaciones,
> Referencias, Anexos). Las secciones marcadas **[PENDIENTE — Fase n]** se
> escriben cuando esa fase cierre. Lo demás ya está sustentado en código y datos.
> Citación APA 7 (compatible con NTC 5613); verificar con la asesora interna si el
> cuerpo exige IEEE. Última actualización: 16/09/2026.

---

**Título:** Construcción de una herramienta estadística de reabastecimiento que permita reducir las devoluciones por productos vencidos en los puntos de venta de canal moderno: una herramienta para la planeación del stock mínimo.
**Tipo de documento:** Informe de práctica presentado como requisito para optar al título de Ingeniero Industrial.
**Autor:** Adrian Camilo Hernández Copete.
**Asesora interna:** Olga Cecilia Usuga Manco. **Asesora externa:** Kellys Johana Otero Palacio.
**Universidad de Antioquia, Facultad de Ingeniería, Departamento de Ingeniería Industrial. Medellín, 2026.**

---

## Resumen

Este trabajo diseña una herramienta estadística que calcula la cantidad a pedir por
referencia (SKU) y punto de venta en cada ciclo de reabastecimiento, integrando el
pronóstico de demanda, la rotación real y la vida útil remanente del producto, con
el fin de reducir las devoluciones por vencimiento en dos puntos de venta del canal
moderno de Postobón S.A. (Éxito San Antonio y Olímpica Villanueva), categoría
bebidas no alcohólicas. Con 24 meses de colocación y notas crédito (septiembre/2024
– agosto/2026) se cuantificó una tasa de devolución por vencimiento de 1,55 % en
Éxito y 3,97 % en Olímpica, y se identificó que la tasa crece de forma continua con
la fracción de la vida útil que consume el intervalo entre entregas. **[PENDIENTE —
Fase 2/3: método de pronóstico elegido, fórmula de cantidad a pedir, resultado de
la simulación frente a la política tradicional.]**

**Palabras clave:** devoluciones, productos vencidos, stock mínimo, demanda
intermitente, vida útil, reabastecimiento, canal moderno.

## Abstract

**[PENDIENTE — traducción del resumen al cierre.]**

**Keywords:** returns, expired products, minimum stock, intermittent demand, shelf
life, replenishment, modern trade.

---

## 1. Introducción

### 1.1 Contexto

Postobón S.A. produce y distribuye bebidas y atiende el canal moderno (grandes
cadenas de supermercados) desde el área de Desarrollo Logístico en Medellín. En ese
canal, mantener alta disponibilidad en góndola induce sobrestock, y el sobrestock de
un producto con vida útil finita termina en devolución por vencimiento: producto que
regresa a la compañía como nota crédito, con pérdida del costo industrial, costos de
logística de reversa y afectación del margen.

### 1.2 Problema

Los parámetros de reabastecimiento vigentes no incorporan la vida útil del producto
ni la rotación real de cada tienda: el mismo criterio de pedido se aplica a
referencias de 49 días de vida útil y a referencias de 360, y a tiendas que reciben
seis veces por semana y a tiendas que reciben dos. El diagnóstico de este trabajo
(sección 5.1) muestra que la devolución por vencimiento es el primer motivo de
devolución en los dos puntos de venta estudiados y que su tasa depende de forma
continua de cuánta vida útil consume el producto entre una entrega y la siguiente.

### 1.3 Alcance

Dos puntos de venta (Ex 039 Éxito San Antonio y St 341 Olímpica Villanueva, regional
Antioquia) y la categoría bebidas no alcohólicas (clasificaciones BNA y Mundo Cero).
Ventana de datos: 01/09/2024 – 31/08/2026. La herramienta se construye en Python con
código replicable; Excel y Power BI se usan solo para exploración y presentación.

### 1.4 Estructura del documento

**[PENDIENTE — párrafo de cierre cuando el documento esté completo.]**

---

## 2. Objetivos

### 2.1 Objetivo general

Desarrollar una herramienta estadística de reabastecimiento basada en la
optimización del stock mínimo para reducir las devoluciones por caducidad en los
puntos de venta del canal moderno.

### 2.2 Objetivos específicos

1. Diagnosticar el estado actual de las devoluciones y el comportamiento histórico de
   las ventas de los productos en los puntos de venta.
2. Diseñar un modelo estadístico de pronóstico y stock mínimo que integre la tasa de
   rotación real con la variable de vida útil del producto.
3. Validar la efectividad de la herramienta a través de una simulación de escenarios
   lógicos y pruebas piloto frente a los parámetros de reabastecimiento tradicionales.

---

## 3. Marco teórico

> Texto completo y verificado en `documentos/Marco_teorico_nuevo.docx` (23
> referencias). Aquí va el resumen de los seis ejes y su vínculo con el proyecto; al
> armar el .docx final se pega el texto completo.

### 3.1 Pronóstico de demanda intermitente en retail

Las series de venta a nivel de SKU y tienda tienen muchos periodos en cero; la
suavización exponencial simple promedia los ceros y sesga el inventario (Hyndman y
Athanasopoulos, 2021). Croston (1972) separa tamaño e intervalo de la demanda;
Syntetos y Boylan (2005) corrigen su sesgo (SBA); Teunter, Syntetos y Babai (2011)
actualizan la probabilidad de demanda en todos los periodos (TSB), lo que detecta
obsolescencia. La clasificación ADI–CV² (Syntetos, Boylan y Croston, 2005) decide qué
método usar y el MASE (Hyndman y Koehler, 2006) permite compararlos cuando hay ceros.
*Vínculo:* el 83 % y 87 % de los SKU de las dos tiendas son intermitentes o
abultados (sección 5.1.4).

### 3.2 Reabastecimiento de perecederos con lote mínimo y tope por vida útil

Nahmias (1982) sistematiza la teoría de inventarios perecederos; Broekmeulen y van
Donselaar (2009, 2019) muestran que cuando el lote mínimo cubre más días que la vida
útil remanente el desperdicio es inevitable; Haijema y Minner (2019) y Li, Yu y Wu
(2016) proponen políticas dependientes de la edad del inventario, con la demanda
esperada dentro de la vida útil residual como tope de la cantidad a pedir.
*Vínculo:* gradiente de la tasa con la fracción de vida útil consumida entre
entregas (sección 5.1.5).

### 3.3 Frecuencia de entrega y periodo de revisión

En revisión periódica el inventario debe cubrir lead time más periodo de revisión
(Silver, Pyke y Peterson, 1998); ciclos largos con lotes mínimos precipitan la merma
en vida corta (Broekmeulen y van Donselaar, 2009). *Vínculo:* Éxito recibe 5,1 veces
por semana y Olímpica 1,9; intervalo mediano entre entregas por SKU de 13 y 35 días.

### 3.4 Sell-out frente a sell-in e inventario fantasma

Fildes, Ma y Kolassa (2022) y Trapero y Pedregal (2016) muestran que el sell-in
amplifica la varianza (efecto látigo) y que el POS es la base del pronóstico;
DeHoratius y Raman (2008) y Chen (2021) documentan la inexactitud de registros y el
inventario fantasma. *Vínculo:* el diagnóstico usó colocación como proxy; la venta
diaria está pendiente (H-13).

### 3.5 Clasificación multicriterio de referencias

Ramanathan (2006) y Ng (2007) reemplazan el ABC unidimensional por puntajes que
combinan volumen, vida útil, lote e intermitencia. *Vínculo:* selección del piloto.

### 3.6 Especificidades de bebidas y consumo masivo

Amorim, Günther y Almada-Lobo (2012) sobre acuerdos de vida útil mínima a la
entrega; Ballou (2004), Chopra y Meindl (2016) sobre visibilidad en canales
multipunto; FAO (2024) y Van Donselaar et al. (2006) sobre la magnitud de las
pérdidas en retail.

---

## 4. Metodología

### 4.1 Enfoque y fases

Enfoque cuantitativo aplicado, con un componente cualitativo (contraste con el
personal de planeación de pedidos). Cinco fases: 0 contextualización, 1 diagnóstico,
2 diseño del modelo, 3 validación por simulación y piloto, 4 documentación. El
cronograma real se corrió un mes respecto a la propuesta por la entrega tardía de
datos (informe de avance N.º 1, sección 2.2).

### 4.2 Fuentes de datos

| Fuente | Contenido | Uso |
|---|---|---|
| Colocación (SAP) | Cajas físicas entregadas por fecha, centro, cadena y SKU | Denominador de la tasa; proxy de rotación mientras no hay venta |
| GA05-Notas Crédito (Power BI, consulta DAX) | Notas crédito por fecha, tienda, SKU, tipo y motivo | Numerador (motivo "Fecha De Vencimiento", tipo "Devolución") |
| Maestro de vidas útiles (centro 43) | Días de vida útil por SKU (1.588 SKU, de los cuales 365 están activos en las dos tiendas, H-15) | Restricción del modelo |
| Maestro de puntos de venta | Días de pedido y entrega por tienda | Periodo de revisión |
| Venta diaria (sell-out) | **[PENDIENTE — H-13]** | Calibración del pronóstico y de la rotación real |

### 4.3 Verificación y depuración

Reglas aplicadas en `codigo/comun.py` y documentadas como hallazgos H-01 a H-11 en
`informes/Registro_hallazgos.md`: colocación bruta como denominador (el extracto
venía neto de notas crédito); caja física como unidad; fecha de transacción del
GA05; líneas de nota crédito sin cantidad marcadas y reportadas aparte; exclusión de
filas en cero; tratamiento del truncamiento por la izquierda. La exportación del GA05
se verificó por consistencia entre dos consultas independientes.

### 4.4 Indicadores y métodos de análisis

- Tasa de devolución por vencimiento = cajas devueltas por vencimiento ÷ cajas
  colocadas brutas, por tienda y periodo.
- Intervalo entre entregas por SKU y tienda = (última − primera entrega) ÷ (entregas
  − 1), y su fracción sobre la vida útil.
- Clasificación ADI–CV² sobre series semanales (Syntetos, Boylan y Croston, 2005).
- Pruebas de robustez: correlación de rangos, exclusión de extremos, redefinición de
  variables.
- Métodos de pronóstico por clase de demanda, métrica de validación y fórmula de
  cantidad a pedir: sección 4.5.
- **[PENDIENTE — Fase 3: diseño de la simulación (política propuesta vs.
  tradicional), métricas: cajas vencidas evitadas, quiebres inducidos, nivel de
  servicio, valor.]**

### 4.5 Modelo de pronóstico de demanda y cantidad a pedir (Fase 2)

El modelo se diseñó en dos etapas encadenadas, de modo que el pronóstico de demanda
sea un insumo y la salida final sea un único número por SKU y tienda en cada ciclo de
reabastecimiento: la cantidad a pedir. La implementación está en
`codigo/modelo_stock_minimo.py` y carga los datos únicamente a través de
`codigo/comun.py`, de manera que hereda las reglas de depuración de la sección 4.3.

#### 4.5.1 Estado de la información al momento del diseño

La venta diaria al consumidor y el inventario en tienda no habían sido entregados
al momento de diseñar el modelo (H-13). Por eso el diseño distingue de forma
explícita tres tipos de insumo:

| Insumo | Fuente | Estado |
|---|---|---|
| Periodo de revisión por tienda (*R*) | Calendario de entregas del maestro comercial | Real, fijado |
| Lead time por tienda (*L*) | Diferencia entre fecha de pedido y de entrega en colocación | Real, fijado |
| Vida útil por SKU | Maestro de vidas útiles (centro 43) | Real, fijado |
| Tasa y variabilidad de la demanda | Venta diaria | **Pendiente**: mientras tanto, colocación semanal como proxy |
| Inventario proyectado y vida útil remanente | Inventario en tienda | **Pendiente**: supuestos declarados en 4.5.5 |

La arquitectura, las funciones y la tubería de cálculo se construyeron y probaron de
punta a punta con el proxy, con la misma lógica con la que el diagnóstico clasificó la
intermitencia (sección 5.1.4). Ninguna cifra producida con el proxy se reporta como
resultado del modelo: al recibir la venta diaria se reemplaza el insumo y se
recalcula todo (`PENDIENTE_ventas_diarias.md`). Esta separación se adoptó porque el
sell-in amplifica la varianza de la demanda real (Trapero y Pedregal, 2016) y el
punto de venta es la base correcta del pronóstico en retail (Fildes, Ma y Kolassa,
2022): un modelo calibrado sobre colocación heredaría ruido logístico que la venta
al consumidor no tiene.

#### 4.5.2 Clasificación de la demanda por SKU y tienda

Cada serie semanal por SKU y tienda se construye completa, con ceros en las semanas
sin demanda dentro de la ventana activa del SKU (de su primera a su última semana con
demanda), porque los métodos de demanda intermitente necesitan observar los huecos.
Sobre esa serie se calculan los dos estadísticos de Syntetos, Boylan y Croston (2005):

- **ADI** (intervalo medio entre demandas) = semanas activas ÷ semanas con demanda
  positiva.
- **CV²** = (desviación estándar ÷ media)² del tamaño de la demanda en las semanas en
  que ocurre.

Con los umbrales ADI = 1,32 y CV² = 0,49 resultan cuatro clases, y cada una recibe un
método de pronóstico distinto:

| Clase | ADI | CV² | Método | Justificación |
|---|---|---|---|---|
| Suave | ≤ 1,32 | ≤ 0,49 | SES | Demanda frecuente y de tamaño estable; basta suavizar el nivel. |
| Errática | ≤ 1,32 | > 0,49 | SBA | Frecuente pero de tamaño muy variable; separar tamaño y frecuencia estabiliza la estimación. |
| Intermitente | > 1,32 | ≤ 0,49 | SBA | Huecos largos con tamaño estable; Croston sesga al alza y SBA lo corrige. |
| Abultada | > 1,32 | > 0,49 | TSB | Huecos largos y tamaño errático; mayor riesgo de descontinuación, TSB decae hacia cero. |

Los SKU con una sola semana de demanda no admiten CV² y se tratan con SES por
defecto; en la práctica son referencias esporádicas que la clasificación multicriterio
del piloto (sección 3.5) dejará fuera.

#### 4.5.3 Métodos de pronóstico

Todos los métodos producen, para cada semana *t*, una estimación de la **tasa de
demanda por periodo** (cajas físicas por semana), ya suavizada; el pronóstico hacia
adelante es plano: se sostiene el último valor estimado. En este primer diseño no se
incluyen tendencia ni estacionalidad, decisión que se revisará con la venta real si
el backtest lo justifica (Hyndman y Athanasopoulos, 2021).

- **Suavización exponencial simple (SES):** *f*ₜ = α·*y*ₜ₋₁ +
  (1 − α)·*f*ₜ₋₁. Con series con muchos ceros el SES promedia los ceros
  y sesga el nivel de inventario; por eso se reserva a la clase suave.
- **Croston (1972):** suaviza por separado el tamaño de la demanda cuando ocurre
  (*z*ₜ) y el intervalo entre demandas (*x*ₜ), actualizando
  ambos solo en los periodos con demanda, y pronostica el cociente *z*ₜ ÷
  *x*ₜ.
- **SBA (Syntetos y Boylan, 2005):** corrige el sesgo positivo de Croston
  multiplicando su pronóstico por (1 − α/2). Es el método base para las clases
  errática e intermitente.
- **TSB (Teunter, Syntetos y Babai, 2011):** suaviza en cada periodo la
  *probabilidad* de que haya demanda (*p*ₜ) y, solo cuando la hay, su
  tamaño (*z*ₜ); el pronóstico es *p*ₜ·*z*ₜ. Al
  actualizar la probabilidad también en los periodos en cero, el pronóstico decae
  cuando un SKU deja de rotar, que es exactamente el SKU con mayor riesgo de
  vencimiento. Por eso se asigna a la clase abultada.

Las constantes de suavización parten de α = 0,2 para SES y α = 0,1 para Croston, SBA
y TSB (valores usuales en la literatura de demanda intermitente) y se calibrarán con
la venta real minimizando el MASE en la ventana de prueba.

#### 4.5.4 Validación del pronóstico

Para cada SKU con al menos 16 semanas activas se reservan las últimas 8 semanas como
ventana de prueba. El método asignado se ajusta con las semanas anteriores y su
último valor se sostiene plano sobre la prueba. La precisión se mide con el **MASE**
(Hyndman y Koehler, 2006): error absoluto medio del método dividido entre el error
absoluto medio del pronóstico ingenuo (repetir la semana anterior) en el
entrenamiento. Se eligió el MASE porque es la única métrica de la familia que se
mantiene definida con ceros en la serie (el MAPE no) y porque es comparable entre
SKU de distinta escala. Un MASE menor que 1 indica que el método le gana al ingenuo.
Los resultados se reportan por tienda y por clase, y una clase cuyo método no supere
al ingenuo con venta real obliga a revisar su asignación antes de la simulación.

#### 4.5.5 Cantidad a pedir por ciclo

La decisión de pedido sigue un modelo de **revisión periódica (R, S)** (Silver, Pyke
y Peterson, 1998): en cada revisión se pide lo que falta para llegar a un nivel
objetivo *S* que cubra la demanda durante el periodo de revisión más el lead time,
con un colchón de seguridad proporcional a la variabilidad de la demanda. Sobre ese
modelo se añade la restricción que distingue a un perecedero de un producto
durable: el nivel objetivo nunca puede exceder lo que la vida útil remanente permite
vender (Nahmias, 1982; Haijema y Minner, 2019; Li, Yu y Wu, 2016). Con *d̄* la tasa
de demanda pronosticada (cajas/semana), *σ* su desviación estándar semanal, *R* y *L*
en días y *V* la vida útil remanente en días:

```
demanda_ciclo   = d̄ · (R + L) / 7
colchon         = z · σ · √((R + L) / 7)
nivel_objetivo  = demanda_ciclo + colchon              (S clásico)
tope_vida_util  = d̄ · V / 7
Q = max(0, min(nivel_objetivo, tope_vida_util) − inventario_proyectado)
```

El `min` entre el nivel objetivo y el tope es la pieza que equilibra las dos fuerzas
opuestas del problema: el nivel de servicio (*z*) empuja la cantidad hacia arriba
para evitar quiebre, y el tope de vida útil la frena para evitar vencimiento. Cuando
el tope es el que manda, el pedido queda por debajo del nivel de servicio nominal:
ese es un resultado deseado, no una falla, porque pedir más solo convertiría el
faltante en devolución (Broekmeulen y van Donselaar, 2009, 2019).

Parámetros y supuestos:

- **Periodo de revisión (*R*):** 7 ÷ días de entrega por semana del maestro
  comercial: 1,2 días en Éxito (6 días de entrega) y 3,5 días en Olímpica (2 días,
  H-06). Es la diferencia estructural entre tiendas que el diagnóstico identificó
  como mecanismo del vencimiento (sección 5.1.5).
- **Lead time (*L*):** mediana observada entre fecha de pedido y de entrega en
  colocación, 2 días en ambas tiendas.
- **Variabilidad (*σ*):** desviación estándar de la serie semanal completa,
  incluidos los ceros, porque es la variabilidad periodo a periodo la que determina
  el colchón; el CV² solo describe el tamaño cuando hay demanda.
- **Nivel de servicio (*z*):** 1,28 (≈ 90 %) como punto de partida del piloto. Se
  calibrará en la Fase 3 comparando cajas vencidas y quiebres bajo distintos valores.
- **Inventario proyectado:** mientras no exista inventario en tienda se asume 0, lo
  que sesga la cantidad al alza. Con el inventario reconstruido (saldo = saldo
  anterior + colocación − venta − devolución) se restará el saldo esperado al
  momento de la entrega.
- **Vida útil remanente (*V*):** mientras no haya inventario por lotes se usa la
  vida útil total del SKU, también un sesgo al alza. Con inventario se asignará edad
  FIFO a las entregas para estimar la vida útil que le queda al lote que se venderá
  primero (Haijema y Minner, 2019).
- **Redondeo a lote:** la cantidad se redondeará al múltiplo de la unidad mínima de
  pedido de cada cadena cuando se confirme ese dato con la asesora externa.

#### 4.5.6 Salida del modelo

Por cada ciclo de revisión el modelo entrega una tabla con una fila por SKU y tienda:
`PDV, SKU, cantidad_a_pedir`, acompañada de las columnas de sustento (clase de
demanda, pronóstico semanal, demanda del ciclo, colchón, nivel objetivo, tope de
vida útil, indicador de si el tope fue el activo e inventario proyectado). Ese número
es el entregable del proyecto; el resto son insumos para explicarlo.

### 4.6 Herramientas

Python 3.12 (pandas, numpy, matplotlib), cuadernos regenerados desde los scripts,
control de versiones con git (los datos de la empresa no se versionan).

---

## 5. Análisis de resultados

### 5.1 Fase 1 — Diagnóstico

#### 5.1.1 Datos y calidad
Resumen de la sección 5.1–5.3 del informe de avance N.º 1: cuatro fuentes, 24 meses,
hallazgos H-01 a H-11. Destacan la colocación neta de notas crédito (H-01), las
líneas sin cantidad del GA05 (H-03), el cambio de centro abastecedor en junio/2025
(H-05) y las entregas de Olímpica fuera del calendario del maestro (H-06).

**Universo de SKU activos (H-15).** Del maestro de vidas útiles (1.588 SKU del centro
43) solo el 23 % se mueve en los dos puntos de venta: un SKU es activo si tuvo al menos
una colocación bruta o una devolución por vencimiento en la tienda durante la ventana.

| Tienda | Con colocación | Con devolución | Solo devolución | SKU activos |
|---|---|---|---|---|
| Éxito San Antonio | 340 | 244 | 6 | **346** |
| Olímpica Villanueva | 172 | 112 | 9 | **181** |
| Unión (activos en al menos una) | 352 | 270 | 13 | **365** |

162 SKU son comunes a ambas tiendas; Olímpica maneja cerca de la mitad del surtido de
Éxito. Un solo SKU con movimiento carece de vida útil (1100 CILINDRO CO2, Éxito), que
no es una bebida y se excluye del alcance BNA **[PENDIENTE — confirmar con la asesora
externa, E-8]**. Los 13 SKU con devolución sin colocación son referencias descontinuadas
o con colocación anterior a la ventana (pesan 1,1 % y 1,2 % de la devolución). Este
universo (`datos/procesados/sku_activos.csv`) es el que alimenta la clasificación de la
demanda (§4.5.2), la priorización de SKU críticos y la cantidad a pedir (§4.5.5).

#### 5.1.2 Indicador principal
Éxito San Antonio: 1.401,3 cajas devueltas por vencimiento sobre 90.635,7 colocadas,
**1,55 %**. Olímpica Villanueva: 174,7 sobre 4.406,3, **3,97 %**. Cota superior si las
líneas sin cantidad fueran físicas: 2,12 % y 12,44 %. El vencimiento es el 61 % y 62 %
de todo lo devuelto. (Fig. 1; tabla `resumen_cifras_diagnostico.csv`.)

#### 5.1.3 Estructura de reposición de cada tienda
Éxito: 5,1 entregas por semana, lote mediano 2 cajas, 100 % dentro del calendario.
Olímpica: 1,9 entregas por semana, lote mediano 1 caja, 21 % de su colocación fuera de
los días del maestro. Lead time 1–3 días en ambas. (Fig. 6; `eda_colocacion_*.csv`.)

#### 5.1.4 Intermitencia de la demanda
83 % (Éxito) y 87 % (Olímpica) de los SKU con ADI > 1,32 sobre colocación semanal;
Olímpica no tiene ningún SKU "suave". (Fig. 8; `eda_intermitencia_*.csv`.) Se
recalcula con venta diaria.

#### 5.1.5 Mecanismo: fracción de vida útil consumida entre entregas
La tasa crece de forma monótona con intervalo ÷ vida útil: Éxito de 0,42 % (< 5 %) a
12,4 % (35–50 %); Olímpica de 0,18 % a 17,1 % (50–100 %). Spearman +0,49 y +0,61.
(Fig. 10; `robustez_cobertura_gradiente.csv`.) El episodio de diciembre/2024 en Éxito
(14.860 cajas, 4,5 veces la mediana; 10,43 % de devolución en enero) ilustra el
mecanismo, pero no constituye un patrón de rezago mensual (H-08).

#### 5.1.6 Concentración y piloto
60 de 238 SKU (Éxito) y 32 de 95 (Olímpica) explican el 80 % de la devolución. (Fig. 4;
`analisis_por_sku.csv`.)

### 5.2 Fase 2 — Diseño del modelo
**[PENDIENTE — Fase 2.]** La arquitectura del modelo (clasificación, métodos,
validación y fórmula de cantidad a pedir) está descrita en la sección 4.5 y
codificada en `codigo/modelo_stock_minimo.py`, probada de punta a punta con
colocación como proxy; los resultados de esta sección se producirán con la venta
diaria. Contenido previsto: reconciliación sell-in/sell-out;
clasificación definitiva ADI–CV² con ventas; pronóstico por clase y su MASE en
ventana de prueba; fórmula de stock mínimo y cantidad a pedir con tope por vida útil
remanente, lote mínimo y periodo de revisión por tienda; tabla de salida por ciclo
(`PDV, SKU, cantidad_a_pedir`).

### 5.3 Fase 3 — Validación
**[PENDIENTE — Fase 3.]** Contenido previsto: simulación retrospectiva sobre la
ventana de prueba comparando la política propuesta con los parámetros tradicionales
(cajas vencidas, quiebres, nivel de servicio, valor); prueba piloto en los SKU
priorizados; análisis de sensibilidad a los supuestos (inventario inicial, vida útil
del centro 79, tratamiento de las líneas sin cantidad).

---

## 6. Conclusiones y recomendaciones

**Parciales (Fase 1):**

1. En los dos puntos de venta la devolución por vencimiento es el primer motivo de
   devolución y su tasa está determinada por la relación entre el intervalo de
   reposición y la vida útil del producto, no por la vida útil sola ni por el volumen.
2. La demanda a nivel de SKU y tienda es intermitente en la gran mayoría de las
   referencias; el pronóstico debe usar métodos para demanda intermitente.
3. Las dos tiendas necesitan parámetros distintos: mismo SKU, distinto intervalo de
   entrega, distinta cantidad a pedir.
4. La calidad de los extractos exige validación previa: dos de los cuatro insumos
   traían distorsiones que habrían cambiado las conclusiones.

**[PENDIENTE — Fases 2 y 3: conclusiones sobre el desempeño del modelo,
recomendaciones de implementación en la planeación de pedidos, replicabilidad a otros
centros.]**

---

## Referencias

Amorim, P., Günther, H. O., & Almada-Lobo, B. (2012). Multi-objective integrated production and distribution planning of perishable products. *International Journal of Production Economics, 138*(1), 89-101. https://doi.org/10.1016/j.ijpe.2012.03.005

Ballou, R. H. (2004). *Logística: Administración de la cadena de suministro* (5.ª ed.). Pearson Educación.

Broekmeulen, R. A. C. M., & Van Donselaar, K. H. (2009). A heuristic to manage perishable inventory with batch ordering, positive lead-times, and time-varying demand. *Computers & Operations Research, 36*(11), 3013-3018. https://doi.org/10.1016/j.cor.2009.01.017

Broekmeulen, R. A. C. M., & van Donselaar, K. H. (2019). Quantifying the potential to improve on food waste, freshness and sales for perishables in supermarkets. *International Journal of Production Economics, 209*, 265-273. https://doi.org/10.1016/j.ijpe.2017.10.003

Chen, L. (2021). Fixing phantom stockouts: Optimal data-driven shelf inspection policies. *Production and Operations Management, 30*(3), 689-702. https://doi.org/10.1111/poms.13291

Chopra, S., & Meindl, P. (2016). *Supply chain management: Strategy, planning, and operation* (6.ª ed.). Pearson Education.

Croston, J. D. (1972). Forecasting and stock control for intermittent demands. *Operational Research Quarterly, 23*(3), 289-303. https://doi.org/10.2307/3007885

DeHoratius, N., & Raman, A. (2008). Inventory record inaccuracy: An empirical analysis. *Management Science, 54*(4), 627-641. https://doi.org/10.1287/mnsc.1070.0789

Fildes, R., Ma, S., & Kolassa, S. (2022). Retail forecasting: Research and practice. *International Journal of Forecasting, 38*(4), 1283-1318. https://doi.org/10.1016/j.ijforecast.2019.06.004

Food and Agriculture Organization of the United Nations [FAO]. (2024). *Food loss and waste database*. https://www.fao.org/policy-support/policy-themes/food-loss-and-food-waste/-Food-Loss-and-Food-Waste-Database/en

Haijema, R., & Minner, S. (2019). Improved ordering of perishables: The value of stock-age information. *International Journal of Production Economics, 209*, 316-324. https://doi.org/10.1016/j.ijpe.2016.04.021

Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3.ª ed.). OTexts.

Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting, 22*(4), 679-688. https://doi.org/10.1016/j.ijforecast.2006.03.001

Li, Q., Yu, P., & Wu, X. (2016). Managing perishable inventories in retailing: Replenishment, clearance sales, and segregation. *Operations Research, 64*(6), 1270-1284. https://doi.org/10.1287/opre.2016.1523

Nahmias, S. (1982). Perishable inventory theory: A review. *Operations Research, 30*(4), 680-708. https://doi.org/10.1287/opre.30.4.680

Ng, W. L. (2007). A simple classifier for multiple criteria ABC analysis. *European Journal of Operational Research, 177*(1), 344-353. https://doi.org/10.1016/j.ejor.2005.11.018

Ramanathan, R. (2006). ABC inventory classification with multiple-criteria using weighted linear optimization. *Computers & Operations Research, 33*(3), 695-700. https://doi.org/10.1016/j.cor.2004.07.014

Silver, E. A., Pyke, D. F., & Peterson, R. (1998). *Inventory management and production planning and scheduling* (3.ª ed.). John Wiley & Sons.

Syntetos, A. A., & Boylan, J. E. (2005). The accuracy of intermittent demand estimates. *International Journal of Forecasting, 21*(2), 303-314. https://doi.org/10.1016/j.ijforecast.2004.10.001

Syntetos, A. A., Boylan, J. E., & Croston, J. D. (2005). On the categorization of demand patterns. *Journal of the Operational Research Society, 56*(5), 495-503. https://doi.org/10.1057/palgrave.jors.2601841

Teunter, R. H., Syntetos, A. A., & Babai, M. Z. (2011). Intermittent demand: Linking forecasting to inventory obsolescence. *European Journal of Operational Research, 214*(3), 606-615. https://doi.org/10.1016/j.ejor.2011.05.018

Trapero, J. R., & Pedregal, D. J. (2016). A novel time-varying bullwhip effect metric: An application to promotional sales. *International Journal of Production Economics, 182*, 465-471. https://doi.org/10.1016/j.ijpe.2016.09.014

Van Donselaar, K. H., Van Woensel, T., Broekmeulen, R. A. C. M., & Fransoo, J. C. (2006). Inventory control of perishables in supermarkets. *International Journal of Production Economics, 104*(2), 462-472. https://doi.org/10.1016/j.ijpe.2004.10.019

---

## Anexos

- Anexo A. Consultas DAX de extracción (en `codigo/analisis_diagnostico_fase1.py`).
- Anexo B. Registro de hallazgos sobre los datos (`informes/Registro_hallazgos.md`).
- Anexo C. Figuras 1 a 10 (`figuras/`).
- Anexo D. Tablas de resultados (`datos/procesados/`).
- Anexo E. **[PENDIENTE]** Código del modelo y de la simulación.
- Anexo F. **[PENDIENTE]** Guía de uso de la herramienta para el encargado de pedidos.
