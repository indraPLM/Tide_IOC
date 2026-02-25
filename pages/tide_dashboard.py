# pages/tide_dashboard.py

import os
import requests
import pandas as pd
import folium
from dash import dcc, html
from dash.dependencies import Input, Output
import dash
import plotly.subplots as sp
import plotly.graph_objs as go

# Register this file as a Dash page
dash.register_page(__name__, path="/tide_dashboard", name="IOC Tide Dashboard")

API_KEY = os.getenv("IOC_API_KEY", "your_default_key_here")

# --- Fetch IOC Stations ---
def get_stations():
    url = "https://api.ioc-sealevelmonitoring.org/v2/stations"
    params = {"showall": "all", "order": "code", "dir": "asc", "limit": 2000}
    headers = {"X-Api-Key": API_KEY, "Accept": "application/json"}
    response = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(response.json())

stations_df = get_stations()

# --- Regional Filters ---
def filter_region(df, lon_min, lon_max, lat_min, lat_max):
    return df[
        (df["country"] == "IDN") &
        (df["Lon"].between(lon_min, lon_max)) &
        (df["Lat"].between(lat_min, lat_max))
    ]

sumatra_df = filter_region(stations_df, 90, 104, -5, 6)
java_df    = filter_region(stations_df, 104, 118, -12, -5)
sulawesi_df= filter_region(stations_df, 118, 128, -5, 5)
papua_df   = filter_region(stations_df, 128, 145, -8, 2)

# --- Build Folium Map ---
def build_map(df):
    tiles = "https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
    m = folium.Map(location=[-12, 115], tiles=tiles, attr="ESRI", zoom_start=4.5)
    for _, row in df.iterrows():
        if pd.notnull(row["Lat"]) and pd.notnull(row["Lon"]):
            popup_text = f""" 
            <b>Code:</b> {row['Code']}<br> 
            <b>Location:</b> {row['Location']}<br> 
            <b>Country:</b> {row['country']}<br> 
            <b>Status:</b> {row['status']} """
            marker_color = "red" if row["status"] == 5 else "green" if row["status"] == 1 else "blue"
            folium.Marker(
                location=[row["Lat"], row["Lon"]],
                popup=popup_text,
                tooltip=row["Code"],
                icon=folium.Icon(color=marker_color, icon="info-sign")
            ).add_to(m)
    return m._repr_html_()

map_html = build_map(stations_df)

# --- Fetch Tide Gauge Data ---
def fetch_data(station_id, sensor="one-sensor",
               start_date="2026-02-20", end_date="2026-02-23"):
    station_id = station_id.lower()
    url = f"https://api.ioc-sealevelmonitoring.org/v2/research/stations/{station_id}/sensors/{sensor}/data"
    params = {"days_per_page": 7, "page": 1,
              "timestart": start_date, "timestop": end_date, "flag_qc": "true"}
    headers = {"X-Api-Key": API_KEY, "Accept": "application/json"}
    r = requests.get(url, params=params, headers=headers)

    if r.status_code == 200:
        js = r.json()
        if "data" in js and len(js["data"]) > 0:
            df = pd.DataFrame(js["data"])
            if "stime" in df.columns:
                df["stime"] = pd.to_datetime(df["stime"])
            return df
    return pd.DataFrame(columns=["stime", "slevel"])

# --- Helper to build subplot figure ---
def build_subplot(stations_df, title, cols, rows):
    stations = stations_df["Code"].tolist()
    fig = sp.make_subplots(rows=rows, cols=cols,
                           subplot_titles=[code.upper() for code in stations])
    for i, code in enumerate(stations):
        df = fetch_data(code)
        row = i // cols + 1
        col = i % cols + 1
        if not df.empty and "stime" in df.columns:
            fig.add_trace(
                go.Scatter(x=df["stime"], y=df["slevel"],
                           mode="lines", name=code.upper()),
                row=row, col=col
            )
    fig.update_layout(title_text=title, height=300*rows)
    return fig

# --- Page Layout ---
layout = html.Div([
    html.H1("IOC Indonesia Tide Gauge Dashboard"),

    html.Iframe(id="map", srcDoc=map_html, width="100%", height="500"),

    html.Div([
        html.H2("Sumatra Tide Gauges"),
        dcc.Graph(id="sumatra-graph"),

        html.H2("Java Tide Gauges"),
        dcc.Graph(id="java-graph"),

        html.H2("Sulawesi Tide Gauges"),
        dcc.Graph(id="sulawesi-graph"),

        html.H2("Papua Tide Gauges"),
        dcc.Graph(id="papua-graph"),
    ])
])

# --- Callbacks ---
@dash.callback(Output("sumatra-graph","figure"), Input("map","srcDoc"))
def update_sumatra(_):
    if sumatra_df.empty:
        return {"data":[],"layout":{"title":"No Sumatra stations"}}
    return build_subplot(sumatra_df, "Sumatra Sea Level", cols=3, rows=7)

@dash.callback(Output("java-graph","figure"), Input("map","srcDoc"))
def update_java(_):
    if java_df.empty:
        return {"data":[],"layout":{"title":"No Java stations"}}
    return build_subplot(java_df, "Java Sea Level", cols=3, rows=9)

@dash.callback(Output("sulawesi-graph","figure"), Input("map","srcDoc"))
def update_sulawesi(_):
    if sulawesi_df.empty:
        return {"data":[],"layout":{"title":"No Sulawesi stations"}}
    return build_subplot(sulawesi_df, "Sulawesi Sea Level", cols=3, rows=2)

@dash.callback(Output("papua-graph","figure"), Input("map","srcDoc"))
def update_papua(_):
    if papua_df.empty:
        return {"data":[],"layout":{"title":"No Papua stations"}}
    return build_subplot(papua_df, "Papua Sea Level", cols=3, rows=2)
