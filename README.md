AeroMetrix Global Forecast

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-green)](https://supabase.com)

**AeroMetrix** es un dashboard analítico avanzado (ETL) desarrollado para la asignatura de Programación Avanzada para la Ciencia de Datos. El proyecto extrae datos atmosféricos en tiempo real a través de APIs REST, persiste el historial en una base de datos relacional en la nube (**Supabase / PostgreSQL**) y visualiza análisis interactivos utilizando Machine Learning para proyecciones futuras.

---

## 🚀 Características Principales (Clean Code)
1. **Doble Motor de Extracción Atmosférica**: 
   - **OpenWeatherMap** (Tiempo Real) para captura satelital instantánea del clima actual.
   - **Open-Meteo Archive** para descargas masivas y retroactivas gratuitas.
2. **Ingeniería de Datos Avanzada**: 
   - Backend robusto usando **Supabase (PostgreSQL)** alojado en la nube con relaciones Primary Key / Foreign Key. Manejo de inserciones masivas y consultas eficientes usando el SDK oficial (`supabase-py`).
   - Contratos de datos estrictos usando **Pydantic** para validar los payloads JSON antes de la persistencia.
3. **Manejo de Errores y Decoradores**: Uso extensivo de bloques `try/except` en la manipulación de datos y creación de decoradores custom (`@timer_decorator` y `@error_handler_df`) para registrar tiempos de ejecución y prevenir fallos en la interfaz.
4. **Machine Learning y Sistema de Recomendación IA**: Uso de `scikit-learn` (**Random Forest Multivariable**) para predecir la temperatura futura y calcular un **Travel Score** predictivo, recomendando el Top 5 de mejores ciudades globales para viajar.
5. **UX/UI Premium**: Interfaz gráfica estilo "Centro Aeroespacial" implementando mapas interactivos, **Radares de Comparativa Múltiple** simultáneos, y un **Registro de Eventos (Event Log)** en tiempo real.

---

## Instalación y Configuración Local

Sigue estos pasos para desplegar la aplicación en tu propia computadora.

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/final-pacd-aerometrix.git
cd final-pacd-aerometrix
```

### 2. Crear un entorno virtual
Se recomienda el uso de un entorno virtual para aislar las dependencias.
```bash
python -m venv venv
# Activar en Windows (Powershell)
.\venv\Scripts\Activate.ps1

# Activar en macOS / Linux
source venv/bin/activate
```

### 3. Instalar dependencias
Asegúrate de que el entorno esté activado y ejecuta:
```bash
pip install -r requirements.txt
```

### 4. Variables de Entorno
Crea un archivo llamado `.env` en la raíz del proyecto y añade tus propias credenciales:
```env
WEATHER_API_KEY=tu_api_key_aqui
SUPABASE_URL=tu_supabase_project_url
SUPABASE_KEY=tu_supabase_anon_key
```

### 5. Ejecutar la Aplicación (Frontend)
```bash
streamlit run src/app.py
```
> La aplicación abrirá automáticamente una nueva ventana en tu navegador en `http://localhost:8501`. La aplicación se conectará de inmediato a tu instancia de Supabase en la nube.

---

#Estructura del Proyecto

```text
project-root/
├── .env                  # Credenciales secretas (ignorado en git)
├── README.md             # Este archivo
├── requirements.txt      # Dependencias de Python
├── docs/               
│   └── final.md          # Documento Técnico Final (Flujo, DB, Mejoras)
└── src/
    ├── app.py            # Controlador central de Streamlit (Frontend + CSS)
    ├── processing.py     # Lógica matemática (Random Forest) y manejo de errores (Decoradores)
    ├── viz.py            # Construcción de gráficos interactivos de Plotly
    ├── api_or_scraper.py # Interfaz de extracción (OpenWeatherMap / Open-Meteo)
    └── db.py             # Motor transaccional y cliente de conexión a Supabase
```
## Limitaciones
 Streamlit no es una herramienta de desarrollo web convencional, sino un framework orientado a prototipado de datos.Elementos como animaciones complejas, navegación multipágina fluida o interacciones asíncronas requieren workarounds que aumentan la complejidad del código.Asimismo,El sistema depende de la disponibilidad continua de OpenWeatherMap y Open-Meteo. Cualquier interrupción, cambio en los límites de rate limiting o modificación en la estructura de los endpoints puede romper el pipeline ETL sin previo aviso.

## ⚖️ Licencias y Referencias
- **Código Fuente**: Licencia MIT
- **Fuentes de Datos**: [OpenWeatherMap API](https://openweathermap.org/) y [Open-Meteo Archive API](https://open-meteo.com/)
- **Infraestructura SQL**: PostGres SQl - SUPABASE
- **Librería UI**: [Streamlit](https://streamlit.io/)
