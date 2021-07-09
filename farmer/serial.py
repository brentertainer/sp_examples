import pyomo.opt as po
from mpisppy.opt.lshaped import LShapedMethod
from mpisppy.opt.ef import ExtensiveForm
from mpisppy.opt.ph import PH

import farmer
from data import SCENARIOS


solve_subproblems_individually = False
solve_extensive_form = True
solve_progressive_hedging = True
solve_benders_decomposition = True

solver = root_solver = sp_solver = 'gurobi'

# Solve Subproblems Individually
if solve_subproblems_individually:
    solver = po.SolverFactory(solver)
    models = [farmer.scenario_creator(s) for s in SCENARIOS]
    for model in models:
        solver.solve(model)
        print(round(model.obj()))


# Extensive Form
if solve_extensive_form:
    options = {'solver': solver}
    ef = ExtensiveForm(options, SCENARIOS, farmer.scenario_creator)
    results = ef.solve_extensive_form()
    print(round(ef.get_objective_value()))


# Progressive Hedging
if solve_progressive_hedging:
    options = {
        'solvername': solver,
        'PHIterLimit': 50,
        'defaultPHrho': 10,
        #'convthresh': 1e-7,
        'convthresh': 1e-16,
        'verbose': False,
        'display_progress': False,
        'display_timing': False,
        'iter0_solver_options': {},
        'iterk_solver_options': {}
    }
    ph = PH(options, SCENARIOS, farmer.scenario_creator)
    results = ph.ph_main()
    variables = ph.gather_var_values_to_rank0()
    for (scenario, variable) in variables:
        print(scenario, variable, variables[scenario, variable])


# Benders Decomposition
if solve_benders_decomposition:
    bounds = {scenario: -432000 for scenario in SCENARIOS}
    options = {
        'root_solver': root_solver,
        'sp_solver': sp_solver,
        'sp_solver_options' : {'threads' : 1},
        'valid_eta_lb': bounds,
        'max_iter': 10,
    }
    ls = LShapedMethod(options, SCENARIOS, farmer.scenario_creator)
    result = ls.lshaped_algorithm()
    variables = ls.gather_var_values_to_rank0()
    for (scenario, variable) in variables:
        print(scenario, variable, variables[scenario, variable])
