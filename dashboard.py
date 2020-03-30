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

server = app.server


def server_layout():
    site = html.Div([
        html.Div(id='setup', style={'display': 'none'}),  # Hidden div, loads data frames, and drop down data

        html.Div(id='diagnosed_cache', style={'display': 'none'}),  # Hidden div, caches data frame

        dcc.Dropdown(
            id='locationsdd',
            multi=True,
        ),

        # dcc.Graph(id='main_graph'),
        html.Div(id='dd-output-container'),

        dcc.RadioItems(
            options=[
                {'label': 'Linear', 'value': 'linear'},
                {'label': 'Log', 'value': 'log'}
            ],
            value='log',
            labelStyle={'display': 'inline-block'},
            id='linlog'
        ),
    ])
    return site


app.layout = server_layout


@app.callback(
    Output('dd-output-container', 'children'),
    [Input('locationsdd', 'value'),
     Input('locationsdd', 'options'),
     Input('linlog', 'value'),
     Input('diagnosed_cache', 'children')])
def plot_data(location_index, location_options, y_axis_type, cached_data):
    if cached_data is None:
        raise dash.exceptions.PreventUpdate

    df = pd.read_json(cached_data)

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
        margin={'l': 60, 'b': 40, 'r': 10, 't': 10},
    )
    figure = dcc.Graph(figure=go.Figure(
        data=fig_data,
        layout=layout))

    # slides = dcc.Slider(
    #     min=0,
    #     max=10,
    #     step=None,
    #     marks={
    #         0: '0 °F',
    #         3: '3 °F',
    #         5: '5 °F',
    #         7.65: '7.65 °F',
    #         10: '10 °F'
    #     },
    #     value=5
    # )

    children = [
        html.Div(id='test', children=[
            figure,
        ])
    ]
    return children


# Called on page load, imports data from web and creates dataframe, options for drop down, and default selections to
# include in plot
@app.callback([Output('diagnosed_cache', 'children'),
               Output('locationsdd', 'options'),
               Output('locationsdd', 'value')],
              [Input('setup', 'children')])
def setup(foo):
    url = "https://raw.githubusercontent.com/vanagonjon/corona-tracker/timeshift/time_series_19-covid-Confirmed.csv"
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace('/', '_')

    # Convert states to string, and remove nan values
    df['province_state'] = df['province_state'].astype(str).str.replace('nan', '')

    locations = df[['province_state', 'country_region']].agg(', '.join, axis=1).values.tolist()
    locations = [x.strip(', ') for x in locations]

    location_options = [{'label': locations[i], 'value': i} for i in df.index.tolist()]

    top_index = df.iloc[:, -1].sort_values(ascending=False).index.tolist()[1:15]

    return df.to_json(), location_options, top_index


if __name__ == '__main__':
    app.run_server(debug=True)
