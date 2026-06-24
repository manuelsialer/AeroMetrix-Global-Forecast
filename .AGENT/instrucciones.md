Características del proyecto
Guía del Proyecto – Programación Avanzada para la Ciencia de Datos
1) Objetivo
Desarrollar una app en Streamlit para ciencia de datos que:
(Parcial) cargue y procese archivos .csv y muestre un prototipo de dashboard.
(Final) incorpore datos externos (API o scraping), persistencia en SQL y un dashboard interactivo completo.
2) Entregables y cronograma (resumen)
Entrega Parcial (40%)
Enfoque: CSV + procesamiento básico + prototipo Streamlit.
Entrega: Documento breve (máx. 4 páginas) + repo GitHub público.
Entrega Final (60%)
Enfoque: API/scraping + SQL + dashboard completo + manejo de errores y decoradores.
Entrega: Documento técnico (máx. 10 páginas) + repo GitHub público + app funcional.
3) Requerimientos mínimos por etapa
3.1) Parcial (40%)
Debe incluir:

Datos:
Carga de uno o más .csv (citar fuente y licencia si corresponde).
Breve descripción de la procedencia y variables clave.
Procesamiento básico:
Limpieza (faltantes, tipos, duplicados).
Métricas descriptivas (promedios, conteos, etc.).
Prototipo Streamlit:
Visualización en tabla.
≥ 1 gráfico sencillo (barras, histograma, línea, etc.).
≥ 1 control (selector de columna, rango, categoría).
Referencias (1–2):
Apps, repos o artículos que el equipo busca imitar en parte (1–2 líneas de justificación).
Repositorio GitHub (público):
Código + README.md con pasos para ejecutar (local).
Puede incluir (opcional):

Pruebas unitarias de funciones de carga/procesamiento.
Esquema inicial de carpetas para escalar a la entrega final.
Checklist (Parcial):

Cito la fuente de los .csv.
Limpieza y métricas descriptivas implementadas.
Tabla + 1 gráfico en Streamlit.
1 control de usuario funcional.
Referencias (1–2) con breve justificación.
Repo público con README.md (instrucciones para correr localmente).
3.2) Final (60%)
Debe incluir:

Datos externos:
API (endpoints, auth, rate limits) o web scraping responsable.
Persistencia:
SQLite o SQL equivalente.
Esquema (≥ 2 tablas relacionadas recomendado) y consultas integradas.
Procesamiento/Análisis:
Transformaciones relevantes; opcional: modelo simple (regresión, clustering, etc.).
Streamlit (dashboard completo):
Varias visualizaciones interactivas (navegación clara).
Múltiples controles que afecten consultas y gráficos.
Indicadores/KPIs si aplica.
Calidad de código:
Manejo de errores con try/except.
Decoradores para logging/tiempos/debug (al menos uno).
Estructura modular de paquetes/módulos.
Documento técnico (máx. 10 págs.):
Flujo de datos (API/scraping → SQL → dashboard).
Diseño de base de datos.
Evidencias y capturas (con explicación).
Limitaciones y mejoras.
Repositorio GitHub (público):
Código final, README.md con dependencias e instrucciones de despliegue (local o Streamlit Cloud).
Puede incluir (opcional):

Cachés (ej. st.cache_data) con invalidación controlada.
Pruebas unitarias para funciones críticas.
Linter/formateo (flake8/ruff + black).
Checklist (Final):

API o scraping funcional documentado.
SQL (SQLite) con esquema + consultas.
Dashboard completo con múltiples visualizaciones.
Controles que cambian consultas y gráficos.
Manejo de errores y decoradores implementados.
Documento técnico (flujo, DB, capturas, mejoras).
Repo público con instrucciones de instalación y ejecución (local/Cloud).
4) Estructura sugerida del repositorio (ambas entregas)
 
project-root/
├── README.md
├── requirements.txt
├── data/                # CSV (parcial) + dumps/exports (final)
├── src/
│   ├── app.py           # entrada de Streamlit
│   ├── processing.py    # limpieza/transformaciones
│   ├── viz.py           # funciones de graficación
│   ├── api_or_scraper.py# (solo final)
│   └── db.py            # (solo final) conexión y consultas SQL
├── docs/
│   ├── parcial.pdf
│   └── final.pdf
└── tests/               # opcional
 
 
5) Reglas de citación y uso de recursos
Citar fuentes de datos y trabajos de inspiración (URL y descripción breve).
Indicar licencias si aplica (datos/imágenes/logos).
Si usan IA (p. ej., para refactor o documentación), declarar: herramienta, versión y qué partes asistió.
6) Rúbricas de evaluación
6.1) Entrega Parcial (40%)
Criterio

Excelente (100%)

Aceptable (70%)

Deficiente (40%)

Obtención de datos

.csv bien seleccionados y explicados

Archivos básicos, poca justificación

Sin datos claros

Procesamiento básico

Limpieza y métricas correctas

Procesamiento mínimo o superficial

Inexistente

Dashboard inicial

Tabla + ≥1 gráfico claro

Visualización muy simple

Sin visualización

Control de usuario

Control funcional y relevante

Control básico o poco útil

Sin control

Referencias

Pertinentes y bien justificadas

Referencias poco claras

Ausentes

Repo GitHub

Público, organizado, con README.md útil

Público pero poco documentado

Inexistente o privado



6.2) Entrega Final (60%)
Criterio

Excelente (100%)

Aceptable (70%)

Deficiente (40%)

Obtención de datos

API/scraping estable, documentado

Flujo parcial o poco robusto

No funciona

Persistencia en SQL

Esquema y consultas correctas e integradas

Base mínima o poco documentada

No existe

Procesamiento/análisis

Relevante y bien documentado

Básico o superficial

Inexistente

Dashboard Streamlit

Completo, interactivo, navegable

Funcional pero limitado

Fallido o incompleto

Controles de usuario

Varios y útiles

Uno o pocos

Ninguno

Errores/decoradores

try/except robusto y decoradores útiles

Implementación parcial o superficial

Ausentes

Documento técnico

Completo, claro y crítico

Parcial o poco detallado

Escaso

Repo GitHub

Público, limpio, bien documentado

Público con fallos de documentación

Desordenado o privado



7) Formato de entrega en Blackboard
Subir:
En Parcial: PDF (máx. 4 págs.) + enlace al repo público.
En Final: PDF (máx. 10 págs.) + enlace al repo público + URL de la app (si despliegan en Streamlit Cloud).
Nombre de archivo sugerido:
Parcial_ProgAvanzada_GrupoX.pdf
Final_ProgAvanzada_GrupoX.pdf
Dentro del PDF incluir en la portada**: curso, sección, integrantes, emails, fecha y nombre del proyecto.
8) Criterios de integridad académica
Trabajo original del equipo, con citación de todo recurso externo.
No se permite copiar código sin referencia.
Uso de IA permitido solo si se declara (qué, cómo y por qué); el equipo sigue siendo responsable del código.