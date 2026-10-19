# Bitácora de avances — Práctica empresarial Postobón S.A.

**Estudiante:** Adrian Camilo Hernández Copete — Ing. Industrial, U. de Antioquia
**Empresa:** Postobón S.A., Desarrollo Logístico (Medellín)
**Práctica:** 22/06/2026 – 21/12/2026
**Alcance:** 2 puntos de venta (Ex 039 Éxito San Antonio, St 341 Villanueva – Olímpica), categoría BNA.

Registro histórico de los avances reales de la práctica, en orden cronológico.
Cada entrada se **agrega al final** — nunca se sobrescribe ni se borra una anterior.
Sirve como respaldo ante la asesora, insumo del informe final y base de la sustentación.

---

### Avance — 2026-09-03
**Fase/objetivo relacionado:** Fase 1 – Diagnóstico (Objetivo específico 1: diagnosticar el estado actual de las devoluciones y el comportamiento histórico de ventas).

**Qué se hizo:**
Se consolidó y depuró la base completa de devoluciones por vencimiento de los dos puntos de venta para 24 meses (01/09/2024 – 31/08/2026), cruzando cuatro fuentes: el modelo de Power BI GA05-Notas Crédito (vía consulta DAX), la colocación, el maestro de vidas útiles y el maestro de puntos de venta. Con esa base se cuantificó la devolución por vencimiento, se identificó el mecanismo que la genera y se priorizaron las referencias críticas de cada tienda. Todo el análisis quedó en código Python reproducible (`analisis_diagnostico_fase1.py` / `.ipynb`) y en un informe con gráficos.

**Resultados clave / cifras:**
- **Éxito San Antonio:** 90.635,7 cajas colocadas (bruto), 1.401,3 devueltas por vencimiento → **tasa 1,55 %** ($59.277.873). 244 SKU con devolución en 195 de 730 días.
- **Olímpica Villanueva:** 4.406,3 cajas colocadas (bruto), 174,7 devueltas → **tasa 3,97 %** ($17.357.428). 112 SKU con devolución en 50 de 730 días. Devuelve 2,6 veces más que Éxito en proporción, moviendo solo el 4,6 % del volumen.
- El **vencimiento es el primer motivo de devolución** en ambas: 61,0 % (Éxito) y 62,0 % (Olímpica) del total devuelto.
- **Mecanismo causal:** los SKU cuya cobertura implícita (lote medio ÷ consumo diario) supera su vida útil devuelven mucho más — 7,09 % vs. 1,51 % en Éxito (4,7×) y 8,96 % vs. 3,49 % en Olímpica (2,6×).
- **Causa estructural de la brecha entre tiendas:** frecuencia de entrega. Éxito 5,1 entregas/semana (cobertura mediana 26,1 días); Olímpica 1,9 entregas/semana (cobertura mediana 73,0 días) contra vidas útiles medianas de 160 y 150 días.
- **Rezago de decisión (solo Éxito):** la colocación de un mes correlaciona con la devolución del mes siguiente (r = 0,716). Caso extremo: diciembre/2024 colocó 14.859,9 cajas (4,5× la mediana) y enero/2025 devolvió 239,0 cajas — tasa 10,43 %, la peor de la serie.
- **Concentración:** 60 SKU de 238 en Éxito (25,2 %) y 32 de 95 en Olímpica (33,7 %) explican el 80 % de la devolución. En Éxito la familia Hit 1.000 ml Tetra concentra el 24,2 % de toda la devolución de la tienda; en Olímpica el perfil es mucho más repartido (el primer SKU no llega al 8,3 %).

**Figuras del diagnóstico:**
Los PNG están en `figuras/` y no se versionan en git (contienen cifras de la operación real); se regeneran corriendo `analisis_diagnostico_fase1.py`. La versión interactiva está en `Informe_diagnostico_Fase1.html`.

![Fig. 1 — Tasa mensual de devolución por vencimiento](figuras/fig1_tasa_mensual.png)
*Fig. 1 · Tasa mensual de devolución por vencimiento, Éxito vs. Olímpica (24 meses). Muestra las trayectorias opuestas: Éxito bajando hacia ~1 %, Olímpica en cero el primer semestre y luego en el rango 4–15 %.*

