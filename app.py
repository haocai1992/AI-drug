import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate

import pandas as pd

# Multi-dropdown and Radioitems options
from controls import CATEGORIES, REGIONS, METRICS

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.config["suppress_callback_exceptions"] = True

# Create controls
category_options = [{'label': str(category),
                     'value': str(category)}
                    for category in CATEGORIES]

region_options = [{'label': str(region),
                   'value': str(region)}
                  for region in REGIONS]

country_options = [{'label': str(country),
                    'value': str(country)}
                   for country in REGIONS['All']]

metric_options = [{'label': str(metric),
                   'value': str(metric)}
                  for metric in METRICS]

# Load data
df = pd.read_csv('./data/all_companies.csv')

# Plotly mapbox token
mapbox_access_token = "pk.eyJ1Ijoic25ha2VicnlhbiIsImEiOiJja2J0dzZnaWEwMWxuMnhsYnUxZTBobWNqIn0.B0E9GC_uNHbz8b9BYDn0Ng"

# Create global chart template
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Geographical Distribution',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-78.05,
            lat=42.54
        ),
        zoom=7,
    )
)

app.layout = html.Div([
    html.Div([

        html.Div([
            html.Label(
                'Select a metric:',
                className="control_label"
            ),
            dcc.RadioItems(
                id='metric_selector',
                options=metric_options,
                value='number of startups',
                labelStyle={'display': 'inline-block'}
            ),
            html.Label(
                'Select R&D category:',
                className="control_label"
            ),
            dcc.Dropdown(
                id='category_selector',
                options=category_options,
                multi=False,
                value='All',
                className="dcc_control"
            ),
            html.Label(
                'Filter by region:',
                className="control_label"
            ),
            dcc.RadioItems(
                id='region_selector',
                options=region_options,
                value='All',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Dropdown(
                id='country_selector',
                options=country_options,
                multi=True,
                value=REGIONS['All'],
                className="dcc_control"
            ),
        ],
        style={'width': '49%', 'display': 'inline-block'}),
    ])])




if __name__ == '__main__':
    app.run_server(debug=True)