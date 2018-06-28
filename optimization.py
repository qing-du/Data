# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 14:13:17 2018

@author: duqi1
"""

from oemof import solph
from oemof.outputlib import processing

from oemof.outputlib import views

import energysystem_1 as es
import os

import pandas as pd

import oemof.graph as grph 
import pprint as pp

import matplotlib.pyplot as plt 


filename1 = os.path.join(os.path.dirname(__file__), 'capex_scenarios_renewables.xlsx')
capex_scenarios = pd.read_excel(filename1)
#import networkx as nx
################################
# Optimizing of the energy system 
################################

    
om = solph.Model(es.energysystem)
om.solve(solver = 'cbc', solve_kwargs ={'tee':True})
my_results = processing.results(om)

###############################
#accessing data of the optimization
###############################

es.energysystem.results['main'] = processing.results(om)
es.energysystem.results['meta'] = processing.meta_results(om)
#
es.energysystem.dump(dpath=None, filename=None)
    # define an alias for shorter calls below (optional)
results = es.energysystem.results['main']

######## create different Data Frame for the different scearnaios#############
############create excel file of max. capacites of each technology############
conservatice_df = pd.DataFrame()
neutral_df = pd.DataFrame()
optimistic_df = pd.DataFrame()

mbc = pd.DataFrame()

###################conservative scenario #####################################

if es.capex_wind_on == capex_scenarios.loc[capex_scenarios.index[0],'capex_wind_on']:
        
    conservative_df = processing.create_dataframe(om)
    print('#### this is the conservative dataframe#########')
    fn = os.path.join(os.path.dirname(__file__), 'conservative_DataFrame.xlsx')
    pd.DataFrame(conservative_df).to_excel(fn)
    
    #1 get the maximum capacities of each technology mbc = maximum built capacity
    
    mbc = conservative_df.loc[conservative_df.variable_name == 'invest', ['value', 'oemof_tuple']]

    # rename the index with the name of the investment flow 
    a = 0
    while a < mbc.index.size:
        mbc.rename(index= { mbc.index[a]: (mbc.loc[mbc.index[a],'oemof_tuple'])}, inplace= True)
        a+=1
   
    
    
    fn = os.path.join(os.path.dirname(__file__), 'network_capacities.csv')
    pd.DataFrame(mbc).to_csv(fn)
    
  
    
    mbc.plot(kind ='bar')
   
############################neutral scenario#################################
if es.capex_wind_on == capex_scenarios.loc[capex_scenarios.index[1],'capex_wind_on']:
    
    neutral_df = processing.create_dataframe(om)
    print('#### this is the neutral scenario#########')
    fn = os.path.join(os.path.dirname(__file__), 'neutral_DataFrame.xlsx')
    pd.DataFrame(conservative_df).to_excel(fn)
    
    #1 get the maximum capacities of each technology mbc = maximum built capacity
    mbc = neutral_df.loc[neutral_df.variable_name == 'invest', ['value', 'oemof_tuple']]
 
    # rename the index with the name of the investment flow 
    a = 0
    while a < mbc.index.size:
        mbc.rename(index= { mbc.index[a]: (mbc.loc[mbc.index[a],'oemof_tuple'])}, inplace= True)
        a+=1
     
    fn = os.path.join(os.path.dirname(__file__), 'neutral_scenario_capacities.csv')
    pd.DataFrame(mbc).to_csv(fn)
    
    mbc.plot(kind ='bar')


######################optimistic scenario######################################         
if es.capex_wind_on == capex_scenarios.loc[capex_scenarios.index[2],'capex_wind_on']:
    
    optimistic_df = processing.create_dataframe(om)
    print('#### this is the optimistic scenario#########')
    fn = os.path.join(os.path.dirname(__file__), 'optimistic_DataFrame.xlsx')
    pd.DataFrame(optimistic_df).to_excel(fn)
   
    #1 get the maximum capacities of each technology mbc = maximum built capacity
    mbc = optimistic_df.loc[optimistic_df.variable_name == 'invest', ['value', 'oemof_tuple']]
   
    # rename the index with the name of the investment flow 
    a = 0
    while a < mbc.index.size:
        mbc.rename(index= { mbc.index[a]: (mbc.loc[mbc.index[a],'oemof_tuple'])}, inplace= True)
        a+=1
   
    fn = os.path.join(os.path.dirname(__file__), 'optimistic_scenario_capacities.csv')
    pd.DataFrame(mbc).to_csv(fn)

    mbc.plot(kind ='bar')



df = processing.create_dataframe(om)
# creating a result dictionary containing node parameters
p_results = processing.param_results(om)

electricity_bus     = views.node(results, 'electricity')
#coal_bus            = views.node(results, 'coal')

#coal_transformer    = views.node(results,'pp_coal')
#gas_transformer     = views.node(results, 'pp_gas')

wind_on_source      = views.node(results, 'wind_on')
wind_off_source     = views.node(results, 'wind_off')
pv_source           = views.node(results, 'pv')


fn = os.path.join(os.path.dirname(__file__), 'electricity_bus_sequences.csv')
pd.DataFrame(electricity_bus['sequences']).to_csv(fn)


print('')
print('--------invest wind_on-------------')
print(wind_on_source['scalars'])
#print(wind_on_source['sequences'])
print('-------end invest wind_on------------')

print('')
print('--------invest wind_off-------------')
print(wind_off_source['scalars'])
#print(wind_on_source['sequences'])
print('-------end invest wind_off------------')



# print a time slice of the state of charge
print('')
print('********* State of Charge (slice) *********')

print('')

print('')
print('--------invest wind_on-------------')
print(pv_source['scalars'])
#print(wind_on_source['sequences'])
print('-------end invest wind_on------------')
# get all variables of a specific component/bus
#custom_storage = views.node(results, 'storage')


# plot the time series (sequences) of a specific component/bus
if plt is not None:

    plt.show()
    electricity_bus['sequences'].plot(kind='line', drawstyle='steps-post')
    plt.show()




# print the solver results
print('********* Meta results *********')
pp.pprint(es.energysystem.results['meta'])
print('')

# print the sums of the flows around the electricity bus
print('********* Main results *********')
print(electricity_bus['sequences'].sum(axis=0))

fn = os.path.join(os.path.dirname(__file__), 'standard_neetwork_electricity_sum_feedin.xlsx')
electricity_bus['sequences'].sum(axis=0).to_excel(fn)



