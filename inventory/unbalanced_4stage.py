# instance parameters
_num_days = 3
_levels = [0, 1, 2]
_cost = 5
_revenue = {1: 8, 2: 7, 3: 6}
_demand = {0: 8, 1: 10, 2: 12}

# scenario tree data
all_nodenames = [
    'ROOT',
    'ROOT_0',
    'ROOT_0_0',
    'ROOT_0_0_0',
    'ROOT_0_0_1',
    'ROOT_0_1',
    'ROOT_0_1_0',
    'ROOT_0_1_1',
    'ROOT_0_1_2',
    'ROOT_0_2',
    'ROOT_0_2_0',
    'ROOT_0_2_1',
    'ROOT_1',
    'ROOT_1_0',
    'ROOT_1_0_0',
    'ROOT_1_0_1',
    'ROOT_1_1',
    'ROOT_1_1_0'
]
parent = {
    'ROOT': None,
    'ROOT_0': 'ROOT',
    'ROOT_1': 'ROOT',
    'ROOT_0_0': 'ROOT_0',
    'ROOT_0_1': 'ROOT_0',
    'ROOT_0_2': 'ROOT_0',
    'ROOT_1_0': 'ROOT_1',
    'ROOT_1_1': 'ROOT_1',
    'ROOT_0_0_0': 'ROOT_0_0',
    'ROOT_0_0_1': 'ROOT_0_0',
    'ROOT_0_1_0': 'ROOT_0_1',
    'ROOT_0_1_1': 'ROOT_0_1',
    'ROOT_0_1_2': 'ROOT_0_1',
    'ROOT_0_2_0': 'ROOT_0_2',
    'ROOT_0_2_1': 'ROOT_0_2',
    'ROOT_1_0_0': 'ROOT_1_0',
    'ROOT_1_0_1': 'ROOT_1_0',
    'ROOT_1_1_0': 'ROOT_1_1'
}
node_prob = {
    'ROOT':       1.00,
    'ROOT_0':     0.25,
    'ROOT_0_0':   0.25,
    'ROOT_0_0_0': 0.60,
    'ROOT_0_0_1': 0.40,
    'ROOT_0_1':   0.50,
    'ROOT_0_1_0': 0.40,
    'ROOT_0_1_1': 0.30,
    'ROOT_0_1_2': 0.30,
    'ROOT_0_2':   0.25,
    'ROOT_0_2_0': 0.70,
    'ROOT_0_2_1': 0.30,
    'ROOT_1':     0.75,
    'ROOT_1_0':   0.80,
    'ROOT_1_0_0': 0.40,
    'ROOT_1_0_1': 0.60,
    'ROOT_1_1':   0.20,
    'ROOT_1_1_0': 1.00
}
scen_prob = {
     'Scen1': 0.03750,
     'Scen2': 0.02500,
     'Scen3': 0.05000,
     'Scen4': 0.03750,
     'Scen5': 0.03750,
     'Scen6': 0.04375,
     'Scen7': 0.01875,
     'Scen8': 0.24000,
     'Scen9': 0.36000,
    'Scen10': 0.15000
}
scenarios = [
     'Scen1',
     'Scen2',
     'Scen3',
     'Scen4',
     'Scen5',
     'Scen6',
     'Scen7',
     'Scen8',
     'Scen9',
    'Scen10'
]
nodes = {
     'Scen1': ['ROOT', 'ROOT_0', 'ROOT_0_0'],
     'Scen2': ['ROOT', 'ROOT_0', 'ROOT_0_0'],
     'Scen3': ['ROOT', 'ROOT_0', 'ROOT_0_1'],
     'Scen4': ['ROOT', 'ROOT_0', 'ROOT_0_1'],
     'Scen5': ['ROOT', 'ROOT_0', 'ROOT_0_1'],
     'Scen6': ['ROOT', 'ROOT_0', 'ROOT_0_2'],
     'Scen7': ['ROOT', 'ROOT_0', 'ROOT_0_2'],
     'Scen8': ['ROOT', 'ROOT_1', 'ROOT_1_0'],
     'Scen9': ['ROOT', 'ROOT_1', 'ROOT_1_0'],
    'Scen10': ['ROOT', 'ROOT_1', 'ROOT_1_1'],
}

# scenario instance data
num_days = _num_days
cost = _cost
demand = {
     'Scen1': {1:  8, 2:  8, 3:  8},
     'Scen2': {1:  8, 2:  8, 3: 12},
     'Scen3': {1:  8, 2: 10, 3:  8},
     'Scen4': {1:  8, 2: 10, 3: 10},
     'Scen5': {1:  8, 2: 10, 3: 12},
     'Scen6': {1:  8, 2: 12, 3:  8},
     'Scen7': {1:  8, 2: 12, 3: 12},
     'Scen8': {1: 12, 2:  8, 3:  8},
     'Scen9': {1: 12, 2:  8, 3: 12},
    'Scen10': {1: 12, 2: 12, 3: 10}
}
revenue = {scen: _revenue for scen in demand}
