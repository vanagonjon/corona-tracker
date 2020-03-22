import pandas as pd
import io
import requests

url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series" \
      "/time_series_19-covid-Confirmed.csv"
s = requests.get(url).content
df = pd.read_csv(io.StringIO(s.decode('utf-8')))
df.columns = df.columns.str.strip().str.lower().str.replace('/', '_')


df = df.loc[df['country_region'] == 'US']

Total = df.groupby['3_21_20'].sum()

print(df.head())

#new_df = df.loc[['US']]
# new_df = df.loc[df['column_name'] == some_value]
# print(new_df)

#df_US = new_df.loc[:, 'US']
#print(df_US.columns[df_US.iloc[0,:].isin(['New York'])])