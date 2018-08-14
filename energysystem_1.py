# Default logger of oemof
from oemof.tools import logger
from oemof.tools import helpers
import oemof.solph as solph
from oemof.tools import economics

# import oemof base classes to create energy system objects
import logging
import os
import pandas as pd
import warnings



solver = 'cbc'  # 'glpk', 'gurobi',....
debug = False  # Set number_of_timesteps to 3 to get a readable lp-file.
solver_verbose = False  # show/hide solver output

############
# 1 initialize energysystem
############

#data
#capex,wacc,n,capacity per pp : Stromgestehungskosten Erneuerbare Energien, ISE, März 2018
#wind and pv feed in and electricity demand : 
#fuelprices & development : Prognos AG 2013; Hecking et al. 2017; Schlesinger et al. 2014; World Bank 2017; DLR Rheinland-Pfalz 2017; Scheftelowitz et al. 2016
#efficiency : Wietschel et al. 2010

date_time_index = pd.date_range('1/1/2018', periods = 500, freq = 'H' )

energysystem = solph.EnergySystem(timeindex=date_time_index)

#input_data
filename = os.path.join(os.path.dirname(__file__), 'normalised data.csv')
data = pd.read_csv(filename)




###################TASK before running the optimization #######################
##### set different boundary conditions for different scenarios by hand ######

# do not change!
sum_nominal_load_values = 6348.4153 # fixed value of the normalized el_demand series

####################### choose el_demand scenario #############################
# use the choosen variable for the actuel value in the network SINK
nominal_BAU = 420000000/sum_nominal_load_values # business as usual 
nominal_traffic_heat = 506000000/sum_nominal_load_values # traffic and heat included 


############## select  Co2- certificates costs in [€/t]#######################
CO2_cost = 16


######################### choose capex scenarios  ############################
# index[0] for conservative
# index[1] for neutral
# index[2] for optimistic

filename1 = os.path.join(os.path.dirname(__file__), 'capex_scenarios_renewables.xlsx')
capex_scenarios = pd.read_excel(filename1)

capex_wind_on   = capex_scenarios.loc[capex_scenarios.index[0],'capex_wind_on']
capex_wind_off  = capex_scenarios.loc[capex_scenarios.index[0], 'capex_wind_off']
capex_pv        = capex_scenarios.loc[capex_scenarios.index[0], 'capex_pv']

###################### END of secetion part ##################################



# investment for each energy carrier
epc_coal_old = economics.annuity(capex= (1650 + 32)*1000, n=40, wacc=0.056)

epc_coal_new = economics.annuity(capex= (1650 + 32)*1000, n=40, wacc=0.056)

epc_lignite_old = economics.annuity(capex=(1900 + 36)*1000, n=40, wacc=0.056)

epc_lignite_new = economics.annuity(capex= (1900 + 36)*1000, n=40, wacc=0.056)

epc_gas = economics.annuity(capex=(950 + 22)*1000, n=30, wacc=0.052)

epc_wind_on = economics.annuity(capex=capex_wind_on, n=25, wacc=0.025)

epc_wind_off = economics.annuity(capex=capex_wind_off, n=25, wacc=0.048)

epc_pv = economics.annuity(capex=capex_pv, n=25, wacc=0.021)


###########
# 2 Built the network
##########

# Create all Buses


bcoal = solph.Bus(label = "coal")


blignite = solph.Bus(label = "lignite")

bgas = solph.Bus(label = "gas")

bel = solph.Bus(label = "electricity")

# add all Buses to the EnergySystem
energysystem.add( bcoal, blignite, bgas, bel)




# Cos costs €/MWh
CO2_gas     =    0.202 * CO2_cost 
CO2_lignite =    0.337 * CO2_cost
CO2_coal    =    0.403 * CO2_cost


# source coal old
#energysystem.add(solph.Source(label='coal_old', outputs={bcoal_old: solph.Flow(
 #   nominal_value=800, variable_costs = 9.6)}))

# source coal new
energysystem.add(solph.Source(label='coal_new', outputs={bcoal: solph.Flow(
    variable_costs = 9.6 + CO2_coal)}))

# source lignite old
#energysystem.add(solph.Source(label='lignite_old', outputs={bcoal_new: solph.Flow(
#    nominal_value=1000, variable_costs = 1.8)}))

# source lignite new
energysystem.add(solph.Source(label='lignite_new', outputs={bcoal: solph.Flow(
    variable_costs = 1.8 + CO2_lignite)}))

# source natural gas
energysystem.add(solph.Source(label='rgas', outputs={bgas: solph.Flow(
    variable_costs = 21 + CO2_gas)}))


# EEG
eeg_wind_on  = -7
eeg_wind_off = -1.9
eeg_Pv       = -22




energysystem.add(solph.Source(label='pv_old', outputs={bel: solph.Flow(
    actual_value=data['PV'], nominal_value=43790, fixed=True)}))

energysystem.add(solph.Source(label='wind_on_old', outputs={bel: solph.Flow(
    actual_value=data['Wind_on'], nominal_value=52320, fixed=True)}))

energysystem.add(solph.Source(label='wind_off_old', outputs={bel: solph.Flow(
    actual_value=data['Wind_off'], nominal_value=5380, fixed=True)}))



# source wind onshore
energysystem.add(solph.Source(label='wind_on', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['Wind_on'],variable_costs = eeg_wind_on , investment = solph.Investment(ep_costs=epc_wind_on,maximum=1187840))}))

#source wind offshore
energysystem.add(solph.Source(label='wind_off', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['Wind_off'], variable_costs = eeg_wind_off,  investment = solph.Investment(ep_costs=epc_wind_off,maximum=45000))}))

# source pv
energysystem.add(solph.Source(label='pv', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['PV'], variable_costs = eeg_Pv, investment = solph.Investment(ep_costs=epc_pv,maximum=275000))}))


energysystem.add(solph.Sink(label = 'electricity_excess', inputs={bel:solph.Flow(variable_costs = eeg_Pv)}))

energysystem.add(solph.Sink(label='demand_elec', inputs={bel: solph.Flow(
       actual_value=data ['normalised_load_profile'] , fixed=True, nominal_value= nominal_BAU)}))


# Create all Transformers



# transformer coal new
energysystem.add(solph.Transformer(
    label="pp_coal_new",
    inputs={bcoal: solph.Flow()},
    outputs={bel: solph.Flow(nominal_value = None, variable_costs=5,investment=solph.Investment(ep_costs=epc_coal_new))},
    conversion_factors={bel: 0.5}))



# transformer lignite new
energysystem.add(solph.Transformer(
    label="pp_lignite_new",
    inputs={blignite: solph.Flow()},
    outputs={bel: solph.Flow(nominal_value = None, variable_costs=5,investment=solph.Investment(ep_costs=epc_lignite_new))},
    conversion_factors={bel: 0.465}))

# transformer gas
energysystem.add(solph.Transformer(
    label="pp_gas",
    inputs={bgas: solph.Flow()},
    outputs={bel: solph.Flow(nominal_value = None, variable_costs=4,investment=solph.Investment(ep_costs=epc_gas))},
    conversion_factors={bel: 0.58}))

