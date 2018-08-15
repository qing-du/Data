"""
General description:
---------------------


Installation requirements:
---------------------------
This example requires oemof 0.2.2. Install by:

    pip install oemof==0.2.2

"""

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

from oemof import solph
from oemof.outputlib import processing

from oemof.outputlib import views

import source_x_system as es
import os

import pandas as pd

import oemof.graph as grph 
import pprint as pp

import matplotlib.pyplot as plt 



""" Reference Network """


solver = 'cbc'  # 'glpk', 'gurobi',....
debug = False  # Set number_of_timesteps to 3 to get a readable lp-file.
solver_verbose = False  # show/hide solver output


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

# do not change!
sum_nominal_load_values = 6348.4153 # fixed value of the normalized el_demand series


# use the choosen variable for the actuel value in the network SINK
nominal_BAU = 420000000/sum_nominal_load_values # business as usual 
nominal_traffic_heat = 506000000/sum_nominal_load_values # traffic and heat included 


# investment for each energy carrier

epc_x = economics.annuity(capex=10000000000000000, n=30, wacc=0.5)
variable_costs_x = 1000000

epc_wind_on = economics.annuity(capex=1780000, n=25, wacc=0.025)

epc_wind_off = economics.annuity(capex=4000000, n=25, wacc=0.048)

epc_pv = economics.annuity(capex=717500, n=25, wacc=0.021)


# MAXIMUM Capacity
   
max_pv_Si   = 26400
max_pv_CIGS = 550
max_pv_CdTe = 550  
       
max_wind_on_hyprid    = 56579
max_wind_on_asynchron = 56579
       
max_wind_off_pure = 45000    

###########
# 2 Built the network
##########

bel = solph.Bus(label = "electricity")

# add all Buses to the EnergySystem
energysystem.add(bel)

#####################################Sources##################################
# source X
energysystem.add(solph.Source(label='rx', 
outputs={bel: solph.Flow(nominal_value = None, 
variable_costs = variable_costs_x, 
investment = solph.Investment(ep_costs=epc_x))}))

   
# source wind onshore
energysystem.add(solph.Source(label='wind_on_hyprid', 
    outputs={bel: solph.Flow(fixed=True, 
    actual_value=data['Wind_on'], 
    investment = solph.Investment(ep_costs=epc_wind_on, 
    maximum=max_wind_on_hyprid))}))
    
energysystem.add(solph.Source(label='wind_on_asynchron',
    outputs={bel: solph.Flow(fixed=True, 
    actual_value=data['Wind_on'], 
    investment = solph.Investment(ep_costs=epc_wind_on,
    maximum=max_wind_on_asynchron))}))
    
#source wind offshore 
energysystem.add(solph.Source(label='wind_off_pure', 
    outputs={bel: solph.Flow(fixed=True, 
    actual_value=data['Wind_off'], 
    investment = solph.Investment(ep_costs=epc_wind_off,
    maximum=max_wind_off_pure))}))
    
    
# source pv     
energysystem.add(solph.Source(label='pv_Si', 
    outputs={bel: solph.Flow(fixed=True, 
    actual_value=data['PV'],
    investment = solph.Investment(ep_costs=epc_pv,maximum=max_pv_Si))}))
    
energysystem.add(solph.Source(label='pv_CIGS', 
    outputs={bel: solph.Flow(fixed=True, 
    actual_value=data['PV'], 
    investment = solph.Investment(ep_costs=epc_pv,maximum=max_pv_CIGS))}))

energysystem.add(solph.Source(label='pv_CdTe', 
    outputs={bel: solph.Flow(fixed=True, 
    actual_value=data['PV'], 
    investment = solph.Investment(ep_costs=epc_pv,maximum=max_pv_CdTe))}))

    
####################################SINK######################################
energysystem.add(solph.Sink(label='demand_elec', 
    inputs={bel: solph.Flow(
    actual_value=data ['normalised_load_profile'] , fixed=True, nominal_value= nominal_BAU)}))

#energysystem.add(solph.Sink(label = 'electricity_excess', inputs={bel:solph.Flow(variable_costs = 1000000)}))
    
################################Storage########################################
energysystem.add(solph.components.GenericStorage(label='storage',
    inputs={bel: solph.Flow()},
    outputs={bel: solph.Flow()},
    nominal_capacity=129000,
    inflow_conversion_factor=1, outflow_conversion_factor=1))

        
om = solph.Model(energysystem)
om.solve(solver = 'cbc', solve_kwargs ={'tee':True})
        
print('----------capacity energy system---------')
my_results_capacity = processing.results(om)
energysystem.results['main'] = processing.results(om)
energysystem.results['meta'] = processing.meta_results(om)
        #
energysystem.dump(dpath=None, filename=None)
# define an alias for shorter calls below (optional)
results_capacity = energysystem.results['main']
electricity_bus     = views.node(results_capacity, 'electricity')
        
# plot the time series (sequences) of a specific component/bus
if plt is not None:

            plt.show()
            electricity_bus['sequences'].plot(kind='line', drawstyle='steps-post')
            plt.show()

# print the solver resul
print('********* Meta results *********')
pp.pprint(es.energysystem.results['meta'])
print('')
    
# print the sums of the flows around the electricity bus
print('********* Main results *********')
print(electricity_bus['sequences'].sum(axis=0))
          
mbc= processing.create_dataframe(om)


fn = os.path.join(os.path.dirname(__file__), 'source_x_dataframe.xlsx')
pd.DataFrame(mbc).to_excel(fn)

#1 get the maximum capacities of each technology mbc = maximum built capacity
    
mbc = mbc.loc[mbc.variable_name == 'invest', ['value', 'oemof_tuple']]

print(mbc)     


        
