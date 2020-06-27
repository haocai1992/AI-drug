# Import required libraries
import os
import pickle
import copy
import datetime as dt
import math

import requests
import pandas as pd
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

# Multi-dropdown options
from controls import CATEGORIES, REGIONS, METRICS, TABLE_COLUMNS

app = dash.Dash(__name__)
server = app.server


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
df = pd.read_csv('data/all_companies.csv')
dataset = df.to_dict(orient='index')


# Create global chart template
mapbox_access_token = 'pk.eyJ1Ijoic25ha2VicnlhbiIsImEiOiJja2J0dzZnaWEwMWxuMnhsYnUxZTBobWNqIn0.B0E9GC_uNHbz8b9BYDn0Ng'

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
    title='Satellite Overview',
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

# Create app layout
app.layout = html.Div(
    [
        # dcc.Store(id='aggregate_data'),
        html.Div(
            [
                html.Img(
                    # src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
                    src=app.get_asset_url('dash-logo.png'),
                    className='two columns',
                ),
                html.Div(
                    [
                        html.H2(
                            'AI-Drug',

                        ),
                        html.H4(
                            'Overview of AI starups in drug discovery field (until April 2020)',
                        )
                    ],

                    className='eight columns',
                    style={'textAlign': 'center'}
                ),
                html.A(
                    html.Button(
                        "Learn More",
                        id="learnMore"

                    ),
                    href="https://github.com/haocai1992/AI-drug",
                    className="two columns",
                    style={'textAlign': 'right'}
                )
            ],
            id="header",
            className='row',
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            'Choose a metric:',
                            className="control_label"
                        ),
                        dcc.RadioItems(
                            id='metric_selector',
                            options=metric_options,
                            value='number of startups',
                            labelStyle={'display': 'inline-block'},
                            className="dcc_control"
                        ),
                        html.P(
                            'Choose a region:',
                            className="control_label"
                        ),
                        dcc.RadioItems(
                            id='region_selector',
                            options=region_options,
                            value='All',
                            labelStyle={'display': 'inline-block'},
                            className='dcc_control'
                        ),
                        dcc.Dropdown(
                            id='country_selector',
                            options=country_options,
                            multi=True,
                            value=REGIONS['All'],
                            className='dcc_control'
                        ),
                        html.P(
                            'Choose R&D category',
                            className='control_label'
                        ),
                        dcc.Dropdown(
                            id='category_selector',
                            options=category_options,
                            value='All',
                            className='dcc_control'
                        ),
                    ],
                    className="pretty_container four columns"
                ),
                html.Div(
                    [
                        dcc.Graph(id='founded_year_graph')
                    ],
                    className='pretty_container eight columns'
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='venture_stage_graph')
                    ],
                    className='pretty_container six columns'
                ),
                html.Div(
                    [
                        dcc.Graph(id='country_pie_graph')
                    ],
                    className='pretty_container six columns'
                )
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='map_graph')
                    ],
                    className='pretty_container six columns',
                    id='map_graph-Container'
                ),
                html.Div(
                    [
                        dt.DataTable(
                            id='table',
                            columns=[{"name":i, "id":i} for i in TABLE_COLUMNS],
                            data=df.to_dict('rows'),
                            sort_action='native',
                            filter_action='native',
                            page_action='native',
                            page_current=0,
                            page_size=12,
                            style_cell={'fontSize':12, 'font-family':'arial'},
                            style_table={'overflowX': 'auto'},
                                style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                        ),
                        html.P(
                            '(click locations in the map to update table)',
                            className='control_label'
                        ),
                    ],
                    className='pretty_container six columns'
                )
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='category_graph'),
                        html.Button('Reset Category', id='reset_category'),
                    ],
                    className='six columns',
                    id='category_graph-Container'
                ),
                html.Div(
                    [
                        html.H6(
                            'Keywords in selected category',
                            style={'textAlign':'left'}
                        ),
                        html.Img(
                            src=app.get_asset_url('All.png'),
                            id='word_cloud_graph',
                            width='140%',
                        ),
                        html.P(
                            '(Click bars in R&D category graph to update word cloud)',
                            className='control_label',
                            style={'textAlign':'left'}
                        )
                    ],
                    className='four columns',
                    style={'textAlign': 'center'}
                ),
            ],
            className='pretty_container row'
        )
    ],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column"
    }
)


