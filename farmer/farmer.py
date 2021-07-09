import mpisppy.utils.sputils as sputils
import pyomo.environ as pe

from data import *


def build_model(scenario):

    model = pe.ConcreteModel()

    # sets
    model.crops = pe.Set(initialize=CROPS)
    model.crops_by_quantity_ranges = pe.Set(initialize=list(SELLING_PRICE.keys()))

    # parameters
    model.acreage = pe.Param(initialize=ACREAGE)
    model.harvest = pe.Param(model.crops, initialize=HARVEST[scenario])
    model.planting_cost = pe.Param(model.crops, initialize=PLANTING_COST)
    model.selling_price = pe.Param(model.crops_by_quantity_ranges, initialize=SELLING_PRICE)
    model.purchase_price = pe.Param(model.crops, initialize=PURCHASE_PRICE, domain=pe.Any)
    model.min_required = pe.Param(model.crops, initialize=MIN_REQUIRED)

    # variables
    def var_w_bounds(model, c, lb, ub):
        if ub is None:
            bounds = (0, None)
        else:
            bounds = (0, ub - lb)
        return bounds

    def var_y_bounds(model, c):
        return (0, 0 if model.purchase_price[c] is None else None)

    model.tons_sold = pe.Var(model.crops_by_quantity_ranges, bounds=var_w_bounds) # w
    model.acres_allocated = pe.Var(model.crops, domain=pe.NonNegativeReals) # x
    model.tons_purchased = pe.Var(model.crops, bounds=var_y_bounds) # y

    # objectives
    obj_expr = 0
    obj_expr -= sum(model.selling_price[c, lb, ub] * model.tons_sold[c, lb, ub]
                    for c, lb, ub in model.crops_by_quantity_ranges)
    obj_expr += sum(model.planting_cost[c] * model.acres_allocated[c]
                    for c in model.crops)
    obj_expr += sum(model.purchase_price[c] * model.tons_purchased[c]
                    for c in model.crops
                    if model.purchase_price[c] is not None)
    model.obj = pe.Objective(sense=pe.minimize, expr=obj_expr)

    # constraints
    def con_max_acreage(model):
        return sum(model.acres_allocated[c] for c in model.crops) <= model.acreage

    def con_min_required(model, c):
        return model.harvest[c] * model.acres_allocated[c]\
            + model.tons_purchased[c]\
            - sum(model.tons_sold[c, lb, ub]
                  for cp, lb, ub in model.crops_by_quantity_ranges
                  if c == cp)\
            >= model.min_required[c]

    model.con_max_acreage = pe.Constraint(rule=con_max_acreage)
    model.con_min_required = pe.Constraint(model.crops, rule=con_min_required)

    return model


def scenario_creator(scenario):

    model = build_model(scenario)

    # attach mpisppy attributes
    model._mpisppy_probability = PROBABILITY[scenario]
    sputils.attach_root_node(model, model.planting_cost, [model.acres_allocated])

    return model
