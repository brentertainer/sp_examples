from itertools import product

import pyomo.environ as penv
from mpisppy.opt.ef import ExtensiveForm

import inventory


# instance parameters
"""
num_days = 2
levels = [0, 1] # 0 = low demand, 1 = high demand
cost = 5
revenue = {1: 7, 2: 5}
probability = {0: 0.25, 1: 0.75}
demand = {0: 5, 1: 10}
"""

# instance parameters
num_days = 5
levels = [0, 1, 2]
cost = 5
revenue = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4}
probability = {0: 0.25, 1: 0.50, 2: 0.25}
demand = {0:  8, 1: 10, 2: 12}


# ExtensiveForm arguments
scenarios = [f'Scen{i}' for i in range(1, len(levels) ** num_days + 1)]
scenario_creator = inventory.scenario_creator
paths = dict()
scen_iter = iter(scenarios)
for prod in product(levels, repeat=num_days):
    paths[next(scen_iter)] = '_'.join(['ROOT', *[str(level) for level in prod]])
scenario_creator_kwargs = {
    'paths': paths,
    'num_days': num_days,
    'cost': cost,
    'revenue': revenue,
    'demand': demand,
    'probability': probability
}
all_nodenames = ['ROOT']
for n in range(1, num_days + 1):
    for prod in product(levels, repeat=n):
        all_nodenames.append('_'.join(['ROOT', *[str(level) for level in prod]]))

options = {'solver': 'gurobi', 'mipgap': 0.0}

ef = ExtensiveForm(options,
                   scenarios,
                   scenario_creator,
                   scenario_creator_kwargs=scenario_creator_kwargs,
                   all_nodenames=all_nodenames)


ef.solve_extensive_form()
print('Objective: ', penv.value(ef.ef.EF_Obj))
print('First Stage Decision: ', penv.value(ef.ef.Scen1.inventory[0]))
#ef.report_var_values_at_rank0()
