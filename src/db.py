import os
import time
import logging
from functools import wraps
from dotenv import load_dotenv
from supabase import create_client, Client

# Configuración central de variables de entorno y logger
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AeroMetrix.DB')

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("No se encontraron las credenciales de Supabase en el .env (SUPABASE_URL o SUPABASE_KEY).")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.error(f"Fallo al inicializar el cliente de Supabase: {e}")
    supabase = None

def timer_decorator(func):
    """
    Decorador personalizado para medir el tiempo de ejecución 
    de las operaciones de la base de datos (Requerimiento del proyecto).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"[Timer] La función '{func.__name__}' se ejecutó en {end_time - start_time:.4f} segundos.")
        return result
    return wrapper

@timer_decorator
def save_weather_data(weather_data: dict):
    """
    Guarda los datos del clima en Supabase.
    Maneja la inserción en 'locations' y 'weather_readings' usando upsert.
    """
    if not supabase: return
    
    try:
        # 1. Insertar o recuperar location
        loc_res = supabase.table('locations').upsert({
            "city_name": weather_data["city_name"],
            "country_code": weather_data["country_code"],
            "latitude": weather_data["latitude"],
            "longitude": weather_data["longitude"]
        }, on_conflict="city_name,country_code").execute()
        
        if not loc_res.data:
            logger.error("No se pudo obtener el ID de la ubicación tras el upsert.")
            return
            
        location_id = loc_res.data[0]['id']
        
        # 2. Insertar weather reading
        supabase.table('weather_readings').upsert({
            "location_id": location_id,
            "timestamp": weather_data["timestamp"],
            "temperature_c": weather_data["temperature_c"],
            "humidity_pct": weather_data["humidity_pct"],
            "wind_speed_kmh": weather_data["wind_speed_kmh"],
            "weather_desc": weather_data["weather_desc"]
        }, on_conflict="location_id,timestamp").execute()
        
    except Exception as e:
        logger.error(f"Fallo al insertar lectura en Supabase: {e}")

def _get_or_create_location(lat, lon, city_name, country_code):
    """Método interno auxiliar para obtener/crear location en Supabase."""
    loc_res = supabase.table('locations').upsert({
        "city_name": city_name,
        "country_code": country_code,
        "latitude": lat,
        "longitude": lon
    }, on_conflict="city_name,country_code").execute()
    
    if loc_res.data:
        return loc_res.data[0]['id']
    raise ValueError("Fallo al crear o recuperar location ID")

@timer_decorator
def batch_save_weather_readings(location_id: int, readings_list: list):
    """Inserta una lista de lecturas de clima en bloques usando Supabase (bulk upsert)."""
    if not supabase or not readings_list:
        return
        
    data_to_insert = [
        {
            "location_id": location_id,
            "timestamp": r["timestamp"],
            "temperature_c": r["temperature_c"],
            "humidity_pct": r["humidity_pct"],
            "wind_speed_kmh": r["wind_speed_kmh"],
            "weather_desc": r["weather_desc"]
        } for r in readings_list
    ]
    
    try:
        # bulk upsert previene fallos por duplicados
        supabase.table('weather_readings').upsert(data_to_insert, on_conflict="location_id,timestamp").execute()
    except Exception as e:
        logger.error(f"Fallo al insertar bloque en Supabase: {e}")

@timer_decorator
def batch_save_historical_data(historical_data: list):
    """Guarda una descarga masiva resolviendo el location_id una sola vez."""
    if not historical_data:
        return
        
    first = historical_data[0]
    
    try:
        loc_id = _get_or_create_location(
            first["latitude"], 
            first["longitude"], 
            first["city_name"], 
            first["country_code"]
        )
        batch_save_weather_readings(loc_id, historical_data)
    except Exception as e:
        logger.error(f"Error en batch_save_historical_data: {e}")

@timer_decorator
def get_available_cities() -> list:
    """Recupera rápidamente la lista de ciudades disponibles directamente de Supabase."""
    if not supabase: return []
    try:
        res = supabase.table('locations').select('id, city_name, country_code').execute()
        return res.data if res.data else []
    except Exception as e:
        logger.error(f"Fallo al obtener ciudades disponibles: {e}")
        return []

@timer_decorator
def get_historical_data(location_ids: list = None, start_date: str = None, end_date: str = None, limit: int = 5000) -> list:
    """
    Recupera el historial de datos climáticos usando un foreign table join en Supabase.
    La estructura retornada empaqueta automáticamente los datos en la llave 'locations'
    gracias a PostgREST.
    """
    if not supabase: return []
    try:
        query = supabase.table('weather_readings').select('*, locations!inner(city_name, country_code, latitude, longitude)')
        
        if location_ids and len(location_ids) > 0:
            query = query.in_('location_id', location_ids)
            
        if start_date:
            query = query.gte('timestamp', start_date)
            
        if end_date:
            query = query.lte('timestamp', end_date)
            
        res = query.order('timestamp', desc=True).limit(limit).execute()
        return res.data if res.data else []
    except Exception as e:
        logger.error(f"Fallo al recuperar historial: {e}")
        return []
