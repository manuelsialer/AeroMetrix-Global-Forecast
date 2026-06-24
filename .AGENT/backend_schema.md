# Backend Schema (Supabase / PostgreSQL)

Para este proyecto de ciencia de datos, se propone un esquema relacional con dos tablas conectadas para cumplir con el requerimiento de SQL con relaciones, optimizando el almacenamiento y las consultas del dashboard.

## Tabla 1: `locations` (Dimensión)
Almacena la información de las ciudades o puntos de interés geográficos consultados.

| Columna | Tipo de Dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | PRIMARY KEY | Identificador único de la ubicación |
| `city_name` | `VARCHAR(100)` | NOT NULL | Nombre de la ciudad (ej. Lima, Madrid) |
| `country_code` | `VARCHAR(2)` | | Código ISO de país |
| `latitude` | `DECIMAL(9,6)` | NOT NULL | Latitud |
| `longitude` | `DECIMAL(9,6)`| NOT NULL | Longitud |

## Tabla 2: `weather_readings` (Hechos)
Almacena las métricas climáticas a lo largo del tiempo para cada ubicación.

| Columna | Tipo de Dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | PRIMARY KEY | Identificador único del registro |
| `location_id` | `UUID` / `INT` | FOREIGN KEY | Referencia a `locations(id)` |
| `timestamp` | `TIMESTAMP` | NOT NULL | Fecha y hora de la medición |
| `temperature_c`| `DECIMAL(5,2)` | | Temperatura en grados Celsius |
| `humidity_pct` | `INT` | | Humedad relativa en porcentaje |
| `wind_speed_kmh`| `DECIMAL(5,2)` | | Velocidad del viento en km/h |
| `weather_desc` | `VARCHAR(100)` | | Descripción corta (ej. "Lluvia ligera") |

## Relaciones e Índices Recomendados
- **Relación (Foreign Key)**: `weather_readings.location_id` hace referencia a `locations.id` (Relación 1 a N).
- **Índice**: Crear un índice en `weather_readings(location_id, timestamp)` para acelerar las consultas temporales del dashboard.
- **Restricción de Unicidad**: Para evitar duplicar datos al actualizar desde la API, se recomienda crear una restricción `UNIQUE(location_id, timestamp)` en la tabla `weather_readings`, permitiendo usar `INSERT ... ON CONFLICT DO NOTHING` u operaciones `UPSERT` en Supabase.
