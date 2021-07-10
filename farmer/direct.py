import pyomo.environ as pe
import pyomo.opt as po

from data import *


def var_tons_sold_bounds(m, c, lb, ub, s):
    if ub is None:
        bounds = 0, None
    else:
        bounds = 0, ub - lb
    return bounds


def var_tons_purchased_bounds(m, c, s):
    return 0, 0 if m.purchase_price[c] is None else None


def obj(m):
    return sum(m.planting_cost[c] * m.acres_allocated[c] for c in m.crops) \
           + m.cvar_eta \
           + sum(m.probability[s] * m.cvar_nu[s] for s in m.scenarios) / m.cvar_epsilon


def con_max_acreage(m):
    return sum(m.acres_allocated[c] for c in m.crops) <= m.acreage


def con_cvar_nu(m, s):
    return m.cvar_nu[s] >= m.cvar_f[s] - m.cvar_eta


def con_min_required(m, c, s):
    return m.harvest[c, s] * m.acres_allocated[c] \
           + m.tons_purchased[c, s] \
           - sum(m.tons_sold[c, lb, ub, s]
                 for cp, lb, ub in m.crops_by_quantity_ranges
                 if c == cp) \
           >= m.min_required[c]


def f(m, s):
    expr = 0
    expr -= sum(m.selling_price[c, lb, ub] * m.tons_sold[c, lb, ub, s]
                for c, lb, ub in m.crops_by_quantity_ranges)
    expr += sum(m.purchase_price[c] * m.tons_purchased[c, s]
                for c in m.crops
                if m.purchase_price[c] is not None)
    return expr


def con_cvar_nu(m, s):
    return m.cvar_nu[s] >= f(m, s) - m.cvar_eta


def con_robust_f(m, s):
    return m.robust_f >= f(m, s)


def model_creator(how=None, **kwargs):
    model = pe.ConcreteModel()
    # sets
    model.crops = pe.Set(initialize=CROPS)
    model.crops_by_quantity_ranges = pe.Set(initialize=CROPS_BY_QUANTITY_RANGES)
    model.scenarios = pe.Set(initialize=SCENARIOS)
    # parameters
    model.acreage = pe.Param(initialize=ACREAGE)
    model.harvest = pe.Param(model.crops, model.scenarios, initialize=HARVEST)
    model.probability = pe.Param(model.scenarios, initialize=PROBABILITY)
    model.planting_cost = pe.Param(model.crops, initialize=PLANTING_COST)
    model.selling_price = pe.Param(model.crops_by_quantity_ranges, initialize=SELLING_PRICE)
    model.purchase_price = pe.Param(model.crops, initialize=PURCHASE_PRICE, domain=pe.Any)
    model.min_required = pe.Param(model.crops, initialize=MIN_REQUIRED)
    # variables
    model.acres_allocated = pe.Var(model.crops, domain=pe.NonNegativeReals)
    model.tons_sold = pe.Var(model.crops_by_quantity_ranges, model.scenarios, bounds=var_tons_sold_bounds)
    model.tons_purchased = pe.Var(model.crops, model.scenarios, bounds=var_tons_purchased_bounds)

    # constraints
    model.con_max_acreage = pe.Constraint(rule=con_max_acreage)
    model.con_min_required = pe.Constraint(model.crops, model.scenarios, rule=con_min_required)

    # objective
    if how is None:
        how = 'expectation'

    if how == 'expectation':
        model.obj_stage1 = pe.Expression(expr=sum(model.planting_cost[c] * model.acres_allocated[c] for c in model.crops))
        model.obj_stage2 = pe.Expression(expr=sum(model.probability[s] * f(model, s) for s in model.scenarios))
    elif how == 'cvar':
        model.cvar_eta = pe.Var(domain=pe.Reals)
        model.cvar_nu = pe.Var(model.scenarios, domain=pe.NonNegativeReals)
        model.cvar_f = pe.Var(model.scenarios, domain=pe.Reals)
        model.con_cvar_nu = pe.Constraint(model.scenarios, rule=con_cvar_nu)
        model.obj_stage1 = pe.Expression(expr=model.cvar_eta + sum(model.planting_cost[c] * model.acres_allocated[c] for c in model.crops))
        model.obj_stage2 = pe.Expression(expr=sum(model.probability[s] * model.cvar_nu[s] for s in  model.scenarios) / kwargs['epsilon'])
    elif how == 'robust':
        model.robust_f = pe.Var(domain=pe.Reals)
        model.con_robust_f = pe.Constraint(model.scenarios, rule=con_robust_f)
        model.obj_stage1 = pe.Expression(expr=model.robust_f + sum(model.planting_cost[c] * model.acres_allocated[c] for c in model.crops))
        model.obj_stage2 = pe.Expression(expr=0)

    model.obj = pe.Objective(sense=pe.minimize, expr=model.obj_stage1 + model.obj_stage2)

    return model


# pick one model_creator_kwargs below
model_creator_kwargs = {'how': 'expectation'}
# model_creator_kwargs = {'how': 'cvar', 'epsilon': 3 / 3}
# model_creator_kwargs = {'how': 'robust'}
# model_creator_kwargs = {'how': 'cvar', 'epsilon': 1 / 3}

model = model_creator(**model_creator_kwargs)
solver = po.SolverFactory('glpk', tee=True)
results = solver.solve(model)
print(model.obj())
for c in model.crops:
    print(c, pe.value(model.acres_allocated[c]))