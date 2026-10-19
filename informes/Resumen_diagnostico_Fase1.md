# Diagnóstico Fase 1 — Devoluciones por vencimiento vs. colocación

**Proyecto:** Herramienta estadística de reabastecimiento basada en optimización del stock mínimo para reducir devoluciones por caducidad, canal moderno.
**Alcance:** 2 puntos de venta — Ex 039 Éxito San Antonio y St 341 Villanueva (Olímpica). Categoría BNA (clasificaciones BNA y Mundo Cero), regional Antioquia.
**Periodo:** 01/09/2024 – 31/08/2026 (24 meses).
**Fecha del análisis:** 03/09/2026. **Corregido tras auditoría:** 15/09/2026.

> **Nota de auditoría (15/09/2026).** Este resumen reemplaza la versión del 03/09.
> Tres afirmaciones de esa versión no resistieron las pruebas de robustez y se
> corrigen aquí (detalle en `informes/Registro_hallazgos.md`):
> 1. **H-03:** un tercio de las líneas de nota crédito trae valor sin cantidad. Los
>    "meses en cero" de ene/2026 (Éxito) y ene–feb/2026 (Olímpica) no son ceros reales;
>    el valor devuelto se reporta separado; los conteos de SKU y días pasan a ser de
>    devolución *física*.
> 2. **H-08:** la correlación de rezago 1 mes (r = 0,716) es un artefacto de un solo par
>    de meses. El hallazgo 2 se reformula como un episodio, no como patrón.
> 3. **H-07:** la "cobertura implícita" era 730 ÷ entregas y el grupo "excede vida útil"
>    eran SKU esporádicos. El hallazgo 3 se reformula como gradiente continuo (Fig. 10).
> Las tasas 1,55 % y 3,97 % no cambian, pero se leen como piso.

---

## 1. Datos y método

| Fuente | Contenido | Registros |
|---|---|---|
| Power BI `GA05-Notas Crédito` (consulta DAX) | Devoluciones por motivo "Fecha de Vencimiento", tipo Devolución | 1.979 filas (fecha × PDV × SKU) |
| Power BI `GA05-Notas Crédito` (segunda consulta DAX) | Universo completo de notas crédito de los 2 PDV, todos los motivos y tipos | 3.513 filas |
| `Colocacion.xlsx` | Colocación por fecha, cliente SAP, centro y material | 22.358 filas |
| `Vidas utiles.XLSX` | Vida útil en días por SKU (centro 43) | 1.588 SKU; cubre 365 de los 366 con colocación o devolución (H-15) |
| `Puntos de venta.xlsx` | Frecuencia de pedido y entrega por PDV | 2 PDV |

**Unidad:** cajas físicas (la única presente en colocación y devoluciones; H-04).
**Identificación de tiendas:** el `Cod Cliente SAP` es la cadena; la tienda se
identifica por `Cliente`. Se validó que la colocación es de un solo PDV por cadena:
el 82 % de las líneas de Olímpica se entrega miércoles y sábado, como dice el maestro.
**Fecha:** `Día Transacción` (H-02, pendiente confirmar la contable).
**Verificación de la exportación:** los tres CSV del GA05 son consistentes entre sí
(`verificacion_exportacion_ga05.csv`).

---

## 2. Correcciones metodológicas sobre los datos

**2.1 La colocación venía neta de devoluciones (H-01).** 2.239 filas negativas (10 %);
1.225 de 1.252 cruces con devoluciones coinciden al decimal; el 99,9 % de las filas con
pedido = entrega son negativas. El 80,5 % de las cajas negativas son devoluciones y el
19,5 % rechazos; la devolución por vencimiento está descontada en un 95,5 % (Éxito) y
97,4 % (Olímpica). **Decisión:** colocación bruta (solo positivas) como denominador.
Con el archivo tal como venía la tasa se inflaría a 1,59 % y 4,33 %.

**2.2 Líneas de nota crédito con valor y sin cantidad (H-03).** 635 de 1.979 líneas
(32 %) traen valor y cero cajas/unidades/hectolitros: $26,6 M (34,7 % del valor).
Solo centro 43, desde julio/2025; en Éxito ene/2026 y Olímpica ene–feb/2026 el 100 %
de las líneas. No es conversión de unidades (150 de 161 SKU sí traen cajas en otras
fechas). Cota superior si fueran físicas: 2,12 % (Éxito) y 12,44 % (Olímpica).
**Pendiente:** confirmar con la asesora externa qué documento las genera.

