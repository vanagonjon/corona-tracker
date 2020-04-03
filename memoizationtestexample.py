import datetime as dt

import numpy as np
from flask_caching import Cache

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import io
import requests

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

server = app.server

TIMEOUT = 600


@cache.memoize(timeout=TIMEOUT)
def query_data():
    url = "https://raw.githubusercontent.com/vanagonjon/corona-tracker/master/time_series_19-covid-Confirmed.csv"
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace('/', '_')

    # Convert states to string, and remove nan values
    df['province_state'] = df['province_state'].astype(str).str.replace('nan', '')

    return df.to_json(date_format='iso', orient='split')


def dataframe():
    return pd.read_json(query_data(), orient='split')


def server_layout():
    site = html.Div([

        html.Div(id='setup', style={'display': 'none'}),  # Hidden div, loads data frames, and drop down data

        dcc.Dropdown( id='locationsdd',multi=True),

        html.Div(id='dd-output-container',
                 children=[
                     dcc.Graph(id='cases'),
                     dcc.RadioItems(
                         options=[
                             {'label': 'Linear', 'value': 'linear'},
                             {'label': 'Log', 'value': 'log'}
                         ],
                         value='log',
                         labelStyle={'display': 'inline-block'},
                         id='linlog'
                     ),
        ]),
    ])
    return site


app.layout = server_layout


@app.callback(
    Output('cases', 'figure'),
    [Input('locationsdd', 'value'),
     Input('locationsdd', 'options'),
     Input('linlog', 'value')])
def plot_data(location_index, location_options, y_axis_type):
    df = dataframe()

    if location_index is None:
        return {}
    else:
        try:
            fig_data = []
            for location in location_index:
                fig_data.append(
                    go.Scatter(
                        y=df.iloc[[location], 4:].values[0, :],
                        x=df.iloc[[location], :].columns[4:],
                        name=location_options[location].get('label'),
                        opacity=0.8,
                    )
                )
        except TypeError:
            fig_data = [go.Scatter(
                y=df.iloc[[location_options], 4:].values[0, :],
                x=df.iloc[[location_options], :].columns[4:],
                name=location_options[location].get('label'),
                opacity=0.8
            )]

    layout = go.Layout(
        xaxis={'type': 'category', 'title': "Date"},
        yaxis={'type': 'linear', 'title': "Total Cases Diagnosed"},
        yaxis_type=y_axis_type,
        margin={'l': 60, 'b': 100, 'r': 10, 't': 30},
    )
    figure={'data':fig_data,'layout':layout}

    return figure


@app.callback([Output('locationsdd', 'options'),
               Output('locationsdd', 'value')],
              [Input('setup', 'children')])
def setup(foo):
    df = dataframe()

    locations = df[['province_state', 'country_region']].agg(', '.join, axis=1).values.tolist()
    locations = [x.strip(', ') for x in locations]

    location_options = [{'label': locations[i], 'value': i} for i in df.index.tolist()]

    top_index = df.iloc[:, -1].sort_values(ascending=False).index.tolist()[0:15]

    return location_options, top_index


if __name__ == '__main__':
    app.run_server(debug=True)