![Fig. 2 — Colocación mensual bruta por tienda](figuras/fig2_colocacion_mensual.png)
*Fig. 2 · Colocación mensual bruta por tienda. Deja ver el pico de diciembre/2024 en Éxito (14.859,9 cajas, 4,5× la mediana) que antecede en un mes a la peor tasa de la serie.*

![Fig. 3 — Tasa según cobertura del lote frente a vida útil](figuras/fig3_cobertura_vida_util.png)
*Fig. 3 · Tasa de devolución según cobertura del lote frente a vida útil. Es la evidencia del mecanismo causal: cuando el lote cubre más días que la vida útil del producto, la tasa se multiplica (4,7× en Éxito, 2,6× en Olímpica).*

![Fig. 4 — Pareto de SKU por tienda](figuras/fig4_pareto_sku.png)
*Fig. 4 · Pareto de cajas devueltas por vencimiento por SKU y tienda. Sustenta la selección del piloto: 60 SKU en Éxito y 32 en Olímpica concentran el 80 % de la devolución.*

**Decisiones o supuestos tomados:**
- **Todas las tasas se calculan sobre colocación BRUTA (solo filas positivas).** Se detectó que el archivo de colocación entregado venía neto de notas crédito: 2.239 filas negativas (10,0 % del total), de las cuales 1.225 de 1.252 coinciden al decimal con una devolución de la misma fecha/PDV/SKU. La devolución por vencimiento estaba descontada en un 95,5 % (Éxito) y 97,4 % (Olímpica), de modo que usar el archivo tal como viene resta el numerador del denominador e infla la tasa (daría 1,59 % y 4,33 %).
- Se usa `Día Transacción` como fecha, no `Fecha`, porque esta última tiene registros inconsistentes (valores hasta el año 2204). Ambas difieren en ~50 % de las filas.
- Unidad de medida: cajas físicas, para que devolución y colocación sean comparables.
- Se excluyen los rechazos del indicador principal; se conserva el universo completo de notas crédito como base de validación.
- La rotación real se aproxima con el promedio de colocación del periodo (supuesto: sobre 24 meses lo que entra se vende). Válido para diagnosticar, **no** para calibrar el modelo.

**Pendientes / bloqueos:**
- **Bloqueo principal (externo):** no se tiene venta al consumidor (sell-out) ni inventario en tienda. Sin uno de los dos, el modelo de Fase 2 no se puede calibrar ni validar contra los parámetros tradicionales. Hay que solicitarlo a Postobón.
- Confirmar con la asesora externa cuál de las dos columnas de fecha del GA05 es la contable.
- El maestro de vidas útiles es del centro 43, pero ambos PDV reciben también del centro 79; falta validar si la vida útil difiere por planta de origen.
- Truncamiento por la izquierda: con vidas útiles de hasta 360 días, 12 SKU (203,1 cajas, 12,9 % del total) muestran más devolución que colocación registrada, concentrados en enero/2025.

**Dificultad del periodo (para el informe de avance):**
La dependencia de datos externos volvió a manifestarse. Además del mes 2 perdido por la entrega tardía, en esta fase se detectó que el archivo de colocación venía neto de devoluciones, lo que obligó a rehacer todo el cálculo de tasas. Lección: los extractos recibidos deben validarse contra una fuente independiente **antes** de usarlos como insumo, no después.

**Próximo paso:**
Cerrar Fase 1 con la priorización formal de SKU críticos y arrancar Fase 2 (diseño del modelo). Tres definiciones ya orientadas por el diagnóstico: (1) el pronóstico no puede ser suavización exponencial sobre la serie diaria — es intermitente, hay que agregar a semana/mes o usar métodos tipo Croston; (2) la vida útil entra como **tope duro** de la cantidad a pedir, no como penalización suave; (3) la frecuencia de entrega es un parámetro por tienda (ciclos equivalentes de 1,4 días en Éxito y 3,7 en Olímpica), por lo que el mismo SKU tendrá stock mínimo distinto en cada punto de venta.

---

### Avance — 2026-09-04
**Fase/objetivo relacionado:** Transversal — trazabilidad y control de versiones (soporte a todas las fases).

