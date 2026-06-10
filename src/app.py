import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pycountry

from api import fetch_weather_data, fetch_historical_data_open_meteo
from db import save_weather_data, get_historical_data, batch_save_weather_readings, get_available_cities, batch_save_historical_data
from viz import create_main_line_chart, create_heatmap_map, create_radar_chart, create_prediction_chart
from processing import process_raw_db_data, calculate_kpis, train_and_predict_temp

# Cargar variables de entorno
load_dotenv()

METRICS_MAP = {
    "Temperatura (°C)": ("temperature_c", "Temperatura (°C)"),
    "Humedad (%)": ("humidity_pct", "Humedad Relativa (%)"),
    "Velocidad del Viento (km/h)": ("wind_speed_kmh", "Velocidad del Viento (km/h)")
}

@st.cache_data(ttl=300)
def load_available_cities():
    """Carga rápida de ciudades disponibles desde locations."""
    return get_available_cities()

@st.cache_data(ttl=60)
def load_historical_data(location_ids=None, start_date=None, end_date=None, limit=5000):
    """Carga y procesa datos históricos filtrados eficientemente desde Supabase."""
    data = get_historical_data(location_ids, start_date, end_date, limit)
    return process_raw_db_data(data)

def main():
    st.set_page_config(page_title="AeroMetrix Global Forecast", page_icon=":material/public:", layout="wide", initial_sidebar_state="expanded")
    
    import os
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    try:
        with open(css_path, "r") as f:
            css = f.read()
    except Exception:
        css = ""
        
    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
    <style>
    {css}
    </style>
    """, unsafe_allow_html=True)
    
    # Cargar lista rápida de ciudades para la UI
    cities_data = load_available_cities()
    df_cities = pd.DataFrame(cities_data) if cities_data else pd.DataFrame(columns=['id', 'city_name', 'country_code'])
    
    # --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.markdown("<h2 style='color:white; margin:0; font-family:Inter, sans-serif;'>AeroMetrix</h2><p style='color:#64748B; font-size:0.8rem; margin-top:0;'>Precision Weather Intelligence</p>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("1. LOCALIZACIÓN PRINCIPAL")
    
    # --- BARRA LATERAL (SIDEBAR) ---
    
    st.sidebar.subheader("1. Filtros de Visualización")
    
    # Ciudades en DB general
    all_cities_in_db = sorted(df_cities['city_name'].unique().tolist()) if not df_cities.empty else []
    
    default_multi = [all_cities_in_db[0]] if all_cities_in_db else []
    selected_cities = st.sidebar.multiselect("Ciudades a Visualizar", all_cities_in_db, default=default_multi)
    
    default_start = datetime.today() - timedelta(days=7)
    date_range = st.sidebar.date_input("Rango de Análisis", value=(default_start, datetime.today()), max_value=datetime.today())
    selected_metrics = st.sidebar.multiselect("Métricas", list(METRICS_MAP.keys()), default=[list(METRICS_MAP.keys())[0]])

    st.sidebar.markdown("---")
    st.sidebar.subheader("2. Motor de Datos (APIs)")
    
    with st.sidebar.expander("⚙️ Extraer / Actualizar Datos", expanded=False):
        st.markdown("<p style='font-size: 0.85rem; color: #A0AEC0;'>Agrega nuevas ciudades o actualiza el historial de las existentes.</p>", unsafe_allow_html=True)
        
        country_list = sorted([country.name for country in pycountry.countries])
        selected_country = st.selectbox("País", country_list, index=country_list.index("Peru") if "Peru" in country_list else 0)
        
        country_obj = pycountry.countries.get(name=selected_country)
        country_code = country_obj.alpha_2 if country_obj else ""
        
        if not df_cities.empty:
            cities_in_db_for_country = sorted(df_cities[df_cities['country_code'] == country_code]['city_name'].unique().tolist())
        else:
            cities_in_db_for_country = []
        
        opcion_nueva_ciudad = "➕ Buscar Nueva Ciudad..."
        opciones_ciudad = [opcion_nueva_ciudad] + cities_in_db_for_country
        
        selected_city_dropdown = st.selectbox("Ciudad Destino", opciones_ciudad)
        
        if selected_city_dropdown == opcion_nueva_ciudad:
            selected_city = st.text_input("Escribe el nombre:", placeholder="Ej. Lima, Madrid...")
        else:
            selected_city = selected_city_dropdown
            
        st.markdown("<hr style='margin: 10px 0; border-color: #1A263D;'>", unsafe_allow_html=True)
        
        tab_live, tab_hist = st.tabs(["📡 En Vivo", "📅 Histórico"])
        
        with tab_live:
            st.caption("Consulta OWM y guarda el clima en este exacto instante.")
            if st.button("Escanear Ahora", type="primary", width="stretch"):
                if not selected_city:
                    st.error("Indica una ciudad.")
                else:
                    try:
                        with st.spinner(f"Consultando {selected_city}..."):
                            weather_data = fetch_weather_data(selected_city)
                            save_weather_data(weather_data)
                            st.toast(f"Datos de {selected_city} guardados.", icon=":material/check_circle:")
                            load_historical_data.clear()
                            load_available_cities.clear()
                            st.rerun()
                    except Exception as e:
                        st.error("Error API: Ciudad no encontrada.")
                        
        with tab_hist:
            st.caption("Descarga Open-Meteo para llenar vacíos históricos.")
            om_start = st.date_input("Desde", value=datetime.today() - timedelta(days=30), max_value=datetime.today())
            om_end = st.date_input("Hasta", value=datetime.today(), max_value=datetime.today())
            if st.button("Descargar Historial", width="stretch"):
                if not selected_city:
                    st.error("Indica una ciudad.")
                else:
                    try:
                        with st.spinner(f"Descargando historial de {selected_city}..."):
                            historical_data = fetch_historical_data_open_meteo(selected_city, om_start.strftime("%Y-%m-%d"), om_end.strftime("%Y-%m-%d"))
                            total = len(historical_data)
                            if total > 0:
                                my_bar = st.progress(0.5, text="Guardando lote en base de datos...")
                                batch_save_historical_data(historical_data)
                                my_bar.empty()
                                st.toast(f"Se guardaron {total} registros en tiempo récord.", icon=":material/check_circle:")
                                load_historical_data.clear()
                                st.rerun()
                            else:
                                st.warning("No se encontraron datos.")
                    except Exception as e:
                        st.error(f"Error Open-Meteo: {e}")

    # --- DESCARGAR DATOS OPTIMIZADOS DESDE SUPABASE ---
    if len(date_range) == 2:
        start_date_str = date_range[0].strftime('%Y-%m-%d')
        end_date_str = (date_range[1] + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        start_date_str = None
        end_date_str = None
        
    cities_to_fetch = selected_cities if selected_cities else default_multi
    
    # Obtener los location_ids de las ciudades a visualizar
    if not df_cities.empty and cities_to_fetch:
        loc_ids = df_cities[df_cities['city_name'].isin(cities_to_fetch)]['id'].tolist()
    else:
        loc_ids = []

    # Cargamos solo los datos necesarios en lugar de 1 millón de registros
    df_filtered = load_historical_data(loc_ids, start_date_str, end_date_str, limit=10000)

    # --- ÁREA PRINCIPAL ---
    st.markdown("<div class='aerometrix-title'>AeroMetrix Global Forecast</div>", unsafe_allow_html=True)
    st.markdown("<div class='aerometrix-subtitle'>Atmospheric Intelligence Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='system-status'><span>●</span> System Online — Last updated: {datetime.now().strftime('%H:%M:%S')} GMT-5</div>", unsafe_allow_html=True)

    if df_filtered.empty:
        st.markdown("""
        <div style="background-color: rgba(245, 158, 11, 0.1); border-left: 4px solid #F59E0B; padding: 20px; border-radius: 5px; margin: 30px 0;">
            <h3 style="color: #F59E0B; margin-top: 0; font-family: 'Inter', sans-serif;">⚠️ Sin Datos Atmosféricos</h3>
            <p style="color: #A0AEC0; margin-bottom: 0; font-family: 'Inter', sans-serif;">
            No hemos encontrado registros para esta ciudad en el rango temporal seleccionado.<br><br>
            <strong>Solución:</strong> Amplía el rango de fechas arriba, o ve a la sección <em>2. Motor de Datos</em> en la barra lateral para descargar el historial masivo satelital.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # --- KPIS TOP ---
    primary_city = selected_city if selected_city in all_cities_in_db else (selected_cities[0] if selected_cities else all_cities_in_db[0])
    
    latest_data, d_temp, d_hum, d_wind = calculate_kpis(df_filtered, primary_city)
    
    if latest_data is not None:
        c1, c2, c3, c4 = st.columns(4)
        
        # Temp
        if d_temp > 0: arr_temp, sgn_temp, cls_temp = "↑", "+", "delta-up"
        elif d_temp < 0: arr_temp, sgn_temp, cls_temp = "↓", "", "delta-down"
        else: arr_temp, sgn_temp, cls_temp = "", "", "delta-neutral"
            
        c1.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Temperature ({primary_city}) <span class="material-symbols-outlined">thermostat</span></div>
            <div class="metric-value-container">
                <div class="metric-value">{latest_data['temperature_c']}°C</div>
                <div class="metric-delta {cls_temp}">{arr_temp} {sgn_temp}{d_temp:.1f}°</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Humidity
        if d_hum > 0: arr_hum, sgn_hum, cls_hum = "↑", "+", "delta-up"
        elif d_hum < 0: arr_hum, sgn_hum, cls_hum = "↓", "", "delta-down"
        else: arr_hum, sgn_hum, cls_hum = "", "", "delta-neutral"
            
        c2.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Humidity <span class="material-symbols-outlined">water_drop</span></div>
            <div class="metric-value-container">
                <div class="metric-value">{latest_data['humidity_pct']}%</div>
                <div class="metric-delta {cls_hum}">{arr_hum} {sgn_hum}{d_hum:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Wind
        if d_wind > 0: arr_wind, sgn_wind, cls_wind = "↑", "+", "delta-up"
        elif d_wind < 0: arr_wind, sgn_wind, cls_wind = "↓", "", "delta-down"
        else: arr_wind, sgn_wind, cls_wind = "", "", "delta-neutral"
            
        c3.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Wind Speed <span class="material-symbols-outlined">air</span></div>
            <div class="metric-value-container">
                <div class="metric-value">{latest_data['wind_speed_kmh']}<span style='font-size:1rem'>km/h</span></div>
                <div class="metric-delta {cls_wind}">{arr_wind} {sgn_wind}{d_wind:.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Condition
        c4.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Condition <span class="material-symbols-outlined">routine</span></div>
            <div class="metric-value-container">
                <div class="metric-value" style="font-size:1.3rem;">{latest_data['weather_desc']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- TABS LAYOUT ---
    tab1, tab2, tab3, tab4 = st.tabs(["Monitoreo Global", "Machine Learning", "Radar Comparativo", "Registro de Eventos"])
    
    with tab1:
        if not selected_metrics:
            st.info("Por favor, selecciona al menos una métrica en el panel lateral.")
        else:
            for metric in selected_metrics:
                metric_col, metric_label = METRICS_MAP[metric]
                col_chart, col_map = st.columns([1.5, 1])
                with col_chart:
                    st.markdown("<div style='background-color:#131B2C; padding:15px; border-radius:8px; border:1px solid #1A263D; margin-bottom: 15px;'>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='color:white; margin:0; font-family:Inter, sans-serif;'>Temporal Trends</h4>", unsafe_allow_html=True)
                    fig_line = create_main_line_chart(df_filtered, metric_col, metric_label)
                    if fig_line: st.plotly_chart(fig_line, width='stretch', key=f"line_{metric_col}")
                    st.markdown("</div>", unsafe_allow_html=True)
                        
                with col_map:
                    st.markdown("<div style='background-color:#131B2C; padding:15px; border-radius:8px; border:1px solid #1A263D; margin-bottom: 15px;'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='color:white; margin:0; font-family:Inter, sans-serif;'>Global Station Overlay</h4>", unsafe_allow_html=True)
                    fig_map = create_heatmap_map(df_filtered, metric_col, metric_label)
                    if fig_map: st.plotly_chart(fig_map, width='stretch', key=f"map_{metric_col}")
                    st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div style='background-color:#131B2C; padding:15px; border-radius:8px; border:1px solid #1A263D;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:white; margin:0; font-family:Inter, sans-serif;'>Proyección de Temperatura (Random Forest)</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color:#A0AEC0; font-size:0.9rem;'>Proyección a 24 horas usando Random Forest Regression.</p>", unsafe_allow_html=True)
        
        with st.spinner("🧠 Entrenando motor de Inteligencia Artificial..."):
            hist_df, fut_df, metrics = train_and_predict_temp(df_filtered, primary_city)
            
        if fut_df is not None:
            if metrics:
                st.markdown(f"<p style='color:#39ff14; font-family: Courier New; font-size:0.85rem; margin-top:-10px;'>✓ Modelo Validado | RMSE: {metrics['rmse']:.2f}°C | MAE: {metrics['mae']:.2f}°C</p>", unsafe_allow_html=True)
            fig_pred = create_prediction_chart(hist_df, fut_df, primary_city)
            st.plotly_chart(fig_pred, width='stretch')
        else:
            st.warning(f"No hay suficientes datos históricos recientes de {primary_city} para entrenar el modelo.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div style='background-color:#131B2C; padding:15px; border-radius:8px; border:1px solid #1A263D;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:white; margin:0; font-family:Inter, sans-serif;'>Comparador de Ciudades</h4>", unsafe_allow_html=True)
        
        # El radar ahora solo permite comparar ciudades de la selección activa (df_filtered)
        if len(cities_to_fetch) >= 2:
            col1, col2 = st.columns(2)
            city_1 = col1.selectbox("Ciudad 1", cities_to_fetch, index=0)
            city_2 = col2.selectbox("Ciudad 2", cities_to_fetch, index=1 if len(cities_to_fetch)>1 else 0)
            
            fig_radar = create_radar_chart(df_filtered, city_1, city_2)
            if fig_radar:
                st.plotly_chart(fig_radar, width='stretch')
        else:
            st.info("Agrega al menos 2 ciudades en el 'Filtro de Visualización' lateral para usar el radar comparativo.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div style='background-color:#131B2C; padding:20px; border-radius:8px; border:1px solid #1A263D;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:white; margin-top:0; font-family:Inter, sans-serif;'>Atmospheric Event Log</h4>", unsafe_allow_html=True)
        
        log_df = df_filtered.sort_values('timestamp', ascending=False).head(15)
        
        display_data = []
        for _, row in log_df.iterrows():
            ts = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            station = f"{row['country_code']}-{row['city_name'][:3].upper()}-{(hash(row['city_name']) % 99):02d}"
            
            if row['wind_speed_kmh'] > 30:
                ev = "🔴 Wind Spike"
                status = "⚠️ ALERT"
                mag = f"{row['wind_speed_kmh']:.1f} km/h"
            elif row['temperature_c'] > 30 or row['temperature_c'] < 0:
                ev = "🔵 Temp Reading"
                status = "🔍 ANALYZED"
                mag = f"{row['temperature_c']:.1f} °C"
            else:
                ev = "🟢 Clear Sky"
                status = "✅ OPTIMAL"
                mag = f"{row['temperature_c']:.1f} °C"
                
            display_data.append({
                "Timestamp": ts,
                "Event Type": ev,
                "Station": station,
                "Magnitude": mag,
                "Status": status
            })
            
        events_df = pd.DataFrame(display_data)
        st.dataframe(
            events_df, 
            width='stretch', 
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.TextColumn("TIMESTAMP"),
                "Event Type": st.column_config.TextColumn("EVENT TYPE"),
                "Station": st.column_config.TextColumn("STATION"),
                "Magnitude": st.column_config.TextColumn("MAGNITUDE"),
                "Status": st.column_config.TextColumn("STATUS"),
            }
        )
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
