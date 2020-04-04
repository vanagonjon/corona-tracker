# import pandas as pd
# import io
# import requests
#
# url = "https://www.soothsawyer.com/wp-content/uploads/2020/03/time_series_19-covid-Confirmed.csv"
# s = requests.get(url).content
# ds = pd.read_csv(io.StringIO(s.decode('utf-8')))
# print(ds.head())


import requests
import pandas as pd
from io import StringIO

url = 'https://www.soothsawyer.com/wp-content/uploads/2020/03/time_series_19-covid-Confirmed.csv'
r = requests.get(url)

df = pd.read_csv(StringIO(r.text))
print(r.text)