**Qué se hizo:**
Se formalizó el registro del proyecto: se creó esta bitácora acumulada y se inicializó el repositorio git local del código, con un `.gitignore` que excluye toda la información de Postobón (extractos `.xlsx`/`.XLSX`, modelo `.pbix`, carpeta `datos/`, cualquier `.csv`, figuras e informe HTML con cifras de la operación) además de credenciales y archivos de entorno. Se versionan únicamente el código, el CLAUDE.md, el resumen metodológico y esta bitácora.

**Resultados clave / cifras:**
- Repositorio local inicializado (no remoto). Primer commit ligado a Fase 1.
- 0 archivos de datos de la empresa rastreados por git.

**Decisiones o supuestos tomados:**
- El repositorio permanece **local**. Si en algún momento se sube a un remoto, debe ser privado y confirmarse antes del push.
- El notebook se versiona sin outputs ejecutados, para que no queden tablas con datos a nivel SKU embebidas en el historial.

**Pendientes / bloqueos:** ninguno.

**Próximo paso:** Fase 2 — diseño del modelo de pronóstico de demanda y de la fórmula de stock mínimo por SKU y punto de venta.

---

### Avance — 2026-09-04
**Fase/objetivo relacionado:** Transversal — organización del repositorio (soporte a todas las fases).

**Qué se hizo:**
Se reorganizó el proyecto, que hasta ahora tenía código, extractos de datos, figuras e informes mezclados en la raíz. Quedó una estructura por función (`codigo/`, `datos/crudos/`, `datos/procesados/`, `figuras/`, `informes/`, `documentos/`), se ajustaron todas las rutas del análisis de Fase 1 y se verificó que el código corre completo desde la nueva ubicación reproduciendo las mismas cifras. Se agregó un `README.md` con el mapa del repositorio y las instrucciones de reproducción.

**Resultados clave / cifras:**
- 17 archivos reubicados; la raíz pasó de 14 archivos sueltos a 4 (contexto, mapa, bitácora y `.gitignore`).
- El análisis corre sin cambios de resultado: Éxito 1,55 % y Olímpica 3,97 % de tasa de devolución por vencimiento (idénticas a las del diagnóstico).
- 0 archivos con datos de Postobón versionados tras la reorganización (verificado con `git check-ignore`).

**Decisiones o supuestos tomados:**
- Se separó `datos/crudos/` (lo que entrega Postobón o sale de la consulta DAX, nunca se edita) de `datos/procesados/` (lo que genera el código y se puede borrar y regenerar). La distinción evita sobrescribir un extracto de la empresa por error.
- El código dejó de usar `Path.cwd()` y ahora localiza la raíz del proyecto buscando `CLAUDE.md` hacia arriba, para que corra igual desde la raíz o desde `codigo/` y no dependa de dónde se lance el cuaderno.
- La estructura y las reglas para archivos nuevos quedaron escritas en `CLAUDE.md`, de modo que el código de las Fases 2 y 3 nazca en su carpeta.

**Pendientes / bloqueos:** el modelo `GA05-Notas Credito.pbix` no se pudo mover a `datos/crudos/` porque está abierto en Power BI Desktop; queda en la raíz hasta cerrar la aplicación.

**Próximo paso:** Fase 2 — diseño del modelo de pronóstico de demanda y de la fórmula de stock mínimo por SKU y punto de venta.

---

### Avance — 2026-09-15
**Fase/objetivo relacionado:** Fase 1 – Diagnóstico (OE1) — auditoría completa del proyecto, análisis exploratorio y construcción de los entregables escritos.

**Qué se hizo:**
Se auditó todo el proyecto (código, datos, informes). Se verificó la exportación del Power BI GA05-Notas Crédito por consistencia entre las dos consultas DAX independientes (los tres CSV cuadran fila a fila). Se terminó la depuración con reglas centralizadas en un módulo común, se agregó el análisis exploratorio y de calidad que faltaba (`eda_fase1.py`, figuras 5–10, 16 tablas nuevas) y se sometieron los hallazgos del diagnóstico del 03/09 a pruebas de robustez. Dos de los cuatro hallazgos no resistieron y se corrigieron en todos los informes. Se crearon el registro numerado de hallazgos (H-01…H-14), el informe de avance N.º 1 (secuencial, meses 1–3), el borrador del informe final con la estructura de la plantilla U. de A. y el archivo con instrucciones para cuando llegue la venta diaria.

