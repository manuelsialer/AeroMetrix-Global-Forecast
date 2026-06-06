import pytest
import pandas as pd
from datetime import datetime, timezone
import sys
import os

# Asegurar que se importen módulos del directorio 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from processing import calculate_kpis

def test_calculate_kpis_empty_df():
    """Prueba que pasa un DataFrame vacío retorne None y deltas cero."""
    empty_df = pd.DataFrame(columns=[
        'timestamp', 'city_name', 'temperature_c', 
        'humidity_pct', 'wind_speed_kmh', 'weather_desc'
    ])
    latest_data, d_temp, d_hum, d_wind = calculate_kpis(empty_df, "Madrid")
    assert latest_data is None
    assert d_temp is None
    assert d_hum is None
    assert d_wind is None

def test_calculate_kpis_valid_data():
    """Prueba que calcula correctamente los deltas basados en el promedio histórico."""
    data = {
        'timestamp': [
            datetime(2023, 1, 1, tzinfo=timezone.utc),
            datetime(2023, 1, 2, tzinfo=timezone.utc),
            datetime(2023, 1, 3, tzinfo=timezone.utc)
        ],
        'city_name': ['Lima', 'Lima', 'Lima'],
        'temperature_c': [20.0, 22.0, 24.0],  # Avg = 22.0, Last = 24.0, Delta = +2.0
        'humidity_pct': [50.0, 60.0, 70.0],  # Avg = 60.0, Last = 70.0, Delta = +10.0
        'wind_speed_kmh': [10.0, 15.0, 20.0], # Avg = 15.0, Last = 20.0, Delta = +5.0
        'weather_desc': ['Clear', 'Clouds', 'Rain']
    }
    df = pd.DataFrame(data)
    
    latest_data, d_temp, d_hum, d_wind = calculate_kpis(df, "Lima")
    
    assert latest_data is not None
    assert latest_data['temperature_c'] == 24.0
    assert d_temp == 2.0
    assert d_hum == 10.0
    assert d_wind == 5.0
