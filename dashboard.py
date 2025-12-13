import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
# We will fetch data for two locations to make the dashboard impressive
LOCATIONS = {
    "Male'": {"lat": 4.1755, "lon": 73.5093},
    "Addu City (Gan)": {"lat": -0.6931, "lon": 73.1585}
}

# --- FUNCTION TO GET DATA ---
def get_rainfall_data(city_name, lat, lon):
    # Fetch last 90 days of data + 3 days forecast
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&past_days=90&forecast_days=3&timezone=auto"
    
    response = requests.get(url)
    data = response.json()
    
    # Extract the daily data
    df = pd.DataFrame({
        'Date': data['daily']['time'],
        'Rainfall_mm': data['daily']['precipitation_sum'],
        'City': city_name
    })
    return df

# --- MAIN EXECUTION ---
print("Fetching data...")
df_male = get_rainfall_data("Male'", LOCATIONS["Male'"]["lat"], LOCATIONS["Male'"]["lon"])
df_gan = get_rainfall_data("Addu City", LOCATIONS["Addu City (Gan)"]["lat"], LOCATIONS["Addu City (Gan)"]["lon"])

# Combine both datasets
df_combined = pd.concat([df_male, df_gan])

# --- VISUALIZATION ---
print("Generating chart...")
fig = px.bar(df_combined, x='Date', y='Rainfall_mm', 
             color='City', 
             barmode='group',
             title="Maldives Rainfall Comparison: Male' vs. Addu City (Last 90 Days)",
             labels={'Rainfall_mm': 'Precipitation (mm)'},
             color_discrete_map={"Male'": "#00CC96", "Addu City": "#636EFA"})

# Polish the layout
fig.update_layout(
    template="plotly_dark",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Date",
    yaxis_title="Rainfall (mm)",
    legend_title="Location",
    hovermode="x unified"
)

# Add a timestamp so users know when it was last updated
last_updated = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
fig.add_annotation(
    text=f"Last Updated: {last_updated} | Data Source: Open-Meteo API",
    xref="paper", yref="paper",
    x=0, y=-0.2, showarrow=False,
    font=dict(size=10, color="gray")
)

# --- SAVE AS HTML ---
fig.write_html("index.html")
print("Done! index.html created.")
