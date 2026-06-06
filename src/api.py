import os
import requests
from datetime import datetime, timezone

def fetch_weather_data(city: str) -> dict:
    """
    Fetches current weather data for a given city from OpenWeatherMap.
    Returns a parsed dictionary containing relevant weather metrics.
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
    response.raise_for_status()  # Lanza una excepción si hay un error HTTP
    
    data = response.json()
    
    return {
        "city_name": data["name"],
        "country_code": data["sys"]["country"],
        "latitude": data["coord"]["lat"],
        "longitude": data["coord"]["lon"],
        "timestamp": datetime.fromtimestamp(data["dt"], tz=timezone.utc).isoformat(),
        "temperature_c": data["main"]["temp"],
        "humidity_pct": data["main"]["humidity"],
        "wind_speed_kmh": data["wind"]["speed"] * 3.6, # Convert m/s to km/h
        "weather_desc": data["weather"][0]["description"].capitalize()
    }
