import os
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Initialize App
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # expose for Render

# Header
header = html.Div(
    [
        html.H1("SISTEM MONITORING DATA V1.0", className="display-4 text-white text-center"),
        html.P("Visualisasi IOC Sea Monitoring Data", className="lead text-white text-center"),
    ],
    style={
        "backgroundColor": "#2c3e50",
        "padding": "20px 0px",
        "marginBottom": "0px"
    }
)

# Layout
app.layout = html.Div([
    header,

    dbc.Container([
        # Tabs Navigation
        dcc.Tabs(id="nav-tabs", value='/dashboard', children=[
            dcc.Tab(label="Tide Indonesia", value='/tide-dashboard',
                    selected_style={'fontWeight': 'bold', 'borderTop': '3px solid #18bc9c'}),
            dcc.Tab(label="Tide + EQ", value='/dashboard',
                    selected_style={'fontWeight': 'bold', 'borderTop': '3px solid #18bc9c'}),
            dcc.Tab(label="Tide Analysis", value='/analysis',
                    selected_style={'fontWeight': 'bold', 'borderTop': '3px solid #18bc9c'}),
        ], style={'height': '50px', 'marginTop': '10px'}, className="mb-4"),

        # URL detection
        dcc.Location(id='url', refresh=False),

        # Page container
        html.Div(dash.page_container,
                 style={"padding": "20px", "backgroundColor": "#f8f9fa", "borderRadius": "10px"})
    ], fluid=True)
])

# Callback to sync tabs with URL
@app.callback(
    Output('url', 'pathname'),
    Input('nav-tabs', 'value')
)
def update_url(tab_value):
    return tab_value

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)
