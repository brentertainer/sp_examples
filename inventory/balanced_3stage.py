from functools import reduce
from itertools import product
from operator import mul

# instance parameters
_num_days = 2
_levels = [0, 1] # 0 = low demand, 1 = high demand
_cost = 5
_revenue = {1: 7, 2: 5}
_probability = {0: 0.25, 1: 0.75}
_demand = {0: 5, 1: 10}

# initialize scenario tree data
all_nodenames = ['ROOT']
parent = {'ROOT': None}
node_prob = {'ROOT': 1.0}
scen_prob = {}
scenarios = []
nodes = {}
# initialize scenario instance data
num_days = _num_days
cost = _cost
revenue = {}
demand = {}
# setup
i = 0
for n in range(1, _num_days + 1):
    for prod in product(_levels, repeat=n):
        node = '_'.join(['ROOT', *[str(level) for level in prod]])
        path = node.split('_')
        all_nodenames.append(node)
        parent[node] = '_'.join(['ROOT', *[str(level) for level in prod[:-1]]])
        if n < _num_days:
            node_prob[node] = _probability[int(path[-1])]
        if n == _num_days:
            i += 1
            scen = f'Scen{i}'
            scenarios.append(scen)
            scen_prob[scen] = reduce(mul, [_probability[int(level)] for level in path[1:]])
            nodes[scen] = ['_'.join(path[:n]) for n in range(1, _num_days + 1)]
            revenue[scen] = _revenue
            demand[scen] = {day: _demand[int(level)] for day, level in enumerate(path[1:], start=1)}
