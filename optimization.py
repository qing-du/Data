# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 14:13:17 2018

@author: duqi1
"""

from oemof import solph
from oemof.outputlib import processing

from oemof.outputlib import views

import energysystem_1 as es


import pandas as pd

import oemof.graph as grph 
import pprint as pp

import matplotlib.pyplot as plt 


#import networkx as nx

om = solph.Model(es.energysystem)

om.solve(solver = 'cbc', solve_kwargs ={'tee':True})

my_results = processing.results(om)




es.energysystem.results['main'] = processing.results(om)
es.energysystem.results['meta'] = processing.meta_results(om)

# The default path is the '.oemof' folder in your $HOME directory.
# The default filename is 'es_dump.oemof'.
# You can omit the attributes (as None is the default value) for testing cases.
# You should use unique names/folders for valuable results to avoid
# overwriting.

# store energy system with results
es.energysystem.dump(dpath=None, filename=None)
# define an alias for shorter calls below (optional)
results = es.energysystem.results['main']

# geeting data of the Data Frame
df = processing.create_dataframe(om)
print('--------------------DataFrame-----------------') 
print(df)



# creating a result dictionary containing node parameters
p_results = processing.param_results(om)
print('-------------------ParamResults---------------')
print(p_results)




electricity_bus     = views.node(results, 'electricity')
#coal_bus            = views.node(results, 'coal')

#coal_transformer    = views.node(results,'pp_coal')
#gas_transformer     = views.node(results, 'pp_gas')

wind_on_source      = views.node(results, 'wind_on')
wind_off_source     = views.node(results, 'wind_off')

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





