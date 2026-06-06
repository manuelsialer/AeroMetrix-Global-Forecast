import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_main_line_chart(df: pd.DataFrame, metric_col: str, metric_name: str):
    """
    Crea el gráfico de líneas principal mostrando la evolución temporal de una métrica
    con un efecto de resplandor neón (Glow Effect).
    """
    if df.empty:
        return None

    df = df.sort_values(by="timestamp")
    
    fig = go.Figure()
    
    # Colores Hex y sus versiones RGBA transparentes para el relleno
    palette = [
        {"line": "#00f0ff", "fill": "rgba(0, 240, 255, 0.1)"},
        {"line": "#39ff14", "fill": "rgba(57, 255, 20, 0.1)"},
        {"line": "#ff5f1f", "fill": "rgba(255, 95, 31, 0.1)"}
    ]
    
    cities = df['city_name'].unique()
    for i, city in enumerate(cities):
        city_df = df[df['city_name'] == city]
        style = palette[i % len(palette)]
        
        fig.add_trace(go.Scatter(
            x=city_df["timestamp"],
            y=city_df[metric_col],
            mode='lines+markers',
            name=city,
            line=dict(color=style["line"], width=3),
            fill='tozeroy',
            fillcolor=style["fill"]
        ))

    fig.update_layout(
        title=f"Temporal Trends: {metric_name}",
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="Time"),
        yaxis=dict(gridcolor="#1E2D4A", title=metric_name),
        legend_title="Station",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def create_heatmap_map(df: pd.DataFrame, metric_col: str, metric_name: str):
    """
    Crea un mapa mundial interactivo donde los puntos de las ciudades
    varían en color y tamaño según la métrica seleccionada.
    """
    if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
        return None

    # Para el mapa, generalmente queremos el último valor de cada ciudad
    # Así que agrupamos y tomamos el registro más reciente
    latest_df = df.sort_values('timestamp').groupby('city_name').tail(1).reset_index()

    fig = px.scatter_geo(
        latest_df,
        lat="latitude",
        lon="longitude",
        color=metric_col,
        hover_name="city_name",
        hover_data=["weather_desc", "temperature_c", "humidity_pct", "wind_speed_kmh"],
        size=metric_col if metric_col != 'temperature_c' else None,
        title=f"Global Station Overlay: {metric_name}",
        color_continuous_scale=[[0, "#171f33"], [1, "#ff5f1f"]] if metric_col == 'temperature_c' else [[0, "#171f33"], [1, "#00f0ff"]],
        projection="natural earth"
    )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            showland=True,
            landcolor="#131B2C",
            showcountries=True,
            countrycolor="#1E2D4A",
            showlakes=True,
            lakecolor="#0A101C"
        ),
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    
    return fig

def create_radar_chart(df: pd.DataFrame, city1: str, city2: str):
    """
    Crea un gráfico de Radar comparando métricas normalizadas entre dos ciudades.
    """
    latest_df = df.sort_values('timestamp').groupby('city_name').tail(1)
    
    cities_data = latest_df[latest_df['city_name'].isin([city1, city2])]
    if len(cities_data) == 0:
        return None
        
    categories = ['Temp (Relativa)', 'Humedad (%)', 'Viento (Relativo)']
    
    fig = go.Figure()
    colors = ["#00f0ff", "#ff5f1f"]
    
    for i, city in enumerate([city1, city2]):
        city_row = cities_data[cities_data['city_name'] == city]
        if not city_row.empty:
            # Normalización rápida (0-100)
            t = min(max(city_row['temperature_c'].values[0] / 50.0 * 100, 0), 100)
            h = city_row['humidity_pct'].values[0]
            v = min(city_row['wind_speed_kmh'].values[0] / 100.0 * 100, 100)
            
            fig.add_trace(go.Scatterpolar(
                r=[t, h, v],
                theta=categories,
                fill='toself',
                name=city,
                line_color=colors[i % 2]
            ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#171f33"),
            angularaxis=dict(gridcolor="#171f33")
        ),
        showlegend=True,
        title="Comparativa Cara a Cara"
    )
    return fig

def create_prediction_chart(history_df: pd.DataFrame, future_df: pd.DataFrame, city: str):
    """
    Crea un gráfico de líneas combinando datos históricos y predicción ML.
    """
    fig = go.Figure()
    
    # Histórico
    fig.add_trace(go.Scatter(
        x=history_df['timestamp'], 
        y=history_df['temperature_c'],
        mode='lines+markers',
        name='Histórico',
        line=dict(color="#00f0ff", width=3)
    ))
    
    # Predicción
    if future_df is not None and not future_df.empty:
        last_hist = history_df.iloc[-1:]
        # Para evitar el warning de FutureWarning al concatenar
        future_df = future_df.copy()
        future_combined = pd.concat([last_hist, future_df], ignore_index=True)
        
        fig.add_trace(go.Scatter(
            x=future_combined['timestamp'], 
            y=future_combined['temperature_c'],
            mode='lines+markers',
            name='Predicción ML',
            line=dict(color="#39ff14", width=3, dash='dash')
        ))
        
    fig.update_layout(
        title=f"Proyección Térmica: {city}",
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#171f33", title="Temperatura (°C)"),
        legend_title="Tipo de Dato"
    )
    return fig
