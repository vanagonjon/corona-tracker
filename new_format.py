import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import io
import requests

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Grab JH data and make dataframe
#url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series" \
#      "/time_series_covid19_confirmed_global.csv"

url = "https://raw.githubusercontent.com/vanagonjon/corona-tracker/timeshift/time_series_19-covid-Confirmed.csv"
s = requests.get(url).content
df = pd.read_csv(io.StringIO(s.decode('utf-8')))
# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace('/', '_')

dfb = df[df['country_region'].str.contains("Mass")].index
print(dfb)

# Convert states to string, and remove nan values
df['province_state'] = df['province_state'].astype(str).str.replace('nan', '')
# Concatenate state and country names in a list
locations = df[['province_state', 'country_region']].agg(', '.join, axis=1).values.tolist()
locations = [x.strip(', ') for x in locations]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


def serve_layout():
    site = html.Div([
        dcc.Dropdown(
            id='locationsdd',
            options=[{'label': locations[i], 'value': i} for i in df.index.tolist()],
            value=225,
            multi=True,
        ),
        #dcc.Graph(id='main_graph'),
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


app.layout = serve_layout


@app.callback(
    Output('dd-output-container', 'children'),
    [Input('locationsdd', 'value'),
     Input('linlog', 'value')])
def plot_data(location_list, y_axis_type):
    if location_list is None:
        return {}
    else:
        try:
            fig_data = []
            for location in location_list:
                fig_data.append(
                    go.Scatter(
                        y=df.iloc[[location], 4:].values[0, :],
                        x=df.iloc[[location], :].columns[4:],
                        name=locations[location],
                        opacity=0.8,
                    )
                )
        except TypeError:
            fig_data = [go.Scatter(
                y=df.iloc[[location_list], 4:].values[0, :],
                x=df.iloc[[location_list], :].columns[4:],
                name=locations[location_list],
                opacity=0.8
            )]

    layout = go.Layout(
        xaxis={'type': 'category', 'title': "Date"},
        yaxis={'type': 'linear', 'title': "Total Cases Diagnosed"},
        yaxis_type=y_axis_type,
        # margin={'l': 60, 'b': 40, 'r': 10, 't': 10},
    )
    figure = dcc.Graph(figure = go.Figure(
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


if __name__ == '__main__':
    app.run_server(debug=True)
