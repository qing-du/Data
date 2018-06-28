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

date_time_index = pd.date_range('1/1/2050', periods = 8760, freq = 'H' )

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


epc_x = economics.annuity(capex=10000000000000000, n=30, wacc=0.5)

epc_wind_on = economics.annuity(capex=1780000, n=25, wacc=0.025)

epc_wind_off = economics.annuity(capex=4000000, n=25, wacc=0.048)

epc_pv = economics.annuity(capex=717500, n=25, wacc=0.021)



###########
# 2 Built the network
##########

# Create all Buses




bel = solph.Bus(label = "electricity")

# add all Buses to the EnergySystem
energysystem.add(bel)


#####################################Sources##################################
# source X
energysystem.add(solph.Source(label='rx', 
   outputs={bel: solph.Flow(nominal_value = None, variable_costs = 1000000, investment = solph.Investment(ep_costs=epc_x)) }))


# source wind onshore
energysystem.add(solph.Source(label='wind_on', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['Wind_on'] , investment = solph.Investment(ep_costs=epc_wind_on,maximum=1187840))}))

#source wind offshore
energysystem.add(solph.Source(label='wind_off', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['Wind_off'], investment = solph.Investment(ep_costs=epc_wind_off,maximum=45000))}))

# source pv
energysystem.add(solph.Source(label='pv', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['PV'], investment = solph.Investment(ep_costs=epc_pv,maximum=275000))}))



####################################SINK######################################


energysystem.add(solph.Sink(label='demand_elec', inputs={bel: solph.Flow(
       actual_value=data ['normalised_load_profile'] , fixed=True, nominal_value= nominal_traffic_heat)}))

energysystem.add(solph.Sink(label = 'electricity_excess', inputs={bel:solph.Flow()}))



