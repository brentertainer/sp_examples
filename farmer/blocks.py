import mpisppy.utils.sputils as sputils
import pyomo.environ as pe
import pyomo.opt as po

from data import *


def var_w_bounds(m, c, lb, ub):
    if ub is None:
        bounds = (0, None)
    else:
        bounds = (0, ub - lb)
    return bounds


def var_y_bounds(m, c):
    return (0, 0 if m.purchase_price[c] is None else None)


def con_max_acreage(m):
    return sum(m.x[c] for c in m.crops) <= m.acreage


def con_min_required(m, c):
    return m.harvest[c] * m.x[c]\
        + m.y[c]\
        - sum(m.w[c, lb, ub]
              for cp, lb, ub in m.crops_by_quantity_ranges
              if c == cp)\
        >= m.min_required[c]


def con_cvar_term(m):
    obj = 0
    obj -= sum(m.selling_price[c, lb, ub] * m.w[c, lb, ub]
               for c, lb, ub in m.crops_by_quantity_ranges)
    obj += sum(model.planting_cost[c] * model.x[c]
               for c in model.crops)
    obj += sum(m.purchase_price[c] * m.y[c]
               for c in m.crops
               if m.purchase_price[c] is not None)
    return m.cvar_term >= obj - m.cvar_beta


def blk_rp(m, scenario):

    # sets
    m.crops = pe.Set(initialize=CROPS)
    m.crops_by_quantity_ranges = pe.Set(initialize=list(SELLING_PRICE.keys()))

    # parameters
    m.acreage = pe.Param(initialize=ACREAGE)
    m.harvest = pe.Param(m.crops, initialize=HARVEST[scenario])
    m.selling_price = pe.Param(m.crops_by_quantity_ranges, initialize=SELLING_PRICE)
    m.purchase_price = pe.Param(m.crops, initialize=PURCHASE_PRICE, domain=pe.Any)
    m.min_required = pe.Param(m.crops, initialize=MIN_REQUIRED)

    # variables
    m.w = pe.Var(m.crops_by_quantity_ranges, bounds=var_w_bounds) # tons sold
    m.x = pe.Var(m.crops, domain=pe.NonNegativeReals) # acreage allocation
    m.y = pe.Var(m.crops, bounds=var_y_bounds) # tons purchased
    m.cvar_beta = pe.Var(domain=pe.Reals)
    m.cvar_term = pe.Var(domain=pe.NonNegativeReals)

    # constraints
    m.con_max_acreage = pe.Constraint(rule=con_max_acreage)
    m.con_min_required = pe.Constraint(m.crops, rule=con_min_required)
    m.con_cvar_term = pe.Constraint(rule=con_cvar_term)

    return m


def con_x_nonanticipativity(m, c, s):
    return m.x[c] == m.rp[s].x[c]


def con_cvar_beta_nonanticipativity(m, s):
    return m.cvar_beta == m.rp[s].cvar_beta


model = pe.ConcreteModel()

# sets
model.crops = pe.Set(initialize=CROPS)
model.scenarios = pe.Set(initialize=SCENARIOS)

# parameters
model.planting_cost = pe.Param(model.crops, initialize=PLANTING_COST)
model.probability = pe.Param(model.scenarios, initialize=PROBABILITY)
model.alpha = pe.Param(initialize=0.00) # make this 1.00 to get expectation objective

# variables
model.x = pe.Var(model.crops, domain=pe.NonNegativeReals) # acreage allocation
model.cvar_beta = pe.Var(domain=pe.Reals)

# recourse problems
model.rp = pe.Block(model.scenarios, rule=blk_rp)

# constraints
model.con_x_nonanticipativity = pe.Constraint(model.crops, model.scenarios, rule=con_x_nonanticipativity)
model.con_cvar_beta_nonanticipativity = pe.Constraint(model.scenarios, rule=con_cvar_beta_nonanticipativity)

# objective
def obj(model):
    return model.cvar_beta +\
        sum(model.probability[s] * model.rp[s].cvar_term
            for s in model.scenarios) / (1 - model.alpha)
model.obj = pe.Objective(sense=pe.minimize, rule=obj)

solver = po.SolverFactory('gurobi')
solver.options['MIPGapAbs'] = 1e-16
solver.solve(model, tee=True)

print(model.obj())
