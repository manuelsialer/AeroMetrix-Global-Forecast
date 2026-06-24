# Flujo de la Aplicación

## 1. Flujo de Datos (Backend / Pipeline)
1. **Disparador (Trigger)**: Puede ser automático (al iniciar la aplicación si no existen datos recientes en la BD) o manual (al hacer clic en un botón de actualizar en la UI).
2. **Extracción (Extract)**: El módulo `api_or_scraper.py` solicita los datos actuales y/o históricos a la API de Clima usando los parámetros correspondientes de ciudad/coordenadas.
3. **Transformación (Transform)**: El módulo `processing.py` recibe el objeto JSON o diccionario, lo aplana, limpia valores nulos, estandariza nombres de columnas y convierte los tipos de datos en un DataFrame de Pandas estructurado.
4. **Carga (Load)**: El módulo `db.py` recibe el DataFrame procesado, se conecta a Supabase y realiza inserciones (`INSERT` o `UPSERT` para evitar duplicados) en las tablas de PostgreSQL.

## 2. Flujo de Usuario (Frontend / Interacción)
1. **Carga Inicial**: El usuario accede a la URL de la aplicación de Streamlit.
2. **Lectura de Base de Datos**: `app.py` hace una solicitud de lectura a Supabase (a través de `db.py`) para popular los controles de la interfaz (ej. la lista de ciudades disponibles en la BD). Estos resultados usan `@st.cache_data` para carga instantánea.
3. **Interacción del Usuario**: 
   - El usuario selecciona la ciudad de "Lima" y ajusta el rango de fechas a "Últimos 7 días" en la barra lateral.
   - El usuario escoge ver la métrica de "Temperatura".
4. **Consulta SQL Dinámica**: Streamlit detecta el cambio en los widgets. Se llama a la función de consulta en `db.py` pasando los parámetros seleccionados, lo que ejecuta un `SELECT` con filtros `WHERE` en la BD de Supabase.
5. **Renderizado de Visualizaciones**: Los datos devueltos se pasan a `viz.py`, que genera los objetos gráficos de Plotly o Altair.
6. **Despliegue Final**: La pantalla principal muestra los KPIs actualizados y los gráficos reflejando los filtros aplicados.
