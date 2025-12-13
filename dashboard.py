import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import dash_bootstrap_components as dbc
import requests

# ------------------------------------------------------------------------------
# 1. CONFIGURATION & API SETUP
# ------------------------------------------------------------------------------
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY_HERE"  # <--- PASTE YOUR KEY HERE
CITY = "Male"
LAT = "4.1755"  # Latitude for Male', Maldives
LON = "73.5093" # Longitude for Male', Maldives

# ------------------------------------------------------------------------------
# 2. DATA PROCESSING (LIVE API ONLY)
# ------------------------------------------------------------------------------

def get_data():
    # We are now ONLY fetching live forecast data (approx 5 days / 3-hour intervals)
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    
    forecast_data = []
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            for item in data['list']:
                forecast_data.append({
                    'Date': pd.to_datetime(item['dt_txt']),
                    'Male_Rainfall': item.get('rain', {}).get('3h', 0), # Rain volume for last 3h
                    'Male_Temperature': item['main']['temp']
                })
        else:
            print(f"API Error: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Connection Error: {e}")

    df = pd.DataFrame(forecast_data)
    
    # Sort just in case
    if not df.empty:
        df = df.sort_values(by='Date')
    
    return df

# Load Data once on startup
df = get_data()

# ------------------------------------------------------------------------------
# 3. APP SETUP (Light Mode)
# ------------------------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# ------------------------------------------------------------------------------
# 4. FIGURE CREATION
# ------------------------------------------------------------------------------

def create_figure(dataframe):
    if dataframe.empty:
        return go.Figure().update_layout(
            title="No Data Available. Please check your API Key.",
            plot_bgcolor='white'
        )

    # Create figure with secondary y-axis (Left: Rain, Right: Temp)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Rainfall (Bar Chart)
    fig.add_trace(
        go.Bar(
            x=dataframe['Date'], 
            y=dataframe['Male_Rainfall'], 
            name="Rainfall (mm/3h)",
            marker_color='#50C878', # Mint Green
            opacity=0.7
        ),
        secondary_y=False,
    )

    # 2. Temperature (Line Chart)
    fig.add_trace(
        go.Scatter(
            x=dataframe['Date'], 
            y=dataframe['Male_Temperature'], 
            name="Temperature (°C)",
            line=dict(color='#007BFF', width=3),
            mode='lines+markers' # Markers added so you can see the 3h points clearly
        ),
        secondary_y=True,
    )

    # Layout Updates
    fig.update_layout(
        title="Male' Weather Forecast (Next 5 Days)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='black',
        height=500,
        legend=dict(orientation="h", y=1.02, x=1),
        
        # DATE AXIS CONFIGURATION
        xaxis=dict(
            type="date",
            rangeslider=dict(visible=True), 
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=3, label="3d", step="day", stepmode="backward"),
                    dict(step="all", label="All 5 Days")
                ])
            ),
        )
    )

    # Axis Formatting
    fig.update_yaxes(title_text="Rainfall (mm)", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True, showgrid=True, gridcolor='#eee')
    
    return fig

# ------------------------------------------------------------------------------
# 5. APP LAYOUT
# ------------------------------------------------------------------------------
app.layout = dbc.Container([
    html.Br(),
    
    # Header
    dbc.Row([
        dbc.Col([
            html.H2("Male' Weather Analytics", className="text-primary"),
            html.P("Real-Time 5-Day Forecast", className="text-muted")
        ], width=12)
    ]),
    
    html.Hr(),

    # Graph
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=create_figure(df), config={'displayModeBar': False})
        ], width=12)
    ]),

    # Footer with Data Source Credit
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Small([
                "Live Data provided by ",
                html.A("OpenWeatherMap", href="https://openweathermap.org/", target="_blank")
            ], className="text-muted")
        ], width=12, style={'text-align': 'center', 'margin-top': '20px'})
    ])

], fluid=True, style={'background-color': '#ffffff', 'min-height': '100vh'})

# ------------------------------------------------------------------------------
# 6. RUN SERVER
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
