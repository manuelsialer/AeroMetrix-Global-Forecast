# 🌍 AeroMetrix Global Forecast

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-green)](https://supabase.com)

**AeroMetrix** es un dashboard analítico avanzado (ETL) desarrollado para la asignatura de Programación Avanzada para la Ciencia de Datos. El proyecto extrae datos atmosféricos en tiempo real a través de APIs REST, persiste el historial en una base de datos relacional en la nube (PostgreSQL/Supabase) y visualiza análisis interactivos utilizando Machine Learning para proyecciones futuras.

---

## 🚀 Características Principales
1. **Extracción Automatizada**: Integración directa con la API de *OpenWeatherMap* para lectura de clima global en vivo.
2. **Persistencia SQL Robusta**: Uso de Supabase para almacenar un registro inmutable de datos atmosféricos. Incluye decoradores de auditoría de rendimiento.
3. **Machine Learning Integrado**: Uso de `scikit-learn` (**Random Forest Multivariable**) para inferir y proyectar la tendencia térmica para las próximas horas basándose en la evolución temporal, la humedad y el viento actuales.
4. **Dashboard "Glow Effect"**: Rediseño extremo de la Interfaz de Usuario mediante inyección de CSS masivo en Streamlit, imitando centros de control aeroespaciales, con gráficos interactivos Plotly (Mapas de calor, Radar de comparación).
5. **Calidad y Tests**: Módulos separados bajo principios de Responsabilidad Única y manejo de excepciones.

---

## 🛠️ Instalación y Configuración Local

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
.\venv\Scripts\Activate
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
OPENWEATHER_API_KEY=tu_api_key_aqui
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_anon_key_de_supabase
```

### 5. Ejecutar la Aplicación (Frontend)
```bash
streamlit run src/app.py
```
> La aplicación abrirá automáticamente una nueva ventana en tu navegador en `http://localhost:8501`.

### 6. Iniciar la Ingesta Automática (Cron Worker)
Para que el sistema recopile datos de forma pasiva sin gastar la cuota de tu API y evalúe **Alertas Climáticas (Webhooks)** en tiempo real, abre otra terminal y ejecuta el script en segundo plano:
```bash
python scripts/cron_worker.py
```
> Esto iniciará un loop infinito que buscará datos meteorológicos nuevos para las ciudades guardadas cada 15 minutos, respetando la restricción `UNIQUE` de PostgreSQL.

---

## 📂 Estructura del Proyecto

```text
project-root/
├── .env                # Credenciales secretas (ignorado en git)
├── README.md           # Este archivo
├── requirements.txt    # Dependencias de Python
├── docs/               
│   └── final.md        # Documento Técnico Final (Arquitectura y Limitaciones)
├── scripts/
│   └── cron_worker.py   # Servicio Background para ingesta pasiva y Webhooks
├── tests/              
│   └── test_processing.py # Pruebas unitarias para validación matemática
└── src/
    ├── app.py           # Controlador central de Streamlit (Frontend + CSS)
    ├── processing.py    # Lógica matemática de KPIs y Machine Learning (Random Forest)
    ├── viz.py           # Construcción de gráficos interactivos de Plotly
    ├── api.py           # Interfaz de extracción con OpenWeatherMap
    └── db.py            # Transacciones SQL, persistencia y decoradores
```

## ⚖️ Licencias y Referencias
- **Código Fuente**: Licencia MIT (Ver archivo `LICENSE`)
- **Fuente de Datos**: [OpenWeatherMap API](https://openweathermap.org/)
- **Infraestructura SQL**: [Supabase](https://supabase.com/)
- **Librería UI**: [Streamlit](https://streamlit.io/)
