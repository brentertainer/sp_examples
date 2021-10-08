from functools import reduce
from itertools import product
from operator import mul

import pyomo.environ as penv
from mpisppy.opt.ef import ExtensiveForm

import inventory
import balanced_3stage as data
#import balanced_6stage as data
#import unbalanced_4stage as data


options = {'solver': 'gurobi', 'mipgap': 0.0}
all_nodenames = data.all_nodenames
scenarios = data.scenarios
scenario_creator = inventory.scenario_creator
scenario_creator_kwargs = {
    # scenario tree data
    'nodes': data.nodes,
    'parent': data.parent,
    'node_prob': data.node_prob,
    'scen_prob': data.scen_prob,
    # scenario instance data
    'num_days': data.num_days,
    'cost': data.cost,
    'revenue': data.revenue,
    'demand': data.demand
}

ef = ExtensiveForm(options,
                   scenarios,
                   scenario_creator,
                   scenario_creator_kwargs=scenario_creator_kwargs,
                   all_nodenames=all_nodenames)

result = ef.solve_extensive_form()
print('Objective:', penv.value(ef.ef.EF_Obj))
print('Purchase:', penv.value(ef.ef.Scen1.inventory[0]))


nodes = set()
edges = set()
for scen, path in data.nodes.items():
    for a, b in zip(path, path[1:] + [scen]):
        nodes.add(a)
        nodes.add(b)
        edges.add((a, b))

import networkx as nx
import matplotlib.pyplot as plt
graph = nx.DiGraph()
graph.add_nodes_from(sorted(nodes))
graph.add_edges_from(sorted(edges))

pos = nx.drawing.nx_pydot.graphviz_layout(graph, "twopi")
nx.draw(graph, pos, with_labels=True)
plt.show()
