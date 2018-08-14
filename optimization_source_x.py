
"""
Optimisation
"""

from oemof import solph
from oemof.outputlib import processing

from oemof.outputlib import views

import source_x_system as es
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

mbc= processing.create_dataframe(om)


fn = os.path.join(os.path.dirname(__file__), 'source_x_dataframe.xlsx')
pd.DataFrame(mbc).to_excel(fn)

#1 get the maximum capacities of each technology mbc = maximum built capacity
    
mbc = mbc.loc[mbc.variable_name == 'invest', ['value', 'oemof_tuple']]

print(mbc)
    # rename the index with the name of the investment flow 
# rename the index with the name of the investment flow 
a = 0
while a < mbc.index.size:
    mbc.rename(index= { mbc.index[a]: (mbc.loc[mbc.index[a],'oemof_tuple'])}, inplace= True)
    a+=1

fn = os.path.join(os.path.dirname(__file__), 'built_capacities_source_x.csv')
pd.DataFrame(mbc).to_csv(fn)


mbc.plot(kind = 'bar')

df = processing.create_dataframe(om)
# creating a result dictionary containing node parameters
p_results = processing.param_results(om)

electricity_bus     = views.node(results, 'electricity')
wind_on_source      = views.node(results, 'wind_on')
wind_off_source     = views.node(results, 'wind_off')
pv_source           = views.node(results, 'pv')



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

fn = os.path.join(os.path.dirname(__file__), 'source_x_electricity_hourly.xlsx')
electricity_bus['sequences'].to_excel(fn)

# print the solver results
print('********* Meta results *********')
pp.pprint(es.energysystem.results['meta'])
print('')

# print the sums of the flows around the electricity bus
print('********* Main results *********')
print(electricity_bus['sequences'].sum(axis=0))

fn = os.path.join(os.path.dirname(__file__), 'source_x_electricity_sum_feedin.xlsx')
electricity_bus['sequences'].sum(axis=0).to_excel(fn)



