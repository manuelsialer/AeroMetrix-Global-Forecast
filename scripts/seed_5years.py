import sys
import os
import time
from datetime import datetime, timedelta

# Añadir la carpeta src al path para poder importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dotenv import load_dotenv
load_dotenv()

from api import fetch_weather_data, fetch_historical_data_open_meteo
from db import get_supabase_client, batch_save_weather_readings

# 30 ciudades preformateadas (las originales del proyecto)
CITIES_TO_SEED = [
    "Madrid", "Barcelona", "Valencia", "Sevilla",
    "Lima", "Cusco", "Arequipa", "Piura",
    "Ciudad de Mexico", "Guadalajara", "Monterrey", "Cancun",
    "Buenos Aires", "Cordoba", "Rosario", "Mendoza",
    "Bogota", "Medellin", "Cali", "Cartagena",
    "Santiago", "Valparaiso", "Concepcion",
    "New York", "Los Angeles", "Miami", "Chicago",
    "Paris", "Marseille", "Lyon"
]

def seed_city(city_name: str, start_date: str, end_date: str):
    print(f"\n--- Iniciando siembra para {city_name} ---")
    
    # 1. Obtener location usando API 1 (OpenWeatherMap)
    try:
        current_data = fetch_weather_data(city_name)
    except Exception as e:
        print(f"[ERROR] No se pudo obtener coordenadas de {city_name}: {e}")
        return
        
    supabase = get_supabase_client()
    
    # 2. Asegurar que exista la location en BD
    location_resp = supabase.table("locations").select("id").eq("city_name", current_data["city_name"]).eq("country_code", current_data["country_code"]).execute()
    
    if len(location_resp.data) > 0:
        location_id = location_resp.data[0]["id"]
    else:
        insert_loc_resp = supabase.table("locations").insert({
            "city_name": current_data["city_name"],
            "country_code": current_data["country_code"],
            "latitude": current_data["latitude"],
            "longitude": current_data["longitude"]
        }).execute()
        location_id = insert_loc_resp.data[0]["id"]
        
    print(f"Location ID resuelto: {location_id} ({current_data['country_code']})")
    
    # 3. Consultar API 2 (Open-Meteo) para 5 años
    print(f"Descargando datos históricos desde {start_date} hasta {end_date}...")
    try:
        historical_data = fetch_historical_data_open_meteo(city_name, start_date, end_date)
    except Exception as e:
        print(f"[ERROR] Fallo Open-Meteo para {city_name}: {e}")
        return
        
    total_records = len(historical_data)
    print(f"Descargados {total_records} registros horarios.")
    
    if total_records == 0:
        return
        
    # 4. Formatear para batch insert (quitar llaves extrañas, solo dejar columnas de BD)
    clean_readings = []
    for r in historical_data:
        clean_readings.append({
            "timestamp": r["timestamp"],
            "temperature_c": r["temperature_c"],
            "humidity_pct": r["humidity_pct"],
            "wind_speed_kmh": r["wind_speed_kmh"],
            "weather_desc": r["weather_desc"]
        })
        
    # 5. Guardado masivo
    print(f"Iniciando guardado por bloques (batch insert)...")
    batch_save_weather_readings(location_id, clean_readings)
    print(f"¡Éxito! {city_name} completado.")

def main():
    end_date_obj = datetime.today()
    start_date_obj = end_date_obj - timedelta(days=5 * 365) # 5 años atrás
    
    start_str = start_date_obj.strftime("%Y-%m-%d")
    end_str = end_date_obj.strftime("%Y-%m-%d")
    
    print(f"=== COMENZANDO SEED MASIVO ===")
    print(f"Período: {start_str} al {end_str}")
    print(f"Total ciudades a procesar: {len(CITIES_TO_SEED)}\n")
    
    for city in CITIES_TO_SEED:
        seed_city(city, start_str, end_str)
        time.sleep(1) # Pausa breve para evitar Rate Limits (429) de las APIs gratuitas

    print("\n=== SEED MASIVO FINALIZADO ===")

if __name__ == "__main__":
    main()
