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
    url_cases = "https://raw.githubusercontent.com/vanagonjon/corona-tracker/master/time_series_19-covid-Confirmed.csv"
    url_deaths = "https://raw.githubusercontent.com/vanagonjon/corona-tracker/master/time_series_19-covid-Deaths.csv"
    s_cases = requests.get(url_cases).content
    df_cases = pd.read_csv(io.StringIO(s_cases.decode('utf-8')))
    s_deaths = requests.get(url_deaths).content
    df_deaths = pd.read_csv(io.StringIO(s_deaths.decode('utf-8')))
    # Clean column names
    df_cases.columns = df_cases.columns.str.strip().str.lower().str.replace('/', '_')
    df_deaths.columns = df_deaths.columns.str.strip().str.lower().str.replace('/', '_')
    # Convert states to string, and remove nan values
    df_cases['province_state'] = df_cases['province_state'].astype(str).str.replace('nan', '')
    df_deaths['province_state'] = df_deaths['province_state'].astype(str).str.replace('nan', '')

    return df_cases.to_json(date_format='iso', orient='split'), df_deaths.to_json(date_format='iso', orient='split')


def dataframe():
    df_cases, df_deaths = query_data()
    return pd.read_json(df_cases, orient='split'), pd.read_json(df_deaths, orient='split')


def server_layout():
    site = html.Div([

        html.Div(id='setup', style={'display': 'none'}),  # Hidden div, loads data frames, and drop down data

        dcc.Dropdown(id='locationsdd', multi=True),

        html.Div(id='dd-output-container',
                 children=[
                     dcc.RadioItems(
                         options=[
                             {'label': 'Linear', 'value': 'linear'},
                             {'label': 'Log', 'value': 'log'}
                         ],
                         value='log',
                         labelStyle={'display': 'inline-block'},
                         id='linlog'
                     ),
                     dcc.Graph(id='cases'),
                     dcc.Graph(id='deaths'),
                 ]),
    ])
    return site


app.layout = server_layout


@app.callback(
    [Output('cases', 'figure'),
     Output('deaths', 'figure')],
    [Input('locationsdd', 'value'),
     Input('locationsdd', 'options'),
     Input('linlog', 'value')])
def plot_data(location_index, location_options, y_axis_type):

    if location_index is None:  # skip if data nothing to plot
        raise dash.exceptions.PreventUpdate

    df_cases, df_deaths = dataframe()  # get data from cache

    if location_index is None:
        return {}
    else:
        try:
            fig_data_case = []
            fig_data_deaths = []
            for location in location_index:
                fig_data_case.append(
                    go.Scatter(
                        y=df_cases.iloc[[location], 4:].values[0, :],
                        x=df_cases.iloc[[location], :].columns[4:],
                        name=location_options[location].get('label'),
                        opacity=0.8,
                    )
                )
                fig_data_deaths.append(
                    go.Scatter(
                        y=df_deaths.iloc[[location], 4:].values[0, :],
                        x=df_deaths.iloc[[location], :].columns[4:],
                        name=location_options[location].get('label'),
                        opacity=0.8,
                    )
                )
        except TypeError:
            fig_data_case = [go.Scatter(
                y=df_cases.iloc[[location_options], 4:].values[0, :],
                x=df_cases.iloc[[location_options], :].columns[4:],
                name=location_options[location].get('label'),
                opacity=0.8
            )]
            fig_data_deaths = [go.Scatter(
                y=df_deaths.iloc[[location_options], 4:].values[0, :],
                x=df_deaths.iloc[[location_options], :].columns[4:],
                name=location_options[location].get('label'),
                opacity=0.8
            )]

    layout_case = go.Layout(
        xaxis={'type': 'category', 'title': "Date"},
        yaxis={'type': 'linear', 'title': "Total Cases Diagnosed"},
        yaxis_type=y_axis_type,
        margin={'l': 60, 'b': 100, 'r': 10, 't': 30},
    )
    layout_death = go.Layout(
        xaxis={'type': 'category', 'title': "Date"},
        yaxis={'type': 'linear', 'title': "Total Deaths"},
        yaxis_type=y_axis_type,
        margin={'l': 60, 'b': 100, 'r': 10, 't': 30},
    )
    figure_cases = {'data': fig_data_case, 'layout': layout_case}
    figure_deaths = {'data': fig_data_deaths, 'layout': layout_death}

    return figure_cases, figure_deaths


@app.callback([Output('locationsdd', 'options'),
               Output('locationsdd', 'value')],
              [Input('setup', 'children')])
def setup(foo):
    df, df2 = dataframe()

    locations = df[['province_state', 'country_region']].agg(', '.join, axis=1).values.tolist()
    locations = [x.strip(', ') for x in locations]

    location_options = [{'label': locations[i], 'value': i} for i in df.index.tolist()]

    top_index = df.iloc[:, -1].sort_values(ascending=False).index.tolist()[0:15]

    return location_options, top_index


if __name__ == '__main__':
    app.run_server(debug=True)
