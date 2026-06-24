# Plan de Implementación

Este plan detalla los pasos secuenciales para llevar a cabo el proyecto, abarcando desde la inicialización del entorno hasta el despliegue final.

## Fase 1: Configuración del Entorno y Repositorio
- [ ] Inicializar repositorio local de Git y crear repositorio público en GitHub.
- [ ] Crear archivo `.gitignore` (excluir archivos `.env`, carpetas `__pycache__`, entornos virtuales).
- [ ] Configurar el entorno virtual de Python.
- [ ] Instalar dependencias iniciales (`streamlit`, `pandas`, `requests`, `supabase`, `python-dotenv`, `plotly`) y generar el archivo `requirements.txt`.
- [ ] Crear la estructura de carpetas (`src/`, `data/`, `docs/`, `tests/`).

## Fase 2: Configuración de la Base de Datos (Supabase)
- [ ] Crear una cuenta o iniciar sesión en Supabase y crear un nuevo proyecto.
- [ ] Ejecutar scripts SQL para crear las tablas `locations` y `weather_readings` (definidas en `backend_schema.md`).
- [ ] Obtener la URL del proyecto y la API Key (Anon/Service Role).
- [ ] Configurar las claves en un archivo `.env` para uso local y en `.streamlit/secrets.toml` para compatibilidad con Streamlit.

## Fase 3: Ingesta de Datos e Integración de API
- [ ] Seleccionar API de clima (ej. OpenWeatherMap) y obtener una API Key gratuita.
- [ ] **`src/api_or_scraper.py`**: Escribir funciones para conectarse a la API, usando bloques `try/except` para manejar errores de conexión o HTTP (ej. límite de peticiones).
- [ ] **`src/processing.py`**: Desarrollar funciones para limpiar la respuesta JSON de la API y convertirla en DataFrames tabulares adecuados para la BD.
- [ ] **`src/db.py`**: Integrar el cliente de Supabase (librería de Python). Crear funciones para realizar las inserciones o actualizaciones de los datos.
- [ ] Implementar decoradores personalizados (ej. `@time_logger`) en las peticiones a la API o BD.

## Fase 4: Desarrollo de la Interfaz con Streamlit
- [ ] **`src/app.py`**: Crear el esqueleto de la aplicación y la barra lateral de configuración (filtros).
- [ ] Integrar `src/db.py` en `app.py` para leer los datos usando operaciones SQL dinámicas basadas en los filtros seleccionados por el usuario.
- [ ] **`src/viz.py`**: Desarrollar funciones para renderizar gráficos (Líneas para temperaturas, Barras para viento, etc.) usando Plotly, invocadas desde `app.py`.
- [ ] Implementar `st.metric` para la vista de los KPIs de manera dinámica.

## Fase 5: Refinamiento y Control de Calidad
- [ ] Implementar manejo de errores visuales (ej. `st.error` y `st.warning`) en caso de que las consultas fallen o no haya datos.
- [ ] Integrar caché explícito mediante `@st.cache_data` en las funciones que lean de la base de datos para no saturar Supabase durante el filtrado en UI.
- [ ] Auditar el código usando linters y formateadores (Black/Ruff).

## Fase 6: Documentación y Entrega Final
- [ ] Redactar el documento técnico final (máx 10 páginas) incluyendo el flujo de datos, diseño de base de datos, capturas y explicaciones, además de limitaciones o mejoras futuras.
- [ ] Documentar el archivo `README.md` con instrucciones claras para clonar, instalar dependencias, configurar el `.env` y correr el comando `streamlit run src/app.py`.
- [ ] (Opcional) Desplegar la aplicación final en Streamlit Community Cloud para facilitar el acceso a la entrega.
