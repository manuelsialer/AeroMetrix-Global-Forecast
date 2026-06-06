import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

from api import fetch_weather_data
from db import save_weather_data, get_historical_data
from viz import create_main_line_chart, create_heatmap_map, create_radar_chart, create_prediction_chart
from processing import process_raw_db_data, calculate_kpis, train_and_predict_temp

# Cargar variables de entorno
load_dotenv()

# Diccionario de países y ciudades predefinidas
COUNTRIES_CITIES = {
    "España": ["Madrid", "Barcelona", "Valencia", "Sevilla"],
    "Perú": ["Lima", "Cusco", "Arequipa", "Piura"],
    "México": ["Ciudad de Mexico", "Guadalajara", "Monterrey", "Cancun"],
    "Argentina": ["Buenos Aires", "Cordoba", "Rosario", "Mendoza"],
    "Colombia": ["Bogota", "Medellin", "Cali", "Cartagena"],
    "Chile": ["Santiago", "Valparaiso", "Concepcion"],
    "Estados Unidos": ["New York", "Los Angeles", "Miami", "Chicago"],
    "Francia": ["Paris", "Marseille", "Lyon"]
}

METRICS_MAP = {
    "Temperatura (°C)": ("temperature_c", "Temperatura (°C)"),
    "Humedad (%)": ("humidity_pct", "Humedad Relativa (%)"),
    "Velocidad del Viento (km/h)": ("wind_speed_kmh", "Velocidad del Viento (km/h)")
}

@st.cache_data(ttl=60)
def load_historical_data(city_filter=None):
    """Carga y procesa datos históricos de Supabase."""
    data = get_historical_data(city_filter)
    return process_raw_db_data(data)

