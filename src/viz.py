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
    
    cities = df['city_name'].unique()
    
    if len(cities) == 1:
        if "temp" in metric_col.lower():
            palette = [{"line": "#FF5F1F", "fill": "rgba(255, 95, 31, 0.1)"}] # Naranja Cálido
        elif "hum" in metric_col.lower():
            palette = [{"line": "#00F0FF", "fill": "rgba(0, 240, 255, 0.1)"}] # Cian Acuático
        else:
            palette = [{"line": "#39FF14", "fill": "rgba(57, 255, 20, 0.1)"}] # Verde Viento
    else:
        palette = [
            {"line": "#3B82F6", "fill": "rgba(59, 130, 246, 0.05)"},
            {"line": "#10B981", "fill": "rgba(16, 185, 129, 0.05)"},
            {"line": "#8B5CF6", "fill": "rgba(139, 92, 246, 0.05)"},
            {"line": "#F59E0B", "fill": "rgba(245, 158, 11, 0.05)"},
            {"line": "#EC4899", "fill": "rgba(236, 72, 153, 0.05)"}
        ]
    
    cities = df['city_name'].unique()
    for i, city in enumerate(cities):
        city_df = df[df['city_name'] == city]
        style = palette[i % len(palette)]
        
        fig.add_trace(go.Scatter(
            x=city_df["timestamp"],
            y=city_df[metric_col],
            mode='lines',
            name=city,
            line=dict(color=style["line"], width=1.5, shape='spline'),
            fill='tozeroy',
            fillcolor=style["fill"]
        ))

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)", 
            title="", showticklabels=True, tickfont=dict(color="#A0AEC0"),
            tickformat="%d %b\n%H:%M"
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.1)", 
            title=dict(text=metric_name, font=dict(color="#A0AEC0")), 
            tickfont=dict(color="#A0AEC0"),
            zeroline=True, zerolinecolor="rgba(255,255,255,0.2)"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#A0AEC0")),
        margin=dict(l=10, r=10, t=40, b=10),
        height=400,
        hovermode="x unified"
    )
    return fig

def create_heatmap_map(df: pd.DataFrame, metric_col: str, metric_name: str):
    """
    Crea un mapa mundial interactivo donde los puntos de las ciudades
    varían en color y tamaño según la métrica seleccionada.
    """
    if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
        return None

    latest_df = df.sort_values('timestamp').groupby('city_name').tail(1).reset_index()
    
    # Prevenir tamaños negativos (ej. temperaturas bajo cero)
    latest_df['bubble_size'] = latest_df[metric_col].abs() + 5

    # Escala de colores semántica
    if "temp" in metric_col.lower():
        color_scale = "Plasma"
    elif "hum" in metric_col.lower():
        color_scale = "Blues"
    else:
        color_scale = "Aggrnyl"

    fig = px.scatter_mapbox(
        latest_df,
        lat="latitude",
        lon="longitude",
        color=metric_col,
        size="bubble_size",
        size_max=15,
        hover_name="city_name",
        hover_data={"bubble_size": False, "latitude": False, "longitude": False, "weather_desc": True, "temperature_c": True, "humidity_pct": True, "wind_speed_kmh": True},
        color_continuous_scale=color_scale,
        zoom=1.5,
        mapbox_style="carto-darkmatter"
    )
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        height=400,
        coloraxis_colorbar=dict(
            title=dict(text="", font=dict(color="#A0AEC0")),
            tickfont=dict(color="#A0AEC0"),
            lenmode="fraction", len=0.75,
            thickness=15
        )
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
    colors = ["#3B82F6", "#8B5CF6"]
    
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
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.2)", tickfont=dict(color="#A0AEC0")),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.2)", tickfont=dict(color="#A0AEC0"))
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5, font=dict(color="#A0AEC0")),
        title=None,
        margin=dict(l=40, r=40, t=80, b=40),
        height=450
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
        mode='lines',
        name='Histórico',
        line=dict(color="#3B82F6", width=1.5)
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
            line=dict(color="#F59E0B", width=1.5, dash='dash'),
            marker=dict(size=4)
        ))
        
    fig.update_layout(
        title=None,
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)",
            tickfont=dict(color="#A0AEC0"),
            tickformat="%d %b\n%H:%M"
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.1)", 
            title=dict(text="Temperatura (°C)", font=dict(color="#A0AEC0")),
            tickfont=dict(color="#A0AEC0"),
            zeroline=True, zerolinecolor="rgba(255,255,255,0.2)"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#A0AEC0")),
        margin=dict(l=10, r=10, t=40, b=10),
        height=450,
        hovermode="x unified"
    )
    return fig
