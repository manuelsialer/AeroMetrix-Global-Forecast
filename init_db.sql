-- Crear tabla locations
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(2),
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    UNIQUE(city_name, country_code)
);

-- Crear tabla weather_readings
CREATE TABLE IF NOT EXISTS weather_readings (
    id SERIAL PRIMARY KEY,
    location_id INT REFERENCES locations(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature_c DECIMAL(5,2),
    humidity_pct INT,
    wind_speed_kmh DECIMAL(5,2),
    weather_desc VARCHAR(100),
    UNIQUE(location_id, timestamp)
);

-- Crear índice para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_weather_location_time ON weather_readings(location_id, timestamp);
