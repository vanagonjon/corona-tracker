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
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series" \
      "/time_series_19-covid-Confirmed.csv"
s = requests.get(url).content
df = pd.read_csv(io.StringIO(s.decode('utf-8')))
# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace('/', '_')

# Convert states to string, and remove nan values
df['province_state'] = df['province_state'].astype(str).str.replace('nan', '')
# Concatinate state and country names in a list
locations = df[['province_state', 'country_region']].agg(', '.join, axis=1).values.tolist()
locations = [x.strip(', ') for x in locations]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    dcc.Dropdown(
        id='locationsdd',
        options=[{'label': locations[i], 'value': i} for i in df.index.tolist()],
        value=101,
        multi=True,
    ),
    dcc.Graph(id='main_graph'),
    html.Div(id='dd-output-container')
])


@app.callback(
    Output('main_graph', 'figure'),
    [Input('locationsdd', 'value')])
def plot_data(location_list):

    if location_list is None:
        return {}
    else:
        try:
            fig_data = []
            for location in location_list:
                fig_data.append(
                    go.Scatter(
                        y=df.iloc[[location], 4:].values[0, :],
                        x=df.iloc[[location],:].columns[4:],
                        name=locations[location],
                        opacity=0.8,
                    )
                )
        except TypeError:
            fig_data = [go.Scatter(
                y=df.iloc[[location_list], 4:].values[0, :],
                x=df.iloc[[location_list],:].columns[4:],
                name=locations[location_list],
                opacity=0.8
            )]

    layout = go.Layout(
        xaxis={'type': 'category', 'title': "Date"},
        yaxis={'type': 'linear', 'title': "Value"},
        #margin={'l': 60, 'b': 40, 'r': 10, 't': 10},
    )
    figure = go.Figure(
        data=fig_data,
        layout=layout)
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
