import pyomo.environ as penv
from mpisppy.scenario_tree import ScenarioNode


def instance_creator(name, num_days, cost, revenue, demand):
    """
    We formulate the inventory problem as a multi-stage stochastic program in which the
    decision-maker faces an initial purchase decision followed by a series of sales decisions.
    Initially, he or she must choose how much product to order to satisfy uncertain demand over a
    finite time horizon. Each day, he or she must determine how much inventory to sell. Daily sales
    may not exceed daily demand. The per-unit purchase cost is deterministic and fixed. The
    per-unit sales revenue is also deterministic but differs from day to day. The demand also
    varies from day to day and is stochastic with a (possibly different) discrete distribution each
    day. No other costs or revenues are considered.
    """

    def profit_by_day(inst, day):
        if day == 0:
            # In day 0, purchase costs are incurred and there is no revenue.
            return -inst.cost * inst.inventory[day]
        else:
            # In each subsequent day, sales revenues are realized and there is no cost.
            return inst.revenue[day] * inst.sales[day]

    def profit_overall(inst):
        return sum(inst.profit_by_day[n] for n in inst.days)

    def con_product_conservation(inst, day):
        # The inventory at the end of today is equal to the inventory at the end of yesterday less
        # today's sales volume.
        if day != 0:
            return inst.inventory[day] == inst.inventory[day - 1] - inst.sales[day]
        else:
            return penv.Constraint.Skip

    def con_no_initial_sales(inst):
        return inst.sales[0] == 0


    inst = penv.ConcreteModel(name=name)
    inst.days = penv.Set(initialize=range(0, num_days + 1))
    inst.cost = penv.Param(default=0, initialize=cost)
    inst.revenue = penv.Param(inst.days, default=0, initialize=revenue)
    inst.demand = penv.Param(inst.days, default=0, initialize=demand)
    # Inventory is measured after sales at end of each day.
    inst.inventory = penv.Var(inst.days, bounds=(0, None))
    # Daily sales may not exceed daily demand.
    inst.sales = penv.Var(inst.days, bounds=lambda inst, n: (0, inst.demand[n]))
    # The following expression set breaks down the objective by stage. We do this for convenience
    # of later telling which part of the objective results from each stage.
    inst.profit_by_day = penv.Expression(inst.days, rule=profit_by_day)
    inst.profit_overall = penv.Objective(sense=penv.maximize, rule=profit_overall)
    inst.con_product_conservation = penv.Constraint(inst.days, rule=con_product_conservation)
    inst.con_no_initial_sales = penv.Constraint(rule=con_no_initial_sales)
    return inst


def scenario_creator(scen,
                     nodes=None,
                     parent=None,
                     node_prob=None,
                     scen_prob=None,
                     num_days=None,
                     cost=None,
                     revenue=None,
                     demand=None):
    """
    In mpi-sppy, the basic idea is to one determinsitic model per leaf node in the scenario tree.
    The mpi-sppy model object (ExtensiveForm, PH, LShapedMethod, etc.) then sews the determinstic
    models together with non-anticipativity constraints.

    The `scenario_creator` function is a dynamic tool for generating the various scenarios. To
    create a scenario, first build a Pyomo model that incorporates all scenario stages. Then attach
    some probability-related data to the scenario for mpi-sppy to later use. First, attach the list
    of non-leaf nodes from the scenario tree that characterize the scenario. The list should start
    from and include the root node (which must be named 'ROOT'). The conditional probability of
    each node must be supplied at the time of construction. The list should be attached to the
    Pyomo model through the `_mpisppy_node_list` attribute. Second, attach the joint probability of
    the scenario to through the `_mpisppy_probability` attribute.

    Note that each scenario is given its own instances of scenario tree nodes. Here's an example.
    On pencil and paper, every scenario shares the root node of the scenario tree; however, in
    mpi-sppy each scenario generates its own root node object (i.e., a distinct root node with a
    unique memory address but with properties identical to all other root node objects).
    """
    # Create an instance of the scenario using the `instance_creator` function.
    instance = instance_creator(scen,
                                num_days=num_days,
                                cost=cost,
                                revenue=revenue[scen],
                                demand=demand[scen])
    # Attach the list of non-tree nodes from the scenario tree that characterize the scenario.
    instance._mpisppy_node_list = [
        ScenarioNode(node,
                     node_prob[node],
                     day+1,
                     instance.profit_by_day[day],
                     None,
                     [instance.inventory[day],
                      instance.sales[day]],
                     instance,
                     parent_name=parent[node])
        for day, node in enumerate(nodes[scen])
    ]
    # Attach the joint probability of the scenario.
    instance._mpisppy_probability = scen_prob[scen]
    return instance
