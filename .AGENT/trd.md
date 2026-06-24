# Technical Requirements Document (TRD)

## 1. Arquitectura del Sistema
El sistema sigue una arquitectura de 3 capas:
1. **Frontend / UI**: Streamlit (Python).
2. **Backend / Lógica**: Scripts de Python modulares para recolección de datos y procesamiento.
3. **Base de Datos**: PostgreSQL alojado en Supabase.

## 2. Tecnologías y Herramientas
- **Lenguaje**: Python 3.9+
- **Librerías Principales**: `streamlit`, `pandas`, `requests`, `supabase`, `python-dotenv`, `plotly` o `altair` (para gráficos).
- **Base de Datos**: Supabase (PostgreSQL).
- **Control de Versiones**: Git & GitHub.
- **Formateo y Linter**: `black`, `flake8` o `ruff`.

## 3. Integración de API (Data Pipeline)
- **Fuente**: API de Clima (ej. OpenWeatherMap).
- **Proceso**: Un módulo dedicado (`api_or_scraper.py`) hará solicitudes GET a la API, manejará la paginación o límites de tasa (rate limits), y parseará la respuesta JSON a un DataFrame de Pandas o diccionarios nativos.
- **Autenticación**: Clave de API almacenada de forma segura en `.streamlit/secrets.toml` o `.env`.

## 4. Estructura del Repositorio
```text
project-root/
├── README.md
├── requirements.txt
├── .env / .streamlit/secrets.toml
├── src/
│   ├── app.py           # Entrada principal de Streamlit
│   ├── processing.py    # Limpieza y transformaciones de datos
│   ├── viz.py           # Funciones de graficación
│   ├── api_or_scraper.py# Conexión y peticiones a la API de clima
│   └── db.py            # Conexión y consultas a Supabase
└── docs/
    └── final.pdf        # Documento técnico final
```

## 5. Manejo de Errores y Decoradores
- **Manejo de Errores**: Uso exhaustivo de `try/except` en `api_or_scraper.py` (para errores de red/timeout) y `db.py` (para errores de conexión o integridad de SQL).
- **Decoradores**: 
  - `@time_logger`: Para medir y mostrar en la terminal el tiempo que toma hacer la petición a la API.
  - `@error_handler_decorator`: Para capturar excepciones no controladas y registrarlas sin romper la aplicación de Streamlit.
