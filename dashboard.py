import datetime as dt

import numpy as np
from flask_caching import Cache
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import io
import requests

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = px.colors.carto.Vivid + px.colors.carto.Bold

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

    if location_index is None:  # skip if data nothing to plot
        raise dash.exceptions.PreventUpdate

    df_cases, df_deaths = dataframe()  # get data from cache

    fig = make_subplots(rows=2, cols=1)
    i = 0
    if location_index is None:
        return {}
    else:
        try:
            for location in location_index:
                fig.add_trace(
                    go.Scatter(
                        y=df_cases.iloc[[location], 4:].values[0, :],
                        x=df_cases.iloc[[location], :].columns[4:],
                        name=location_options[location].get('label'),
                        legendgroup=location,
                        marker_color=colors[i],
                        opacity=0.8,
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        y=df_deaths.iloc[[location], 4:].values[0, :],
                        x=df_deaths.iloc[[location], :].columns[4:],
                        name=location_options[location].get('label'),
                        legendgroup=location,
                        marker_color=colors[i],
                        showlegend=False,
                        opacity=0.8,
                    ),
                    row=2, col=1
                )
                i += 1

        except TypeError:
            fig.add_trace(
                go.Scatter(
                    y=df_cases.iloc[[location_options], 4:].values[0, :],
                    x=df_cases.iloc[[location_options], :].columns[4:],
                    name=location_options[location].get('label'),
                    legendgroup=location,
                    marker_color=colors[0],
                    opacity=0.8,
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    y=df_deaths.iloc[[location_options], 4:].values[0, :],
                    x=df_deaths.iloc[[location_options], :].columns[4:],
                    name=location_options[location].get('label'),
                    legendgroup=location,
                    marker_color=colors[0],
                    showlegend=False,
                    opacity=0.8,
                ),
                row=2, col=1
            )


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
    fig.update_layout(
        height=800,
        title_text="Deaths and Confirmed Cases for States and Countries",
    )
    fig.update_yaxes(title="Total Cases Diagnosed", type=y_axis_type, tickvals=[1, 10, 100, 1000, 10000, 100000, 1000000], row=1, col=1)
    fig.update_yaxes(title="Total Deaths", type=y_axis_type, tickvals=[1, 10, 100, 1000, 10000, 100000, 1000000], row=2, col=1)
    fig.update_xaxes(showticklabels = False, dtick=1, row=1, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    return fig


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
