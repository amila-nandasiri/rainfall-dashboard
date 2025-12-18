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
# 2. CREATE DASHBOARD (DEEPMIND / DARK MODE STYLE)
# ------------------------------------------------------------------------------
df = get_weather_data()

if not df.empty:
    # Create Figure with Dual Axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # --- STYLE CONFIGURATION ---
    # Colors based on the "DeepMind" aesthetic
    BG_COLOR = "#101010"       # Deep charcoal/black
    TEXT_COLOR = "#E0E0E0"     # Off-white for text
    BAR_COLOR = "#8AB4F8"      # Google Light Blue (Rain)
    LINE_COLOR = "#F28B82"     # Soft Red/Coral (Temp) - High contrast against dark
    GRID_COLOR = "#333333"     # Subtle grid lines

    # 1. Plot Rainfall (Bar Chart)
    fig.add_trace(
        go.Bar(
            x=df['Date'], y=df['Rain'],
            name="Rainfall (mm)",
            marker_color=BAR_COLOR,
            marker_line_width=0, # Clean, no borders
            opacity=0.9
        ), secondary_y=False
    )

    # 2. Plot Temperature (Line Chart)
    fig.add_trace(
        go.Scatter(
            x=df['Date'], y=df['Temp'],
            name="Temperature (°C)",
            line=dict(color=LINE_COLOR, width=3),
            mode='lines+markers',
            marker=dict(size=6, color=BG_COLOR, line=dict(width=2, color=LINE_COLOR)) # Hollow circle effect
        ), secondary_y=True
    )

    # --- VISUALS & LAYOUT ---
    today_date = pd.Timestamp.now().normalize()

    # Vertical Line for "Today"
    fig.add_vline(x=today_date, line_dash="dot", line_color="#5f6368", line_width=1)
    
    # "Today" Text Label
    fig.add_annotation(
        x=today_date, y=1.05, yref="paper",
        text="TODAY",
        showarrow=False,
        font=dict(color="#9AA0A6", size=10, family="Roboto, Arial, sans-serif")
    )

    fig.update_layout(
        title=dict(
            text="<b>Male' City Weather</b>",
            font=dict(size=24, color="white", family="Roboto, sans-serif"),
            x=0.05, # Align left like the screenshot
            y=0.95
        ),
        # Dark Theme Settings
        template="plotly_dark",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family="Roboto, sans-serif", color=TEXT_COLOR),
        height=600,
        hovermode="x unified",
        
        # Legend styling (Top Right, minimal)
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=12, color="#9AA0A6")
        ),
        
        # Rangeslider styling to match dark theme
        xaxis=dict(
            type="date",
            showgrid=False,
            color="#9AA0A6",
            rangeslider=dict(visible=True, bgcolor=BG_COLOR, bordercolor=GRID_COLOR),
        )
    )

    # Customize Axis Grids (Subtle)
    fig.update_yaxes(
        title_text="Rainfall (mm)", 
        secondary_y=False, 
        showgrid=True, 
        gridcolor=GRID_COLOR, 
        zerolinecolor=GRID_COLOR,
        color="#9AA0A6"
    )
    fig.update_yaxes(
        title_text="Temperature (°C)", 
        secondary_y=True, 
        showgrid=False, 
        color=LINE_COLOR # Match the axis text color to the line
    )

    # Footer Credit (Styled)
    fig.add_annotation(
        x=0.5, y=-0.25, xref='paper', yref='paper',
        text="Data Source: <a href='https://open-meteo.com/' style='color: #8AB4F8;'>Open-Meteo API</a>",
        showarrow=False, 
        font=dict(size=11, color="#5f6368")
    )

    # Save as HTML
    fig.write_html("index.html")
    print("Dashboard updated successfully!")

else:
    print("Failed to fetch data.")