# Helper functions
def filter_dataframe(df, country_selector, category_selector):
    if category_selector=='All':
        dff = df[df['country'].isin(country_selector)]
    else:
        dff = df[(df['country'].isin(country_selector))
                & (df['category']==category_selector)]
    return dff

# Create callbacks

# Radio -> multi
@app.callback(Output('country_selector', 'value'),
              [Input('region_selector', 'value')])
def display_country(selector):
    return REGIONS[selector]


# selectors -> founded_year_graph
@app.callback(Output('founded_year_graph', 'figure'),
              [Input('metric_selector', 'value'),
               Input('country_selector', 'value'),
               Input('category_selector', 'value')])
def make_founded_year_graph(metric_selector, country_selector, category_selector):
    dff = filter_dataframe(df, country_selector, category_selector)
    if metric_selector == 'number of startups':
        dfff = dff.groupby('founded').size().reset_index().rename(columns={0:'number of startups'})
        fig = px.bar(dfff, x='founded', y='number of startups')
    if metric_selector == "$M of investment":
        dfff = dff.groupby('founded')['funding_amount'].sum().reset_index().rename(columns={'funding_amount': '$M of investment'})
        fig = px.bar(dfff, x='founded', y='$M of investment')
    fig.update_xaxes(range=[1990, 2020], dtick=5)
    fig.update_layout(title_text="Chronological Trend")
    return fig


# selectors -> venture_stage_graph
@app.callback(Output('venture_stage_graph', 'figure'),
              [Input('metric_selector', 'value'),
               Input('country_selector', 'value'),
               Input('category_selector', 'value')])
def make_venture_stage_graph(metric_selector, country_selector, category_selector):
    stages = ['Pre-seed', 'Seed', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'Acquired', 'IPO', 'Closed']
    df['funding_stage'] = pd.Categorical(df['funding_stage'], stages)
    dff = filter_dataframe(df, country_selector, category_selector)
    if metric_selector == 'number of startups':
        dfff = dff.groupby('funding_stage').size().reset_index().rename(columns={0:'number of startups'})
        fig = px.bar(dfff, x='funding_stage', y='number of startups')
    if metric_selector == "$M of investment":
        dfff = dff.groupby('funding_stage')['funding_amount'].sum().reset_index().rename(columns={'funding_amount': '$M of investment'})
        fig = px.bar(dfff, x='funding_stage', y='$M of investment')
    fig.update_xaxes(title_text='funding stage', tickangle=45)
    fig.update_layout(title_text="Venture Stages")
    return fig

# Selectors -> map_graph
@app.callback(Output('map_graph', 'figure'),
              [Input('metric_selector', 'value'),
               Input('country_selector', 'value'),
               Input('category_selector', 'value')])
def make_map(metric_selector, country_selector, category_selector):
    dff = filter_dataframe(df, country_selector, category_selector)
    if metric_selector == 'number of startups':
        dfff = dff.groupby('headquarters').size().reset_index().rename(columns={0:'number of startups'})
    if metric_selector == "$M of investment":
        bubble_metric = 'funding_amount'
        dfff = dff.groupby('headquarters')['funding_amount'].sum().reset_index().rename(columns={'funding_amount':'$M of investment'})
    dfff = dfff.merge(dff[['headquarters', 'latitude', 'longitude']],
                      on='headquarters', how='left')
    bubble_metric = metric_selector
    fig = px.scatter_mapbox(dfff,
                            lat='latitude',
                            lon='longitude',
                            size=bubble_metric,
                            color=bubble_metric,
                            range_color=[dfff[bubble_metric].min(), dfff[bubble_metric].max()],
                            hover_name="headquarters", 
                            hover_data=[], 
                            color_continuous_scale=px.colors.sequential.Viridis, 
                            size_max=15, zoom=1)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, )
    return fig