**2.3 Truncamiento por la izquierda (H-11).** 12 SKU (203 de 1.576 cajas, 12,9 %) con
más devolución que colocación, casi todos en enero/2025 y con vida útil larga.

**2.4 Cambio de centro (H-05) y calendario real (H-06).** Ambas tiendas pasaron del
centro 79 al 43 en junio/2025; Olímpica recibe el 21 % de su colocación fuera de
miércoles y sábado.

---

## 3. Resultado principal

| Indicador | Éxito San Antonio | Olímpica Villanueva |
|---|---|---|
| Colocado bruto (cajas) | 90.635,7 | 4.406,3 |
| Devuelto por vencimiento, líneas con cantidad (cajas) | 1.401,3 | 174,7 |
| **Tasa de devolución por vencimiento** | **1,55 %** | **3,97 %** |
| Cota superior (H-03) | 2,12 % | 12,44 % |
| Valor devuelto, líneas con cantidad | $44.024.179 | $6.008.223 |
| Valor en líneas sin cantidad | $15.253.694 | $11.349.205 |
| SKU activos (colocación o devolución en la ventana, H-15) | 346 | 181 |
| SKU con devolución física | 238 | 95 |
| Días con devolución física (de 730) | 168 | 35 |
| Meses en cero real (de 24) | 0 | 6 |
| Devoluciones totales, todos los motivos (cajas) | 2.298,6 | 281,8 |
| **Vencimiento sobre el total de devoluciones** | **61,0 %** | **62,0 %** |
| Tasa de devolución por todos los motivos | 2,54 % | 6,39 % |

**El vencimiento es el primer motivo de devolución en ambas tiendas.** Olímpica
devuelve 2,6 veces más que Éxito en proporción a lo que recibe, moviendo el 4,6 % del
volumen.

---

## 4. Cuatro hallazgos (versión corregida)

### 4.1 Trayectorias opuestas (Fig. 1)
Éxito baja desde 2025 y cierra en 1,28 %; Olímpica arranca en cero el primer semestre
(seis ceros reales) y desde abril/2025 se mueve entre 4 % y 15 % (cierra en 4,00 %).
Las series semanales son intermitentes: Éxito tiene devolución física en 85 de 106
semanas, Olímpica en 31.

### 4.2 Un episodio de sobrecolocación, no un patrón de rezago (H-08)
Diciembre/2024: Éxito recibió 14.859,9 cajas (4,5 veces la mediana de 3.271), el 64 %
en Bretaña 300 ml vidrio no retornable (9.562 cajas). Enero/2025: 239,0 cajas
devueltas, tasa 10,43 %, el 71 % en la familia Hit 1.000 ml Tetra. La correlación de
Pearson a rezago 1 (0,716) no es robusta: Spearman 0,030; sin ese par de meses,
−0,088. Se conserva como caso, no como regla. En Olímpica no hay correlación con
ningún método.

### 4.3 La tasa crece con la fracción de vida útil consumida entre entregas (H-07, Fig. 10)
Con el intervalo real entre entregas — (última − primera) ÷ (entregas − 1), SKU con
≥ 3 entregas — solo un SKU por tienda supera su vida útil. Pero la tasa sube de forma
monótona con intervalo ÷ vida útil:

| Intervalo ÷ vida útil | Éxito | Olímpica |
|---|---|---|
| < 5 % | 0,42 % (90 SKU) | 0,18 % (3) |
| 5–10 % | 4,23 % (101) | 0,14 % (16) |
| 10–20 % | 6,87 % (82) | 1,88 % (45) |
| 20–35 % | 4,88 % (37) | 2,60 % (39) |
| 35–50 % | 12,38 % (9) | 14,40 % (24) |
| 50–100 % | 7,58 % (3) | 17,14 % (13) |

Spearman(fracción, tasa) = +0,49 (Éxito) y +0,61 (Olímpica).

