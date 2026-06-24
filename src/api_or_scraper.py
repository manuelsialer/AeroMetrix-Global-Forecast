import os
import requests
import streamlit as st
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ValidationError
import logging

logger = logging.getLogger('AeroMetrix.API')

class WeatherResponse(BaseModel):
    city_name: str
    country_code: str
    latitude: float
    longitude: float
    timestamp: str
    temperature_c: float
    humidity_pct: float
    wind_speed_kmh: float
    weather_desc: str

@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather_data(city: str) -> dict:
    """
    Fetches current weather data for a given city from OpenWeatherMap.
    Returns a parsed dictionary containing relevant weather metrics, 
    validated strictly by Pydantic.
    """
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("WEATHER_API_KEY environment variable is not set.")

    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "es"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    try:
        # Validación estricta y casteo con Pydantic
        valid_data = WeatherResponse(
            city_name=data["name"],
            country_code=data.get("sys", {}).get("country", ""),
            latitude=data.get("coord", {}).get("lat", 0.0),
            longitude=data.get("coord", {}).get("lon", 0.0),
            timestamp=datetime.fromtimestamp(data["dt"], tz=timezone.utc).isoformat(),
            temperature_c=data.get("main", {}).get("temp", 0.0),
            humidity_pct=data.get("main", {}).get("humidity", 0.0),
            wind_speed_kmh=data.get("wind", {}).get("speed", 0.0) * 3.6,
            weather_desc=data.get("weather", [{}])[0].get("description", "Desconocido").capitalize()
        )
        return valid_data.model_dump()
    except ValidationError as e:
        logger.error(f"Error de validación de datos desde OpenWeatherMap: {e}")
        raise ValueError("La API devolvió datos en un formato inesperado o corrupto.")

WMO_CODES = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna leve",
    53: "Llovizna moderada",
    55: "Llovizna densa",
    56: "Llovizna helada leve",
    57: "Llovizna helada densa",
    61: "Lluvia leve",
    63: "Lluvia moderada",
    65: "Lluvia fuerte",
    66: "Lluvia helada leve",
    67: "Lluvia helada fuerte",
    71: "Nieve leve",
    73: "Nieve moderada",
    75: "Nieve fuerte",
    77: "Granos de nieve",
    80: "Chubascos leves",
    81: "Chubascos moderados",
    82: "Chubascos violentos",
    85: "Chubascos de nieve leves",
    86: "Chubascos de nieve fuertes",
    95: "Tormenta eléctrica",
    96: "Tormenta con granizo leve",
    99: "Tormenta con granizo fuerte"
}

def fetch_historical_data_open_meteo(city: str, start_date: str, end_date: str) -> list:
    """
    Fetches historical hourly weather data for a given city from Open-Meteo.
    Uses OpenWeatherMap once to get the exact coordinates of the city.
    """
    # 1. Obtener coordenadas actuales de la ciudad
    current_data = fetch_weather_data(city)
    lat = current_data["latitude"]
    lon = current_data["longitude"]
    city_name = current_data["city_name"]
    country_code = current_data["country_code"]

    # 2. Consultar Open-Meteo Archive API
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "timezone": "UTC"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # 3. Formatear la respuesta
    historical_readings = []
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    hums = hourly.get("relative_humidity_2m", [])
    winds = hourly.get("wind_speed_10m", [])
    codes = hourly.get("weather_code", [])

    for i in range(len(times)):
        if temps[i] is None:
            continue
            
        dt = datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc).isoformat()
        code = codes[i] if codes[i] is not None else 0
        desc = WMO_CODES.get(code, "Desconocido")
        
        reading = {
            "city_name": city_name,
            "country_code": country_code,
            "latitude": lat,
            "longitude": lon,
            "timestamp": dt,
            "temperature_c": temps[i],
            "humidity_pct": hums[i],
            "wind_speed_kmh": winds[i],
            "weather_desc": desc
        }
        historical_readings.append(reading)
        
    return historical_readings