# Selectors/map click/map selection -> table
@app.callback(Output('table', 'data'),
              [Input('country_selector', 'value'),
               Input('category_selector', 'value'),
               Input('map_graph', 'clickData'),
               Input('map_graph', 'selectedData')])
def make_table(country_selector, category_selector, map_click, map_select):
    dff = filter_dataframe(df, country_selector, category_selector)
    headquarters_filter = []
    if map_click is None and map_select is None:
        return dff.to_dict('rows')
    if map_click is not None:
        headquarters_filter = [map_click['points'][0]['hovertext']]
    if map_select is not None:
        for point in map_select['points']:
            headquarters_filter.append(point['hovertext'])
    dff = dff[dff.headquarters.isin(set(headquarters_filter))]
    return dff.to_dict('rows')

# Reset table when click empty space in map.
@app.callback([Output('map_graph', 'clickData'),
               Output('map_graph', 'selectedData')],
              [Input('map_graph-Container', 'n_clicks')])
def reset_map_clickData(n_clicks):
    return [None, None]

# Selectors -> category_graph
@app.callback(Output('category_graph', 'figure'),
              [Input('metric_selector', 'value'),
               Input('country_selector', 'value'),
               Input('category_selector', 'value')])
def make_category_graph(metric_selector, country_selector, category_selector):
    phases = CATEGORIES[1:]
    df['category'] = pd.Categorical(df['category'], phases)
    dff = filter_dataframe(df, country_selector, category_selector='All')
    colors = ['#636EFA']*len(phases)
    if category_selector != 'All':
        colors[phases.index(category_selector)] = '#EF553B'
    if category_selector == 'All':
        colors = ['#636EFA']*len(phases)
    if metric_selector == 'number of startups':
        dfff = dff.groupby('category').size().reset_index().rename(columns={0:'number of startups'})
        fig = px.bar(dfff, y='category', x='number of startups', orientation='h', )
        fig.update_traces(marker_color=colors)
    if metric_selector == "$M of investment":
        dfff = dff.groupby('category')['funding_amount'].sum().reset_index().rename(columns={'funding_amount': '$M of investment'})
        fig = px.bar(dfff, y='category', x='$M of investment', orientation='h', )
        fig.update_traces(marker_color=colors)
    fig.update_layout(yaxis={'categoryorder':'array', 'categoryarray':phases[::-1]}, title_text="R&D category")
    return fig

# category_graph click -> category_selector
@app.callback(Output('category_selector', 'value'),
              [Input('category_graph', 'clickData')])
def click_category(category_graph_click):
    if category_graph_click is None:
        return 'All'
    if category_graph_click is not None:
        clicked_category = category_graph_click['points'][0]['y']
    return clicked_category

# Reset category when click "reset_category" button .
@app.callback(Output('category_graph', 'clickData'),
              [Input('reset_category', 'n_clicks')])
def reset_category_clickData(n_clicks):
    return None 

# category_selector -> word cloud
@app.callback(Output('word_cloud_graph', 'src'),
              [Input('category_selector', 'value')])
def make_word_cloud_graph(category_selector):
    return app.get_asset_url('{}.png'.format(category_selector))

# category_selector -> pie graph
@app.callback(Output('country_pie_graph', 'figure'),
              [Input('metric_selector', 'value'),
               Input('category_selector', 'value'),
               Input('country_selector', 'value')])
def make_country_pie_graph(metric_selector, category_selector, country_selector):
    dff = filter_dataframe(df, country_selector, category_selector)
    if metric_selector == 'number of startups':
        dfff = dff.groupby('country').size().reset_index().rename(columns={0:'number of startups'})
        fig = px.pie(dfff, 
                     values='number of startups', 
                     names='country')
    if metric_selector == "$M of investment":
        dfff = dff.groupby('country')['funding_amount'].sum().reset_index().rename(columns={'funding_amount': '$M of investment'})
        fig = px.pie(dfff, 
                     values='$M of investment', 
                     names='country')
    fig.update_layout(title_text="Countries")
    return fig


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
