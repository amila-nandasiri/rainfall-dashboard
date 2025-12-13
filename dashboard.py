import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import dash_bootstrap_components as dbc
import requests

# ------------------------------------------------------------------------------
# 1. DATA PROCESSING (OPEN-METEO: NO KEY NEEDED)
# ------------------------------------------------------------------------------

def get_data():
    # Male', Maldives Coordinates
    lat = 4.1755
    lon = 73.5093
    
    # We ask Open-Meteo for: 
    # - hourly temperature and rain
    # - past_days=30 (History)
    # - forecast_days=7 (Forecast)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,rain&past_days=30&forecast_days=7&timezone=auto"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Open-Meteo returns 'hourly' data as separate lists. We align them in a DataFrame.
        hourly_data = data['hourly']
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(hourly_data['time']),
            'Male_Temperature': hourly_data['temperature_2m'],
            'Male_Rainfall': hourly_data['rain']
        })
        
        # Tagging data as Historical vs Forecast
        # Everything before "now" is history
        now = pd.Timestamp.now()
        df['Type'] = df['Date'].apply(lambda x: 'Historical' if x < now else 'Forecast')
        
        return df

    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame() # Return empty if error

# Load Data
df = get_data()

# ------------------------------------------------------------------------------
# 2. APP SETUP (Light Mode)
# ------------------------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# ------------------------------------------------------------------------------
# 3. FIGURE CREATION
# ------------------------------------------------------------------------------

def create_figure(dataframe):
    if dataframe.empty:
        return go.Figure().update_layout(title="Error loading data. Check internet connection.")

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Rainfall (Bar Chart)
    fig.add_trace(
        go.Bar(
            x=dataframe['Date'], 
            y=dataframe['Male_Rainfall'], 
            name="Rainfall (mm)",
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
            line=dict(color='#007BFF', width=2),
            mode='lines'
        ),
        secondary_y=True,
    )

    # Visual Marker: Where does Forecast start?
    # Find the first row where Type is 'Forecast'
    forecast_df = dataframe[dataframe['Type'] == 'Forecast']
    if not forecast_df.empty:
        forecast_start = forecast_df['Date'].iloc[0]
        fig.add_vline(x=forecast_start, line_width=1, line_dash="dash", line_color="grey")
        fig.add_annotation(x=forecast_start, y=1.05, yref="paper", text="Forecast Start", showarrow=False)

    # Layout Updates
    fig.update_layout(
        title="Male' Weather: Last 30 Days + 7 Day Forecast",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='black',
        height=500,
        legend=dict(orientation="h", y=1.02, x=1),
        
        # DATE AXIS & SLIDER
        xaxis=dict(
            type="date",
            rangeslider=dict(visible=True), 
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=14, label="2w", step="day", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
        )
    )

    # Axis Formatting
    fig.update_yaxes(title_text="Rainfall (mm)", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True, showgrid=True, gridcolor='#eee')
    
    return fig

# ------------------------------------------------------------------------------
# 4. APP LAYOUT
# ------------------------------------------------------------------------------
app.layout = dbc.Container([
    html.Br(),
    
    # Header
    dbc.Row([
        dbc.Col([
            html.H2("Male' Weather Analytics", className="text-primary"),
            html.P("Live Data Integration (No API Key Required)", className="text-muted")
        ], width=12)
    ]),
    
    html.Hr(),

    # Graph
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=create_figure(df), config={'displayModeBar': False})
        ], width=12)
    ]),

    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Small([
                "Data provided by ",
                html.A("Open-Meteo.com", href="https://open-meteo.com/", target="_blank"),
                " (Creative Commons Attribution 4.0)"
            ], className="text-muted")
        ], width=12, style={'text-align': 'center', 'margin-top': '20px'})
    ])

], fluid=True, style={'background-color': '#ffffff', 'min-height': '100vh'})

# ------------------------------------------------------------------------------
# 5. RUN SERVER
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
