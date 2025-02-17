import pandas as pd
import re

df = pd.read_csv("all_Markets.csv")

reg_dict = {'VERRA':[],'ACR':[],'MRK':[],'CAR':[]}

verra_sdg = {}
car_sdg = {}
acr_sdg = {}
mrk_sdg = {}

for v in range(17):
    verra_sdg[v+1] = 0
    car_sdg[v+1] = 0
    acr_sdg[v+1] = 0
    mrk_sdg[v+1] = 0

#create a list of list for each project's SDG's and match them with their registry
for v in range(df['Registry'].size):
    reg = df['Registry'].values[v]
    text = df['SDGs'].iloc[v]
    pat = r'[1-9][1-9]*'
    list = re.findall(pat,text)
    list = [int(x) for x in list]
    reg_dict[reg].append(list)

#count each sdg per registry and format them into Goal X: Count
for v in range(len(reg_dict['VERRA'])):
    for item in reg_dict['VERRA'][v]:
        for key in range(len(verra_sdg)):
            if item == key:
                verra_sdg[key] += 1

verra_sdg = {"Goal " + str(key): [value] for key, value in verra_sdg.items()}

for v in range(len(reg_dict['CAR'])):
    for item in reg_dict['CAR'][v]:
        for key in range(len(car_sdg)):
            if item == key:
                car_sdg[key] += 1

car_sdg = {"Goal " + str(key): [value] for key, value in car_sdg.items()}

for v in range(len(reg_dict['ACR'])):
    for item in reg_dict['ACR'][v]:
        for key in range(len(acr_sdg)):
            if item == key:
                acr_sdg[key] += 1

acr_sdg = {"Goal " + str(key): [value] for key, value in acr_sdg.items()}

for v in range(len(reg_dict['MRK'])):
    for item in reg_dict['MRK'][v]:
        for key in range(len(mrk_sdg)):
            if item == key:
                mrk_sdg[key] += 1

mrk_sdg = {"Goal " + str(key): [value] for key, value in mrk_sdg.items()}

#create the dfs

df1 = pd.DataFrame(verra_sdg)
df2 = pd.DataFrame(car_sdg)
df3 = pd.DataFrame(acr_sdg)
df4 = pd.DataFrame(mrk_sdg)
df_combined = pd.concat([df1, df2, df3, df4], ignore_index=True)
df_combined.insert(0, 'Registry', ['VERRA', 'CAR', 'ACR', 'MRK'])

df_combined.to_csv('sdg_counts.csv', index=False)
