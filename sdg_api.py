import requests
import pandas as pd

#API from https://unstats.un.org/sdgapi/swagger/#!/Goal/V1SdgGoalListGet

url = 'https://unstats.un.org/SDGAPI/v1/sdg/Goal/List'

response = requests.get(url)

data_list = {}

if response.status_code == 200: #reference ChatGPT
    data_list = response.json()

#create dataframe

df = pd.DataFrame(data_list)

#convert df to csv

df.to_csv('sdg.csv', index=False)

