import os
import time
from functools import wraps
from supabase import create_client, Client

def timer_decorator(func):
    """
    Un decorador personalizado para medir el tiempo de ejecución 
    de las operaciones de la base de datos (Requerimiento del proyecto).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[Timer] La función '{func.__name__}' se ejecutó en {end_time - start_time:.4f} segundos.")
        return result
    return wrapper

def get_supabase_client() -> Client:
    """
    Inicializa y retorna el cliente de Supabase.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en las variables de entorno.")
    return create_client(url, key)

@timer_decorator
def save_weather_data(weather_data: dict):
    """
    Guarda los datos del clima en la base de datos de Supabase.
    Maneja la inserción en 'locations' y 'weather_readings'.
    """
    supabase = get_supabase_client()
    
    # 1. Insertar o recuperar location
    location_resp = supabase.table("locations").select("id").eq("city_name", weather_data["city_name"]).eq("country_code", weather_data["country_code"]).execute()
    
    if len(location_resp.data) > 0:
        location_id = location_resp.data[0]["id"]
    else:
        # Insertar nueva location
        insert_loc_resp = supabase.table("locations").insert({
            "city_name": weather_data["city_name"],
            "country_code": weather_data["country_code"],
            "latitude": weather_data["latitude"],
            "longitude": weather_data["longitude"]
        }).execute()
        location_id = insert_loc_resp.data[0]["id"]

    # 2. Insertar weather reading
    try:
        supabase.table("weather_readings").insert({
            "location_id": location_id,
            "timestamp": weather_data["timestamp"],
            "temperature_c": weather_data["temperature_c"],
            "humidity_pct": weather_data["humidity_pct"],
            "wind_speed_kmh": weather_data["wind_speed_kmh"],
            "weather_desc": weather_data["weather_desc"]
        }).execute()
    except Exception as e:
        error_str = str(e)
        if '23505' in error_str:
            print(f"    [INFO] Lectura ya existe en base de datos. (Prevenido por UNIQUE constraint)")
        else:
            print(f"    [ERROR] Fallo al insertar lectura: {e}")

@timer_decorator
def get_historical_data(city_name: str = None) -> list:
    """
    Recupera el historial de datos climáticos.
    """
    supabase = get_supabase_client()
    query = supabase.table("weather_readings").select("*, locations!inner(city_name, country_code, latitude, longitude)")
    
    if city_name:
        query = query.eq("locations.city_name", city_name)
        
    response = query.order("timestamp", desc=True).execute()
    return response.data
