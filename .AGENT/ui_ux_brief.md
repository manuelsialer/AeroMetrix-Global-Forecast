# UI/UX Design Brief

## 1. Concepto Visual
El dashboard debe tener un diseño limpio, profesional y enfocado en los datos ("Data-ink ratio" alto). Se utilizará el tema nativo de Streamlit (soporte para modo claro y oscuro), aprovechando las columnas y contenedores para organizar la información lógicamente.

## 2. Estructura de la Pantalla (Layout)

### Barra Lateral (Sidebar)
La barra lateral servirá como el centro de control del usuario.
- **Título**: Configuración / Filtros.
- **Selector de Ubicación**: Un menú desplegable (`st.selectbox`) para elegir la ciudad a analizar.
- **Selector de Rango de Fechas**: Un widget de fechas (`st.date_input`) para limitar los datos históricos.
- **Selector de Métricas**: Casillas de verificación o botones de radio para alternar entre Temperatura, Humedad y Velocidad del Viento.
- **Botón de Acción**: Botón para forzar la actualización de datos desde la API (`st.button('Actualizar Datos')`).

### Área Principal (Main Content)
- **Encabezado**: Título del proyecto y descripción breve.
- **Sección de KPIs (Key Performance Indicators)**: 
  - Fila superior con 3 a 4 métricas destacadas utilizando `st.metric`, mostrando valores actuales y deltas (cambios respecto a promedios o días anteriores). Ej: Temperatura actual, Humedad, Viento.
- **Sección de Visualizaciones**:
  - **Gráfico Principal (Líneas/Área)**: Evolución temporal de la métrica seleccionada en el rango de fechas. Ubicado en el centro ocupando el 100% del ancho.
  - **Gráfico Secundario (Barras/Dispersión)**: Comparativa (ej. Temperatura vs Humedad) o distribución de precipitaciones en layout de 2 columnas.
- **Sección de Datos Crudos (Opcional/Colapsable)**: Un contenedor desplegable (`st.expander`) con la tabla interactiva (`st.dataframe`) de los datos consultados para referencia rápida.

## 3. Interacciones y Experiencia
- **Feedback visual**: Mostrar un indicador de carga (`st.spinner` o `st.progress`) mientras se obtienen datos de la API o se realizan consultas a Supabase.
- **Manejo de estados vacíos**: Si no hay datos para una ciudad/fecha específica, mostrar un mensaje de advertencia (`st.warning` o `st.info`) amigable indicando la situación en lugar de gráficos vacíos o arrojar errores técnicos.
- **Alertas**: Utilizar notificaciones (`st.toast`, `st.success`) cuando los datos se actualicen correctamente y alertas de error (`st.error`) si falla la conexión a la base de datos o API.
