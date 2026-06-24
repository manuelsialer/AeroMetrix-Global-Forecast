# Product Requirements Document (PRD)

## 1. Objetivo del Producto
Desarrollar una aplicación de panel de control (dashboard) interactiva utilizando Streamlit para el análisis y visualización de datos climáticos. La aplicación consumirá datos de una API de clima externa, los almacenará en una base de datos SQL alojada en Supabase y presentará visualizaciones dinámicas a los usuarios. Este producto corresponde a la entrega final del curso "Programación Avanzada para la Ciencia de Datos".

## 2. Público Objetivo
- Profesores y evaluadores del curso.
- Usuarios interesados en consultar el clima histórico o actual de diferentes ciudades con métricas clave.

## 3. Casos de Uso
1. **Consulta de Clima Actual e Histórico**: El usuario ingresa a la aplicación y selecciona una ciudad para ver sus condiciones climáticas.
2. **Comparación de Métricas**: El usuario utiliza controles interactivos para cambiar el tipo de gráfico o la métrica (ej. temperatura vs humedad).
3. **Actualización de Datos**: El sistema obtiene nuevos datos de la API de clima de manera transparente para el usuario y los guarda en Supabase.

## 4. Requerimientos Funcionales
- **Integración de API de Clima**: Obtener datos climáticos (temperatura, humedad, velocidad del viento, etc.) mediante una API pública (ej. OpenWeatherMap, WeatherAPI).
- **Almacenamiento (Persistencia)**: Guardar los datos obtenidos en una base de datos PostgreSQL alojada en Supabase.
- **Panel de Control (Dashboard)**: Interfaz gráfica construida en Streamlit.
- **Controles de Usuario**: Filtros interactivos (ej. selección de ciudad, rango de fechas, selección de métricas) que modifiquen las consultas SQL y actualicen los gráficos en tiempo real.
- **Visualizaciones**: Al menos dos tipos de gráficos diferentes (ej. líneas para tendencias temporales, barras para comparaciones) y KPIs numéricos.

## 5. Requerimientos No Funcionales
- **Calidad de Código**: Uso de modularidad (separación en archivos como `app.py`, `db.py`, etc.).
- **Manejo de Errores**: Bloques `try/except` robustos, especialmente en las llamadas a la API y la conexión a la base de datos.
- **Decoradores**: Implementar al menos un decorador personalizado (ej. para medir el tiempo de ejecución de las consultas o para registrar logs).
- **Desempeño**: Uso de caché de Streamlit (`@st.cache_data`) para optimizar cargas repetitivas.