**Resultados clave / cifras:**
- **Exportación GA05:** consistente (0 diferencias entre extractos). Pero 635 de 1.979 líneas (32 %) traen valor sin cantidad: $26,6 M (34,7 % del valor), solo centro 43, desde jul/2025 (H-03). Éxito: 404 líneas, $15,3 M; Olímpica: 231 líneas, $11,3 M (65 % de su valor). Cota superior de la tasa si fueran físicas: Éxito 2,12 %, Olímpica 12,44 %.
- **Correcciones a cifras publicadas:** Éxito 0 meses en cero real (no 1); Olímpica 6 (no 8). SKU/días con devolución física: Éxito 238 / 168 (antes 244 / 195), Olímpica 95 / 35 (antes 112 / 50). Las tasas 1,55 % y 3,97 % no cambian, pero son piso.
- **Hallazgo 2 reformulado (H-08):** r = 0,716 a rezago 1 depende de dic-24/ene-25; Spearman 0,03, Pearson sin ese par −0,09. Es un episodio, no un patrón.
- **Hallazgo 3 reformulado (H-07):** la "cobertura implícita" era 730 ÷ entregas y el grupo "excede" eran SKU esporádicos (mediana 2–3 entregas). Con el intervalo real solo 1 SKU por tienda supera su vida útil. Lo robusto es el gradiente: tasa de 0,42 % → 12,4 % (Éxito) y 0,18 % → 17,1 % (Olímpica) al crecer intervalo ÷ vida útil; Spearman +0,49 y +0,61 (Fig. 10).
- **Exploración:** cambio de centro 79→43 en junio/2025 en ambas tiendas (H-05); Olímpica recibe el 21 % de su colocación fuera de X/S (H-06), Éxito 100 % en calendario; lead time 1–3 días; lote mediano 2 cajas (Éxito) y 1 (Olímpica); 83 % / 87 % de los SKU con demanda intermitente o abultada (H-12); vida útil mediana ponderada por cajas 140 / 120 días.

**Decisiones o supuestos tomados:**
- Toda carga de datos pasa por `codigo/comun.py`; los cuadernos se regeneran desde los scripts sin salidas.
- Las líneas sin cantidad quedan marcadas y fuera de todo conteo físico; el valor se reporta separado. Pendiente confirmar su origen con la asesora externa.
- Alcance "BNA" = clasificaciones BNA + Mundo Cero del GA05 (H-09).
- El Hallazgo 3 pasa al modelo como restricción continua (intervalo ÷ vida útil remanente), no como umbral.
- Archivos reubicados: `.pbix` a `datos/crudos/`; marco teórico (23 refs) copiado a `documentos/`; revisión de literatura movida de la raíz a `documentos/`.

**Pendientes / bloqueos:**
- Venta diaria (sell-out) e inventario en tienda sin entregar (H-13): bloquea la calibración de la Fase 2.
- Agenda con la asesora externa: H-02, H-03, H-05, H-06, H-13.
- Re-ejecutar la consulta DAX con Power BI abierto para cerrar formalmente la verificación.

**Dificultad del periodo (para el informe de avance):**
Los hallazgos propios también hay que auditarlos: dos de cuatro no resistieron pruebas de robustez sencillas. Se corrigieron antes de llegar a un informe evaluado y quedó la regla de que toda cifra pasa por una prueba de sensibilidad y se registra con código H-nn.

**Próximo paso:** reunión con la asesora externa por los hallazgos abiertos; al recibir la venta diaria, ejecutar `PENDIENTE_ventas_diarias.md`; iniciar Fase 2 (pronóstico por clase ADI–CV² y fórmula de cantidad a pedir con tope por vida útil remanente).

---

### Avance — 2026-09-15 (complemento)
**Fase/objetivo relacionado:** Fase 1 – Diagnóstico (OE1) — gráficos exploratorios básicos y versión Word del informe de avance.

