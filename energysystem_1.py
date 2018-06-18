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
date_time_index = pd.date_range('1/1/2018', periods = 100, freq = 'H' )

energysystem = solph.EnergySystem(timeindex=date_time_index)

#input_data
filename = os.path.join(os.path.dirname(__file__), 'reference_scenario.csv')
data = pd.read_csv(filename)

# investment for each energy carrier
epc_coal_old = economics.annuity(capex=1650, n=40, wacc=0.056)

epc_coal_new = economics.annuity(capex=1650, n=40, wacc=0.056)

epc_lignite_old = economics.annuity(capex=1900, n=40, wacc=0.056)

epc_lignite_new = economics.annuity(capex=1900, n=40, wacc=0.056)

epc_gas = economics.annuity(capex=950, n=30, wacc=0.052)

epc_wind_on = economics.annuity(capex=1750, n=25, wacc=0.025)

epc_wind_off = economics.annuity(capex=3900, n=25, wacc=0.048)

epc_pv = economics.annuity(capex=700, n=25, wacc=0.021)


###########
# 2 Built the network
##########

# Create all Buses
#bcoal_old = solph.Bus(label = "coal_old") 

bcoal = solph.Bus(label = "coal")

#blignite_old = solph.Bus(label = "lignite_old")

blignite = solph.Bus(label = "lignite")

bgas = solph.Bus(label = "gas")

bel = solph.Bus(label = "electricity")

# add all Buses to the EnergySystem
energysystem.add( bcoal, blignite, bgas, bel)

# source coal old
#energysystem.add(solph.Source(label='coal_old', outputs={bcoal_old: solph.Flow(
    #nominal_value=800, variable_costs = 9.6)}))

# source coal new
energysystem.add(solph.Source(label='coal_new', outputs={bcoal: solph.Flow(
    nominal_value=800, variable_costs = 9.6)}))

# source lignite old
#energysystem.add(solph.Source(label='lignite_old', outputs={bcoal_new: solph.Flow(
    #nominal_value=1000, variable_costs = 1.8)}))

# source lignite new
energysystem.add(solph.Source(label='lignite_new', outputs={bcoal: solph.Flow(
    nominal_value=1000, variable_costs = 1.8)}))

# source natural gas
energysystem.add(solph.Source(label='rgas', outputs={bgas: solph.Flow(
    nominal_value=200, variable_costs = 21)}))

# source wind onshore
energysystem.add(solph.Source(label='wind_on', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['Wind_on'], investment = solph.Investment(ep_costs=epc_wind_on,maximum=60000))}))

#source wind offshore
energysystem.add(solph.Source(label='wind_off', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['Wind_off'], investment = solph.Investment(ep_costs=epc_wind_off,maximum=45000))}))

# source pv
energysystem.add(solph.Source(label='pv', outputs={bel: solph.Flow(fixed=True, 
        actual_value=data['PV'], investment = solph.Investment(ep_costs=epc_pv,maximum=275000))}))


# create simple sink object for electrical demand for each electrical bus
solph.Sink(label='demand_elec', inputs={bel: solph.Flow(
       actual_value= data['el_demand'], fixed=True, nominal_value=1)})


# Create all Transformers

# transformer coal old
energysystem.add(solph.Transformer(
       label="pp_coal_old", 
       inputs={bcoal: solph.Flow()}, 
       outputs = {bel: solph.Flow(nominal_value = None, variable_costs=6,investment=solph.Investment(ep_costs=epc_coal_old))},
       conversion_factors ={bel:0.46}))

# transformer coal new
energysystem.add(solph.Transformer(
    label="pp_coal_new",
    inputs={bcoal: solph.Flow()},
    outputs={bel: solph.Flow(nominal_value = None, variable_costs=10,investment=solph.Investment(ep_costs=epc_coal_new))},
    conversion_factors={bel: 0.5}))

# transformer lignite old
energysystem.add(solph.Transformer(
    label="pp_lignite_old",
    inputs={blignite: solph.Flow()},
    outputs={bel: solph.Flow(nominal_value = None, variable_costs=10,investment=solph.Investment(ep_costs=epc_lignite_old))},
    conversion_factors={bel: 0.45}))

# transformer lignite new
energysystem.add(solph.Transformer(
    label="pp_lignite_new",
    inputs={blignite: solph.Flow()},
    outputs={bel: solph.Flow(nominal_value = None, variable_costs=10,investment=solph.Investment(ep_costs=epc_lignite_new))},
    conversion_factors={bel: 0.465}))

# transformer gas
energysystem.add(solph.Transformer(
    label="pp_gas",
    inputs={bgas: solph.Flow()},
    outputs={bel: solph.Flow(nominal_value = None, variable_costs=10,investment=solph.Investment(ep_costs=epc_gas))},
    conversion_factors={bel: 0.58}))

