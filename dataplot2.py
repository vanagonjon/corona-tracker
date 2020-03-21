import pandas as pd
import plotly.graph_objects as go
import io
import requests

url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series" \
      "/time_series_19-covid-Confirmed.csv"
s = requests.get(url).content
df = pd.read_csv(io.StringIO(s.decode('utf-8')))

df.columns = df.columns.str.strip().str.lower().str.replace('/', '_')
df['province_state'] = df['province_state'].astype(str).str.replace('nan', '')
locations = df[['province_state', 'country_region']].agg(' '.join, axis=1).values.tolist()

print(locations)

states = ['Massachusetts','New York','Connecticut','Washington','California','Italy','Germany','Spain','Switzerland','Iran','Korea, South'] #,'Hubei'
states = ['Massachusetts']
states_inx = df[df.isin(states).any(1)].index

fig = go.Figure()

for index in states_inx:
    y = df.iloc[[index],4:].values[0,:]
    x = df.iloc[[index],:].columns[4:].tolist()
    print(x)
    name = str(df.iloc[[index], 0].values[0]) + ', ' + df.iloc[[index], 1].values[0]
    fig.add_trace(go.Scatter(y=y, x=x, name=name))

fig.show()
