import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pycountry

from api_or_scraper import fetch_weather_data, fetch_historical_data_open_meteo
from db import save_weather_data, get_historical_data, batch_save_weather_readings, get_available_cities, batch_save_historical_data
from viz import create_main_line_chart, create_heatmap_map, create_radar_chart, create_prediction_chart
from processing import process_raw_db_data, calculate_kpis, train_and_predict_temp, recommend_travel_destinations

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
        
    st.html(f"""
<style>
{css}
</style>
""")
    
    # Cargar lista rápida de ciudades para la UI
    cities_data = load_available_cities()
    df_cities = pd.DataFrame(cities_data) if cities_data else pd.DataFrame(columns=['id', 'city_name', 'country_code'])
    
    # --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.markdown("<h2 style='color:white; margin:0; font-family:Inter, sans-serif;'>AeroMetrix</h2><p style='color:#64748B; font-size:0.8rem; margin-top:0;'>Inteligencia Meteorológica de Precisión</p>", unsafe_allow_html=True)
    
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
    st.markdown("<div class='section-title'>Resumen</div>", unsafe_allow_html=True)

    if df_filtered.empty:
        st.markdown("""
        <div class="neo-card" style="border-left: 4px solid #F59E0B;">
            <h3 style="color: #F59E0B; margin-top: 0; font-family: 'Outfit', sans-serif;">⚠️ Sin Datos Atmosféricos</h3>
            <p style="color: #8C9FBA; margin-bottom: 0;">
            No hemos encontrado registros para esta ciudad en el rango temporal seleccionado.<br><br>
            <strong>Solución:</strong> Amplía el rango de fechas arriba, o ve a la sección <em>2. Motor de Datos</em> en la barra lateral para descargar el historial masivo satelital.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    primary_city = selected_city if selected_city in all_cities_in_db else (selected_cities[0] if selected_cities else all_cities_in_db[0])
    latest_data, d_temp, d_hum, d_wind = calculate_kpis(df_filtered, primary_city)
    
    if latest_data is not None:
        col_temp, col_hum, col_chart = st.columns([1, 1, 2.5])
        
        with col_temp:
            # Temperature Card
            country = latest_data.get('country_code', 'NA')
            st.markdown(f"""
            <div class="neo-card">
                <div class="card-title">Temperatura <div class="card-icon-button"><span class="material-symbols-outlined">chevron_right</span></div></div>
                <div style="display:flex; align-items:center; gap:10px; margin: 10px 0; flex-wrap: wrap;">
                    <div class="big-weather-icon" style="margin:0;"><span class="material-symbols-outlined" style="font-size:3.5rem;">rainy</span></div>
                    <div class="main-temp" style="margin:0;">{latest_data['temperature_c']:.1f}°C</div>
                </div>
                <div class="temp-hl">Min <span>18°C</span> Max <span>25°C</span></div>
                <div class="card-footer-location"><span class="material-symbols-outlined" style="font-size:1rem;">location_on</span> {primary_city}, {country}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_hum:
            # Air Quality (Humidity) Card
            st.markdown(f"""
            <div class="neo-card">
                <div class="card-title">Calidad del Aire (Hum) <div class="card-icon-button"><span class="material-symbols-outlined">chevron_right</span></div></div>
                <div style="text-align:center; margin: auto 0; padding: 20px 0;">
                    <div style="font-size:3rem; font-weight:800; color:var(--text-main); line-height: 1;">{latest_data['humidity_pct']:.0f}<span style="font-size:1rem; color:var(--text-sec);">%</span></div>
                </div>
                <div>
                    <div style="color:#38BDF8; font-weight:600; font-size:0.9rem;">| Bueno</div>
                    <div style="color:var(--text-sec); font-size:0.75rem; margin-top:5px; line-height:1.3;">La humedad está en un nivel estándar y es saludable para todos.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_chart:
            # Main Line Chart
            st.markdown("""
            <div class="neo-card" style="padding-bottom: 0px;">
                <div class="card-title">Temperatura <div class="card-icon-button" style="font-size:0.8rem; padding: 5px 10px;">Esta semana <span class="material-symbols-outlined" style="font-size:1rem;">expand_more</span></div></div>
            """, unsafe_allow_html=True)
            fig_line = create_main_line_chart(df_filtered, "temperature_c", "Temp")
            if fig_line: 
                # Ajustar márgenes para encajar perfecto en la tarjeta
                fig_line.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=250)
                st.plotly_chart(fig_line, use_container_width=True, key="main_chart")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Destacados de Hoy</div>", unsafe_allow_html=True)
    
    col_wind, col_uv, col_sun, col_banner = st.columns([1, 1, 1, 2.5])
    
    if latest_data is not None:
        with col_wind:
            st.markdown(f"""
            <div class="neo-card" style="min-height:200px; padding:20px;">
                <div class="card-title" style="margin-bottom:10px;">Estado del Viento</div>
                <div style="margin:auto 0; padding-top: 10px;">
                    <div class="value-display">{latest_data['wind_speed_kmh']:.1f} <span>km/h</span></div>
                    <div class="value-subtext">{datetime.now().strftime('%H:%M %p')}</div>
                </div>
                <div class="bottom-info-row">
                    <div class="card-footer-location"><span class="material-symbols-outlined" style="color:#38BDF8; font-size:1.2rem;">water_drop</span> Humedad</div>
                    <div class="bottom-info-val">{latest_data['humidity_pct']}<span>%</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_uv:
            st.markdown(f"""
            <div class="neo-card" style="min-height:200px; padding:20px;">
                <div class="card-title" style="margin-bottom:10px;">Condición</div>
                <div style="margin:auto 0; text-align:center;">
                    <div class="value-display" style="font-size:1.5rem;">{latest_data['weather_desc'].capitalize()}</div>
                </div>
                <div class="bottom-info-row">
                    <div class="card-footer-location"><span class="material-symbols-outlined" style="color:#38BDF8; font-size:1.2rem;">foggy</span> Niebla</div>
                    <div class="bottom-info-val">500 <span>m</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_sun:
            st.markdown(f"""
            <div class="neo-card" style="min-height:200px; padding:20px;">
                <div class="card-title" style="margin-bottom:10px;">Amanecer y Atardecer</div>
                <div style="margin:auto 0; text-align:center;">
                    <div style="width:100px; height:50px; border-top-left-radius:100px; border-top-right-radius:100px; border:2px dashed rgba(255,255,255,0.2); border-bottom:none; margin:10px auto; position:relative;">
                        <div style="position:absolute; bottom:-10px; left:10px; color:#FBBF24; font-size:1.2rem; text-shadow: 0 0 10px #FBBF24;">☀️</div>
                    </div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#8C9FBA; margin-top:5px;">
                    <div><span class="material-symbols-outlined" style="font-size:1rem; display:block; text-align:center;">wb_twilight</span>Amanecer<br>5:50 AM</div>
                    <div><span class="material-symbols-outlined" style="font-size:1rem; display:block; text-align:center;">nights_stay</span>Atardecer<br>6:30 PM</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_banner:
            st.markdown("""
            <div class="alert-banner">
                <div class="alert-text">¡Recibe alertas automáticas de cambios climáticos repentinos en tu dispositivo!</div>
                <button class="alert-button">Activar notificaciones</button>
            </div>
            """, unsafe_allow_html=True)

    # --- PREPARACIÓN DE CIUDADES PARA ANÁLISIS AVANZADO (Radar y Recommender) ---
    fallback_cities = ['Madrid', 'Tokyo', 'Lima', 'New York', 'Sydney', 'Paris', 'Cairo']
    fallback_available = [c for c in fallback_cities if c in all_cities_in_db]
    
    if len(selected_cities) >= 2:
        cities_for_ai = selected_cities
    else:
        cities_for_ai = list(set(cities_to_fetch + fallback_available))[:5]
        
    df_ai = pd.DataFrame()
    if len(cities_for_ai) > 0:
        ai_loc_ids = df_cities[df_cities['city_name'].isin(cities_for_ai)]['id'].tolist()
        df_ai = load_historical_data(ai_loc_ids, start_date_str, end_date_str, limit=5000)

    # Comparativa de Ciudades (Radar)
    if len(cities_for_ai) >= 2 and not df_ai.empty:
        st.markdown("<div class='section-title'>Análisis Multivariable</div>", unsafe_allow_html=True)
        col_rad_txt, col_rad_chart = st.columns([1, 2.5])
        
        with col_rad_txt:
            st.markdown(f"""
            <div class="neo-card" style="height:100%; justify-content:center;">
                <div class="card-title">Comparativa Climática</div>
                <h3 style="color:var(--text-main); font-size:1.5rem; margin:10px 0;">
                    {' <br><span style="color:var(--text-sec); font-size:1rem;">vs</span><br> '.join(cities_for_ai[:3])}
                </h3>
                <p style="color:var(--text-sec); font-size:0.9rem; line-height:1.5; margin-top:20px;">
                El gráfico de radar muestra el balance entre la temperatura, humedad y velocidad del viento normalizadas. 
                Un área mayor indica condiciones más extremas o valores más altos.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_rad_chart:
            st.markdown("<div class='neo-card' style='padding:0 20px;'>", unsafe_allow_html=True)
            fig_radar = create_radar_chart(df_ai, cities_for_ai[:3])
            if fig_radar:
                st.plotly_chart(fig_radar, use_container_width=True, key="radar_chart")
            st.markdown("</div>", unsafe_allow_html=True)

    # Travel Recommender Below
    st.markdown("<div class='section-title'>Recomendador de Viajes con IA</div>", unsafe_allow_html=True)
    
    if not df_ai.empty:
        with st.spinner("🤖 Calculando Proyecciones y Travel Score predictivo..."):
            rec_df = recommend_travel_destinations(df_ai, cities_for_ai)
        
        if not rec_df.empty:
            cols = st.columns(len(rec_df))
            for i, (_, row) in enumerate(rec_df.iterrows()):
                with cols[i]:
                    medal = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else "⭐"))
                    st.markdown(f"""
                    <div class="neo-card" style="background: linear-gradient(135deg, rgba(56,189,248,0.05) 0%, rgba(37,99,235,0.05) 100%); border: 1px solid rgba(56,189,248,0.2);">
                        <div class="card-title" style="color:var(--text-sec); font-size:0.8rem;">{medal} Puesto #{i+1}</div>
                        <h3 style="color:var(--text-main); font-size:1.2rem; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{row['city_name']}</h3>
                        <div style="font-size:1.8rem; font-weight:800; color:#38BDF8; margin:10px 0;">{row['score']:.1f}<span style="font-size:0.8rem; color:var(--text-sec);">/100</span></div>
                        <div style="color:var(--text-sec); font-size:0.75rem; line-height:1.4;">
                            Temp (24h): <span style="color:var(--text-main); font-weight:600;">{row['predicted_avg_temp']:.1f}°C</span><br>
                            Viento: {row['current_wind']:.1f} km/h
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Faltan datos históricos recientes para entrenar la IA.")
    else:
        st.info("No hay suficientes ciudades en la base de datos para generar recomendaciones.")

    st.markdown("<div class='section-title'>Registro de Eventos (Event Log)</div>", unsafe_allow_html=True)
    st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
    log_df = df_filtered.sort_values('timestamp', ascending=False).head(15)
    
    display_data = []
    for _, row in log_df.iterrows():
        ts = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        station = f"{row['country_code']}-{row['city_name'][:3].upper()}-{(hash(row['city_name']) % 99):02d}"
        
        if row['wind_speed_kmh'] > 30:
            ev = "🔴 Pico de Viento"
            status = "⚠️ ALERTA"
            mag = f"{row['wind_speed_kmh']:.1f} km/h"
        elif row['temperature_c'] > 30 or row['temperature_c'] < 0:
            ev = "🔵 Temp Extrema"
            status = "🔍 ANALIZADO"
            mag = f"{row['temperature_c']:.1f} °C"
        else:
            ev = "🟢 Despejado"
            status = "✅ ÓPTIMO"
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
            "Timestamp": st.column_config.TextColumn("FECHA/HORA"),
            "Event Type": st.column_config.TextColumn("TIPO DE EVENTO"),
            "Station": st.column_config.TextColumn("ESTACIÓN"),
            "Magnitude": st.column_config.TextColumn("MAGNITUD"),
            "Status": st.column_config.TextColumn("ESTADO"),
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='background-color:#131B2C; padding:20px; border-radius:8px; border:1px solid #1A263D;'>", unsafe_allow_html=True)

    st.subheader(f"Análisis Climático de {primary_city}")

    city_df = df_filtered[df_filtered["city_name"] == primary_city].copy()

    if not city_df.empty:

        city_df["mes"] = city_df["timestamp"].dt.month

        temp_mensual = city_df.groupby("mes")["temperature_c"].mean().reset_index()

        nombres_meses = {
            1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",
            5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",
            9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
        }

        temp_mensual["Mes"] = temp_mensual["mes"].map(nombres_meses)

        mes_caluroso = temp_mensual.loc[temp_mensual["temperature_c"].idxmax()]
        mes_frio = temp_mensual.loc[temp_mensual["temperature_c"].idxmin()]

        promedio = temp_mensual["temperature_c"].mean()

        meses_calidos = temp_mensual[temp_mensual["temperature_c"] > promedio]["Mes"].tolist()
        meses_frios = temp_mensual[temp_mensual["temperature_c"] < promedio]["Mes"].tolist()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "🔥 Mes más caluroso",
                f"{mes_caluroso['Mes']}",
                f"{mes_caluroso['temperature_c']:.1f} °C"
            )

        with col2:
            st.metric(
                "❄️ Mes más frío",
                f"{mes_frio['Mes']}",
                f"{mes_frio['temperature_c']:.1f} °C"
            )

        st.write("### 🌤️ Meses cálidos")
        st.write(", ".join(meses_calidos))

        st.write("### 🥶 Meses fríos")
        st.write(", ".join(meses_frios))

        st.write("### 📊 Temperatura promedio mensual")
        st.dataframe(
            temp_mensual[["Mes", "temperature_c"]]
            .rename(columns={"temperature_c": "Temperatura Promedio (°C)"})
        )

    st.markdown("</div>", unsafe_allow_html=True)
if __name__ == "__main__":
    main()