**Qué se hizo:**
Se agregó al análisis exploratorio la sección de gráficos básicos por SKU y tienda (diagramas de caja, histogramas, matriz de correlación de Spearman y dispersión de la tasa frente a sus variables candidatas; figuras 11–14, tabla `eda_variables_sku.csv` y matrices `eda_correlacion_spearman_*.csv`). Se incrustaron las 14 figuras en el informe de avance en el punto donde se discuten y se construyó un generador Markdown → Word (`codigo/generar_informe_docx.py`) que produce `informes/Informe_avance_01.docx` (y el Word de los demás informes) con las figuras embebidas.

**Resultados clave / cifras:**
- Spearman con la tasa de devolución (SKU con ≥ 3 entregas): intervalo ÷ vida útil +0,36 (Éxito, 323 SKU) y +0,62 (Olímpica, 141 SKU); ADI +0,28 y +0,54; intervalo entre entregas +0,24 y +0,50; vida útil sola −0,20 y −0,22; lote medio, cajas colocadas y CV² sin relación apreciable.
- Vida útil mediana por SKU casi igual en las dos tiendas (168 y 160 días); intervalo mediano entre entregas 12,9 frente a 35 días; fracción intervalo ÷ vida útil mediana 0,08 frente a 0,24: la diferencia entre tiendas es de frecuencia de reposición, no de producto.
- Informe de avance N.º 1 en Word: 121 párrafos, 7 tablas, 14 figuras, títulos numerados en secuencia.

**Decisiones o supuestos tomados:** los informes se escriben en Markdown con las figuras referenciadas en el punto donde se discuten y el Word se genera desde ahí (no se versiona); las correlaciones se reportan con Spearman por la asimetría de las variables.

**Pendientes / bloqueos:** sin cambios (H-02, H-03, H-05, H-06, H-13).

**Próximo paso:** sin cambios respecto a la entrada anterior.

---

### Avance — 2026-09-16
**Fase/objetivo relacionado:** Fase 2 – Diseño del modelo de pronóstico de demanda y de la fórmula de stock mínimo (OE2), adelantado mientras se espera la venta diaria (H-13).

**Qué se hizo:**
Se diseñó y codificó un primer borrador de la arquitectura completa del modelo (`codigo/modelo_stock_minimo.py`): selección del método de pronóstico según la clase de intermitencia de cada SKU (SES para demanda suave, SBA para intermitente/errática, TSB para abultada), un backtest simple con MASE para validar esa selección, y la fórmula de cantidad a pedir (revisión periódica con colchón de seguridad, topada por lo que la vida útil remanente permite vender). Como todavía no llega la venta diaria, el pipeline corre sobre la colocación (sell-in) como proxy de demanda, igual que ya se hizo para el hallazgo H-12; ninguna cifra que produce se reporta como resultado del proyecto, solo confirma que la arquitectura funciona de punta a punta. El periodo de revisión y el lead time de la fórmula sí son reales, tomados del calendario de entregas del maestro comercial y de la colocación.

**Resultados clave / cifras (todas sobre colocación como proxy, no son resultado del proyecto):**
- Éxito: 512 combinaciones SKU procesadas (149 suaves/erráticas, 91 abultadas, el resto intermitentes); Olímpica: 19 abultadas, 1 errática, el resto intermitentes. Ningún SKU "suave" en Olímpica (consistente con H-12).
- Backtest MASE (mediana): Éxito 0,81 (suave), 0,63 (errática), 1,12 (intermitente), 0,91 (abultada); Olímpica 1,26 (intermitente), 0,90 (abultada) — con demanda real se espera que mejore, porque el sell-in trae ruido logístico adicional (efecto látigo) que la venta al consumidor no tiene.
- Periodo de revisión real: Éxito 1,2 días (6 entregas/semana), Olímpica 3,5 días (2 entregas/semana, H-06); lead time mediano 2 días en ambas.
- Con la demanda proxy actual, el tope de vida útil casi no se activa (0,3 % de los SKU en Éxito, 0 % en Olímpica): la restricción se pondrá a prueba de verdad con la venta real, que va a mostrar más concentración de demanda en menos SKU.

