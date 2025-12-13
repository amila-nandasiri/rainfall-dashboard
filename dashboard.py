import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- CONFIGURATION ---
LOCATIONS = {
    "Male'": {"lat": 4.1755, "lon": 73.5093},
    "Addu City": {"lat": -0.6931, "lon": 73.1585}
}

# --- 1. FETCH DATA ---
def get_weather_data(lat, lon):
    # Fetch 90 days history + 7 days forecast
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum,temperature_2m_max&past_days=90&forecast_days=7&timezone=auto"
    resp = requests.get(url).json()
    
    return pd.DataFrame({
        'Date': resp['daily']['time'],
        'Rain': resp['daily']['precipitation_sum'],
        'Temp': resp['daily']['temperature_2m_max']
    })

print("Fetching Weather Data...")
df_male = get_weather_data(LOCATIONS["Male'"]["lat"], LOCATIONS["Male'"]["lon"])
df_addu = get_weather_data(LOCATIONS["Addu City"]["lat"], LOCATIONS["Addu City"]["lon"])

# --- 2. BUILD THE DASHBOARD (GRID LAYOUT) ---
# We create a grid: Top row for "KPI Cards", Middle for Main Chart, Bottom for Comparison
fig = make_subplots(
    rows=3, cols=2,
    specs=[
        [{"type": "indicator"}, {"type": "indicator"}], # Row 1: Big Numbers
        [{"colspan": 2, "type": "xy"}, None],           # Row 2: Main Graph (Spans both cols)
        [{"colspan": 2, "type": "xy"}, None]            # Row 3: Temp Comparison
    ],
    vertical_spacing=0.08,
    subplot_titles=("Total Rainfall (Last 90 Days - Male')", "Max Temp Today (Male')", 
                    "Daily Rainfall & Trend", "Temperature Comparison (Male' vs Addu)")
)

# --- ROW 1: KPI INDICATORS ---
# KPI 1: Total Rainfall (Male')
total_rain_male = df_male['Rain'].sum()
fig.add_trace(go.Indicator(
    mode="number+delta",
    value=total_rain_male,
    title={"text": "Total Rain (mm)"},
    number={'suffix': " mm", 'font': {'color': '#00cc96'}},
    delta={'position': "bottom", 'reference': 300, 'relative': False}, # Dummy reference for fun
    domain={'row': 0, 'column': 0}
), row=1, col=1)

# KPI 2: Max Temp Today
temp_today = df_male.iloc[-7]['Temp'] # Approximate 'today' based on forecast index
fig.add_trace(go.Indicator(
    mode="number",
    value=temp_today,
    title={"text": "Max Temp Today"},
    number={'suffix': " °C", 'font': {'color': '#EF553B'}},
    domain={'row': 0, 'column': 1}
), row=1, col=2)

# --- ROW 2: MAIN RAINFALL CHART (Interactive) ---
# Bar Chart for Rain
fig.add_trace(go.Bar(
    x=df_male['Date'], y=df_male['Rain'],
    name="Rainfall (Male')",
    marker_color='#00cc96',
    opacity=0.8
), row=2, col=1)

# Line Chart for Trend
fig.add_trace(go.Scatter(
    x=df_male['Date'], y=df_male['Rain'].rolling(7).mean(),
    name="7-Day Trend",
    line=dict(color='white', width=2, dash='dot')
), row=2, col=1)

# --- ROW 3: COMPARISON (Male' vs Addu) ---
fig.add_trace(go.Scatter(
    x=df_male['Date'], y=df_male['Temp'],
    name="Temp (Male')",
    line=dict(color='#00cc96')
), row=3, col=1)

fig.add_trace(go.Scatter(
    x=df_addu['Date'], y=df_addu['Temp'],
    name="Temp (Addu)",
    line=dict(color='#636EFA')
), row=3, col=1)

# --- 3. STYLING (Dark Mode like the Video) ---
fig.update_layout(
    template="plotly_dark",
    height=900,  # Tall dashboard
    title_text="<b>MALDIVES WEATHER ANALYTICS</b>",
    title_x=0.5, # Center title
    font=dict(family="Arial", size=12),
    showlegend=True,
    # The Slider! This mimics the video's interactivity
    xaxis2=dict(
        rangeslider=dict(visible=True),
        type="date"
    )
)

# --- 4. EXPORT ---
fig.write_html("index.html")
print("Dashboard Generated: index.html")
