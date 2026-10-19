# Herramienta de reabastecimiento — Postobón S.A.

Práctica empresarial, Ingeniería Industrial (U. de Antioquia).
Modelo estadístico de stock mínimo para reducir devoluciones por caducidad en
**dos puntos de venta del canal moderno** (Éxito San Antonio y Olímpica
Villanueva), **categoría BNA** (clasificaciones BNA y Mundo Cero). El entregable
final del modelo es la **cantidad a pedir por SKU y por tienda** en cada ciclo de
reabastecimiento.

El contexto completo (objetivos, alcance, cronograma real, reglas de depuración,
convenciones) está en `CLAUDE.md`. El registro histórico de avances está en
`bitacora_avances.md`. Todo hallazgo sobre los datos tiene un código H-nn en
`informes/Registro_hallazgos.md`.

## Estructura del repositorio

```
.
├── CLAUDE.md                    Contexto y reglas del proyecto
├── README.md                    Este mapa
├── bitacora_avances.md          Registro acumulado de avances (no se sobrescribe)
├── PENDIENTE_ventas_diarias.md  Qué pegar y qué hacer cuando llegue la venta diaria
├── PENDIENTE_devoluciones_CEN.md  Qué pegar y qué hacer cuando lleguen las devoluciones del CEN
├── PENDIENTES.md                Lista viva única de pendientes, preguntas y recomendaciones
├── codigo/
│   ├── comun.py                       Rutas, constantes, paleta y cargadores de datos
│   ├── analisis_diagnostico_fase1.py  Fase 1 — indicador y hallazgos (figs. 1–4)
│   ├── eda_fase1.py                   Fase 1 — calidad, verificación, exploración,
│   │                                  intermitencia, robustez, gráficos básicos (figs. 5–14)
│   ├── modelo_stock_minimo.py         Fase 2 — BORRADOR: pronóstico por clase ADI–CV²
│   │                                  (SES/SBA/TSB) y fórmula de cantidad a pedir con tope
│   │                                  de vida útil; corre sobre colocación como proxy de
│   │                                  demanda hasta que llegue la venta diaria (H-13)
│   ├── sku_activos.py                 Cruce de SKU activos: maestro de vidas útiles ∩
│   │                                  (colocación ∪ devoluciones), por tienda
│   ├── sincronizar_notebooks.py       Regenera los .ipynb desde los .py
│   ├── generar_informe_docx.py        Convierte informes/*.md a Word con figuras
│   └── *.ipynb                        Cuadernos generados (sin salidas)
├── datos/                       ⚠ NO se versiona (información de Postobón)
│   ├── crudos/                  Extractos SAP, CSV de las consultas DAX y el .pbix
│   └── procesados/              Tablas calculadas por el código (se regeneran)
├── figuras/                     PNG generados por el código (no se versionan)
├── informes/
│   ├── Registro_hallazgos.md            Hallazgos H-01…H-14 (versionado)
│   ├── Informe_avance_01.md             Informe de avance secuencial, meses 1–3 (versionado)
│   ├── Informe_final_borrador.md        Estructura del informe final U. de A. (versionado)
│   ├── Resumen_diagnostico_Fase1.md     Resumen metodológico corregido (versionado)
│   ├── Informe_avance_01.docx           Versión Word con figuras (generada, no versionada)
│   └── Informe_diagnostico_Fase1.html   Informe visual del 03/09 con nota de auditoría (no versionado)
└── documentos/                  Propuesta, plantilla U. de A., marco teórico (no versionado)
```

### Qué hay en `datos/`

| Carpeta | Archivos | Origen |
|---|---|---|
| `crudos/` | `Colocacion.xlsx`, `Vidas utiles.XLSX`, `Puntos de venta.xlsx` | Extractos entregados por Postobón |
| `crudos/` | `devoluciones_vencimiento_analitico.csv`, `devoluciones_vencimiento_diario_*.csv/.xlsx`, `notas_credito_todas_*.csv` | Consultas DAX sobre `GA05-Notas Credito.pbix` |
| `crudos/` | `GA05-Notas Credito.pbix` | Modelo de Power BI (94 MB) |
| `procesados/` | `analisis_*.csv`, `resumen_cifras_diagnostico.csv` | Salidas de `analisis_diagnostico_fase1.py` |
| `procesados/` | `calidad_fuentes.csv`, `verificacion_exportacion_ga05.csv`, `eda_*.csv`, `robustez_*.csv`, `resumen_eda_fase1.csv` | Salidas de `eda_fase1.py` |
| `procesados/` | `modelo_backtest_mase_proxy_colocacion.csv`, `stock_minimo_BORRADOR_proxy_colocacion.csv` | Salidas de `modelo_stock_minimo.py` (BORRADOR, demanda = colocación) |
| `procesados/` | `sku_activos.csv/.xlsx`, `sku_activos_resumen.csv`, `sku_sin_vida_util.csv` | Salidas de `sku_activos.py` (universo de SKU activos por tienda) |

## Cómo reproducir el análisis

```bash
python codigo/analisis_diagnostico_fase1.py   # indicador, hallazgos 1–4, figuras 1–4
python codigo/eda_fase1.py                    # calidad, verificación GA05, exploración, robustez, figuras 5–14
python codigo/modelo_stock_minimo.py          # Fase 2 (BORRADOR): pronóstico por clase y cantidad a pedir
python codigo/sku_activos.py                  # universo de SKU activos (vida útil ∩ colocación ∪ devoluciones)
python codigo/sincronizar_notebooks.py        # regenera los cuadernos desde los scripts
python codigo/generar_informe_docx.py informes/Informe_avance_01.md   # Word con figuras
```

Requiere `pandas`, `numpy`, `matplotlib`, `openpyxl` y, para el Word, `python-docx` (probado con Python 3.12 y
pandas 3.0). El código localiza solo la raíz del proyecto (sube directorios hasta
encontrar `CLAUDE.md`), así que corre igual desde la raíz o desde `codigo/`. Toda
lectura de datos pasa por `codigo/comun.py`, que aplica las reglas de depuración
documentadas en `informes/Registro_hallazgos.md`.

No necesita Power BI: la extracción DAX está incluida pero comentada, y el análisis
corre sobre los CSV ya exportados. Para regenerarlos hay que abrir
`datos/crudos/GA05-Notas Credito.pbix` en Power BI Desktop y descomentar la llamada
a `extraer_devoluciones_dax`.

## Confidencialidad

Los datos de Postobón (ventas, colocación, devoluciones, vida útil, maestro de
tiendas, notas crédito) **no se versionan**. El `.gitignore` excluye `datos/`,
`figuras/`, `documentos/`, los extractos `.xlsx`/`.XLSX`, el modelo `.pbix`,
cualquier `.csv`, los informes HTML con cifras de la operación, y credenciales.
Los cuadernos se versionan sin salidas. Si el repositorio se sube a un remoto, debe
ser **privado**.
