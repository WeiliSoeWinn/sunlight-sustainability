"""
The purpose of the script is to calculate the total cost of operations - TCO for both
coal plant and solar plant for over 40 years period. This script evaluates the
financial and environmental trade-offs of replacing U.S. coal-fired power plants
with solar photovoltaic (PV) systems. For each coal plant, it calculates the total cost
of ownership (TCO) over a 40-year horizon, accounting for fixed and variable O&M costs,
fuel costs, and the social cost of carbon (SCC). It then models the equivalent
solar plant size needed to replace the coal plant’s generation,
computes the associated solar TCO (including capital costs, ITC, O&M, and
degradation-adjusted costs), and compares both TCOs.
Here, the cost of land to build the solar is not included with the assumption that
it will be build on the land plot of current coal plant.
"""

import pandas as pd

# Load eGRID dataset

plant = pd.read_excel('egrid2023_data_rev1.xlsx', 'PLNT23', header = 1)
plant.rename(columns = {
    'ORISPL':'Plant_ID', 'PNAME' : 'Plant_Name','PLFUELCT': 'Plant_Fueltype',
    'NAMEPCAP': 'Plant_Nameplate_Capacity', 'CAPFAC' : 'Cap_Factor',
    'PLCO2EQA': 'CO2EQ_2023', 'PSTATABB':'State'}, inplace=True)

plant = plant [[
    'Plant_ID', 'Plant_Name','State', 'LAT', 'LON', 'Plant_Fueltype','CO2EQ_2023',
    'Plant_Nameplate_Capacity', 'Cap_Factor']]

# For coal plant, calculate annual generation in MWh by each plant
plant['Annual_Generation_MWh'] = plant['Plant_Nameplate_Capacity'] * plant['Cap_Factor'] * 8760 # nameplate in MW

# Filter coal plants
plant_coal = plant[plant['Plant_Fueltype'] == 'COAL'].copy()
#plant_coal.dropna()

# Assumptions for coal power plant
discount_rate = 0.05
scc_price = 50  # $/ton CO2

coal_fixed_om_per_mw = 45.68 * 1000 # reference from EIA March 2023
coal_variable_om_per_mwh = 5.06
coal_heat_rate = 8638 * 1000 # Btu/kWh - now /MWh
coal_price_per_mmbtu = 2.5 # $ - coal price per ton / btu content per ton

# Assumptions for solar power plant
solar_capex_per_mw = 1448 * 1000  # $/kW
solar_om_per_mw = 17.16 * 1000 # $/kW
solar_cf = 0.25 # approximately between 20 - 30%
itc_rate = 0.30 # 30% Tax credit
years = range(0, 40)

results = []

for _, row in plant_coal.iterrows():
    
    gen_mwh = row['Annual_Generation_MWh']
    capacity_mw = row['Plant_Nameplate_Capacity']
    co2_tons = row['CO2EQ_2023']
    state = row['State']


    # Coal Total Cost of Ownership - tco 
    coal_annual_fixed_om = capacity_mw * coal_fixed_om_per_mw # in MW
    coal_annual_variable_om = gen_mwh * coal_variable_om_per_mwh
    fuel_cost_per_mwh = (coal_heat_rate / 1e6) * coal_price_per_mmbtu
    coal_annual_fuel_cost = gen_mwh * fuel_cost_per_mwh
    coal_annual_scc = co2_tons * scc_price

    coal_tco = 0
    for t in range(1, 40):
        total_cost = coal_annual_fixed_om + coal_annual_variable_om + coal_annual_fuel_cost + coal_annual_scc
        dcf = total_cost / ((1 + discount_rate) ** t)
        coal_tco += dcf/1e6

    # Solar Total Cost of Ownership - tco
    solar_mw = gen_mwh / (solar_cf * 8760)
    solar_capex = solar_mw * solar_capex_per_mw
    solar_itc = solar_capex * itc_rate
    net_capex = solar_capex - solar_itc
    solar_annual_gen = solar_mw * solar_cf * 8760
    solar_annual_om = solar_mw * solar_om_per_mw

    solar_tco = net_capex/1e6
    for t in range(1, 40):
        dcf = solar_annual_om / ((1 + discount_rate) ** t)
        solar_tco += dcf/1e6

    results.append({
        'Plant_ID': row['Plant_ID'],
        'Plant_Name': row['Plant_Name'],
        'State': state,
        'Coal TCO (mil$)': coal_tco,
        'Solar TCO (mil$)':solar_tco,
        'PV Gain (mil$)': (coal_tco - solar_tco), # coal_tco (total cost of ownership or coal_pvc (present value of cost)
        'CO2 Avoided (tons/year)': co2_tons,
        'Solar MW Required': solar_mw,
        'LAT': row['LAT'],
        'LON': row['LON']
    })

# Output CSV for QGIS mapping
PV_results = pd.DataFrame(results)
PV_results.to_csv("coal_to_solar_pv_gain.csv", index=False)