**Decisiones o supuestos tomados:**
- Umbrales ADI = 1,32 y CV² = 0,49 (Syntetos, Boylan y Croston, 2005), los mismos que ya se usaron en el diagnóstico de intermitencia (H-12).
- Nivel de servicio inicial z = 1,28 (≈90 %) para el colchón de seguridad; se calibra en la Fase 3 con la simulación de escenarios.
- Inventario proyectado = 0 y vida útil remanente = vida útil total del SKU (sin descontar edad de lote) como supuestos temporales, porque aún no hay inventario en tienda reconstruido; ambos sesgan la cantidad a pedir al alza y se corrigen en cuanto llegue el inventario (Paso 4 de `PENDIENTE_ventas_diarias.md`).
- Se dejó fuera a propósito la priorización de SKU críticos y el informe parcial: ambos se hacen con la venta real, no antes.
- De paso se corrigió un bug de codificación en `codigo/sincronizar_notebooks.py` (fallaba en consola Windows con cp1252 al imprimir "→"); mismo ajuste que ya tenía `comun.py`.

**Pendientes / bloqueos:** todo el pipeline queda bloqueado para convertirse en resultado real hasta que llegue la venta diaria y el inventario (H-13); mientras tanto sirve solo como borrador de arquitectura ya probado.

**Próximo paso:** al recibir la venta diaria, seguir `PENDIENTE_ventas_diarias.md` (Pasos 1–5): cargador `cargar_ventas()`, reconciliación sell-in vs. sell-out, reclasificación ADI–CV² con venta real, reconstrucción de inventario y recalibración de este mismo modelo con datos reales; en paralelo, avanzar la redacción de la sección metodológica del informe final con el marco teórico ya verificado.

---

### Avance — 2026-09-16 (complemento)
**Fase/objetivo relacionado:** Fase 2 – Diseño del modelo (OE2) y Fase 4 – Documentación: sección metodológica del informe final.

**Qué se hizo:**
Se redactó la sección 4.5 del borrador del informe final ("Modelo de pronóstico de demanda y cantidad a pedir"), con seis subsecciones: estado de la información al momento del diseño (qué insumos son reales y cuáles esperan la venta diaria), clasificación ADI–CV², métodos de pronóstico por clase (SES, Croston, SBA, TSB) con su justificación, validación con MASE, fórmula de cantidad a pedir con tope por vida útil remanente y sus supuestos, y la tabla de salida del modelo. Se cerró el pendiente de Fase 2 en la sección 4.4 y se dejó en 5.2 la nota de que los resultados esperan la venta diaria. Todas las citas salen de la lista de 23 referencias ya verificadas; no se agregaron fuentes nuevas.

**Resultados clave / cifras:** sección de unas 150 líneas en Markdown; el Word se regenera con `generar_informe_docx.py` (los subíndices se escribieron en Unicode porque el generador no interpreta etiquetas HTML).

**Decisiones o supuestos tomados:** la sección describe el método (cómo) y deja los resultados (cuánto) para 5.2, de modo que no haya que reescribirla cuando llegue la venta real: solo cambian los insumos marcados como pendientes.

**Pendientes / bloqueos:** sin cambios (H-13 bloquea los resultados de 5.2; lote mínimo de pedido y nivel de servicio objetivo por confirmar con la asesora externa).

**Próximo paso:** esqueleto de `cargar_ventas()` en `comun.py` y, al llegar la venta diaria, ejecutar `PENDIENTE_ventas_diarias.md`.

---

### Avance — 2026-09-18
**Fase/objetivo relacionado:** Fase 1 – Diagnóstico (cierre: universo de SKU) → insumo directo de Fase 2 (priorización C-7 y universo del modelo).

**Qué se hizo:**
Se cruzó el maestro de vidas útiles (1.588 SKU, centro 43) con la colocación bruta y las devoluciones por vencimiento de la ventana sep/2024 – ago/2026 para determinar cuántos SKU están realmente activos en cada tienda. Un SKU se considera activo si tuvo al menos una colocación o una devolución en la tienda. Script nuevo `codigo/sku_activos.py`; salida `datos/procesados/sku_activos.xlsx` (hojas Resumen, SKU activos, Sin vida útil).

