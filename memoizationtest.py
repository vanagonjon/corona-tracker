from flask_caching import Cache

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import io
import requests


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


df1, df2 = dataframe()
print(df1.describe(), df2.describe())
