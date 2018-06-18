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

# print a time slice of the state of charge
print('')
print('********* State of Charge (slice) *********')

print('')

# get all variables of a specific component/bus
#custom_storage = views.node(results, 'storage')
electricity_bus = views.node(results, 'electricity')

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

