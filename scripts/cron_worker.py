import os
import sys
import time
import requests
import schedule
from dotenv import load_dotenv

# Ensure 'src' is in path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from api import fetch_weather_data
from db import save_weather_data, get_supabase_client

load_dotenv()

WEBHOOK_URL = "https://webhook.site/#!/dummy"  # This is a dummy URL for testing alerts

def send_alert_webhook(city: str, wind_speed: float, temp: float):
    """Envía un webhook HTTP POST simulando una Edge Function para Alertas Activas."""
    payload = {
        "text": f"🚨 ALERTA CLIMÁTICA 🚨\nCiudad: {city}\nVientos peligrosos: {wind_speed} km/h\nTemperatura: {temp}°C",
        "severity": "high"
    }
    try:
        # En producción, esto sería la URL de Discord, Slack o Twilio
        print(f"\n--> [WEBHOOK DISPARADO]")
        print(payload["text"])
        print("--> [/WEBHOOK]\n")
        
        # Ejemplo de envío real comentado:
        # requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Error enviando webhook: {e}")

def fetch_and_store_all_cities():
    """Extrae pasivamente el clima para todas las ciudades en la BD para evitar saturar la API (Rate Limiting)."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando Cron Job: Recolección de datos por lote...")
    
    try:
        supabase = get_supabase_client()
        # Traer todas las ciudades distintas que hemos consultado alguna vez
        resp = supabase.table("locations").select("city_name").execute()
        cities = [item['city_name'] for item in resp.data]
        
        # Eliminar duplicados si los hubiera
        cities = list(set(cities))
    except Exception as e:
        print(f"Error conectando a Supabase para obtener ciudades: {e}")
        return
        
    for city in cities:
        try:
            print(f"  -> Polling: Extrayendo {city}...")
            data = fetch_weather_data(city)
            save_weather_data(data)
            
            # Evaluación de alertas (Webhooks Activos)
            # Threshold de 30 km/h fijado por configuración
            if data['wind_speed_kmh'] > 30.0:
                send_alert_webhook(city, data['wind_speed_kmh'], data['temperature_c'])
                
            # Dormir para respetar el Rate Limit de la API externa
            time.sleep(2) 
        except Exception as e:
            print(f"Error procesando {city}: {e}")
            
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cron Job finalizado. Esperando al siguiente ciclo...")

if __name__ == "__main__":
    print("Iniciando Worker Background (CRON)...")
    print("Presiona Ctrl+C para detener el proceso.")
    
    # Ejecución inmediata al arrancar
    fetch_and_store_all_cities() 
    
    # Programar cada 15 minutos
    schedule.every(15).minutes.do(fetch_and_store_all_cities)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
