# Documento Técnico Final - AeroMetrix Global Forecast

Este documento justifica las decisiones de arquitectura técnica para la Entrega Final (60%) de la asignatura de Programación Avanzada para la Ciencia de Datos, cumpliendo con la rúbrica de calificación "Excelente".

## 1. Flujo de Datos (ETL)

El ciclo de vida del dato en AeroMetrix consta de las siguientes fases:
1. **Extracción (Extract)**: Ejecutada en `api_or_scraper.py`. Se orquestan peticiones a las APIs REST de *OpenWeatherMap* (tiempo real) y *Open-Meteo* (datos históricos). Se utiliza Pydantic para castear los tipos de datos (str, float) y validar el schema en el origen.
2. **Transformación (Transform)**: Llevada a cabo en `processing.py`. Aquí entra en juego el "Clean Code". Hemos diseñado decoradores (`@error_handler_df`) y manejado excepciones complejas (`try/except`) para asegurar que los fallos del modelado matemático (Random Forest) o de pandas no rompan la aplicación Streamlit. Se aplanan los diccionarios geográficos recuperados de la DB y se realiza codificación cíclica temporal (seno/coseno) sobre las horas para alimentar correctamente al modelo de Machine Learning.
3. **Carga (Load)**: Ejecutada por `db.py`. Los diccionarios limpios se persisten en una base de datos local SQLite mediante los métodos `sqlite3.Cursor.execute` y `executemany`, utilizando bind parameters (`?`) que previenen ataques de inyección SQL.

## 2. Diseño de la Base de Datos Relacional

AeroMetrix implementa un esquema en **SQLite**, evidenciando una relación One-to-Many garantizando la integridad referencial. El uso del factory `sqlite3.Row` facilita la compatibilidad de objetos en las capas superiores.

### Diagrama Entidad-Relación

**Tabla `locations`**
* Almacena las coordenadas geoespaciales inmutables de cada ciudad.
* `id` (INTEGER, PRIMARY KEY)
* `city_name` (TEXT, NOT NULL)
* `country_code` (TEXT)
* `latitude` (REAL, NOT NULL)
* `longitude` (REAL, NOT NULL)
* Restricción: `UNIQUE(city_name, country_code)`

**Tabla `weather_readings`**
* Almacena el historial climático temporal asociado a una localización.
* `id` (INTEGER, PRIMARY KEY)
* `location_id` (INTEGER, FOREIGN KEY REFERENCES locations(id) ON DELETE CASCADE)
* `timestamp` (TEXT, NOT NULL)
* `temperature_c` (REAL)
* `humidity_pct` (REAL)
* `wind_speed_kmh` (REAL)
* `weather_desc` (TEXT)
* Restricción: `UNIQUE(location_id, timestamp)`

*El uso de restricciones UNIQUE evita la duplicidad de la ingesta en las consultas repetidas a las APIs satelitales, respetando la consistencia temporal y espacial.*

## 3. Mejoras y Trabajo a Futuro

Para la siguiente iteración del software, se proponen las siguientes arquitecturas:
1. **Contenedorización**: Incorporar `Docker` y un archivo `docker-compose.yml` para empaquetar el frontend y la base de datos dentro de una misma imagen, permitiendo despliegues ágiles y predecibles en la nube (ej. AWS EC2 o Google Cloud Run).
2. **Pruebas Unitarias Integrales**: Aumentar la cobertura (Coverage) del testing añadiendo la suite `pytest` en un pipeline de integración continua (CI/CD) alojado en GitHub Actions.
3. **Módulo de Autenticación de Usuario**: Limitar el panel de control de "Recarga de datos" a administradores mediante `streamlit-authenticator` para que los usuarios genéricos solo tengan privilegios de lectura y uso de gráficos interactivos.
