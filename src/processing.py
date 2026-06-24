import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import logging
from functools import wraps

logger = logging.getLogger('AeroMetrix.Processing')

def error_handler_df(func):
    """
    Decorador para capturar fallos en las transformaciones de Pandas/Scikit-learn,
    registrar el error con logging, y devolver un resultado seguro para no colapsar la UI.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en {func.__name__}: {str(e)}", exc_info=True)
            # Retornar valores por defecto según la función
            if func.__name__ == 'process_raw_db_data':
                return pd.DataFrame()
            elif func.__name__ == 'calculate_kpis':
                return None, None, None, None
            elif func.__name__ == 'train_and_predict_temp':
                return pd.DataFrame(), None, None
            return None
    return wrapper

@error_handler_df
def process_raw_db_data(data: list) -> pd.DataFrame:
    """
    Convierte la respuesta cruda de SQLite (lista de diccionarios)
    en un DataFrame limpio, aplanando los campos anidados de 'locations'.
    """
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    
    # Extraer campos anidados del diccionario 'locations' 
    df['city_name'] = df['locations'].apply(lambda x: x['city_name'] if isinstance(x, dict) else x)
    df['country_code'] = df['locations'].apply(lambda x: x['country_code'] if isinstance(x, dict) else x)
    df['latitude'] = df['locations'].apply(lambda x: x.get('latitude') if isinstance(x, dict) else x)
    df['longitude'] = df['locations'].apply(lambda x: x.get('longitude') if isinstance(x, dict) else x)
    
    # Asegurar tipos de datos correctos
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

@error_handler_df
def calculate_kpis(df: pd.DataFrame, current_city: str):
    """
    Calcula los Indicadores Clave de Rendimiento (KPIs) y sus deltas (variaciones) 
    históricos para una ciudad específica.
    """
    city_df = df[df['city_name'] == current_city].sort_values('timestamp', ascending=False)
    
    if len(city_df) == 0:
        return None, None, None, None
        
    latest = city_df.iloc[0]
    
    # Calcular promedios históricos para el delta de la ciudad actual
    avg_temp = city_df['temperature_c'].mean()
    avg_hum = city_df['humidity_pct'].mean()
    avg_wind = city_df['wind_speed_kmh'].mean()
    
    # Calculo de variaciones (valor actual - promedio histórico)
    delta_temp = latest['temperature_c'] - avg_temp
    delta_hum = latest['humidity_pct'] - avg_hum
    delta_wind = latest['wind_speed_kmh'] - avg_wind
    
    return latest, delta_temp, delta_hum, delta_wind

@error_handler_df
def train_and_predict_temp(df: pd.DataFrame, city_name: str, periods: int = 8):
    """
    Entrena un modelo Multivariable (Random Forest) para predecir temperaturas futuras
    basado en la hora del día, la humedad y el viento.
    Aplica validación (train/test split) y codificación cíclica para el tiempo.
    Maneja excepciones en caso de que los datos no sean suficientes para entrenar.
    """
    city_df = df[df['city_name'] == city_name].sort_values('timestamp').copy()
    if len(city_df) < 5:
        return city_df, None, None # Insuficiente data
    
    try:
        # Feature Engineering: Codificación Cíclica para la Hora
        city_df['hour'] = city_df['timestamp'].dt.hour
        city_df['hour_sin'] = np.sin(2 * np.pi * city_df['hour'] / 24)
        city_df['hour_cos'] = np.cos(2 * np.pi * city_df['hour'] / 24)
        
        X = city_df[['hour_sin', 'hour_cos', 'humidity_pct', 'wind_speed_kmh']].values
        y = city_df['temperature_c'].values
        
        # Train/Test Split para validación rigurosa
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Calcular métricas de error
        y_pred_test = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        mae = mean_absolute_error(y_test, y_pred_test)
        metrics = {"rmse": rmse, "mae": mae}
        
        # Entrenar en todo el dataset para la predicción final
        model.fit(X, y)
        
        # Predecir futuro
        last_time = city_df['timestamp'].max()
        last_hum = city_df['humidity_pct'].iloc[-1]
        last_wind = city_df['wind_speed_kmh'].iloc[-1]
        
        future_dates = [last_time + timedelta(hours=3*i) for i in range(1, periods + 1)]
        future_features = []
        
        for d in future_dates:
            # Codificar hora futura cíclicamente
            h_sin = np.sin(2 * np.pi * d.hour / 24)
            h_cos = np.cos(2 * np.pi * d.hour / 24)
            future_features.append([h_sin, h_cos, last_hum, last_wind])
            
        future_temps = model.predict(future_features)
        
        future_df = pd.DataFrame({
            'timestamp': future_dates,
            'temperature_c': future_temps,
            'city_name': city_name
        })
        
        return city_df, future_df, metrics
    except ValueError as ve:
        logger.error(f"Error de valor durante el entrenamiento del modelo para {city_name}: {ve}")
        return city_df, None, None
    except Exception as e:
        logger.error(f"Error general durante el entrenamiento del modelo para {city_name}: {e}")
        return city_df, None, None

@error_handler_df
def recommend_travel_destinations(df: pd.DataFrame, all_cities: list) -> pd.DataFrame:
    """
    Evalúa todas las ciudades disponibles usando el modelo ML predictivo (24 horas).
    Calcula un 'Travel Score' penalizando desviaciones de 22°C y vientos fuertes.
    """
    if df.empty or not all_cities:
        return pd.DataFrame()
        
    recommendations = []
    
    for city in all_cities:
        # Predecir futuro para la ciudad (8 periodos de 3 horas = 24 horas)
        _, fut_df, _ = train_and_predict_temp(df, city, periods=8)
        
        if fut_df is not None and not fut_df.empty:
            avg_temp = fut_df['temperature_c'].mean()
            
            # Obtener datos actuales de viento y humedad de la ciudad
            city_df = df[df['city_name'] == city].sort_values('timestamp')
            if not city_df.empty:
                current_wind = city_df['wind_speed_kmh'].iloc[-1]
                current_hum = city_df['humidity_pct'].iloc[-1]
                
                # Calcular score (Base 100)
                # Penalización por temp: -5 pts por cada grado de diferencia con 22°C
                temp_penalty = abs(avg_temp - 22) * 5
                # Penalización por viento: -1 pt por cada km/h sobre 15km/h
                wind_penalty = max(0, current_wind - 15) * 1
                
                score = 100 - temp_penalty - wind_penalty
                score = max(0, min(100, score)) # Acotar entre 0 y 100
                
                recommendations.append({
                    "city_name": city,
                    "predicted_avg_temp": avg_temp,
                    "current_wind": current_wind,
                    "current_hum": current_hum,
                    "score": score
                })
                
    if not recommendations:
        return pd.DataFrame()
        
    rec_df = pd.DataFrame(recommendations)
    rec_df = rec_df.sort_values('score', ascending=False).head(5) # Top 5
    return rec_df
