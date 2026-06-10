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
        logger.info(f"[Timer] La función '{func.__name__}' se ejecutó en {end_time - start_time:.4f} segundos.")
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
            logger.debug(f"Lectura ya existe en base de datos. (Prevenido por UNIQUE constraint)")
        else:
            logger.error(f"Fallo al insertar lectura: {e}")

@timer_decorator
def batch_save_weather_readings(location_id: int, readings_list: list):
    """
    Inserta una lista de lecturas de clima en bloques para mayor velocidad.
    readings_list debe ser una lista de diccionarios ya formateados para la tabla 'weather_readings'.
    """
    if not readings_list:
        return
        
    supabase = get_supabase_client()
    
    # Preparar datos agregando location_id
    for r in readings_list:
        r["location_id"] = location_id

    # Insertar en bloques (chunks) de 1000 para no saturar la API de Supabase
    chunk_size = 1000
    for i in range(0, len(readings_list), chunk_size):
        chunk = readings_list[i:i + chunk_size]
        try:
            # upsert maneja los duplicados (necesita que haya constraint unique)
            supabase.table("weather_readings").upsert(chunk, ignore_duplicates=True).execute()
        except Exception as e:
            logger.error(f"Fallo al insertar bloque {i}-{i+len(chunk)}: {e}")

@timer_decorator
def batch_save_historical_data(historical_data: list):
    """
    Guarda una descarga masiva de historial resolviendo el location_id una sola vez
    y guardando en la base de datos usando bulk insert. Resuelve el problema N+1.
    """
    if not historical_data:
        return
        
    supabase = get_supabase_client()
    first = historical_data[0]
    
    # 1. Obtener location_id
    loc_id = _get_or_create_location(
        supabase, 
        first["latitude"], 
        first["longitude"], 
        first["city_name"], 
        first["country_code"]
    )
    
    # 2. Formatear para inserción
    clean_readings = []
    for r in historical_data:
        clean_readings.append({
            "timestamp": r["timestamp"],
            "temperature_c": r["temperature_c"],
            "humidity_pct": r["humidity_pct"],
            "wind_speed_kmh": r["wind_speed_kmh"],
            "weather_desc": r["weather_desc"]
        })
        
    # 3. Guardar todo en lote
    batch_save_weather_readings(loc_id, clean_readings)

@timer_decorator
def get_available_cities() -> list:
    """
    Recupera rápidamente la lista de ciudades disponibles directamente de la tabla locations.
    """
    supabase = get_supabase_client()
    response = supabase.table("locations").select("id, city_name, country_code").execute()
    return response.data

@timer_decorator
def get_historical_data(location_ids: list = None, start_date: str = None, end_date: str = None, limit: int = 5000) -> list:
    """
    Recupera el historial de datos climáticos empujando los filtros a Supabase.
    """
    supabase = get_supabase_client()
    query = supabase.table("weather_readings").select("*, locations!inner(city_name, country_code, latitude, longitude)")
    
    if location_ids and len(location_ids) > 0:
        query = query.in_("location_id", location_ids)
        
    if start_date:
        query = query.gte("timestamp", start_date)
    if end_date:
        query = query.lte("timestamp", end_date)
        
    # El limit protege de colapsos si se pide mucho rango para muchas ciudades a la vez.
    response = query.order("timestamp", desc=True).limit(limit).execute()
    return response.data
