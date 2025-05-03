"""
The purpose of this script is to calculate the total tons of CO2eq 
that can be avoided in 2023 year alone, ranking top 20% (dirtiest) of 
coal plants with highest CO2eq tons emissions, and monetized the emission as
social cost of carbon - SCC. 
Then, the csv file created was used to locate the coal plants with highest 
CO2eq emissions in QGIS in US Map.

"""

import pandas as pd


plant = pd.read_excel('egrid2023_data_rev1.xlsx', 'PLNT23', header = 1)

plant.rename(columns = {
    'ORISPL':'Plant_ID', 'PNAME' :'Plant_Name','PLFUELCT': 'Plant_Fueltype',
    'NAMEPCAP': 'Plant_Nameplate_Capacity', 'CAPFAC' : 'Cap_Factor',
    'PLCO2EQA': 'CO2EQ_2023'}, inplace=True)

plant = plant [[
    'Plant_ID','Plant_Name','LAT', 'LON', 'Plant_Fueltype','CO2EQ_2023',
    'Plant_Nameplate_Capacity', 'Cap_Factor']]

coal_PP = plant[plant["Plant_Fueltype"] == 'COAL']
coal_PP['CO2EQ_2023'] = coal_PP['CO2EQ_2023'].round(2)
coal_PP.to_csv('CoalPP_US.csv')

CO2_US_avoided = coal_PP['CO2EQ_2023'].round(2).sum()
CO2_US_avoided = CO2_US_avoided / 1e6
print (f'CO2 avoided by Coal Power Plants in short ton : {CO2_US_avoided:.3f} megatons')

coal_PP_by_rank = coal_PP.sort_values(by='CO2EQ_2023', ascending = False)

coal_PP['Rank'] = coal_PP['CO2EQ_2023'].rank(ascending=False)
top_n = int(len(coal_PP) * 0.20)
top_20_percent = coal_PP[coal_PP['Rank'] <= top_n]
top_20_percent.to_csv('top20_dirtiest coal plants.csv')

# Calculating Social Cost of Carbon
# formula, Monetized value of CO2EQ = CO2EQ * SCC
SCC = 50
coal_PP['Monetized'] = coal_PP['CO2EQ_2023'] * 50
coal_PP_SCC = coal_PP['Monetized'].sum()
coal_PP_SCC = coal_PP_SCC / 1e9
print(f"Total Social Cost of Carbon per year : {coal_PP_SCC:.3f} billion $")