**Por qué Olímpica está peor — estructura de reposición:**

| | Éxito San Antonio | Olímpica Villanueva |
|---|---|---|
| Frecuencia de entrega (maestro) | L–S | X, S (+ 21 % fuera de calendario) |
| Entregas por semana | 5,1 | 1,9 |
| Intervalo mediano entre entregas por SKU | 12,9 días | 35,0 días |
| Lote mediano por línea | 2 cajas | 1 caja |
| Vida útil mediana ponderada por cajas | 140 días | 120 días |
| % de cajas con vida útil ≤ 120 días | 49 % | 53 % |

### 4.4 El problema cabe en pocas referencias (Fig. 4)
60 de 238 SKU (25 %) en Éxito y 32 de 95 (34 %) en Olímpica explican el 80 % de la
devolución física. Éxito: la familia Hit 1.000 ml Tetra concentra el 24 % (338,9 cajas)
y la marca Hit el 34 %. Olímpica: repartido, el primer SKU no llega al 9 %. SKU con
tasa elevada: Bretaña 1.500 ml Pet x2 (31,5 %, VU 98 d) y Seven Up 400 ml (22,7 %, VU
49 d) en Éxito; Pepsi Black 1.500 ml (33,2 %, VU 70 d) y Soda Hatsu Frambuesa 310 ml
(30,0 %) en Olímpica.

### 4.5 La demanda es intermitente (H-12, Fig. 8)
Sobre colocación semanal, 83 % (Éxito) y 87 % (Olímpica) de los SKU tienen ADI > 1,32.
Olímpica no tiene SKU "suaves". Se recalcula con la venta diaria.

---

## 5. Limitaciones de la base actual

1. No hay venta al consumidor (H-13): la rotación se aproxima con colocación.
2. No hay inventario inicial ni en tienda.
3. Fecha contable del GA05 por confirmar (H-02).
4. Maestro de vidas útiles solo del centro 43; nueve meses fueron abastecidos por el
   79 (H-05).
5. Líneas sin cantidad del GA05 (H-03): las tasas son un piso.
6. Ventana insuficiente para vidas útiles largas (H-11).

---

## 6. Implicaciones para la Fase 2

1. Pronóstico con métodos para demanda intermitente (SBA/TSB), SES solo para los SKU
   suaves de Éxito; precisión con MASE.
2. La cantidad a pedir se acota por la demanda esperada dentro de la vida útil
   remanente, y la restricción actúa de forma continua con la fracción intervalo ÷
   vida útil, no como un umbral.
3. El periodo de revisión es un parámetro por tienda tomado del calendario real de
   entregas (no del maestro).

**Piloto propuesto:** 60 SKU en Éxito y 32 en Olímpica, ordenados por fracción de
vida útil consumida entre entregas.

---

### Archivos generados

| Archivo | Contenido |
|---|---|
| `codigo/comun.py` | Rutas, constantes, paleta y cargadores con las reglas de depuración |
| `codigo/analisis_diagnostico_fase1.py` / `.ipynb` | Validaciones, indicador, hallazgos 1–4, figuras 1–4, consultas DAX |
| `codigo/eda_fase1.py` / `.ipynb` | Calidad, verificación del GA05, exploración, intermitencia, robustez, figuras 5–10 |
| `codigo/sincronizar_notebooks.py` | Regenera los cuadernos desde los scripts |
| `datos/procesados/*.csv` | 21 tablas (indicador, por SKU, mensual, calidad, verificación, intermitencia, robustez) |
| `figuras/fig1..fig10 .png` | Figuras del diagnóstico y de la exploración |
| `informes/Registro_hallazgos.md` | Hallazgos H-01 a H-14 con evidencia, decisión y estado |
| `informes/Informe_avance_01.md` | Informe de avance secuencial (meses 1–3) |
| `informes/Informe_final_borrador.md` | Estructura del informe final con lo ya sustentado |

**Reproducibilidad:** `python codigo/analisis_diagnostico_fase1.py` y
`python codigo/eda_fase1.py` desde cualquier directorio; requieren `pandas`, `numpy`,
`matplotlib`, `openpyxl`. No necesitan Power BI (la consulta DAX está incluida pero
comentada).
