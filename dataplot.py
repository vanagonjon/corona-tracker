import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

df = pd.read_csv('COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv').T
headers = df.iloc[1]
new_df = pd.DataFrame(df.values[0:], columns=headers)
new_df = new_df.drop(new_df.index[1])
#print(new_df.head())

df_US = new_df.loc[:, 'US']
print(df_US.columns[df_US.iloc[0,:].isin(['New York'])])

# df[df.columns[df.isin([0,1]).all()]]

#y_mass = new_df.loc[3:,'Massachusetts']
#y_conn = new_df.loc[3:,'Connecticut']
#y_ny = new_df.loc[3:,'New York']
#y_hub = new_df.loc[3:, 'Hubei']
y_ity = new_df.loc[3:, 'US']

#print(new_df.loc[:, 'US'].head())

fig = go.Figure([go.Scatter(y=y_ity, name='Italy')])
#fig.add_trace(go.Scatter(y=y_conn, name='Connecticut'))
#fig.add_trace(go.Scatter(y=y_ny, name='New York'))
#fig.add_trace(go.Scatter(y=y_ity, name='Italy'))

#fig.show()