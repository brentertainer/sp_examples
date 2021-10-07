from functools import reduce
from operator import mul

import pyomo.environ as penv
from mpisppy.scenario_tree import ScenarioNode

import mpisppy.utils.sputils as sputils


def instance_creator(name, num_days, cost, revenue, demand):

    def obj_by_stage(inst, day):
        if day == 0:
            return -inst.cost * inst.inventory[day]
        else:
            return inst.revenue[day] * inst.sales[day]

    def obj_overall(inst):
        return sum(inst.obj_by_stage[n] for n in inst.days)

    def con_y0_is_zero(inst):
        return inst.sales[0] == 0

    def con_product_conservation(inst, day):
        if day != 0:
            return inst.inventory[day] == inst.inventory[day-1] - inst.sales[day]
        else:
            return penv.Constraint.Skip

    def con_sales_le_inventory(inst, day):
        if day != 0:
            return inst.sales[day] <= inst.inventory[day-1]
        else:
            return penv.Constraint.Skip


    inst = penv.ConcreteModel(name=name)
    inst.days = penv.Set(initialize=range(0, num_days + 1))
    inst.cost = penv.Param(default=0, initialize=cost)
    inst.revenue = penv.Param(inst.days, default=0, initialize=revenue)
    inst.demand = penv.Param(inst.days, default=0, initialize=demand)
    inst.inventory = penv.Var(inst.days, domain=penv.NonNegativeReals) # at end of day
    inst.sales = penv.Var(inst.days, bounds=lambda inst, n: (0, inst.demand[n]))
    inst.obj_by_stage = penv.Expression(inst.days, rule=obj_by_stage)
    inst.obj_overall = penv.Objective(sense=penv.maximize, rule=obj_overall)
    inst.con_y0_is_zero = penv.Constraint(rule=con_y0_is_zero)
    inst.con_product_conservation = penv.Constraint(inst.days, rule=con_product_conservation)
    inst.con_sales_le_inventory = penv.Constraint(inst.days, rule=con_sales_le_inventory)
    return inst


def node_creator(instance, path, probability):
    nodes = []
    nodes.append(ScenarioNode('ROOT',
                              1.0,
                              1,
                              instance.obj_by_stage[0],
                              None,
                              [instance.inventory[0],
                               instance.sales[0]],
                              instance))
    for day, val in enumerate(path[:-1], start=1):
        this_name = '_'.join(['ROOT', *[str(level) for level in path[:day]]])
        if day == 1:
            parent_name = 'ROOT'
        else:
            parent_name = '_'.join(['ROOT', *[str(level) for level in path[:day-1]]])
        nodes.append(ScenarioNode(this_name,
                                  probability[path[day-1]],
                                  day+1,
                                  instance.obj_by_stage[day],
                                  None,
                                  [instance.inventory[day],
                                   instance.sales[day]],
                                  instance,
                                  parent_name=parent_name))
    return nodes


def scenario_creator(name,
                     paths=None,
                     num_days=None,
                     cost=None,
                     revenue=None,
                     demand=None,
                     probability=None):

    path = tuple(map(int, paths[name].split('_')[1:]))
    instance = instance_creator(name,
                                num_days=num_days,
                                cost=cost,
                                revenue=revenue,
                                demand={day: demand[val] for day, val in enumerate(path, start=1)})

    # The following had me stumped for quite a while.
    # When we create the nodes, we have to specify conditional probabilities.
    # But when we create the scenarios, we have to specify *joint* probabilities.
    instance._mpisppy_node_list = node_creator(instance, path, probability)
    instance._mpisppy_probability = reduce(mul, [probability[level] for level in path])
    return instance
