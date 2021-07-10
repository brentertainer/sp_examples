from mpisppy.opt.ef import ExtensiveForm

from data import SCENARIOS
from farmer import scenario_creator

options = {'solver': 'glpk'}

# pick one scenario_creator_kwargs below
scenario_creator_kwargs = {'how': 'expectation'}
# scenario_creator_kwargs = {'how': 'cvar', 'epsilon': 3 / 3}
# scenario_creator_kwargs = {'how': 'robust'}
# scenario_creator_kwargs = {'how': 'cvar', 'epsilon': 1 / 3}

ef = ExtensiveForm(options, SCENARIOS, scenario_creator, scenario_creator_kwargs=scenario_creator_kwargs)
results = ef.solve_extensive_form()
variables = ef.gather_var_values_to_rank0()
print('Profit: ', ef.get_objective_value())
for key, val in variables.items():
    print(key, val)
