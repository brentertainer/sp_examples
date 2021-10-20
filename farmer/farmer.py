import mpisppy.utils.sputils as sputils
import pyomo.environ as pe

from data import *


def var_tons_sold_bounds(m, c, lb, ub):
    if ub is None:
        bounds = 0, None
    else:
        bounds = 0, ub - lb
    return bounds


def var_tons_purchased_bounds(m, c):
    return 0, 0 if m.purchase_price[c] is None else None


def con_max_acreage(m):
    return sum(m.acres_allocated[c] for c in m.crops) <= m.acreage


def con_min_required(m, c):
    return m.harvest[c] * m.acres_allocated[c]\
           + m.tons_purchased[c]\
           - sum(m.tons_sold[c, lb, ub]
                 for cp, lb, ub in m.crops_by_quantity_ranges
                 if c == cp)\
           >= m.min_required[c]


def f(m):
    expr = 0
    expr -= sum(m.selling_price[c, lb, ub] * m.tons_sold[c, lb, ub]
                for c, lb, ub in m.crops_by_quantity_ranges)
    expr += sum(m.purchase_price[c] * m.tons_purchased[c]
                for c in m.crops
                if m.purchase_price[c] is not None)
    return expr


def con_cvar_nu(m):
    return m.cvar_nu >= f(m) - m.cvar_eta


def con_robust_f(m):
    return m.robust_f >= f(m)


def scenario_creator(scenario, risk_measure=None, **kwargs):
    model = pe.ConcreteModel()
    # sets
    model.crops = pe.Set(initialize=CROPS)
    model.crops_by_quantity_ranges = pe.Set(initialize=CROPS_BY_QUANTITY_RANGES)
    # parameters
    model.acreage = pe.Param(initialize=ACREAGE)
    harvest = {crop: value for (crop, _scenario), value in HARVEST.items() if _scenario == scenario}
    model.harvest = pe.Param(model.crops, initialize=harvest)
    model.planting_cost = pe.Param(model.crops, initialize=PLANTING_COST)
    model.selling_price = pe.Param(model.crops_by_quantity_ranges, initialize=SELLING_PRICE)
    model.purchase_price = pe.Param(model.crops, initialize=PURCHASE_PRICE, domain=pe.Any)
    model.min_required = pe.Param(model.crops, initialize=MIN_REQUIRED)
    # variables
    model.acres_allocated = pe.Var(model.crops, domain=pe.NonNegativeReals)
    model.tons_sold = pe.Var(model.crops_by_quantity_ranges, bounds=var_tons_sold_bounds)
    model.tons_purchased = pe.Var(model.crops, bounds=var_tons_purchased_bounds)
    # constraints
    model.con_max_acreage = pe.Constraint(rule=con_max_acreage)
    model.con_min_required = pe.Constraint(model.crops, rule=con_min_required)

    # mpisppy probability
    model._mpisppy_probability = PROBABILITY[scenario]

    # objective
    if risk_measure is None:
        risk_measure = 'expectation'

    if risk_measure == 'expectation':
        expr = sum(model.planting_cost[c] * model.acres_allocated[c] for c in model.crops)
        model.obj_stage1 = pe.Expression(expr=expr)
        model.obj_stage2 = pe.Expression(expr=f(model))
        sputils.attach_root_node(model, model.obj_stage1, [model.acres_allocated])
    elif risk_measure == 'cvar':
        model.cvar_eta = pe.Var(domain=pe.Reals)
        model.cvar_nu = pe.Var(domain=pe.NonNegativeReals)
        model.con_cvar_nu = pe.Constraint(rule=con_cvar_nu)
        expr = model.cvar_eta + sum(model.planting_cost[c] * model.acres_allocated[c] for c in model.crops)
        model.obj_stage1 = pe.Expression(expr=expr)
        model.obj_stage2 = pe.Expression(expr=model.cvar_nu / kwargs['epsilon'])
        sputils.attach_root_node(model, model.obj_stage1, [model.cvar_eta, model.acres_allocated])
    elif risk_measure == 'robust':
        model.robust_f = pe.Var(domain=pe.Reals)
        model.con_robust_f = pe.Constraint(rule=con_robust_f)
        expr = model.robust_f + sum(model.planting_cost[c] * model.acres_allocated[c] for c in model.crops)
        model.obj_stage1 = pe.Expression(expr=expr)
        model.obj_stage2 = pe.Expression(expr=0)
        sputils.attach_root_node(model, model.obj_stage1, [model.robust_f, model.acres_allocated])

    model.obj = pe.Objective(sense=pe.minimize, expr=model.obj_stage1 + model.obj_stage2)

    return model