**Resultados clave / cifras:**
| Tienda | Con colocación | Con devolución | Solo devolución | **SKU activos** |
|---|---|---|---|---|
| Éxito | 340 | 244 | 6 | **346** |
| Olímpica | 172 | 112 | 9 | **181** |
| Unión | 352 | 270 | 13 | **365** |
- 162 SKU activos en ambas tiendas a la vez; Olímpica maneja aproximadamente la mitad del surtido de Éxito.
- Solo el 23 % del maestro de vidas útiles (365 de 1.588) se mueve en los dos PDV.
- 1 SKU con movimiento sin vida útil: 1100 CILINDRO CO2 (Éxito), que no es una bebida (pregunta E-8).

**Decisiones o supuestos tomados:** las líneas `Solo_valor` (H-03) cuentan como evidencia de actividad (prueban que el SKU se movió), aunque no aporten cajas. El denominador de colocación es la bruta (H-01).

**Pendientes / bloqueos:** confirmar exclusión del CILINDRO CO2 (E-8); revisar los 13 SKU con devolución sin colocación (C-10).

**Próximo paso:** usar `sku_activos.csv` como universo del modelo y de la priorización de SKU críticos; al llegar la venta diaria, contrastar el universo con los SKU que registran sell-out.

---

### Avance — 2026-10-02
**Fase/objetivo relacionado:** Fase 1 – Diagnóstico (verificación del numerador: líneas sin cantidad del GA05, H-03 → H-16).

**Qué se hizo:**
Se consolidaron las descargas de la plataforma CEN de enero/2026 (31 CSV del portal Éxito y 41 TXT de Olímpica) y se filtraron a los dos puntos de venta del proyecto. El EAN del portal se llevó a SKU SAP con el maestro de portafolio de Éxito y se cruzó con las notas crédito del GA05, que en enero/2026 vienen todas sin cantidad. Cargadores nuevos en `comun.py` y script `codigo/cruce_devoluciones_cen.py` (Fig. 15).

**Resultados clave / cifras:**
- **Éxito San Antonio:** el portal registra 17 devoluciones BNA + Mundo Cero en enero/2026: 34 SKU, 280 unidades = **37,0 cajas físicas** (valor a precio GA05 $1,14 M). Los 34 SKU tienen líneas en cero en el GA05 (ene–feb) y en 23 hay una línea cuyo valor es exactamente unidades × precio → las líneas en cero **sí son devoluciones físicas**.
- Pero el GA05 valora **4,34 veces** lo devuelto en esos SKU ($4,93 M vs. $1,14 M): 27 líneas son múltiplos exactos (2×–7×, 14 el 29/01) y 73 de 148 líneas de enero repiten valor en otra fecha. La cota superior por valor (≈ 303 cajas en enero) sobrestima; el portal muestra 37.
- 8 EAN BNA (37 unidades) no están en el maestro de Éxito; 26 SKU del GA05 de enero ($3,22 M) no tienen devolución en el portal ese mes.
- **Olímpica Villanueva:** no verificable. Los 41 TXT son avisos de recibo del CD Barranquilla (8001), no devoluciones de la tienda 341; el maestro de Olímpica no trae SKU SAP.

**Decisiones o supuestos tomados:** la cantidad de las líneas sin cantidad se tomará del portal CEN (unidades → cajas con el factor unidades/caja del GA05), no de valor ÷ precio. No se modifica `cargar_devoluciones()` con un solo mes y una sola tienda. Devoluciones que reaparecen en otra descarga por recogida reprogramada se cuentan una vez.

**Pendientes / bloqueos:** CEN de Éxito jul/2025 – abr/2026 (B-3a); devoluciones de Villanueva desde el CEN de Olímpica (B-4); ¿notas duplicadas o efecto del modelo? (E-10, C-11); homologar 8 EAN (E-11).

**Próximo paso:** llevar a la asesora externa el ejemplo de la Uva 1,5 L (23 unidades devueltas → GA05 4× + 1×) y pedir el extracto CEN completo; con él, extender el cruce a todos los meses y rellenar cantidades (C-12).

