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

r = 0

while r < 2:
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

    date_time_index = pd.date_range('1/1/2050', periods = 500, freq = 'H' )

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
        outputs={bel: solph.Flow(nominal_value = None, variable_costs = 1000000, investment = solph.Investment(ep_costs=epc_x))}))

    # Exsisting capacities Sources

    # MAXIMUM Capacity
   

    if r == 0:
       max_pv_Si = 27500
       max_pv_CIGS =27500
       max_pv_CdTe = 27500  


   # TODO - calculate the new capacities depending on material shortage"""
    elif r == 1:
       max_pv_Si = 0
       max_pv_CIGS = 0
       max_pv_CdTe = 0

    # source wind onshore
    energysystem.add(solph.Source(label='wind_on', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['Wind_on'],variable_costs = 0.01 , investment = solph.Investment(ep_costs=epc_wind_on,maximum=1187840))}))

    #source wind offshore
    energysystem.add(solph.Source(label='wind_off', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['Wind_off'], investment = solph.Investment(ep_costs=epc_wind_off,maximum=45000))}))

    # source pv
  
    
    energysystem.add(solph.Source(label='pv_Si', outputs={bel: solph.Flow(fixed=True, 
       actual_value=data['PV'], investment = solph.Investment(ep_costs=epc_pv,maximum=max_pv_Si))}))
    
    energysystem.add(solph.Source(label='pv_CIGS', outputs={bel: solph.Flow(fixed=True, 
       actual_value=data['PV'], investment = solph.Investment(ep_costs=epc_pv,maximum=max_pv_CIGS))}))

    energysystem.add(solph.Source(label='pv_CdTe', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['PV'], investment = solph.Investment(ep_costs=epc_pv,maximum=max_pv_CdTe))}))

    
    ####################################SINK######################################


    energysystem.add(solph.Sink(label='demand_elec', inputs={bel: solph.Flow(
       actual_value=data ['normalised_load_profile'] , fixed=True, nominal_value= nominal_traffic_heat)}))

    energysystem.add(solph.Sink(label = 'electricity_excess', inputs={bel:solph.Flow(variable_costs = 0.0749)}))


    ##########################Storage########################################

#Quelle EEG Vergütung 
#https://www.erneuerbare-energien.de/EE/Navigation/DE/Technologien/Windenergie-auf-See/Finanzierung/EEG-Verguetung/eeg-verguetung.html#doc153466bodyText1


    


###############################
#accessing data of the optimization
###############################
      
              
   
    if r == 0:
        
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
        
    if r == 1:
        
        om = solph.Model(energysystem)
        om.solve(solver = 'cbc', solve_kwargs ={'tee':True})
        print('----------shortage energy system---------')
        my_results_shortage = processing.results(om)
        energysystem.results['main'] = processing.results(om)
        energysystem.results['meta'] = processing.meta_results(om)
        #
        energysystem.dump(dpath=None, filename=None)
        # define an alias for shorter calls below (optional)
        results_shortage = energysystem.results['main']
        electricity_bus     = views.node(results_shortage, 'electricity')
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
    r +=1