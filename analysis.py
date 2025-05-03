"""
This script analyzes the relationship between CO₂ intensity and the economic benefits
(PV Gain) of replacing U.S. coal power plants with solar. 
Then, it identifies a subset of coal plants that are both high in CO₂ intensity
(>1.0 tons/MWh) and show significant economic advantage when replaced with solar
(PV Gain > $8 billion). A scatter plot is generated to visualize the correlation
between CO₂ intensity and PV Gain, and the correlation coefficient is calculated.
Finally, the filtered dataset with high-priority coal plants are exported
for further mapping in QGIS.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

tco = pd.read_csv("coal_to_solar_pv_gain.csv")
plant = pd.read_excel("egrid2023_data_rev1.xlsx", "PLNT23", header=1)

plant.rename(columns = {
    'ORISPL':'Plant_ID','PNAME' : 'Plant_Name','PLFUELCT': 'Plant_Fueltype',
    'NAMEPCAP': 'Plant_Nameplate_Capacity', 'CAPFAC' : 'Cap_Factor',
    'PLCO2EQA': 'CO2EQ_2023', 'PSTATABB':'State'
    }, inplace=True)

plant = plant [[
    'Plant_ID','Plant_Name','State', 'LAT', 'LON', 'Plant_Fueltype','CO2EQ_2023',
    'Plant_Nameplate_Capacity', 'Cap_Factor']]

state_fullname = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota',
    'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
    'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
}
plant ['State'] = plant['State'].map(state_fullname)

coal = plant[plant['Plant_Fueltype'] == 'COAL'].copy()
coal = plant[['Plant_ID', 'Plant_Name','Plant_Nameplate_Capacity', 'Cap_Factor',
              'CO2EQ_2023', 'State', 'LAT', 'LON']].dropna()

# Calculate annual generation and CO2 intensity (tons/MWh)
coal['Annual_MWh'] = coal['Plant_Nameplate_Capacity'] * coal['Cap_Factor'] * 8760
coal['CO2_Intensity'] = coal['CO2EQ_2023'] / coal['Annual_MWh']  # tons/MWh

# Merge with PV gain data
merged = pd.merge(coal, tco[['Plant_ID', 'PV Gain (mil$)', 'State']],
                  on='Plant_ID', how='inner')

# top coal plants best to replace with solar
filtered = merged[(merged['CO2_Intensity'] > 1.0) & (merged['PV Gain (mil$)'] > 8000)]
filtered = filtered.sort_values(by=['PV Gain (mil$)'], ascending = False)

# Scatter plot to visualize correlation
plt.figure(figsize=(10, 6))
sns.scatterplot(data = merged, x='CO2_Intensity', y='PV Gain (mil$)',
                hue='PV Gain (mil$)', palette='coolwarm', size='PV Gain (mil$)',
                sizes=(20, 200))
plt.title('PV Gain vs. CO2 Intensity (tons/MWh) for Coal Plants')
plt.xlabel('CO2 Intensity (tons/MWh)')
plt.ylabel('PV Gain (mil$) from Replacing with Solar')
plt.grid(True)
plt.tight_layout()
plt.savefig("pv_vs_CO2_intensity.png")
plt.show()

# correlation calculation
correlation = merged[['CO2_Intensity', 'PV Gain (mil$)']].corr().iloc[0, 1]
print(f"Correlation between CO2 intensity and NPV Gain: {correlation:.3f}")

# Save merged dataset for further filtering in QGIS or Excel
merged.to_csv("pv_CO2_intensity_analysis.csv", index=False)
filtered.to_csv("filtered_by_highest_TCO.csv", index=False)