def main():
    st.set_page_config(page_title="AeroMetrix Global Forecast", page_icon=":material/public:", layout="wide")
    
    st.markdown("""
    <style>
    /* Custom AeroMetrix Styling */
    .stApp {
        background-color: #0B1320;
    }
    [data-testid="stSidebar"] {
        background-color: #0A101C;
        border-right: 1px solid #1A263D;
    }
    div[data-testid="stMetric"] {
        background-color: #131B2C;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #1E2D4A;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Courier New', Courier, monospace;
        font-weight: 700;
        font-size: 2.2rem;
        color: #FFFFFF;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
    }
    .aerometrix-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 0px;
        line-height: 1.1;
    }
    .aerometrix-subtitle {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 10px;
    }
    .system-status {
        color: #64748B; 
        font-family: 'Courier New', monospace; 
        font-size: 0.8rem; 
        margin-top: 5px; 
        margin-bottom: 30px;
        text-transform: uppercase;
    }
    .system-status span {
        color: #39ff14;
    }
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #1A263D;
    }
    .stTabs [aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom-color: #00f0ff !important;
    }
    button[kind="secondary"] {
        background-color: #131B2C;
        border: 1px solid #1E2D4A;
        color: #A0AEC0;
    }
    button[kind="primary"] {
        background: linear-gradient(90deg, #00f0ff 0%, #00b8ff 100%);
        color: #000000;
        font-weight: bold;
        border: none;
    }
    /* Eliminar el borde feo de los expanders/contenedores */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.title(":material/settings: Configuración")
    
    st.sidebar.subheader("Ubicación (API)")
    selected_country = st.sidebar.selectbox("Selecciona un País", list(COUNTRIES_CITIES.keys()))
    selected_city = st.sidebar.selectbox("Selecciona una Ciudad", COUNTRIES_CITIES[selected_country])
    
    if st.sidebar.button("Obtener Clima Actual", type="primary", use_container_width=True):
        try:
            with st.spinner(f"Consultando API para {selected_city}..."):
                weather_data = fetch_weather_data(selected_city)
                save_weather_data(weather_data)
                st.toast(f"Datos de {selected_city} guardados en Supabase", icon=":material/check_circle:")
                load_historical_data.clear() # Invalidar caché
        except Exception as e:
            st.sidebar.error(f"Error al contactar la API: {e}")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros Históricos")
    
    default_start = datetime.today() - timedelta(days=7)
    default_end = datetime.today()
    
    date_range = st.sidebar.date_input(
        "Rango de Fechas",
        value=(default_start, default_end),
        max_value=datetime.today()
    )
    
    selected_metrics = st.sidebar.multiselect(
        "Métricas a Visualizar", 
        list(METRICS_MAP.keys()),
        default=["Temperatura (°C)"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader(":material/warning: Alertas de Viento")
    wind_threshold = st.sidebar.slider("Umbral Viento Fuerte (km/h)", min_value=0, max_value=100, value=30)

    # --- ÁREA PRINCIPAL ---
    st.markdown("<div class='aerometrix-title'>AeroMetrix Global Forecast</div>", unsafe_allow_html=True)
    st.markdown("<div class='aerometrix-subtitle'>Atmospheric Intelligence Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='system-status'><span>●</span> System Online — Last updated: LIVE GMT-5</div>", unsafe_allow_html=True)
    
    df = load_historical_data()
    
    if df.empty:
        st.warning("No hay datos en la base de datos de Supabase. Usa el botón de la barra lateral para registrar el clima de algunas ciudades.")
        return
        
    if len(date_range) == 2:
        start_date, end_date = date_range
        start_date = pd.to_datetime(start_date).tz_localize('UTC')
        end_date = pd.to_datetime(end_date).tz_localize('UTC') + pd.Timedelta(days=1)
        
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] < end_date)]
        
        if df.empty:
            st.warning("No hay datos históricos para el rango de fechas seleccionado.")
            return

    # --- KPIS TOP ---
    st.subheader(f"Métricas Actuales: {selected_city}")
    latest_data, d_temp, d_hum, d_wind = calculate_kpis(df, selected_city)
    
    if latest_data is not None:
        if latest_data['wind_speed_kmh'] > wind_threshold:
            st.error(f"¡ALERTA! El viento en {selected_city} es de {latest_data['wind_speed_kmh']} km/h (Supera el umbral de {wind_threshold} km/h)", icon=":material/emergency:")
            
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            with st.container(border=True):
                st.metric("Temperatura", f"{latest_data['temperature_c']} °C", f"{d_temp:+.1f} °C vs Promedio")
        with col2:
            with st.container(border=True):
                st.metric("Humedad", f"{latest_data['humidity_pct']} %", f"{d_hum:+.1f} % vs Promedio", delta_color="inverse")
        with col3:
            with st.container(border=True):
                st.metric("Vel. Viento", f"{latest_data['wind_speed_kmh']} km/h", f"{d_wind:+.1f} km/h vs Promedio", delta_color="inverse")
        with col4:
            with st.container(border=True):
                st.metric("Condición Actual", latest_data['weather_desc'], f"Actualizado: {latest_data['timestamp'].strftime('%H:%M')}", delta_color="off")
    else:
        st.info(f"Aún no hay datos guardados para {selected_city}. ¡Consúltalos en la barra lateral!")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- PESTAÑAS (TABS) ---
    tab1, tab2, tab3 = st.tabs([":material/dashboard: Panel General", ":material/compare_arrows: Comparativa Cara a Cara", ":material/memory: Predicción ML"])
    
    with tab1:
        if not selected_metrics:
            st.warning("Selecciona al menos una métrica en la barra lateral para ver los gráficos.")
        
        for metric in selected_metrics:
            metric_col, metric_label = METRICS_MAP[metric]
            
            st.markdown(f"### Análisis de {metric_label}")
            chart_col, map_col = st.columns([1.2, 1])
            
            with chart_col:
                fig_line = create_main_line_chart(df, metric_col, metric_label)
                if fig_line:
                    st.plotly_chart(fig_line, width='stretch', key=f"line_{metric_col}")
                    
            with map_col:
                fig_map = create_heatmap_map(df, metric_col, metric_label)
                if fig_map:
                    st.plotly_chart(fig_map, width='stretch', key=f"map_{metric_col}")
                    
            st.markdown("---")

        with st.expander("Ver Datos Crudos y Exportar"):
            st.dataframe(
                df[['timestamp', 'city_name', 'country_code', 'temperature_c', 'humidity_pct', 'wind_speed_kmh', 'weather_desc']]
                  .sort_values('timestamp', ascending=False),
                use_container_width=True
            )
            # Exportar a CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=":material/download: Descargar Datos Históricos (CSV)",
                data=csv,
                file_name='weather_history.csv',
                mime='text/csv',
            )

    with tab2:
        st.markdown("### Comparativa de Ciudades")
        st.write("Compara las condiciones actuales entre dos ciudades distintas.")
        col_c1, col_c2 = st.columns(2)
        
        all_cities_in_db = df['city_name'].unique().tolist()
        if len(all_cities_in_db) >= 2:
            with col_c1:
                comp_city_1 = st.selectbox("Ciudad 1", all_cities_in_db, index=0)
            with col_c2:
                comp_city_2 = st.selectbox("Ciudad 2", all_cities_in_db, index=1)
                
            radar_fig = create_radar_chart(df, comp_city_1, comp_city_2)
            if radar_fig:
                st.plotly_chart(radar_fig, width='stretch')
        else:
            st.info("Necesitas registrar al menos 2 ciudades en la base de datos para usar la comparativa.")

    with tab3:
        st.markdown("### Predicción de Temperatura a Futuro")
        st.write("Modelo de Machine Learning entrenado en vivo con los datos históricos para proyectar las próximas horas.")
        
        with st.spinner("Entrenando modelo Predictivo..."):
            hist_df, pred_df = train_and_predict_temp(df, selected_city, periods=8)
            
        if pred_df is not None:
            pred_fig = create_prediction_chart(hist_df, pred_df, selected_city)
            st.plotly_chart(pred_fig, width='stretch')
            
            st.success("Modelo entrenado exitosamente. La línea punteada verde muestra la tendencia para las próximas 24 horas.", icon=":material/check_circle:")
        else:
            st.warning(f"No hay suficientes datos históricos para {selected_city} para entrenar el modelo. Obtén el clima varias veces o espera a tener más registros históricos.")

if __name__ == "__main__":
    main()

# Trigger reload
