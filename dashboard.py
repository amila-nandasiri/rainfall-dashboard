import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ------------------------------------------------------------------------------
# 1. FETCH DATA (Open-Meteo Free API)
# ------------------------------------------------------------------------------
def get_weather_data():
    # Male' City Coordinates
    lat = 4.1755
    lon = 73.5093
    
    # API Request: Daily Rain & Max Temp (14 days history + 5 days forecast)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,precipitation_sum&past_days=14&forecast_days=5&timezone=auto"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Organize data into a table
        daily = data['daily']
        df = pd.DataFrame({
            'Date': pd.to_datetime(daily['time']),
            'Rain': daily['precipitation_sum'],
            'Temp': daily['temperature_2m_max']
        })
        
        # Tag Past vs Future
        today = pd.Timestamp.now().normalize()
        df['Type'] = df['Date'].apply(lambda x: 'Forecast' if x >= today else 'History')
        
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------------------------
# 2. CREATE DASHBOARD
# ------------------------------------------------------------------------------
df = get_weather_data()

if not df.empty:
    # Create Figure with Dual Axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Plot Rainfall (Bar Chart)
    fig.add_trace(
        go.Bar(
            x=df['Date'], y=df['Rain'],
            name="Rainfall (mm)",
            marker_color='#4BC0C0',  # Clean Teal/Cyan for light mode
            opacity=0.7
        ), secondary_y=False
    )

    # Plot Temperature (Line Chart)
    fig.add_trace(
        go.Scatter(
            x=df['Date'], y=df['Temp'],
            name="Temperature (°C)",
            line=dict(color='#FF6384', width=3), # Nice Red/Pink for temp
            mode='lines+markers'
        ), secondary_y=True
    )

    # Add "Today" Reference Line
    today_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    fig.add_vline(x=today_date, line_dash="dash", line_color="gray", annotation_text="Today")

    # Clean Light Mode Styling
    fig.update_layout(
        title="<b>Male' City Weather Dashboard</b><br><sup>Past 14 Days + 5 Day Forecast</sup>",
        template="plotly_white",  # Built-in clean light theme
        hovermode="x unified",
        height=600,
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
        
        # Footer Credit
        annotations=[dict(
            x=0.5, y=-0.15, xref='paper', yref='paper',
            text="Data Source: <a href='https://open-meteo.com/'>Open-Meteo API</a> (Free License)",
            showarrow=False, font=dict(size=12, color="gray")
        )]
    )

    # Axis Titles
    fig.update_yaxes(title_text="Rainfall (mm)", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="Max Temperature (°C)", secondary_y=True, showgrid=True, gridcolor='#eee')

    # Save as HTML
    fig.write_html("index.html")
    print("Dashboard updated successfully!")
else:
    print("Failed to fetch data.")
