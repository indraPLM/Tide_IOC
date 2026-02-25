import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Inisialisasi App
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# 1. Definisikan Header (Title)
header = html.Div(
    [
        html.H1("SISTEM MONITORING DATA V1.0", className="display-4 text-white text-center"),
        html.P(
            "Visualisasi IOC Sea Monitoring Data",
            className="lead text-white text-center",
        ),
    ],
    style={
        "backgroundColor": "#2c3e50", # Warna biru gelap profesional
        "padding": "20px 0px",
        "marginBottom": "0px"
    }
)

# 2. Layout Utama
app.layout = html.Div([
    header, # Title Header muncul pertama
    
    dbc.Container([
        # Tab Navigasi di bawah Header
        dcc.Tabs(id="nav-tabs", value='/', children=[
            dcc.Tab(label="Tide Indonesia", value='/tide_dashboard', 
                    selected_style={'fontWeight': 'bold', 'borderTop': '3px solid #18bc9c'}),
            dcc.Tab(label="Tide_Eq", value='/eq_tide_dashboard', 
                    selected_style={'fontWeight': 'bold', 'borderTop': '3px solid #18bc9c'}),
            dcc.Tab(label="Tide_Analysis", value='/eq_tide_dashboard', 
                    selected_style={'fontWeight': 'bold', 'borderTop': '3px solid #18bc9c'}),
        ], style={'height': '50px', 'marginTop': '10px'}, className="mb-4"),

        # Komponen Deteksi URL
        dcc.Location(id='url', refresh=False),

        # Area Konten (Sub-apps akan muncul di sini)
        html.Div(dash.page_container, style={"padding": "20px", "backgroundColor": "#f8f9fa", "borderRadius": "10px"})
        
    ], fluid=True)
])

# Callback untuk sinkronisasi Tab dengan URL
@app.callback(
    Output('url', 'pathname'),
    Input('nav-tabs', 'value')
)
def update_url(tab_value):
    return tab_value

if __name__ == '__main__':
    app.run_server(debug=True)
